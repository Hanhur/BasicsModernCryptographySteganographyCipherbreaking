# Задачи, возникающие при использовании физических генераторов случайных чисел
import math
import random
from collections import defaultdict
from typing import List, Tuple, Dict
import itertools


class PhysicalRandomGenerator:
    """
    Эмуляция физического генератора случайных чисел с заданным смещением p.
    В реальности это был бы аппаратный генератор, но для демонстрации
    используем программный с контролируемым смещением.
    """
    def __init__(self, p: float, seed: int = None):
        """
        p: вероятность появления единицы (0 < p < 1)
        """
        self.p = p
        if seed is not None:
            random.seed(seed)
    
    def generate_bit(self) -> int:
        """Генерирует один бит с вероятностью P(1) = p"""
        return 1 if random.random() < self.p else 0
    
    def generate_sequence(self, length: int) -> List[int]:
        """Генерирует последовательность бит заданной длины"""
        return [self.generate_bit() for _ in range(length)]


class VonNeumannExtractor:
    """
    Классический метод фон Неймана (1949).
    Разбивает последовательность на пары бит.
    00 → Λ (пусто), 01 → 0, 10 → 1, 11 → Λ
    """
    
    @staticmethod
    def extract(bits: List[int]) -> List[int]:
        """
        Преобразует смещенную последовательность в равновероятную.
        Возвращает очищенную последовательность.
        """
        result = []
        for i in range(0, len(bits) - 1, 2):
            a, b = bits[i], bits[i + 1]
            if a == 0 and b == 1:
                result.append(0)
            elif a == 1 and b == 0:
                result.append(1)
            # 00 и 11 игнорируем
        return result
    
    @staticmethod
    def efficiency(p: float) -> float:
        """
        Теоретическая эффективность метода фон Неймана:
        из t входных бит получается t * p * (1 - p) выходных.
        Максимум при p = 0.5: 0.25 (т.е. 25% от входа).
        """
        return p * (1 - p)


class EliasExtractor:
    """
    Метод Элайеса (обобщение метода фон Неймана).
    Кодирует блоки длины n. Все блоки с одинаковым количеством
    нулей и единиц преобразуются в уникальные коды.
    
    Сложность: O(2 ^ n) по памяти.
    """
    
    def __init__(self, n: int):
        """
        n: длина блока для кодирования
        """
        self.n = n
        self.encoding_table = self._build_encoding_table()
    
    def _build_encoding_table(self) -> Dict[Tuple[int, ...], List[int]]:
        """
        Строит таблицу кодирования для всех блоков длины n.
        Принцип: все блоки с одинаковым весом Хэмминга (одинаковым
        количеством единиц) кодируются одинаковым количеством бит,
        но с разными значениями, чтобы сохранить равновероятность.
        """
        table = {}
        
        # Группируем все блоки по количеству единиц
        groups = defaultdict(list)
        for bits in itertools.product([0, 1], repeat = self.n):
            ones_count = sum(bits)
            groups[ones_count].append(bits)
        
        # Для каждой группы строим кодирование
        for ones_count, blocks in groups.items():
            # Количество блоков в группе
            m = len(blocks)
            if m <= 1:
                # Если блок только один (все нули или все единицы),
                # его нельзя использовать - пропускаем
                continue
            
            # Вычисляем, сколько бит нужно для кодирования m вариантов
            code_length = math.ceil(math.log2(m))
            
            # Присваиваем каждому блоку уникальный код
            for idx, block in enumerate(blocks):
                # Преобразуем индекс в бинарный код фиксированной длины
                code = []
                for j in range(code_length - 1, -1, -1):
                    code.append((idx >> j) & 1)
                table[block] = code
        
        return table
    
    def extract(self, bits: List[int]) -> List[int]:
        """
        Извлекает равновероятные биты из входной последовательности.
        """
        result = []
        i = 0
        while i + self.n <= len(bits):
            block = tuple(bits[i:i + self.n])
            if block in self.encoding_table:
                result.extend(self.encoding_table[block])
            i += self.n
        return result
    
    def get_efficiency(self, p: float) -> float:
        """
        Вычисляет теоретическую эффективность метода.
        η_n = (средняя длина выходного слова) / n
        """
        total_prob = 0
        total_bits = 0
        
        for block, code in self.encoding_table.items():
            ones = sum(block)
            prob = (p ** ones) * ((1 - p) ** (self.n - ones))
            total_prob += prob
            total_bits += len(code) * prob
        
        return total_bits / self.n if total_prob > 0 else 0


class RyabkoMachikinaExtractor:
    """
    Улучшенный метод Рябко и Мачикиной.
    Асимптотически достигает энтропии Шеннона,
    но требует памяти O(n log n) вместо O(2 ^ n).
    
    Принцип: использует арифметическое кодирование на основе
    весов Хэмминга блоков.
    """
    
    def __init__(self, n: int):
        """
        n: длина блока для кодирования
        """
        self.n = n
        # Предварительно вычисляем биномиальные коэффициенты
        # для быстрого доступа
        self.binomial = self._precompute_binomial(n)
    
    def _precompute_binomial(self, n: int) -> List[List[int]]:
        """Вычисляет биномиальные коэффициенты C(n, k)"""
        C = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            C[i][0] = C[i][i] = 1
            for j in range(1, i):
                C[i][j] = C[i - 1][j - 1] + C[i - 1][j]
        return C
    
    def _encode_block(self, block: Tuple[int, ...]) -> List[int]:
        """
        Кодирует один блок используя комбинаторное кодирование.
        Для блока с k единицами:
        - Находим его порядковый номер среди всех блоков с k единицами
        - Кодируем этот номер минимальным числом бит
        """
        n = len(block)
        k = sum(block)
        
        if k == 0 or k == n:
            # Блоки из всех нулей или всех единиц не несут энтропии
            return []
        
        # Находим ранг блока среди всех блоков с таким же весом
        # Используем комбинаторную нумерацию (система счисления)
        rank = 0
        ones_seen = 0
        for i, bit in enumerate(block):
            if bit == 1:
                # Если на позиции i стоит 1, то все блоки,
                # где на этой позиции 0, а остальные k - ones_seen - 1
                # единиц расположены правее, идут перед текущим
                remaining = n - i - 1
                need = k - ones_seen - 1
                if need >= 0 and remaining >= need:
                    rank += self.binomial[remaining][need]
                ones_seen += 1
        
        # Количество блоков с таким же весом
        total = self.binomial[n][k]
        
        # Кодируем ранг минимальным числом бит
        if total <= 1:
            return []
        
        code_length = math.ceil(math.log2(total))
        code = []
        for j in range(code_length - 1, -1, -1):
            code.append((rank >> j) & 1)
        
        return code
    
    def extract(self, bits: List[int]) -> List[int]:
        """
        Извлекает равновероятные биты из входной последовательности.
        """
        result = []
        i = 0
        while i + self.n <= len(bits):
            block = tuple(bits[i:i + self.n])
            result.extend(self._encode_block(block))
            i += self.n
        return result
    
    def get_efficiency_theoretical(self, p: float) -> float:
        """
        Теоретическая эффективность стремится к энтропии Шеннона
        при n → ∞.
        """
        if p == 0 or p == 1:
            return 0
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def entropy(p: float) -> float:
    """Вычисляет энтропию Шеннона для вероятности p"""
    if p == 0 or p == 1:
        return 0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def test_extractors(p: float, sequence_length: int = 10000, n: int = 4):
    """
    Тестирует все три метода очистки на одной входной последовательности.
    """
    print("=" * 70)
    print(f"Тестирование методов очистки случайных бит")
    print(f"Входные параметры: p = {p}, длина последовательности = {sequence_length}, n = {n}")
    print("=" * 70)
    
    # Генерируем входную последовательность
    rng = PhysicalRandomGenerator(p, seed = 42)
    bits = rng.generate_sequence(sequence_length)
    
    # Статистика входной последовательности
    ones = sum(bits)
    zeros = len(bits) - ones
    print(f"\nВходная последовательность:")
    print(f"  Нулей: {zeros}, Единиц: {ones}")
    print(f"  P(0) = {zeros / len(bits):.4f}, P(1) = {ones / len(bits):.4f}")
    print(f"  Энтропия Шеннона: {entropy(p):.4f} бит/символ")
    
    # 1. Метод фон Неймана
    vn = VonNeumannExtractor()
    vn_result = vn.extract(bits)
    vn_ones = sum(vn_result)
    vn_zeros = len(vn_result) - vn_ones
    vn_efficiency = len(vn_result) / len(bits)
    
    print(f"\n1. Метод фон Неймана:")
    print(f"   Длина выхода: {len(vn_result)} (из {len(bits)} входных)")
    print(f"   Эффективность: {vn_efficiency:.4f} (теоретическая: {VonNeumannExtractor.efficiency(p):.4f})")
    if len(vn_result) > 0:
        print(f"   P(0) = {vn_zeros / len(vn_result):.4f}, P(1) = {vn_ones / len(vn_result):.4f}")
    
    # 2. Метод Элайеса
    elias = EliasExtractor(n)
    elias_result = elias.extract(bits)
    elias_ones = sum(elias_result)
    elias_zeros = len(elias_result) - elias_ones
    elias_efficiency = len(elias_result) / len(bits)
    
    print(f"\n2. Метод Элайеса (n={n}):")
    print(f"   Длина выхода: {len(elias_result)} (из {len(bits)} входных)")
    print(f"   Эффективность: {elias_efficiency:.4f} (теоретическая: {elias.get_efficiency(p):.4f})")
    if len(elias_result) > 0:
        print(f"   P(0) = {elias_zeros / len(elias_result):.4f}, P(1) = {elias_ones / len(elias_result):.4f}")
    print(f"   Размер таблицы кодирования: {len(elias.encoding_table)} блоков")
    
    # 3. Метод Рябко-Мачикиной
    rm = RyabkoMachikinaExtractor(n)
    rm_result = rm.extract(bits)
    rm_ones = sum(rm_result)
    rm_zeros = len(rm_result) - rm_ones
    rm_efficiency = len(rm_result) / len(bits)
    
    print(f"\n3. Метод Рябко-Мачикиной (n={n}):")
    print(f"   Длина выхода: {len(rm_result)} (из {len(bits)} входных)")
    print(f"   Эффективность: {rm_efficiency:.4f}")
    print(f"   Теоретический предел (энтропия): {entropy(p):.4f}")
    if len(rm_result) > 0:
        print(f"   P(0) = {rm_zeros / len(rm_result):.4f}, P(1) = {rm_ones / len(rm_result):.4f}")
    print(f"   Используемая память: O(n log n) = O({n} * {math.log2(n):.1f})")
    
    print("\n" + "=" * 70)


def compare_efficiencies():
    """Сравнивает эффективность методов для разных p"""
    print("\nСравнение эффективности методов при разных p:")
    print("-" * 70)
    print(f"{'p':>6} | {'Энтропия':>10} | {'Фон Нейман':>12} | {'Элайес (n = 4)':>14} | {'Элайес (n = 6)':>14}")
    print("-" * 70)
    
    for p in [0.1, 0.2, 0.3, 0.4, 0.5]:
        h = entropy(p)
        vn_eff = VonNeumannExtractor.efficiency(p)
        
        elias4 = EliasExtractor(4)
        elias4_eff = elias4.get_efficiency(p)
        
        elias6 = EliasExtractor(6)
        elias6_eff = elias6.get_efficiency(p)
        
        print(f"{p:6.2f} | {h:10.4f} | {vn_eff:12.4f} | {elias4_eff:14.4f} | {elias6_eff:14.4f}")
    
    print("-" * 70)
    print("Примечание: Элайес (n = 6) требует O(2 ^ 6) = 64 элемента памяти.")
    print("          Для n = 20 потребовалось бы O(2 ^ 20) ≈ 1 миллион элементов.")
    print("          Метод Рябко-Мачикиной решает эту проблему.")


def demo_block_length_impact():
    """Демонстрирует влияние длины блока на эффективность метода Рябко-Мачикиной"""
    print("\nВлияние длины блока n на эффективность (p=0.3):")
    print("-" * 70)
    print(f"{'n':>4} | {'Эффективность':>14} | {'Память O(n log n)':>18} | {'O(2 ^ n) (Элайес)':>18}")
    print("-" * 70)
    
    p = 0.3
    h = entropy(p)
    
    for n in [2, 3, 4, 5, 6, 7, 8]:
        rm = RyabkoMachikinaExtractor(n)
        # Для небольших n моделируем эффективность эмпирически
        # Генерируем тестовую последовательность
        rng = PhysicalRandomGenerator(p, seed = 42)
        bits = rng.generate_sequence(10000)
        result = rm.extract(bits)
        eff = len(result) / len(bits)
        
        memory_rm = n * math.log2(n) if n > 0 else 0
        memory_elias = 2 ** n
        
        print(f"{n:4d} | {eff:14.4f} | {memory_rm:18.1f} | {memory_elias:18d}")
    
    print("-" * 70)
    print(f"Энтропия Шеннона для p = {p}: {h:.4f} (теоретический предел)")


if __name__ == "__main__":
    # Основной тест
    test_extractors(p = 0.3, sequence_length = 10000, n = 4)
    
    # Сравнение эффективности
    compare_efficiencies()
    
    # Демонстрация влияния длины блока
    demo_block_length_impact()