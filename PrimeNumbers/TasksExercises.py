# Задачи и упражнения 
# Задача 1. =========================================================================================================================================
def is_prime(n: int) -> bool:
    """Базовая проверка на простоту (для небольших n)"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def check_condition(n: int) -> bool:
    """Проверяет, делит ли n (2 ^ n - 2)"""
    # Для больших n используем встроенную функцию pow с модулем
    return pow(2, n, n) == 2

def find_counterexamples(limit: int):
    """Ищет составные n <= limit, для которых n | (2 ^ n - 2)"""
    counterexamples = []
    for n in range(2, limit + 1):
        if not is_prime(n) and check_condition(n):
            counterexamples.append(n)
    return counterexamples

if __name__ == "__main__":
    N = 10000  # можно менять границу поиска
    print(f"Поиск составных n <= {N}, для которых n | (2 ^ n - 2):\n")
    examples = find_counterexamples(N)
    if examples:
        print("Найденные контрпримеры (псевдопростые по основанию 2):")
        for num in examples:
            print(f"{num} = {num} (составное), {num} | (2 ^ {num} - 2)")
    else:
        print("Контрпримеры не найдены в заданном диапазоне.")

# Задача 2. =========================================================================================================================================
# Пусть р - простое число. Доказать, что (р - 1)! = -1(modp). Этот результат известен как теорема Вильсона.
def wilson_theorem_check(n: int) -> bool:
    """
    Проверяет, выполняется ли (n - 1)! ≡ -1 mod n.
    Если n > 1 и условие верно, то n — простое (теорема Вильсона: необходимое и достаточное условие).
    """
    if n <= 1:
        return False
    
    # Вычисляем (n-1)! mod n с помощью цикла (для небольших n)
    factorial_mod = 1
    for i in range(2, n):  # от 2 до n-1
        factorial_mod = (factorial_mod * i) % n
    
    return factorial_mod == n - 1  # т.к. -1 mod n = n-1

def find_primes_via_wilson(limit: int):
    """Находит все простые числа до limit, используя теорему Вильсона (медленно, для демонстрации)."""
    primes = []
    for n in range(2, limit + 1):
        if wilson_theorem_check(n):
            primes.append(n)
    return primes

if __name__ == "__main__":
    # Пример 1: проверить одно число
    p = 7
    result = wilson_theorem_check(p)
    print(f"Для p = {p}: (p - 1)! ≡ -1 mod p? {result}")  # True

    # Пример 2: найти все простые до 20 с помощью Вильсона
    limit = 20
    primes = find_primes_via_wilson(limit)
    print(f"\nПростые числа до {limit} по теореме Вильсона: {primes}")

    # Пример 3: проверить составное число
    n = 9
    result2 = wilson_theorem_check(n)
    print(f"\nДля n = {n}: (n - 1)! ≡ -1 mod n? {result2}")  # False

# Задача 3. =========================================================================================================================================
# Пусть n - составное число, отличное от 4. Доказать, что (n - 1)! = 0(mod n).
import math

def check_wilson_composite(n: int) -> bool:
    """
    Проверяет, выполняется ли (n - 1)! ≡ 0 mod n для составного n ≠ 4.
    """
    if n <= 1:
        return False
    if n == 4:
        return False  # исключение
    if n % 2 == 0 and n > 2:
        # составное чётное число > 2, должно выполниться
        pass
    # основной расчет
    return math.factorial(n - 1) % n == 0

def demonstrate():
    print("Проверка утверждения: если n составное и n ≠ 4, то (n - 1)! ≡ 0 (mod n)\n")
    
    # Проверяем несколько чисел
    test_numbers = [4, 6, 8, 9, 10, 12, 14, 15, 16, 21, 25]
    
    for n in test_numbers:
        if n == 4:
            result = math.factorial(3) % 4
            print(f"n = {n}: (n - 1)! = 3! = 6, 6 mod {n} = {result} (исключение)")
        else:
            is_true = check_wilson_composite(n)
            remainder = math.factorial(n - 1) % n
            print(f"n = {n} (составное): (n - 1)! mod {n} = {remainder} → {'✅ верно' if is_true else '❌ неверно'}")

def find_counterexamples(limit: int):
    """Ищет составные n (кроме 4), для которых утверждение не выполняется (должно быть пусто)."""
    counterexamples = []
    for n in range(2, limit + 1):
        # Проверяем, что n составное
        if n == 4:
            continue
        # Упрощённая проверка на составное (не используем is_prime для чистоты)
        if n > 2 and n % 2 == 0:
            # чётное > 2 — составное
            if math.factorial(n - 1) % n != 0:
                counterexamples.append(n)
        else:
            # нечётное, проверим, составное ли оно
            composite = False
            for d in range(3, int(n ** 0.5) + 1, 2):
                if n % d == 0:
                    composite = True
                    break
            if composite:
                if math.factorial(n - 1) % n != 0:
                    counterexamples.append(n)
    return counterexamples

if __name__ == "__main__":
    demonstrate()
    
    print("\nПоиск возможных контрпримеров (должен быть пустой список):")
    bad_numbers = find_counterexamples(50)
    if not bad_numbers:
        print("✅ Контрпримеров не найдено (кроме n = 4, которое исключено условием).")
    else:
        print(f"❌ Найдены контрпримеры: {bad_numbers}")

# Задача 4. =========================================================================================================================================
import math

def is_prime(num: int) -> bool:
    """Проверка на простоту (для небольших чисел)."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            return False
    return True

def check_condition(a: int, n: int) -> bool:
    """
    Проверяет: если a ^ n - 1 простое, то a = 2 и n простое.
    Возвращает True, если утверждение выполняется для данной пары (a, n).
    """
    val = a ** n - 1
    if is_prime(val):
        return (a == 2) and is_prime(n)
    return True  # Если a^n - 1 не простое, условие задачи не применимо (считаем True)

def find_mersenne_primes(limit_n: int):
    """Находит простые числа Мерсенна 2 ^ n - 1 для простых n <= limit_n."""
    mersenne_primes = []
    for n in range(2, limit_n + 1):
        if is_prime(n):
            mersenne_candidate = 2 ** n - 1
            if is_prime(mersenne_candidate):
                mersenne_primes.append((n, mersenne_candidate))
    return mersenne_primes

def demonstrate_counterexamples(limit_a: int, limit_n: int):
    """Демонстрирует, что если a > 2 или n составное, то a ^ n - 1 составное."""
    print("Проверка составных a ^ n - 1 для a > 2 или составных n:\n")
    examples = []
    for a in range(2, limit_a + 1):
        for n in range(2, limit_n + 1):
            if a == 2 and is_prime(n):
                continue  # это числа Мерсенна, могут быть простыми
            val = a**n - 1
            if val < 2:
                continue
            if not is_prime(val):
                examples.append((a, n, val))
                if len(examples) >= 5:
                    break
        if len(examples) >= 5:
            break
    
    for a, n, val in examples:
        print(f"a = {a}, n = {n} -> {a} ^ {n} - 1 = {val} (составное)")

if __name__ == "__main__":
    # Проверка основного утверждения
    print("Проверка условия: если a^n - 1 простое, то a = 2 и n простое\n")
    test_cases = [(2, 2), (2, 3), (2, 5), (2, 7), (3, 2), (3, 3), (4, 2), (2, 4)]
    
    for a, n in test_cases:
        val = a**n - 1
        is_val_prime = is_prime(val)
        result = check_condition(a, n)
        print(f"a = {a}, n = {n}, a ^ n - 1 = {val} (простое? {is_val_prime}) -> Утверждение верно? {result}")
    
    # Числа Мерсенна
    print("\nПростые числа Мерсенна 2 ^ n - 1 для n <= 20:")
    mersenne_list = find_mersenne_primes(20)
    for n, m in mersenne_list:
        print(f"M_{n} = {m} (простое)")
    
    # Демонстрация контрпримеров (когда a > 2 или n составное)
    demonstrate_counterexamples(5, 6)

# Задача 5. =========================================================================================================================================
import math

def is_prime(num: int) -> bool:
    """Проверка числа на простоту."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0:
            return False
    return True

def is_power_of_two(x: int) -> bool:
    """Проверяет, является ли x степенью двойки (x > 0)."""
    return (x & (x - 1)) == 0 and x != 0

def check_fermat_condition(a: int, n: int) -> bool:
    """
    Проверяет: если a^n + 1 простое, то a чётное и n — степень 2.
    Возвращает True, если условие выполняется для данной пары.
    """
    val = a ** n + 1
    if is_prime(val):
        return (a % 2 == 0) and is_power_of_two(n)
    return True  # Если a^n + 1 не простое, условие не применимо

def find_fermat_primes(max_t: int):
    """Находит простые числа Ферма F_t = 2 ^ (2 ^ t) + 1 для t = 0..max_t."""
    fermat_primes = []
    for t in range(max_t + 1):
        exponent = 2 ** t
        f = 2 ** exponent + 1
        if is_prime(f):
            fermat_primes.append((t, f))
        else:
            # Для информации, например F_5
            if t == 5:
                print(f"F_5 = 2 ^ {2 ^ 5} + 1 = {f} — составное (известно)")
    return fermat_primes

def demonstrate_counterexamples(limit_a: int, limit_n: int):
    """Показывает, что если a нечётное или n не степень 2, то a ^ n + 1 составное."""
    print("\nКонтрпримеры (нарушение условий):")
    count = 0
    for a in range(2, limit_a + 1):
        for n in range(1, limit_n + 1):
            if a % 2 == 1 or not is_power_of_two(n):
                val = a**n + 1
                if not is_prime(val) and val > 2:
                    print(f"a = {a}, n = {n} -> {a} ^ {n} + 1 = {val} (составное)")
                    count += 1
                    if count >= 6:
                        return

if __name__ == "__main__":
    # Проверка условия
    print("Проверка условия: если a ^ n + 1 простое, то a чётное и n — степень 2\n")
    test_cases = [(2, 1), (2, 2), (2, 4), (4, 1), (2, 3), (3, 2), (4, 2), (6, 1), (2, 8)]

    for a, n in test_cases:
        val = a ** n + 1
        prime_flag = is_prime(val)
        result = check_fermat_condition(a, n)
        power_of_two_flag = is_power_of_two(n)
        print(f"a = {a}, n = {n} → {a} ^ {n} + 1 = {val} (простое? {prime_flag}), "f"n степень 2? {power_of_two_flag}, a чётное? {a % 2 == 0} → "f"Утверждение верно? {result}")

    # Простые числа Ферма
    print("\nПростые числа Ферма F_t = 2 ^ (2 ^ t) + 1 для t = 0..5:")
    fermat_list = find_fermat_primes(5)
    for t, f in fermat_list:
        # Правильно выводим 2^(2^t)
        exponent_of_exponent = 2 ** t
        print(f"F_{t} = 2 ^ {{{2 ** t}}} + 1 = {f} (простое)")

    # Демонстрация, что при нарушении условий число составное
    demonstrate_counterexamples(6, 5)