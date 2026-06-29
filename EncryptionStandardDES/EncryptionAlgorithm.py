# 4. Алгоритм шифрования
"""
Реализация алгоритма шифрования DES (Data Encryption Standard)
на основе предоставленного описания.
"""

# ==================== ТАБЛИЦЫ ПЕРЕСТАНОВОК ====================

# Начальная перестановка IP (Initial Permutation)
IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Обратная перестановка IP^-1 (Final Permutation)
IP_INV_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Перестановка с расширением E (Expansion Permutation)
E_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Перестановка P (Permutation P)
P_TABLE = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

# ==================== S-БЛОКИ ====================

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
    # S5
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

# ==================== РАСПИСАНИЕ КЛЮЧЕЙ ====================

# Таблица сжатия PC-1 (Permuted Choice 1) - 56 бит из 64
PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# Количество сдвигов для каждого раунда
SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Таблица сжатия PC-2 (Permuted Choice 2) - 48 бит из 56
PC2_TABLE = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def string_to_bits(text: str) -> list:
    """
    Преобразует строку в список битов (MSB first).
    Каждый символ кодируется в 8 бит (ASCII).
    """
    bits = []
    for char in text:
        byte = ord(char)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_string(bits: list) -> str:
    """
    Преобразует список битов обратно в строку.
    """
    if len(bits) % 8 != 0:
        raise ValueError("Длина битовой строки должна быть кратна 8")
    
    chars = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        chars.append(chr(byte))
    return ''.join(chars)

def bits_to_hex(bits: list) -> str:
    """Преобразует список битов в шестнадцатеричную строку."""
    if len(bits) % 4 != 0:
        raise ValueError("Длина битовой строки должна быть кратна 4")
    
    hex_chars = "0123456789ABCDEF"
    result = ""
    for i in range(0, len(bits), 4):
        val = 0
        for j in range(4):
            val = (val << 1) | bits[i + j]
        result += hex_chars[val]
    return result

def hex_to_bits(hex_str: str) -> list:
    """Преобразует шестнадцатеричную строку в список битов."""
    hex_str = hex_str.replace(" ", "").replace("0x", "")
    bits = []
    for ch in hex_str:
        val = int(ch, 16)
        for i in range(3, -1, -1):
            bits.append((val >> i) & 1)
    return bits

def permute(bits: list, table: list) -> list:
    """
    Выполняет перестановку битов согласно таблице.
    """
    return [bits[idx - 1] for idx in table]

def xor_bits(a: list, b: list) -> list:
    """Побитовое XOR двух списков битов."""
    return [x ^ y for x, y in zip(a, b)]

def split_bits(bits: list, n: int) -> tuple:
    """Разбивает список битов на две части."""
    return bits[:n], bits[n:]

def left_shift(bits: list, n: int = 1) -> list:
    """Циклический сдвиг влево на n позиций."""
    return bits[n:] + bits[:n]

def pad_to_64(bits: list) -> list:
    """Дополняет биты до 64, используя PKCS#7."""
    pad_len = 64 - (len(bits) % 64)
    if pad_len == 64:
        pad_len = 64
    return bits + [1] + [0] * (pad_len - 1)

def unpad_pkcs7(bits: list) -> list:
    """Удаляет PKCS#7 дополнение."""
    # Находим последний байт
    pad_len = 0
    for i in range(len(bits) - 8, len(bits)):
        pad_len = (pad_len << 1) | bits[i]
    
    if pad_len > 0:
        return bits[:-pad_len * 8]
    return bits

# ==================== ГЕНЕРАЦИЯ КЛЮЧЕЙ ====================

def generate_round_keys(key_bits: list) -> list:
    """
    Генерирует 16 раундовых ключей по 48 бит из 64-битного ключа.
    """
    if len(key_bits) != 64:
        raise ValueError("Ключ должен быть 64 бита")
    
    # Шаг 1: Применяем PC-1 (сжатие до 56 бит)
    key_56 = permute(key_bits, PC1_TABLE)
    
    # Шаг 2: Разбиваем на две половины по 28 бит
    C, D = split_bits(key_56, 28)
    
    round_keys = []
    
    for i in range(16):
        # Сдвигаем обе половины
        shift = SHIFT_SCHEDULE[i]
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        
        # Объединяем и применяем PC-2 (сжатие до 48 бит)
        combined = C + D
        round_key = permute(combined, PC2_TABLE)
        round_keys.append(round_key)
    
    return round_keys

# ==================== ФУНКЦИЯ F (ФЕЙСТЕЛЯ) ====================

def feistel_function(R: list, K: list) -> list:
    """
    Функция Фейстеля: f(R, K)
    """
    # 1. Расширение E: 32 -> 48 бит
    R_expanded = permute(R, E_TABLE)
    
    # 2. XOR с раундовым ключом
    R_xor = xor_bits(R_expanded, K)
    
    # 3. S-блоки: 48 -> 32 бита
    S_output = []
    for i in range(8):
        # Берем 6 бит
        block = R_xor[i * 6 : (i + 1) * 6]
        
        # Вычисляем строку и столбец
        r = (block[0] << 1) | block[5]
        c = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        
        # Получаем значение из S-блока
        val = S_BOXES[i][r][c]
        
        # Добавляем 4 бита
        for j in range(3, -1, -1):
            S_output.append((val >> j) & 1)
    
    # 4. Перестановка P: 32 -> 32 бита
    return permute(S_output, P_TABLE)

# ==================== ШИФРОВАНИЕ / РАСШИФРОВАНИЕ ====================

def des_encrypt_block(block_bits: list, round_keys: list) -> list:
    """
    Шифрует один 64-битный блок.
    """
    if len(block_bits) != 64:
        raise ValueError("Блок должен быть 64 бита")
    
    # 1. Начальная перестановка IP
    block = permute(block_bits, IP_TABLE)
    
    # 2. Разбиваем на L0 и R0
    L, R = split_bits(block, 32)
    
    # 3. 16 раундов
    for i in range(16):
        L_prev, R_prev = L, R
        R = xor_bits(L_prev, feistel_function(R_prev, round_keys[i]))
        L = R_prev
    
    # 4. Замена частей (L16 и R16 меняются местами)
    block = R + L
    
    # 5. Обратная перестановка IP^-1
    return permute(block, IP_INV_TABLE)

def des_decrypt_block(block_bits: list, round_keys: list) -> list:
    """
    Расшифровывает один 64-битный блок (ключи подаются в обратном порядке).
    """
    return des_encrypt_block(block_bits, round_keys[::-1])

# ==================== ОСНОВНЫЕ ФУНКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЯ ====================

def des_encrypt(plaintext: str, key: str) -> str:
    """
    Шифрует строку с использованием DES (ECB режим).
    Возвращает шестнадцатеричную строку.
    """
    # Преобразуем текст и ключ в биты
    plaintext_bits = string_to_bits(plaintext)
    key_bits = string_to_bits(key)
    
    # Дополняем ключ до 64 бит если нужно
    if len(key_bits) > 64:
        raise ValueError("Ключ не может быть длиннее 8 символов")
    while len(key_bits) < 64:
        key_bits.append(0)
    
    # Генерируем раундовые ключи
    round_keys = generate_round_keys(key_bits)
    
    # Дополняем текст до кратности 64 бит
    padded_bits = pad_to_64(plaintext_bits)
    
    # Шифруем по блокам
    cipher_bits = []
    for i in range(0, len(padded_bits), 64):
        block = padded_bits[i:i + 64]
        encrypted_block = des_encrypt_block(block, round_keys)
        cipher_bits.extend(encrypted_block)
    
    return bits_to_hex(cipher_bits)

def des_decrypt(cipher_hex: str, key: str) -> str:
    """
    Расшифровывает шестнадцатеричную строку, зашифрованную DES.
    """
    # Преобразуем данные в биты
    cipher_bits = hex_to_bits(cipher_hex)
    key_bits = string_to_bits(key)
    
    # Дополняем ключ до 64 бит если нужно
    if len(key_bits) > 64:
        raise ValueError("Ключ не может быть длиннее 8 символов")
    while len(key_bits) < 64:
        key_bits.append(0)
    
    # Генерируем раундовые ключи
    round_keys = generate_round_keys(key_bits)
    
    # Расшифровываем по блокам
    plain_bits = []
    for i in range(0, len(cipher_bits), 64):
        block = cipher_bits[i:i + 64]
        decrypted_block = des_decrypt_block(block, round_keys)
        plain_bits.extend(decrypted_block)
    
    # Удаляем дополнение
    unpadded_bits = unpad_pkcs7(plain_bits)
    
    return bits_to_string(unpadded_bits)

# ==================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ====================

if __name__ == "__main__":
    # Тестовый пример из описания DES
    print("=" * 60)
    print("ПРИМЕР ШИФРОВАНИЯ DES")
    print("=" * 60)
    
    # Ключ и текст из стандартного теста DES
    key = "key12345"  # 8 символов = 64 бита
    plaintext = "Hello DES"
    
    print(f"Исходный текст: {plaintext}")
    print(f"Ключ: {key}")
    print()
    
    # Шифрование
    encrypted = des_encrypt(plaintext, key)
    print(f"Зашифрованный текст (HEX): {encrypted}")
    print(f"Длина шифротекста: {len(encrypted)} символов HEX ({len(encrypted) // 2} байт)")
    print()
    
    # Расшифрование
    decrypted = des_decrypt(encrypted, key)
    print(f"Расшифрованный текст: {decrypted}")
    print()
    
    # Проверка
    if plaintext == decrypted:
        print("✅ Успешно! Шифрование и расшифрование работают корректно.")
    else:
        print("❌ Ошибка! Текст не совпадает.")
    
    print("=" * 60)
    
    # Дополнительный пример с более длинным текстом
    print("\nДОПОЛНИТЕЛЬНЫЙ ПРИМЕР (длинный текст):")
    long_text = "This is a longer text for DES encryption testing."
    encrypted_long = des_encrypt(long_text, key)
    decrypted_long = des_decrypt(encrypted_long, key)
    
    print(f"Исходный: {long_text}")
    print(f"HEX: {encrypted_long[:64]}...")  # Показываем только начало
    print(f"Расшифровано: {decrypted_long}")
    print(f"Совпадает: {'✅' if long_text == decrypted_long else '❌'}")