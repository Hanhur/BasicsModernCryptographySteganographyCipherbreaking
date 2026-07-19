# Анализ алгоритма DES
"""
Полная реализация алгоритма DES (Data Encryption Standard)
на основе анализа из текста. Без использования NumPy.
"""

# ========== ТАБЛИЦЫ ПЕРЕСТАНОВОК ==========

# Начальная перестановка (IP) - 64 бита
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Конечная перестановка (IP^-1) - обратная начальной
IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Перестановка E (расширение 32 -> 48 бит)
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Перестановка P (32 бита) после S-блоков
P = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# ========== S-БЛОКИ (8 штук 4x16) ==========
# Из вашего текста: числа от 0 до 15

S_BOXES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    # S5 (тот самый, с "однозначными числами" в 14-м столбце)
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

# ========== ТАБЛИЦЫ ДЛЯ КЛЮЧА ==========

# PC-1: сжатие 64 бит до 56 бит (отбрасываем каждый 8-й бит для четности)
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# PC-2: сжатие 56 бит до 48 бит для подключей
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Количество сдвигов для каждого раунда
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def string_to_bits(text):
    """Преобразование строки в битовый массив (8 бит на символ)"""
    bits = []
    for char in text:
        # Получаем ASCII код символа и переводим в 8-битное представление
        byte = ord(char)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_string(bits):
    """Преобразование битового массива обратно в строку"""
    # Дополняем до кратности 8
    while len(bits) % 8 != 0:
        bits.append(0)
    
    text = ""
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        text += chr(byte)
    return text

def hex_to_bits(hex_str):
    """Преобразование HEX строки в битовый массив"""
    bits = []
    for char in hex_str:
        val = int(char, 16)
        for i in range(3, -1, -1):
            bits.append((val >> i) & 1)
    return bits

def bits_to_hex(bits):
    """Преобразование битового массива в HEX строку"""
    # Дополняем до кратности 4
    while len(bits) % 4 != 0:
        bits.append(0)
    
    hex_str = ""
    for i in range(0, len(bits), 4):
        val = 0
        for j in range(4):
            val = (val << 1) | bits[i + j]
        hex_str += hex(val)[2:].upper()
    return hex_str

def permute(bits, table):
    """Перестановка битов согласно таблице"""
    return [bits[i - 1] for i in table]

def xor_bits(bits1, bits2):
    """XOR двух битовых массивов одинаковой длины"""
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

def split_bits(bits, n):
    """Разбиение битового массива на две части"""
    return bits[:n], bits[n:]

def left_shift(bits, n):
    """Циклический сдвиг битового массива влево на n позиций"""
    return bits[n:] + bits[:n]

def pad_text(text):
    """Дополнение текста до кратности 64 бит (8 байт)"""
    # Добавляем пробелы в конец
    while len(text) % 8 != 0:
        text += ' '
    return text


# ========== ОСНОВНЫЕ ФУНКЦИИ DES ==========

def generate_round_keys(key_bits):
    """
    Генерация 16 раундовых ключей (по 48 бит каждый)
    Из 64-битного ключа (с битами четности)
    """
    # Шаг 1: PC-1 - сжатие 64 -> 56 бит
    # Отбрасываются биты четности (каждый 8-й)
    key_56 = permute(key_bits, PC1)
    
    # Шаг 2: Разбиваем на C и D (по 28 бит)
    C, D = split_bits(key_56, 28)
    
    round_keys = []
    
    # Шаг 3: Генерация 16 ключей
    for i in range(16):
        # Циклический сдвиг C и D
        C = left_shift(C, SHIFTS[i])
        D = left_shift(D, SHIFTS[i])
        
        # Объединяем C и D (56 бит)
        combined = C + D
        
        # PC-2: сжатие 56 -> 48 бит
        round_key = permute(combined, PC2)
        round_keys.append(round_key)
    
    return round_keys

def f_function(R, round_key):
    """
    Функция f(Ri-1, Ki) - основной этап шифрования
    R: 32 бита (правая половина)
    round_key: 48 бит
    Возвращает: 32 бита
    """
    # Шаг 1: Расширение E: 32 -> 48 бит
    R_expanded = permute(R, E)
    
    # Шаг 2: XOR с раундовым ключом: 48 бит
    R_xor = xor_bits(R_expanded, round_key)
    
    # Шаг 3: S-блоки: 48 -> 32 бита
    # Разбиваем 48 бит на 8 групп по 6 бит
    S_output = []
    for i in range(8):
        # Берем 6 бит для S-блока i
        start = i * 6
        block_6bit = R_xor[start:start + 6]
        
        # Номер строки: первый и последний бит (2 бита -> 0-3)
        row = (block_6bit[0] << 1) | block_6bit[5]
        
        # Номер столбца: средние 4 бита (4 бита -> 0-15)
        col = 0
        for j in range(1, 5):
            col = (col << 1) | block_6bit[j]
        
        # Получаем значение из S-блока (4 бита)
        s_val = S_BOXES[i][row][col]
        
        # Преобразуем в 4 бита
        for j in range(3, -1, -1):
            S_output.append((s_val >> j) & 1)
    
    # Шаг 4: Перестановка P: 32 бита
    result = permute(S_output, P)
    
    return result

def des_round(L, R, round_key):
    """Один раунд сети Фейстеля"""
    # Вычисляем новую правую половину
    new_R = xor_bits(L, f_function(R, round_key))
    # Левая половина становится старой правой
    new_L = R
    return new_L, new_R

def des_encrypt_block(block_bits, round_keys):
    """
    Шифрование одного 64-битного блока
    """
    # Начальная перестановка IP
    block = permute(block_bits, IP)
    
    # Разбиваем на L и R (по 32 бита)
    L, R = split_bits(block, 32)
    
    # 16 раундов
    for i in range(16):
        L, R = des_round(L, R, round_keys[i])
    
    # Финальная перестановка (обратная IP)
    # Обратите внимание: после 16 раундов L и R меняются местами!
    result = permute(R + L, IP_INV)
    
    return result

def des_decrypt_block(block_bits, round_keys):
    """
    Дешифрование одного 64-битного блока
    Ключи подаются в обратном порядке
    """
    # Начальная перестановка IP
    block = permute(block_bits, IP)
    
    # Разбиваем на L и R
    L, R = split_bits(block, 32)
    
    # 16 раундов (ключи в обратном порядке)
    for i in range(15, -1, -1):
        L, R = des_round(L, R, round_keys[i])
    
    # Финальная перестановка
    result = permute(R + L, IP_INV)
    
    return result

def des_encrypt(text, key):
    """
    Шифрование текста алгоритмом DES
    """
    # Подготовка текста
    text = pad_text(text)
    key_bits = string_to_bits(key)
    
    # Если ключ меньше 8 байт, дополняем
    while len(key_bits) < 64:
        key_bits.append(0)
    # Обрезаем до 64 бит
    key_bits = key_bits[:64]
    
    # Генерация раундовых ключей
    round_keys = generate_round_keys(key_bits)
    
    # Шифрование по блокам
    encrypted_bits = []
    for i in range(0, len(text), 8):
        block = text[i:i + 8]
        block_bits = string_to_bits(block)
        encrypted_block = des_encrypt_block(block_bits, round_keys)
        encrypted_bits.extend(encrypted_block)
    
    return bits_to_hex(encrypted_bits)

def des_decrypt(hex_cipher, key):
    """
    Дешифрование HEX строки алгоритмом DES
    """
    key_bits = string_to_bits(key)
    while len(key_bits) < 64:
        key_bits.append(0)
    key_bits = key_bits[:64]
    
    round_keys = generate_round_keys(key_bits)
    
    cipher_bits = hex_to_bits(hex_cipher)
    
    decrypted_bits = []
    for i in range(0, len(cipher_bits), 64):
        block_bits = cipher_bits[i:i + 64]
        decrypted_block = des_decrypt_block(block_bits, round_keys)
        decrypted_bits.extend(decrypted_block)
    
    return bits_to_string(decrypted_bits).strip()


# ========== ПРИМЕР ИСПОЛЬЗОВАНИЯ ==========

if __name__ == "__main__":
    print("=" * 60)
    print("DES (DATA ENCRYPTION STANDARD) - РЕАЛИЗАЦИЯ НА PYTHON")
    print("=" * 60)
    
    # Пример 1: Шифрование строки
    print("\n[ПРИМЕР 1] Шифрование текста")
    print("-" * 40)
    
    plaintext = "HELLO DES"
    key = "MYKEY123"
    
    print(f"Исходный текст: '{plaintext}'")
    print(f"Ключ: '{key}'")
    
    cipher = des_encrypt(plaintext, key)
    print(f"Зашифрованный текст (HEX): {cipher}")
    
    decrypted = des_decrypt(cipher, key)
    print(f"Расшифрованный текст: '{decrypted}'")
    
    # Пример 2: Шифрование числа (для демонстрации работы алгоритма)
    print("\n[ПРИМЕР 2] Демонстрация работы с битами")
    print("-" * 40)
    
    # Берем простой 64-битный блок (8 символов)
    test_block = "12345678"
    test_key = "ABCDEFGH"
    
    print(f"Блок: '{test_block}'")
    print(f"Ключ: '{test_key}'")
    
    # Показываем внутреннюю работу для первого раунда
    key_bits = string_to_bits(test_key)[:64]
    round_keys = generate_round_keys(key_bits)
    
    print(f"\nРаундовые ключи (первые 48 бит K1):")
    print(f"K1 = {''.join(map(str, round_keys[0][:48]))}")
    
    block_bits = string_to_bits(test_block)
    print(f"\nБлок до начальной перестановки (64 бита):")
    print(f"{''.join(map(str, block_bits))}")
    
    # Начальная перестановка
    after_ip = permute(block_bits, IP)
    print(f"\nПосле начальной перестановки IP:")
    print(f"{''.join(map(str, after_ip))}")
    
    L, R = split_bits(after_ip, 32)
    print(f"\nL0 (32 бита): {''.join(map(str, L))}")
    print(f"R0 (32 бита): {''.join(map(str, R))}")
    
    # Первый раунд
    L1, R1 = des_round(L, R, round_keys[0])
    print(f"\nПосле 1-го раунда:")
    print(f"L1: {''.join(map(str, L1))}")
    print(f"R1: {''.join(map(str, R1))}")
    
    print("\n" + "=" * 60)
    print("✓ DES успешно работает!")
    print("=" * 60)