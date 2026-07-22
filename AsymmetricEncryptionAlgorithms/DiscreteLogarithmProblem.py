# Задача дискретного логарифма
# дискретный_логарифм.py
# Чистый Python, библиотеки не используются (только math для проверки простоты)

import math
import time

# =============================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================

def is_prime(n: int) -> bool:
    """Проверка, является ли число простым (для маленьких чисел)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Проверяем до квадратного корня
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def factorize(n: int) -> list:
    """Разложение числа на простые множители (для проверки образующего)."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2  # после 2 проверяем только нечетные
    if n > 1:
        factors.append(n)
    return factors

def is_primitive_root(g: int, p: int) -> bool:
    """
    Проверяет, является ли g образующим элементом (примитивным корнем) по модулю p.
    Условие: для всех простых делителей q числа (p - 1), g ^ ((p - 1) / q) != 1 (mod p)
    """
    if not is_prime(p):
        return False
    if g % p == 0:
        return False
    
    phi = p - 1
    prime_factors = list(set(factorize(phi)))  # уникальные простые делители
    
    for q in prime_factors:
        if pow(g, phi // q, p) == 1:
            return False
    return True

# =============================================
# 2. ОСНОВНЫЕ ФУНКЦИИ (ЗАДАЧА ДИСКРЕТНОГО ЛОГАРИФМА)
# =============================================

def discrete_log_bruteforce(g: int, b: int, p: int, max_steps: int = None) -> int:
    """
    Вычисляет дискретный логарифм x: g ^ x ≡ b (mod p)
    методом полного перебора (грубая сила).
    
    Возвращает наименьшее неотрицательное x.
    Если max_steps задан, ищем только в этом диапазоне (для демонстрации).
    """
    if max_steps is None:
        max_steps = p - 1  # максимум, так как порядок делит (p-1)
    
    for x in range(max_steps + 1):
        if pow(g, x, p) == b:
            return x
    return -1  # не найдено

def generate_powers_sequence(g: int, p: int, length: int = None) -> list:
    """
    Генерирует последовательность степеней g ^ x mod p для наглядности.
    Показывает, как числа "скачут" хаотично.
    """
    if length is None:
        length = p - 1
    sequence = []
    for x in range(length):
        sequence.append(pow(g, x, p))
    return sequence

def find_all_solutions_sample(g: int, b: int, p: int, num_examples: int = 3) -> list:
    """
    Показывает, что решений бесконечно много (периодичность).
    Возвращает несколько решений: x, x + (p - 1), x + 2(p - 1), ...
    """
    # Сначала находим первое (наименьшее) решение
    first_x = discrete_log_bruteforce(g, b, p)
    if first_x == -1:
        return []
    
    solutions = []
    period = p - 1
    for n in range(num_examples):
        solutions.append(first_x + n * period)
    return solutions

# =============================================
# 3. ДЕМОНСТРАЦИОННЫЙ КЛАСС (для красивой печати)
# =============================================

class DiscreteLogDemo:
    """Класс для демонстрации всех свойств задачи дискретного логарифма."""
    
    def __init__(self, p: int, g: int):
        if not is_prime(p):
            raise ValueError(f"{p} не является простым числом!")
        
        self.p = p
        self.g = g
        self.is_g_primitive = is_primitive_root(g, p)
        
    def print_properties(self):
        """Выводит основные свойства поля."""
        print("=" * 60)
        print(f"РАБОТА В КОНЕЧНОМ ПОЛЕ Z_{self.p}")
        print("=" * 60)
        print(f"Образующий элемент g = {self.g}")
        
        if self.is_g_primitive:
            print(f"✅ g = {self.g} ЯВЛЯЕТСЯ образующим (примитивным корнем) для Z_{self.p}")
            print(f"   Он порождает ВСЕ числа от 1 до {self.p - 1}")
        else:
            print(f"❌ g = {self.g} НЕ ЯВЛЯЕТСЯ образующим для Z_{self.p}")
            print("   Он порождает только подгруппу меньшего размера")
        
        print(f"Порядок группы (количество элементов): {self.p - 1}")
        print("=" * 60)
    
    def demo_powers(self, num_terms: int = None):
        """Показывает последовательность степеней, чтобы продемонстрировать хаотичность."""
        if num_terms is None:
            num_terms = min(self.p - 1, 30)  # показываем не более 30 членов
        
        seq = generate_powers_sequence(self.g, self.p, num_terms)
        
        print(f"\nПОСЛЕДОВАТЕЛЬНОСТЬ СТЕПЕНЕЙ g ^ {{x}} mod {self.p}:")
        print("-" * 60)
        for i, val in enumerate(seq):
            # Форматируем вывод: показываем только первые 20 и последние 10, если их много
            if i < 20 or i >= len(seq) - 10:
                print(f"  x = {i:2d}  →  {self.g} ^ {i:2d} mod {self.p} = {val:3d}")
            elif i == 20:
                print("  ... (пропущено) ...")
        print("-" * 60)
        print("Обратите внимание: числа НЕ возрастают, они скачут хаотично!")
        print("Именно поэтому обычный логарифм здесь не работает.\n")
    
    def demo_discrete_log(self, b: int):
        """Показывает решение задачи дискретного логарифма."""
        print(f"\nЗАДАЧА ДИСКРЕТНОГО ЛОГАРИФМА:")
        print(f"  Найти x такое, что {self.g} ^ {{x}} ≡ {b} (mod {self.p})")
        print("-" * 60)
        
        start_time = time.time()
        x = discrete_log_bruteforce(self.g, b, self.p)
        elapsed = time.time() - start_time
        
        if x == -1:
            print(f"❌ Решение не найдено (число {b} не принадлежит подгруппе, порожденной {self.g})")
        else:
            print(f"✅ Найдено решение: x = {x}")
            print(f"   Проверка: {self.g} ^ {x} = {pow(self.g, x, self.p)} ≡ {b} (mod {self.p})")
            print(f"   Время поиска (перебором): {elapsed * 1000:.3f} мс")
            
            # Показываем, что решений бесконечно много
            more_solutions = find_all_solutions_sample(self.g, b, self.p, num_examples = 4)
            print(f"\n   ⚠️  ВАЖНО: Это НЕ единственное решение!")
            print(f"   В силу периодичности, все числа вида x + n·({self.p} - 1) тоже подходят:")
            for sol in more_solutions:
                print(f"      x = {sol}  →  {self.g} ^ {sol} mod {self.p} = {pow(self.g, sol, self.p)}")
            print(f"   То есть решений БЕСКОНЕЧНО много (n = 0, 1, 2, ...)")
    
    def demo_inverse_problem(self, b: int):
        """Показывает обратную операцию: возведение в степень."""
        print(f"\nПРЯМАЯ ОПЕРАЦИЯ (возведение в степень):")
        print(f"  Дано: x = ? , {self.g} ^ {{x}} ≡ {b} (mod {self.p})")
        
        x = discrete_log_bruteforce(self.g, b, self.p)
        if x != -1:
            print(f"  Найден дискретный логарифм: x = {x}")
            print(f"  Проверка прямой операцией: {self.g} ^ {x} = {pow(self.g, x, self.p)}")
        else:
            print(f"  Число {b} не достижимо из {self.g}")


# =============================================
# 4. ПРИМЕРЫ ИЗ ВАШЕГО ТЕКСТА + ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ
# =============================================

def run_demo_from_text():
    """Запускает демонстрацию на примерах из вашего текста."""
    
    print("\n" + "=" * 60)
    print("  ДЕМОНСТРАЦИЯ ЗАДАЧИ ДИСКРЕТНОГО ЛОГАРИФМА")
    print("  На основе объяснения из книги")
    print("=" * 60 + "\n")
    
    # ---- Пример 1: p = 13, g = 2 (это образующий!) ----
    print("\n>>> ПРИМЕР 1: p = 13, g = 2 (из вашего текста)")
    demo1 = DiscreteLogDemo(p = 13, g = 2)
    demo1.print_properties()
    demo1.demo_powers(num_terms = 13)  # показываем полный цикл
    demo1.demo_discrete_log(b = 3)     # 2^x ≡ 3 (mod 13) -> x = 4
    demo1.demo_inverse_problem(b = 3)
    
    # ---- Пример 2: p = 13, g = 5 (НЕ образующий) ----
    print("\n\n>>> ПРИМЕР 2: p = 13, g = 5 (НЕ образующий, для сравнения)")
    demo2 = DiscreteLogDemo(p = 13, g = 5)
    demo2.print_properties()
    demo2.demo_powers(num_terms = 13)
    demo2.demo_discrete_log(b = 3)     # 5^x ≡ 3 (mod 13) - решения НЕТ!
    
    # ---- Пример 3: Большое поле (но не слишком, чтобы не ждать долго) ----
    print("\n\n>>> ПРИМЕР 3: p = 31, g = 3 (образующий)")
    demo3 = DiscreteLogDemo(p = 31, g = 3)
    demo3.print_properties()
    demo3.demo_powers(num_terms = 31)
    demo3.demo_discrete_log(b = 16)    # 3^x ≡ 16 (mod 31)
    
    # ---- Дополнительно: показываем рост времени поиска ----
    print("\n\n>>> ДЕМОНСТРАЦИЯ РОСТА СЛОЖНОСТИ (время поиска):")
    print("-" * 60)
    for p in [13, 31, 67, 101]:
        if not is_prime(p):
            continue
        # Ищем примитивный корень (просто берем 2, если подходит, иначе 3)
        g = 2
        if not is_primitive_root(g, p):
            g = 3
            if not is_primitive_root(g, p):
                g = 5
        
        # Берем случайное b (последнее число в последовательности)
        b = pow(g, p // 2, p)  # середина цикла
        
        start = time.time()
        x = discrete_log_bruteforce(g, b, p)
        elapsed = time.time() - start
        
        print(f"  p = {p:3d}, g = {g}:  перебор {p - 1} вариантов занял {elapsed * 1000:7.3f} мс")
        if p >= 101:
            print("  ⚠️  Для реальных p (300-значные числа) это займет миллиарды лет!")
    
    print("\n" + "=" * 60)
    print("  ВЫВОД: Задача дискретного логарифма труднорешаема,")
    print("  потому что числа ведут себя хаотично, а быстрого")
    print("  алгоритма (полиномиального) не существует.")
    print("=" * 60)


# =============================================
# 5. ТОЧКА ВХОДА
# =============================================

if __name__ == "__main__":
    run_demo_from_text()