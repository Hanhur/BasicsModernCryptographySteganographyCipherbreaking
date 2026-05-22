# Задачи и упражнения
# Задача 1. Используя обобщенный алгоритм Эвклида, найти 19- 1 (mod26), 13-1 (mod834).
def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y), такие что a * x + b * y = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y


def modular_inverse(a, m):
    """
    Находит обратный элемент a^(-1) mod m.
    Возвращает число x, такое что (a * x) % m == 1
    """
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратный элемент не существует: НОД({a}, {m}) = {gcd}")
    else:
        # x может быть отрицательным, приводим к положительному значению по модулю m
        return x % m


def main():
    # Задача 2.1: найти 19^(-1) mod 26 и 13^(-1) mod 834
    examples = [
        (19, 26, "19^(-1) mod 26"),
        (13, 834, "13^(-1) mod 834")
    ]

    for a, m, description in examples:
        try:
            inv = modular_inverse(a, m)
            print(f"{description} = {inv}")
            # Проверка:
            print(f"Проверка: {a} * {inv} mod {m} = {(a * inv) % m}\n")
        except ValueError as e:
            print(f"{description}: {e}\n")


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 2. Используя лишь калькулятор, найти число х, удовлетворяющее уравнению 3х = 5(modp), где р - 1 = 2 * 3 * 101 * 103 * 1072. 
# Упрощенный вариант: р - 1 = 2 * 3 * 101 , или еще проще: р - 1 = 2 * 3 * 11.
def modular_inverse(a, m):
    """
    Находит обратный элемент a^(-1) mod m с помощью расширенного алгоритма Евклида.
    """
    # Расширенный алгоритм Евклида
    def egcd(a, b):
        if b == 0:
            return a, 1, 0
        gcd, x1, y1 = egcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return gcd, x, y

    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратный элемент не существует: НОД({a}, {m}) = {gcd}")
    return x % m


def solve_linear_congruence(a, b, m):
    """
    Решает уравнение a * x ≡ b (mod m)
    Возвращает решение x (mod m)
    """
    inv_a = modular_inverse(a, m)
    x = (b * inv_a) % m
    return x


def main():
    print("Задача: найти x, удовлетворяющее 3x ≡ 5 (mod p)")
    print("-" * 50)
    
    # Вариант 1: самый простой (p-1 = 2 * 3 * 11)
    p1 = 2 * 3 * 11 + 1
    a, b = 3, 5
    x1 = solve_linear_congruence(a, b, p1)
    print(f"Вариант 1: p = {p1}")
    print(f"Решение: x ≡ {x1} (mod {p1})")
    print(f"Проверка: {a} * {x1} mod {p1} = {(a * x1) % p1}\n")
    
    # Вариант 2: средний (p-1 = 2 * 3 * 101)
    p2 = 2 * 3 * 101 + 1
    x2 = solve_linear_congruence(a, b, p2)
    print(f"Вариант 2: p = {p2}")
    print(f"Решение: x ≡ {x2} (mod {p2})")
    print(f"Проверка: {a} * {x2} mod {p2} = {(a * x2) % p2}\n")
    
    # Вариант 3: полный (p-1 = 2 * 3 * 101 * 103 * 107^2)
    # Вычисляем p
    p3_minus_1 = 2 * 3 * 101 * 103 * (107 ** 2)
    p3 = p3_minus_1 + 1
    x3 = solve_linear_congruence(a, b, p3)
    print(f"Вариант 3: p = {p3}")
    print(f"Решение: x ≡ {x3} (mod {p3})")
    print(f"Проверка: {a} * {x3} mod {p3} = {(a * x3) % p3}\n")
    
    # Дополнительно: покажем процесс нахождения обратного элемента для полного варианта
    print("-" * 50)
    print("Альтернативный метод для полного варианта (подбор m):")
    print(f"Ищем k такое, что 3k = 1 + m*{p3}")
    
    # Можно найти обратный элемент перебором m от 1 до 3
    for m in range(1, 4):
        candidate = 1 + m * p3
        if candidate % 3 == 0:
            inv = candidate // 3
            print(f"При m = {m}: 1 + {m}*{p3} = {candidate}")
            print(f"3^{-1} mod {p3} = {inv}")
            x_alt = (b * inv) % p3
            print(f"x = {b} * {inv} mod {p3} = {x_alt}")
            print(f"Проверка: {a} * {x_alt} mod {p3} = {(a * x_alt) % p3}")
            break


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача3. П о Китайской теореме об остатках вычислить х (найти общее решение) для следующей системы сравнений: 
# x = 5(mod 7),
# x = 3(mod 11),
# x = 10(mod 13).
def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y), такие что a * x + b * y = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y


def modular_inverse(a, m):
    """
    Находит обратный элемент a^(-1) mod m.
    """
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратный элемент не существует: НОД({a}, {m}) = {gcd}")
    return x % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Решает систему сравнений:
    x ≡ remainders[i] (mod moduli[i]) для всех i
    
    Аргументы:
        remainders: список остатков [a1, a2, ..., ak]
        moduli: список модулей [m1, m2, ..., mk] (попарно взаимно простые)
    
    Возвращает:
        x (mod M), где M = произведение всех модулей
    """
    if len(remainders) != len(moduli):
        raise ValueError("Списки остатков и модулей должны быть одинаковой длины")
    
    # Вычисляем общее произведение модулей
    M = 1
    for m in moduli:
        M *= m
    
    # Вычисляем решение по формуле CRT
    result = 0
    for i in range(len(moduli)):
        # Mi = M / mi
        Mi = M // moduli[i]
        
        # Находим yi = Mi^(-1) mod mi
        yi = modular_inverse(Mi, moduli[i])
        
        # Добавляем слагаемое ai * Mi * yi
        result += remainders[i] * Mi * yi
    
    # Приводим результат по модулю M
    return result % M


def solve_system_example():
    """
    Решает систему из задачи:
    x ≡ 5 (mod 7)
    x ≡ 3 (mod 11)
    x ≡ 10 (mod 13)
    """
    remainders = [5, 3, 10]
    moduli = [7, 11, 13]
    
    print("Решение системы сравнений:")
    print("x ≡ 5 (mod 7)")
    print("x ≡ 3 (mod 11)")
    print("x ≡ 10 (mod 13)")
    print("-" * 50)
    
    # Находим решение
    x = chinese_remainder_theorem(remainders, moduli)
    M = 7 * 11 * 13
    
    print(f"M = 7 * 11 * 13 = {M}")
    print(f"Решение: x ≡ {x} (mod {M})")
    print("\nПроверка:")
    
    # Проверяем каждое сравнение
    for i in range(len(moduli)):
        print(f"{x} mod {moduli[i]} = {x % moduli[i]} (должно быть {remainders[i]})")
        assert x % moduli[i] == remainders[i], f"Ошибка в проверке для модуля {moduli[i]}"
    
    print("\n✓ Все проверки пройдены успешно!")


def show_detailed_calculation():
    """
    Показывает пошаговое вычисление (как в ручном решении)
    """
    print("\n" + "=" * 50)
    print("ДЕТАЛЬНЫЙ РАСЧЁТ (как в ручном решении):")
    print("=" * 50)
    
    remainders = [5, 3, 10]
    moduli = [7, 11, 13]
    
    # Вычисляем M и Mi
    M = 7 * 11 * 13
    M1 = 11 * 13  # 143
    M2 = 7 * 13   # 91
    M3 = 7 * 11   # 77
    
    print(f"M = {M}")
    print(f"M1 = {M1}, M2 = {M2}, M3 = {M3}\n")
    
    # Находим обратные элементы
    y1 = modular_inverse(M1, 7)
    y2 = modular_inverse(M2, 11)
    y3 = modular_inverse(M3, 13)
    
    print(f"y1 = {M1}^(-1) mod 7 = {y1} (так как {M1} mod 7 = {M1 % 7}, и {M1 % 7} * {y1} ≡ 1 mod 7)")
    print(f"y2 = {M2}^(-1) mod 11 = {y2} (так как {M2} mod 11 = {M2 % 11}, и {M2 % 11} * {y2} ≡ 1 mod 11)")
    print(f"y3 = {M3}^(-1) mod 13 = {y3} (так как {M3} mod 13 = {M3 % 13}, и {M3 % 13} * {y3} ≡ 1 mod 13)\n")
    
    # Вычисляем решение
    term1 = 5 * M1 * y1
    term2 = 3 * M2 * y2
    term3 = 10 * M3 * y3
    
    print(f"Член 1: a1*M1*y1 = 5 * {M1} * {y1} = {term1}")
    print(f"Член 2: a2*M2*y2 = 3 * {M2} * {y2} = {term2}")
    print(f"Член 3: a3*M3*y3 = 10 * {M3} * {y3} = {term3}")
    
    total = term1 + term2 + term3
    print(f"\nСумма: {term1} + {term2} + {term3} = {total}")
    
    x = total % M
    print(f"x ≡ {total} mod {M} = {x}")
    
    return x


def main():
    # Основное решение
    solve_system_example()
    
    # Детальный пошаговый расчёт
    x = show_detailed_calculation()
    
    print("\n" + "=" * 50)
    print(f"ИТОГОВЫЙ ОТВЕТ: x ≡ {x} (mod 1001)")
    print("=" * 50)


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 4. Используя Китайскую теорему об остатках, вычислить х (найти общее решение) для следующей системы сравнений:
# x = 1(mod 15),
# x = 3(mod 17),
# x = 3(mod 24),
# x = 4(mod 19).
# Существует ли решение, если вместо 19 взять в качестве последнего модуля 18?
from math import gcd
from functools import reduce


def extended_gcd(a, b):
    """Расширенный алгоритм Евклида."""
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y


def modular_inverse(a, m):
    """Находит обратный элемент a^(-1) mod m."""
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратный элемент не существует: НОД({a}, {m}) = {gcd}")
    return x % m


def lcm(a, b):
    """Наименьшее общее кратное."""
    return a * b // gcd(a, b)


def lcm_list(numbers):
    """НОК списка чисел."""
    return reduce(lcm, numbers)


def solve_crt(remainders, moduli):
    """
    Решает систему сравнений с попарно взаимно простыми модулями.
    Возвращает x mod M.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Списки должны быть одинаковой длины")
    
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    for i in range(len(moduli)):
        Mi = M // moduli[i]
        inv = modular_inverse(Mi, moduli[i])
        result += remainders[i] * Mi * inv
    
    return result % M


def check_congruence_consistency(remainders, moduli):
    """
    Проверяет совместность системы сравнений.
    Для каждого простого множителя проверяет, что все сравнения
    дают одинаковые остатки.
    """
    # Получаем все простые множители всех модулей
    all_primes = set()
    
    def get_prime_factors(n):
        factors = set()
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.add(d)
                n //= d
            d += 1
        if n > 1:
            factors.add(n)
        return factors
    
    for m in moduli:
        all_primes.update(get_prime_factors(m))
    
    # Для каждого простого числа проверяем совместность
    consistent = True
    conflicts = []
    
    for p in sorted(all_primes):
        # Собираем все условия для этого простого
        conditions = []
        for i, (r, m) in enumerate(zip(remainders, moduli)):
            if m % p == 0:
                # Вычисляем остаток по модулю p^k
                # Для простоты проверяем только по модулю p
                conditions.append((r % p, i))
        
        # Проверяем, что все остатки одинаковы
        if conditions:
            first_remainder, first_idx = conditions[0]
            for r, idx in conditions[1:]:
                if r != first_remainder:
                    consistent = False
                    conflicts.append(f"Противоречие по модулю {p}: "f"сравнение {idx + 1} даёт {r}, "f"сравнение {first_idx + 1} даёт {first_remainder}")
    
    return consistent, conflicts


def solve_system_with_general_crt(remainders, moduli):
    """
    Решает систему сравнений с необязательно взаимно простыми модулями.
    Использует метод последовательного решения.
    """
    # Сначала проверяем совместность
    consistent, conflicts = check_congruence_consistency(remainders, moduli)
    if not consistent:
        return None, conflicts
    
    # Метод последовательного решения
    x = remainders[0]
    m = moduli[0]
    
    for i in range(1, len(moduli)):
        # Решаем x ≡ remainders[i] (mod moduli[i])
        # То есть x + k*m ≡ remainders[i] (mod moduli[i])
        # k*m ≡ remainders[i] - x (mod moduli[i])
        
        a = m
        b = (remainders[i] - x) % moduli[i]
        mod = moduli[i]
        
        g = gcd(a, mod)
        if b % g != 0:
            return None, [f"Система несовместна на шаге {i + 1}: {x} ≡ {remainders[i]} (mod {mod})"]
        
        # Сокращаем
        a //= g
        b //= g
        mod //= g
        
        try:
            inv_a = modular_inverse(a % mod, mod)
            k = (b * inv_a) % mod
        except ValueError:
            return None, [f"Не удалось найти обратный элемент для {a} mod {mod}"]
        
        # Новое решение
        x = x + k * m
        m = lcm(m, moduli[i])
        x %= m
    
    return x % m, []


def analyze_system(remainders, moduli, description=""):
    """Анализирует и решает систему сравнений."""
    print(f"\n{'=' * 60}")
    print(f"Система: {description}")
    print(f"{'=' * 60}")
    
    print("Сравнения:")
    for i, (r, m) in enumerate(zip(remainders, moduli)):
        print(f"  {i + 1}. x ≡ {r} (mod {m})")
    
    # Проверяем на взаимную простоту
    print("\n1. Проверка попарной взаимной простоты модулей:")
    pairwise_coprime = True
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            g = gcd(moduli[i], moduli[j])
            if g != 1:
                print(f"   НОД({moduli[i]}, {moduli[j]}) = {g} ≠ 1")
                pairwise_coprime = False
    
    if pairwise_coprime:
        print("   ✓ Все модули попарно взаимно просты")
    else:
        print("   ✗ Не все модули попарно взаимно просты")
    
    # Проверяем совместность
    print("\n2. Проверка совместности:")
    consistent, conflicts = check_congruence_consistency(remainders, moduli)
    
    if not consistent:
        print("   ✗ Система НЕСОВМЕСТНА!")
        for conflict in conflicts:
            print(f"     • {conflict}")
        return None
    
    print("   ✓ Система совместна")
    
    # Решаем систему
    print("\n3. Решение системы:")
    solution, errors = solve_system_with_general_crt(remainders, moduli)
    
    if solution is None:
        print(f"   ✗ Ошибка при решении: {errors}")
        return None
    
    M = lcm_list(moduli)
    print(f"   x ≡ {solution} (mod {M})")
    
    # Проверка решения
    print("\n4. Проверка решения:")
    all_correct = True
    for i, (r, m) in enumerate(zip(remainders, moduli)):
        if solution % m == r:
            print(f"   ✓ {solution} mod {m} = {solution % m} (должно быть {r})")
        else:
            print(f"   ✗ {solution} mod {m} = {solution % m} (должно быть {r})")
            all_correct = False
    
    if all_correct:
        print("\n   ✓ Все проверки пройдены успешно!")
    
    return solution


def main():
    # Вариант A: с модулем 19
    remainders_A = [1, 3, 3, 4]
    moduli_A = [15, 17, 24, 19]
    
    analyze_system(remainders_A, moduli_A, "Вариант A: последний модуль 19")
    
    # Вариант B: с модулем 18 вместо 19
    remainders_B = [1, 3, 3, 4]
    moduli_B = [15, 17, 24, 18]
    
    analyze_system(remainders_B, moduli_B, "Вариант B: последний модуль 18")
    
    # Дополнительно: исправленная совместная система для демонстрации
    print("\n" + "=" * 60)
    print("Дополнительный пример: исправленная совместная система")
    print("=" * 60)
    
    # Исправленная система (убрали противоречия)
    remainders_fixed = [1, 3, 3, 4]
    moduli_fixed = [5, 17, 8, 9]  # Взаимно простые модули
    
    print("Оригинальные сравнения:")
    print("  x ≡ 1 (mod 5)   (из x ≡ 1 mod 15)")
    print("  x ≡ 3 (mod 17)")
    print("  x ≡ 3 (mod 8)   (из x ≡ 3 mod 24)")
    print("  x ≡ 4 (mod 9)   (из x ≡ 4 mod 18)")
    
    solution = analyze_system(remainders_fixed, moduli_fixed, "Исправленная система (взаимно простые модули)")


if __name__ == "__main__":
    main()


# ===================================================================================================================================================

# Задача 5. Сколько существует обратимых матриц порядка 2 х 2 над кольцом Zб? Над кольцом Z8?
import math
from functools import reduce


def prime_factors(n):
    """Разложение числа на простые множители с их степенями."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def gl2_order_over_zp(p, k = 1):
    """
    Вычисляет |GL(2, Z_{p^k})|.
    Формула: p^{4(k - 1)} * (p^2 - 1)(p^2 - p)
    """
    if k == 1:
        return (p ** 2 - 1) * (p ** 2 - p)
    else:
        return (p ** (4 * (k - 1))) * (p ** 2 - 1) * (p ** 2 - p)


def gl2_order_over_zm(m):
    """
    Вычисляет |GL(2, Z_m)| через китайскую теорему об остатках.
    """
    factors = prime_factors(m)
    
    total = 1
    for p, exp in factors.items():
        total *= gl2_order_over_zp(p, exp)
    
    return total


def count_invertible_matrices_mod_m(m, verbose = True):
    """
    Подсчитывает количество обратимых матриц 2x2 над Z_m.
    """
    result = gl2_order_over_zm(m)
    
    if verbose:
        print(f"m = {m}")
        factors = prime_factors(m)
        print(f"Разложение: {' * '.join([f'{p}^{exp}' for p, exp in factors.items()])}")
        
        for p, exp in factors.items():
            order_p = gl2_order_over_zp(p, exp)
            print(f"  |GL(2, Z_{p}^{exp})| = {order_p}")
        
        print(f"|GL(2, Z_{m})| = {result}")
        print()
    
    return result


def manual_count_check():
    """
    Дополнительная функция для прямого перебора (для маленьких m, чтобы проверить формулу).
    """
    from itertools import product
    
    def is_invertible_mod_m(a, b, c, d, m):
        det = (a*d - b*c) % m
        return math.gcd(det, m) == 1
    
    def brute_force_count(m):
        count = 0
        total = m**4
        for a, b, c, d in product(range(m), repeat = 4):
            if is_invertible_mod_m(a, b, c, d, m):
                count += 1
        return count
    
    print("\n" + "=" * 60)
    print("Проверка для маленьких m (прямой перебор):")
    print("=" * 60)
    for m in [2, 3, 4, 5]:
        formula = gl2_order_over_zm(m)
        brute = brute_force_count(m)
        print(f"m = {m}: формула = {formula}, перебор = {brute}, совпадение: {formula == brute}")


def main():
    print("=" * 60)
    print("Задача 5. Количество обратимых матриц 2×2 над кольцом Z_m")
    print("=" * 60)
    print()
    
    # Случай m = 6
    print("--- Случай 1: m = 6 ---")
    count_invertible_matrices_mod_m(6)
    
    # Случай m = 8
    print("--- Случай 2: m = 8 ---")
    count_invertible_matrices_mod_m(8)
    
    # Дополнительные примеры для иллюстрации
    print("--- Дополнительные примеры ---")
    for m in [2, 3, 4, 5, 7, 9, 10, 12]:
        count_invertible_matrices_mod_m(m, verbose = False)
        print(f"m = {m}: |GL(2, Z_{m})| = {gl2_order_over_zm(m)}")
    
    # Проверка для маленьких m прямым перебором
    manual_count_check()


if __name__ == "__main__":
    main()