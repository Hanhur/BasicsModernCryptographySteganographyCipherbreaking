# 3. Генерация раундовых ключей
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерация раундовых ключей DES (Data Encryption Standard)
На основе описания из задания
"""

# Таблица начальной перестановки PC-1 (56 бит на выходе)
# Отбрасываются биты 8, 16, 24, 32, 40, 48, 56, 64
PC1 = [
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4
]

# Таблица сжатия PC-2 (48 бит на выходе из 56)
PC2 = [
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Количество сдвигов для каждого раунда (1..16)
SHIFT_SCHEDULE = [
    1, 1, 2, 2, 2, 2, 2, 2,
    1, 2, 2, 2, 2, 2, 2, 1
]


def string_to_bits(text):
    """
    Преобразует строку (текст) в битовую строку.
    Каждый символ кодируется 8 битами (ASCII).
    """
    bits = []
    for char in text:
        # Получаем 8-битное представление символа
        byte = ord(char)
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_string(bits):
    """Преобразует битовую строку обратно в текст."""
    chars = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bits):
                byte = (byte << 1) | bits[i + j]
        chars.append(chr(byte))
    return ''.join(chars)


def hex_key_to_bits(hex_key):
    """
    Преобразует 16-символьную шестнадцатеричную строку в 64 бита.
    Пример: "0123456789ABCDEF" -> 64 бита
    """
    bits = []
    for char in hex_key:
        val = int(char, 16)
        for i in range(3, -1, -1):
            bits.append((val >> i) & 1)
    return bits


def bits_to_hex(bits):
    """Преобразует биты в шестнадцатеричную строку."""
    hex_str = ""
    for i in range(0, len(bits), 4):
        val = 0
        for j in range(4):
            if i + j < len(bits):
                val = (val << 1) | bits[i + j]
        hex_str += hex(val)[2:].upper()
    return hex_str


def apply_permutation(bits, table):
    """
    Применяет перестановку к битам согласно таблице.
    table содержит индексы (1-based) битов в исходной последовательности.
    """
    result = []
    for pos in table:
        # В таблице индексы идут с 1, поэтому вычитаем 1
        result.append(bits[pos - 1])
    return result


def left_shift(bits, shift_count):
    """Выполняет циклический сдвиг влево на shift_count позиций."""
    return bits[shift_count:] + bits[:shift_count]


def generate_round_keys(initial_key):
    """
    Генерирует 16 раундовых ключей из 64-битного исходного ключа.
    initial_key: список из 64 бит (0 или 1)
    Возвращает: список из 16 ключей, каждый по 48 бит
    """
    # 1. Применяем перестановку PC-1 (сжатие до 56 бит)
    key56 = apply_permutation(initial_key, PC1)
    
    # 2. Разбиваем на две половины по 28 бит
    C = key56[:28]
    D = key56[28:]
    
    round_keys = []
    
    # 3. Генерируем 16 раундовых ключей
    for i in range(16):
        shift = SHIFT_SCHEDULE[i]
        
        # Циклический сдвиг влево
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        
        # Объединяем C и D (получаем 56 бит)
        combined = C + D
        
        # Применяем PC-2 (сжатие до 48 бит)
        key48 = apply_permutation(combined, PC2)
        round_keys.append(key48)
    
    return round_keys


def print_key_info(key_bits, label=""):
    """Выводит информацию о ключе в читаемом виде."""
    if label:
        print(f"\n{label}")
    print(f"  Битовая строка: {''.join(str(b) for b in key_bits)}")
    print(f"  Длина: {len(key_bits)} бит")
    print(f"  HEX: {bits_to_hex(key_bits)}")
    
    # Для 64-битных ключей показываем и ASCII
    if len(key_bits) == 64:
        try:
            text = bits_to_string(key_bits)
            if all(32 <= ord(c) <= 126 for c in text):
                print(f"  ASCII: {text}")
        except:
            pass


def main():
    """Пример использования."""
    
    print("=" * 70)
    print("ГЕНЕРАЦИЯ РАУНДОВЫХ КЛЮЧЕЙ DES")
    print("=" * 70)
    
    # Пример 1: Используем шестнадцатеричный ключ "133457799BBCDFF1" (из стандарта)
    hex_key = "133457799BBCDFF1"
    print(f"\nИсходный 64-битный ключ (HEX): {hex_key}")
    
    # Преобразуем HEX в биты
    key_bits = hex_key_to_bits(hex_key)
    print(f"Битовая строка: {''.join(str(b) for b in key_bits)}")
    
    # Генерируем раундовые ключи
    round_keys = generate_round_keys(key_bits)
    
    # Выводим все 16 ключей
    print("\n" + "-" * 70)
    print("СГЕНЕРИРОВАННЫЕ РАУНДОВЫЕ КЛЮЧИ (48 бит каждый):")
    print("-" * 70)
    
    for i, key in enumerate(round_keys, 1):
        print(f"\nK{i:2d}: {''.join(str(b) for b in key)}")
        print(f"     HEX: {bits_to_hex(key)}")
    
    # Проверка: все ключи должны быть разными
    print("\n" + "-" * 70)
    unique_keys = len(set(tuple(k) for k in round_keys))
    print(f"Всего сгенерировано уникальных ключей: {unique_keys} из 16")
    
    # Пример 2: Используем текстовый ключ (для демонстрации)
    print("\n" + "=" * 70)
    print("ПРИМЕР 2: Текстовый ключ")
    print("=" * 70)
    
    text_key = "ABCDEFGH"  # 8 символов = 64 бита
    print(f"\nИсходный ключ (текст): {text_key}")
    
    text_bits = string_to_bits(text_key)
    print(f"Битовая строка: {''.join(str(b) for b in text_bits)}")
    
    keys_text = generate_round_keys(text_bits)
    
    print("\nПервые 3 раундовых ключа:")
    for i in range(3):
        print(f"K{i + 1}: {bits_to_hex(keys_text[i])}")
    
    return round_keys


def test_with_known_vectors():
    """Тест с известными векторами из стандарта DES."""
    print("\n" + "=" * 70)
    print("ТЕСТ С ИЗВЕСТНЫМИ ВЕКТОРАМИ (из стандарта DES)")
    print("=" * 70)
    
    # Известный ключ из стандарта
    hex_key = "133457799BBCDFF1"
    key_bits = hex_key_to_bits(hex_key)
    
    # Известные раундовые ключи (из стандарта DES)
    known_keys = [
        "1B02EFFC7072",  # K1
        "79AEEB77C15A",  # K2
        "CD79915F4EBE",  # K3
        "A9E252B5AAD7",  # K4
        "224E3CE58F7B",  # K5
        "67D64BEC6E49",  # K6
        "97B8995C78DA",  # K7
        "7FF2714FEE27",  # K8
        "DEE5053F1692",  # K9
        "1054D8D9C7A9",  # K10
        "96248FDC657A",  # K11
        "B41B4E938AAD",  # K12
        "48F5A3626836",  # K13
        "B7B5F85047ED",  # K14
        "B736F8C59155",  # K15
        "431FC5BE9EB3"   # K16
    ]
    
    print(f"\nИсходный ключ: {hex_key}")
    print("Проверка сгенерированных ключей с эталонными...")
    
    round_keys = generate_round_keys(key_bits)
    all_match = True
    
    for i, (gen_key, known_key) in enumerate(zip(round_keys, known_keys), 1):
        gen_hex = bits_to_hex(gen_key)
        match = "✓" if gen_hex == known_key else "✗"
        if gen_hex != known_key:
            all_match = False
        print(f"K{i:2d}: {gen_hex} {match}")
    
    if all_match:
        print("\n✅ ВСЕ КЛЮЧИ СОВПАДАЮТ С ЭТАЛОНОМ!")
    else:
        print("\n❌ ЕСТЬ НЕСОВПАДЕНИЯ!")


if __name__ == "__main__":
    # Запускаем основную функцию
    keys = main()
    
    # Запускаем тест с известными векторами
    test_with_known_vectors()