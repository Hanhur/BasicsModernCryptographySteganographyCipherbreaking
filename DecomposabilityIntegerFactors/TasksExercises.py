# Задачи и упражнения
# Задача 1. =========================================================================================================================================
# Разложить на множители числа n1 = 21894583143407671, n2 = 317481472366756346287.
import math
import sympy as sp

def factorize_number(n: int) -> dict:
    """
    Разлагает число на простые множители.
    Возвращает словарь {простое число: степень}.
    """
    factors = {}
    temp = n
    
    # Проверка делимости на 2
    while temp % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        temp //= 2
    
    # Проверка делимости на нечётные числа до sqrt(temp)
    p = 3
    while p * p <= temp:
        while temp % p == 0:
            factors[p] = factors.get(p, 0) + 1
            temp //= p
        p += 2
    
    # Если осталось простое число > 1
    if temp > 1:
        # Пробуем использовать sympy для проверки простоты больших остатков
        if sp.isprime(temp):
            factors[temp] = factors.get(temp, 0) + 1
        else:
            # Если sympy говорит, что составное, пытаемся разложить его через sp.factorint
            more_factors = sp.factorint(temp)
            for prime, exp in more_factors.items():
                factors[prime] = factors.get(prime, 0) + exp
    
    return factors

def main():
    # Числа из задачи
    n1 = 2189458
    n2 = 3174814
    
    print("=== Разложение чисел на множители ===\n")
    
    # Факторизация n1
    print(f"n1 = {n1}")
    factors_n1 = factorize_number(n1)
    # Формируем строку с разложением
    factorization_str_n1 = " * ".join([f"{p} ^ {e}" if e > 1 else f"{p}" for p, e in sorted(factors_n1.items())])
    print(f"Разложение n1: {factorization_str_n1}")
    # Проверка, совпадает ли произведение множителей с исходным числом
    check_n1 = math.prod(p ** e for p, e in factors_n1.items())
    print(f"Проверка: {check_n1} == {n1} -> {check_n1 == n1}\n")
    
    # Факторизация n2
    print(f"n2 = {n2}")
    factors_n2 = factorize_number(n2)
    factorization_str_n2 = " * ".join([f"{p} ^ {e}" if e > 1 else f"{p}" for p, e in sorted(factors_n2.items())])
    print(f"Разложение n2: {factorization_str_n2}")
    check_n2 = math.prod(p ** e for p, e in factors_n2.items())
    print(f"Проверка: {check_n2} == {n2} -> {check_n2 == n2}\n")

if __name__ == "__main__":
    main()

# Задача 2. =========================================================================================================================================
import math

def is_prime(n: int) -> bool:
    """Проверка, является ли число n простым."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Проверяем делители вида 6k ± 1 до sqrt(n)
    limit = int(math.isqrt(n))
    i = 5
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def find_sophie_germain(start_p: int = 2100):
    """
    Находит наименьшее простое p >= start_p, такое что (p -1 ) / 2 тоже простое.
    """
    # Минимальное q, которое может дать p >= start_p
    q_start = (start_p - 1) // 2
    # Начинаем перебор с q_start, но корректируем, чтобы q было нечётным (кроме 2)
    if q_start < 2:
        q_start = 2
    # Если q_start чётное и больше 2, делаем нечётным
    if q_start % 2 == 0 and q_start > 2:
        q_start += 1

    q = q_start
    while True:
        # Для ускорения: p = 2q+1 не должно делиться на 3
        # То есть q % 3 должно быть равно 2 (так как 2*2+1=5 ≡ 2 mod 3)
        # Если q=2, это особый случай (p=5), но для q>=1050 это неактуально
        if q % 3 == 2 or q == 2:
            if is_prime(q):
                p = 2 * q + 1
                if is_prime(p):
                    return p, q
        q += 2  # Перебираем только нечётные q (чётные >2 не простые)

if __name__ == "__main__":
    p, q = find_sophie_germain(2100)
    print(f"Найдено простое число Софи Жермен:")
    print(f"q = {q} (простое)")
    print(f"p = 2q + 1 = {p} (простое)")
    print(f"p >= 2100: {p >= 2100}")

# Задача 3. =========================================================================================================================================
import math
import random

# ---------- Проверка на простоту (тест Миллера–Рабина) ----------
def is_probable_prime(n, k = 10):
    """Вероятностный тест простоты Миллера–Рабина."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True

    for _ in range(k):
        a = random.randint(2, n - 2)
        if check_composite(a):
            return False
    return True

# ---------- Алгоритм Полларда ρ ----------
def pollards_rho(n, seed = 2, c = 1):
    """Возвращает нетривиальный делитель n или n, если не найден."""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3

    def f(x):
        return (pow(x, 2, n) + c) % n

    x = seed
    y = seed
    d = 1
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), n)
    return d if d != n else None

# ---------- Факторизация с помощью малых простых и ρ ----------
def factorize(n, small_prime_limit = 10 ** 6):
    """Разложение на множители. Возвращает словарь {простой: степень}."""
    factors = {}

    # 1. Обработка малых делителей
    # Генерируем простые до small_prime_limit решетом Эратосфена (упрощённо)
    sieve = [True] * (small_prime_limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(small_prime_limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, small_prime_limit + 1, i):
                sieve[j] = False
    primes = [i for i, is_prime in enumerate(sieve) if is_prime]

    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            cnt = 0
            while n % p == 0:
                n //= p
                cnt += 1
            factors[p] = cnt

    # 2. Если остаток > 1 и он простой
    if n > 1 and is_probable_prime(n):
        factors[n] = factors.get(n, 0) + 1
        return factors

    # 3. Иначе пробуем Полларда ρ, чтобы разбить составной остаток
    remaining = n
    if remaining > 1:
        # Пытаемся факторизовать остаток с помощью ρ
        stack = [remaining]
        while stack:
            cur = stack.pop()
            if cur == 1:
                continue
            if is_probable_prime(cur):
                factors[cur] = factors.get(cur, 0) + 1
                continue
            d = pollards_rho(cur)
            if d and d != cur:
                stack.append(d)
                stack.append(cur // d)
            else:
                # Не удалось разложить — оставляем как есть
                factors[cur] = factors.get(cur, 0) + 1
    return factors

# ---------- Основная часть: заданные числа ----------
numbers = [
    5739861760560673878097455365537181774496887708448761680768591535390324,
    3000482301261042233534380159958868822954036395871448716256542877572006105366916299426263644379470339,
    166045890368446099470756111654736772731460671003059151938763854196360081247044441029824134260263654537
]

for idx, num in enumerate(numbers, start = 1):
    print(f"\n=== Факторизация n{idx} ===")
    print(f"Число: {num}")
    factors = factorize(num)
    if not factors:
        print("Не удалось разложить на множители.")
    else:
        # Вывод в виде произведения степеней простых
        expr = " * ".join(f"{p}^{e}" if e > 1 else f"{p}" for p, e in sorted(factors.items()))
        print(f"Разложение: {expr}")