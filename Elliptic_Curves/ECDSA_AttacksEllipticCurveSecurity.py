# Атаки на ECDSA и безопасность эллиптических кривых
"""
Атака на ECDSA при повторном использовании случайного ключа k
Основано на реальной атаке на PlayStation 3 (2010 год)

Восстановление приватного ключа d, если два сообщения подписаны
с одинаковым эфемерным ключом k
"""

from math import gcd

# Расширенный алгоритм Евклида для нахождения обратного элемента по модулю
def modinv(a, m):
    """
    Находит обратный элемент a^(-1) mod m
    Использует расширенный алгоритм Евклида
    """
    a = a % m
    if gcd(a, m) != 1:
        raise ValueError(f"Число {a} не имеет обратного элемента по модулю {m}")
    
    # Расширенный алгоритм Евклида
    m0 = m
    y = 0
    x = 1
    
    if m == 1:
        return 0
    
    while a > 1:
        q = a // m
        t = m
        
        m = a % m
        a = t
        t = y
        
        y = x - q * y
        x = t
    
    if x < 0:
        x = x + m0
    
    return x


def recover_k_from_two_signatures(z1, z2, s1, s2, modulus):
    """
    Восстанавливает случайный ключ k из двух подписей,
    созданных с одинаковым k для разных хешей z1 и z2
    
    Формула: k = (z1 - z2) / (s1 - s2) mod n
    
    Аргументы:
        z1, z2: хеши сообщений
        s1, s2: значения S из подписей
        modulus: порядок кривой (n)
    
    Возвращает:
        k: восстановленный случайный ключ
    """
    # Вычисляем числитель: (z1 - z2) mod n
    numerator = (z1 - z2) % modulus
    
    # Вычисляем знаменатель: (s1 - s2) mod n
    denominator = (s1 - s2) % modulus
    
    # Находим обратный элемент знаменателя по модулю
    inv_denominator = modinv(denominator, modulus)
    
    # k = numerator * inv_denominator mod n
    k = (numerator * inv_denominator) % modulus
    
    return k


def recover_private_key(z, s, r, k, modulus):
    """
    Восстанавливает приватный ключ d, зная случайный ключ k
    
    Формула: d = (s * k - z) / r mod n
    
    Аргументы:
        z: хеш сообщения
        s: значение S из подписи
        r: значение R из подписи
        k: случайный ключ
        modulus: порядок кривой (n)
    
    Возвращает:
        d: восстановленный приватный ключ
    """
    # Вычисляем числитель: (s * k - z) mod n
    numerator = (s * k - z) % modulus
    
    # Находим обратный элемент r по модулю
    inv_r = modinv(r, modulus)
    
    # d = numerator * inv_r mod n
    d = (numerator * inv_r) % modulus
    
    return d


def verify_signature(z, s, r, d, k, modulus):
    """
    Проверяет, что подпись валидна при известных параметрах
    
    Аргументы:
        z: хеш сообщения
        s, r: компоненты подписи
        d: приватный ключ
        k: случайный ключ
        modulus: порядок кривой (n)
    
    Возвращает:
        True если подпись верна, иначе False
    """
    # Проверяем уравнение: s = (z + r*d) / k mod n
    # => s * k ≡ z + r*d (mod n)
    left_side = (s * k) % modulus
    right_side = (z + r * d) % modulus
    
    return left_side == right_side


def demonstrate_attack():
    """
    Демонстрирует атаку на ECDSA с использованием данных из примера в тексте
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ АТАКИ НА ECDSA")
    print("Восстановление приватного ключа при повторном использовании k")
    print("=" * 60)
    
    # Параметры из примера в тексте
    # Модуль (порядок кривой) - для примера используем простое число
    modulus = 67  # В реальном ECDSA это простое число n (порядок кривой)
    
    # Параметры первой подписи
    z1 = 17   # Хеш первого сообщения
    s1 = 47   # Значение S первой подписи
    r = 62    # Значение R (одинаково для обеих подписей, если k одинаковое)
    
    # Параметры второй подписи
    z2 = 23   # Хеш второго сообщения
    s2 = 49   # Значение S второй подписи
    
    print("\nИСХОДНЫЕ ДАННЫЕ:")
    print(f"Модуль (порядок кривой n): {modulus}")
    print(f"Первое сообщение - хеш z1: {z1}, подпись S1: {s1}")
    print(f"Второе сообщение - хеш z2: {z2}, подпись S2: {s2}")
    print(f"Значение r (общее): {r}")
    
    # Шаг 1: Восстановление случайного ключа k
    print("\n" + "-" * 60)
    print("ШАГ 1: Восстановление случайного ключа k")
    print("-" * 60)
    
    k = recover_k_from_two_signatures(z1, z2, s1, s2, modulus)
    print(f"Восстановленное значение k = {k}")
    
    # Проверяем, что восстановленный k совпадает с ожидаемым
    expected_k = 3
    if k == expected_k:
        print(f"✓ k = {k} совпадает с ожидаемым значением!")
    else:
        print(f"✗ Ожидалось k = {expected_k}, получено k = {k}")
    
    # Шаг 2: Восстановление приватного ключа d
    print("\n" + "-" * 60)
    print("ШАГ 2: Восстановление приватного ключа d")
    print("-" * 60)
    
    d = recover_private_key(z1, s1, r, k, modulus)
    print(f"Восстановленное значение d = {d}")
    
    # Проверяем, что восстановленный d совпадает с ожидаемым
    expected_d = 2
    if d == expected_d:
        print(f"✓ d = {d} совпадает с ожидаемым значением!")
    else:
        print(f"✗ Ожидалось d = {expected_d}, получено d = {d}")
    
    # Шаг 3: Проверка валидности подписи
    print("\n" + "-" * 60)
    print("ШАГ 3: Проверка валидности восстановленных ключей")
    print("-" * 60)
    
    # Проверяем первую подпись
    is_valid_1 = verify_signature(z1, s1, r, d, k, modulus)
    print(f"Подпись 1 (z1 = {z1}, S1 = {s1}): {'✓ ВАЛИДНА' if is_valid_1 else '✗ НЕВАЛИДНА'}")
    
    # Проверяем вторую подпись
    is_valid_2 = verify_signature(z2, s2, r, d, k, modulus)
    print(f"Подпись 2 (z2 = {z2}, S2 = {s2}): {'✓ ВАЛИДНА' if is_valid_2 else '✗ НЕВАЛИДНА'}")
    
    # Детальный вывод уравнений
    print("\n" + "-" * 60)
    print("МАТЕМАТИЧЕСКАЯ ПРОВЕРКА")
    print("-" * 60)
    
    print(f"Для подписи 1:")
    print(f"  S1 * k = {s1} * {k} = {s1 * k} mod {modulus} = {(s1 * k) % modulus}")
    print(f"  z1 + r * d = {z1} + {r} * {d} = {z1 + r * d} mod {modulus} = {(z1 + r * d) % modulus}")
    print(f"  Равенство: {(s1 * k) % modulus} == {(z1 + r * d) % modulus} -> {'ДА' if (s1 * k) % modulus == (z1 + r * d) % modulus else 'НЕТ'}")
    
    print(f"\nДля подписи 2:")
    print(f"  S2 * k = {s2} * {k} = {s2 * k} mod {modulus} = {(s2 * k) % modulus}")
    print(f"  z2 + r * d = {z2} + {r} * {d} = {z2 + r * d} mod {modulus} = {(z2 + r * d) % modulus}")
    print(f"  Равенство: {(s2 * k) % modulus} == {(z2 + r * d) % modulus} -> {'ДА' if (s2 * k) % modulus == (z2 + r * d) % modulus else 'НЕТ'}")
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ:")
    print(f"Приватный ключ успешно восстановлен: d = {d}")
    print("=" * 60)


def demonstrate_realistic_scenario():
    """
    Демонстрирует атаку на более реалистичных числах (но всё ещё маленьких для наглядности)
    """
    print("\n\n")
    print("=" * 60)
    print("РЕАЛИСТИЧНЫЙ СЦЕНАРИЙ (с большими числами)")
    print("=" * 60)
    
    # Используем большее простое число для наглядности
    modulus = 101  # Простое число
    
    # Генерируем реальные значения (злоумышленник перехватывает две подписи)
    # Приватный ключ (секретный)
    d_real = 7
    
    # Случайный ключ (секретный, но использован дважды - ошибка!)
    k_real = 13
    
    # Значение r (вычисляется из k * G, но для примера возьмем любое)
    r_real = 42
    
    # Хеши двух разных сообщений
    z1_real = 35
    z2_real = 89
    
    # Вычисляем подписи (то, что видит злоумышленник)
    s1_real = ((z1_real + r_real * d_real) * modinv(k_real, modulus)) % modulus
    s2_real = ((z2_real + r_real * d_real) * modinv(k_real, modulus)) % modulus
    
    print(f"\nИСХОДНЫЕ ДАННЫЕ:")
    print(f"Модуль (порядок кривой n): {modulus}")
    print(f"Реальный приватный ключ d (секрет): {d_real}")
    print(f"Реальный случайный ключ k (секрет, но использован дважды): {k_real}")
    print(f"Значение r: {r_real}")
    print(f"\nПерехваченные подписи:")
    print(f"  Сообщение 1 (z1 = {z1_real}): S1 = {s1_real}")
    print(f"  Сообщение 2 (z2 = {z2_real}): S2 = {s2_real}")
    
    # Атака
    print("\n" + "-" * 60)
    print("ПРОВЕДЕНИЕ АТАКИ")
    print("-" * 60)
    
    k_recovered = recover_k_from_two_signatures(z1_real, z2_real, s1_real, s2_real, modulus)
    print(f"Восстановленный k: {k_recovered}")
    
    d_recovered = recover_private_key(z1_real, s1_real, r_real, k_recovered, modulus)
    print(f"Восстановленный d: {d_recovered}")
    
    if d_recovered == d_real:
        print("\n✓ АТАКА УСПЕШНА! Приватный ключ полностью восстановлен!")
    else:
        print("\n✗ Атака не удалась (такого не должно быть при корректных данных)")


def main():
    """
    Главная функция программы
    """
    # Демонстрация на примере из текста
    demonstrate_attack()
    
    # Демонстрация на реалистичном сценарии
    demonstrate_realistic_scenario()
    
    print("\n\n" + "=" * 60)
    print("ВЫВОД:")
    print("1. Повторное использование случайного ключа k - фатальная ошибка")
    print("2. Достаточно двух подписей с одинаковым k для восстановления")
    print("3. Злоумышленник получает полный контроль над приватным ключом")
    print("4. Это привело к взлому PlayStation 3 в 2010 году")
    print("=" * 60)


if __name__ == "__main__":
    main()