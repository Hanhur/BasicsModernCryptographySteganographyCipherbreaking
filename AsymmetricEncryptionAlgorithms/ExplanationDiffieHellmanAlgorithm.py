# Объяснение алгоритма Диффи — Хеллмана
"""
Алгоритм Диффи-Хеллмана (Diffie-Hellman Key Exchange)
Реализация на чистом Python без использования numpy
"""

import random


def is_prime(n: int) -> bool:
    """Проверка числа на простоту (базовый тест)"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Проверка делителей до квадратного корня
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def find_primitive_root(p: int) -> int:
    """
    Поиск первообразного корня (генератора) по модулю p
    Упрощенная версия для небольших чисел
    """
    if not is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    
    # Для простоты проверяем числа от 2 до p-1
    for g in range(2, p):
        # Проверяем, что g^(p-1)/q != 1 для всех простых делителей q числа p-1
        factors = []
        n = p - 1
        d = 2
        while d * d <= n:
            if n % d == 0:
                factors.append(d)
                while n % d == 0:
                    n //= d
            d += 1
        if n > 1:
            factors.append(n)
        
        is_primitive = True
        for factor in factors:
            if pow(g, (p - 1) // factor, p) == 1:
                is_primitive = False
                break
        
        if is_primitive:
            return g
    
    raise ValueError(f"Не удалось найти первообразный корень для p = {p}")


def generate_private_key(p: int) -> int:
    """Генерация секретного ключа (случайное число от 2 до p - 2)"""
    return random.randint(2, p - 2)


def compute_public_key(g: int, private_key: int, p: int) -> int:
    """Вычисление открытого ключа: A = g ^ a mod p"""
    return pow(g, private_key, p)


def compute_shared_secret(public_key: int, private_key: int, p: int) -> int:
    """Вычисление общего секрета: k = B ^ a mod p"""
    return pow(public_key, private_key, p)


def diffie_hellman_exchange(p: int, g: int, a: int, b: int) -> tuple:
    """
    Полный обмен ключами с заданными параметрами
    Возвращает: (A, B, kA, kB) - открытые ключи и общие секреты
    """
    # Вычисляем открытые ключи
    A = compute_public_key(g, a, p)
    B = compute_public_key(g, b, p)
    
    # Вычисляем общие секреты
    kA = compute_shared_secret(B, a, p)
    kB = compute_shared_secret(A, b, p)
    
    return A, B, kA, kB


def demo_with_small_numbers():
    """Демонстрация с маленькими числами (как в примере из текста)"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ С МАЛЕНЬКИМИ ЧИСЛАМИ (из примера)")
    print("=" * 60)
    
    # Параметры из текста
    p = 11
    g = 7
    a = 3  # Секрет Алисы
    b = 6  # Секрет Боба
    
    print(f"Открытые параметры: p = {p}, g = {g}")
    print(f"Секрет Алисы (a) = {a}")
    print(f"Секрет Боба (b) = {b}")
    print()
    
    A, B, kA, kB = diffie_hellman_exchange(p, g, a, b)
    
    print(f"Алиса вычисляет: A = {g} ^ {a} mod {p} = {A}")
    print(f"Боб вычисляет: B = {g} ^ {b} mod {p} = {B}")
    print()
    print(f"Алиса отправляет Бобу: {A}")
    print(f"Боб отправляет Алисе: {B}")
    print()
    print(f"Алиса вычисляет: k = {B} ^ {a} mod {p} = {kA}")
    print(f"Боб вычисляет: k = {A} ^ {b} mod {p} = {kB}")
    print()
    print(f"✓ ОБЩИЙ СЕКРЕТНЫЙ КЛЮЧ: {kA}")
    print(f"✓ Ключи совпадают: {kA == kB}")
    print("=" * 60)


def demo_with_large_numbers():
    """Демонстрация с большими числами (реалистичный сценарий)"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С БОЛЬШИМИ ЧИСЛАМИ")
    print("=" * 60)
    
    # Используем простое число побольше
    p = 997  # Простое число
    g = find_primitive_root(p)
    
    print(f"Открытые параметры: p = {p}, g = {g}")
    print()
    
    # Генерируем случайные секретные ключи
    a = generate_private_key(p)
    b = generate_private_key(p)
    
    print(f"Секрет Алисы (a) = {a}")
    print(f"Секрет Боба (b) = {b}")
    print()
    
    A, B, kA, kB = diffie_hellman_exchange(p, g, a, b)
    
    print(f"Открытый ключ Алисы (A) = {A}")
    print(f"Открытый ключ Боба (B) = {B}")
    print()
    print(f"Общий секрет Алисы (kA) = {kA}")
    print(f"Общий секрет Боба (kB) = {kB}")
    print()
    print(f"✓ Ключи совпадают: {kA == kB}")
    print("=" * 60)


def simulate_man_in_the_middle():
    """Симуляция атаки "Человек посередине" (Man-in-the-Middle)"""
    print("\n" + "=" * 60)
    print("СИМУЛЯЦИЯ АТАКИ 'ЧЕЛОВЕК ПОСЕРЕДИНЕ' (MITM)")
    print("=" * 60)
    
    # Открытые параметры
    p = 23
    g = 5
    
    print(f"Открытые параметры: p = {p}, g = {g}")
    print()
    
    # Секретные ключи сторон
    a = 6   # Секрет Алисы
    b = 15  # Секрет Боба
    e = 8   # Секрет Евы (злоумышленника)
    
    print(f"Секрет Алисы (a) = {a}")
    print(f"Секрет Боба (b) = {b}")
    print(f"Секрет Евы (e) = {e}")
    print()
    
    # Вычисление открытых ключей
    A = compute_public_key(g, a, p)  # Алиса -> A
    B = compute_public_key(g, b, p)  # Боб -> B
    
    print(f"Алиса вычисляет: A = {g} ^ {a} mod {p} = {A}")
    print(f"Боб вычисляет: B = {g} ^ {b} mod {p} = {B}")
    print()
    
    # Ева перехватывает и подменяет
    E1 = compute_public_key(g, e, p)  # Ева для Алисы
    E2 = compute_public_key(g, e, p)  # Ева для Боба
    
    print("Ева перехватывает сообщения и подменяет их:")
    print(f"  Алиса отправляет {A}, но Боб получает {E1}")
    print(f"  Боб отправляет {B}, но Алиса получает {E2}")
    print()
    
    # Вычисление секретов
    k_Alice = compute_shared_secret(E2, a, p)  # Алиса думает, что говорит с Бобом
    k_Bob = compute_shared_secret(E1, b, p)    # Боб думает, что говорит с Алисой
    k_Eve_with_Alice = compute_shared_secret(A, e, p)  # Ева с Алисой
    k_Eve_with_Bob = compute_shared_secret(B, e, p)    # Ева с Бобом
    
    print(f"Алиса вычисляет: k = {E2} ^ {a} mod {p} = {k_Alice}")
    print(f"Боб вычисляет: k = {E1} ^ {b} mod {p} = {k_Bob}")
    print(f"Ева с Алисой: k = {A} ^ {e} mod {p} = {k_Eve_with_Alice}")
    print(f"Ева с Бобом: k = {B} ^ {e} mod {p} = {k_Eve_with_Bob}")
    print()
    print(f"⚠ Алиса и Боб думают, что у них общий ключ, но на самом деле:")
    print(f"  - Алиса общается с Евой (ключ {k_Alice})")
    print(f"  - Боб общается с Евой (ключ {k_Bob})")
    print(f"  - Ева читает все сообщения!")
    print("=" * 60)


def interactive_demo():
    """Интерактивная демонстрация с пользовательским вводом"""
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    
    try:
        # Ввод параметров
        p = int(input("Введите простое число p (например, 97): "))
        if not is_prime(p):
            print(f"Ошибка: {p} не является простым числом!")
            return
        
        g = int(input(f"Введите генератор g (первообразный корень по модулю {p}): "))
        
        a = int(input("Введите секретное число для Алисы (a): "))
        b = int(input("Введите секретное число для Боба (b): "))
        
        if not (1 < a < p - 1 and 1 < b < p - 1):
            print("Ошибка: секретные числа должны быть в диапазоне (1, p - 1)")
            return
        
        print()
        print("-" * 60)
        A, B, kA, kB = diffie_hellman_exchange(p, g, a, b)
        
        print(f"Открытый ключ Алисы (A) = {A}")
        print(f"Открытый ключ Боба (B) = {B}")
        print(f"Общий секрет Алисы = {kA}")
        print(f"Общий секрет Боба = {kB}")
        print(f"✓ Ключи {'совпадают' if kA == kB else 'НЕ совпадают!'}")
        print("-" * 60)
        
    except ValueError as e:
        print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nПрервано пользователем")


if __name__ == "__main__":
    # Демонстрация примеров
    demo_with_small_numbers()
    demo_with_large_numbers()
    simulate_man_in_the_middle()
    
    # Раскомментируйте для интерактивного режима
    interactive_demo()