# Последняя теорема Ферма, простые числа и модульная арифметика
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЕДИНАЯ ПРОГРАММА: Математические основы криптографии
Основана на тексте о последней теореме Ферма, простых числах и модульной арифметике

Автор: Объединенная версия всех демонстрационных программ
Дата: 2026
"""

import random
import time
from typing import List, Tuple, Optional

# ====================================================================
# БЛОК 1: РАБОТА С ПРОСТЫМИ ЧИСЛАМИ
# ====================================================================

def is_prime_trial(n: int) -> bool:
    """
    Проверка простоты числа методом пробного деления.
    Точный метод, но медленный для больших чисел.
    
    Аргументы:
        n: проверяемое число
    
    Возвращает:
        True, если число простое, иначе False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Вероятностный тест простоты Ферма.
    Основан на малой теореме Ферма: a ^ (n - 1) ≡ 1 (mod n)
    
    Аргументы:
        n: проверяемое число
        k: количество раундов тестирования (чем больше, тем точнее)
    
    Возвращает:
        True, если число вероятно простое, иначе False
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        if pow(a, n - 1, n) != 1:
            return False
    return True

def generate_prime(bits: int = 16, max_attempts: int = 1000) -> Optional[int]:
    """
    Генерация случайного простого числа заданной битности.
    
    Аргументы:
        bits: количество бит для числа
        max_attempts: максимальное количество попыток
    
    Возвращает:
        Сгенерированное простое число или None
    """
    if bits < 2:
        return None
    
    for _ in range(max_attempts):
        # Генерируем нечетное число нужной битности
        n = random.getrandbits(bits)
        # Убеждаемся, что число имеет нужную битность
        n |= (1 << (bits - 1))  # Старший бит = 1
        n |= 1  # Младший бит = 1 (нечетное)
        
        if is_prime_fermat(n, k = 10):
            return n
    return None

# ====================================================================
# БЛОК 2: ЧИСЛА ФЕРМА И МЕРСЕННА
# ====================================================================

def fermat_number(n: int) -> int:
    """
    Вычисляет число Ферма: F_n = 2 ^ (2 ^ n) + 1
    
    Аргументы:
        n: индекс числа Ферма
    
    Возвращает:
        Значение F_n
    """
    return 2 ** (2 ** n) + 1

def mersenne_number(n: int) -> int:
    """
    Вычисляет число Мерсенна: M_n = 2 ^ n - 1
    
    Аргументы:
        n: индекс числа Мерсенна
    
    Возвращает:
        Значение M_n
    """
    return (2 ** n) - 1

def find_primes_in_sequence(sequence_func, max_n: int, name: str) -> List[Tuple[int, int]]:
    """
    Находит простые числа в заданной последовательности.
    
    Аргументы:
        sequence_func: функция, вычисляющая n-й член последовательности
        max_n: максимальное количество членов для проверки
        name: название последовательности (для вывода)
    
    Возвращает:
        Список кортежей (n, простое_число)
    """
    primes = []
    print(f"\nПоиск простых чисел в последовательности {name}:")
    print("-" * 50)
    
    for n in range(1, max_n + 1):
        num = sequence_func(n)
        is_prime = is_prime_trial(num)
        status = "✓ ПРОСТОЕ" if is_prime else "  составное"
        print(f"  {name}_{n:2} = {num:>20} -> {status}")
        if is_prime:
            primes.append((n, num))
    
    return primes

# ====================================================================
# БЛОК 3: МОДУЛЬНАЯ АРИФМЕТИКА
# ====================================================================

def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Находит обратный элемент a по модулю m.
    Использует расширенный алгоритм Евклида.
    
    Аргументы:
        a: число
        m: модуль
    
    Возвращает:
        x такой, что (a * x) % m == 1, или None если не существует
    """
    def extended_gcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, x1, y1 = extended_gcd(b % a, a)
        return (g, y1 - (b // a) * x1, x1)
    
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None  # Обратного элемента не существует
    return x % m

def modular_clock_demo() -> None:
    """Демонстрация модульной арифметики на примере часов (mod 12)"""
    print("\n" + "=" * 70)
    print("МОДУЛЬНАЯ АРИФМЕТИКА (аналогия с часами)")
    print("=" * 70)
    
    print("\n📌 Основная идея: 13 ≡ 1 (mod 12) потому что 13 часов = 1 час на циферблате")
    
    examples = [
        (13, 1, 12, "13 часов = 1 час"),
        (25, 1, 12, "25 часов = 1 час"),
        (37, 1, 12, "37 часов = 1 час"),
        (14, 2, 12, "14 часов = 2 часа"),
        (23, 11, 12, "23 часа = 11 часов"),
        (48, 12, 12, "48 часов = 12 часов"),
        (100, 4, 12, "100 часов = 4 часа")
    ]
    
    print("\nПримеры сравнений по модулю 12:")
    print("-" * 65)
    print(f"{'a':^6} | {'b':^6} | {'mod':^6} | {'a mod mod':^12} | {'b mod mod':^12} | {'Совпадение'}")
    print("-" * 65)
    
    for a, b, mod, desc in examples:
        a_mod = a % mod
        b_mod = b % mod
        match = "✓" if a_mod == b_mod else "✗"
        print(f"{a:^6} | {b:^6} | {mod:^6} | {a_mod:^12} | {b_mod:^12} | {match:^10} ({desc})")

def modular_operations_demo() -> None:
    """Демонстрация операций в модульной арифметике"""
    print("\n" + "=" * 70)
    print("ОПЕРАЦИИ В МОДУЛЬНОЙ АРИФМЕТИКЕ")
    print("=" * 70)
    
    mod = 7
    a, b = 15, 23
    
    print(f"\nИсходные данные: a = {a}, b = {b}, mod = {mod}")
    print("-" * 60)
    print(f"a + b = {a} + {b} = {a + b} ≡ {(a + b) % mod} (mod {mod})")
    print(f"a - b = {a} - {b} = {a - b} ≡ {(a - b) % mod} (mod {mod})")
    print(f"a * b = {a} * {b} = {a * b} ≡ {(a * b) % mod} (mod {mod})")
    print(f"a^b   = {a} ^ {b} ≡ {pow(a, b, mod)} (mod {mod})")
    
    inv = mod_inverse(a, mod)
    if inv:
        print(f"\nОбратный элемент к {a} по модулю {mod}: {inv}")
        print(f"Проверка: {a} * {inv} = {a * inv} ≡ {(a * inv) % mod} (mod {mod}) ✓")
    else:
        print(f"\n{a} не имеет обратного элемента по модулю {mod} (не взаимно прост с {mod})")

def mod_power_demo() -> None:
    """Демонстрация возведения в степень по модулю"""
    print("\n" + "=" * 70)
    print("ВОЗВЕДЕНИЕ В СТЕПЕНЬ ПО МОДУЛЮ")
    print("=" * 70)
    
    base = 2
    exponent = 10
    mod = 1000
    
    print(f"\nВычисление {base}^{exponent} (mod {mod})")
    print("-" * 60)
    
    # Обычное вычисление (может быть огромным)
    normal = base ** exponent
    print(f"Обычное вычисление: {base} ^ {exponent} = {normal}")
    print(f"  Результат по модулю: {normal % mod}")
    
    # Вычисление с помощью pow (эффективно)
    modular = pow(base, exponent, mod)
    print(f"Модульное возведение: {base} ^ {exponent} ≡ {modular} (mod {mod})")
    print(f"  (используется в криптографии для работы с огромными числами)")

# ====================================================================
# БЛОК 4: МАЛАЯ ТЕОРЕМА ФЕРМА
# ====================================================================

def fermat_little_theorem_demo() -> None:
    """Демонстрация малой теоремы Ферма"""
    print("\n" + "=" * 70)
    print("МАЛАЯ ТЕОРЕМА ФЕРМА")
    print("=" * 70)
    
    print("\n📌 Формулировка: если p - простое число, то для любого целого a")
    print("   a ^ p ≡ a (mod p) или a ^ (p - 1) ≡ 1 (mod p)")
    
    examples = [
        (2, 3),
        (3, 5),
        (4, 7),
        (5, 11),
        (2, 13)
    ]
    
    print("\nПримеры:")
    print("-" * 65)
    print(f"{'a':^6} | {'p':^6} | {'a^p mod p':^15} | {'a mod p':^12} | {'Совпадает?'}")
    print("-" * 65)
    
    for a, p in examples:
        result = pow(a, p, p)
        a_mod = a % p
        match = "✓" if result == a_mod else "✗"
        print(f"{a:^6} | {p:^6} | {result:^15} | {a_mod:^12} | {match:^10}")

def primality_test_comparison() -> None:
    """Сравнение методов проверки простоты"""
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ МЕТОДОВ ПРОВЕРКИ ПРОСТОТЫ")
    print("=" * 70)
    
    test_numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 67, 257, 65537, 1009, 4, 6, 8, 9, 10, 15, 21, 25, 27, 33, 49, 65]
    
    print("\nТестирование чисел:")
    print("-" * 70)
    print(f"{'Число':^8} | {'Точный метод':^18} | {'Тест Ферма':^18} | {'Совпадает?'}")
    print("-" * 70)
    
    for num in test_numbers:
        trial_result = is_prime_trial(num)
        fermat_result = is_prime_fermat(num, k=5)
        match = "✓" if trial_result == fermat_result else "✗"
        print(f"{num:^8} | {str(trial_result):^18} | {str(fermat_result):^18} | {match:^10}")

# ====================================================================
# БЛОК 5: ПОСЛЕДНЯЯ ТЕОРЕМА ФЕРМА
# ====================================================================

def check_fermat_last_theorem(max_a: int = 3, max_b: int = 3, max_c: int = 3, max_n: int = 5) -> None:
    """
    Проверяет последнюю теорему Ферма для заданных диапазонов.
    
    Аргументы:
        max_a, max_b, max_c: максимальные значения для a, b, c
        max_n: максимальное значение для n
    """
    print("\n" + "=" * 70)
    print("ПОСЛЕДНЯЯ ТЕОРЕМА ФЕРМА")
    print("=" * 70)
    
    print("\n📌 Формулировка: для любого целого n > 2")
    print("   уравнение a ^ n + b ^ n = c ^ n не имеет решений в целых ненулевых числах")
    
    print(f"\nПроверка для a, b, c ∈ [1, {max_a}] и n ∈ [3, {max_n}]")
    print("-" * 70)
    
    total_checks = 0
    counterexamples = []
    
    for n in range(3, max_n + 1):
        print(f"\nПроверка для n = {n}:")
        found_for_n = False
        
        for a in range(1, max_a + 1):
            for b in range(1, max_b + 1):
                for c in range(1, max_c + 1):
                    total_checks += 1
                    left = a ** n + b ** n
                    right = c ** n
                    
                    if left == right:
                        counterexamples.append((a, b, c, n))
                        found_for_n = True
                        print(f"  ❗ НАЙДЕН КОНТРПРИМЕР: {a} ^ {n} + {b} ^ {n} = {c} ^ {n}")
        
        if not found_for_n:
            print(f"  ✓ Контрпримеров не найдено для n = {n} (теорема подтверждается)")
    
    print(f"\nВсего проверено комбинаций: {total_checks}")
    print(f"Найдено контрпримеров: {len(counterexamples)}")
    
    if not counterexamples:
        print("✅ Теорема подтверждена для заданных диапазонов!")
    else:
        print("❌ Найдены контрпримеры (что невозможно по теореме)!")

def fermat_demonstration_small() -> None:
    """Наглядная демонстрация теоремы для малых чисел"""
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ТЕОРЕМЫ ДЛЯ МАЛЫХ ЧИСЕЛ")
    print("=" * 70)
    
    # Для n=2 (есть решения - пифагоровы тройки)
    print("\n📐 Для n = 2 (ЕСТЬ решения - пифагоровы тройки):")
    print("-" * 60)
    pythagorean_triples = [
        (3, 4, 5),
        (5, 12, 13),
        (6, 8, 10),
        (8, 15, 17),
        (7, 24, 25),
        (9, 40, 41)
    ]
    
    for a, b, c in pythagorean_triples[:5]:
        print(f"  {a}² + {b}² = {a ** 2} + {b ** 2} = {c ** 2} = {c}²  ✓")
    
    print(f"  ... и так далее (бесконечно много решений)")
    
    # Для n=3 (нет решений)
    print("\n📐 Для n = 3 (НЕТ решений):")
    print("-" * 60)
    test_cases = [(1, 2, 3), (2, 3, 4), (3, 4, 5), (1, 1, 2)]
    
    for a, b, c in test_cases:
        left = a ** 3 + b ** 3
        right = c ** 3
        sign = "=" if left == right else "≠"
        print(f"  {a}³ + {b}³ = {left} {sign} {right} = {c}³")
    
    print("  ✓ Ни одно из проверенных чисел не удовлетворяет уравнению")
    
    # Для простых чисел p > 2
    print("\n📐 Для простых чисел p > 2 (по теореме):")
    print("-" * 60)
    a, b, c = 2, 3, 4
    
    for p in [3, 5, 7]:
        left = a ** p + b ** p
        right = c ** p
        sign = "=" if left == right else "≠"
        print(f"  {a} ^ {p} + {b} ^ {p} = {left} {sign} {right} = {c} ^ {p}")

# ====================================================================
# БЛОК 6: ПРИМЕНЕНИЕ В КРИПТОГРАФИИ
# ====================================================================

def crypto_application_demo() -> None:
    """Демонстрация применения в криптографии"""
    print("\n" + "=" * 70)
    print("ПРИМЕНЕНИЕ В КРИПТОГРАФИИ")
    print("=" * 70)
    
    print("\n🔐 Почему простые числа важны для криптографии?")
    print("-" * 70)
    print("1. Легко перемножить два больших простых числа")
    print("2. Очень трудно разложить произведение на множители (факторизовать)")
    print("3. Эта асимметрия используется в RSA и других алгоритмах")
    
    # Генерация ключей RSA (упрощенная демонстрация)
    print("\n🔑 Упрощенная демонстрация генерации ключей RSA:")
    print("-" * 70)
    
    # Генерируем два простых числа (маленьких для демонстрации)
    print("1. Генерируем два простых числа p и q:")
    p = generate_prime(8)  # 8-битные числа для демонстрации
    q = generate_prime(8)
    
    if p and q:
        print(f"   p = {p} (простое)")
        print(f"   q = {q} (простое)")
        
        n = p * q
        print(f"\n2. Вычисляем модуль n = p * q = {p} * {q} = {n}")
        
        phi = (p - 1) * (q - 1)
        print(f"   φ(n) = (p - 1)(q - 1) = {p - 1} * {q - 1} = {phi}")
        
        # Выбираем e (обычно 65537 или небольшое число)
        e = 17
        if e < phi and mod_inverse(e, phi):
            print(f"\n3. Выбираем открытую экспоненту e = {e}")
            
            d = mod_inverse(e, phi)
            print(f"   Вычисляем закрытую экспоненту d = {d}")
            print(f"   (проверка: {e} * {d} = {e * d} ≡ {(e * d) % phi} (mod {phi}))")
            
            print(f"\n📋 Открытый ключ: (n = {n}, e = {e})")
            print(f"🔒 Закрытый ключ: (n = {n}, d = {d})")
            
            # Шифрование и дешифрование
            message = 42
            print(f"\n4. Пример шифрования сообщения m = {message}:")
            
            encrypted = pow(message, e, n)
            print(f"   Зашифрованное сообщение: c = m ^ e mod n = {message} ^ {e} mod {n} = {encrypted}")
            
            decrypted = pow(encrypted, d, n)
            print(f"   Расшифрованное сообщение: m = c ^ d mod n = {encrypted} ^ {d} mod {n} = {decrypted}")
            
            if message == decrypted:
                print("   ✅ Шифрование и дешифрование работают корректно!")
            else:
                print("   ❌ Ошибка в шифровании/дешифровании")
        else:
            print(f"   {e} не подходит как открытая экспонента")
    else:
        print("   Не удалось сгенерировать простые числа")

# ====================================================================
# БЛОК 7: ИНФОРМАЦИЯ О ПРОСТЫХ ЧИСЛАХ
# ====================================================================

def prime_info_demo() -> None:
    """Информация о простых числах"""
    print("\n" + "=" * 70)
    print("ИНТЕРЕСНЫЕ ФАКТЫ О ПРОСТЫХ ЧИСЛАХ")
    print("=" * 70)
    
    # Поиск простых чисел в диапазоне
    print("\n🔢 Простые числа до 100:")
    primes = [str(i) for i in range(2, 101) if is_prime_trial(i)]
    for i in range(0, len(primes), 10):
        print(f"  {' '.join(primes[i:i + 10])}")
    
    # Количество простых чисел
    print("\n📊 Количество простых чисел в диапазонах:")
    ranges = [(1, 10), (1, 50), (1, 100), (1, 1000)]
    for start, end in ranges:
        count = sum(1 for i in range(start, end + 1) if is_prime_trial(i))
        print(f"  От {start} до {end}: {count} простых чисел")
    
    # Расстояние между простыми числами
    print("\n📏 Расстояние между простыми числами:")
    primes_list = [i for i in range(2, 50) if is_prime_trial(i)]
    gaps = []
    for i in range(1, len(primes_list)):
        gaps.append(primes_list[i] - primes_list[i - 1])
    
    for i in range(len(gaps)):
        print(f"  {primes_list[i]} -> {primes_list[i + 1]}: разница {gaps[i]}")

# ====================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ====================================================================

def main() -> None:
    """Главная функция программы"""
    print("\n" + "=" * 70)
    print("МАТЕМАТИЧЕСКИЕ ОСНОВЫ КРИПТОГРАФИИ")
    print("Последняя теорема Ферма, простые числа и модульная арифметика")
    print("=" * 70)
    print("\nПрограмма демонстрирует ключевые математические концепции,")
    print("используемые в современной криптографии.")
    
    # Меню для навигации (или автоматический запуск всех блоков)
    print("\n" + "=" * 70)
    print("ЗАПУСК ВСЕХ ДЕМОНСТРАЦИОННЫХ БЛОКОВ")
    print("=" * 70)
    
    # Блок 1: Простые числа
    print("\n" + "=" * 70)
    print("БЛОК 1: ПРОВЕРКА ПРОСТЫХ ЧИСЕЛ")
    print("=" * 70)
    
    test_numbers = [7, 11, 13, 17, 19, 23, 29, 31, 67, 257, 4, 6, 8, 9, 10, 15, 21, 25, 49, 65]
    print("\nТестирование чисел на простоту:")
    print("-" * 50)
    for num in test_numbers:
        is_prime = is_prime_trial(num)
        status = "ПРОСТОЕ" if is_prime else "составное"
        print(f"  {num:4} -> {status}")
    
    # Блок 2: Числа Ферма и Мерсенна
    print("\n" + "=" * 70)
    print("БЛОК 2: ЧИСЛА ФЕРМА И МЕРСЕННА")
    print("=" * 70)
    
    # Числа Ферма
    print("\nЧисла Ферма (первые 6):")
    print("-" * 60)
    for n in range(1, 7):
        f = fermat_number(n)
        is_prime = is_prime_trial(f)
        status = "✓ ПРОСТОЕ" if is_prime else "  составное"
        print(f"  F_{n} = {f:>20} -> {status}")
    
    # Числа Мерсенна
    print("\nЧисла Мерсенна (первые 12):")
    print("-" * 60)
    for n in range(1, 13):
        m = mersenne_number(n)
        is_prime = is_prime_trial(m)
        status = "✓ ПРОСТОЕ" if is_prime else "  составное"
        print(f"  M_{n:2} = {m:>20} -> {status}")
    
    # Поиск простых чисел Мерсенна
    mersenne_primes = find_primes_in_sequence(mersenne_number, 20, "Мерсенна")
    if mersenne_primes:
        print(f"\nНайдено простых чисел Мерсенна: {len(mersenne_primes)}")
    
    # Блок 3: Малая теорема Ферма
    fermat_little_theorem_demo()
    primality_test_comparison()
    
    # Блок 4: Модульная арифметика
    modular_clock_demo()
    modular_operations_demo()
    mod_power_demo()
    
    # Блок 5: Последняя теорема Ферма
    fermat_demonstration_small()
    check_fermat_last_theorem(max_a = 3, max_b = 3, max_c = 3, max_n = 5)
    
    # Блок 6: Информация о простых числах
    prime_info_demo()
    
    # Блок 7: Применение в криптографии
    crypto_application_demo()
    
    # Заключение
    print("\n" + "=" * 70)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 70)
    print("\nПрограмма продемонстрировала ключевые математические концепции:")
    print("  1. Простые числа - основа криптографии")
    print("  2. Малая теорема Ферма - основа тестов простоты")
    print("  3. Модульная арифметика - основа вычислений в криптографии")
    print("  4. Последняя теорема Ферма - связана с эллиптическими кривыми")
    print("  5. Числа Ферма и Мерсенна - источники больших простых чисел")
    print("\nВсе эти концепции используются в современных криптосистемах.")
    print("\n" + "=" * 70)
    print("Программа завершена.")
    print("=" * 70)

# ====================================================================
# ЗАПУСК ПРОГРАММЫ
# ====================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\n\nПроизошла ошибка: {e}")
        import traceback
        traceback.print_exc()