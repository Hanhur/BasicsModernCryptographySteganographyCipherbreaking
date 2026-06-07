# 4. Возможные атаки на подпись в системе RSA
import random
from typing import Tuple

# ------------------- Вспомогательные функции RSA -------------------
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def modinv(a: int, m: int) -> int:
    # Расширенный алгоритм Евклида
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def is_prime(n: int, k: int = 5) -> bool:
    # Простая проверка на простоту (для малых чисел)
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
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

def generate_prime(bits: int = 16) -> int:
    # Генерация простого числа (для демонстрации, битность мала)
    while True:
        n = random.randrange(2 ** (bits - 1), 2 ** bits)
        if n % 2 == 0:
            n += 1
        if is_prime(n):
            return n

def generate_rsa_keys(bits: int = 16) -> Tuple[int, int, int]:
    # Генерация ключей RSA: (n, e, d)
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if gcd(e, phi) != 1:
        e = 17
        while gcd(e, phi) != 1:
            e += 2
    d = modinv(e, phi)
    return (n, e, d)

# ------------------- Демонстрация уязвимостей -------------------

def demo_multiplicativity():
    """Уязвимость 1: мультипликативность подписи без хэш-функции"""
    print("\n" + "=" * 60)
    print("1. УЯЗВИМОСТЬ МУЛЬТИПЛИКАТИВНОСТИ (без R)")
    print("=" * 60)
    
    n, e, d = generate_rsa_keys(12)  # маленькие числа для наглядности
    print(f"Ключи Алисы: n = {n}, e = {e}, d = {d}")
    
    # Два сообщения
    m1 = 123
    m2 = 456
    print(f"Сообщение m1 = {m1}, m2 = {m2}")
    
    # Подписи (без хэша, R тождественна)
    s1 = pow(m1, d, n)
    s2 = pow(m2, d, n)
    print(f"Подпись s1 = {s1}, s2 = {s2}")
    
    # Атака: комбинируем подписи
    s_fake = (s1 * s2) % n
    m_fake = (m1 * m2) % n
    
    # Проверка: подпись подходит для произведения
    check = pow(s_fake, e, n)
    print(f"\nКомбинированная подпись s_fake = {s_fake}")
    print(f"Проверка: s_fake^e mod n = {check}")
    print(f"Произведение сообщений m1 * m2 mod n = {m_fake}")
    if check == m_fake:
        print("УСПЕХ АТАКИ: подпись на произведении подделана без знания секретного ключа!")
    else:
        print("Атака не удалась (маловероятно при правильной реализации RSA)")
    
    print("\nЗащита: использовать хэш-функцию R, где R(m1 * m2) ≠ R(m1) * R(m2)")

def demo_sign_on_encrypted():
    """Уязвимость 2: Подпись на зашифрованном документе"""
    print("\n" + "=" * 60)
    print("2. АТАКА: ПОДПИСЬ НА ЗАШИФРОВАННОМ ДОКУМЕНТЕ")
    print("=" * 60)
    
    # Генерация ключей для A, B, C
    nA, eA, dA = generate_rsa_keys(12)
    nB, eB, dB = generate_rsa_keys(12)
    nC, eC, dC = generate_rsa_keys(12)
    
    print(f"Алиса: nA = {nA}, eA = {eA}")
    print(f"Боб:   nB = {nB}, eB = {eB}")
    print(f"Мэллори: nC = {nC}, eC = {eC}")
    
    # Документ m
    m = 42
    print(f"\nДокумент m = {m}")
    
    # Легитимная схема: шифрование для Боба → подпись Алисы
    encrypted = pow(m, eB, nB)      # шифруем для Боба
    print(f"Зашифрованный для Боба: c = {encrypted}")
    
    # Алиса подписывает зашифрованное (без R)
    signature = pow(encrypted, dA, nA)
    print(f"Алиса подписывает c: s = {signature}")
    
    # ----- АТАКА МЭЛЛОРИ -----
    # 1. Снимает подпись Алисы с помощью её открытого ключа
    recovered = pow(signature, eA, nA)
    print(f"\nМэллори снимает подпись: recovered = {recovered}")
    print(f"  (должно быть равно c = {encrypted})")
    
    # 2. Подписывает своим ключом
    fake_signature = pow(recovered, dC, nC)
    print(f"Мэллори накладывает свою подпись: s_fake = {fake_signature}")
    
    # Проверка: чужая подпись на чужом зашифрованном документе
    check = pow(fake_signature, eC, nC)
    print(f"\nПроверка подписи Мэллори: s_fake ^ eC mod nC = {check}")
    print(f"Исходное зашифрованное c = {encrypted}")
    if check == encrypted:
        print("УСПЕХ АТАКИ: Мэллори подменил подпись, не зная m!")
    else:
        print("Атака не удалась")

def demo_order_problem():
    """Уязвимость 3: Ошибка порядка (подпись → шифрование)"""
    print("\n" + "=" * 60)
    print("3. ОШИБКА: СНАЧАЛА ПОДПИСЬ, ПОТОМ ШИФРОВАНИЕ")
    print("=" * 60)
    
    # Специально делаем модуль подписи > модуля шифрования
    nA, eA, dA = generate_rsa_keys(14)   # больший модуль
    nB, eB, dB = generate_rsa_keys(12)   # меньший модуль
    
    # Гарантируем nA > nB
    while nA <= nB:
        nA, eA, dA = generate_rsa_keys(14)
        nB, eB, dB = generate_rsa_keys(12)
    
    print(f"Алиса (подпись): nA = {nA}")
    print(f"Боб (шифрование): nB = {nB}")
    
    # Сообщение m (меньше nA, но может быть больше nB)
    m = random.randrange(nB + 1, nA - 1)
    print(f"\nСообщение m = {m} (m > nB, что уже проблема)")
    
    # 1. Сначала подпись
    s = pow(m, dA, nA)
    print(f"Подпись Алисы s = {s}")
    
    # 2. Потом шифрование для Боба
    try:
        c = pow(s, eB, nB)
        print(f"Шифрование для Боба: c = {c}")
        
        # Расшифровка и проверка
        s_recovered = pow(c, dB, nB)
        print(f"Боб расшифровал: s_recovered = {s_recovered}")
        
        m_recovered = pow(s_recovered, eA, nA)
        print(f"Восстановленное m' = {m_recovered}")
        
        if m_recovered != m:
            print("\n!!! ОШИБКА: сообщение не восстановилось !!!")
            print(f"Исходное m = {m}, получено m' = {m_recovered}")
            print("Причина: подпись s была больше модуля nB, произошла потеря информации")
        else:
            print("Повезло: s < nB, ошибки нет")
            
    except Exception as ex:
        print(f"Ошибка при шифровании/расшифровании: {ex}")
    
    print("\nЗащита: модуль для подписи всегда < модуля для шифрования")
    print("или использовать разные системы для подписи и шифрования")

# ------------------- Запуск всех демонстраций -------------------
if __name__ == "__main__":
    random.seed(42)  # для воспроизводимости
    
    demo_multiplicativity()
    demo_sign_on_encrypted()
    demo_order_problem()
    
    print("\n" + "=" * 60)
    print("ВЫВОД: Функция R (хэш/рандомизация) и правильный порядок")
    print("операций критически важны для безопасности подписи RSA.")
    print("=" * 60)