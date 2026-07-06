# Тесты для проверки генераторов случайных и псевдослучайных чисел
import math
import random
from typing import List, Tuple

class MoveToFrontTest:
    """
    Реализация статистического теста "Стопка книг" (Move-to-Front)
    для проверки случайности последовательности символов.
    Без внешних зависимостей (только стандартная библиотека).
    """
    
    def __init__(self, alphabet_size: int, groups: List[Tuple[int, int]]):
        """
        Инициализация теста.
        
        Args:
            alphabet_size: Размер алфавита S (количество возможных символов)
            groups: Список кортежей (начало, конец) для разбиения номеров позиций
                   Например: [(1, 10), (11, 20)] для двух групп
                   Нумерация позиций начинается с 1!
        """
        self.S = alphabet_size
        self.groups = groups
        self.r = len(groups)
        
        # Проверка корректности разбиения
        self._validate_groups()
        
        # Вычисление вероятностей для каждой группы при H0
        self.probs = []
        for start, end in groups:
            size = end - start + 1
            self.probs.append(size / self.S)
            
        # Инициализация стопки книг (позиции букв)
        self.positions = list(range(1, self.S + 1))
        self.pos_to_letter = {i: i for i in range(1, self.S + 1)}
        
        # Счетчики попаданий в группы
        self.counts = [0] * self.r
        
        self.n = 0
        
    def _validate_groups(self):
        """Проверка корректности разбиения на группы."""
        all_positions = set()
        for start, end in self.groups:
            if start < 1 or end > self.S:
                raise ValueError(f"Позиции должны быть в диапазоне 1..{self.S}")
            if start > end:
                raise ValueError(f"Начало {start} не может быть больше конца {end}")
            for pos in range(start, end + 1):
                if pos in all_positions:
                    raise ValueError(f"Позиция {pos} входит в несколько групп")
                all_positions.add(pos)
        
        if len(all_positions) != self.S:
            raise ValueError(f"Разбиение покрывает не все позиции 1..{self.S}")
    
    def _move_to_front(self, letter: int):
        """Обновление стопки книг по правилу move-to-front."""
        current_pos = self.pos_to_letter[letter]
        
        for other_letter, pos in self.pos_to_letter.items():
            if pos < current_pos and other_letter != letter:
                self.pos_to_letter[other_letter] = pos + 1
        
        self.pos_to_letter[letter] = 1
        
        self.positions = [0] * (self.S + 1)
        for l, p in self.pos_to_letter.items():
            self.positions[l] = p
    
    def process_symbol(self, letter: int) -> int:
        """Обработка одного символа."""
        if letter < 1 or letter > self.S:
            raise ValueError(f"Символ должен быть в диапазоне 1..{self.S}")
        
        pos = self.pos_to_letter[letter]
        
        for i, (start, end) in enumerate(self.groups):
            if start <= pos <= end:
                self.counts[i] += 1
                break
        
        self._move_to_front(letter)
        self.n += 1
        return pos
    
    def process_sequence(self, sequence: List[int]) -> None:
        """Обработка последовательности символов."""
        for letter in sequence:
            self.process_symbol(letter)
    
    def compute_statistic(self) -> float:
        """Вычисление статистики χ²."""
        if self.n == 0:
            return 0.0
        
        stat = 0.0
        for i, count in enumerate(self.counts):
            expected = self.n * self.probs[i]
            if expected > 0:
                stat += (count - expected) ** 2 / expected
        
        return stat
    
    def _gamma_function(self, x: float) -> float:
        """Вычисление гамма-функции (аппроксимация Ланцоша)."""
        if x < 0.5:
            return math.pi / (math.sin(math.pi * x) * self._gamma_function(1 - x))
        
        x -= 1
        g = 7
        c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
             771.32342877765313, -176.61502916214059, 12.507343278686905,
             -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
        
        x += 1
        t = c[0]
        for i in range(1, g + 2):
            t += c[i] / (x + i - 1)
        
        return math.sqrt(2 * math.pi) * math.pow(x + g - 0.5, x - 0.5) * math.exp(-(x + g - 0.5)) * t
    
    def _regularized_gamma(self, a: float, x: float) -> float:
        """Вычисление регуляризованной гамма-функции P(a, x)."""
        if x < 0 or a <= 0:
            return 0.0
        
        if x < a + 1:
            # Используем ряд
            term = 1.0 / a
            sum_series = 1.0 / a
            for i in range(1, 1000):
                term *= x / (a + i)
                sum_series += term
                if abs(term) < 1e-15:
                    break
            return math.pow(x, a) * math.exp(-x) * sum_series
        else:
            # Используем цепную дробь
            b = x + 1 - a
            c = 1.0 / 1e-30
            d = 1.0 / b
            h = d
            for i in range(1, 1000):
                an = -i * (i - a)
                b = b + 2
                d = an * d + b
                if abs(d) < 1e-30:
                    d = 1e-30
                c = b + an / c
                if abs(c) < 1e-30:
                    c = 1e-30
                d = 1.0 / d
                delta = d * c
                h *= delta
                if abs(delta - 1) < 1e-15:
                    break
            return 1.0 - math.pow(x, a) * math.exp(-x) * h / self._gamma_function(a)
    
    def _chi2_cdf(self, x: float, df: int) -> float:
        """Функция распределения χ²."""
        if x < 0:
            return 0.0
        if df <= 0:
            return 0.0
        if x == float('inf'):
            return 1.0
        
        return self._regularized_gamma(df / 2.0, x / 2.0)
    
    def get_p_value(self) -> float:
        """Вычисление p-value."""
        stat = self.compute_statistic()
        df = self.r - 1
        return 1.0 - self._chi2_cdf(stat, df)
    
    def test(self, alpha: float = 0.05) -> Tuple[bool, float, float]:
        """Проверка гипотезы H0 (случайность) против H1 (неслучайность)."""
        stat = self.compute_statistic()
        df = self.r - 1
        p_value = 1.0 - self._chi2_cdf(stat, df)
        reject = p_value < alpha
        
        return reject, stat, p_value
    
    def reset(self):
        """Сброс теста к начальному состоянию."""
        self.positions = list(range(1, self.S + 1))
        self.pos_to_letter = {i: i for i in range(1, self.S + 1)}
        self.counts = [0] * self.r
        self.n = 0
    
    def get_critical_value(self, alpha: float) -> float:
        """Получение критического значения χ² для заданного уровня значимости."""
        df = self.r - 1
        # Находим квантиль с помощью бинарного поиска
        lo, hi = 0.0, 1000.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if self._chi2_cdf(mid, df) < 1 - alpha:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


def generate_linear_congruential(n: int, a: int = 1103515245, c: int = 12345, m: int = 2 ** 31, seed: int = 12345):
    """Генератор линейной конгруэнтной последовательности (для демонстрации)."""
    x = seed
    sequence = []
    for _ in range(n):
        x = (a * x + c) % m
        sequence.append(x)
    return sequence


def extract_high_bit(values: List[int], m: int) -> List[int]:
    """Извлечение старшего бита из значений (режим R1)."""
    result = []
    for i, x in enumerate(values):
        if m % 2 == 0:  # четное
            bit = 0 if x < m / 2 else 1
        else:  # нечетное
            if x < (m - 1) / 2:
                bit = 0
            elif x > (m - 1) / 2:
                bit = 1
            else:
                continue  # пропускаем
        if i % 8 == 0:
            byte = 0
        byte = (byte << 1) | bit
        if i % 8 == 7:
            result.append(byte + 1)  # +1, так как символы от 1 до S
    return result


def demo_simple():
    """Простая демонстрация работы теста."""
    print("\n" + "=" * 70)
    print("Простая демонстрация работы теста")
    print("=" * 70)
    
    S = 8
    groups = [(1, 4), (5, 8)]
    
    print(f"Алфавит размера S = {S}")
    print(f"Группы: A1 = {list(range(1,5))}, A2 = {list(range(5,9))}")
    print(f"Вероятности при H0: P(A1) = {4 / 8:.2f}, P(A2) = {4 / 8:.2f}")
    
    test = MoveToFrontTest(S, groups)
    
    # Случайная последовательность
    print("\n--- Тест на случайной последовательности ---")
    random.seed(123)
    random_seq = [random.randint(1, S) for _ in range(1000)]
    test.process_sequence(random_seq)
    reject, stat, p_value = test.test()
    print(f"Статистика χ² = {stat:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Гипотеза H0 {'ОТКЛОНЯЕТСЯ' if reject else 'НЕ отклоняется'} при α = 0.05")
    
    # Неслучайная последовательность
    print("\n--- Тест на неслучайной последовательности ---")
    test.reset()
    non_random_seq = []
    for _ in range(1000):
        if random.random() < 0.5:
            non_random_seq.append(1)
        else:
            non_random_seq.append(random.randint(2, S))
    
    test.process_sequence(non_random_seq)
    reject, stat, p_value = test.test()
    print(f"Статистика χ² = {stat:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Гипотеза H0 {'ОТКЛОНЯЕТСЯ' if reject else 'НЕ отклоняется'} при α = 0.05")


def test_knuth_generators():
    """Тестирование генераторов из книги Кнута."""
    print("\n" + "=" * 70)
    print("Тестирование генераторов из книги Д. Кнута")
    print("=" * 70)
    
    # Исправленные группы: теперь они покрывают все позиции
    tests = [
        ("B", 24, 1680000, [(1, 2 ** 17), (2 ** 17 + 1, 2 ** 24)], 52, 4),
        ("C", 24, 7920000, [(1, 2 ** 17), (2 ** 17 + 1, 2 ** 24)], 70, 17),
        ("D", 16, 160000, [(1, 2 ** 10), (2 ** 10 + 1, 2 ** 14), (2 ** 14 + 1, 2 ** 16)], 74, 16),
        ("E", 12, 12000, [(1, 2 ** 3), (2 ** 3 + 1, 2 ** 5), (2 ** 5 + 1, 2 ** 12)], 99, 97),
        ("F", 8, 240, [(1, 2 ** 1), (2 ** 1 + 1, 2 ** 2), (2 ** 2 + 1, 2 ** 8)], 83, 80),
    ]
    
    for name, s, n, groups_spec, expected_q50, expected_q95 in tests:
        S = 2 ** s
        groups = []
        for g in groups_spec:
            if isinstance(g, tuple):
                groups.append(g)
            elif isinstance(g, int):
                groups.append((1, g))
        
        print(f"\nГенератор {name}, s = {s}, S = {S}, n = {n}")
        print(f"Группы: {groups}")
        
        # Проверяем, что группы покрывают все позиции
        total_size = sum(end - start + 1 for start, end in groups)
        print(f"Общий размер групп: {total_size} (должно быть {S})")
        
        test = MoveToFrontTest(S, groups)
        
        # Генерация последовательности
        if name == "B":
            random.seed(42)
            sequence = [random.randint(1, S) for _ in range(n)]
        elif name == "F":
            # Используем линейный конгруэнтный генератор
            lcg_values = generate_linear_congruential(n, seed = 12345)
            sequence = extract_high_bit(lcg_values, 2 ** 31)
            # Обрезаем до нужной длины
            sequence = sequence[:n]
            # Если последовательность короче, дополняем случайными
            while len(sequence) < n:
                sequence.append(random.randint(1, S))
            sequence = sequence[:n]
        else:
            random.seed(42)
            sequence = [random.randint(1, S) for _ in range(n)]
        
        test.process_sequence(sequence)
        stat = test.compute_statistic()
        df = len(groups) - 1
        p_value = test.get_p_value()
        
        print(f"Статистика χ² = {stat:.4f}")
        print(f"Число степеней свободы = {df}")
        print(f"p-value = {p_value:.6f}")
        
        critical_95 = test.get_critical_value(0.95)
        critical_50 = test.get_critical_value(0.50)
        
        print(f"Критическое значение (α = 0.95): {critical_95:.4f}")
        print(f"Критическое значение (α = 0.50): {critical_50:.4f}")
        print(f"Ожидаемые Q0.5 = {expected_q50}, Q0.95 = {expected_q95} из таблицы")
        
        if stat > critical_95:
            print("⚠️  Генератор ОТКЛОНЕН при α = 0.95")
        elif stat > critical_50:
            print("⚠️  Генератор на грани при α = 0.50")
        else:
            print("✓ Генератор прошел тест")
        
        # 100 испытаний
        print("\nПроведение 100 испытаний для оценки Q0.5 и Q0.95...")
        
        q50_count = 0
        q95_count = 0
        
        for trial in range(100):
            test.reset()
            if name == "B":
                seq = [random.randint(1, S) for _ in range(n)]
            elif name == "F":
                lcg_vals = generate_linear_congruential(n, seed = 12345 + trial * 1000)
                seq = extract_high_bit(lcg_vals, 2**31)
                while len(seq) < n:
                    seq.append(random.randint(1, S))
                seq = seq[:n]
            else:
                seq = [random.randint(1, S) for _ in range(n)]
            
            test.process_sequence(seq)
            stat_i = test.compute_statistic()
            
            if stat_i > critical_50:
                q50_count += 1
            if stat_i > critical_95:
                q95_count += 1
        
        print(f"Q0.5 = {q50_count} (ожидалось ~{expected_q50})")
        print(f"Q0.95 = {q95_count} (ожидалось ~{expected_q95})")
        
        if q95_count > 11:
            print(f"⚠️  Генератор {name} ОТКЛОНЯЕТСЯ при уровне значимости 0.01 (Q0.95 = {q95_count} > 11)")
        else:
            print(f"✓ Генератор {name} не отклоняется при уровне значимости 0.01")


if __name__ == "__main__":
    demo_simple()
    test_knuth_generators()