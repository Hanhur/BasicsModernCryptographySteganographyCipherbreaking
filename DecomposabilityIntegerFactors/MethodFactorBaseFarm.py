# 2. Метод фактор-баз Ферма
import math
import random
from collections import defaultdict

def is_prime(n):
    """Простая проверка на простоту (для небольших чисел)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def generate_primes(limit):
    """Генерирует список простых чисел до limit (решето Эратосфена)."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_p in enumerate(sieve) if is_p]

def least_absolute_residue(a, n):
    """
    Наименьший абсолютный вычет числа a по модулю n.
    Возвращает число из интервала [-(n - 1) / 2, (n - 1) / 2] для нечётного n.
    """
    r = a % n
    if r > n // 2:
        r -= n
    return r

def factor_over_base(num, base_primes):
    """
    Разлагает число num на простые из factor_base.
    Возвращает:
        None - если num не является B-числом
        dict - словарь {простое: показатель степени}
        sign - 1 или -1 (знак числа)
    """
    if num == 0:
        return None
    
    sign = 1 if num > 0 else -1
    n = abs(num)
    
    factors = defaultdict(int)
    temp = n
    
    for p in base_primes:
        if p * p > temp:
            break
        while temp % p == 0:
            factors[p] += 1
            temp //= p
    
    # Если осталось число больше 1, оно должно быть простым и входить в базу
    if temp > 1:
        if temp in base_primes:
            factors[temp] += 1
        else:
            return None  # Не B-число
    
    return {"sign": sign, "factors": dict(factors)}

def vector_mod2(factor_dict, prime_index_map):
    """
    Преобразует словарь разложения в вектор над F2.
    """
    size = len(prime_index_map)
    vec = [0] * (size + 1)  # +1 для знака
    
    # Первая компонента - знак (0 для +, 1 для -)
    vec[0] = 0 if factor_dict["sign"] == 1 else 1
    
    for p, exp in factor_dict["factors"].items():
        if p in prime_index_map:
            vec[1 + prime_index_map[p]] = exp % 2
    return vec

def find_dependent_set(vectors):
    """
    Находит линейно зависимый набор векторов над F2.
    Возвращает индексы векторов, образующих зависимость.
    Использует метод Гаусса.
    """
    if not vectors:
        return None
    
    n = len(vectors[0])  # размерность пространства
    m = len(vectors)     # количество векторов
    
    # Копируем векторы
    rows = [vec[:] for vec in vectors]
    row_index = list(range(m))  # исходные индексы
    
    row = 0
    for col in range(n):
        # Находим строку с единицей в текущем столбце, начиная с row
        pivot = -1
        for r in range(row, m):
            if rows[r][col] == 1:
                pivot = r
                break
        
        if pivot == -1:
            continue
        
        # Меняем местами
        rows[row], rows[pivot] = rows[pivot], rows[row]
        row_index[row], row_index[pivot] = row_index[pivot], row_index[row]
        
        # Обнуляем остальные строки в этом столбце
        for r in range(m):
            if r != row and rows[r][col] == 1:
                for c in range(n):
                    rows[r][c] ^= rows[row][c]
        row += 1
    
    # Ищем нулевую строку (зависимость)
    for r in range(m):
        if all(x == 0 for x in rows[r]):
            # Возвращаем индексы всех векторов, которые использовались
            # для получения этой нулевой строки (упрощённо: сам вектор)
            return [row_index[r]]
    
    # Если нулевой строки нет, ищем любую зависимость
    # Для простоты: если векторов больше, чем размерность, берём первые n+1
    if m > n:
        return list(range(n + 1))
    
    return None

def dickson_factorization(n, B_size = 10, max_attempts = 1000):
    """
    Метод фактор-баз (алгоритм Диксона) для факторизации n.
    
    Параметры:
        n - составное нечётное число
        B_size - примерный размер фактор-базы (количество простых)
        max_attempts - максимальное количество попыток поиска B-квадратов
    
    Возвращает:
        (d1, d2) - нетривиальные делители n (или (1, n) при неудаче)
    """
    if n % 2 == 0:
        return (2, n // 2)
    
    # Генерация фактор-базы
    prime_limit = 50  # начальный порог
    primes = generate_primes(prime_limit)
    factor_base = [-1] + primes[:B_size]
    base_primes = primes[:B_size]
    
    print(f"Фактор-база: {factor_base}")
    print(f"Простые числа: {base_primes}")
    
    prime_index = {p: i for i, p in enumerate(base_primes)}
    
    b_values = []      # значения b_i
    b_vectors = []     # их векторы
    b_squares = []     # b_i^2
    
    start = int(math.isqrt(n))
    
    # Поиск B-квадратов
    attempt = 0
    i = 1
    while len(b_values) < B_size + 5 and attempt < max_attempts:
        b = start + i
        b_sq = b * b
        r = least_absolute_residue(b_sq, n)
        
        if r == 0:
            # Нашли точный квадрат
            d = math.gcd(b, n)
            if 1 < d < n:
                return (d, n // d)
            i += 1
            continue
        
        # Проверяем, является ли r B-числом
        factorization = factor_over_base(r, base_primes)
        if factorization is not None:
            vec = vector_mod2(factorization, prime_index)
            b_values.append(b)
            b_vectors.append(vec)
            b_squares.append(b_sq)
            print(f"Найден B-квадрат: b = {b}, b ^ 2 mod n = {r}, разложение = {factorization}")
        
        i += 1
        attempt += 1
    
    if len(b_values) < 2:
        print("Не найдено достаточно B-квадратов. Попробуйте увеличить B_size.")
        return (1, n)
    
    print(f"\nНайдено {len(b_values)} B-квадратов")
    
    # Поиск четного поднабора
    dependent = find_dependent_set(b_vectors)
    
    if dependent is None:
        print("Не найдена линейная зависимость")
        return (1, n)
    
    print(f"Найдена зависимость: индексы {dependent}")
    
    # Вычисляем t и s
    t_squared = 1
    s_squared = 1
    
    for idx in dependent:
        t_squared = (t_squared * b_values[idx]) % n
        r = least_absolute_residue(b_squares[idx], n)
        s_squared = (s_squared * r) % n
    
    t = t_squared  # t^2 mod n
    s = int(math.isqrt(s_squared))
    while s * s < s_squared:
        s += 1
    while s * s > s_squared:
        s -= 1
    
    if s * s != s_squared:
        # s_squared может быть не точным квадратом из-за знака
        # Нужно скорректировать
        s_squared_abs = abs(s_squared)
        s = int(math.isqrt(s_squared_abs))
        if s * s != s_squared_abs:
            print("Ошибка: произведение не является квадратом")
            return (1, n)
    
    print(f"t ^ 2 mod n = {t}, s ^ 2 = {s} ^ 2 = {s * s}")
    
    # Проверяем сравнение
    if (t * t) % n != (s * s) % n:
        print("Ошибка: сравнение не выполняется")
        return (1, n)
    
    # Вычисляем делители
    d1 = math.gcd(t + s, n)
    d2 = math.gcd(t - s, n)
    
    print(f"gcd(t + s, n) = {d1}")
    print(f"gcd(t - s, n) = {d2}")
    
    if d1 != 1 and d1 != n:
        return (d1, n // d1)
    if d2 != 1 and d2 != n:
        return (d2, n // d2)
    
    # Если не удалось, пробуем другой зависимый набор
    # (упрощённо: пробуем взять другой набор индексов)
    for start_idx in range(1, len(b_vectors) - len(dependent) + 1):
        alt_indices = list(range(start_idx, start_idx + len(dependent)))
        if set(alt_indices) == set(dependent):
            continue
        
        t_squared = 1
        s_squared = 1
        for idx in alt_indices:
            t_squared = (t_squared * b_values[idx]) % n
            r = least_absolute_residue(b_squares[idx], n)
            s_squared = (s_squared * r) % n
        
        t = t_squared
        s = int(math.isqrt(abs(s_squared)))
        d1 = math.gcd(t + s, n)
        d2 = math.gcd(t - s, n)
        
        if d1 != 1 and d1 != n:
            return (d1, n // d1)
        if d2 != 1 and d2 != n:
            return (d2, n // d2)
    
    return (1, n)


def main():
    """Тестирование программы на примерах из текста."""
    
    # Пример 49
    print("=" * 60)
    print("Пример 49: n = 23299")
    print("=" * 60)
    n1 = 23299
    d1, d2 = dickson_factorization(n1, B_size = 6, max_attempts = 50)
    print(f"\nРезультат: {n1} = {d1} × {d2}\n")
    
    # Пример 50
    print("=" * 60)
    print("Пример 50: n = 1829")
    print("=" * 60)
    n2 = 1829
    d1, d2 = dickson_factorization(n2, B_size = 9, max_attempts = 50)
    print(f"\nРезультат: {n2} = {d1} × {d2}\n")
    
    # Дополнительный тест
    print("=" * 60)
    print("Дополнительный тест: n = 143")
    print("=" * 60)
    n3 = 143
    d1, d2 = dickson_factorization(n3, B_size = 4, max_attempts = 30)
    print(f"\nРезультат: {n3} = {d1} × {d2}")


if __name__ == "__main__":
    main()