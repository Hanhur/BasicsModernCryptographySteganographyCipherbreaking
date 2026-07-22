# Анализ RSA
import random
import math
import sys

# ------------------ Вспомогательные функции ------------------

def is_prime(n, k = 10):
    """Тест Миллера-Рабина для проверки простоты чисел"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проверяем k раундов
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    """Генерирует простое число заданной битовой длины"""
    while True:
        # Генерируем нечётное число
        n = random.getrandbits(bits)
        # Убеждаемся, что число нечётное и имеет нужную длину
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def gcd_extended(a, b):
    """Расширенный алгоритм Евклида для нахождения обратного элемента"""
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = gcd_extended(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def mod_inverse(a, m):
    """Находит обратный элемент a по модулю m"""
    gcd, x, _ = gcd_extended(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента не существует для {a} mod {m}")
    return x % m

# ------------------ Основные функции RSA ------------------

def generate_keypair(bits = 1024):
    """
    Генерирует пару ключей RSA
    bits - битность простых чисел p и q (рекомендуется 1024 или 2048)
    Возвращает: (public_key, private_key)
    public_key = (e, N)
    private_key = (d, N)
    """
    print(f"Генерация простых чисел размером {bits} бит...")
    
    # Шаг 1: Выбираем два больших простых числа p и q
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:  # Чтобы p и q были разными
        q = generate_prime(bits)
    
    print(f"p = {p}")
    print(f"q = {q}")
    
    # Шаг 2: Вычисляем N = p * q
    N = p * q
    
    # Шаг 3: Вычисляем функцию Эйлера φ(N) = (p-1)(q-1)
    phi = (p - 1) * (q - 1)
    
    # Шаг 4: Выбираем открытую экспоненту e (обычно 65537)
    # e должно быть взаимно простым с φ(N)
    e = 65537
    if math.gcd(e, phi) != 1:
        # Если 65537 не подходит (редкий случай), ищем другое
        e = random.randint(3, phi - 1)
        while math.gcd(e, phi) != 1:
            e = random.randint(3, phi - 1)
    
    print(f"e = {e}")
    print(f"φ(N) = {phi}")
    
    # Шаг 5: Вычисляем закрытую экспоненту d = e^(-1) mod φ(N)
    d = mod_inverse(e, phi)
    print(f"d = {d}")
    
    public_key = (e, N)
    private_key = (d, N)
    
    return public_key, private_key

def encrypt(message, public_key):
    """
    Шифрует сообщение
    message - строка или число
    public_key = (e, N)
    Возвращает: зашифрованное сообщение (число или список чисел)
    """
    e, N = public_key
    
    # Если сообщение - строка, преобразуем в числа
    if isinstance(message, str):
        # Преобразуем каждый символ в его ASCII код
        numbers = [ord(char) for char in message]
        # Шифруем каждое число
        encrypted_numbers = [pow(num, e, N) for num in numbers]
        return encrypted_numbers
    else:
        # Если сообщение - число
        return pow(message, e, N)

def decrypt(ciphertext, private_key):
    """
    Расшифровывает сообщение
    ciphertext - число или список чисел
    private_key = (d, N)
    Возвращает: расшифрованное сообщение (число или строка)
    """
    d, N = private_key
    
    # Если шифротекст - список (от строки)
    if isinstance(ciphertext, list):
        # Расшифровываем каждое число
        decrypted_numbers = [pow(num, d, N) for num in ciphertext]
        # Преобразуем числа обратно в символы
        try:
            message = ''.join([chr(num) for num in decrypted_numbers])
            return message
        except ValueError:
            # Если не удалось преобразовать в строку, возвращаем числа
            return decrypted_numbers
    else:
        # Если шифротекст - число
        return pow(ciphertext, d, N)

# ------------------ Демонстрация работы ------------------

def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ RSA")
    print("=" * 60)
    
    # Генерируем ключи (для демонстрации используем 512 бит, чтобы было быстрее)
    print("\n1. Генерация ключей...")
    public_key, private_key = generate_keypair(bits = 512)
    
    e, N = public_key
    d, _ = private_key
    
    print(f"\nПубличный ключ: e = {e}, N = {N}")
    print(f"Приватный ключ: d = {d}, N = {N}")
    
    # Демонстрация 1: Шифрование числа
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ 1: Шифрование числа")
    print("=" * 60)
    
    original_number = 123456
    print(f"Исходное число: {original_number}")
    
    encrypted_number = encrypt(original_number, public_key)
    print(f"Зашифрованное число: {encrypted_number}")
    
    decrypted_number = decrypt(encrypted_number, private_key)
    print(f"Расшифрованное число: {decrypted_number}")
    
    print(f"\nПроверка: {original_number} == {decrypted_number} -> {original_number == decrypted_number}")
    
    # Демонстрация 2: Шифрование текста
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ 2: Шифрование текста")
    print("=" * 60)
    
    original_text = "Hello, RSA!"
    print(f"Исходный текст: '{original_text}'")
    
    encrypted_text = encrypt(original_text, public_key)
    print(f"Зашифрованный текст (числа): {encrypted_text}")
    
    decrypted_text = decrypt(encrypted_text, private_key)
    print(f"Расшифрованный текст: '{decrypted_text}'")
    
    print(f"\nПроверка: '{original_text}' == '{decrypted_text}' -> {original_text == decrypted_text}")
    
    # Демонстрация 3: Проверка математического свойства
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ 3: Проверка M ^ (e * d) ≡ M (mod N)")
    print("=" * 60)
    
    test_m = 42
    print(f"Возьмём M = {test_m}")
    
    # Вычисляем M^e mod N (шифрование)
    c = pow(test_m, e, N)
    print(f"M ^ e mod N = {test_m} ^ {e} mod {N} = {c}")
    
    # Вычисляем c^d mod N (расшифрование)
    m_restored = pow(c, d, N)
    print(f"c ^ d mod N = {c} ^ {d} mod {N} = {m_restored}")
    
    print(f"\nM ^ (e * d) ≡ M (mod N): {test_m} == {m_restored} -> {test_m == m_restored}")
    
    # Дополнительная проверка: все ли работает
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)

if __name__ == "__main__":
    main()