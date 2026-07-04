# Постановка задачи
import math
import time
import random
from typing import Optional, Tuple

class DiscreteLogarithmDemo:
    """
    Демонстрация методов вычисления дискретного логарифма
    на основе текста о криптоанализе
    """
    
    def __init__(self):
        self.operations_count = 0  # Счетчик операций умножения
        
    def reset_counter(self):
        """Сброс счетчика операций"""
        self.operations_count = 0
        
    def mod_pow(self, a: int, x: int, p: int) -> int:
        """
        Быстрое возведение в степень по модулю (бинарный метод)
        Сложность: O(log x) операций умножения
        Соответствует формуле t_y ≤ 2·log x из текста
        """
        self.operations_count = 0
        result = 1
        base = a % p
        
        while x > 0:
            if x & 1:  # Если текущий бит = 1
                result = (result * base) % p
                self.operations_count += 1
            base = (base * base) % p
            self.operations_count += 1
            x >>= 1
            
        return result
    
    def brute_force(self, a: int, y: int, p: int) -> Optional[int]:
        """
        Метод прямого перебора
        Сложность: O(p) операций в худшем случае, O(p/2) в среднем
        Соответствует формуле t_п.п. ≈ p/2 из текста
        """
        self.reset_counter()
        
        # Проверяем x от 0 до p-1
        current = 1  # a^0 mod p
        
        for x in range(p):
            self.operations_count += 1  # Проверка равенства
            if current == y:
                return x
            # Умножаем на a для следующего шага
            current = (current * a) % p
            self.operations_count += 1  # Умножение
            
        return None
    
    def baby_step_giant_step(self, a: int, y: int, p: int) -> Optional[int]:
        """
        Метод "шаг младенца, шаг великана" (Baby-step giant-step)
        Сложность: O(√p) операций памяти и времени
        Соответствует формуле t_ш.м.ш.в. ≈ 2·√p из текста
        """
        self.reset_counter()
        
        if p == 1:
            return 0
            
        # m = ceil(√p)
        m = int(math.isqrt(p)) + 1
        
        # Шаг младенца: вычисляем a^j mod p для j = 0..m-1
        baby_steps = {}
        current = 1  # a^0 mod p
        
        for j in range(m):
            baby_steps[current] = j
            self.operations_count += 1  # Сохранение в словарь
            # Переход к следующему j
            current = (current * a) % p
            self.operations_count += 1  # Умножение
            
        # Вычисляем a^{-m} mod p
        # a^{-m} ≡ a^{p-1-m} mod p (по теореме Ферма)
        a_inv_m = pow(a, p - 1 - m, p)
        self.operations_count += m.bit_length()  # Учитываем сложность pow
        
        # Шаг великана: ищем совпадение
        # y * (a^{-m})^i mod p
        current = y % p
        
        for i in range(m):
            self.operations_count += 1  # Проверка в словаре
            if current in baby_steps:
                x = i * m + baby_steps[current]
                if x < p:
                    return x
            # Переход к следующему i
            current = (current * a_inv_m) % p
            self.operations_count += 1  # Умножение
            
        return None
    
    def index_calculus_demo(self, p: int) -> Tuple[int, int]:
        """
        Демонстрация метода исчисления порядка (упрощенная версия)
        Реальная реализация сложна, здесь показываем только оценку сложности
        """
        # Метод исчисления порядка имеет сложность
        # t_и.п. ≈ c1 · 2^(c2·√(log p · log log p))
        # Это субэкспоненциальная сложность
        
        log_p = math.log(p)
        log_log_p = math.log(log_p) if log_p > 1 else 1
        
        # Оценочное количество операций (c1 ≈ 2, c2 ≈ 1)
        estimated_ops = int(2 * math.exp(math.sqrt(log_p * log_log_p)))
        
        return estimated_ops, len(str(p))
    
    def measure_time(self, method, *args) -> Tuple[Optional[int], float, int]:
        """
        Измерение времени выполнения метода
        Возвращает: (результат, время_в_секундах, количество_операций)
        """
        self.reset_counter()
        start_time = time.perf_counter()
        result = method(*args)
        end_time = time.perf_counter()
        
        return result, end_time - start_time, self.operations_count


def print_separator(char = '=', length = 70):
    """Печать разделителя"""
    print(char * length)


def format_large_number(num: float) -> str:
    """Форматирует большие числа в читаемый вид"""
    if num < 1:
        return f"{num:.2f}"
    elif num < 10:
        return f"{num:.2f}"
    elif num < 1000:
        return f"{num:.0f}"
    elif num < 1e6:
        return f"{num / 1e3:.1f}K"
    elif num < 1e9:
        return f"{num / 1e6:.1f}M"
    elif num < 1e12:
        return f"{num / 1e9:.1f}B"
    elif num < 1e15:
        return f"{num / 1e12:.1f}T"
    else:
        # Для очень больших чисел используем научную нотацию
        exponent = int(math.log10(num))
        mantissa = num / (10 ** exponent)
        return f"{mantissa:.2f}×10 ^ {exponent}"


def format_log2_operations(log2_ops: float) -> str:
    """Форматирует количество операций в log2 масштабе"""
    if log2_ops < 10:
        return f"2 ^ {log2_ops:.1f} ≈ {2 ** log2_ops:.0f}"
    elif log2_ops < 20:
        return f"2 ^ {log2_ops:.1f} ≈ {2 ** log2_ops:,.0f}"
    elif log2_ops < 30:
        return f"2 ^ {log2_ops:.1f} ≈ {2 ** log2_ops / 1e6:.1f}M"
    elif log2_ops < 40:
        return f"2 ^ {log2_ops:.1f} ≈ {2 ** log2_ops / 1e9:.1f}B"
    elif log2_ops < 50:
        return f"2 ^ {log2_ops:.1f} ≈ {2 ** log2_ops / 1e12:.1f}T"
    else:
        # Для очень больших значений показываем только степень
        return f"2 ^ {log2_ops:.1f}"


def demo_small_numbers():
    """Демонстрация на маленьких числах для понимания работы"""
    demo = DiscreteLogarithmDemo()
    
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ АЛГОРИТМОВ НА МАЛЕНЬКИХ ЧИСЛАХ")
    print("=" * 70)
    
    # Выбираем простое число p и основание a
    p = 101  # Простое число
    a = 2    # Основание (первообразный корень по модулю 101)
    x = 37   # Секретный показатель
    
    print(f"\nДано:")
    print(f"  p = {p} (длина {p.bit_length()} бит)")
    print(f"  a = {a}")
    print(f"  x = {x} (секретный показатель)")
    
    # Вычисляем y = a^x mod p
    y = demo.mod_pow(a, x, p)
    ops_pow = demo.operations_count
    
    print(f"\nПрямая задача (возведение в степень):")
    print(f"  y = a^x mod p = {y}")
    print(f"  Операций умножения: {ops_pow}")
    print(f"  Сложность: O(log x) ≈ O({x.bit_length()})")
    print(f"  Теоретическая оценка: ≤ 2·log₂(x) = {2 * math.log2(x):.1f}")
    
    print(f"\n{'=' * 70}")
    print("РЕШЕНИЕ ОБРАТНОЙ ЗАДАЧИ (поиск x):")
    print("=" * 70)
    
    # 1. Прямой перебор
    print(f"\n1. ПРЯМОЙ ПЕРЕБОР (Brute Force):")
    print(f"   Теоретическая сложность: O(p) = O({p})")
    print(f"   log₂(t_п.п.) ≈ log₂(p) = {math.log2(p):.1f}")
    
    result, elapsed, ops = demo.measure_time(demo.brute_force, a, y, p)
    
    if result is not None:
        print(f"   Найден x = {result}")
    print(f"   Время выполнения: {elapsed:.6f} сек")
    print(f"   Операций умножения: {ops}")
    print(f"   Соответствует формуле: t_п.п. ≈ p / 2 = {p / 2:.1f}")
    
    # 2. Метод "шаг младенца, шаг великана"
    print(f"\n2. МЕТОД 'ШАГ МЛАДЕНЦА, ШАГ ВЕЛИКАНА':")
    print(f"   Теоретическая сложность: O(2·√p) = O({2 * int(math.sqrt(p))})")
    print(f"   log₂(t_ш.м.ш.в.) ≈ log₂(2·√p) = {math.log2(2 * math.sqrt(p)):.1f}")
    
    result, elapsed, ops = demo.measure_time(demo.baby_step_giant_step, a, y, p)
    
    if result is not None:
        print(f"   Найден x = {result}")
    print(f"   Время выполнения: {elapsed:.6f} сек")
    print(f"   Операций умножения: {ops}")
    print(f"   Соответствует формуле: t_ш.м.ш.в. ≈ 2·√{p} = {2 * math.sqrt(p):.1f}")
    
    # 3. Оценка метода исчисления порядка
    print(f"\n3. МЕТОД ИСЧИСЛЕНИЯ ПОРЯДКА (оценка):")
    estimated_ops, digits = demo.index_calculus_demo(p)
    log2_estimated = math.log2(estimated_ops)
    print(f"   Оценочное количество операций: {format_large_number(estimated_ops)}")
    print(f"   log₂(t_и.п.) ≈ {log2_estimated:.1f}")
    print(f"   Сложность: субэкспоненциальная")
    
    # Сравнение эффективности
    print(f"\nСРАВНЕНИЕ ЭФФЕКТИВНОСТИ (в log₂):")
    print(f"  log₂(t_п.п.) = {math.log2(p):.1f}")
    print(f"  log₂(t_ш.м.ш.в.) = {math.log2(2 * math.sqrt(p)):.1f}")
    print(f"  log₂(t_и.п.) = {log2_estimated:.1f}")
    print(f"  Выигрыш BSGS над перебором: 2 ^ {math.log2(p) - math.log2(2 * math.sqrt(p)):.1f} раз")


def demo_scale_comparison():
    """Сравнение сложности при разных длинах чисел"""
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ СЛОЖНОСТИ ПРИ РАЗНОЙ БИТОВОЙ ДЛИНЕ n")
    print("=" * 70)
    
    # Тестируем разные длины
    test_cases = [
        (10, "~2 ^ 10", 1024),
        (20, "~2 ^ 20", 1_048_576),
        (30, "~2 ^ 30", 1_073_741_824),
        (40, "~2 ^ 40", 1_099_511_627_776),
        (50, "~2 ^ 50", 1_125_899_906_842_624),
        (60, "~2 ^ 60", 1_152_921_504_606_846_976),
    ]
    
    print("\nТаблица сложности алгоритмов:")
    print("-" * 100)
    print(f"{'n (бит)':<10} {'p ≈':<20} {'log₂(t_п.п.)':<20} {'log₂(t_ш.м.ш.в.)':<20} {'log₂(t_и.п.)':<20}")
    print("-" * 100)
    
    for n, p_str, p_val in test_cases:
        ty = n
        log2_tpp = n - 1  # t_п.п. ≈ 2^(n-1)
        log2_tbsgs = n / 2  # t_ш.м.ш.в. ≈ 2^(n/2)
        
        # Оценка для метода исчисления порядка
        # t_и.п. ≈ 2^(c·√(n·log n)), c ≈ 1
        log2_tip = math.sqrt(n * math.log2(n))
        
        print(f"{n:<10} {p_str:<20} {log2_tpp:<20.1f} {log2_tbsgs:<20.1f} {log2_tip:<20.1f}")
    
    print("-" * 100)
    
    print("\nАбсолютные значения (количество операций):")
    print("-" * 100)
    print(f"{'n (бит)':<10} {'t_п.п. (перебор)':<30} {'t_ш.м.ш.в.':<30} {'t_и.п. (оценка)':<30}")
    print("-" * 100)
    
    for n, p_str, p_val in test_cases:
        tpp = 2 ** (n - 1)
        tbsgs = 2 ** (n / 2)
        log2_tip = math.sqrt(n * math.log2(n))
        tip = 2 ** log2_tip
        
        print(f"{n:<10} {format_log2_operations(n - 1):<30} {format_log2_operations(n / 2):<30} {format_log2_operations(log2_tip):<30}")
    
    print("-" * 100)
    print("\nВывод: При увеличении n на 1 бит:")
    print("  - t_y (возведение) растет линейно (+1 операция)")
    print("  - t_п.п. (перебор) удваивается")
    print("  - t_ш.м.ш.в. растет в √2 раз")
    print("  - t_и.п. растет субэкспоненциально")
    print("  - Это создает огромный разрыв в сложности!")


def demo_security_implications():
    """Демонстрация практических последствий для безопасности"""
    print("\n" + "=" * 70)
    print("ПРАКТИЧЕСКИЕ ВЫВОДЫ ДЛЯ КРИПТОГРАФИЧЕСКОЙ БЕЗОПАСНОСТИ")
    print("=" * 70)
    
    # Современные рекомендации по длине ключей
    security_levels = [
        (1024, "Низкий (устаревший)", "не рекомендуется"),
        (2048, "Средний (минимальный)", "рекомендуется"),
        (3072, "Высокий", "рекомендуется для новых систем"),
        (4096, "Очень высокий", "для долгосрочной безопасности"),
    ]
    
    print("\nРекомендации по длине модуля p:")
    print("-" * 100)
    print(f"{'Битовая длина n':<18} {'Уровень безопасности':<30} {'Статус':<35}")
    print("-" * 100)
    
    for n, level, status in security_levels:
        print(f"{n:<18} {level:<30} {status:<35}")
    
    print("-" * 100)
    
    print("\nОценка сложности взлома (в log₂ операций):")
    print("-" * 100)
    print(f"{'n (бит)':<12} {'Прямой перебор':<25} {'BSGS':<25} {'Исчисление порядка'}")
    print("-" * 100)
    
    for n, level, status in security_levels:
        log2_bruteforce = n - 1
        log2_bsgs = n / 2
        log2_index = math.sqrt(n * math.log2(n))
        
        print(f"{n:<12} {log2_bruteforce:<25.1f} {log2_bsgs:<25.1f} {log2_index:<25.1f}")
    
    print("-" * 100)
    
    # Практическая интерпретация
    print("\nПРАКТИЧЕСКАЯ ИНТЕРПРЕТАЦИЯ:")
    print("-" * 100)
    
    interpretations = [
        (1024, "Взлом возможен за несколько дней/недель при достаточных ресурсах"),
        (2048, "Взлом требует астрономических ресурсов (> 2 ^ 1024 операций)"),
        (3072, "Взлом практически невозможен даже с использованием всех мировых ресурсов"),
        (4096, "Взлом невозможен даже в обозримом будущем при текущих знаниях"),
    ]
    
    for n, interpretation in interpretations:
        print(f"  n = {n}: {interpretation}")
    
    print("-" * 100)
    
    print("\nВажно понимать:")
    print("1. Даже самый быстрый метод взлома (исчисление порядка)")
    print("   имеет субэкспоненциальную сложность.")
    print("2. Это вынуждает использовать числа длиной ≥ 2048 бит.")
    print("3. Если будет найден полиномиальный алгоритм,")
    print("   все существующие системы станут небезопасными.")
    
    # Дополнительная информация о современных требованиях
    print("\n" + "=" * 70)
    print("СОВРЕМЕННЫЕ РЕКОМЕНДАЦИИ ПО БЕЗОПАСНОСТИ (2024-2026)")
    print("=" * 70)
    print("""
    Для обеспечения безопасности на 2024-2026 годы:
    
    • Минимальная длина модуля p: 2048 бит
    • Рекомендуемая длина: 3072 - 4096 бит
    • Для долгосрочной безопасности (до 2030+): 4096 бит
    
    Сравнение методов взлома при n = 2048:
    • Прямой перебор: 2 ^ 2047 ≈ 10 ^ 616 операций (невозможно)
    • BSGS: 2 ^ 1024 ≈ 10 ^ 308 операций (невозможно)
    • Исчисление порядка: 2 ^ 150 ≈ 10 ^ 45 операций (теоретически возможно, 
      но требует огромных ресурсов и времени)
    
    Это показывает, почему метод исчисления порядка является 
    самым опасным для криптосистем!
    """)


def demo_practical_example():
    """Практический пример с реальными числами"""
    print("\n" + "=" * 70)
    print("ПРАКТИЧЕСКИЙ ПРИМЕР С РЕАЛЬНЫМИ ЧИСЛАМИ")
    print("=" * 70)
    
    demo = DiscreteLogarithmDemo()
    
    # Используем большее простое число, но все еще manageable
    p = 1009  # Простое число
    a = 3
    x = 567
    
    print(f"\nТестируем с p = {p} (длина {p.bit_length()} бит):")
    print(f"Это соответствует n = {p.bit_length()} бит")
    
    y = demo.mod_pow(a, x, p)
    print(f"y = {a} ^ {x} mod {p} = {y}")
    
    print("\nПоиск дискретного логарифма методом BSGS...")
    
    # BSGS метод
    result, elapsed, ops = demo.measure_time(demo.baby_step_giant_step, a, y, p)
    
    if result is not None and result == x:
        print(f"✓ Успешно найден x = {result}")
        print(f"  Время: {elapsed:.4f} сек")
        print(f"  Операций: {ops}")
        print(f"  Теоретическая оценка: 2·√{p} ≈ {2 * math.sqrt(p):.1f}")
        print(f"  log₂(t_ш.м.ш.в.) = {math.log2(2 * math.sqrt(p)):.1f}")
        
        # Сравнение с перебором
        print(f"\nСравнение с прямым перебором:")
        print(f"  Перебор потребовал бы: ~{p / 2:.0f} операций")
        print(f"  BSGS потребовал: {ops} операций")
        print(f"  Ускорение в {p / 2 / ops:.0f} раз!")
    else:
        print("✗ Ошибка в вычислениях")


def main():
    """Главная функция программы"""
    print("\n" + "=" * 70)
    print("ДИСКРЕТНЫЙ ЛОГАРИФМ: АНАЛИЗ СЛОЖНОСТИ И МЕТОДОВ ВЗЛОМА")
    print("На основе задачи из криптоанализа")
    print("=" * 70)
    
    # Демонстрация на малых числах
    demo_small_numbers()
    
    # Сравнение сложности
    demo_scale_comparison()
    
    # Практические выводы
    demo_security_implications()
    
    # Практический пример
    demo_practical_example()
    
    print("\n" + "=" * 70)
    print("КЛЮЧЕВЫЕ ВЫВОДЫ:")
    print("=" * 70)
    print("""
    1. Криптосистемы основаны на разрыве между прямой и обратной задачей.
    2. Возведение в степень (y = a ^ x mod p) — линейная сложность O(n).
    3. Поиск дискретного логарифма:
       - Прямой перебор: O(2 ^ n) — экспоненциальный рост
       - Шаг младенца/великана: O(2 ^ (n / 2)) — экспоненциальный, но быстрее
       - Исчисление порядка: O(2 ^ (c·√(n·log n))) — субэкспоненциальный
    4. Выбор длины числа p — компромисс между скоростью и безопасностью.
    5. Существование полиномиального алгоритма — открытая проблема!
    
    Рекомендации по длине модуля p (2024 - 2026):
    - 2048 бит: минимально приемлемый уровень
    - 3072 бит: рекомендуется для новых систем
    - 4096 бит: для долгосрочной безопасности
    
    ВНИМАНИЕ: С развитием квантовых компьютеров алгоритм Шора
    может решить задачу дискретного логарифмирования за 
    полиномиальное время, что сделает эти системы небезопасными!
    """)


if __name__ == "__main__":
    main()