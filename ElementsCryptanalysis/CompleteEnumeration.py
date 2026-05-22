# 2. Полный перебор
import itertools
import string

# ------------------------------------------------------------
# 1. Упрощённая криптосистема (XOR)
# ------------------------------------------------------------
def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Шифрование XOR: повторяем ключ по длине текста"""
    key_len = len(key)
    return bytes([plaintext[i] ^ key[i % key_len] for i in range(len(plaintext))])

def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Дешифрование XOR — то же самое, что шифрование"""
    return encrypt(ciphertext, key)  # XOR симметричен

# ------------------------------------------------------------
# 2. Проверка «осмысленности» текста (для английского)
# ------------------------------------------------------------
def is_meaningful(text: bytes, threshold: float = 0.7) -> bool:
    """
    Простейшая проверка: доля печатных ASCII символов + пробелов/букв.
    Для демонстрации — не криптоаналитический стандарт, но достаточно.
    """
    if len(text) == 0:
        return False
    printable = 0
    for byte in text:
        ch = chr(byte)
        if ch in string.ascii_letters or ch == ' ' or ch in string.punctuation:
            printable += 1
    ratio = printable / len(text)
    return ratio >= threshold

# ------------------------------------------------------------
# 3. Атака типа 1: известны (m, c) -> ищем ключ e
# ------------------------------------------------------------
def brute_force_key_known_plaintext(plaintext: bytes, ciphertext: bytes, max_key_len: int = 4):
    """
    Перебираем все возможные ключи заданной длины (от 1 до max_key_len).
    Для наглядности ключ — байты от 0 до 255, перебор всех комбинаций.
    """
    print("\n=== АТАКА 1: ИЗВЕСТНЫ (m, c) ===")
    print(f"Открытый текст: {plaintext}")
    print(f"Шифртекст:      {ciphertext}")

    for key_len in range(1, max_key_len + 1):
        print(f"\nПеребор ключей длины {key_len} байт...")
        # Все возможные ключи длины key_len (0..255)
        for key_tuple in itertools.product(range(256), repeat = key_len):
            key = bytes(key_tuple)
            # Проверяем: зашифруем m, должно совпасть с c
            if encrypt(plaintext, key) == ciphertext:
                print(f"  НАЙДЕН КЛЮЧ: {key.hex()} (длина {key_len})")
                # Проверка расшифровки
                decrypted = decrypt(ciphertext, key)
                print(f"  Расшифровка: {decrypted}")
                return key
    print("Ключ не найден (возможно, больше длина ключа)")
    return None

# ------------------------------------------------------------
# 4. Атака типа 2: известен только шифртекст -> ищем ключ дешифрования
# ------------------------------------------------------------
def brute_force_key_ciphertext_only(ciphertext: bytes, max_key_len: int = 4):
    """
    Перебираем все ключи дешифрования, пока расшифрованный текст
    не покажется осмысленным.
    """
    print("\n=== АТАКА 2: ТОЛЬКО ШИФРТЕКСТ ===")
    print(f"Шифртекст: {ciphertext}")

    candidates = []
    for key_len in range(1, max_key_len + 1):
        print(f"\nПеребор ключей длины {key_len} байт...")
        for key_tuple in itertools.product(range(256), repeat = key_len):
            key = bytes(key_tuple)
            decrypted = decrypt(ciphertext, key)
            if is_meaningful(decrypted):
                candidates.append((key, decrypted))
                # Для демонстрации покажем первые 3 найденных
                if len(candidates) <= 3:
                    print(f"  Возможный ключ: {key.hex()} -> {decrypted}")

    if candidates:
        print("\n=== НАЙДЕННЫЕ ОСМЫСЛЕННЫЕ РАСШИФРОВКИ ===")
        for key, text in candidates[:5]:  # покажем не более 5
            print(f"Ключ {key.hex()}: {text}")
        return candidates[0][0]  # возвращаем первый подходящий ключ
    else:
        print("Осмысленных расшифровок не найдено.")
        return None

# ------------------------------------------------------------
# 5. Демонстрация работы
# ------------------------------------------------------------
if __name__ == "__main__":
    # Исходные данные (для примера)
    original_message = b"Hello World"
    secret_key = b"KEY"  # настоящий ключ (3 байта)

    print("=== ИСХОДНЫЕ ПАРАМЕТРЫ ===")
    print(f"Сообщение: {original_message}")
    print(f"Реальный ключ: {secret_key.hex()}")

    # Шифруем
    cipher = encrypt(original_message, secret_key)
    print(f"Шифртекст: {cipher}")

    # --- АТАКА 1 (знаем m и c) ---
    found_key = brute_force_key_known_plaintext(original_message, cipher, max_key_len = 4)
    if found_key:
        print(f"\nАтака 1 успешна. Ключ: {found_key.hex()}")

    # --- АТАКА 2 (знаем только c, ищем осмысленный текст) ---
    # Зашифруем другое сообщение, чтобы показать атаку №2
    secret_msg = b"Attack at dawn"
    cipher2 = encrypt(secret_msg, secret_key)
    print("\n" + "=" * 60)
    print("ДЛЯ АТАКИ 2 (только шифртекст):")
    print(f"Реальное сообщение: {secret_msg}")
    print(f"Шифртекст: {cipher2}")

    brute_force_key_ciphertext_only(cipher2, max_key_len = 4)