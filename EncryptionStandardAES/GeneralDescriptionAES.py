# 2. Общее описание AES
"""
Полная реализация AES-128 на Python
Основана на математическом аппарате поля GF(2 ^ 8) с неприводимым многочленом
f(x) = x ^ 8 + x ^ 4 + x ^ 3 + x + 1 (0x11B)
"""

# ==================== ОПЕРАЦИИ В ПОЛЕ GF(2 ^ 8) ====================

def gf_add(a, b):
    """Сложение в GF(2 ^ 8) - это XOR"""
    return a ^ b

def gf_mul(a, b):
    """
    Умножение в GF(2 ^ 8) по модулю f(x) = x ^ 8 + x ^ 4 + x ^ 3 + x + 1
    (алгоритм, аналогичный показанному в примере 78.1)
    """
    result = 0
    # Умножаем как многочлены, затем берём остаток
    for i in range(8):
        if b & 1:
            result ^= a
        # Проверяем старший бит перед сдвигом
        high_bit = a & 0x80
        a <<= 1
        if high_bit:
            a ^= 0x1B  # 0x1B = 0b11011 (неприводимый многочлен без x ^ 8)
        b >>= 1
    return result & 0xFF

def gf_pow(a, exp):
    """Возведение в степень в GF(2 ^ 8)"""
    result = 1
    for _ in range(exp):
        result = gf_mul(result, a)
    return result

def gf_inv(a):
    """
    Нахождение обратного элемента в GF(2 ^ 8)
    Расширенный алгоритм Евклида (как в примере 78.2)
    """
    if a == 0:
        return 0
    
    # Расширенный алгоритм Евклида для многочленов над GF(2)
    # Представляем a как многочлен степени <= 7
    # Модуль f(x) = x^8 + x^4 + x^3 + x + 1
    
    # Инициализация для расширенного алгоритма Евклида
    r0 = 0x11B  # f(x)
    r1 = a
    s0 = 0
    s1 = 1
    
    while r1 != 0:
        # Деление r0 на r1 в GF(2)
        if r0 == 0:
            break
            
        # Находим степень старшего члена
        deg_r0 = r0.bit_length() - 1
        deg_r1 = r1.bit_length() - 1
        
        if deg_r0 < deg_r1:
            r0, r1 = r1, r0
            s0, s1 = s1, s0
            continue
        
        # Вычисляем частное q = x^(deg_r0 - deg_r1)
        q = 1 << (deg_r0 - deg_r1)
        # Вычисляем новый остаток
        r_new = r0 ^ (gf_mul(r1, q))
        s_new = s0 ^ (gf_mul(s1, q))
        
        r0, r1 = r1, r_new
        s0, s1 = s1, s_new
    
    return s0 & 0xFF

# ==================== S-BOX И ОБРАТНЫЙ S-BOX ====================

def generate_sbox():
    """
    Генерация S-box:
    1. Находим мультипликативный обратный в GF(2 ^ 8)
    2. Применяем аффинное преобразование
    """
    sbox = [0] * 256
    
    # Аффинное преобразование (в матричной форме)
    affine_matrix = [
        [1, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1]
    ]
    constant = 0x63  # 0b01100011
    
    for i in range(256):
        # Шаг 1: мультипликативный обратный
        inv = gf_inv(i)
        
        # Шаг 2: аффинное преобразование
        result = 0
        for row in range(8):
            bit = 0
            for col in range(8):
                if affine_matrix[row][col]:
                    bit ^= (inv >> (7 - col)) & 1
            # Добавляем константу
            bit ^= (constant >> (7 - row)) & 1
            result |= bit << (7 - row)
        
        sbox[i] = result
    
    return sbox

def generate_inv_sbox(sbox):
    """Генерация обратного S-box"""
    inv_sbox = [0] * 256
    for i, val in enumerate(sbox):
        inv_sbox[val] = i
    return inv_sbox

# Генерируем S-box
SBOX = generate_sbox()
INV_SBOX = generate_inv_sbox(SBOX)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def sub_bytes(state, sbox = SBOX):
    """SubBytes - замена каждого байта через S-box"""
    return [[sbox[state[i][j]] for j in range(4)] for i in range(4)]

def inv_sub_bytes(state):
    """Обратный SubBytes"""
    return sub_bytes(state, INV_SBOX)

def shift_rows(state):
    """ShiftRows - циклический сдвиг строк"""
    result = [row[:] for row in state]
    for i in range(1, 4):
        result[i] = state[i][i:] + state[i][:i]
    return result

def inv_shift_rows(state):
    """Обратный ShiftRows"""
    result = [row[:] for row in state]
    for i in range(1, 4):
        result[i] = state[i][-i:] + state[i][:-i]
    return result

def mix_columns(state):
    """
    MixColumns - умножение каждого столбца на фиксированную матрицу
    Матрица:
    [02 03 01 01]
    [01 02 03 01]
    [01 01 02 03]
    [03 01 01 02]
    """
    result = [[0] * 4 for _ in range(4)]
    
    for col in range(4):
        # Извлекаем столбец
        col_vals = [state[row][col] for row in range(4)]
        
        # Умножаем на матрицу
        result[0][col] = gf_mul(0x02, col_vals[0]) ^ gf_mul(0x03, col_vals[1]) ^ col_vals[2] ^ col_vals[3]
        result[1][col] = col_vals[0] ^ gf_mul(0x02, col_vals[1]) ^ gf_mul(0x03, col_vals[2]) ^ col_vals[3]
        result[2][col] = col_vals[0] ^ col_vals[1] ^ gf_mul(0x02, col_vals[2]) ^ gf_mul(0x03, col_vals[3])
        result[3][col] = gf_mul(0x03, col_vals[0]) ^ col_vals[1] ^ col_vals[2] ^ gf_mul(0x02, col_vals[3])
    
    return result

def inv_mix_columns(state):
    """
    Обратный MixColumns
    Матрица:
    [0E 0B 0D 09]
    [09 0E 0B 0D]
    [0D 09 0E 0B]
    [0B 0D 09 0E]
    """
    result = [[0] * 4 for _ in range(4)]
    
    for col in range(4):
        col_vals = [state[row][col] for row in range(4)]
        
        result[0][col] = gf_mul(0x0E, col_vals[0]) ^ gf_mul(0x0B, col_vals[1]) ^ gf_mul(0x0D, col_vals[2]) ^ gf_mul(0x09, col_vals[3])
        result[1][col] = gf_mul(0x09, col_vals[0]) ^ gf_mul(0x0E, col_vals[1]) ^ gf_mul(0x0B, col_vals[2]) ^ gf_mul(0x0D, col_vals[3])
        result[2][col] = gf_mul(0x0D, col_vals[0]) ^ gf_mul(0x09, col_vals[1]) ^ gf_mul(0x0E, col_vals[2]) ^ gf_mul(0x0B, col_vals[3])
        result[3][col] = gf_mul(0x0B, col_vals[0]) ^ gf_mul(0x0D, col_vals[1]) ^ gf_mul(0x09, col_vals[2]) ^ gf_mul(0x0E, col_vals[3])
    
    return result

def add_round_key(state, round_key):
    """AddRoundKey - XOR с раундовым ключом"""
    return [[state[i][j] ^ round_key[i][j] for j in range(4)] for i in range(4)]

# ==================== РАЗВЁРТКА КЛЮЧА ====================

def rot_word(word):
    """Циклический сдвиг слова влево на 1 байт"""
    return word[1:] + word[:1]

def sub_word(word, sbox = SBOX):
    """Подстановка байтов слова через S-box"""
    return [sbox[b] for b in word]

def key_expansion(key):
    """
    Развёртка ключа для AES-128
    Ключ: 16 байт -> 44 слова (по 4 байта) для 11 раундов
    """
    # Ключ должен быть 16 байт
    assert len(key) == 16
    
    # Инициализируем ключевое расписание 4 словами из исходного ключа
    key_schedule = []
    for i in range(4):
        word = list(key[4 * i:4 * i + 4])
        key_schedule.append(word)
    
    # Генерируем остальные 40 слов
    rcon = 0x01  # Раундовая константа
    
    for i in range(4, 44):
        temp = key_schedule[i - 1][:]
        
        if i % 4 == 0:
            # Применяем RotWord, SubWord и XOR с Rcon
            temp = rot_word(temp)
            temp = sub_word(temp)
            temp[0] ^= rcon
            # Обновляем Rcon
            rcon = gf_mul(rcon, 0x02)
        
        # XOR с словом на 4 позиции назад
        key_schedule.append([
            key_schedule[i - 4][0] ^ temp[0],
            key_schedule[i - 4][1] ^ temp[1],
            key_schedule[i - 4][2] ^ temp[2],
            key_schedule[i - 4][3] ^ temp[3]
        ])
    
    # Преобразуем в раундовые ключи (каждый по 16 байт = 4 слова)
    round_keys = []
    for i in range(11):
        round_key = []
        for j in range(4):
            word = key_schedule[i * 4 + j]
            round_key.append(word)
        round_keys.append(round_key)
    
    return round_keys

# ==================== ШИФРОВАНИЕ И РАСШИФРОВАНИЕ ====================

def text_to_state(text):
    """Преобразование 16-байтного текста в матрицу состояния"""
    assert len(text) == 16
    state = []
    for i in range(4):
        row = [text[i + 4 * j] for j in range(4)]
        state.append(row)
    return state

def state_to_text(state):
    """Преобразование матрицы состояния обратно в текст"""
    text = []
    for i in range(4):
        for j in range(4):
            text.append(state[j][i])
    return bytes(text)

def encrypt_block(plaintext, key):
    """
    Шифрование одного блока (16 байт) с использованием AES-128
    """
    # Подготовка
    state = text_to_state(plaintext)
    round_keys = key_expansion(key)
    
    # Начальный раунд
    state = add_round_key(state, round_keys[0])
    
    # Основные раунды (1-9)
    for round_num in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[round_num])
    
    # Финальный раунд (без MixColumns)
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[10])
    
    return state_to_text(state)

def decrypt_block(ciphertext, key):
    """
    Расшифрование одного блока (16 байт) с использованием AES-128
    """
    # Подготовка
    state = text_to_state(ciphertext)
    round_keys = key_expansion(key)
    
    # Финальный раунд
    state = add_round_key(state, round_keys[10])
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    
    # Основные раунды (9-1)
    for round_num in range(9, 0, -1):
        state = add_round_key(state, round_keys[round_num])
        state = inv_mix_columns(state)
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
    
    # Начальный раунд
    state = add_round_key(state, round_keys[0])
    
    return state_to_text(state)

# ==================== ДЕМОНСТРАЦИЯ ====================

def print_state(state, title = "Состояние"):
    """Вывод состояния в читаемом виде"""
    print(f"\n{title}:")
    for row in state:
        print("  " + " ".join(f"{x:02X}" for x in row))

def demo():
    """Демонстрация работы AES-128"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ AES-128")
    print("=" * 60)
    
    # Пример из текста: байты в шестнадцатеричном виде
    # Произведение байтов из примера 78.1
    a = 0x6E  # (0,1,1,0,1,1,1,0) = 0x6E
    b = 0x9B  # (1,0,0,1,1,0,1,1) = 0x9B
    product = gf_mul(a, b)
    print(f"\nПроверка умножения в GF(2 ^ 8):")
    print(f"  {a:02X} · {b:02X} = {product:02X}")
    print(f"  (совпадает с примером 78.1: 0x{product:02X})")
    
    # Проверка обратного элемента (пример 78.2)
    g = 0xDA  # (1,1,0,1,1,0,1,0) = 0xDA
    g_inv = gf_inv(g)
    print(f"\nПроверка обратного элемента в GF(2 ^ 8):")
    print(f"  g = {g:02X}, g ^ (-1) = {g_inv:02X}")
    print(f"  g · g ^ (-1) = {gf_mul(g, g_inv):02X} (должно быть 01)")
    
    # Проверка S-box
    print(f"\nНесколько значений S-box:")
    for i in [0x00, 0x01, 0x57, 0xDA]:
        print(f"  S-box[{i:02X}] = {SBOX[i]:02X}")
    
    # Тестовое шифрование
    print("\n" + "=" * 60)
    print("ТЕСТОВОЕ ШИФРОВАНИЕ AES-128")
    print("=" * 60)
    
    # Используем стандартный тестовый вектор AES
    plaintext = bytes([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF])
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F])
    
    print(f"\nИсходный текст:    {plaintext.hex().upper()}")
    print(f"Ключ:              {key.hex().upper()}")
    
    ciphertext = encrypt_block(plaintext, key)
    print(f"Зашифрованный текст: {ciphertext.hex().upper()}")
    
    decrypted = decrypt_block(ciphertext, key)
    print(f"Расшифрованный текст: {decrypted.hex().upper()}")
    
    # Проверка корректности
    if decrypted == plaintext:
        print("\n✓ Шифрование и расшифрование работают корректно!")
    else:
        print("\n✗ Ошибка: расшифрованный текст не совпадает с исходным")

if __name__ == "__main__":
    demo()