# 3. Построение больших простых чисел
"""
Генерация больших простых чисел на основе теоремы 38
n = qr + 1, где q - простое, r - четное, q <= r <= 4q + 2
"""

import random
import math
import sys


def is_prime_miller_rabin(n, k = 10):
    """Вероятностный тест Миллера-Рабина для проверки простоты"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Записываем n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return False
        return True

    for _ in range(k):
        a = random.randrange(2, n - 1)
        if check_composite(a):
            return False
    return True


def is_prime_division(n):
    """Проверка простоты делением на маленькие простые числа"""
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in small_primes:
        if n % p == 0:
            return n == p
    return True


def generate_small_prime(bits):
    """Генерация небольшого простого числа заданной битовой длины"""
    while True:
        n = random.randrange(2 ** (bits - 1), 2 ** bits)
        if n % 2 == 0:
            n += 1
        if is_prime_division(n) and is_prime_miller_rabin(n):
            return n


def find_a(n, q, r, max_attempts = 100):
    """
    Поиск числа a, удовлетворяющего условиям теоремы 38:
    1) a ^ (n - 1) ≡ 1 (mod n)
    2) НОД(a ^ r - 1, n) = 1
    """
    for attempt in range(max_attempts):
        a = random.randrange(2, n - 1)

        # Проверка первого условия
        if pow(a, n - 1, n) != 1:
            continue

        # Проверка второго условия: a^r mod n не должно быть 1
        a_pow_r = pow(a, r, n)
        if a_pow_r == 1:
            continue

        # Проверка НОД(a^r - 1, n) = 1
        if math.gcd(a_pow_r - 1, n) == 1:
            return a

    return None


def build_next_prime(q, max_attempts_r = 50, max_attempts_a = 100):
    """
    По заданному простому q строит простое n = qr + 1
    с условием q <= r <= 4q + 2, r четное
    """
    for _ in range(max_attempts_r):
        # Выбираем случайное четное r в диапазоне [q, 4q+2]
        r = random.randrange(q, 4 * q + 3)
        if r % 2 != 0:
            r += 1
        if r < q:
            r = q
            if r % 2 != 0:
                r += 1

        n = q * r + 1

        # Небольшая предварительная проверка
        if n % 2 == 0 or n % 3 == 0:
            continue

        # Ищем подходящее a
        a = find_a(n, q, r, max_attempts_a)
        if a is not None:
            # Дополнительная проверка: гарантия из предложения 39
            if r <= 4 * q + 2:
                print(f"  Найдено: n = {n} (q = {q}, r = {r})")
                print(f"  a = {a}")
                return n
            # Если r > 4q+2, теорема не гарантирует простоту,
            # но можно проверить отдельно
            if is_prime_miller_rabin(n):
                return n

    return None


def generate_large_prime(target_bits, start_bits = 8):
    """
    Генерация простого числа заданной битовой длины
    с использованием многократного применения теоремы
    """
    # Начинаем с малого простого числа
    q = generate_small_prime(start_bits)
    print(f"Стартовое простое: {q}")

    primes = [q]
    iteration = 0

    while q.bit_length() < target_bits:
        iteration += 1
        print(f"\nИтерация {iteration}: q = {q} (бит: {q.bit_length()})")

        n = build_next_prime(q)
        if n is None:
            print("  Не удалось найти n, пробуем другое q...")
            q = generate_small_prime(start_bits)
            primes = [q]
            continue

        primes.append(n)
        q = n

        if q.bit_length() >= target_bits:
            break

    print(f"\n{'=' * 60}")
    print(f"Финальное простое число ({q.bit_length()} бит):")
    print(f"{q}")
    print(f"\nЦепочка построения:")
    for i, p in enumerate(primes):
        print(f"  q{i + 1} = {p}")
    return q


def main():
    print("Генератор больших простых чисел")
    print("Основан на теореме 38 и предложении 39\n")

    # Пример: генерация 256-битного простого числа
    bits = 256

    print(f"Генерация {bits}-битного простого числа...\n")

    prime = generate_large_prime(bits, start_bits = 8)

    # Финальная проверка
    print(f"\nФинальная проверка: число {'ПРОСТОЕ' if is_prime_miller_rabin(prime, k = 20) else 'СОСТАВНОЕ'}")


if __name__ == "__main__":
    main()