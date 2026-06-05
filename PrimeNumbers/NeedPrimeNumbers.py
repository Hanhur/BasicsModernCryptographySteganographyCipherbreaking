# 1. Потребность в простых числах
import random
import math

# --------------------------------------------
# 1. Модуль для работы с большими числами
# --------------------------------------------

def is_prime_miller_rabin(n, k = 40):
    """
    Тест Миллера-Рабина для больших чисел.
    n - проверяемое число (нечетное, > 3)
    k - количество раундов (чем больше, тем точнее)
    Вероятность ошибки ~ 4^{-k}
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Представить n-1 как d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True  # составное

    for _ in range(k):
        a = random.randrange(2, n - 1)
        if check_composite(a):
            return False
    return True


def sieve_small_primes(limit = 10000):
    """Решето Эратосфена для маленьких простых чисел (используется для предварительного отсева)"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i, prime in enumerate(is_prime) if prime]


SMALL_PRIMES = sieve_small_primes(10000)


def has_small_prime_divisor(n, small_primes):
    """Проверяет, делится ли n на одно из маленьких простых чисел"""
    for p in small_primes:
        if n % p == 0:
            return True
        if p * p > n:  # можно прервать раньше, но для маленьких p это быстро
            break
    return False


def generate_random_prime(bits, k = 40):
    """
    Генерирует случайное простое число заданной битности.
    bits - длина в битах (например, 1024, 2048)
    k - раундов Миллера-Рабина
    """
    if bits < 2:
        raise ValueError("Размер в битах должен быть >= 2")

    while True:
        # Генерируем случайное нечетное число нужной длины
        candidate = random.getrandbits(bits)
        # Устанавливаем старший и младший биты в 1 (чтобы было точно нужной длины и нечетное)
        candidate |= (1 << (bits - 1)) | 1

        # Быстрый отсев по маленьким простым
        if has_small_prime_divisor(candidate, SMALL_PRIMES):
            continue

        # Основная проверка на простоту
        if is_prime_miller_rabin(candidate, k):
            return candidate


def generate_safe_prime(bits, k = 40):
    """
    Генерирует безопасное простое p = 2 * q + 1, где q тоже простое.
    bits - битность p (должно быть чуть больше битности q)
    """
    while True:
        # Генерируем q с битностью на 1 меньше (или чуть меньше)
        q_bits = bits - 1
        q = generate_random_prime(q_bits, k)

        p = 2 * q + 1
        # Проверяем, что p простое
        if has_small_prime_divisor(p, SMALL_PRIMES):
            continue
        if is_prime_miller_rabin(p, k):
            return p, q


# --------------------------------------------
# 2. Примеры использования
# --------------------------------------------

if __name__ == "__main__":
    print("=== Генерация простых чисел для криптографии ===\n")

    # Пример 1: простое число для RSA (2048 бит)
    print("1. Генерация случайного простого числа (2048 бит):")
    bits_rsa = 2048
    prime_rsa = generate_random_prime(bits_rsa)
    print(f"   Простое число (первые 50 цифр): {prime_rsa}")
    print(f"   Длина в битах: {prime_rsa.bit_length()}")
    print()

    # Пример 2: безопасное простое для дискретного логарифма (1024 бита)
    print("2. Генерация безопасного простого p = 2q+1 (1024 бита):")
    bits_safe = 1024
    p_safe, q_safe = generate_safe_prime(bits_safe)
    print(f"   p (safe prime): {p_safe}")
    print(f"   q (простое):    {q_safe}")
    print(f"   Битность p: {p_safe.bit_length()}, q: {q_safe.bit_length()}")
    print(f"   Проверка: p = 2 * q + 1? {p_safe == 2 * q_safe + 1}")
    print()

    # Пример 3: небольшое простое для демонстрации
    print("3. Демонстрация: небольшое простое число (512 бит):")
    prime_demo = generate_random_prime(512)
    print(f"   Простое: {prime_demo}")
    print(f"   Битность: {prime_demo.bit_length()}")
    print(f"   Является простым? {is_prime_miller_rabin(prime_demo)}")