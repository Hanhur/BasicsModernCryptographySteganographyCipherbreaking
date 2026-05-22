# # 2. Кольца вычетов
# import math

# class ResidueRing:
#     """Класс для работы с кольцом вычетов Zn"""
    
#     def __init__(self, n):
#         """Инициализация кольца Zn"""
#         if n < 2:
#             raise ValueError("Модуль n должен быть >= 2")
#         self.n = n
    
#     def add(self, a, b):
#         """Сложение вычетов: (a + b) mod n"""
#         return (a + b) % self.n
    
#     def mul(self, a, b):
#         """Умножение вычетов: (a * b) mod n"""
#         return (a * b) % self.n
    
#     def is_equal(self, a, b):
#         """Проверка сравнения a ≡ b (mod n)"""
#         return (a - b) % self.n == 0
    
#     def is_zero_divisor(self, a):
#         """Проверка, является ли элемент делителем нуля"""
#         if a % self.n == 0:
#             return False
#         for b in range(1, self.n):
#             if b % self.n != 0 and self.mul(a, b) == 0:
#                 return True
#         return False
    
#     def is_invertible(self, a):
#         """Проверка, обратим ли элемент a в Zn"""
#         a = a % self.n
#         return math.gcd(a, self.n) == 1 and a != 0
    
#     def extended_gcd(self, a, b):
#         """
#         Расширенный алгоритм Евклида
#         Возвращает (d, x, y): d = gcd(a, b) = a * x + b * y
#         """
#         if b == 0:
#             return a, 1, 0
#         d, x1, y1 = self.extended_gcd(b, a % b)
#         x = y1
#         y = x1 - (a // b) * y1
#         return d, x, y
    
#     def inverse(self, a):
#         """Находит обратный элемент для a в Zn"""
#         a = a % self.n
#         if not self.is_invertible(a):
#             raise ValueError(f"Элемент {a} не обратим в Z{self.n}")
        
#         d, x, _ = self.extended_gcd(a, self.n)
#         if d != 1:
#             raise ValueError(f"НОД({a}, {self.n}) = {d} ≠ 1")
        
#         # Приводим x к стандартному имени (0..n-1)
#         return x % self.n
    
#     def find_all_invertible(self):
#         """Находит все обратимые вычеты в Zn"""
#         return [i for i in range(1, self.n) if self.is_invertible(i)]
    
#     def euler_phi(self):
#         """Вычисляет функцию Эйлера φ(n)"""
#         count = 0
#         for i in range(1, self.n):
#             if math.gcd(i, self.n) == 1:
#                 count += 1
#         return count
    
#     def solve_x2_eq_1(self):
#         """Находит все решения уравнения x² ≡ 1 (mod n)"""
#         solutions = []
#         for x in range(self.n):
#             if (x * x) % self.n == 1:
#                 solutions.append(x)
#         return solutions


# def main():
#     """Демонстрация работы с кольцами вычетов"""
    
#     print("=" * 60)
#     print("Кольца вычетов Zn - демонстрация")
#     print("=" * 60)
    
#     # Пример 1: операции в кольце
#     print("\n1. Операции в кольце вычетов:")
#     print("-" * 40)
    
#     rings = [(8, 5, 7), (24, 13, 11), (5, 2, 8), (26, 4, 21), (18, 3, 6)]
    
#     for n, a, b in rings:
#         ring = ResidueRing(n)
#         print(f"В Z{n}: {a} + {b} = {ring.add(a, b)} (mod {n})")
#         print(f"В Z{n}: {a} · {b} = {ring.mul(a, b)} (mod {n})")
#         print()
    
#     # Пример 2: сравнения по модулю
#     print("\n2. Сравнения по модулю:")
#     print("-" * 40)
#     ring10 = ResidueRing(10)
#     print(f"5 ≡ 25 (mod 10)? {ring10.is_equal(5, 25)} (верно, т.к. 25-5=20 делится на 10)")
    
#     # Пример 3: делители нуля
#     print("\n3. Делители нуля:")
#     print("-" * 40)
#     ring18 = ResidueRing(18)
#     for a in [3, 6, 9, 2]:
#         is_zero_div = ring18.is_zero_divisor(a)
#         if is_zero_div:
#             print(f"{a} - делитель нуля в Z18")
#             # Найдем b, такой что a*b ≡ 0
#             for b in range(1, 18):
#                 if ring18.mul(a, b) == 0 and b != 0:
#                     print(f"   Действительно, {a} · {b} = {ring18.mul(a, b)} (mod 18)")
#                     break
    
#     # Пример 4: обратимые элементы
#     print("\n4. Обратимые элементы:")
#     print("-" * 40)
    
#     # Проверка обратимости
#     ring125 = ResidueRing(125)
#     a = 17
#     inv = ring125.inverse(a)
#     print(f"В Z125: 17⁻¹ = {inv} (mod 125)")
#     print(f"Проверка: 17 · {inv} = {ring125.mul(17, inv)} (mod 125)")
    
#     # Все обратимые mod 15
#     ring15 = ResidueRing(15)
#     inv_elements = ring15.find_all_invertible()
#     print(f"\nВ Z15 обратимые вычеты: {inv_elements}")
#     print(f"Количество: φ(15) = {ring15.euler_phi()}")
    
#     # Находим пары обратных
#     print("Пары обратных элементов в Z15:")
#     for a in inv_elements:
#         inv_a = ring15.inverse(a)
#         if a <= inv_a:  # чтобы не дублировать
#             print(f"  {a} · {inv_a} = {ring15.mul(a, inv_a)} (mod 15)")
    
#     # Пример 5: решение x² ≡ 1 (mod n)
#     print("\n5. Решения уравнения x² ≡ 1 (mod n):")
#     print("-" * 40)
    
#     ring15_solutions = ring15.solve_x2_eq_1()
#     print(f"В Z15: x² ≡ 1 (mod 15) имеет решения: {ring15_solutions}")
#     print(f"Всего решений: {len(ring15_solutions)}")
    
#     # Пример 6: функция Эйлера
#     print("\n6. Функция Эйлера φ(n):")
#     print("-" * 40)
    
#     test_values = [2, 3, 4, 5, 6, 7, 10, 15, 20]
#     for n in test_values:
#         ring = ResidueRing(n)
#         phi = ring.euler_phi()
#         # Проверка для простых чисел
#         if all(n % i != 0 for i in range(2, int(n ** 0.5) + 1)) and n > 1:
#             print(f"φ({n}) = {phi} (для простого числа: {n} - 1 = {n - 1})")
#         else:
#             print(f"φ({n}) = {phi}")
    
#     # Пример 7: для RSA - n = p·q
#     print("\n7. Для RSA (произведение двух простых чисел):")
#     print("-" * 40)
    
#     p, q = 7, 13  # простые числа
#     n = p * q
#     ring_rsa = ResidueRing(n)
#     phi_n = ring_rsa.euler_phi()
#     print(f"n = {p} · {q} = {n}")
#     print(f"φ({n}) = {phi_n}")
#     print(f"Проверка формулы: (p - 1)(q - 1) = {p - 1} · {q - 1} = {(p - 1) * (q - 1)}")
#     print(f"Совпадает: {phi_n == (p - 1) * (q - 1)}")
    
#     # Пример 8: демонстрация расширенного алгоритма Евклида
#     print("\n8. Расширенный алгоритм Евклида:")
#     print("-" * 40)
    
#     ring_test = ResidueRing(125)
#     d, x, y = ring_test.extended_gcd(17, 125)
#     print(f"НОД(17, 125) = {d}")
#     print(f"17·({x}) + 125·({y}) = {17 * x + 125 * y}")
#     print(f"17·({x}) ≡ 1 (mod 125) → 17⁻¹ = {x % 125}")


# if __name__ == "__main__":
#     main()

# ===================================================================================================================================================

"""
Программа для работы с кольцами вычетов Zn
Реализует все основные понятия из теории колец вычетов:
- операции сложения и умножения по модулю
- делители нуля
- обратимые элементы
- расширенный алгоритм Евклида
- функция Эйлера
- решение уравнения x^2 ≡ 1 (mod n)
"""

def gcd(a, b):
    """Нахождение наибольшего общего делителя (алгоритм Евклида)"""
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида
    Возвращает (d, x, y): d = gcd(a, b) = a * x + b * y
    """
    if b == 0:
        return a, 1, 0
    
    d, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return d, x, y

class ResidueRing:
    """
    Класс, представляющий кольцо вычетов Zn
    Zn = {0, 1, 2, ..., n-1} с операциями по модулю n
    """
    
    def __init__(self, n):
        """Создание кольца Zn"""
        if n < 2:
            raise ValueError("Модуль n должен быть больше 1")
        self.n = n
        self.name = f"Z{n}"
    
    def add(self, a, b):
        """
        Сложение в кольце Zn
        Вычисляем a+b в Z, затем берем остаток от деления на n
        """
        return (a + b) % self.n
    
    def multiply(self, a, b):
        """
        Умножение в кольце Zn
        Вычисляем a*b в Z, затем берем остаток от деления на n
        """
        return (a * b) % self.n
    
    def is_congruent(self, a, b):
        """
        Проверка сравнения a ≡ b (mod n)
        a ≡ b (mod n) если (a-b) делится на n
        """
        return (a - b) % self.n == 0
    
    def is_zero_divisor(self, a):
        """
        Проверка, является ли элемент a делителем нуля
        Делитель нуля: a ≠ 0, b ≠ 0, но a*b ≡ 0 (mod n)
        """
        a = a % self.n
        if a == 0:
            return False
        
        for b in range(1, self.n):
            if self.multiply(a, b) == 0:
                return True
        return False
    
    def find_zero_divisors(self):
        """Находит все делители нуля в кольце"""
        zero_divisors = []
        for a in range(1, self.n):
            if self.is_zero_divisor(a):
                zero_divisors.append(a)
        return zero_divisors
    
    def is_invertible(self, a):
        """
        Проверка, обратим ли элемент a в Zn
        Элемент обратим тогда и только тогда, когда gcd(a, n) = 1
        (Предложение 2 из текста)
        """
        a = a % self.n
        if a == 0:
            return False
        return gcd(a, self.n) == 1
    
    def inverse(self, a):
        """
        Нахождение обратного элемента a^(-1) в Zn
        Использует расширенный алгоритм Евклида
        """
        a = a % self.n
        
        if not self.is_invertible(a):
            raise ValueError(f"Элемент {a} не обратим в {self.name}")
        
        d, x, y = extended_gcd(a, self.n)
        
        # d должно быть равно 1, так как a обратим
        if d != 1:
            raise ValueError(f"НОД({a}, {self.n}) = {d} ≠ 1")
        
        # Приводим x к стандартному имени (от 0 до n-1)
        return x % self.n
    
    def find_all_invertible(self):
        """Находит все обратимые элементы в Zn"""
        return [i for i in range(1, self.n) if self.is_invertible(i)]
    
    def euler_phi(self):
        """
        Функция Эйлера φ(n)
        Количество чисел от 1 до n-1, взаимно простых с n
        Это количество обратимых элементов в Zn
        """
        count = 0
        for i in range(1, self.n):
            if gcd(i, self.n) == 1:
                count += 1
        return count
    
    def solve_x2_equals_1(self):
        """
        Решает уравнение x² ≡ 1 (mod n)
        Возвращает список всех решений
        """
        solutions = []
        for x in range(self.n):
            if (x * x) % self.n == 1:
                solutions.append(x)
        return solutions
    
    def get_standard_name(self, a):
        """
        Приводит вычет к стандартному имени (0, 1, ..., n-1)
        """
        return a % self.n


def demo_ring(ring):
    """Демонстрация работы с кольцом вычетов"""
    n = ring.n
    print(f"\n{'='*60}")
    print(f"Кольцо вычетов {ring.name}")
    print(f"{'='*60}")
    
    # 1. Базовые операции
    print("\n1. Операции сложения и умножения:")
    print("-" * 40)
    examples = [(5, 7), (13, 11), (2, 8), (4, 21), (3, 6)]
    for a, b in examples[:3]:  # показываем несколько примеров
        if a < n and b < n:
            print(f"  {a} + {b} = {ring.add(a, b)} (mod {n})")
            print(f"  {a} · {b} = {ring.multiply(a, b)} (mod {n})")
    
    # 2. Делители нуля
    print("\n2. Делители нуля:")
    print("-" * 40)
    zero_divisors = ring.find_zero_divisors()
    if zero_divisors:
        print(f"  Делители нуля в {ring.name}: {zero_divisors}")
        # Показываем пример
        for a in zero_divisors[:2]:
            for b in range(1, n):
                if ring.multiply(a, b) == 0 and b != 0:
                    print(f"  Пример: {a} · {b} = 0 (mod {n})")
                    break
    else:
        print(f"  В {ring.name} нет делителей нуля → это область целостности")
    
    # 3. Обратимые элементы
    print("\n3. Обратимые элементы:")
    print("-" * 40)
    invertible = ring.find_all_invertible()
    phi = ring.euler_phi()
    print(f"  Обратимые элементы: {invertible}")
    print(f"  Количество: φ({n}) = {phi}")
    
    # Показываем пары обратных элементов
    if len(invertible) <= 10:  # только для небольших колец
        print("  Пары взаимно обратных элементов:")
        processed = set()
        for a in invertible:
            if a not in processed:
                inv = ring.inverse(a)
                print(f"    {a} · {inv} = {ring.multiply(a, inv)} (mod {n})")
                processed.add(a)
                processed.add(inv)
    
    # 4. Решение x² ≡ 1 (mod n)
    print("\n4. Решение уравнения x² ≡ 1 (mod n):")
    print("-" * 40)
    solutions = ring.solve_x2_equals_1()
    print(f"  Решения: {solutions}")
    print(f"  Количество решений: {len(solutions)}")
    for x in solutions:
        print(f"    {x}² = {x * x} ≡ {(x * x) % n} (mod {n})")


def main():
    """Основная функция программы"""
    print("="*60)
    print("ПРОГРАММА ДЛЯ РАБОТЫ С КОЛЬЦАМИ ВЫЧЕТОВ Zn")
    print("="*60)
    
    # Демонстрируем различные кольца
    rings = [ResidueRing(8), ResidueRing(15), ResidueRing(5), ResidueRing(125)]
    
    for ring in rings:
        demo_ring(ring)
    
    # Специальная демонстрация для RSA (n = p*q)
    print("\n" + "=" * 60)
    print("ПРИМЕР ДЛЯ RSA: n = p·q")
    print("=" * 60)
    
    p, q = 7, 13
    n = p * q
    ring_rsa = ResidueRing(n)
    
    print(f"\nПусть p = {p}, q = {q}")
    print(f"Тогда n = {p}·{q} = {n}")
    print(f"φ({n}) = ({p}-1)·({q}-1) = {p - 1}·{q - 1} = {(p - 1) * (q - 1)}")
    print(f"Проверка через алгоритм: φ({n}) = {ring_rsa.euler_phi()}")
    
    # Демонстрация расширенного алгоритма Евклида на примере из текста
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Нахождение 17⁻¹ (mod 125)")
    print("=" * 60)
    
    ring125 = ResidueRing(125)
    a = 17
    inv = ring125.inverse(a)
    
    print(f"\nВычисляем {a}⁻¹ в Z125:")
    print(f"Шаги расширенного алгоритма Евклида:")
    print("  125 = 17·7 + 6")
    print("  17 = 6·2 + 5")
    print("  6 = 5·1 + 1")
    print("  5 = 1·5 + 0")
    print("\n  Обратный ход:")
    print("  1 = 6 - 5·1")
    print("  1 = 6 - (17 - 6·2)·1 = 6·3 - 17·1")
    print("  1 = (125 - 17·7)·3 - 17·1 = 125·3 - 17·22")
    print(f"\nРезультат: 17·(-22) ≡ 1 (mod 125)")
    print(f"Стандартное имя вычета (-22): {inv}")
    print(f"Проверка: 17·{inv} = {17 * inv} ≡ {ring125.multiply(17, inv)} (mod 125)")
    
    # Демонстрация для простых чисел (поле)
    print("\n" + "=" * 60)
    print("ПРОСТЫЕ МОДУЛИ (ПОЛЯ)")
    print("=" * 60)
    
    for p in [2, 3, 5, 7, 11]:
        if all(p % i != 0 for i in range(2, int(p ** 0.5) + 1)):
            ring_p = ResidueRing(p)
            print(f"\nZ{p}:")
            print(f"  φ({p}) = {ring_p.euler_phi()} = {p} - 1")
            print(f"  Все ненулевые элементы обратимы: {ring_p.find_all_invertible()}")
            print(f"  Делители нуля: {ring_p.find_zero_divisors()} (нет) → это ПОЛЕ")


if __name__ == "__main__":
    main()