# 1. История создания
"""
Симуляция истории создания DES на основе текста.
Образовательная демонстрация: принцип Фейстеля, замена ключа, влияние NSA, 3DES.
"""

import hashlib
import struct

# ------------------- 1. Принцип Фейстеля (основа LUCIFER) -------------------
def feistel_round(right_half, subkey):
    """
    Симуляция раундовой функции Фейстеля.
    В реальности здесь были бы S-боксы, перестановки и XOR.
    """
    # Хешируем половину блока с подключом для имитации нелинейного преобразования
    combined = f"{right_half}{subkey}".encode()
    hash_digest = hashlib.sha256(combined).digest()
    # Берем первые 4 байта как 32-битное число
    return struct.unpack('<I', hash_digest[:4])[0]

def feistel_encrypt(block_64bit, key_128bit, rounds = 16):
    """
    Симуляция шифрования на основе сети Фейстеля.
    block_64bit: целое число (0..2 ^ 64 - 1)
    key_128bit: целое число (0..2 ^ 128 - 1)
    """
    left = (block_64bit >> 32) & 0xFFFFFFFF
    right = block_64bit & 0xFFFFFFFF

    # Генерируем 16 подключей из 128-битного ключа (упрощенно)
    subkeys = []
    key_bytes = key_128bit.to_bytes(16, 'big')
    for i in range(rounds):
        # Используем SHA-256 для получения псевдослучайных подключей
        h = hashlib.sha256(key_bytes + struct.pack('<I', i)).digest()
        subkeys.append(struct.unpack('<I', h[:4])[0])

    for i in range(rounds):
        f_result = feistel_round(right, subkeys[i])
        new_left = right
        new_right = left ^ f_result
        left, right = new_left, new_right

    # Финальная перестановка (обмен)
    return (right << 32) | left

# ------------------- 2. Алгоритм LUCIFER (1971) -------------------
def lucifer_encrypt(block_64bit, key_128bit):
    """Эмуляция LUCIFER с 128-битным ключом"""
    print("   [LUCIFER] Используется 128-битный ключ")
    return feistel_encrypt(block_64bit, key_128bit, rounds = 16)

# ------------------- 3. DES с 56-битным ключом (навязан NSA) -------------------
def des_encrypt(block_64bit, key_56bit):
    """Эмуляция DES с ослабленным 56-битным ключом"""
    print("   [DES] Используется 56-битный ключ (по настоянию NSA)")
    # Расширяем 56 бит до 128 для совместимости с функцией Фейстеля
    expanded_key = key_56bit << 72  # просто сдвиг для имитации
    return feistel_encrypt(block_64bit, expanded_key, rounds = 16)

# ------------------- 4. Тройной DES (3DES) -------------------
def triple_des_encrypt(block_64bit, key1_56bit, key2_56bit, key3_56bit):
    """Эмуляция 3DES: Encrypt-Decrypt-Encrypt с тремя ключами"""
    print("   [3DES] Тройное шифрование (Encrypt-Decrypt-Encrypt)")
    # Шифрование первым ключом
    c1 = des_encrypt(block_64bit, key1_56bit)
    # Расшифровка вторым ключом (в симуляции используем ту же функцию)
    c2 = des_encrypt(c1, key2_56bit)
    # Шифрование третьим ключом
    c3 = des_encrypt(c2, key3_56bit)
    return c3

# ------------------- 5. Демонстрация истории -------------------
def print_history_stage(stage_name, description):
    """Красивый вывод этапов истории"""
    print("\n" + "=" * 60)
    print(f"📜 {stage_name}")
    print("=" * 60)
    print(description)

def main():
    print("\n🔐 ИСТОРИЯ СОЗДАНИЯ DES — ИНТЕРАКТИВНАЯ СИМУЛЯЦИЯ")
    print("Основано на тексте: IBM → LUCIFER → DES → 3DES\n")

    # Тестовый блок данных (64 бита)
    plaintext_block = 0x0123456789ABCDEF
    print(f"Исходный блок (64 бита): 0x{plaintext_block:016X}")

    # ------------------- ЭТАП 1: LUCIFER (1971) -------------------
    print_history_stage(
        "1. LUCIFER (1971) — Банк Ллойда",
        "Разработан под руководством Хорста Фейстеля.\n"
        "Использует 128-битный ключ и 64-битные блоки."
    )
    key_128 = 0x0123456789ABCDEFFEDCBA9876543210
    print(f"Ключ (128 бит): 0x{key_128:032X}")
    cipher_lucifer = lucifer_encrypt(plaintext_block, key_128)
    print(f"Результат:      0x{cipher_lucifer:016X}")

    # ------------------- ЭТАП 2: DES (1977) — вмешательство NSA -------------------
    print_history_stage(
        "2. DES (1977) — Стандарт США",
        "NSA заменило 128-битный ключ на 56-битный.\n"
        "Внесены изменения в S-таблицы (спорно — есть ли 'черный ход')."
    )
    key_56 = 0x0123456789ABCD  # 56 бит
    print(f"Ключ (56 бит):  0x{key_56:014X}  (ослаблен!)")
    cipher_des = des_encrypt(plaintext_block, key_56)
    print(f"Результат:      0x{cipher_des:016X}")

    # ------------------- ЭТАП 3: 3DES — защита от слабого ключа -------------------
    print_history_stage(
        "3. Тройной DES (3DES) — Современное решение",
        "Из-за 56-битного ключа DES стал уязвим к полному перебору.\n"
        "3DES использует три ключа (Encrypt-Decrypt-Encrypt) для повышения стойкости."
    )
    key1 = 0x0123456789ABCD
    key2 = 0xFEDCBA98765432
    key3 = 0x89ABCDEF012345
    print(f"Ключ 1: 0x{key1:014X}")
    print(f"Ключ 2: 0x{key2:014X}")
    print(f"Ключ 3: 0x{key3:014X}")
    cipher_3des = triple_des_encrypt(plaintext_block, key1, key2, key3)
    print(f"Результат:      0x{cipher_3des:016X}")

    # ------------------- ИТОГОВАЯ ИНФОРМАЦИЯ -------------------
    print("\n" + "=" * 60)
    print("📌 ВЫВОД")
    print("=" * 60)
    print("""
    • DES стал мировым стандартом, но 56-битный ключ был слаб с самого начала.
    • Современные параллельные вычисления делают DES легко взламываемым.
    • На практике применяется 3DES, использующий многократное шифрование.
    • Споры о 'черном ходе' в S-таблицах, внесенных NSA, не утихают до сих пор.
    """)

    print("\n✅ Симуляция завершена. Алгоритм DES — исторический прорыв, но сегодня он устарел.")

if __name__ == "__main__":
    main()