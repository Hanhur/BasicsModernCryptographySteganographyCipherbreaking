# Основные режимы функционирования блоковых шифров
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii


def print_separator(title):
    """Вспомогательная функция для красивого вывода"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def demonstrate_ecb():
    """
    Демонстрация режима ECB (Electronic CodeBook)
    Показывает проблему сохранения 'образа данных'
    """
    print_separator("РЕЖИМ ECB (Electronic CodeBook)")
    
    # Генерируем случайный ключ (16 байт = 128 бит для AES)
    key = get_random_bytes(16)
    print(f"Ключ (hex): {binascii.hexlify(key).decode()}")
    
    # Создаем два сообщения с одинаковыми блоками
    # Блок AES = 16 байт. Создадим сообщение из двух одинаковых блоков 'A'*16
    block1 = b'A' * 16  # Первый блок
    block2 = b'A' * 16  # Второй блок (идентичный первому)
    message = block1 + block2
    print(f"\nИсходное сообщение (первые 32 байта): {message[:32]}")
    print(f"  Блок 1: {block1}")
    print(f"  Блок 2: {block2} (ИДЕНТИЧЕН блоку 1)")
    
    # Создаем шифр в режиме ECB
    cipher_ecb = AES.new(key, AES.MODE_ECB)
    
    # Шифруем (padding не нужен, т.к. длина кратна 16)
    ciphertext = cipher_ecb.encrypt(message)
    print(f"\nЗашифрованное сообщение (hex): {binascii.hexlify(ciphertext).decode()}")
    
    # Разбиваем шифротекст на блоки для наглядности
    ct_block1 = ciphertext[:16]
    ct_block2 = ciphertext[16:32]
    print(f"\n  Блок шифротекста 1: {binascii.hexlify(ct_block1).decode()}")
    print(f"  Блок шифротекста 2: {binascii.hexlify(ct_block2).decode()}")
    print(f"  → Блоки шифротекста ИДЕНТИЧНЫ! (сохранение 'образа данных')")
    
    # Дешифрование
    cipher_ecb_dec = AES.new(key, AES.MODE_ECB)
    decrypted = cipher_ecb_dec.decrypt(ciphertext)
    print(f"\nРасшифрованное сообщение: {decrypted[:32]}")
    print(f"  Совпадает с исходным: {decrypted == message}")
    
    print("\n⚠️  НЕДОСТАТОК ECB: Одинаковые блоки открытого текста → одинаковые блоки шифротекста.")
    print("   Это позволяет противнику проводить частотный анализ.")


def demonstrate_cbc():
    """
    Демонстрация режима CBC (Cipher-Block Chaining)
    Показывает, как сцепление блоков разрушает 'образ данных'
    """
    print_separator("РЕЖИМ CBC (Cipher-Block Chaining)")
    
    # Генерируем случайный ключ (16 байт)
    key = get_random_bytes(16)
    print(f"Ключ (hex): {binascii.hexlify(key).decode()}")
    
    # Генерируем случайный вектор инициализации (IV)
    iv = get_random_bytes(16)
    print(f"IV (hex): {binascii.hexlify(iv).decode()}")
    
    # Создаем те же самые два идентичных блока
    block1 = b'A' * 16
    block2 = b'A' * 16
    message = block1 + block2
    print(f"\nИсходное сообщение (первые 32 байта): {message[:32]}")
    print(f"  Блок 1: {block1}")
    print(f"  Блок 2: {block2} (ИДЕНТИЧЕН блоку 1)")
    
    # Создаем шифр в режиме CBC
    cipher_cbc = AES.new(key, AES.MODE_CBC, iv = iv)
    
    # Шифруем
    ciphertext = cipher_cbc.encrypt(message)
    print(f"\nЗашифрованное сообщение (hex): {binascii.hexlify(ciphertext).decode()}")
    
    # Разбиваем шифротекст на блоки
    ct_block1 = ciphertext[:16]
    ct_block2 = ciphertext[16:32]
    print(f"\n  Блок шифротекста 1: {binascii.hexlify(ct_block1).decode()}")
    print(f"  Блок шифротекста 2: {binascii.hexlify(ct_block2).decode()}")
    print(f"  → Блоки шифротекста РАЗЛИЧНЫ! ('образ данных' разрушен)")
    
    # Дешифрование
    cipher_cbc_dec = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted = cipher_cbc_dec.decrypt(ciphertext)
    print(f"\nРасшифрованное сообщение: {decrypted[:32]}")
    print(f"  Совпадает с исходным: {decrypted == message}")
    
    print("\n✅ ПРЕИМУЩЕСТВО CBC: Даже одинаковые блоки дают разный шифротекст.")
    print("   Недостаток: Дешифрование возможно только последовательно.")
    print("   (для расшифровки блока 2 нужен блок 1)")


def demonstrate_cbc_with_padding():
    """
    Демонстрация CBC с сообщением произвольной длины (используем padding)
    """
    print_separator("CBC С ПРОИЗВОЛЬНЫМ СООБЩЕНИЕМ (с Padding)")
    
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    # Сообщение произвольной длины (не кратной 16)
    message = b"Hello, this is a secret message! It has arbitrary length."
    print(f"Исходное сообщение: {message}")
    print(f"Длина сообщения: {len(message)} байт (не кратно 16)")
    
    # Шифрование с добавлением паддинга (PKCS7)
    cipher_cbc = AES.new(key, AES.MODE_CBC, iv = iv)
    padded_message = pad(message, AES.block_size)
    print(f"Длина с паддингом: {len(padded_message)} байт (кратно 16)")
    
    ciphertext = cipher_cbc.encrypt(padded_message)
    print(f"Шифротекст (hex): {binascii.hexlify(ciphertext).decode()[:64]}...")
    
    # Дешифрование с удалением паддинга
    cipher_cbc_dec = AES.new(key, AES.MODE_CBC, iv = iv)
    decrypted_padded = cipher_cbc_dec.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)
    
    print(f"Расшифрованное сообщение: {decrypted}")
    print(f"Совпадает с исходным: {decrypted == message}")


def compare_ecb_cbc_visual():
    """
    Визуальное сравнение ECB и CBC на одинаковых данных
    """
    print_separator("СРАВНЕНИЕ ECB vs CBC (визуально)")
    
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    # Создаем сообщение из 4 одинаковых блоков
    message = b'A' * 16 * 4
    print(f"Сообщение: {message[:64]}")
    print("(4 одинаковых блока по 16 байт)")
    
    # ECB
    cipher_ecb = AES.new(key, AES.MODE_ECB)
    ct_ecb = cipher_ecb.encrypt(message)
    
    # CBC
    cipher_cbc = AES.new(key, AES.MODE_CBC, iv = iv)
    ct_cbc = cipher_cbc.encrypt(message)
    
    print("\n🔹 ECB шифротекст (блоки):")
    for i in range(4):
        block = ct_ecb[i * 16:(i + 1) * 16]
        print(f"  Блок {i + 1}: {binascii.hexlify(block).decode()}")
    print("  → Все блоки ОДИНАКОВЫЕ (проблема!)")
    
    print("\n🔸 CBC шифротекст (блоки):")
    for i in range(4):
        block = ct_cbc[i * 16:(i + 1) * 16]
        print(f"  Блок {i + 1}: {binascii.hexlify(block).decode()}")
    print("  → Все блоки РАЗНЫЕ (безопасно!)")


def main():
    """Главная функция"""
    print("=" * 60)
    print(" ДЕМОНСТРАЦИЯ РЕЖИМОВ БЛОЧНЫХ ШИФРОВ (ECB vs CBC)")
    print("=" * 60)
    print("\nНа основе материала: '8.3. Основные режимы функционирования блочных шифров'")
    
    # Запускаем все демонстрации
    demonstrate_ecb()
    demonstrate_cbc()
    demonstrate_cbc_with_padding()
    compare_ecb_cbc_visual()
    
    print("\n" + "=" * 60)
    print(" ВЫВОДЫ:")
    print("=" * 60)
    print("1. ECB: Простой, быстрый, но НЕБЕЗОПАСНЫЙ для длинных сообщений")
    print("   → Сохраняет 'образ данных' → уязвим к частотному анализу")
    print("2. CBC: Безопаснее, разрушает 'образ данных'")
    print("   → Требует IV и последовательного дешифрования")
    print("3. В реальных проектах используйте CBC, CTR или GCM (не ECB!)")
    print("=" * 60)


if __name__ == "__main__":
    main()