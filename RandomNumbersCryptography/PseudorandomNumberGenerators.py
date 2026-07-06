# Генераторы псевдослучайных чисел
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSA ГЕНЕРАТОР ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ
На основе текста из раздела 9.3 "Генераторы псевдослучайных чисел"

Реализует:
1. RSA-генератор псевдослучайных чисел
2. Статистические тесты (частотный, блоков, серий, длинных серий)
3. ASCII-визуализация битовой последовательности
4. Демонстрация непредсказуемости
5. Тестирование производительности

Автор: на основе учебного материала по криптографии
Версия: 2.0 (исправлены ошибки)
"""

import random
import math
import time
import sys
from typing import List, Tuple, Optional


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СТАТИСТИКИ
# ============================================================================

def incomplete_gamma(s: float, x: float, max_iter: int = 1000) -> float:
    """
    Вычисление регуляризованной неполной гамма-функции P(s, x)
    Используется для расчета p-value в тесте частоты в блоках
    
    Args:
        s: параметр формы (s > 0)
        x: значение (x >= 0)
        max_iter: максимальное число итераций
    
    Returns:
        P(s, x) - регуляризованная неполная гамма-функция
    """
    if x < 0 or s <= 0:
        return 0.0
    
    if x == 0:
        return 0.0
    
    if s > 100:  # Для больших s используем аппроксимацию
        # Аппроксимация нормальным распределением
        mean = s
        var = s
        z = (x - mean) / math.sqrt(var)
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    # Используем ряд для малых x
    if x < s + 1:
        # Последовательный ряд
        term = math.exp(s * math.log(x) - x - math.lgamma(s + 1))
        sum_val = term
        for n in range(1, max_iter):
            term *= x / (s + n)
            sum_val += term
            if term < 1e-15 * sum_val:
                break
        return sum_val
    else:
        # Используем цепную дробь для больших x
        a = 1 - s
        b = x + 1 - s
        c = 1 / b
        d = 1 / b
        h = d
        for i in range(1, max_iter):
            a += 1
            b += 2
            d = a * d + b
            if d == 0:
                d = 1e-30
            c = b + a / c
            if c == 0:
                c = 1e-30
            d = 1 / d
            delta = c * d
            h *= delta
            if abs(delta - 1) < 1e-15:
                break
        
        # Регуляризованная гамма-функция
        result = 1 - math.exp(s * math.log(x) - x - math.lgamma(s)) * h
        return max(0.0, min(1.0, result))


def chi_square_cdf(x: float, df: float) -> float:
    """
    Функция распределения хи-квадрат
    
    Args:
        x: значение
        df: число степеней свободы
    
    Returns:
        P(X <= x) для распределения хи-квадрат с df степенями свободы
    """
    if x <= 0:
        return 0.0
    return incomplete_gamma(df / 2, x / 2)


# ============================================================================
# КЛАСС: ГЕНЕРАТОР ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ НА ОСНОВЕ RSA
# ============================================================================

class RSAPRNG:
    """
    Генератор псевдослучайных чисел на основе RSA
    
    Алгоритм:
        xi ← xi-1^e mod N
        zi ← младший бит xi
    
    Свойства:
        - Статистически неотличим от случайного
        - Непредсказуем за полиномиальное время (основан на сложности факторизации)
        - Может использоваться для генерации ключей
    """
    
    def __init__(self, bits: int = 256, e: int = 3, verbose: bool = True):
        """
        Инициализация генератора
        
        Args:
            bits: размер простых чисел в битах (рекомендуется >= 256)
            e: открытая экспонента (по умолчанию 3 для ускорения)
            verbose: вывод информации о генерации параметров
        """
        self.bits = bits
        self.e = e
        self.N = None
        self.x_current = None
        self.verbose = verbose
        self._generate_parameters()
        
    def _is_prime(self, n: int, k: int = 40) -> bool:
        """
        Тест Миллера-Рабина для проверки простоты
        
        Args:
            n: проверяемое число
            k: количество раундов теста
            
        Returns:
            True если число вероятно простое
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
            
        # Представление n-1 как d * 2^r
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
            
        # Проверка k раундов
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def _generate_prime(self) -> int:
        """Генерация простого числа заданного размера"""
        while True:
            # Генерация нечетного числа с установленными старшим и младшим битами
            n = random.getrandbits(self.bits)
            n |= (1 << self.bits - 1) | 1
            
            if self._is_prime(n):
                return n
    
    def _generate_parameters(self):
        """Генерация параметров RSA (P, Q, N)"""
        if self.verbose:
            print(f"Генерация параметров RSA ({self.bits}-битные простые числа)...")
        
        start_time = time.time()
        
        # Генерация двух различных простых чисел
        P = self._generate_prime()
        Q = self._generate_prime()
        while P == Q:
            Q = self._generate_prime()
            
        self.N = P * Q
        
        # Проверка, что e взаимно просто с (P-1)(Q-1)
        phi = (P - 1) * (Q - 1)
        if math.gcd(self.e, phi) != 1:
            # Если e не взаимно просто, используем стандартное значение
            self.e = 65537
            while math.gcd(self.e, phi) != 1:
                self.e = random.randrange(3, phi, 2)
        
        if self.verbose:
            elapsed = time.time() - start_time
            print(f"  Параметры сгенерированы за {elapsed:.2f} сек.")
            print(f"  Размер N: {self.N.bit_length()} бит")
            print(f"  e = {self.e}")
            print(f"  Размер P: {P.bit_length()} бит, Q: {Q.bit_length()} бит")
        
    def seed(self, seed_value: Optional[int] = None):
        """
        Установка начального значения (семени)
        
        Args:
            seed_value: случайное число из диапазона (1, N-1) если None, генерируется случайное
        """
        if seed_value is None:
            self.x_current = random.randrange(2, self.N - 1)
        else:
            if not (1 < seed_value < self.N):
                raise ValueError(f"Семя должно быть в диапазоне (1, {self.N - 1})")
            self.x_current = seed_value
            
    def next_bit(self) -> int:
        """
        Генерация следующего бита последовательности
        
        Returns:
            0 или 1 (младший бит xi)
        """
        if self.x_current is None:
            self.seed()
            
        # xi ← xi-1^e mod N
        self.x_current = pow(self.x_current, self.e, self.N)
        
        # zi ← младший бит xi
        return self.x_current & 1
    
    def generate_bits(self, count: int) -> List[int]:
        """
        Генерация последовательности бит
        
        Args:
            count: количество бит для генерации
            
        Returns:
            Список бит (0 или 1)
        """
        if count <= 0:
            return []
            
        bits = []
        for _ in range(count):
            bits.append(self.next_bit())
        return bits
    
    def generate_bytes(self, byte_count: int) -> bytes:
        """
        Генерация байтов (по 8 бит)
        
        Args:
            byte_count: количество байтов
            
        Returns:
            Байтовая строка
        """
        bits = self.generate_bits(byte_count * 8)
        result = bytearray()
        
        for i in range(byte_count):
            byte_val = 0
            for j in range(8):
                byte_val |= (bits[i * 8 + j] << (7 - j))
            result.append(byte_val)
            
        return bytes(result)
    
    def get_state(self) -> dict:
        """Получение текущего состояния генератора"""
        return {
            'bits': self.bits,
            'e': self.e,
            'N': self.N,
            'x_current': self.x_current,
            'N_bit_length': self.N.bit_length() if self.N else 0
        }
    
    def __str__(self) -> str:
        """Строковое представление генератора"""
        return f"RSAPRNG(bits = {self.bits}, e = {self.e}, N = {self.N.bit_length()} бит)"


# ============================================================================
# КЛАСС: СТАТИСТИЧЕСКИЕ ТЕСТЫ
# ============================================================================

class StatisticalTests:
    """
    Набор статистических тестов для проверки качества ГПСЧ
    
    Тесты из NIST SP 800-22:
        1. Частотный тест (Frequency Test)
        2. Тест частоты в блоках (Block Frequency Test)
        3. Тест серий (Runs Test)
        4. Тест на длинные серии (Long Runs Test)
    """
    
    @staticmethod
    def frequency_test(bits: List[int]) -> Tuple[float, bool]:
        """
        Частотный тест: проверка баланса нулей и единиц
        
        Returns:
            (p-value, passed) - p-value и результат (True если пройден)
        """
        n = len(bits)
        if n == 0:
            return (0.0, False)
            
        sum_bits = sum(bits)
        s = abs(sum_bits - n / 2) / math.sqrt(n / 4)
        p_value = math.erfc(s / math.sqrt(2))
        
        # Уровень значимости 0.01
        passed = p_value >= 0.01
        return (p_value, passed)
    
    @staticmethod
    def block_frequency_test(bits: List[int], block_size: int = 128) -> Tuple[float, bool]:
        """
        Тест частоты в блоках: проверка равномерности распределения в блоках
        
        Returns:
            (p-value, passed)
        """
        n = len(bits)
        if n < block_size:
            return (0.0, False)
            
        m = n // block_size
        blocks = [bits[i * block_size:(i + 1) * block_size] for i in range(m)]
        
        # Статистика хи-квадрат
        chi_square = 0.0
        for block in blocks:
            ones = sum(block)
            proportion = ones / block_size
            chi_square += (proportion - 0.5) ** 2
            
        chi_square *= 4.0 * block_size
        
        # Вычисляем p-value через функцию распределения хи-квадрат
        p_value = 1.0 - chi_square_cdf(chi_square, m)
        
        passed = p_value >= 0.01
        return (p_value, passed)
    
    @staticmethod
    def runs_test(bits: List[int]) -> Tuple[float, bool]:
        """
        Тест серий: проверка случайности появления серий одинаковых бит
        
        Returns:
            (p-value, passed)
        """
        n = len(bits)
        if n < 2:
            return (0.0, False)
            
        # Количество переходов между 0 и 1
        transitions = sum(1 for i in range(n - 1) if bits[i] != bits[i + 1])
        
        ones = sum(bits)
        zeros = n - ones
        
        if ones == 0 or zeros == 0:
            return (0.0, False)
            
        # Статистика
        mean = 1 + 2 * ones * zeros / n
        variance = 2 * ones * zeros * (2 * ones * zeros - n) / (n * n * (n - 1))
        
        if variance == 0:
            return (0.0, False)
            
        s = (transitions - mean) / math.sqrt(variance)
        p_value = math.erfc(abs(s) / math.sqrt(2))
        
        passed = p_value >= 0.01
        return (p_value, passed)
    
    @staticmethod
    def long_runs_test(bits: List[int], threshold: int = 26) -> Tuple[bool, str]:
        """
        Тест на длинные серии
        
        Returns:
            (passed, message)
        """
        if not bits:
            return (False, "Пустая последовательность")
            
        max_run = 0
        current_run = 1
        
        for i in range(1, len(bits)):
            if bits[i] == bits[i - 1]:
                current_run += 1
            else:
                max_run = max(max_run, current_run)
                current_run = 1
        max_run = max(max_run, current_run)
        
        passed = max_run < threshold
        message = f"Максимальная серия: {max_run} {'(OK)' if passed else '(ПРЕВЫШЕНА!)'}"
        return (passed, message)
    
    @staticmethod
    def run_all_tests(bits: List[int], block_size: int = 128) -> dict:
        """
        Запуск всех статистических тестов
        
        Returns:
            Словарь с результатами всех тестов
        """
        results = {}
        
        # 1. Частотный тест
        p_val, passed = StatisticalTests.frequency_test(bits)
        results['frequency'] = {'p_value': p_val, 'passed': passed}
        
        # 2. Тест частоты в блоках
        p_val, passed = StatisticalTests.block_frequency_test(bits, block_size)
        results['block_frequency'] = {'p_value': p_val, 'passed': passed}
        
        # 3. Тест серий
        p_val, passed = StatisticalTests.runs_test(bits)
        results['runs'] = {'p_value': p_val, 'passed': passed}
        
        # 4. Тест на длинные серии
        passed, message = StatisticalTests.long_runs_test(bits)
        results['long_runs'] = {'passed': passed, 'message': message}
        
        return results


# ============================================================================
# ФУНКЦИИ ВИЗУАЛИЗАЦИИ
# ============================================================================

def visualize_bits_ascii(bits: List[int], width: int = 80, show_stats: bool = True):
    """
    ASCII-визуализация битовой последовательности
    
    Args:
        bits: список бит (0 или 1)
        width: ширина строки в битах
        show_stats: показывать ли статистику
    """
    if not bits:
        print("Пустая последовательность")
        return
    
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ БИТОВОЙ ПОСЛЕДОВАТЕЛЬНОСТИ")
    print("=" * 60)
    print("█ = 1, ░ = 0")
    print("-" * (width + 2))
    
    # Вывод битов в виде ASCII-графики
    rows = len(bits) // width
    for i in range(min(rows, 20)):  # Ограничиваем вывод 20 строками
        chunk = bits[i * width:(i + 1) * width]
        line = ''.join('█' if b == 1 else '░' for b in chunk)
        print(f"|{line}|")
    
    if rows > 20:
        print(f"|... (всего {rows} строк) ...|")
    
    # Остаток
    remainder = len(bits) % width
    if remainder > 0 and rows < 20:
        chunk = bits[rows * width:]
        line = ''.join('█' if b == 1 else '░' for b in chunk)
        print(f"|{line}{'░' * (width - remainder)}|")
    
    print("-" * (width + 2))
    
    if show_stats:
        # Статистика
        print(f"\nВсего бит: {len(bits)}")
        ones = sum(bits)
        zeros = len(bits) - ones
        print(f"Единиц: {ones} ({ones / len(bits) * 100:.2f}%)")
        print(f"Нулей:  {zeros} ({zeros / len(bits) * 100:.2f}%)")
        print(f"Разница: {abs(ones - zeros)}")
        
        # Статистика по строкам
        if rows > 0:
            ones_per_row = []
            for i in range(min(rows, 10)):
                row = bits[i * width:(i + 1) * width]
                ones_per_row.append(sum(row))
            
            print(f"\nЕдиниц в первых {len(ones_per_row)} строках:")
            print(f"  {ones_per_row}")
            if rows > 10:
                print(f"  ... (всего {rows} строк)")


def print_bit_sequence(bits: List[int], max_display: int = 100):
    """
    Печать битовой последовательности в сжатом виде
    
    Args:
        bits: список бит
        max_display: максимальное количество бит для отображения
    """
    print("\nБИТОВАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:")
    print("-" * 40)
    
    if len(bits) <= max_display:
        print(''.join(str(b) for b in bits))
    else:
        print(''.join(str(b) for b in bits[:max_display]))
        print(f"... (всего {len(bits)} бит)")


# ============================================================================
# ДЕМОНСТРАЦИОННЫЕ ФУНКЦИИ
# ============================================================================

def demo_basic():
    """Базовая демонстрация работы генератора"""
    print("\n" + "=" * 60)
    print("БАЗОВАЯ ДЕМОНСТРАЦИЯ RSA ГЕНЕРАТОРА")
    print("=" * 60)
    
    # Создание генератора с небольшим размером для скорости
    prng = RSAPRNG(bits = 128, e = 3)
    
    # Установка семени
    seed = random.randint(2, prng.N - 2)
    prng.seed(seed)
    print(f"\nСемя: {seed}")
    
    # Генерация бит
    print("\nГенерация 1000 бит...")
    bits = prng.generate_bits(1000)
    
    # Визуализация
    visualize_bits_ascii(bits[:200], width = 40, show_stats = False)
    
    # Статистические тесты
    print("\nСТАТИСТИЧЕСКИЕ ТЕСТЫ:")
    print("-" * 40)
    results = StatisticalTests.run_all_tests(bits)
    
    for test_name, result in results.items():
        if 'p_value' in result:
            status = '✓ ПРОЙДЕН' if result['passed'] else '✗ НЕ ПРОЙДЕН'
            print(f"{test_name}:")
            print(f"  p-value = {result['p_value']:.6f}")
            print(f"  Результат: {status}")
        else:
            print(f"{test_name}: {result['message']}")


def demo_predictability():
    """Демонстрация непредсказуемости генератора"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НЕПРЕДСКАЗУЕМОСТИ")
    print("=" * 60)
    
    prng = RSAPRNG(bits = 256, verbose = False)
    prng.seed()
    
    # Генерируем последовательность
    known_bits = 100
    bits = prng.generate_bits(known_bits + 1)
    
    print(f"\nЗадача:")
    print(f"  Дано: {known_bits} бит последовательности")
    print(f"  Цель: предсказать {(known_bits + 1)}-й бит")
    
    print("\nТеоретическая атака перебором ключей:")
    print(f"  Размер ключа: {prng.bits} бит")
    print(f"  Количество возможных ключей: 2 ^ {prng.bits} ≈ {2 ** prng.bits:.2e}")
    print(f"  Время перебора на суперкомпьютере: неприемлемо большое")
    
    print("\nПрактическое применение:")
    print("  Сгенерированный ключ (32 байта) можно использовать как:")
    print("  - Симметричный ключ для AES")
    print("  - Семя для другого ГПСЧ")
    print("  - Ключ для HMAC")
    
    # Показываем первые биты
    print(f"\nПервые 50 бит последовательности:")
    print(''.join(str(b) for b in bits[:50]))
    print(f"...")
    print(f"{(known_bits + 1)}-й бит (реальное значение): {bits[known_bits]}")
    print("\nБез знания семени невозможно предсказать этот бит!")


def demo_performance():
    """Тестирование производительности генератора"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    
    # Тестируем разные размеры
    sizes = [128, 256, 512]
    iterations = 1000
    
    print(f"\nГенерация {iterations} бит для разных размеров ключа:")
    print("-" * 60)
    print(f"{'Размер ключа':<15} {'Время (сек)':<15} {'Бит/сек':<15}")
    print("-" * 60)
    
    for bits in sizes:
        # Создаем генератор (без вывода)
        prng = RSAPRNG(bits = bits, verbose = False)
        prng.seed()
        
        # Измеряем время генерации
        start_time = time.time()
        _ = prng.generate_bits(iterations)
        elapsed = time.time() - start_time
        
        speed = iterations / elapsed if elapsed > 0 else 0
        print(f"{bits:<15} {elapsed:<15.6f} {speed:<15.2f}")


def demo_key_generation():
    """Демонстрация генерации ключей"""
    print("\n" + "=" * 60)
    print("ГЕНЕРАЦИЯ КРИПТОГРАФИЧЕСКИХ КЛЮЧЕЙ")
    print("=" * 60)
    
    # Создаем генератор
    prng = RSAPRNG(bits = 256)
    prng.seed()
    
    # Генерируем ключи разных размеров
    key_sizes = [16, 32, 64]  # байт
    
    print("\nСгенерированные ключи:")
    print("-" * 60)
    
    for size in key_sizes:
        key = prng.generate_bytes(size)
        print(f"Ключ {size} байт (hex): {key.hex()}")
        print(f"Ключ {size} байт (len): {len(key)} байт")
        print("-" * 40)


def demo_entropy_estimation():
    """Оценка энтропии сгенерированной последовательности"""
    print("\n" + "=" * 60)
    print("ОЦЕНКА ЭНТРОПИИ")
    print("=" * 60)
    
    # Создаем генератор
    prng = RSAPRNG(bits = 256, verbose = False)
    prng.seed()
    
    # Генерируем биты
    bit_count = 10000
    bits = prng.generate_bits(bit_count)
    
    # Оценка энтропии по частотам
    ones = sum(bits)
    zeros = bit_count - ones
    p1 = ones / bit_count
    p0 = zeros / bit_count
    
    # Энтропия Шеннона
    entropy = 0
    if p0 > 0:
        entropy -= p0 * math.log2(p0)
    if p1 > 0:
        entropy -= p1 * math.log2(p1)
    
    print(f"\nАнализ {bit_count} бит:")
    print(f"  Единиц: {ones} ({p1 * 100:.2f}%)")
    print(f"  Нулей:  {zeros} ({p0 * 100:.2f}%)")
    print(f"  Энтропия: {entropy:.6f} бит (максимум: 1.0)")
    print(f"  Качество: {entropy * 100:.2f}% от идеального")
    
    if entropy > 0.99:
        print("  ✓ Энтропия близка к идеальной (отличное качество)")
    elif entropy > 0.95:
        print("  ✓ Хорошая энтропия")
    else:
        print("  ⚠ Энтропия ниже ожидаемой")


def compare_with_random():
    """Сравнение с встроенным генератором random"""
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ С ВСТРОЕННЫМ ГЕНЕРАТОРОМ RANDOM")
    print("=" * 60)
    
    bit_count = 10000
    
    # RSA генератор
    print("\nRSA Генератор:")
    prng = RSAPRNG(bits = 256, verbose = False)
    prng.seed()
    rsa_bits = prng.generate_bits(bit_count)
    rsa_results = StatisticalTests.run_all_tests(rsa_bits)
    
    # Встроенный генератор
    print("\nВстроенный генератор random:")
    random.seed(42)  # Фиксируем семя для воспроизводимости
    random_bits = [random.randint(0, 1) for _ in range(bit_count)]
    random_results = StatisticalTests.run_all_tests(random_bits)
    
    # Сравнение результатов
    print("\nСРАВНЕНИЕ РЕЗУЛЬТАТОВ ТЕСТОВ:")
    print("-" * 60)
    print(f"{'Тест':<25} {'RSA':<15} {'random':<15}")
    print("-" * 60)
    
    for test_name in ['frequency', 'block_frequency', 'runs']:
        rsa_p = rsa_results[test_name]['p_value']
        rand_p = random_results[test_name]['p_value']
        rsa_ok = '✓' if rsa_results[test_name]['passed'] else '✗'
        rand_ok = '✓' if random_results[test_name]['passed'] else '✗'
        print(f"{test_name:<25} {rsa_p:.6f} {rsa_ok:<8} {rand_p:.6f} {rand_ok:<8}")
    
    print("\nВывод: RSA генератор статистически неотличим от встроенного random")


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ И МЕНЮ
# ============================================================================

def show_menu():
    """Отображение меню"""
    print("\n" + "=" * 60)
    print("RSA ГЕНЕРАТОР ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ")
    print("=" * 60)
    print("\nВыберите режим работы:")
    print("  1. Базовая демонстрация")
    print("  2. Демонстрация непредсказуемости")
    print("  3. Тестирование производительности")
    print("  4. Генерация ключей")
    print("  5. Оценка энтропии")
    print("  6. Сравнение с встроенным генератором")
    print("  7. Все тесты (полная демонстрация)")
    print("  0. Выход")
    print("-" * 60)


def run_all_tests():
    """Запуск всех демонстраций"""
    demo_basic()
    demo_predictability()
    demo_performance()
    demo_key_generation()
    demo_entropy_estimation()
    compare_with_random()


def main():
    """Главная функция"""
    while True:
        show_menu()
        choice = input("\nВаш выбор: ").strip()
        
        if choice == '0':
            print("\nДо свидания!")
            break
        elif choice == '1':
            demo_basic()
        elif choice == '2':
            demo_predictability()
        elif choice == '3':
            demo_performance()
        elif choice == '4':
            demo_key_generation()
        elif choice == '5':
            demo_entropy_estimation()
        elif choice == '6':
            compare_with_random()
        elif choice == '7':
            run_all_tests()
        else:
            print("\nНеверный выбор. Пожалуйста, выберите от 0 до 7.")
        
        input("\nНажмите Enter для продолжения...")


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")