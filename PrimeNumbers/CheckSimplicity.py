# 2. Проверка на простоту
import random
import math

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def gcd(a, b):
    """Наибольший общий делитель."""
    while b:
        a, b = b, a % b
    return a

def factor_out_twos(n_minus_1):
    """
    Представляет n-1 = 2 ^ s * t, где t нечётное.
    Возвращает (s, t).
    """
    s = 0
    t = n_minus_1
    while t % 2 == 0:
        t //= 2
        s += 1
    return s, t

def modular_pow(base, exponent, mod):
    """Быстрое возведение в степень по модулю: base^exponent % mod."""
    result = 1
    base = base % mod
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exponent >>= 1
    return result


# ========== ТЕСТ МИЛЛЕРА–РАБИНА (вероятностный) ==========
def is_strong_pseudoprime(n, b):
    """
    Проверяет, является ли n сильно псевдопростым по основанию b.
    (как в определении из текста)
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # НОД(b, n) должен быть 1, иначе n составное
    if gcd(b, n) != 1:
        return False
    
    s, t = factor_out_twos(n - 1)
    
    # Вычисляем b^t mod n
    x = modular_pow(b, t, n)
    
    if x == 1 or x == n - 1:
        return True
    
    # Последовательно возводим в квадрат
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return True
        if x == 1:
            return False
    
    return False

def miller_rabin(n, k=10):
    """
    Тест Миллера–Рабина.
    n — проверяемое нечётное число.
    k — количество случайных оснований (чем больше, тем точнее).
    
    Возвращает:
        True  — n вероятно простое
        False — n составное
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Проверяем k случайных оснований
    for _ in range(k):
        b = random.randint(2, n - 2)
        # Пропускаем основания, не взаимно простые с n
        while gcd(b, n) != 1:
            b = random.randint(2, n - 2)
        
        if not is_strong_pseudoprime(n, b):
            return False
    
    return True


# ========== ПРОВЕРКА НА ЧИСЛО КАРМАЙКЛА ==========
def prime_factors(n):
    """Разложение n на простые множители (для небольших n)."""
    factors = []
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors

def is_carmichael(n):
    """
    Проверяет, является ли n числом Кармайкла по критерию из предложения 34:
    1) n — составное нечётное
    2) n свободно от квадратов (все простые делители различны)
    3) Для каждого простого делителя p: (p - 1) делит (n - 1)
    """
    if n < 2 or n % 2 == 0:
        return False
    
    factors = prime_factors(n)
    
    # Составное?
    if len(factors) < 2:
        return False
    
    # Свободно от квадратов?
    if len(set(factors)) != len(factors):
        return False
    
    # Условие (p-1) | (n-1) для каждого простого делителя
    for p in set(factors):
        if (n - 1) % (p - 1) != 0:
            return False
    
    return True


# ========== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ==========
if __name__ == "__main__":
    # Примеры из текста
    test_numbers = [
        561,            # число Кармайкла (3·11·17)
        1105,           # число Кармайкла (5·13·17)
        1729,           # число Кармайкла (7·13·19)
        3215031751,     # из текста: выдерживает тест для b=2,3,5,7, но составное
        17,             # простое
        997,            # простое
        1000003,        # простое (проверьте)
        1000000007,     # простое
        10403,          # псевдопростое по основанию 2? Проверим тестом
    ]
    
    print("=" * 60)
    print("Проверка на числа Кармайкла:")
    print("=" * 60)
    for num in test_numbers:
        if is_carmichael(num):
            print(f"{num} — ЧИСЛО КАРМАЙКЛА")
    
    print("\n" + "=" * 60)
    print("Тест Миллера–Рабина (k = 10 случайных оснований):")
    print("=" * 60)
    
    for num in test_numbers:
        # Определяем, простое ли число
        is_prime = miller_rabin(num, k = 10)
        status = "ПРОСТОЕ (вероятно)" if is_prime else "СОСТАВНОЕ"
        print(f"{num}: {status}")
    
    print("\n" + "=" * 60)
    print("Демонстрация сильной псевдопростоты для конкретных оснований:")
    print("=" * 60)
    
    # Пример из текста: n=3215031751 выдерживает b=2,3,5,7
    n_example = 3215031751
    print(f"\nЧисло {n_example}:")
    for b in [2, 3, 5, 7]:
        spsp = is_strong_pseudoprime(n_example, b)
        print(f"  Сильно псевдопростое по основанию {b}: {spsp}")
    
    # Проверка на псевдопростоту (простой тест Ферма) из начала текста
    print("\n" + "=" * 60)
    print("Псевдопростота (Ферма) по основанию b:")
    print("=" * 60)
    
    def is_fermat_pseudoprime(n, b):
        """Проверка по малой теореме Ферма: b ^ (n - 1) ≡ 1 mod n"""
        if gcd(b, n) != 1:
            return False
        return modular_pow(b, n - 1, n) == 1
    
    n_test = 561  # число Кармайкла
    print(f"\nЧисло {n_test} (Кармайкл):")
    for b in [2, 3, 5, 7, 11]:
        print(f"  Псевдопростое по основанию {b}: {is_fermat_pseudoprime(n_test, b)}")