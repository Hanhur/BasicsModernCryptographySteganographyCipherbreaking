# Первая система с открытым ключом — система Диффи–Хеллмана
"""
Реализация протокола Диффи-Хеллмана
Основано на тексте: "2.2. Первая система с открытым ключом — система Диффи–Хеллмана"
"""

import random
import math


def is_prime(n: int) -> bool:
    """Проверка числа на простоту (базовый тест)"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Быстрое возведение в степень по модулю: (base^exponent) % modulus
    Используется встроенная функция pow(), которая делает то же самое эффективно
    """
    return pow(base, exponent, modulus)


def find_primitive_root(p: int) -> int:
    """
    Находит первообразный корень g для простого числа p.
    Использует подход из текста: p = 2 * q + 1, где q - тоже простое.
    """
    if not is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    
    # Проверяем, что p = 2 * q + 1 (безопасное простое)
    q = (p - 1) // 2
    if not is_prime(q):
        raise ValueError(f"{p} не является безопасным простым (p-1) / 2 = {q} не является простым числом")
    
    print(f"p = {p} = 2*{q} + 1, где {q} - простое число")
    
    # Перебираем возможные g от 2 до p-2
    for g in range(2, p - 1):
        # Проверяем условие из текста: g^q mod p != 1
        if mod_pow(g, q, p) != 1:
            print(f"Найден подходящий g = {g}")
            return g
    
    raise RuntimeError("Не удалось найти первообразный корень")


def generate_keys(p: int, g: int) -> tuple:
    """
    Генерирует пару ключей для одного абонента.
    Возвращает: (секретный_ключ_X, открытый_ключ_Y)
    """
    # X - секретное число (выбирается случайно)
    X = random.randint(2, p - 2)
    # Y = g^X mod p
    Y = mod_pow(g, X, p)
    return X, Y


def compute_shared_secret(my_secret_X: int, other_public_Y: int, p: int) -> int:
    """
    Вычисляет общий секретный ключ:
    Z = (Y_other)^X_my mod p
    """
    return mod_pow(other_public_Y, my_secret_X, p)


def find_safe_prime(bits: int = 8) -> int:
    """
    Находит безопасное простое число p = 2 * q + 1, где q тоже простое.
    bits - количество бит для числа p (по умолчанию 8 бит для демонстрации)
    """
    min_value = 2 ** (bits - 1)
    max_value = 2 ** bits
    
    # Начинаем с случайного числа в нужном диапазоне
    for _ in range(1000):  # Ограничиваем количество попыток
        q = random.randint(min_value // 2, max_value // 2)
        if not is_prime(q):
            continue
        p = 2 * q + 1
        if is_prime(p):
            return p
    raise RuntimeError("Не удалось найти безопасное простое число")


def demo_diffie_hellman():
    """Демонстрация работы протокола Диффи-Хеллмана"""
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА ДИФФИ-ХЕЛЛМАНА")
    print("=" * 60)
    
    # Шаг 1: Выбор публичных параметров (как в примере 2.2 из текста)
    print("\n[Шаг 1] Выбор публичных параметров")
    print("-" * 40)
    
    # Используем параметры из примера 2.2: p = 23, g = 5
    p = 23
    print(f"Выбрано простое число p = {p}")
    
    # Находим g по алгоритму из текста
    g = find_primitive_root(p)
    print(f"Выбран параметр g = {g}")
    print(f"Публичные параметры (p, g) = ({p}, {g}) известны всем")
    
    # Шаг 2: Каждый абонент выбирает секретное число
    print("\n[Шаг 2] Генерация секретных ключей абонентами")
    print("-" * 40)
    
    # Используем значения из примера 2.2
    XA = 7
    XB = 13
    print(f"Секретный ключ A: XA = {XA} (хранится в тайне)")
    print(f"Секретный ключ B: XB = {XB} (хранится в тайне)")
    
    # Шаг 3: Вычисление открытых ключей
    print("\n[Шаг 3] Вычисление открытых ключей")
    print("-" * 40)
    
    YA = mod_pow(g, XA, p)
    YB = mod_pow(g, XB, p)
    
    print(f"YA = {g} ^ {XA} mod {p} = {YA} (открыто передаётся всем)")
    print(f"YB = {g} ^ {XB} mod {p} = {YB} (открыто передаётся всем)")
    
    # Шаг 4: Обмен открытыми ключами и вычисление общего секрета
    print("\n[Шаг 4] Вычисление общего секретного ключа")
    print("-" * 40)
    
    # Абонент A вычисляет ZAB = (YB)^XA mod p
    ZAB = compute_shared_secret(XA, YB, p)
    print(f"A вычисляет ZAB = {YB} ^ {XA} mod {p} = {ZAB}")
    
    # Абонент B вычисляет ZBA = (YA)^XB mod p
    ZBA = compute_shared_secret(XB, YA, p)
    print(f"B вычисляет ZBA = {YA} ^ {XB} mod {p} = {ZBA}")
    
    # Проверка совпадения
    print("\n[Результат]")
    print("-" * 40)
    print(f"ZAB = {ZAB}")
    print(f"ZBA = {ZBA}")
    
    if ZAB == ZBA:
        print(f"✓ КЛЮЧИ СОВПАЛИ! Общий секретный ключ: {ZAB}")
        print(f"  (Совпадает с примером 2.2, где ключ = 10)")
    else:
        print("✗ ОШИБКА: ключи не совпали!")
    
    # Шаг 5: Демонстрация того, что Ева не может вычислить ключ
    print("\n[Безопасность]")
    print("-" * 40)
    print("Ева видит в открытом канале только:")
    print(f"  p = {p}")
    print(f"  g = {g}")
    print(f"  YA = {YA}")
    print(f"  YB = {YB}")
    print("Но Ева НЕ ЗНАЕТ XA и XB, поэтому не может вычислить Z.")
    print("Для вычисления XA нужно решить задачу дискретного логарифма:")
    print(f"  {YA} = {g} ^ XA mod {p}")
    print("При больших p это практически невозможно.")


def demo_with_large_numbers():
    """Демонстрация с большими числами для реальной стойкости"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С БОЛЬШИМИ ЧИСЛАМИ")
    print("=" * 60)
    
    # Находим безопасное простое число
    # Используем 10-битные числа для демонстрации (в реальности 2048+ бит)
    print("Поиск безопасного простого числа...")
    p = find_safe_prime(bits = 10)
    print(f"Найдено безопасное простое число p = {p}")
    
    q = (p - 1) // 2
    print(f"p = 2 * {q} + 1, где {q} - простое число")
    
    # Находим g
    g = find_primitive_root(p)
    print(f"Найден первообразный корень g = {g}")
    print(f"Публичные параметры: p = {p}, g = {g}")
    
    # Генерируем ключи
    print("\nГенерация ключей для 3 абонентов A, B, C...")
    XA, YA = generate_keys(p, g)
    XB, YB = generate_keys(p, g)
    XC, YC = generate_keys(p, g)
    
    print(f"Секретные ключи (не передаются):")
    print(f"  XA = {XA}")
    print(f"  XB = {XB}")
    print(f"  XC = {XC}")
    print(f"\nОткрытые ключи (передаются по каналу):")
    print(f"  YA = {YA}")
    print(f"  YB = {YB}")
    print(f"  YC = {YC}")
    
    # Вычисляем общие ключи для всех пар
    print("\nВычисление общих ключей для всех пар:")
    print("-" * 40)
    
    Z_AB = compute_shared_secret(XA, YB, p)
    Z_BA = compute_shared_secret(XB, YA, p)
    print(f"A и B: Z = {Z_AB} (проверка: B получил {Z_BA})")
    
    Z_AC = compute_shared_secret(XA, YC, p)
    Z_CA = compute_shared_secret(XC, YA, p)
    print(f"A и C: Z = {Z_AC} (проверка: C получил {Z_CA})")
    
    Z_BC = compute_shared_secret(XB, YC, p)
    Z_CB = compute_shared_secret(XC, YB, p)
    print(f"B и C: Z = {Z_BC} (проверка: C получил {Z_BC})")
    
    # Проверка: ключи для разных пар разные
    print("\nВажно: ключи для разных пар уникальны")
    print(f"Z_AB = {Z_AB}")
    print(f"Z_AC = {Z_AC}")
    print(f"Z_BC = {Z_BC}")
    
    unique_keys = {Z_AB, Z_AC, Z_BC}
    print(f"Количество уникальных ключей: {len(unique_keys)} из 3")
    
    # Статистика масштабирования
    print("\n[Статистика масштабирования]")
    print("-" * 40)
    print("Количество ключей при симметричном подходе:")
    for N in [10, 100, 1000]:
        keys_needed = N * (N - 1) // 2
        print(f"  Для N = {N} абонентов: {keys_needed} ключей")
    print("\nВ протоколе Диффи-Хеллмана каждый абонент хранит:")
    print("  - 1 секретный ключ (личный)")
    print("  - N-1 открытых ключей (других абонентов)")
    print("  - 1 публичный параметр g")
    print("  - Всего ~N ключей на систему, вместо N²/2")


def list_safe_primes():
    """Выводит список безопасных простых чисел для демонстрации"""
    print("\n" + "=" * 60)
    print("СПИСОК БЕЗОПАСНЫХ ПРОСТЫХ ЧИСЕЛ ДЛЯ ДЕМОНСТРАЦИИ")
    print("=" * 60)
    
    safe_primes = []
    # Проверяем числа до 500
    for q in range(2, 250):
        if is_prime(q):
            p = 2 * q + 1
            if is_prime(p):
                safe_primes.append((p, q))
    
    print("Безопасные простые числа p = 2q + 1 (где q - простое):")
    for p, q in safe_primes[:10]:  # Показываем первые 10
        print(f"  p = {p} (q = {q})")
    
    print(f"\nВсего найдено {len(safe_primes)} безопасных простых чисел до 500")
    print("\nДля реальных систем используются p размером 2048-4096 бит")


if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов
    random.seed(42)
    
    # Запускаем основную демонстрацию (на примере из текста)
    demo_diffie_hellman()
    
    # Дополнительная демонстрация с большими числами
    demo_with_large_numbers()
    
    # Показываем список безопасных простых чисел
    list_safe_primes()
    
    print("\n" + "=" * 60)
    print("Программа завершена.")
    print("=" * 60)