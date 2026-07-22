# RSA
"""
RSA Криптосистема - Полная реализация с блочным шифрованием
Оптимизирована для демонстрации: можно выбрать битность
"""

import random
import math
import sys
import time

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def is_prime(n, k = 5):
    """
    Проверка числа на простоту (тест Миллера-Рабина)
    k - количество раундов (для демонстрации можно уменьшить)
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 как 2^r * d
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Проводим k раундов теста
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits = 16, max_attempts = 1000):
    """
    Генерация простого числа заданной битности
    bits - количество бит (для демонстрации используйте 8 - 32)
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        # Генерируем случайное число нужной длины
        n = random.getrandbits(bits)
        # Убеждаемся, что число нечетное и достаточно большое
        n |= (1 << bits - 1) | 1
        
        # Быстрая проверка на малые делители
        if n % 3 == 0 or n % 5 == 0 or n % 7 == 0 or n % 11 == 0:
            continue
            
        if is_prime(n, k = 3):  # Меньше раундов для скорости
            return n
    
    raise Exception(f"Не удалось сгенерировать простое число за {max_attempts} попыток")

def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def mod_inverse(a, m):
    """Мультипликативный обратный элемент"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception(f"Модулярный обратный не существует для a = {a}, m = {m}")
    return x % m

def string_to_blocks(text, block_size):
    """
    Преобразование строки в блоки чисел
    block_size - максимальный размер блока в байтах
    """
    data = text.encode('utf-8')
    blocks = []
    
    for i in range(0, len(data), block_size):
        block_bytes = data[i:i + block_size]
        block_num = int.from_bytes(block_bytes, 'big')
        blocks.append(block_num)
    
    return blocks

def blocks_to_string(blocks):
    """Преобразование блоков чисел обратно в строку"""
    data = b''
    for block in blocks:
        block_bytes = (block.bit_length() + 7) // 8
        if block_bytes == 0:
            block_bytes = 1
        data += block.to_bytes(block_bytes, 'big')
    
    try:
        return data.decode('utf-8')
    except:
        return "<Ошибка декодирования>"

# ========== ОСНОВНЫЕ ФУНКЦИИ RSA ==========

def generate_keys(bits = 16):
    """
    Генерация ключей RSA
    bits - битность простых чисел
    Для демонстрации рекомендуется 16-32 бита
    """
    print(f"\n🔐 ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA (битность: {bits})")
    print("-" * 50)
    print("⏳ Генерация простых чисел... (может занять несколько секунд)")
    
    start_time = time.time()
    
    print("1️⃣ Генерация простых чисел p и q...")
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:
        q = generate_prime(bits)
    
    print(f"   p = {p}")
    print(f"   q = {q}")
    
    n = p * q
    print(f"2️⃣ n = p * q = {n}")
    
    phi_n = (p - 1) * (q - 1)
    print(f"3️⃣ φ(n) = (p - 1)(q - 1) = {phi_n}")
    
    # Выбираем e (обычно 65537, но для малых чисел используем 3)
    print("4️⃣ Поиск открытой экспоненты e...")
    e = 3
    while math.gcd(e, phi_n) != 1:
        e += 2
    
    print(f"   e = {e}")
    
    # Вычисляем d
    print("5️⃣ Вычисление закрытой экспоненты d...")
    d = mod_inverse(e, phi_n)
    print(f"   d = {d}")
    
    check = (e * d) % phi_n
    print(f"   Проверка: (e * d) % φ(n) = {check} ✓")
    
    public_key = (e, n)
    private_key = (d, n)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️ Ключи сгенерированы за {elapsed:.2f} секунд")
    
    # Максимальный размер блока в байтах
    max_block_bytes = (n.bit_length() - 1) // 8
    if max_block_bytes < 1:
        max_block_bytes = 1
    
    print(f"📋 Публичный ключ: (e = {e}, n = {n})")
    print(f"🔐 Приватный ключ: (d = {d}, n = {n})")
    print(f"📏 Максимальный размер блока: {max_block_bytes} байт")
    print(f"   (можно шифровать сообщения длиной до ~{max_block_bytes * 4} символов)")
    
    return public_key, private_key, p, q, max_block_bytes

def encrypt_message(message, public_key, max_block_bytes):
    """Шифрование сообщения с разбиением на блоки"""
    e, n = public_key
    
    print(f"\n📝 ШИФРОВАНИЕ СООБЩЕНИЯ:")
    print(f"   Исходное сообщение: '{message}'")
    print(f"   Длина: {len(message)} символов")
    
    # Разбиваем на блоки
    blocks = string_to_blocks(message, max_block_bytes)
    print(f"   Разбито на {len(blocks)} блоков")
    
    # Шифруем каждый блок
    encrypted_blocks = []
    for i, block in enumerate(blocks):
        if block >= n:
            raise ValueError(f"Блок {i} слишком большой! n = {n}, блок = {block}")
        encrypted = pow(block, e, n)
        encrypted_blocks.append(encrypted)
        print(f"   Блок {i + 1}: {block} -> {encrypted}")
    
    return encrypted_blocks

def decrypt_message(encrypted_blocks, private_key):
    """Расшифрование сообщения из блоков"""
    d, n = private_key
    
    print(f"\n🔓 РАСШИФРОВАНИЕ СООБЩЕНИЯ:")
    print(f"   Получено {len(encrypted_blocks)} блоков")
    
    # Расшифровываем каждый блок
    decrypted_blocks = []
    for i, block in enumerate(encrypted_blocks):
        decrypted = pow(block, d, n)
        decrypted_blocks.append(decrypted)
        print(f"   Блок {i + 1}: {block} -> {decrypted}")
    
    # Собираем сообщение
    message = blocks_to_string(decrypted_blocks)
    print(f"   Расшифрованное сообщение: '{message}'")
    
    return message

def demo_rsa():
    """Полная демонстрация RSA с блочным шифрованием"""
    print("=" * 70)
    print("🔐  RSA КРИПТОСИСТЕМА (БЛОЧНОЕ ШИФРОВАНИЕ)  🔐")
    print("=" * 70)
    
    print("\n📖 ТЕОРИЯ ИЗ ТЕКСТА:")
    print("   ✓ Асимметричный алгоритм: разные ключи для шифрования и расшифрования")
    print("   ✓ Боб шифрует публичным ключом Алисы")
    print("   ✓ Даже Боб не может расшифровать сообщение после шифрования")
    print("   ✓ Алиса расшифровывает своим приватным ключом")
    print("   ✓ Безопасность основана на сложности факторизации n")
    
    # Для демонстрации используем 256 бит - достаточно быстро, но показывает принцип
    # Для реальной безопасности нужно 2048+ бит, но это медленно на Python
    bits = 256
    print(f"\n💡 Используем {bits}-битные ключи для демонстрации")
    print("   (В реальном мире используются 2048 - 4096 бит)")
    
    print("\n" + "=" * 70)
    print("👩 АЛИСА СОЗДАЕТ СВОИ КЛЮЧИ")
    print("=" * 70)
    
    public_key, private_key, p, q, max_block_bytes = generate_keys(bits = bits)
    e, n = public_key
    d, n = private_key
    
    print("\n" + "=" * 70)
    print("📨 БОБ ОТПРАВЛЯЕТ СООБЩЕНИЕ АЛИСЕ")
    print("=" * 70)
    
    # Теперь можно отправлять сообщения
    message = "Привет, Алиса! Это секретное сообщение."
    
    print(f"\n✉️ Боб хочет отправить: '{message}'")
    print(f"🔑 Боб использует публичный ключ Алисы")
    
    # Боб шифрует
    ciphertext_blocks = encrypt_message(message, public_key, max_block_bytes)
    
    print(f"\n📦 Зашифрованное сообщение (блоки):")
    for i, block in enumerate(ciphertext_blocks):
        print(f"   Блок {i + 1}: {block}")
    
    # Демонстрация: Боб не может расшифровать
    print(f"\n🤔 Боб пытается расшифровать свое же сообщение...")
    print(f"   У Боба нет приватного ключа d = {d}!")
    print(f"   Он знает только e = {e} и n = {n}")
    print(f"   Расшифровка публичным ключом невозможна!")
    
    print("\n" + "=" * 70)
    print("📬 АЛИСА ПОЛУЧАЕТ И РАСШИФРОВЫВАЕТ")
    print("=" * 70)
    
    decrypted_message = decrypt_message(ciphertext_blocks, private_key)
    
    print("\n" + "=" * 70)
    print("✅ ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 70)
    print(f"   Отправлено:  '{message}'")
    print(f"   Получено:   '{decrypted_message}'")
    print(f"   Совпадает:  {message == decrypted_message} ✓")
    
    # Криптоанализ
    print("\n" + "=" * 70)
    print("🔍 КРИПТОАНАЛИЗ")
    print("=" * 70)
    print(f"   Злоумышленник знает:")
    print(f"   - Публичный ключ: e = {e}")
    print(f"   - Модуль: n = {n}")
    print(f"   - Шифротекст: {len(ciphertext_blocks)} блоков")
    print(f"\n   Чтобы взломать RSA, нужно найти d из уравнения:")
    print(f"   d * e ≡ 1 (mod φ(n))")
    print(f"   Для этого нужно разложить n на множители p и q")
    print(f"   n = {n}")
    print(f"   p = {p}, q = {q} (известны только Алисе)")
    print(f"\n   Сложность: факторизация {bits} - битного числа")
    
    # Оценка сложности
    if bits <= 256:
        print("   ⚠️ Для демонстрационных ключей это легко взломать")
        print(f"   {n} = {p} × {q}")
    else:
        print("   ✅ Для 2048-битных чисел это невозможно даже для суперкомпьютера")
    
    print("\n" + "=" * 70)
    print("🎓 ЗАКЛЮЧЕНИЕ")
    print("=" * 70)
    print("   ✓ RSA использует разные ключи для шифрования и расшифрования")
    print("   ✓ Безопасность основана на сложности факторизации")
    print("   ✓ Даже отправитель не может расшифровать свое сообщение")
    print("   ✓ Сообщения любой длины шифруются по блокам")
    print("   ✓ Асимметричное шифрование - основа современной криптографии")
    print("=" * 70)

def interactive_rsa():
    """Интерактивный режим с выбором битности"""
    print("=" * 70)
    print("🔐  ИНТЕРАКТИВНЫЙ RSA  🔐")
    print("=" * 70)
    
    print("\nВыберите битность ключей (рекомендации):")
    print("1 - 64 бита  (очень быстро, только для демонстрации)")
    print("2 - 128 бит (быстро, можно шифровать короткие сообщения)")
    print("3 - 256 бит (медленнее, но показывает реальный принцип)")
    print("4 - 512 бит (медленно, как в старых системах)")
    print("5 - Своя битность")
    
    choice = input("\nВаш выбор (1 - 5): ").strip()
    
    if choice == "1":
        bits = 64
    elif choice == "2":
        bits = 128
    elif choice == "3":
        bits = 256
    elif choice == "4":
        bits = 512
    elif choice == "5":
        bits = int(input("Введите битность (64 - 1024): "))
    else:
        bits = 256
    
    if bits > 1024:
        print("⚠️ Внимание: битность > 1024 может работать очень медленно!")
        confirm = input("Продолжить? (y / n): ")
        if confirm.lower() != 'y':
            bits = 256
    
    try:
        public_key, private_key, p, q, max_block_bytes = generate_keys(bits)
        e, n = public_key
        d, n = private_key
        
        print(f"\n📏 Максимальный размер блока: {max_block_bytes} байт")
        
        message = input("\n✉️ Введите сообщение для шифрования: ")
        if not message:
            message = "Hello RSA!"
        
        print(f"\n📝 Шифрование...")
        encrypted_blocks = encrypt_message(message, public_key, max_block_bytes)
        
        print(f"\n📦 Зашифрованное сообщение:")
        for i, block in enumerate(encrypted_blocks):
            print(f"   Блок {i + 1}: {block}")
        
        print(f"\n🔓 Расшифрование...")
        decrypted = decrypt_message(encrypted_blocks, private_key)
        
        print("\n" + "=" * 70)
        print("✅ РЕЗУЛЬТАТ")
        print("=" * 70)
        print(f"   Исходное:  '{message}'")
        print(f"   Расшифровано: '{decrypted}'")
        print(f"   Совпадает: {message == decrypted} ✓")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("   Попробуйте использовать меньшую битность или более короткое сообщение.")

def speed_test():
    """Тест скорости генерации ключей разных размеров"""
    print("\n" + "=" * 70)
    print("🚀 ТЕСТ СКОРОСТИ RSA")
    print("=" * 70)
    
    bit_sizes = [64, 128, 256, 512]
    
    print("\nТестирование генерации ключей разных размеров:\n")
    print("Битность | Время генерации | Макс. блок (байт)")
    print("-" * 50)
    
    for bits in bit_sizes:
        start = time.time()
        try:
            public_key, private_key, p, q, max_block_bytes = generate_keys(bits)
            elapsed = time.time() - start
            print(f"{bits:8} | {elapsed:14.2f}s | {max_block_bytes:17}")
        except Exception as e:
            print(f"{bits:8} | {'ОШИБКА':14} | -")
    
    print("\n" + "=" * 70)

# ========== ЗАПУСК ПРОГРАММЫ ==========

if __name__ == "__main__":
    random.seed()
    
    print("\n" + "=" * 70)
    print("ДОБРО ПОЖАЛОВАТЬ В МИР RSA!")
    print("=" * 70)
    
    while True:
        print("\nВыберите режим:")
        print("1 - Полная демонстрация (рекомендуется)")
        print("2 - Интерактивный режим")
        print("3 - Тест скорости генерации ключей")
        print("4 - Выход")
        
        choice = input("\nВаш выбор (1 - 4): ").strip()
        
        if choice == "1":
            demo_rsa()
            input("\nНажмите Enter для продолжения...")
        elif choice == "2":
            interactive_rsa()
            input("\nНажмите Enter для продолжения...")
        elif choice == "3":
            speed_test()
            input("\nНажмите Enter для продолжения...")
        elif choice == "4":
            print("👋 До свидания!")
            sys.exit(0)
        else:
            print("❌ Неверный выбор")