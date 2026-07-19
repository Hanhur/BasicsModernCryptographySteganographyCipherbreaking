# Алгоритмы DES
"""
Реализация алгоритма DES (Data Encryption Standard)
Без использования внешних библиотек (numpy, pycryptodome и т.д.)
Только встроенные средства Python

Шифрование одного 64-битного блока (8 байт)
"""

# ==================== ТАБЛИЦЫ ПЕРЕСТАНОВОК ====================

# Начальная перестановка (IP) - 64 бита -> 64 бита
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

# Обратная перестановка (IP⁻¹) - 64 бита -> 64 бита
INV_IP_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Таблица расширения (E) - 32 бита -> 48 бит
EXPANSION_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Перестановка P - 32 бита -> 32 бита
P_TABLE = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# S-блоки (8 блоков по 4x16)
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

# Таблица сжатия ключа PC-1 (56 бит из 64)
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

# Таблица сжатия ключа PC-2 (48 бит из 56)
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

# Количество сдвигов для каждого раунда (16 раундов)
SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def string_to_bits(text: str, length: int = 64) -> str:
    """
    Преобразует строку в битовую строку.
    Каждый символ -> 8 бит (ASCII).
    """
    bits = ''.join(format(ord(c), '08b') for c in text)
    if len(bits) < length:
        # Дополняем пробелами до нужной длины
        text += ' ' * ((length - len(bits)) // 8)
        bits = ''.join(format(ord(c), '08b') for c in text)
    return bits[:length]


def bits_to_string(bits: str) -> str:
    """Преобразует битовую строку обратно в строку (по 8 бит -> символ)."""
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def hex_to_bits(hex_str: str) -> str:
    """Преобразует шестнадцатеричную строку в битовую."""
    return ''.join(format(int(c, 16), '04b') for c in hex_str)


def bits_to_hex(bits: str) -> str:
    """Преобразует битовую строку в шестнадцатеричную."""
    hex_str = ''
    for i in range(0, len(bits), 4):
        chunk = bits[i:i + 4]
        if len(chunk) == 4:
            hex_str += format(int(chunk, 2), 'x')
    return hex_str


def permute(bits: str, table: list) -> str:
    """
    Выполняет перестановку битов согласно таблице.
    bits: битовая строка
    table: список индексов (нумерация с 1)
    """
    return ''.join(bits[i - 1] for i in table)


def xor_bits(a: str, b: str) -> str:
    """Побитовое XOR двух битовых строк одинаковой длины."""
    return ''.join('1' if x != y else '0' for x, y in zip(a, b))


def left_shift(bits: str, n: int) -> str:
    """Циклический сдвиг влево на n позиций."""
    return bits[n:] + bits[:n]


def split_half(bits: str) -> tuple:
    """Разделяет битовую строку на две половины."""
    mid = len(bits) // 2
    return bits[:mid], bits[mid:]


# ==================== ФУНКЦИЯ РАУНДА ====================

def s_box_substitution(bits_48: str) -> str:
    """
    Подстановка через S-блоки.
    Вход: 48 бит (8 групп по 6 бит)
    Выход: 32 бита (8 групп по 4 бита)
    """
    result = ''
    for i in range(8):
        # Берем 6 бит для i-го S-блока
        chunk = bits_48[i * 6:(i + 1) * 6]
        
        # Строка: биты 0 и 5 (первый и последний)
        row = int(chunk[0] + chunk[5], 2)
        # Столбец: биты 1, 2, 3, 4 (средние 4)
        col = int(chunk[1:5], 2)
        
        # Получаем значение из S-блока
        sbox_value = S_BOXES[i][row][col]
        
        # Преобразуем в 4 бита
        result += format(sbox_value, '04b')
    
    return result


def des_round(left: str, right: str, round_key: str) -> tuple:
    """
    Один раунд сети Фейстеля.
    left: 32 бита
    right: 32 бита
    round_key: 48 бит
    Возвращает (new_left, new_right)
    """
    # 1. Расширение правой половины с 32 до 48 бит
    expanded_right = permute(right, EXPANSION_TABLE)
    
    # 2. XOR с раундовым ключом
    xored = xor_bits(expanded_right, round_key)
    
    # 3. Подстановка через S-блоки (48 -> 32)
    substituted = s_box_substitution(xored)
    
    # 4. Перестановка P (32 -> 32)
    permuted = permute(substituted, P_TABLE)
    
    # 5. XOR с левой половиной (результат - новая правая половина)
    new_right = xor_bits(left, permuted)
    
    # 6. Новая левая половина - это старая правая
    new_left = right
    
    return new_left, new_right


# ==================== ГЕНЕРАЦИЯ КЛЮЧЕЙ ====================

def generate_round_keys(key_bits: str) -> list:
    """
    Генерирует 16 раундовых ключей по 48 бит из 64-битного ключа.
    Возвращает список из 16 строк по 48 бит.
    """
    # 1. Сжатие ключа PC-1 (64 -> 56)
    key_56 = permute(key_bits, PC1_TABLE)
    
    # 2. Разделение на C0 и D0 (по 28 бит)
    c, d = split_half(key_56)
    
    round_keys = []
    for shift in SHIFT_SCHEDULE:
        # 3. Циклический сдвиг влево
        c = left_shift(c, shift)
        d = left_shift(d, shift)
        
        # 4. Сжатие PC-2 (56 -> 48) для получения раундового ключа
        combined = c + d
        round_key = permute(combined, PC2_TABLE)
        round_keys.append(round_key)
    
    return round_keys


# ==================== ОСНОВНАЯ ФУНКЦИЯ DES ====================

def des_encrypt_block(plaintext_bits: str, key_bits: str, debug: bool = False) -> str:
    """
    Шифрует один 64-битный блок с помощью DES.
    plaintext_bits: 64 бита
    key_bits: 64 бита (используется 56)
    debug: печатать промежуточные результаты
    """
    if len(plaintext_bits) != 64 or len(key_bits) != 64:
        raise ValueError("Входные данные и ключ должны быть ровно 64 бита")
    
    # 1. Генерация раундовых ключей
    round_keys = generate_round_keys(key_bits)
    
    # 2. Начальная перестановка IP
    ip_bits = permute(plaintext_bits, IP_TABLE)
    left, right = split_half(ip_bits)
    
    if debug:
        print(f"Начальная перестановка: {bits_to_hex(ip_bits)}")
        print(f"L0 = {bits_to_hex(left)}, R0 = {bits_to_hex(right)}")
        print("-" * 50)
    
    # 3. 16 раундов
    for i in range(16):
        left, right = des_round(left, right, round_keys[i])
        if debug:
            print(f"Раунд {i + 1:2d}: L = {bits_to_hex(left)}, R = {bits_to_hex(right)}")
    
    # 4. Финальная перестановка (после 16 раундов меняем местами L и R)
    combined = right + left  # Важно: перед IP⁻¹ меняем местами!
    ciphertext_bits = permute(combined, INV_IP_TABLE)
    
    return ciphertext_bits


def des_decrypt_block(ciphertext_bits: str, key_bits: str, debug: bool = False) -> str:
    """
    Расшифровывает один 64-битный блок с помощью DES.
    Использует те же раунды, но ключи в обратном порядке.
    """
    if len(ciphertext_bits) != 64 or len(key_bits) != 64:
        raise ValueError("Входные данные и ключ должны быть ровно 64 бита")
    
    # 1. Генерация раундовых ключей
    round_keys = generate_round_keys(key_bits)
    
    # 2. Начальная перестановка IP
    ip_bits = permute(ciphertext_bits, IP_TABLE)
    left, right = split_half(ip_bits)
    
    if debug:
        print(f"Начальная перестановка (расшифр): {bits_to_hex(ip_bits)}")
        print(f"L0 = {bits_to_hex(left)}, R0 = {bits_to_hex(right)}")
        print("-" * 50)
    
    # 3. 16 раундов с обратным порядком ключей
    for i in range(16):
        left, right = des_round(left, right, round_keys[15 - i])
        if debug:
            print(f"Раунд {i + 1:2d}: L = {bits_to_hex(left)}, R = {bits_to_hex(right)}")
    
    # 4. Финальная перестановка
    combined = right + left
    plaintext_bits = permute(combined, INV_IP_TABLE)
    
    return plaintext_bits


# ==================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ====================

def main():
    print("=" * 60)
    print("DES (Data Encryption Standard) - реализация на чистом Python")
    print("=" * 60)
    
    # Пример 1: Шифрование короткой строки
    print("\n[Пример 1] Шифрование строки 'HELLO'")
    print("-" * 40)
    
    # Подготавливаем 64 бита (8 байт)
    plaintext = "HELLO   "  # 8 символов (HELLO + 3 пробела)
    key = "12345678"        # 8 символов
    
    plaintext_bits = string_to_bits(plaintext, 64)
    key_bits = string_to_bits(key, 64)
    
    print(f"Открытый текст: '{plaintext}'")
    print(f"Ключ: '{key}'")
    print(f"Открытый текст (hex): {bits_to_hex(plaintext_bits)}")
    print(f"Ключ (hex): {bits_to_hex(key_bits)}")
    print()
    
    # Шифрование
    ciphertext_bits = des_encrypt_block(plaintext_bits, key_bits)
    ciphertext_hex = bits_to_hex(ciphertext_bits)
    print(f"Шифротекст (hex): {ciphertext_hex}")
    
    # Расшифрование
    decrypted_bits = des_decrypt_block(ciphertext_bits, key_bits)
    decrypted_text = bits_to_string(decrypted_bits)
    print(f"Расшифрованный текст: '{decrypted_text}'")
    
    # Проверка
    print(f"\n✅ Корректность: {'ДА' if decrypted_text == plaintext else 'НЕТ'}")
    
    # Пример 2: С подробным выводом
    print("\n" + "=" * 60)
    print("[Пример 2] Шифрование с отладочным выводом")
    print("=" * 60)
    
    test_plaintext = "ABCDEFGH"
    test_key = "12345678"
    
    pt_bits = string_to_bits(test_plaintext, 64)
    key_bits = string_to_bits(test_key, 64)
    
    print(f"\nИсходные данные:")
    print(f"  Plaintext: {test_plaintext}")
    print(f"  Plaintext (hex): {bits_to_hex(pt_bits)}")
    print(f"  Key: {test_key}")
    print(f"  Key (hex): {bits_to_hex(key_bits)}")
    print("\n--- ПРОЦЕСС ШИФРОВАНИЯ ---")
    
    cipher = des_encrypt_block(pt_bits, key_bits, debug = True)
    print(f"\nИтоговый шифротекст (hex): {bits_to_hex(cipher)}")
    
    # Пример 3: Работа с битами (математический тест)
    print("\n" + "=" * 60)
    print("[Пример 3] Математический тест - известный вектор")
    print("=" * 60)
    
    # Известный тестовый вектор (из стандарта)
    # Plaintext: 0x0123456789ABCDEF
    # Key: 0x133457799BBCDFF1
    # Ciphertext: 0x85E813540F0AB405
    
    test_pt_hex = "0123456789abcdef"
    test_key_hex = "133457799bbcdfF1"
    expected_ct_hex = "85e813540f0ab405"
    
    test_pt_bits = hex_to_bits(test_pt_hex.lower())
    test_key_bits = hex_to_bits(test_key_hex.lower())
    
    print(f"Входной блок (hex): {test_pt_hex}")
    print(f"Ключ (hex): {test_key_hex}")
    print(f"Ожидаемый шифротекст (hex): {expected_ct_hex}")
    
    result_bits = des_encrypt_block(test_pt_bits, test_key_bits)
    result_hex = bits_to_hex(result_bits)
    
    print(f"Полученный шифротекст (hex): {result_hex}")
    print(f"\n✅ Совпадение с эталоном: {'ДА' if result_hex == expected_ct_hex else 'НЕТ'}")
    
    print("\n" + "=" * 60)
    print("Программа завершена.")


if __name__ == "__main__":
    main()