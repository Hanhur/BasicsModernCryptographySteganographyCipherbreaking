# Задачи и упражнения
# Задача 1. Объяснить, почему при установке ВВS-генератора требуется, чтобы простые числа р, q были сравнимы с 3(mod4).
import random
import sys

def is_prime(n, k = 10):
    """Проверка простоты числа n с помощью теста Миллера–Рабина"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Проверка k раз
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_blum_prime(bits):
    """Генерирует простое число p с условием p ≡ 3 (mod 4)"""
    while True:
        # Генерируем нечётное число заданной битовой длины
        p = random.getrandbits(bits)
        # Устанавливаем старший бит в 1 для гарантии длины
        p |= (1 << (bits - 1)) | 1
        # Проверяем условие p ≡ 3 mod 4
        if p % 4 != 3:
            p += (3 - p % 4)  # корректируем
        if is_prime(p):
            return p

def generate_bbs_parameters(bits):
    """Генерирует p и q с условием p ≡ q ≡ 3 (mod 4)"""
    p = generate_blum_prime(bits)
    q = generate_blum_prime(bits)
    while p == q:  # p и q должны быть различны
        q = generate_blum_prime(bits)
    return p, q

def find_seed(M):
    """Находит начальное значение x0, взаимно простое с M и являющееся квадратичным вычетом"""
    while True:
        r = random.randint(2, M - 1)
        # Проверяем, что r взаимно просто с M
        if pow(r, 1, M) == 0:
            continue
        # Возводим в квадрат, чтобы гарантированно получить квадратичный вычет
        x0 = pow(r, 2, M)
        if x0 == 0:
            continue
        return x0

class BBSGenerator:
    """Генератор псевдослучайных чисел BBS"""
    
    def __init__(self, p, q, seed = None):
        """
        Инициализация генератора.
        p, q - простые числа, сравнимые с 3 mod 4
        seed - начальное значение x0 (если None, выбирается случайно)
        """
        if p % 4 != 3 or q % 4 != 3:
            raise ValueError("p и q должны быть сравнимы с 3 по модулю 4")
        if not (is_prime(p) and is_prime(q)):
            raise ValueError("p и q должны быть простыми числами")
        if p == q:
            raise ValueError("p и q должны быть различны")
        
        self.p = p
        self.q = q
        self.M = p * q
        
        if seed is None:
            self.x = find_seed(self.M)
        else:
            if seed % self.M == 0 or pow(seed, 1, self.M) == 0:
                raise ValueError("seed должен быть взаимно прост с M")
            self.x = seed % self.M
    
    def next_bit(self):
        """Генерирует следующий случайный бит"""
        self.x = pow(self.x, 2, self.M)
        # Берём младший бит
        return self.x & 1
    
    def next_bits(self, n):
        """Генерирует n случайных битов"""
        bits = 0
        for i in range(n):
            bits |= (self.next_bit() << i)
        return bits
    
    def next_bytes(self, n_bytes):
        """Генерирует n байт случайных данных"""
        data = bytearray()
        for _ in range(n_bytes):
            byte_val = self.next_bits(8)
            data.append(byte_val)
        return bytes(data)
    
    def get_state(self):
        """Возвращает текущее состояние x"""
        return self.x
    
    def set_state(self, x):
        """Устанавливает состояние x"""
        self.x = x

def analyze_period(bbs, max_steps = 10000):
    """
    Анализирует период генератора BBS.
    Возвращает (период, предпериод)
    """
    states = {}  # состояние -> номер шага
    step = 0
    current_state = bbs.get_state()
    
    print(f"Начальное состояние: {current_state}")
    
    while step < max_steps:
        if current_state in states:
            # Нашли повторение
            preperiod = states[current_state]
            period = step - preperiod
            return period, preperiod
        
        states[current_state] = step
        bbs.next_bit()  # Генерируем следующий бит (обновляем состояние)
        current_state = bbs.get_state()
        step += 1
    
    return None, None  # Период не найден

def main():
    """Пример использования"""
    print("Генератор BBS (Blum–Blum–Shub)")
    print("=" * 40)
    
    # Для демонстрации используем маленькие числа, чтобы период был небольшим
    # Но p и q должны быть простыми и сравнимы с 3 mod 4
    
    # Вариант 1: используем предопределённые маленькие простые числа для гарантии работы
    print("\nВариант 1: Использование предопределённых маленьких простых чисел")
    print("-" * 60)
    
    # Маленькие простые числа, сравнимые с 3 mod 4: 3, 7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103...
    p_small = 19   # 19 % 4 = 3
    q_small = 23   # 23 % 4 = 3
    
    print(f"p = {p_small} (p % 4 = {p_small % 4})")
    print(f"q = {q_small} (q % 4 = {q_small % 4})")
    print(f"M = p * q = {p_small * q_small}")
    
    # Создаём генератор с фиксированным seed для воспроизводимости
    fixed_seed = 4  # 4 - квадратичный вычет по mod 19 и mod 23
    bbs1 = BBSGenerator(p_small, q_small, seed = fixed_seed)
    
    print(f"\nНачальное состояние x0 = {bbs1.get_state()}")
    
    # Генерируем 40 битов
    print("\nГенерация 40 случайных битов:")
    bits = []
    for i in range(40):
        bit = bbs1.next_bit()
        bits.append(str(bit))
        if (i + 1) % 8 == 0:
            print(''.join(bits[-8:]), end = " ")
    print("\n")
    
    # Анализ периода
    print("Анализ периода:")
    # Создаём новый генератор с тем же начальным состоянием
    bbs_analysis = BBSGenerator(p_small, q_small, seed = fixed_seed)
    period, preperiod = analyze_period(bbs_analysis, max_steps = 500)
    
    if period is not None:
        print(f"Найден период: {period} (предпериод: {preperiod})")
        theoretical_max = (p_small - 1) * (q_small - 1) // 4
        print(f"Теоретический максимальный период: {theoretical_max}")
    else:
        print("Период не найден в пределах заданного количества шагов")
    
    # Вариант 2: генерация случайных чисел (только для демонстрации)
    print("\n" + "=" * 40)
    print("Вариант 2: Генерация случайных параметров (для демонстрации)")
    print("-" * 60)
    
    bits = 16  # в реальности нужно брать > 512 бит
    print(f"Генерация простых чисел p и q длиной {bits} бит...")
    
    try:
        p, q = generate_bbs_parameters(bits)
        print(f"p = {p} (p % 4 = {p % 4})")
        print(f"q = {q} (q % 4 = {q % 4})")
        print(f"M = p * q = {p * q}")
        
        bbs2 = BBSGenerator(p, q)
        
        print("\nГенерация 40 случайных битов:")
        bits_output = []
        for i in range(40):
            bit = bbs2.next_bit()
            bits_output.append(str(bit))
            if (i + 1) % 8 == 0:
                print(''.join(bits_output[-8:]), end = " ")
        print("\n")
        
        print("Генерация 16 случайных байтов (в HEX):")
        random_bytes = bbs2.next_bytes(16)
        print(random_bytes.hex())
        
    except Exception as e:
        print(f"Ошибка при генерации: {e}")
        print("Попробуйте уменьшить битовую длину или используйте предопределённые значения")

if __name__ == "__main__":
    main()

# Задача 2. Вывести формулу для общего члена последовательности, порождаемой ЛКГ xt+1 = axt + b(modn).
import math
from typing import Tuple, Optional

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y) такие что a * x + b * y = gcd"""
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x

def mod_inverse(a: int, n: int) -> Optional[int]:
    """
    Возвращает обратный элемент к a по модулю n.
    Возвращает None, если обратный не существует.
    """
    g, x, _ = egcd(a, n)
    if g != 1:
        return None
    else:
        return x % n

def solve_linear_congruence(a: int, b: int, n: int) -> Optional[int]:
    """
    Решает сравнение a * x ≡ b (mod n)
    Возвращает решение x или None, если решения нет
    """
    g = math.gcd(a, n)
    if b % g != 0:
        return None
    a1, b1, n1 = a // g, b // g, n // g
    inv = mod_inverse(a1, n1)
    if inv is None:
        return None
    return (inv * b1) % n1

class LCG:
    """
    Линейный конгруэнтный генератор (ЛКГ)
    X_{t + 1} = a * X_t + b (mod n)
    
    Также поддерживает вывод общего члена последовательности:
    X_t = a ^ t * X0 + b * (a ^ t - 1) / (a - 1)  (mod n)
    """
    
    def __init__(self, a: int, b: int, n: int, seed: int):
        """
        Инициализация ЛКГ
        
        Параметры:
        a, b, n - параметры генератора
        seed - начальное значение X0
        """
        self.a = a % n
        self.b = b % n
        self.n = n
        self.seed = seed % n
        self.current = seed % n
        
        # Проверяем, существует ли обратный к (a-1)
        self.has_inverse = (math.gcd(self.a - 1, self.n) == 1)
        if self.has_inverse and self.a != 1:
            self.inv_a_minus_1 = mod_inverse(self.a - 1, self.n)
        else:
            self.inv_a_minus_1 = None
            
        # Для случая a = 1
        if self.a == 1:
            self.has_inverse = True  # особая формула
    
    def next(self) -> int:
        """Генерирует следующее значение последовательности"""
        self.current = (self.a * self.current + self.b) % self.n
        return self.current
    
    def generate(self, count: int) -> list:
        """Генерирует count значений последовательности"""
        result = []
        for _ in range(count):
            result.append(self.next())
        return result
    
    def get_nth_term_formula(self, t: int) -> int:
        """
        Вычисляет X_t по явной формуле:
        X_t = a ^ t * X0 + b * (a ^ t - 1) / (a - 1)  (mod n)
        
        Используется только когда gcd(a - 1, n) = 1 или a = 1
        """
        if t == 0:
            return self.seed % self.n
        
        if self.a == 1:
            # X_t = X0 + t*b (mod n)
            return (self.seed + t * self.b) % self.n
        
        if not self.has_inverse:
            raise ValueError(
                f"Нельзя применить формулу: gcd(a - 1, n) = {math.gcd(self.a - 1, self.n)} != 1.\n"
                f"Используйте итеративный метод или разложение по модулям."
            )
        
        # Вычисляем a^t mod n
        a_pow_t = pow(self.a, t, self.n)
        
        # Вычисляем b*(a^t - 1)/(a-1) mod n
        # Сначала (a^t - 1) mod n
        numerator = (a_pow_t - 1) % self.n
        
        # Умножаем на b и на обратный к (a-1)
        term = (self.b * numerator) % self.n
        term = (term * self.inv_a_minus_1) % self.n
        
        # Итоговый результат
        result = (a_pow_t * self.seed + term) % self.n
        return result
    
    def get_nth_term_iterative(self, t: int) -> int:
        """Вычисляет X_t итеративно (для сравнения)"""
        val = self.seed
        for _ in range(t):
            val = (self.a * val + self.b) % self.n
        return val
    
    def verify_formula(self, t_max: int = 10) -> bool:
        """Проверяет формулу для всех t от 0 до t_max"""
        print(f"\nПроверка формулы для a = {self.a}, b = {self.b}, n = {self.n}, X0 = {self.seed}")
        print("-" * 60)
        
        if self.a == 1:
            print("Случай a = 1: X_t = X0 + t * b (mod n)")
        elif self.has_inverse:
            print("Случай a ≠ 1, gcd(a - 1, n) = 1")
            print("Формула: X_t = a ^ t * X0 + b * (a ^ t - 1) / (a - 1) (mod n)")
        else:
            print("ВНИМАНИЕ: gcd(a - 1, n) ≠ 1. Формула может не работать!")
            print(f"gcd({self.a - 1}, {self.n}) = {math.gcd(self.a - 1, self.n)}")
            return False
        
        print(f"\n{'t':<4} {'По формуле':<15} {'Итеративно':<15} {'Совпадает':<10}")
        print("-" * 60)
        
        all_match = True
        for t in range(t_max + 1):
            try:
                formula_val = self.get_nth_term_formula(t)
            except ValueError as e:
                print(f"{t:<4} {'Ошибка':<15} {'-':<15} {'Нет':<10}")
                print(f"  Причина: {e}")
                return False
            
            iter_val = self.get_nth_term_iterative(t)
            match = formula_val == iter_val
            all_match = all_match and match
            
            print(f"{t:<4} {formula_val:<15} {iter_val:<15} {'✓' if match else '✗':<10}")
        
        return all_match
    
    def find_period(self, max_steps: int = 10000) -> int:
        """Находит период последовательности"""
        seen = {}
        val = self.seed
        step = 0
        
        while step < max_steps:
            if val in seen:
                return step - seen[val]
            seen[val] = step
            val = (self.a * val + self.b) % self.n
            step += 1
        
        return -1  # Период не найден
    
    def reset(self):
        """Сбрасывает генератор к начальному состоянию"""
        self.current = self.seed
    
    def __repr__(self) -> str:
        return f"LCG: X_{{t + 1}} = {self.a} * X_t + {self.b} mod {self.n}, X0 = {self.seed}"

def demonstrate_lcg_formula():
    """Демонстрация работы ЛКГ и явной формулы"""
    
    print("=" * 70)
    print("ЛИНЕЙНЫЙ КОНГРУЭНТНЫЙ ГЕНЕРАТОР (ЛКГ)")
    print("Формула общего члена: X_t = a ^ t * X0 + b * (a ^ t - 1) / (a - 1) (mod n)")
    print("=" * 70)
    
    # Пример 1: a ≠ 1, gcd(a-1, n) = 1
    print("\n" + "=" * 70)
    print("ПРИМЕР 1: a ≠ 1, gcd(a - 1, n) = 1 (формула работает)")
    print("-" * 70)
    
    lcg1 = LCG(a = 3, b = 2, n = 11, seed = 1)
    print(lcg1)
    print(f"gcd(a - 1, n) = gcd(2, 11) = {math.gcd(2, 11)}")
    
    # Проверяем формулу
    lcg1.verify_formula(t_max = 10)
    
    # Генерируем последовательность
    print(f"\nПервые 15 значений последовательности (итеративно):")
    lcg1.reset()
    values = lcg1.generate(15)
    print("X_t =", values)
    
    # Находим период
    period = lcg1.find_period()
    print(f"\nПериод последовательности: {period}")
    
    # Пример 2: a = 1 (арифметическая прогрессия)
    print("\n" + "=" * 70)
    print("ПРИМЕР 2: a = 1 (арифметическая прогрессия по модулю n)")
    print("-" * 70)
    
    lcg2 = LCG(a = 1, b = 7, n = 20, seed = 3)
    print(lcg2)
    print("Формула: X_t = X0 + t * b (mod n)")
    lcg2.verify_formula(t_max = 10)
    
    print(f"\nПервые 15 значений:")
    lcg2.reset()
    values = lcg2.generate(15)
    print("X_t =", values)
    
    # Пример 3: a ≠ 1, но gcd(a-1, n) ≠ 1
    print("\n" + "=" * 70)
    print("ПРИМЕР 3: a ≠ 1, НО gcd(a - 1, n) ≠ 1 (формула НЕ работает)")
    print("-" * 70)
    
    lcg3 = LCG(a = 3, b = 2, n = 10, seed = 1)
    print(lcg3)
    print(f"gcd(a - 1, n) = gcd(2, 10) = {math.gcd(2, 10)}")
    print("\nПопытка применить формулу:")
    try:
        lcg3.verify_formula(t_max = 10)
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\nНо итеративный метод работает:")
    lcg3.reset()
    values = lcg3.generate(15)
    print("X_t =", values)
    
    # Пример 4: Реальный пример из криптографии (n - степень двойки)
    print("\n" + "=" * 70)
    print("ПРИМЕР 4: ЛКГ с n = 2 ^ 31 (типичный для генераторов случайных чисел)")
    print("-" * 70)
    
    # Параметры из известного генератора glibc
    n_large = 2 ** 31
    a_large = 1103515245
    b_large = 12345
    seed_large = 1
    
    lcg4 = LCG(a = a_large, b = b_large, n = n_large, seed = seed_large)
    print(lcg4)
    print(f"gcd(a - 1, n) = gcd({a_large - 1}, {n_large}) = {math.gcd(a_large - 1, n_large)}")
    
    if math.gcd(a_large-1, n_large) == 1:
        print("Формула работает!")
        print(f"\nX_100 по формуле: {lcg4.get_nth_term_formula(100)}")
        print(f"X_100 итеративно: {lcg4.get_nth_term_iterative(100)}")
    
    # Пример 5: Демонстрация формулы с большими степенями
    print("\n" + "=" * 70)
    print("ПРИМЕР 5: Вычисление X_t для больших t без итераций")
    print("-" * 70)
    
    lcg5 = LCG(a = 5, b = 3, n = 1009, seed = 42)  # 1009 - простое число
    print(lcg5)
    print(f"gcd(a - 1, n) = gcd(4, 1009) = {math.gcd(4, 1009)}")
    
    t_large = 10 ** 6  # миллион шагов
    print(f"\nВычисление X_{t_large} по формуле (мгновенно):")
    result_formula = lcg5.get_nth_term_formula(t_large)
    print(f"X_{t_large} = {result_formula}")
    
    print(f"\nВычисление X_{t_large} итеративно (займёт время):")
    print("(итеративный метод опущен для экономии времени)")
    
    # Пример 6: Случай с большим n и обратимым a-1
    print("\n" + "=" * 70)
    print("ПРИМЕР 6: Простое n, формула работает отлично")
    print("-" * 70)
    
    lcg6 = LCG(a = 7, b = 5, n = 97, seed = 13)  # 97 - простое число
    print(lcg6)
    print(f"gcd(a - 1, n) = gcd(6, 97) = {math.gcd(6, 97)}")
    lcg6.verify_formula(t_max = 8)
    
    # Демонстрация преимущества формулы
    print("\n" + "=" * 70)
    print("ПРЕИМУЩЕСТВО ФОРМУЛЫ: быстрое вычисление для больших t")
    print("-" * 70)
    
    lcg7 = LCG(a = 2, b = 1, n = 10 ** 9 + 7, seed = 12345)  # Большое простое число
    print(lcg7)
    
    t_huge = 10 ** 9  # миллиард шагов
    print(f"\nВычисление X_{t_huge} по формуле (мгновенно):")
    result = lcg7.get_nth_term_formula(t_huge)
    print(f"X_{t_huge} = {result}")
    print("\nИтеративный метод потребовал бы миллиард итераций!")

def interactive_lcg():
    """Интерактивный режим для работы с ЛКГ"""
    print("\n" + "=" * 70)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 70)
    
    try:
        a = int(input("Введите a: "))
        b = int(input("Введите b: "))
        n = int(input("Введите n (модуль): "))
        seed = int(input("Введите X0 (начальное значение): "))
        t = int(input("Введите t (номер члена последовательности): "))
        
        lcg = LCG(a, b, n, seed)
        print(f"\n{lcg}")
        
        g = math.gcd(a - 1, n)
        print(f"gcd(a - 1, n) = {g}")
        
        if g == 1:
            result = lcg.get_nth_term_formula(t)
            print(f"\nX_{t} по формуле: {result}")
            print(f"X_{t} итеративно: {lcg.get_nth_term_iterative(t)}")
        elif a == 1:
            result = lcg.get_nth_term_formula(t)
            print(f"\nX_{t} по формуле (арифм. прогрессия): {result}")
        else:
            print("\nФормула не применима (нет обратного к a - 1)")
            print(f"Используйте итеративный метод:")
            result = lcg.get_nth_term_iterative(t)
            print(f"X_{t} = {result}")
            
    except ValueError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nПрервано пользователем")

if __name__ == "__main__":
    # Запуск демонстрации
    demonstrate_lcg_formula()
    
    # Интерактивный режим (раскомментируйте для использования)
    # interactive_lcg()

# Задача 3. Выяснить, когда ЛКГ из предыдущей задачи порождает последовательность максимального периода.
import math
from typing import Tuple, List

def factorize(n: int) -> List[int]:
    """Разложение на простые множители (для небольших n)"""
    factors = []
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            factors.append(p)
            while temp % p == 0:
                temp //= p
        p += 1 if p == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors

def check_max_period_conditions(a: int, b: int, n: int) -> Tuple[bool, str]:
    """
    Проверяет условия максимального периода для ЛКГ:
    X_{t + 1} = a * X_t + b mod n
    
    Возвращает (выполняется_ли, пояснение)
    """
    a = a % n
    b = b % n
    
    # Условие 1: gcd(b, n) = 1
    g = math.gcd(b, n)
    if g != 1:
        return False, f"Условие 1 нарушено: gcd(b, n) = {g} != 1"
    
    # Получаем простые делители n
    prime_factors = factorize(n)
    
    # Условие 2: a ≡ 1 (mod p) для каждого простого p|n
    for p in prime_factors:
        if a % p != 1:
            return False, f"Условие 2 нарушено: для p={p} имеем a mod {p} = {a % p} != 1"
    
    # Условие 3: если 4|n, то a ≡ 1 (mod 4)
    if n % 4 == 0:
        if a % 4 != 1:
            return False, f"Условие 3 нарушено: 4|n, но a mod 4 = {a % 4} != 1"
    
    return True, "Все условия выполнены, период = n"

def find_actual_period(a: int, b: int, n: int, seed: int = 0, max_steps: int = 100000):
    """Находит фактический период ЛКГ (для проверки)"""
    seen = {}
    x = seed % n
    step = 0
    
    while step < max_steps:
        if x in seen:
            period = step - seen[x]
            return period
        seen[x] = step
        x = (a * x + b) % n
        step += 1
    
    return -1  # Не найден

def demonstrate_max_period():
    """Демонстрация условий максимального периода"""
    
    print("=" * 70)
    print("УСЛОВИЯ МАКСИМАЛЬНОГО ПЕРИОДА ЛКГ")
    print("Теорема: период = n тогда и только тогда, когда:")
    print("1. gcd(b, n) = 1")
    print("2. Для каждого простого p|n: a ≡ 1 (mod p)")
    print("3. Если 4|n, то a ≡ 1 (mod 4)")
    print("=" * 70)
    
    examples = [
        # n, a, b, seed, ожидаемый период
        (16, 5, 3, 0, 16, "✅ Правильные параметры"),
        (16, 5, 2, 0, 8,  "❌ b чётное (gcd = 2)"),
        (16, 3, 3, 0, 8,  "❌ a mod 4 = 3"),
        (16, 1, 3, 0, 16, "✅ a = 1 подходит"),
        (9, 4, 2, 0, 9,   "✅ a ≡ 1 mod 3, gcd(b, 9) = 1"),
        (9, 4, 3, 0, 3,   "❌ b кратно 3"),
        (10, 1, 3, 0, 10,  "✅ a = 1, b = 3 взаимно просто"),
        (10, 3, 3, 0, 10,  "⚠️ a ≠ 1 mod 5? a = 3 mod 5 ≠ 1 → период < 10"),
        (15, 1, 2, 0, 15,  "✅ a = 1, gcd(2, 15) = 1"),
        (15, 4, 2, 0, 15,  "❌ a ≡ 4 mod 3 = 1, a ≡ 4 mod 5 = 4 ≠ 1"),
        (8, 5, 3, 0, 8,    "✅ a = 5 ≡ 1 mod 4, b = 3 нечётно"),
        (8, 5, 1, 0, 8,    "✅ a = 5 ≡ 1 mod 4, b = 1 нечётно"),
        (12, 1, 5, 0, 12,  "✅ a = 1, gcd(5, 12) = 1"),
        (12, 7, 5, 0, 6,   "❌ a = 7 mod 3 = 1, но a = 7 mod 2 = 1? 12 = 2² * 3, p = 2 требует a ≡ 1 mod 2 (да), p = 3 требует a ≡ 1 mod 3 (7 mod 3 = 1) — ок, но a ≡ 1 mod 4? нет, 12 делится на 4? 12 / 4 = 3 → делится! a mod 4 = 3 ≠ 1 → период < 12"),
    ]
    
    for n, a, b, seed, expected_period, comment in examples:
        print(f"\n{'─' * 70}")
        print(f"n = {n}, a = {a}, b = {b}, seed = {seed}")
        print(f"Ожидаемый период: {expected_period}")
        print(comment)
        
        # Проверяем условия
        condition_ok, message = check_max_period_conditions(a, b, n)
        print(f"Условия: {message}")
        
        # Вычисляем фактический период
        actual_period = find_actual_period(a, b, n, seed)
        print(f"Фактический период: {actual_period}")
        
        if actual_period == n:
            print("✅ ПЕРИОД МАКСИМАЛЬНЫЙ")
        else:
            print("❌ ПЕРИОД НЕ МАКСИМАЛЬНЫЙ")
    
    # Особый случай: большая степень двойки
    print("\n" + "=" * 70)
    print("ПРИМЕР: n = 2 ^ k (широко используется на практике)")
    print("=" * 70)
    
    k = 10
    n_pow2 = 2 ** k
    a_good = 1  # a=1 всегда даёт период n
    a_glibc = 1103515245 % n_pow2  # параметр из glibc, но mod 2^10
    a_bad = 3
    b_odd = 12345 % n_pow2
    b_even = 2
    
    print(f"\nДля n = 2 ^ {k} = {n_pow2}")
    
    # Хороший a
    condition_ok, msg = check_max_period_conditions(a_good, b_odd, n_pow2)
    print(f"a = {a_good}, b = {b_odd}: {msg}")
    print(f"Фактический период: {find_actual_period(a_good, b_odd, n_pow2)}")
    
    # a ≡ 1 mod 4, но a != 1
    # Найдём a ≡ 1 mod 4, но не 1
    a_4k1 = 5
    condition_ok, msg = check_max_period_conditions(a_4k1, b_odd, n_pow2)
    print(f"\na = {a_4k1}, b = {b_odd}: {msg}")
    print(f"Фактический период: {find_actual_period(a_4k1, b_odd, n_pow2)}")
    
    # Плохой a
    condition_ok, msg = check_max_period_conditions(a_bad, b_odd, n_pow2)
    print(f"\na = {a_bad}, b = {b_odd}: {msg}")
    print(f"Фактический период: {find_actual_period(a_bad, b_odd, n_pow2)}")
    
    # Чётное b
    condition_ok, msg = check_max_period_conditions(a_good, b_even, n_pow2)
    print(f"\na = {a_good}, b = {b_even}: {msg}")
    print(f"Фактический период: {find_actual_period(a_good, b_even, n_pow2)}")

if __name__ == "__main__":
    demonstrate_max_period()

# Задача 4. Пусть задан МКГ Xt+1 = axt(modn). 
# Предположим, что нод(х0 , n) = 1. Каково возможное максимальное значение периода выпускной последовательности?
import math
from functools import reduce

def carmichael_lambda(n: int) -> int:
    """Вычисляет функцию Кармайкла λ(n)"""
    if n == 1:
        return 1
    
    # Факторизация n
    factors = {}
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            cnt = 0
            while temp % p == 0:
                temp //= p
                cnt += 1
            factors[p] = cnt
        p += 1 if p == 2 else 2
    if temp > 1:
        factors[temp] = 1
    
    # Вычисляем λ(p^k) для каждого простого
    lambdas = []
    for p, k in factors.items():
        if p == 2:
            if k == 1:
                lambdas.append(1)
            elif k == 2:
                lambdas.append(2)
            else:
                lambdas.append(2 ** (k - 2))
        else:
            lambdas.append(p ** (k - 1) * (p - 1))
    
    # НОК всех λ(p^k)
    def lcm(a, b):
        return a * b // math.gcd(a, b)
    
    return reduce(lcm, lambdas)

def multiplicative_order(a: int, n: int, max_order: int = None) -> int:
    """Находит порядок a в группе Z_n ^ *"""
    if math.gcd(a, n) != 1:
        return -1
    
    if max_order is None:
        max_order = carmichael_lambda(n)
    
    order = 1
    current = a % n
    while order <= max_order:
        if current == 1:
            return order
        current = (current * a) % n
        order += 1
    return -1

def find_max_period_mkg(n: int, a: int = None, x0: int = 1) -> dict:
    """Анализирует МКГ X_{t + 1} = a * X_t mod n с gcd(x0, n) = 1"""
    
    if math.gcd(x0, n) != 1:
        return {"error": "gcd(x0, n) != 1"}
    
    if a is None:
        # Ищем a с максимальным порядком
        max_period = 0
        best_a = None
        for candidate in range(1, n):
            if math.gcd(candidate, n) == 1:
                period = multiplicative_order(candidate, n)
                if period > max_period:
                    max_period = period
                    best_a = candidate
        a = best_a
        period = max_period
    else:
        if math.gcd(a, n) != 1:
            return {"error": "gcd(a, n) != 1"}
        period = multiplicative_order(a, n)
    
    theoretical_max = carmichael_lambda(n)
    
    return {
        "n": n,
        "a": a,
        "x0": x0,
        "period": period,
        "max_possible_period": theoretical_max,
        "is_max": period == theoretical_max
    }

def demonstrate():
    """Демонстрация"""
    print("=" * 70)
    print("МАКСИМАЛЬНЫЙ ПЕРИОД МУЛЬТИПЛИКАТИВНОГО КОНГРУЭНТНОГО ГЕНЕРАТОРА")
    print("X_{t + 1} = a * X_t mod n,  gcd(X0, n) = 1")
    print("=" * 70)
    
    examples = [7, 8, 9, 15, 16, 21, 25, 32, 49]
    
    for n in examples:
        print(f"\n--- n = {n} ---")
        print(f"φ({n}) = {math.phi(n) if hasattr(math, 'phi') else '?'}")
        print(f"λ({n}) = {carmichael_lambda(n)}")
        
        result = find_max_period_mkg(n)
        print(f"Максимальный период: {result['max_possible_period']}")
        print(f"Достигается при a = {result['a']} (период = {result['period']})")
        
        # Проверка на примере
        print(f"\nПроверка при a = {result['a']}, X0 = 1:")
        x = 1
        sequence = [x]
        for _ in range(result['period']):
            x = (result['a'] * x) % n
            sequence.append(x)
        print(f"Первые {min(20, len(sequence))} значений: {sequence[:20]}")
        print(f"Последовательность зациклилась через {result['period']} шагов")

if __name__ == "__main__":
    demonstrate()