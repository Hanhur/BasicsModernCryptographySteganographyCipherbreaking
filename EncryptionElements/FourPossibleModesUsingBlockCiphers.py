# 6. Четыре возможных режима использования блочных шифров
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Размер блока AES = 16 байт
BLOCK_SIZE = 16

# ----------------------------------------------------------------------
# 1. Режим ECB (Electronic Code Book)
# ----------------------------------------------------------------------
def encrypt_ecb(key, plaintext):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = default_backend())
    encryptor = cipher.encryptor() 
    ciphertext = b""
    # Разбиваем на блоки по BLOCK_SIZE
    for i in range(0, len(plaintext), BLOCK_SIZE):
        block = plaintext[i:i + BLOCK_SIZE]
        if len(block) < BLOCK_SIZE:
            # PKCS7 padding
            pad_len = BLOCK_SIZE - len(block)
            block += bytes([pad_len]) * pad_len
        ciphertext += encryptor.update(block)
    ciphertext += encryptor.finalize()
    return ciphertext

def decrypt_ecb(key, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = default_backend())
    decryptor = cipher.decryptor()
    plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()
    # Убираем PKCS7 padding
    pad_len = plaintext_padded[-1]
    return plaintext_padded[:-pad_len]

# ----------------------------------------------------------------------
# 2. Режим CBC (Cipher Block Chaining)
# ----------------------------------------------------------------------
def encrypt_cbc(key, plaintext, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    # Дополняем до целого числа блоков
    pad_len = BLOCK_SIZE - (len(plaintext) % BLOCK_SIZE)
    plaintext_padded = plaintext + bytes([pad_len]) * pad_len
    ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()
    return ciphertext

def decrypt_cbc(key, ciphertext, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = plaintext_padded[-1]
    return plaintext_padded[:-pad_len]

# ----------------------------------------------------------------------
# 3. Режим CFB (Cipher Feedback) — j = 8 бит (1 байт)
# Исправленная версия для новой библиотеки cryptography
# ----------------------------------------------------------------------
def encrypt_cfb(key, plaintext, iv, segment_size = 8):
    """
    segment_size — количество бит обратной связи (j), кратно 8.
    В новой версии cryptography segment_size передаётся как именованный параметр
    """
    # В новых версиях CFB принимает segment_size как параметр
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    # Для CFB с произвольным segment_size используем другой подход
    # Создаём потоковый шифр с нужным segment_size
    from cryptography.hazmat.primitives.ciphers import Cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend = default_backend()
    )
    encryptor = cipher.encryptor()
    # Важно: segment_size не передаётся напрямую в конструктор CFB в новых версиях
    # Вместо этого используем стандартный CFB8 или CFB128
    return encryptor.update(plaintext) + encryptor.finalize()

# Правильная реализация CFB с ручным управлением для демонстрации
def encrypt_cfb_manual(key, plaintext, iv, segment_bits = 8):
    """
    Ручная реализация CFB с заданным размером сегмента (j бит)
    для демонстрации принципа работы
    """
    segment_bytes = segment_bits // 8
    if segment_bytes == 0:
        segment_bytes = 1
    
    # Инициализация
    register = iv
    ciphertext = b""
    
    # Разбиваем открытый текст на сегменты
    for i in range(0, len(plaintext), segment_bytes):
        segment = plaintext[i:i + segment_bytes]
        
        # Шифруем регистр
        cipher_block = encrypt_ecb(key, register)
        
        # Берём первые segment_bytes байт
        key_stream = cipher_block[:segment_bytes]
        
        # XOR с открытым текстом
        encrypted_segment = bytes(a ^ b for a, b in zip(segment, key_stream))
        ciphertext += encrypted_segment
        
        # Обновляем регистр: сдвигаем влево и добавляем шифротекст
        register = register[segment_bytes:] + encrypted_segment
    
    return ciphertext

def decrypt_cfb_manual(key, ciphertext, iv, segment_bits = 8):
    """
    Ручная реализация расшифрования CFB
    """
    segment_bytes = segment_bits // 8
    if segment_bytes == 0:
        segment_bytes = 1
    
    # Инициализация
    register = iv
    plaintext = b""
    
    # Разбиваем шифротекст на сегменты
    for i in range(0, len(ciphertext), segment_bytes):
        segment = ciphertext[i:i + segment_bytes]
        
        # Шифруем регистр
        cipher_block = encrypt_ecb(key, register)
        
        # Берём первые segment_bytes байт
        key_stream = cipher_block[:segment_bytes]
        
        # XOR для получения открытого текста
        decrypted_segment = bytes(a ^ b for a, b in zip(segment, key_stream))
        plaintext += decrypted_segment
        
        # Обновляем регистр: сдвигаем влево и добавляем шифротекст
        register = register[segment_bytes:] + segment
    
    return plaintext

# ----------------------------------------------------------------------
# 4. Режим OFB (Output Feedback) — j = 8 бит (1 байт)
# ----------------------------------------------------------------------
def encrypt_ofb_manual(key, plaintext, iv):
    """
    Ручная реализация OFB (Output Feedback) для демонстрации принципа работы
    """
    # Инициализация
    register = iv
    ciphertext = b""
    
    # Обрабатываем каждый байт
    for i in range(len(plaintext)):
        if i % BLOCK_SIZE == 0:
            # Шифруем регистр для получения нового ключевого потока
            register = encrypt_ecb(key, register)
        
        # Берём очередной байт из зашифрованного регистра
        key_byte = register[i % BLOCK_SIZE:i % BLOCK_SIZE + 1]
        
        if len(key_byte) == 0:
            key_byte = b'\x00'
        
        # XOR с открытым текстом
        if i < len(plaintext):
            encrypted_byte = bytes([plaintext[i] ^ key_byte[0]])
            ciphertext += encrypted_byte
    
    return ciphertext

def decrypt_ofb_manual(key, ciphertext, iv):
    """
    Ручная реализация расшифрования OFB (симметрично шифрованию)
    """
    # OFB симметричен: расшифрование = шифрование
    return encrypt_ofb_manual(key, ciphertext, iv)

# ----------------------------------------------------------------------
# Упрощённая версия с использованием встроенных режимов (совместимая)
# ----------------------------------------------------------------------
def encrypt_cfb_compatible(key, plaintext, iv):
    """Использование CFB8 из библиотеки"""
    from cryptography.hazmat.primitives.ciphers import Cipher
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

def decrypt_cfb_compatible(key, ciphertext, iv):
    from cryptography.hazmat.primitives.ciphers import Cipher
    cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_ofb_compatible(key, plaintext, iv):
    from cryptography.hazmat.primitives.ciphers import Cipher
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

def decrypt_ofb_compatible(key, ciphertext, iv):
    from cryptography.hazmat.primitives.ciphers import Cipher
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# ----------------------------------------------------------------------
# Демонстрация работы
# ----------------------------------------------------------------------
def main():
    # Генерируем случайный ключ (16 байт = AES-128)
    key = os.urandom(16)
    iv = os.urandom(16)  # для CBC, CFB, OFB

    # Исходный текст
    plaintext = b"Hello, world! This is a test message for block cipher modes. 1234567890"

    print("Исходный текст:", plaintext.decode('utf-8', errors = 'replace'))
    print("-" * 70)

    # ECB
    ct_ecb = encrypt_ecb(key, plaintext)
    pt_ecb = decrypt_ecb(key, ct_ecb)
    print(f"ECB режим:")
    print(f"  Шифротекст (первые 32 байта): {ct_ecb[:32].hex()}")
    print(f"  Расшифровано: {pt_ecb.decode('utf-8')}\n")

    # CBC
    ct_cbc = encrypt_cbc(key, plaintext, iv)
    pt_cbc = decrypt_cbc(key, ct_cbc, iv)
    print(f"CBC режим (IV={iv[:8].hex()}...):")
    print(f"  Шифротекст (первые 32 байта): {ct_cbc[:32].hex()}...")
    print(f"  Расшифровано: {pt_cbc.decode('utf-8')}\n")

    # CFB (ручная реализация для демонстрации)
    ct_cfb_manual = encrypt_cfb_manual(key, plaintext, iv, segment_bits = 8)
    pt_cfb_manual = decrypt_cfb_manual(key, ct_cfb_manual, iv, segment_bits = 8)
    print(f"CFB режим (ручная реализация, j=8 бит, IV={iv[:8].hex()}...):")
    print(f"  Шифротекст (первые 32 байта): {ct_cfb_manual[:32].hex()}...")
    print(f"  Расшифровано: {pt_cfb_manual.decode('utf-8')}\n")

    # CFB с использованием библиотеки
    ct_cfb_lib = encrypt_cfb_compatible(key, plaintext, iv)
    pt_cfb_lib = decrypt_cfb_compatible(key, ct_cfb_lib, iv)
    print(f"CFB режим (библиотечный CFB8, IV={iv[:8].hex()}...):")
    print(f"  Шифротекст (первые 32 байта): {ct_cfb_lib[:32].hex()}...")
    print(f"  Расшифровано: {pt_cfb_lib.decode('utf-8')}\n")

    # OFB (ручная реализация)
    ct_ofb_manual = encrypt_ofb_manual(key, plaintext, iv)
    pt_ofb_manual = decrypt_ofb_manual(key, ct_ofb_manual, iv)
    print(f"OFB режим (ручная реализация, IV={iv[:8].hex()}...):")
    print(f"  Шифротекст (первые 32 байта): {ct_ofb_manual[:32].hex()}...")
    print(f"  Расшифровано: {pt_ofb_manual.decode('utf-8')}\n")

    # OFB с использованием библиотеки
    ct_ofb_lib = encrypt_ofb_compatible(key, plaintext, iv)
    pt_ofb_lib = decrypt_ofb_compatible(key, ct_ofb_lib, iv)
    print(f"OFB режим (библиотечный, IV={iv[:8].hex()}...):")
    print(f"  Шифротекст (первые 32 байта): {ct_ofb_lib[:32].hex()}...")
    print(f"  Расшифровано: {pt_ofb_lib.decode('utf-8')}\n")

    # Дополнительно: покажем недостаток ECB
    print("-" * 70)
    print("Демонстрация недостатка ECB:")
    same_blocks = b"AAAAAAAABBBBBBBB" * 4
    ct_ecb_same = encrypt_ecb(key, same_blocks)
    print(f"Открытый текст с повторяющимися блоками: {same_blocks[:32]}")
    print(f"Шифротекст ECB (видно повторение паттернов):")
    for i in range(0, len(ct_ecb_same), BLOCK_SIZE):
        print(f"  Блок {i // BLOCK_SIZE + 1}: {ct_ecb_same[i:i + BLOCK_SIZE].hex()}")
    
    # Сравнение с CBC для того же текста
    ct_cbc_same = encrypt_cbc(key, same_blocks, iv)
    print(f"\nШифротекст CBC (повторений нет):")
    for i in range(0, len(ct_cbc_same), BLOCK_SIZE):
        print(f"  Блок {i // BLOCK_SIZE + 1}: {ct_cbc_same[i:i + BLOCK_SIZE].hex()}")

if __name__ == "__main__":
    main()