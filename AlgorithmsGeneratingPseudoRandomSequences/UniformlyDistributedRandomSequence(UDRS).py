# 1. Равномерно распределенная случайная последовательность (РРСП)
import secrets
import math
from collections import Counter
from typing import List, Tuple, Dict

def _normal_cdf(x: float) -> float:
    """Функция распределения стандартного нормального закона."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def _chi2_p_value(chi2_stat: float, df: int) -> float:
    """
    Вычисление p-value для хи-квадрат распределения.
    Использует аппроксимацию без внешних библиотек.
    """
    if df <= 0:
        return 1.0
    
    # Для малых значений используем прямое вычисление
    if chi2_stat < 0:
        return 1.0
    
    # Аппроксимация через нормальное распределение (асимптотически точная)
    # Преобразование Уилсона-Хильферти
    if chi2_stat > 0:
        # Кубический корень из (chi2/df)
        cube_root = (chi2_stat / df) ** (1 / 3)
        mu = 1 - 2 / (9 * df)
        sigma = math.sqrt(2 / (9 * df))
        z = (cube_root - mu) / sigma
        p_value = 1.0 - _normal_cdf(z)
    else:
        p_value = 1.0
    
    return min(1.0, max(0.0, p_value))

def frequency_test(sequence: List[int], n: int, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Проверяет свойство (C2): равномерность распределения.
    Использует критерий хи-квадрат Пирсона.
    """
    observed = Counter(sequence)
    expected = len(sequence) / n
    
    chi2_stat = 0.0
    for val in range(n):
        o = observed.get(val, 0)
        chi2_stat += (o - expected) ** 2 / expected
    
    df = n - 1
    p_value = _chi2_p_value(chi2_stat, df)
    
    passed = p_value > alpha
    return passed, p_value

def independence_test(sequence: List[int], n: int, lag: int = 1, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Проверяет свойство (C1): независимость.
    Использует критерий хи-квадрат для таблицы сопряженности.
    """
    if len(sequence) <= lag:
        return True, 1.0
    
    pairs = [(sequence[i], sequence[i + lag]) for i in range(len(sequence) - lag)]
    observed = Counter(pairs)
    expected_count = len(pairs) / (n * n)
    
    chi2_stat = 0.0
    for a in range(n):
        for b in range(n):
            o = observed.get((a, b), 0)
            chi2_stat += (o - expected_count) ** 2 / expected_count
    
    df = n * n - 1
    p_value = _chi2_p_value(chi2_stat, df)
    
    passed = p_value > alpha
    return passed, p_value

def runs_test(sequence: List[int], n: int, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Серийный тест (runs test) на случайность.
    Проверяет количество серий (непрерывных последовательностей одинаковых элементов).
    """
    if len(sequence) < 2:
        return True, 1.0
    
    # Подсчет количества серий
    runs = 1
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i - 1]:
            runs += 1
    
    L = len(sequence)
    p_same = 1.0 / n
    p_diff = 1.0 - p_same
    
    expected_runs = 1 + (L - 1) * p_diff
    variance_runs = (L - 1) * p_diff * p_same
    
    if variance_runs <= 0:
        return True, 1.0
    
    z = (runs - expected_runs) / math.sqrt(variance_runs)
    # Двусторонний тест
    p_value = 2 * (1.0 - _normal_cdf(abs(z)))
    
    passed = p_value > alpha
    return passed, p_value

def poker_test(sequence: List[int], n: int, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Покер-тест - проверяет распределение комбинаций в блоках.
    Более чувствительный тест для обнаружения неслучайностей.
    """
    block_size = min(5, len(sequence) // 10)
    if block_size < 2:
        return True, 1.0
    
    num_blocks = len(sequence) // block_size
    if num_blocks < 10:
        return True, 1.0
    
    # Разбиваем на блоки
    blocks = [sequence[i * block_size:(i + 1) * block_size] for i in range(num_blocks)]
    # Подсчитываем количество уникальных значений в каждом блоке
    unique_counts = [len(set(block)) for block in blocks]
    observed = Counter(unique_counts)
    
    # Числа Стирлинга второго рода для block_size
    stirling = {
        2: {1: 1, 2: 1},
        3: {1: 1, 2: 3, 3: 1},
        4: {1: 1, 2: 7, 3: 6, 4: 1},
        5: {1: 1, 2: 15, 3: 25, 4: 10, 5: 1}
    }
    
    # Вычисление количества сочетаний (без использования math.comb для старых версий Python)
    def comb(n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        k = min(k, n - k)
        result = 1
        for i in range(1, k + 1):
            result = result * (n - k + i) // i
        return result
    
    chi2_stat = 0.0
    effective_categories = 0
    
    stirling_vals = stirling.get(block_size, {1: 1})
    
    for r in range(1, min(n, block_size) + 1):
        if r not in stirling_vals:
            continue
        prob = comb(n, r) * stirling_vals[r] * math.factorial(r) / (n ** block_size)
        expected = prob * num_blocks
        if expected >= 5:  # Критерий применимости хи-квадрат
            obs = observed.get(r, 0)
            chi2_stat += (obs - expected) ** 2 / expected
            effective_categories += 1
    
    df = effective_categories - 1
    if df <= 0:
        return True, 1.0
    
    p_value = _chi2_p_value(chi2_stat, df)
    passed = p_value > alpha
    return passed, p_value

def autocorrelation_test(sequence: List[int], n: int, max_lag: int = 10, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Тест на автокорреляцию - проверяет корреляцию между элементами на разных расстояниях.
    Возвращает минимальный p-value среди всех лагов.
    """
    min_p_value = 1.0
    all_passed = True
    
    for lag in range(1, min(max_lag, len(sequence) // 10) + 1):
        passed, p_value = independence_test(sequence, n, lag, alpha)
        min_p_value = min(min_p_value, p_value)
        if not passed:
            all_passed = False
    
    return all_passed, min_p_value

def generate_rrsp_like_sequence(length: int, n: int, use_crypto: bool = True) -> List[int]:
    """
    Генерирует последовательность, эмулирующую РРСП над Z_n.
    
    Параметры:
        length: длина последовательности
        n: модуль (размер алфавита Z_n = {0, 1, ..., n-1})
        use_crypto: если True, использует cryptographically secure RNG (secrets)
    """
    if use_crypto:
        return [secrets.randbelow(n) for _ in range(length)]
    else:
        import random
        random.seed(42)  # для воспроизводимости (только для отладки)
        return [random.randrange(n) for _ in range(length)]

def validate_rrsp(sequence: List[int], n: int, verbose: bool = True) -> Dict:
    """
    Проверяет, соответствует ли последовательность свойствам РРСП.
    
    Возвращает словарь с результатами всех тестов.
    """
    results = {}
    
    # Тест на равномерность (C2)
    passed_freq, p_freq = frequency_test(sequence, n)
    results['frequency_test'] = {'passed': passed_freq, 'p_value': p_freq, 'name': 'Равномерность (C2)'}
    
    # Тест на независимость для lag=1 (C1)
    passed_ind1, p_ind1 = independence_test(sequence, n, lag = 1)
    results['independence_lag1'] = {'passed': passed_ind1, 'p_value': p_ind1, 'name': 'Независимость (лаг 1)'}
    
    # Тест на независимость для lag=2
    passed_ind2, p_ind2 = independence_test(sequence, n, lag = 2)
    results['independence_lag2'] = {'passed': passed_ind2, 'p_value': p_ind2, 'name': 'Независимость (лаг 2)'}
    
    # Серийный тест
    passed_runs, p_runs = runs_test(sequence, n)
    results['runs_test'] = {'passed': passed_runs, 'p_value': p_runs, 'name': 'Серийный тест'}
    
    # Покер-тест
    passed_poker, p_poker = poker_test(sequence, n)
    results['poker_test'] = {'passed': passed_poker, 'p_value': p_poker, 'name': 'Покер-тест'}
    
    # Тест на автокорреляцию
    passed_auto, p_auto = autocorrelation_test(sequence, n, max_lag = 5)
    results['autocorrelation_test'] = {'passed': passed_auto, 'p_value': p_auto, 'name': 'Автокорреляция'}
    
    if verbose:
        print("=" * 70)
        print("РЕЗУЛЬТАТЫ ПРОВЕРКИ ПОСЛЕДОВАТЕЛЬНОСТИ НА СВОЙСТВА РРСП")
        print("=" * 70)
        print(f"Длина последовательности: {len(sequence)}")
        print(f"Модуль n = {n} (алфавит Z_{n})\n")
        
        all_passed = True
        for key, res in results.items():
            status = "✅ ПРОЙДЕН" if res['passed'] else "❌ НЕ ПРОЙДЕН"
            print(f"{res['name']:25} : {status}  (p-value = {res['p_value']:.6f})")
            if not res['passed']:
                all_passed = False
        
        print("-" * 70)
        if all_passed:
            print("📊 ВЫВОД: Последовательность НЕ ПРОТИВОРЕЧИТ свойствам РРСП.")
            print("   (Статистически значимых отклонений от равномерности и независимости не обнаружено)")
        else:
            print("⚠️ ВЫВОД: Последовательность статистически отличается от РРСП.")
            print("   (Некоторые тесты показали значимые отклонения)")
        print("=" * 70)
    
    return results

def demonstrate_properties(sequence: List[int], n: int):
    """
    Демонстрирует основные свойства РРСП.
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ СВОЙСТВ РРСП")
    print("=" * 70)
    
    # Свойство (C2): равномерность
    print("\n1. Свойство (C2) - Равномерность распределения:")
    dist = Counter(sequence)
    print(f"   Распределение значений от 0 до {n - 1}:")
    for val in range(n):
        freq = dist.get(val, 0)
        expected = len(sequence) / n
        print(f"     {val}: {freq} (ожидалось ≈ {expected:.1f}, отклонение = {freq - expected:+.1f})")
    
    # Свойство (C1): независимость (наглядный пример)
    print("\n2. Свойство (C1) - Независимость:")
    print("   Проверим условные вероятности на небольшом примере:")
    
    # Выбираем конкретное значение для анализа
    test_value = 0
    total_count = len(sequence)
    prob_all = dist.get(test_value, 0) / total_count
    
    # Проверяем условную вероятность после определенного паттерна
    pattern = [0, 1, 2]
    pattern_count = 0
    pattern_and_next_count = 0
    
    for i in range(len(sequence) - len(pattern) - 1):
        if sequence[i:i + len(pattern)] == pattern:
            pattern_count += 1
            if sequence[i + len(pattern)] == test_value:
                pattern_and_next_count += 1
    
    if pattern_count > 0:
        cond_prob = pattern_and_next_count / pattern_count
        print(f"   P(X_t = {test_value}) = {prob_all:.3f}")
        print(f"   P(X_t = {test_value} | предыдущие {pattern} = ...) = {cond_prob:.3f}")
        print(f"   Разница: {abs(cond_prob - prob_all):.3f} (в идеале должна быть близка к 0)")
    else:
        print("   Недостаточно данных для демонстрации условной вероятности")

def main():
    """Основная функция."""
    print("\n" + "█" * 70)
    print("█  РАВНОМЕРНО РАСПРЕДЕЛЕННАЯ СЛУЧАЙНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ (РРСП)")
    print("█  Эмуляция и статистическая верификация")
    print("█" * 70)
    
    # Параметры эксперимента
    N = 10          # модуль (Z_10 = {0, 1, ..., 9})
    LENGTH = 10000  # длина последовательности
    
    print(f"\n▶ Параметры:")
    print(f"   - Алфавит: Z_{N} = {{{', '.join(map(str, range(N)))}}}")
    print(f"   - Длина последовательности: {LENGTH}")
    print(f"   - Генератор: криптостойкий RNG (secrets.randbelow)")
    
    print(f"\n▶ Генерация последовательности...")
    seq = generate_rrsp_like_sequence(LENGTH, N, use_crypto = True)
    
    print(f"\n▶ Первые 100 значений:")
    # Красивый вывод по 20 чисел в строке
    for i in range(0, 100, 20):
        print("   ", ' '.join(f"{x:2d}" for x in seq[i:i + 20]))
    
    print()
    
    # Статистическая проверка
    results = validate_rrsp(seq, N, verbose = True)
    
    # Демонстрация свойств
    demonstrate_properties(seq, N)
    
    print("\n" + "=" * 70)
    print("ТЕОРЕТИЧЕСКАЯ СПРАВКА")
    print("=" * 70)
    print("РРСП (Uniformly Distributed Random Sequence) удовлетворяет:")
    print("  (C1) - независимость в совокупности")
    print("  (C2) - равномерное распределение")
    print("\nВажное следствие (с точки зрения теории информации):")
    print("  • Энтропия: H(X_t) = log₂(n) бит")
    print("  • Условная энтропия: H(X_t | прошлое) = log₂(n) бит")
    print("  • Взаимная информация: I(X_t; X_{t - 1}) = 0")
    print("  • Абсолютная непредсказуемость")
    print("\nПримечание: Это математическая идеализация. Компьютер может только")
    print("эмулировать РРСП с помощью криптостойких генераторов псевдослучайных чисел.")
    print("=" * 70)

if __name__ == "__main__":
    main()