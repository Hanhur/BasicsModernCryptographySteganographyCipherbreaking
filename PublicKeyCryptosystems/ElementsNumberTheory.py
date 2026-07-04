# Элементы теории чисел
"""
Программа, реализующая основные алгоритмы теории чисел
из раздела 2.3 "Элементы теории чисел"
"""

import math
import random


def is_prime(n: int) -> bool:
    """
    Проверяет, является ли число простым.
    Определение 2.2: простое число не делится ни на какое другое число,
    кроме самого себя и единицы.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Проверяем делители до sqrt(n)
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factors(n: int) -> list:
    """
    Разложение числа на простые множители.
    Основная теорема арифметики (Теорема 2.3).
    """
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


def gcd_euclid(a: int, b: int) -> int:
    """
    Алгоритм Евклида (Алгоритм 2.1) для нахождения НОД.
    gcd(a, b) = наибольшее число c, которое делит и a, и b.
    """
    # Обеспечиваем a >= b
    if a < b:
        a, b = b, a
    
    while b != 0:
        r = a % b
        a = b
        b = r
    
    return a


def extended_gcd(a: int, b: int) -> tuple:
    """
    Обобщенный алгоритм Евклида (Алгоритм 2.2).
    Возвращает (gcd, x, y), такие что ax + by = gcd(a, b).
    Теорема 2.9.
    """
    if a < b:
        a, b = b, a
    
    # Инициализация строк U и V
    u1, u2, u3 = a, 1, 0
    v1, v2, v3 = b, 0, 1
    
    while v1 != 0:
        q = u1 // v1
        t1 = u1 % v1
        t2 = u2 - q * v2
        t3 = u3 - q * v3
        
        u1, u2, u3 = v1, v2, v3
        v1, v2, v3 = t1, t2, t3
    
    return u1, u2, u3  # (gcd, x, y)


def mod_inverse(c: int, m: int) -> int:
    """
    Вычисляет инверсию c по модулю m: c ^ (-1) mod m.
    Определение 2.6.
    Существует тогда и только тогда, когда gcd(c, m) = 1.
    """
    if gcd_euclid(c, m) != 1:
        raise ValueError(f"Инверсия не существует: gcd({c}, {m}) != 1")
    
    # Используем расширенный алгоритм Евклида
    _, d, _ = extended_gcd(m, c)
    
    # Приводим результат к [0, m-1]
    return d % m


def phi_euler(n: int) -> int:
    """
    Функция Эйлера φ(n) (Определение 2.4).
    Количество чисел в ряду 1..n-1, взаимно простых с n.
    """
    if n == 1:
        return 1
    
    result = n
    temp = n
    
    # Используем разложение на простые множители
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1 if p == 2 else 2
    
    if temp > 1:
        result -= result // temp
    
    return result


def phi_prime(p: int) -> int:
    """Утверждение 2.4: если p простое, то φ(p) = p - 1"""
    if not is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    return p - 1


def phi_product(p: int, q: int) -> int:
    """Утверждение 2.5: если p и q простые, p ≠ q, то φ(pq) = (p-1)(q-1)"""
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p и q должны быть простыми числами")
    if p == q:
        raise ValueError("p и q должны быть различными")
    return (p - 1) * (q - 1)


def modular_power_right_to_left(a: int, x: int, p: int) -> int:
    """
    Возведение в степень по модулю (Алгоритм 2.3).
    Биты показателя просматриваются справа-налево (от младшего к старшему).
    Возвращает a ^ x mod p.
    """
    y = 1
    s = a
    
    while x > 0:
        if x & 1:  # Проверяем младший бит (xi = 1)
            y = (y * s) % p
        s = (s * s) % p
        x >>= 1  # Сдвигаем вправо
    
    return y


def modular_power_left_to_right(a: int, x: int, p: int) -> int:
    """
    Возведение в степень по модулю (Алгоритм 2.4).
    Биты показателя просматриваются слева-направо (от старшего к младшему).
    Возвращает a ^ x mod p.
    """
    # Получаем бинарное представление x
    binary = bin(x)[2:]  # '0b...' отбрасываем
    
    y = 1
    for bit in binary:
        y = (y * y) % p
        if bit == '1':
            y = (y * a) % p
    
    return y


def fermat_theorem(p: int, a: int) -> bool:
    """
    Проверка малой теоремы Ферма (Теорема 2.6):
    Если p простое и 0 < a < p, то a ^ (p-1) mod p = 1.
    """
    if not is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    if not (0 < a < p):
        raise ValueError(f"Должно быть 0 < {a} < {p}")
    
    result = modular_power_right_to_left(a, p - 1, p)
    return result == 1


def euler_theorem(a: int, b: int) -> bool:
    """
    Проверка теоремы Эйлера (Теорема 2.7):
    Если a и b взаимно просты, то a ^ φ(b) mod b = 1.
    """
    if gcd_euclid(a, b) != 1:
        raise ValueError(f"{a} и {b} не взаимно просты")
    
    phi_b = phi_euler(b)
    result = modular_power_right_to_left(a, phi_b, b)
    return result == 1


def euler_corollary(p: int, q: int, a: int, k: int) -> tuple:
    """
    Проверка следствия из теоремы Эйлера (Теорема 2.8):
    Если p и q простые, p ≠ q, то a ^ (k * φ(pq) + 1) mod (pq) = a.
    Возвращает (результат, модуль, степень).
    """
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p и q должны быть простыми")
    if p == q:
        raise ValueError("p и q должны быть различными")
    
    n = p * q
    phi_n = phi_euler(n)
    exponent = k * phi_n + 1
    
    result = modular_power_right_to_left(a, exponent, n)
    return result, n, exponent


class NumberTheoryDemo:
    """Класс для демонстрации всех алгоритмов"""
    
    @staticmethod
    def demo_basic_concepts():
        """Демонстрация основных понятий"""
        print("=" * 60)
        print("1. ОСНОВНЫЕ ПОНЯТИЯ ТЕОРИИ ЧИСЕЛ")
        print("=" * 60)
        
        # Простые и составные числа (Пример 2.3)
        print("\nПример 2.3: Простые и составные числа")
        nums = [11, 23, 27, 33]
        for n in nums:
            status = "простое" if is_prime(n) else "составное"
            factors = prime_factors(n) if not is_prime(n) else []
            if factors:
                print(f"  {n} - {status} (делится на {', '.join(map(str, factors))})")
            else:
                print(f"  {n} - {status}")
        
        # Разложение на простые множители (Пример 2.4)
        print("\nПример 2.4: Разложение на простые множители")
        nums = [27, 33]
        for n in nums:
            factors = prime_factors(n)
            print(f"  {n} = {' · '.join(map(str, factors))}")
    
    @staticmethod
    def demo_gcd():
        """Демонстрация алгоритма Евклида"""
        print("\n" + "=" * 60)
        print("2. НАИБОЛЬШИЙ ОБЩИЙ ДЕЛИТЕЛЬ (АЛГОРИТМ ЕВКЛИДА)")
        print("=" * 60)
        
        # Пример 2.10
        print("\nПример 2.10: Вычисление НОД")
        pairs = [(10, 15), (8, 28), (28, 8)]
        for a, b in pairs:
            result = gcd_euclid(a, b)
            print(f"  gcd({a}, {b}) = {result}")
        
        # Расширенный алгоритм Евклида (Пример 2.12)
        print("\nПример 2.12: Расширенный алгоритм Евклида")
        a, b = 28, 19
        gcd, x, y = extended_gcd(a, b)
        print(f"  gcd({a}, {b}) = {gcd}")
        print(f"  {a}·({x}) + {b}·({y}) = {a * x + b * y}")
        print(f"  Проверка: {a}·({x}) + {b}·({y}) = {a * x + b * y}")
    
    @staticmethod
    def demo_phi():
        """Демонстрация функции Эйлера"""
        print("\n" + "=" * 60)
        print("3. ФУНКЦИЯ ЭЙЛЕРА")
        print("=" * 60)
        
        # Пример 2.6
        print("\nПример 2.6: Вычисление φ(n)")
        nums = [10, 12]
        for n in nums:
            phi = phi_euler(n)
            # Находим взаимно простые числа
            coprime = [i for i in range(1, n) if gcd_euclid(i, n) == 1]
            print(f"  φ({n}) = {phi}")
            print(f"  Взаимно простые с {n}: {coprime}")
        
        # Утверждение 2.4
        print("\nУтверждение 2.4: Если p простое, то φ(p) = p - 1")
        primes = [7, 11, 13]
        for p in primes:
            phi = phi_prime(p)
            print(f"  φ({p}) = {phi} = {p} - 1")
        
        # Утверждение 2.5
        print("\nУтверждение 2.5: φ(pq) = (p - 1)(q - 1)")
        p, q = 3, 5
        n = p * q
        phi = phi_product(p, q)
        print(f"  φ({p}·{q}) = φ({n}) = {phi} = ({p} - 1)·({q} - 1)")
    
    @staticmethod
    def demo_theorems():
        """Демонстрация теорем Ферма и Эйлера"""
        print("\n" + "=" * 60)
        print("4. ТЕОРЕМЫ ФЕРМА И ЭЙЛЕРА")
        print("=" * 60)
        
        # Малая теорема Ферма (Пример 2.7)
        print("\nПример 2.7: Малая теорема Ферма")
        test_cases = [(13, 2), (11, 10)]
        for p, a in test_cases:
            result = modular_power_right_to_left(a, p - 1, p)
            print(f"  {a} ^ {p-1} mod {p} = {result}")
            print(f"  Теорема Ферма: {result == 1}")
        
        # Теорема Эйлера (Пример 2.8)
        print("\nПример 2.8: Теорема Эйлера")
        test_cases = [(5, 12), (2, 21)]
        for a, b in test_cases:
            phi_b = phi_euler(b)
            result = modular_power_right_to_left(a, phi_b, b)
            print(f"  {a} ^ φ({b}) mod {b} = {a} ^ {phi_b} mod {b} = {result}")
            print(f"  Теорема Эйлера: {result == 1}")
        
        # Следствие из теоремы Эйлера (Теорема 2.8, Пример 2.9)
        print("\nПример 2.9: Следствие из теоремы Эйлера")
        p, q = 5, 7
        n = p * q
        phi_n = phi_euler(n)
        print(f"  p = {p}, q = {q}, n = {n}, φ(n) = {phi_n}")
        
        # Для чисел, взаимно простых с n
        print("\n  Для чисел, взаимно простых с n:")
        test_cases = [(9, 2), (23, 2)]
        for a, k in test_cases:
            result, _, exp = euler_corollary(p, q, a, k)
            print(f"    {a} ^ {k}·{phi_n} + 1 mod {n} = {a} ^ {exp} mod {n} = {result}")
            print(f"    Результат {result} {'=' if result == a else '≠'} {a}")
        
        # Для чисел, не взаимно простых с n
        print("\n  Для чисел, НЕ взаимно простых с n (важно!):")
        test_cases = [(10, 2), (28, 2)]
        for a, k in test_cases:
            result, _, exp = euler_corollary(p, q, a, k)
            print(f"    {a} ^ {k}·{phi_n} + 1 mod {n} = {a} ^ {exp} mod {n} = {result}")
            print(f"    Результат {result} {'=' if result == a else '≠'} {a}")
            # Проверяем, что теорема Эйлера не работает
            if gcd_euclid(a, n) != 1:
                euler_result = modular_power_right_to_left(a, phi_n, n)
                print(f"    Заметим: {a} ^ {phi_n} mod {n} = {euler_result} (теорема Эйлера не применима)")
    
    @staticmethod
    def demo_mod_inverse():
        """Демонстрация модульной инверсии"""
        print("\n" + "=" * 60)
        print("5. МОДУЛЬНАЯ ИНВЕРСИЯ")
        print("=" * 60)
        
        # Пример 2.13
        print("\nПример 2.13: Модульная инверсия")
        test_cases = [(3, 11), (5, 11), (7, 11)]
        for c, m in test_cases:
            inv = mod_inverse(c, m)
            check = (c * inv) % m
            print(f"  {c} ^ {-1} mod {m} = {inv}")
            print(f"  Проверка: {c}·{inv} mod {m} = {check} {'✓' if check == 1 else '✗'}")
        
        # Пример 2.14 с расширенным алгоритмом Евклида
        print("\nПример 2.14: Вычисление инверсии через расширенный алгоритм Евклида")
        c, m = 7, 11
        _, d, _ = extended_gcd(m, c)
        print(f"  Решая уравнение m·(-k) + c·d = 1:")
        print(f"  11·(-k) + 7·d = 1")
        print(f"  Получаем d = {d}")
        inv = d % m
        print(f"  {c} ^ {-1} mod {m} = {inv}")
        print(f"  Проверка: {c}·{inv} mod {m} = {(c * inv) % m}")
    
    @staticmethod
    def demo_modular_power():
        """Демонстрация возведения в степень по модулю"""
        print("\n" + "=" * 60)
        print("6. ВОЗВЕДЕНИЕ В СТЕПЕНЬ ПО МОДУЛЮ")
        print("=" * 60)
        
        a, x, p = 2, 100, 1000
        print(f"\nВычисление {a} ^ {x} mod {p}")
        
        # Алгоритм 2.3 (справа-налево)
        result1 = modular_power_right_to_left(a, x, p)
        print(f"  Алгоритм 2.3 (справа-налево):  {result1}")
        
        # Алгоритм 2.4 (слева-направо)
        result2 = modular_power_left_to_right(a, x, p)
        print(f"  Алгоритм 2.4 (слева-направо):  {result2}")
        
        # Проверка
        check = pow(a, x, p)
        print(f"  Встроенная функция pow:       {check}")
        print(f"  Все методы дают {'одинаковый' if result1 == result2 == check else 'разный'} результат")
        
        # Пример с числами из текста
        print("\nПример из текста: 2 ^ 100 mod 13 = 3")
        result = modular_power_right_to_left(2, 100, 13)
        print(f"  2^100 mod 13 = {result}")
        print(f"  Соответствует тексту: {'Да' if result == 3 else 'Нет'}")
    
    @staticmethod
    def run_all_demos():
        """Запуск всех демонстраций"""
        print("\n" + "=" * 70)
        print("ПРОГРАММНАЯ РЕАЛИЗАЦИЯ АЛГОРИТМОВ ТЕОРИИ ЧИСЕЛ")
        print("(на основе раздела 2.3 'Элементы теории чисел')")
        print("=" * 70)
        
        NumberTheoryDemo.demo_basic_concepts()
        NumberTheoryDemo.demo_gcd()
        NumberTheoryDemo.demo_phi()
        NumberTheoryDemo.demo_theorems()
        NumberTheoryDemo.demo_mod_inverse()
        NumberTheoryDemo.demo_modular_power()
        
        print("\n" + "=" * 70)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("=" * 70)


def main():
    """Главная функция программы"""
    # Запуск демонстрации
    NumberTheoryDemo.run_all_demos()
    
    # Дополнительные примеры для самостоятельного экспериментирования
    print("\n" + "=" * 70)
    print("ДОПОЛНИТЕЛЬНЫЕ ПРИМЕРЫ")
    print("=" * 70)
    
    # Пример: проверка взаимной простоты
    print("\nПроверка взаимной простоты:")
    pairs = [(27, 28), (27, 33)]
    for a, b in pairs:
        g = gcd_euclid(a, b)
        status = "взаимно просты" if g == 1 else f"имеют общий делитель {g}"
        print(f"  {a} и {b}: {status}")
    
    # Пример: все инверсии по модулю 11
    print("\nИнверсии по модулю 11:")
    for i in range(1, 11):
        if gcd_euclid(i, 11) == 1:
            inv = mod_inverse(i, 11)
            print(f"  {i} ^ {-1} mod 11 = {inv}")

if __name__ == "__main__":
    main()