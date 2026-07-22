# Объяснение алгоритма RSA
import random
import math

# =============================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================

def is_prime(num):
    """Проверка числа на простоту (перебор делителей до корня)."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(math.isqrt(num)) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def generate_prime(min_value, max_value):
    """Генерация случайного простого числа в заданном диапазоне."""
    while True:
        num = random.randint(min_value, max_value)
        if is_prime(num):
            return num

def egcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y), где a * x + b * y = gcd(a, b).
    """
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = egcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def mod_inverse(a, m):
    """
    Находит обратное число по модулю m:
    a * d ≡ 1 (mod m)
    """
    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента не существует: gcd({a}, {m}) = {gcd}")
    return x % m

# =============================================
# 2. ГЕНЕРАЦИЯ КЛЮЧЕЙ (как в тексте)
# =============================================

def generate_keys():
    """
    Генерирует пару ключей (открытый и закрытый).
    Возвращает: (public_key, private_key)
    public_key  = (e, N)
    private_key = (d, N)
    """
    print("\n--- ГЕНЕРАЦИЯ КЛЮЧЕЙ ---")
    
    # 1. Выбираем два простых числа p и q (для примера — небольшие)
    #    В реальности они должны быть огромными (например, 1024 бита).
    p = generate_prime(50, 200)
    q = generate_prime(50, 200)
    
    # Чтобы p и q не были равны (иначе N = p^2 — легко взломать)
    while q == p:
        q = generate_prime(50, 200)
    
    print(f"p = {p}, q = {q}")
    
    # 2. Вычисляем N = p * q (открытый ключ)
    N = p * q
    print(f"N = p * q = {N}")
    
    # 3. Вычисляем функцию Эйлера φ(N) = (p - 1) * (q - 1)
    phi = (p - 1) * (q - 1)
    print(f"φ(N) = (p - 1) * (q - 1) = {phi}")
    
    # 4. Выбираем открытую экспоненту e
    #    В реальности почти всегда используют 65537.
    #    Здесь для демонстрации возьмём e так, чтобы было 1 < e < φ и gcd(e, φ) = 1.
    e = 65537
    if e >= phi or math.gcd(e, phi) != 1:
        # Если 65537 не подходит (маловероятно для больших p,q), подбираем другое
        e = random.randint(2, phi - 1)
        while math.gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)
    
    print(f"e = {e}")
    
    # 5. Вычисляем закрытый ключ d (обратное к e по модулю φ)
    #    d * e ≡ 1 (mod φ)
    d = mod_inverse(e, phi)
    print(f"d = {d}")
    
    public_key = (e, N)
    private_key = (d, N)
    
    return public_key, private_key

# =============================================
# 3. ШИФРОВАНИЕ И РАСШИФРОВКА
# =============================================

def encrypt(message, public_key):
    """
    Шифрует сообщение M.
    c ≡ M ^ e (mod N)
    """
    e, N = public_key
    # Возведение в степень по модулю (встроенная функция Python очень быстрая)
    ciphertext = pow(message, e, N)
    return ciphertext

def decrypt(ciphertext, private_key):
    """
    Расшифровывает сообщение C.
    M ≡ C ^ d (mod N)
    """
    d, N = private_key
    message = pow(ciphertext, d, N)
    return message

# =============================================
# 4. ДЕМОНСТРАЦИЯ РАБОТЫ (как в вашем примере)
# =============================================

def demo_with_your_numbers():
    """
    Демонстрация с числами из вашего текста:
    M = 88, e = 9007, p = 101, q = 67, N = 6767, d = 3943
    """
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ С ЧИСЛАМИ ИЗ ВАШЕГО ПРИМЕРА")
    print("=" * 50)
    
    M = 88
    e = 9007
    N = 6767
    d = 3943
    
    print(f"Исходное сообщение M = {M}")
    print(f"Открытый ключ: (e = {e}, N = {N})")
    print(f"Закрытый ключ: (d = {d}, N = {N})")
    
    # Шифрование
    C = pow(M, e, N)
    print(f"\nШифруем: C = {M} ^ {e} mod {N} = {C}")
    
    # Расшифровка
    M_decrypted = pow(C, d, N)
    print(f"Расшифровываем: M' = {C} ^ {d} mod {N} = {M_decrypted}")
    
    print(f"\n✅ Успех: M = {M} == M' = {M_decrypted}")

def demo_random_keys():
    """
    Полноценная демонстрация с генерацией случайных ключей.
    """
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ СО СЛУЧАЙНЫМИ КЛЮЧАМИ")
    print("=" * 50)
    
    # 1. Генерируем ключи
    public_key, private_key = generate_keys()
    e, N = public_key
    d, _ = private_key
    
    print(f"\nОткрытый ключ Алисы: (e = {e}, N = {N})")
    print(f"Закрытый ключ Алисы: (d = {d}, N = {N})")
    
    # 2. Боб хочет отправить сообщение
    M = random.randint(2, N - 2)  # Чтобы M было взаимно просто с N
    print(f"\nСекретное сообщение Боба: M = {M}")
    
    # 3. Боб шифрует открытым ключом Алисы
    C = encrypt(M, public_key)
    print(f"Боб шифрует: C = {M} ^ {e} mod {N} = {C}")
    
    # 4. Алиса расшифровывает своим закрытым ключом
    M_decrypted = decrypt(C, private_key)
    print(f"Алиса расшифровывает: M' = {C} ^ {d} mod {N} = {M_decrypted}")
    
    # 5. Проверка
    if M == M_decrypted:
        print("\n✅ РАСШИФРОВКА ВЫПОЛНЕНА УСПЕШНО!")
    else:
        print("\n❌ ОШИБКА: сообщения не совпадают!")

# =============================================
# 5. ТЕКСТОВОЕ СООБЩЕНИЕ (ДОПОЛНИТЕЛЬНО)
# =============================================

def text_to_numbers(text):
    """Преобразует строку в число (каждый символ -> его ASCII-код)."""
    result = 0
    for ch in text:
        result = result * 256 + ord(ch)
    return result

def numbers_to_text(num):
    """Преобразует число обратно в строку."""
    chars = []
    while num > 0:
        chars.append(chr(num % 256))
        num //= 256
    return ''.join(reversed(chars))

def demo_text_message():
    """
    Демонстрация шифрования текстового сообщения.
    """
    print("\n" + "=" * 50)
    print("ШИФРОВАНИЕ ТЕКСТОВОГО СООБЩЕНИЯ")
    print("=" * 50)
    
    # Генерируем ключи (достаточно большие, чтобы вместить текст)
    # Возьмём p и q побольше
    p = generate_prime(1000, 3000)
    q = generate_prime(1000, 3000)
    while q == p:
        q = generate_prime(1000, 3000)
    
    N = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if e >= phi or math.gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)
        while math.gcd(e, phi) != 1:
            e = random.randint(2, phi - 1)
    
    d = mod_inverse(e, phi)
    public_key = (e, N)
    private_key = (d, N)
    
    print(f"Сгенерирован ключ N = {N} (бит: {N.bit_length()})")
    
    # Исходное сообщение
    original_text = "Hello, RSA!"
    print(f"\nИсходный текст: \"{original_text}\"")
    
    # Преобразуем текст в число
    M = text_to_numbers(original_text)
    print(f"Числовое представление M = {M}")
    
    # Проверяем, что M < N (иначе текст не влезет в один блок)
    if M >= N:
        print("⚠️  Предупреждение: сообщение слишком длинное для одного блока.")
        print("   В реальности используют блочное шифрование или гибридные схемы.")
        return
    
    # Шифруем
    C = encrypt(M, public_key)
    print(f"Шифротекст C = {C}")
    
    # Расшифровываем
    M_dec = decrypt(C, private_key)
    print(f"Расшифрованное число M' = {M_dec}")
    
    # Восстанавливаем текст
    decrypted_text = numbers_to_text(M_dec)
    print(f"Расшифрованный текст: \"{decrypted_text}\"")
    
    if original_text == decrypted_text:
        print("\n✅ Текст успешно расшифрован!")
    else:
        print("\n❌ Ошибка расшифровки текста!")

# =============================================
# 6. ЗАПУСК ВСЕХ ДЕМОНСТРАЦИЙ
# =============================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости (можно убрать)
    random.seed(42)
    
    # 1. Демонстрация с вашими числами
    demo_with_your_numbers()
    
    # 2. Демонстрация со случайно сгенерированными ключами
    demo_random_keys()
    
    # 3. Демонстрация с текстовым сообщением
    demo_text_message()
    
    print("\n" + "=" * 50)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 50)