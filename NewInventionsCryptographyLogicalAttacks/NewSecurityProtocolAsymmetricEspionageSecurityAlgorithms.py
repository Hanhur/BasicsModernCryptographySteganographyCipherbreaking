# Новый протокол защиты RSA и асимметричные алгоритмы защиты от шпионажа
import random
import hashlib
import math

# ---------- Вспомогательные функции для RSA ----------
def is_prime(n, k = 40):
    """Тест Миллера-Рабина для больших чисел"""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    
    # Представление n-1 = d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проверка k раундов
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

def generate_prime(bits = 512):
    """Генерация простого числа заданной битности"""
    while True:
        # Генерируем нечётное число
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1  # Старший и младший бит = 1
        if is_prime(num):
            return num

def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    g, x1, y1 = egcd(b % a, a)
    return (g, y1 - (b // a) * x1, x1)

def modinv(a, m):
    """Обратное число по модулю m"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def generate_rsa_keypair(bits = 1024):
    """
    Генерация пары ключей RSA
    Возвращает: (n, e, d) — открытый (n, e) и закрытый d
    """
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e = 65537 (часто используемое простое число)
    e = 65537
    # Убеждаемся, что gcd(e, phi) = 1
    while math.gcd(e, phi) != 1:
        e = random.randint(3, phi - 1)
    
    d = modinv(e, phi)
    return (n, e, d)  # Возвращаем три элемента

# ---------- Реализация вашего протокола ----------

def bob_encrypt_and_sign(message, alice_public_key, bob_private_key):
    """
    Боб:
    1. Шифрует сообщение открытым ключом Алисы: c = M^e_A mod N_A
    2. Подписывает шифротекст своим закрытым ключом: S = H(c) ^ d_B mod N_B
       (используем хеш, чтобы избежать проблем c > N_B)
    
    Возвращает: (c, signature)
    """
    n_A, e_A, _ = alice_public_key  # Распаковываем (n, e, d)
    n_B, _, d_B = bob_private_key   # Распаковываем (n, e, d)
    
    # 1. Шифрование
    c = pow(message, e_A, n_A)
    
    # 2. Вычисляем хеш от шифротекста (для подписи)
    #    Преобразуем c в байты и хешируем SHA-256
    c_bytes = c.to_bytes((c.bit_length() + 7) // 8, 'big')
    h = int.from_bytes(hashlib.sha256(c_bytes).digest(), 'big')
    
    # 3. Подпись: S = h^d_B mod N_B
    signature = pow(h, d_B, n_B)
    
    return c, signature

def alice_verify_and_decrypt(c, signature, bob_public_key, alice_private_key):
    """
    Алиса:
    1. Проверяет подпись: вычисляет h' = S ^ e_B mod N_B
    2. Сравнивает H(c) с h'
    3. Если совпадают — расшифровывает: M = c ^ d_A mod N_A
    4. Возвращает (message, is_valid)
    """
    n_B, e_B, _ = bob_public_key    # Распаковываем (n, e, d)
    n_A, _, d_A = alice_private_key # Распаковываем (n, e, d)
    
    # 1. Восстанавливаем хеш из подписи
    h_recovered = pow(signature, e_B, n_B)
    
    # 2. Вычисляем хеш от полученного шифротекста
    c_bytes = c.to_bytes((c.bit_length() + 7) // 8, 'big')
    h_calc = int.from_bytes(hashlib.sha256(c_bytes).digest(), 'big')
    
    # 3. Проверка
    if h_recovered != h_calc:
        return None, False  # Подпись неверна — шифротекст изменён
    
    # 4. Расшифровка
    message = pow(c, d_A, n_A)
    return message, True

# ---------- Демонстрация работы ----------

def demo_protocol():
    print("=" * 60)
    print("ПРОТОКОЛ ЗАЩИТЫ RSA ОТ БЭКДОРОВ (ПОДПИСЬ ШИФРОТЕКСТА)")
    print("=" * 60)
    
    # 1. Генерация ключей
    print("\n[1] Генерация ключей RSA (1024 бита)...")
    alice_n, alice_e, alice_d = generate_rsa_keypair(1024)
    bob_n, bob_e, bob_d = generate_rsa_keypair(1024)
    
    # Формируем кортежи для удобства
    alice_public = (alice_n, alice_e, alice_d)
    alice_private = (alice_n, alice_e, alice_d)
    bob_public = (bob_n, bob_e, bob_d)
    bob_private = (bob_n, bob_e, bob_d)
    
    print(f"    Алиса: N = {alice_n}")
    print(f"    Боб:   N = {bob_n}")
    
    # 2. Исходное сообщение
    original_message = 123456789  # Числовое представление
    print(f"\n[2] Исходное сообщение Боба: M = {original_message}")
    
    # 3. Боб шифрует и подписывает
    print("\n[3] Боб шифрует сообщение и подписывает шифротекст...")
    c, signature = bob_encrypt_and_sign(
        original_message, 
        alice_public, 
        bob_private
    )
    print(f"    Шифротекст c = {c}")
    print(f"    Подпись S = {signature}")
    
    # 4. Алиса проверяет и расшифровывает (честный случай)
    print("\n[4] Алиса проверяет подпись и расшифровывает...")
    decrypted, valid = alice_verify_and_decrypt(
        c, signature, 
        bob_public, 
        alice_private
    )
    
    if valid:
        print(f"    ✅ ПОДПИСЬ ВЕРНА! Расшифрованное сообщение: M = {decrypted}")
        print(f"    Сообщение совпадает с исходным: {decrypted == original_message}")
    else:
        print("    ❌ ПОДПИСЬ НЕВЕРНА! Сообщение отклонено.")
    
    # 5. Демонстрация атаки: изменение шифротекста
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АТАКИ (изменение шифротекста)")
    print("=" * 60)
    
    # Злоумышленник изменяет c
    c_modified = c + 1
    print(f"\n[5] Злоумышленник изменил шифротекст: c' = {c_modified}")
    print("    (подпись осталась старой)")
    
    decrypted, valid = alice_verify_and_decrypt(
        c_modified, signature, 
        bob_public, 
        alice_private
    )
    
    if valid:
        print(f"    ⚠️ Расшифровано: M = {decrypted}")
    else:
        print("    ❌ ПОДПИСЬ НЕВЕРНА! Алиса ОТКЛОНИЛА сообщение.")
        print("    ✅ Защита сработала: бэкдор или модификация обнаружены!")
    
    # 6. Демонстрация: если подпись тоже изменена
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: изменение подписи")
    print("=" * 60)
    
    signature_modified = signature + 1
    print(f"\n[6] Злоумышленник изменил подпись: S' = {signature_modified}")
    print("    (шифротекст остался правильным)")
    
    decrypted, valid = alice_verify_and_decrypt(
        c, signature_modified, 
        bob_public, 
        alice_private
    )
    
    if valid:
        print(f"    ⚠️ Расшифровано: M = {decrypted}")
    else:
        print("    ❌ ПОДПИСЬ НЕВЕРНА! Алиса ОТКЛОНИЛА сообщение.")
        print("    ✅ Защита сработала: подпись не совпадает!")
    
    # 7. Итоговый вывод
    print("\n" + "=" * 60)
    print("ВЫВОД:")
    print("  Протокол гарантирует, что Алиса расшифрует ТОЛЬКО")
    print("  шифротекст, подписанный Бобом.")
    print("  Любое изменение c или S приводит к отклонению.")
    print("=" * 60)

if __name__ == "__main__":
    # Для воспроизводимости
    random.seed(42)
    demo_protocol()