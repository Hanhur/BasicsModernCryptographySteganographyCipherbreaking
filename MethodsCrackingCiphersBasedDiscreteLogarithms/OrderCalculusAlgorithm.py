# Алгоритм исчисления порядка
import random
import math
from collections import defaultdict

def factorize_smooth(n, primes):
    """
    Разлагает число n на множители из множества primes.
    Если n p_t-гладкое, возвращает словарь {prime: exponent}.
    Иначе возвращает None.
    """
    factors = defaultdict(int)
    temp = n
    
    for p in primes:
        while temp % p == 0:
            factors[p] += 1
            temp //= p
    
    # Если после деления на все простые из базиса осталось что-то кроме 1,
    # значит число не является гладким относительно данного базиса
    if temp != 1:
        return None
    
    return dict(factors)

def extended_gcd(a, b):
    """Расширенный алгоритм Евклида для нахождения обратного элемента."""
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    return gcd, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """Находит обратный элемент a по модулю m."""
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    return x % m

def solve_linear_system(equations, mod):
    """
    Решает систему линейных уравнений методом Гаусса по модулю mod.
    equations: список уравнений, каждое уравнение - список [k, c1, c2, ..., ct]
    где k - правая часть, c_i - коэффициенты при неизвестных.
    Возвращает список значений неизвестных или None, если решение не единственное.
    """
    if not equations:
        return None
    
    t = len(equations[0]) - 1  # количество неизвестных
    matrix = []
    
    for eq in equations:
        row = eq.copy()
        # Приводим все коэффициенты по модулю mod
        row = [coef % mod for coef in row]
        matrix.append(row)
    
    # Прямой ход метода Гаусса
    row = 0
    col = 0
    where = [-1] * t
    
    while row < len(matrix) and col < t:
        # Ищем строку с ненулевым элементом в колонке col
        sel = row
        while sel < len(matrix) and matrix[sel][col] == 0:
            sel += 1
        
        if sel == len(matrix):
            col += 1
            continue
        
        # Меняем строки местами
        matrix[row], matrix[sel] = matrix[sel], matrix[row]
        where[col] = row
        
        # Находим обратный элемент для ведущего
        inv = mod_inverse(matrix[row][col], mod)
        
        # Нормализуем строку
        for j in range(col, t + 1):
            matrix[row][j] = (matrix[row][j] * inv) % mod
        
        # Вычитаем из остальных строк
        for i in range(len(matrix)):
            if i != row and matrix[i][col] != 0:
                factor = matrix[i][col]
                for j in range(col, t + 1):
                    matrix[i][j] = (matrix[i][j] - factor * matrix[row][j]) % mod
        
        row += 1
        col += 1
    
    # Проверяем наличие решения
    for i in range(len(matrix)):
        all_zero = all(matrix[i][j] == 0 for j in range(t))
        if all_zero and matrix[i][t] != 0:
            return None  # Система несовместна
    
    # Проверяем единственность решения
    if any(w == -1 for w in where):
        return None  # Бесконечно много решений
    
    # Формируем решение
    solution = [0] * t
    for col in range(t):
        if where[col] != -1:
            solution[col] = matrix[where[col]][t]
    
    return solution

def index_calculus(a, y, p, t = None, epsilon = 2, max_attempts = 10000):
    """
    Реализация алгоритма исчисления порядка для вычисления дискретного логарифма.
    
    Параметры:
    a - основание
    y - число, логарифм которого ищем
    p - модуль (простое число)
    t - количество простых чисел в базисе (если None, вычисляется автоматически)
    epsilon - дополнительное количество уравнений для компенсации зависимостей
    max_attempts - максимальное количество попыток
    
    Возвращает:
    x = log_a(y) mod (p - 1)
    """
    
    print(f"Решаем уравнение: {y} = {a} ^ x mod {p}")
    print("-" * 60)
    
    # Шаг 1: Формируем множество базовых множителей
    if t is None:
        # Для маленьких p используем простые числа до 20
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        t = 0
        for prime in small_primes:
            if prime < p and t < 8:  # Ограничиваем для простоты
                t += 1
            else:
                break
    
    # Находим первые t простых чисел
    primes = []
    num = 2
    while len(primes) < t:
        is_prime = True
        for d in range(2, int(math.sqrt(num)) + 1):
            if num % d == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
        num += 1
    
    print(f"Шаг 1: Базис S = {primes}")
    
    # Шаг 2: Поиск гладких чисел
    print(f"\nШаг 2: Поиск {t + epsilon} гладких чисел...")
    smooth_powers = []
    k = 1
    attempts = 0
    
    while len(smooth_powers) < t + epsilon and attempts < max_attempts:
        value = pow(a, k, p)
        factors = factorize_smooth(value, primes)
        
        if factors is not None:
            # Записываем уравнение: k = sum(c_i * log_a(p_i))
            equation = [k % (p - 1)]
            for prime in primes:
                equation.append(factors.get(prime, 0) % (p - 1))
            smooth_powers.append(equation)
            print(f"  Найдено: {a} ^ {k} mod {p} = {value} = {' * '.join([f'{prime} ^ {exp}' for prime, exp in factors.items()])}")
        
        k += 1
        attempts += 1
    
    if len(smooth_powers) < t + epsilon:
        raise ValueError(f"Не удалось найти достаточно гладких чисел за {max_attempts} попыток")
    
    # Шаг 3: Решение системы уравнений
    print(f"\nШаг 3: Решение системы из {len(smooth_powers)} уравнений...")
    print("  Система уравнений:")
    for i, eq in enumerate(smooth_powers, 1):
        k_val = eq[0]
        coeffs = eq[1:]
        eq_str = f"    {k_val} = " + " + ".join([f"{coeff} * u {i + 1}" for i, coeff in enumerate(coeffs) if coeff != 0])
        print(eq_str)
    
    solution = solve_linear_system(smooth_powers, p - 1)
    
    if solution is None:
        raise ValueError("Система не имеет единственного решения. Попробуйте увеличить epsilon.")
    
    log_primes = {}
    for i, prime in enumerate(primes):
        log_primes[prime] = solution[i]
    
    print(f"\n  Найдены логарифмы чисел из S:")
    for prime, log_val in log_primes.items():
        print(f"    log_{a}({prime}) = {log_val}")
        # Проверка
        check = pow(a, log_val, p)
        print(f"      Проверка: {a} ^ {log_val} mod {p} = {check} {'✓' if check == prime else '✗'}")
    
    # Шаг 4: Поиск гладкого представления для y
    print(f"\nШаг 4: Поиск r такого, что y * a ^ r mod p является гладким...")
    
    for r in range(1, p):
        value = (y * pow(a, r, p)) % p
        factors = factorize_smooth(value, primes)
        
        if factors is not None:
            print(f"  Найдено: {y} * {a} ^ {r} mod {p} = {value}")
            print(f"    = {' * '.join([f'{prime} ^ {exp}' for prime, exp in factors.items()])}")
            
            # Шаг 5: Вычисление логарифма
            print(f"\nШаг 5: Вычисление конечного результата")
            sum_logs = 0
            log_parts = []
            for prime, exp in factors.items():
                if prime in log_primes:
                    sum_logs = (sum_logs + exp * log_primes[prime]) % (p - 1)
                    log_parts.append(f"{exp} * log_{a}({prime})")
            
            x = (sum_logs - r) % (p - 1)
            
            print(f"  log_{a}({y}) = ({' + '.join(log_parts)} - {r}) mod {p - 1}")
            print(f"    = {sum_logs} - {r} mod {p - 1}")
            print(f"    = {x}")
            
            # Проверка результата
            check = pow(a, x, p)
            print(f"\n  Проверка: {a} ^ {x} mod {p} = {check}")
            if check == y:
                print(f"  ✓ Решение найдено верно!")
            else:
                print(f"  ✗ Ошибка в вычислениях!")
            
            return x
    
    raise ValueError(f"Не удалось найти гладкое представление для {y}")

def main():
    """Пример использования алгоритма."""
    
    # Пример из текста: 37 = 10^x mod 47
    print("=" * 70)
    print("ПРИМЕР 1: Из учебника")
    print("=" * 70)
    
    try:
        x = index_calculus(a = 10, y = 37, p = 47, t = 3, epsilon = 1)
        print(f"\nОтвет: x = {x}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "=" * 70)
    print("ПРИМЕР 2: Другой пример")
    print("=" * 70)
    
    # Другой пример: 5 = 3^x mod 17
    # Проверим, что 3^? mod 17 = 5
    # 3^1=3, 3^2=9, 3^3=27=10, 3^4=30=13, 3^5=39=5 ✓
    try:
        x = index_calculus(a = 3, y = 5, p = 17, t = 3, epsilon = 1)
        print(f"\nОтвет: x = {x}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "=" * 70)
    print("ПРИМЕР 3: Случайный пример")
    print("=" * 70)
    
    # Генерируем случайный пример
    p = 101
    a = 2
    # Находим первообразный корень для простоты
    # Используем 2 как основание (для 101 это первообразный корень)
    x_true = random.randint(1, p - 2)
    y = pow(a, x_true, p)
    
    print(f"Сгенерирован пример: {y} = {a} ^ x mod {p}, где x = {x_true}")
    print()
    
    try:
        x_found = index_calculus(a = a, y = y, p = p, t = 5, epsilon = 2)
        print(f"\nНайденный x = {x_found}, истинный x = {x_true}")
        if x_found == x_true:
            print("✓ Решение совпадает!")
        else:
            print("✗ Решение не совпадает!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()