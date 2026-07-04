# Метод «шаг младенца, шаг великана»
"""
Метод "шаг младенца, шаг великана" (Baby-Step Giant-Step)
для решения задачи дискретного логарифмирования:
a ^ x ≡ y (mod p), где p - простое число.
"""

import math


def baby_step_giant_step(a, y, p):
    """
    Находит x такое, что a ^ x ≡ y (mod p) методом "шаг младенца, шаг великана".
    
    Аргументы:
        a: основание (целое число)
        y: число, для которого ищем логарифм
        p: модуль (простое число)
    
    Возвращает:
        x: дискретный логарифм, или None, если решение не найдено
    """
    # Приводим числа к модулю p
    a = a % p
    y = y % p
    
    # Шаг 1: Выбираем m и k такие, что mk > p
    # Используем m = ceil(sqrt(p)), k = ceil(sqrt(p))
    m = math.isqrt(p) + 1  # ceil(sqrt(p))
    k = math.isqrt(p) + 1  # ceil(sqrt(p))
    
    print(f"Выбраны параметры: m = {m}, k = {k}, mk = {m * k} > {p}")
    
    # Шаг 2: Вычисляем список "младенцев" (baby steps)
    # Ряд: y, a*y, a^2*y, ..., a^(m-1)*y (mod p)
    print("\nВычисление списка младенцев (baby steps)...")
    baby_steps = {}
    current = y % p
    
    for j in range(m):
        # Сохраняем значение и соответствующий индекс j
        baby_steps[current] = j
        print(f"  j = {j}: {current}")
        # Переход к следующему: умножаем на a
        current = (current * a) % p
    
    # Шаг 3: Вычисляем список "великанов" (giant steps) и ищем совпадение
    # Ряд: a^m, a^(2m), ..., a^(k*m) (mod p)
    print("\nВычисление списка великанов (giant steps) и поиск совпадений...")
    
    # Вычисляем a^m (mod p)
    a_m = pow(a, m, p)
    current = a_m  # a^(1*m)
    
    for i in range(1, k + 1):
        print(f"  i = {i}: {current}")
        
        # Проверяем, есть ли current в списке младенцев
        if current in baby_steps:
            j = baby_steps[current]
            x = i * m - j
            print(f"\nНайдено совпадение!")
            print(f"  a ^ {i * m} = {current} = a ^ {j} * y")
            print(f"  i = {i}, j = {j}")
            print(f"  x = i * m - j = {i} * {m} - {j} = {x}")
            
            # Проверка результата
            if pow(a, x, p) == y % p:
                return x
            else:
                print("  ВНИМАНИЕ: проверка не прошла! Возможно, ошибка.")
                return None
        
        # Переход к следующему: умножаем на a^m
        current = (current * a_m) % p
    
    # Если совпадение не найдено
    print("\nСовпадение не найдено. Решения нет или параметры выбраны неверно.")
    return None


def main():
    """
    Примеры использования метода.
    """
    print("=" * 60)
    print("МЕТОД «ШАГ МЛАДЕНЦА, ШАГ ВЕЛИКАНА»")
    print("Решение дискретного логарифма: a ^ x ≡ y (mod p)")
    print("=" * 60)
    
    # Пример 1: из учебного материала
    print("\n--- Пример 1: 2 ^ x ≡ 9 (mod 23) ---")
    a, y, p = 2, 9, 23
    x = baby_step_giant_step(a, y, p)
    if x is not None:
        print(f"\nРезультат: x = {x}")
        print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)} (ожидалось {y})")
    else:
        print("\nРешение не найдено!")
    
    # Пример 2: другой простой случай
    print("\n" + "=" * 60)
    print("\n--- Пример 2: 3 ^ x ≡ 7 (mod 17) ---")
    a, y, p = 3, 7, 17
    x = baby_step_giant_step(a, y, p)
    if x is not None:
        print(f"\nРезультат: x = {x}")
        print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)} (ожидалось {y})")
    else:
        print("\nРешение не найдено!")
    
    # Пример 3: более сложный
    print("\n" + "=" * 60)
    print("\n--- Пример 3: 5 ^ x ≡ 3 (mod 31) ---")
    a, y, p = 5, 3, 31
    x = baby_step_giant_step(a, y, p)
    if x is not None:
        print(f"\nРезультат: x = {x}")
        print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)} (ожидалось {y})")
    else:
        print("\nРешение не найдено!")
    
    # Пример 4: случай, когда a - первообразный корень
    print("\n" + "=" * 60)
    print("\n--- Пример 4: 7 ^ x ≡ 12 (mod 41) ---")
    a, y, p = 7, 12, 41
    x = baby_step_giant_step(a, y, p)
    if x is not None:
        print(f"\nРезультат: x = {x}")
        print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)} (ожидалось {y})")
    else:
        print("\nРешение не найдено!")
    
    # Пример 5: вручную зададим параметры как в учебнике
    print("\n" + "=" * 60)
    print("\n--- Пример 5 (как в учебнике): 2 ^ x ≡ 9 (mod 23) с m = 6, k = 4 ---")
    a, y, p = 2, 9, 23
    m, k = 6, 4
    print(f"Используем m = {m}, k = {k}, mk = {m * k} > {p}")
    
    # Строим список младенцев
    baby_steps = {}
    current = y % p
    print("\nСписок младенцев:")
    for j in range(m):
        baby_steps[current] = j
        print(f"  j = {j}: {current}")
        current = (current * a) % p
    
    # Строим список великанов и ищем совпадение
    a_m = pow(a, m, p)
    current = a_m
    print("\nСписок великанов и поиск совпадений:")
    found = False
    for i in range(1, k + 1):
        print(f"  i = {i}: {current}")
        if current in baby_steps:
            j = baby_steps[current]
            x = i * m - j
            print(f"\nНайдено совпадение!")
            print(f"  i = {i}, j = {j}")
            print(f"  x = {i} * {m} - {j} = {x}")
            print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)} (ожидалось {y})")
            found = True
            break
        current = (current * a_m) % p
    
    if not found:
        print("\nСовпадение не найдено!")


def interactive_mode():
    """
    Интерактивный режим для ввода своих значений.
    """
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    
    try:
        a = int(input("Введите основание a: "))
        y = int(input("Введите число y (для которого ищем логарифм): "))
        p = int(input("Введите модуль p (простое число): "))
        
        if p <= 0:
            print("Модуль должен быть положительным числом!")
            return
        
        # Проверка, что a и y приведены по модулю p
        a = a % p
        y = y % p
        
        print(f"\nРешаем: {a} ^ x ≡ {y} (mod {p})")
        x = baby_step_giant_step(a, y, p)
        
        if x is not None:
            print(f"\n✓ Решение найдено: x = {x}")
            print(f"Проверка: {a} ^ {x} mod {p} = {pow(a, x, p)}")
        else:
            print("\n✗ Решение не найдено.")
            
    except ValueError:
        print("Ошибка: введите целые числа!")
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")


if __name__ == "__main__":
    # Запуск с примерами
    main()
    
    # Раскомментируйте следующую строку для интерактивного режима:
    interactive_mode()