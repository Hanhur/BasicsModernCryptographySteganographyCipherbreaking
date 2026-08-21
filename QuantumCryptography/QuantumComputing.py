# Квантовые вычисления 
import math
import random
from collections import Counter
from fractions import Fraction

# =====================================================
# ШАГ 1: Вспомогательные функции (НОД, проверка простоты)
# =====================================================

def gcd(a, b):
    """Наибольший общий делитель (классический алгоритм Евклида)"""
    while b != 0:
        a, b = b, a % b
    return a

def is_prime(n):
    """Проверка на простоту (для маленьких чисел)"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def random_coprime(n):
    """Выбирает случайное число a, взаимно простое с n (1 < a < n)"""
    while True:
        a = random.randint(2, n - 1)
        if gcd(a, n) == 1:
            return a

def factorize_trivial(n):
    """Тривиальная факторизация для проверки (маленькие числа)"""
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return i, n // i
    return None


# =====================================================
# ШАГ 2: Квантовая суперпозиция (симуляция)
# =====================================================

def create_superposition(m):
    """
    Создает суперпозицию всех состояний от 0 до 2^m - 1
    Возвращает список значений x в виде обычного списка Python
    (в реальном QC это были бы кубиты)
    """
    N = 2 ** m
    return list(range(N))


# =====================================================
# ШАГ 3: Вычисление f(x) = a^x mod n
# =====================================================

def modular_exponentiation(a, x, n):
    """Быстрое возведение в степень по модулю: a^x mod n"""
    result = 1
    base = a % n
    while x > 0:
        if x & 1:  # Если текущий бит = 1
            result = (result * base) % n
        base = (base * base) % n
        x >>= 1
    return result

def apply_function(superposition, a, n):
    """
    Применяет f(x) = a^x mod n ко всем состояниям суперпозиции
    Возвращает словарь {x: f(x)}
    """
    return {x: modular_exponentiation(a, x, n) for x in superposition}


# =====================================================
# ШАГ 4: Квантовое измерение (коллапс состояния)
# =====================================================

def measure_state(function_results, target_value):
    """
    Симуляция измерения: выбираем все x, для которых f(x) == target_value
    Это соответствует коллапсу в подпространство с заданным значением
    """
    selected = [x for x, fx in function_results.items() if fx == target_value]
    return selected


# =====================================================
# ШАГ 5: Дискретное преобразование Фурье (DFT) - аналог QFT
# =====================================================

def dft(sequence):
    """
    Дискретное преобразование Фурье (без NumPy)
    Для списка длиной N возвращает список комплексных амплитуд
    """
    N = len(sequence)
    result = []
    for k in range(N):
        sum_real = 0.0
        sum_imag = 0.0
        for n in range(N):
            angle = 2.0 * math.pi * k * n / N
            real_part = sequence[n] * math.cos(angle)
            imag_part = -sequence[n] * math.sin(angle)
            sum_real += real_part
            sum_imag += imag_part
        result.append((sum_real, sum_imag))  # Комплексное число
    return result

def find_period_from_dft(dft_result, m):
    """
    Находит период r из DFT:
    - Вычисляем амплитуду |c|^2 для каждого k
    - Находим пики (где амплитуда максимальна)
    - Используем цепные дроби для восстановления периода
    """
    N = len(dft_result)
    amplitudes = [(k, (real ** 2 + imag ** 2)) for k, (real, imag) in enumerate(dft_result)]
    
    # Сортируем по убыванию амплитуды
    amplitudes.sort(key = lambda x: x[1], reverse = True)
    
    # Берем топ-3 пика (кроме k=0, который всегда DC-компонента)
    peaks = [k for k, amp in amplitudes[1:4] if amp > 0.01]
    
    if not peaks:
        return None
    
    # Для каждого пика пытаемся найти период через цепные дроби
    for k in peaks:
        if k == 0:
            continue
        # k/N ≈ j/r, где j - целое, r - период
        frac = Fraction(k, N).limit_denominator(N // 2)
        r = frac.denominator
        
        # Проверяем, что период разумный
        if 1 < r < N and r < N // 2:
            return r
    
    return None


# =====================================================
# ШАГ 6: Полный алгоритм Шора
# =====================================================

def shor_algorithm(n, max_attempts = 10, verbose = True):
    """
    Симуляция алгоритма Шора для факторизации числа n
    """
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"АЛГОРИТМ ШОРА: Факторизация числа {n}")
        print(f"{'=' * 60}\n")
    
    # Шаг 0: Проверка на простоту
    if is_prime(n):
        if verbose:
            print(f"Число {n} простое, факторизация не требуется.")
        return None
    
    # Если n четное
    if n % 2 == 0:
        if verbose:
            print(f"Число {n} четное: {n} = 2 × {n // 2}")
        return (2, n // 2)
    
    # Проверка тривиальных делителей (для маленьких чисел)
    trivial = factorize_trivial(n)
    if trivial:
        if verbose:
            print(f"Найден тривиальный делитель: {n} = {trivial[0]} × {trivial[1]}")
        return trivial
    
    for attempt in range(1, max_attempts + 1):
        if verbose:
            print(f"\n--- Попытка {attempt} ---")
        
        # Шаг 1: Выбираем случайное a (1 < a < n, взаимно простое)
        a = random_coprime(n)
        if verbose:
            print(f"  Выбрано a = {a}")
        
        # Проверка: если a^(n-1)/2 ≡ ±1 mod n, возможно быстрое решение
        # (для простоты пропускаем, но можно добавить)
        
        # Шаг 2: Определяем m такое, что n^2 ≤ 2^m < 2n
        m = 0
        while 2 ** m < n ** 2:
            m += 1
        # Корректируем, чтобы не было слишком больших вычислений
        m = min(m, 12)  # Ограничиваем для скорости (2^12 = 4096)
        
        N_states = 2 ** m
        if verbose:
            print(f"  m = {m}, количество состояний = {N_states}")
        
        # Шаг 3: Создаем суперпозицию всех |x⟩
        superposition = create_superposition(m)
        
        # Шаг 4: Применяем f(x) = a^x mod n
        function_results = apply_function(superposition, a, n)
        
        # Шаг 5: Выбираем случайное значение f(x) для измерения
        # (в реальном QC это случайно, мы эмулируем)
        f_values = list(function_results.values())
        target_f = random.choice(f_values)
        
        if verbose:
            print(f"  Измерение: выбрано f(x) = {target_f}")
        
        # Шаг 6: Коллапс в подпространство с f(x) = target_f
        selected_x = measure_state(function_results, target_f)
        
        if len(selected_x) < 2:
            if verbose:
                print("  Недостаточно состояний для измерения периода.")
            continue
        
        if verbose:
            print(f"  Найдено {len(selected_x)} состояний с f(x) = {target_f}")
            # Показываем только первые 5 для читаемости
            sample = selected_x[:5]
            if len(selected_x) > 5:
                sample.append("...")
            print(f"  x: {sample}")
        
        # Шаг 7: Строим индикаторную последовательность для DFT
        # (1 в позициях выбранных x, 0 в остальных)
        sequence = [0] * N_states
        for x in selected_x:
            sequence[x] = 1
        
        # Шаг 8: Выполняем DFT (симуляция QFT)
        if verbose:
            print("  Выполняется преобразование Фурье...")
        
        dft_result = dft(sequence)
        
        # Шаг 9: Находим период из DFT
        r = find_period_from_dft(dft_result, m)
        
        if r is None:
            if verbose:
                print("  Не удалось найти период.")
            continue
        
        if verbose:
            print(f"  Найден период r = {r}")
        
        # Шаг 10: Проверка периода
        # Должно быть: a^r ≡ 1 (mod n)
        check = modular_exponentiation(a, r, n)
        if check != 1:
            if verbose:
                print(f"  Проверка: a ^ {r} mod {n} = {check} ≠ 1, неверный период.")
            continue
        
        if verbose:
            print(f"  Проверка: a ^ {r} ≡ 1 (mod {n}) ✓")
        
        # Шаг 11: Если r нечетное, пытаемся снова
        if r % 2 != 0:
            if verbose:
                print("  Период r нечетный, нужна другая попытка.")
            continue
        
        # Шаг 12: Вычисляем a^(r/2) ± 1 и находим НОД
        half_r = r // 2
        a_half = modular_exponentiation(a, half_r, n)
        
        if a_half % n == n - 1:
            if verbose:
                print(f"  a ^ {half_r} ≡ -1 (mod {n}), тривиальный случай.")
            continue
        
        factor1 = gcd(a_half - 1, n)
        factor2 = gcd(a_half + 1, n)
        
        if verbose:
            print(f"  a ^ {half_r} mod {n} = {a_half}")
            print(f"  НОД({a_half - 1}, {n}) = {factor1}")
            print(f"  НОД({a_half + 1}, {n}) = {factor2}")
        
        # Шаг 13: Проверяем, что получили нетривиальные делители
        if factor1 not in (1, n) and factor2 not in (1, n):
            if factor1 * factor2 == n:
                if verbose:
                    print(f"\n✓ УСПЕХ! {n} = {factor1} × {factor2}")
                return (factor1, factor2)
            else:
                # Иногда один из делителей равен 1, но другой дает n
                # Проверяем оба варианта
                if factor1 != 1 and factor1 != n:
                    other = n // factor1
                    if other != 1 and other != n:
                        if verbose:
                            print(f"\n✓ УСПЕХ! {n} = {factor1} × {other}")
                        return (factor1, other)
                if factor2 != 1 and factor2 != n:
                    other = n // factor2
                    if other != 1 and other != n:
                        if verbose:
                            print(f"\n✓ УСПЕХ! {n} = {factor2} × {other}")
                        return (factor2, other)
        else:
            if verbose:
                print("  Получены тривиальные делители, нужна другая попытка.")
    
    if verbose:
        print(f"\nНе удалось факторизовать {n} за {max_attempts} попыток.")
    return None


# =====================================================
# ТЕСТОВЫЙ ЗАПУСК
# =====================================================

def demo():
    """Демонстрация работы алгоритма на нескольких числах"""
    test_numbers = [15, 21, 33, 35, 77, 91]
    
    print("=" * 60)
    print("СИМУЛЯЦИЯ АЛГОРИТМА ШОРА (КЛАССИЧЕСКАЯ ВЕРСИЯ)")
    print("=" * 60)
    print("\nПримечание: Это классическая симуляция, которая эмулирует")
    print("квантовые операции через DFT на списках. Реальный квантовый")
    print("компьютер делает это за O(poly(log N)), а не O(N log N).")
    print("Но логика и шаги алгоритма полностью соответствуют тексту.\n")
    
    for n in test_numbers:
        factors = shor_algorithm(n, max_attempts = 8, verbose = True)
        if factors:
            print(f"\n✅ РЕЗУЛЬТАТ: {n} = {factors[0]} × {factors[1]}")
        else:
            print(f"\n❌ Не удалось факторизовать {n}")


# =====================================================
# ИНТЕРАКТИВНЫЙ РЕЖИМ
# =====================================================

def interactive():
    """Интерактивный режим для ввода пользователя"""
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nВведите число для факторизации (или 'exit' для выхода): ")
            if user_input.lower() in ('exit', 'quit', 'q'):
                break
            
            n = int(user_input)
            if n < 2:
                print("Число должно быть >= 2")
                continue
            
            factors = shor_algorithm(n, max_attempts = 10, verbose = True)
            if factors:
                print(f"\n✅ {n} = {factors[0]} × {factors[1]}")
            else:
                print(f"\n❌ Не удалось факторизовать {n}")
                
        except ValueError:
            print("Пожалуйста, введите целое число.")
        except KeyboardInterrupt:
            print("\nВыход...")
            break


# =====================================================
# ЗАПУСК
# =====================================================

if __name__ == "__main__":
    # Запускаем демонстрацию
    demo()
    
    # Раскомментируйте следующую строку для интерактивного режима
    # interactive()