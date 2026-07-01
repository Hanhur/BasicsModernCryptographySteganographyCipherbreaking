# 3. Описание алгоритма
"""
AES-128 шифрование (один блок)
Реализация на основе описания алгоритма Rijndael
"""

# Поле GF(2 ^ 8) с неприводимым многочленом x ^ 8 + x ^ 4 + x ^ 3 + x + 1 (0x11B)
def gf_mul(a, b):
    """Умножение в GF(2 ^ 8)"""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= 0x1B  # модуль x^8 + x^4 + x^3 + x + 1
        b >>= 1
    return p

def gf_inv(a):
    """Обращение в GF(2 ^ 8) через расширенный алгоритм Евклида"""
    if a == 0:
        return 0
    # Расширенный алгоритм Евклида для многочленов над GF(2)
    u, v = a, 0x11B
    g1, g2 = 1, 0
    while v:
        # Деление многочленов
        deg_u = u.bit_length() - 1
        deg_v = v.bit_length() - 1
        if deg_u < deg_v:
            u, v = v, u
            g1, g2 = g2, g1
            continue
        shift = deg_u - deg_v
        u ^= v << shift
        g1 ^= g2 << shift
    return g1

# S-Box таблица (предвычисленная)
def sub_byte(b):
    """Замена байта через S-Box"""
    if b == 0:
        inv = 0
    else:
        inv = gf_inv(b)
    
    # Аффинное преобразование (матрица 8x8 + вектор)
    result = 0
    # Матрица из описания
    matrix = [
        [1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1]
    ]
    const = 0x63  # вектор (1,1,0,0,0,1,1,0)
    
    for i in range(8):
        bit = 0
        for j in range(8):
            if matrix[i][j] and ((inv >> (7 - j)) & 1):
                bit ^= 1
        if bit ^ ((const >> (7 - i)) & 1):
            result |= (1 << (7 - i))
    return result

# Предвычисленная S-Box таблица для скорости
S_BOX = [sub_byte(i) for i in range(256)]

# Обратная S-Box (для дешифрования, но мы не используем)
INV_S_BOX = [0] * 256
for i, val in enumerate(S_BOX):
    INV_S_BOX[val] = i

# Константы раундов для Key Schedule
RCON = [
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
]

def sub_word(word):
    """SubBytes для 4-байтового слова"""
    return (S_BOX[(word >> 24) & 0xFF] << 24) | \
           (S_BOX[(word >> 16) & 0xFF] << 16) | \
           (S_BOX[(word >> 8) & 0xFF] << 8) | \
           (S_BOX[word & 0xFF])

def rot_word(word):
    """Циклический сдвиг слова влево на 1 байт"""
    return ((word << 8) & 0xFFFFFFFF) | (word >> 24)

def key_expansion(key):
    """Развёртка ключа для AES-128 (10 раундов)"""
    key_words = []
    # Разбиваем ключ на 4 слова по 32 бита
    for i in range(4):
        word = 0
        for j in range(4):
            word = (word << 8) | key[i * 4 + j]
        key_words.append(word)
    
    # Генерируем остальные 40 слов (всего 44 слова для 10 раундов)
    for i in range(4, 44):
        temp = key_words[i - 1]
        if i % 4 == 0:
            temp = sub_word(rot_word(temp)) ^ (RCON[i // 4 - 1] << 24)
        key_words.append(key_words[i - 4] ^ temp)
    
    # Преобразуем слова в байтовый массив (round keys)
    round_keys = []
    for i in range(11):  # 11 ключей для 10 раундов
        round_key = []
        for j in range(4):
            word = key_words[i * 4 + j]
            round_key.extend([
                (word >> 24) & 0xFF,
                (word >> 16) & 0xFF,
                (word >> 8) & 0xFF,
                word & 0xFF
            ])
        round_keys.append(round_key)
    return round_keys

def add_round_key(state, key):
    """Наложение ключа (XOR)"""
    return [state[i] ^ key[i] for i in range(16)]

def sub_bytes(state):
    """Замена всех байтов через S-Box"""
    return [S_BOX[b] for b in state]

def shift_rows(state):
    """Сдвиг строк влево: строка 1 на 1, строка 2 на 2, строка 3 на 3"""
    # state представлен как массив 16 байт [a00, a10, a20, a30, a01, a11, ...]
    # Но для удобства представим как матрицу 4x4
    matrix = [[state[r + c * 4] for r in range(4)] for c in range(4)]
    # Сдвиг строк
    for r in range(1, 4):
        matrix[r] = matrix[r][r:] + matrix[r][:r]
    # Обратно в плоский массив
    result = [0] * 16
    for c in range(4):
        for r in range(4):
            result[r + c * 4] = matrix[c][r]
    return result

def mix_columns(state):
    """Перемешивание столбцов"""
    result = [0] * 16
    for c in range(4):  # для каждого столбца
        col = [state[r + c * 4] for r in range(4)]
        # Умножение на многочлен g(y) = (x+1)y^3 + y^2 + y + x
        # Матричное представление умножения
        new_col = [0] * 4
        new_col[0] = gf_mul(col[0], 0x02) ^ gf_mul(col[1], 0x03) ^ col[2] ^ col[3]
        new_col[1] = col[0] ^ gf_mul(col[1], 0x02) ^ gf_mul(col[2], 0x03) ^ col[3]
        new_col[2] = col[0] ^ col[1] ^ gf_mul(col[2], 0x02) ^ gf_mul(col[3], 0x03)
        new_col[3] = gf_mul(col[0], 0x03) ^ col[1] ^ col[2] ^ gf_mul(col[3], 0x02)
        for r in range(4):
            result[r + c * 4] = new_col[r]
    return result

def aes_encrypt_block(plaintext, key):
    """
    Шифрование одного блока (16 байт) AES-128
    plaintext: list из 16 байт
    key: list из 16 байт
    возвращает: list из 16 байт (зашифрованный блок)
    """
    # Развёртка ключа
    round_keys = key_expansion(key)
    
    # Начальное наложение ключа
    state = add_round_key(plaintext, round_keys[0])
    
    # 9 полных раундов (с MixColumns)
    for round_num in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[round_num])
    
    # Последний раунд (без MixColumns)
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[10])
    
    return state

# ============================================================
# Тестовый пример
# ============================================================

def print_state(state, title = "State"):
    """Вывод состояния в виде матрицы 4x4"""
    print(f"\n{title}:")
    for r in range(4):
        row = []
        for c in range(4):
            row.append(f"{state[r + c * 4]:02X}")
        print("  ".join(row))

def test_aes():
    """Тестовый пример из стандарта AES"""
    # Ключ: 0x2b7e151628aed2a6abf7158809cf4f3c
    key = [
        0x2b, 0x7e, 0x15, 0x16,
        0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88,
        0x09, 0xcf, 0x4f, 0x3c
    ]
    
    # Плейнтекст: 0x3243f6a8885a308d313198a2e0370734
    plaintext = [
        0x32, 0x43, 0xf6, 0xa8,
        0x88, 0x5a, 0x30, 0x8d,
        0x31, 0x31, 0x98, 0xa2,
        0xe0, 0x37, 0x07, 0x34
    ]
    
    print("=" * 60)
    print("AES-128 ШИФРОВАНИЕ (ТЕСТОВЫЙ ПРИМЕР)")
    print("=" * 60)
    
    print_state(key, "Ключ")
    print_state(plaintext, "Открытый текст")
    
    # Шифрование
    ciphertext = aes_encrypt_block(plaintext, key)
    print_state(ciphertext, "Зашифрованный текст")
    
    # Ожидаемый результат из стандарта AES
    expected = [
        0x39, 0x25, 0x84, 0x1d,
        0x02, 0xdc, 0x09, 0xfb,
        0xdc, 0x11, 0x85, 0x97,
        0x19, 0x6a, 0x0b, 0x32
    ]
    print_state(expected, "Ожидаемый результат")
    
    # Проверка
    if ciphertext == expected:
        print("\n✅ ТЕСТ ПРОЙДЕН! Результат совпадает со стандартом AES.")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("Получено:", " ".join(f"{b:02X}" for b in ciphertext))
        print("Ожидалось:", " ".join(f"{b:02X}" for b in expected))

def demo_custom():
    """Демонстрация шифрования произвольного блока"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ШИФРОВАНИЯ ПРОИЗВОЛЬНОГО БЛОКА")
    print("=" * 60)
    
    # Пример ключа
    key_hex = "000102030405060708090a0b0c0d0e0f"
    key = bytes.fromhex(key_hex)
    
    # Пример данных
    plaintext_hex = "00112233445566778899aabbccddeeff"
    plaintext = bytes.fromhex(plaintext_hex)
    
    print(f"Ключ:           {key_hex.upper()}")
    print(f"Открытый текст: {plaintext_hex.upper()}")
    
    # Шифрование
    ciphertext = aes_encrypt_block(list(plaintext), list(key))
    ciphertext_hex = "".join(f"{b:02X}" for b in ciphertext)
    print(f"Зашифровано:    {ciphertext_hex}")

if __name__ == "__main__":
    # Запуск тестов
    test_aes()
    demo_custom()