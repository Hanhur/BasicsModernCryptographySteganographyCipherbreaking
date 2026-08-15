# Числовой пример цифровой подписи на кривой secp256k1
"""
ECDSA на кривой secp256k1 (учебный пример с малыми числами)
Без использования numpy, только встроенные средства Python
"""

def mod_inv(a, p):
    """
    Вычисляет обратное число по модулю p (расширенный алгоритм Евклида)
    """
    a = a % p
    # Перебор для малых чисел (учебный вариант)
    for x in range(1, p):
        if (a * x) % p == 1:
            return x
    raise ValueError(f"Обратное число для {a} по модулю {p} не существует")

def point_double(point, p):
    """
    Удвоение точки на эллиптической кривой y ^ 2 = x ^ 3 + 7 (для secp256k1 a = 0)
    point: (x, y)
    p: модуль поля
    """
    if point is None:
        return None
    
    x, y = point
    if y == 0:
        return None  # Точка на бесконечности
    
    # t = (3*x^2 + a) / (2*y), где a=0
    numerator = (3 * x * x) % p
    denominator = (2 * y) % p
    inv_denominator = mod_inv(denominator, p)
    t = (numerator * inv_denominator) % p
    
    # x3 = t^2 - 2*x
    x3 = (t * t - 2 * x) % p
    
    # y3 = t*(x - x3) - y
    y3 = (t * (x - x3) - y) % p
    
    return (x3, y3)

def point_add(point1, point2, p):
    """
    Сложение двух точек на эллиптической кривой
    """
    if point1 is None:
        return point2
    if point2 is None:
        return point1
    
    x1, y1 = point1
    x2, y2 = point2
    
    if x1 == x2 and y1 != y2:
        return None  # Точка на бесконечности
    
    if x1 == x2 and y1 == y2:
        return point_double(point1, p)
    
    # t = (y2 - y1) / (x2 - x1)
    numerator = (y2 - y1) % p
    denominator = (x2 - x1) % p
    inv_denominator = mod_inv(denominator, p)
    t = (numerator * inv_denominator) % p
    
    # x3 = t^2 - x1 - x2
    x3 = (t * t - x1 - x2) % p
    
    # y3 = t*(x1 - x3) - y1
    y3 = (t * (x1 - x3) - y1) % p
    
    return (x3, y3)

def scalar_mult(k, point, p):
    """
    Умножение точки на скаляр (двоичный метод)
    """
    if k == 0 or point is None:
        return None
    
    result = None
    addend = point
    
    while k > 0:
        if k & 1:  # Если младший бит равен 1
            result = point_add(result, addend, p)
        addend = point_double(addend, p)
        k >>= 1
    
    return result

def print_point(label, point):
    """Красивый вывод точки"""
    if point is None:
        print(f"{label}: Точка на бесконечности")
    else:
        print(f"{label}: ({point[0]}, {point[1]})")

def main():
    print("=" * 60)
    print("ECDSA на кривой secp256k1 (учебный пример)")
    print("=" * 60)
    
    # Параметры кривой (secp256k1, но с малыми числами)
    p = 67      # Модуль поля
    n = 79      # Порядок базовой точки G
    G = (2, 22) # Базовая точка
    
    # Закрытый ключ Алисы
    d = 2
    
    print("\n[1] Параметры кривой:")
    print(f"    p = {p}")
    print(f"    n = {n}")
    print_point("    G", G)
    print(f"    Закрытый ключ d = {d}")
    
    # --- Вычисление открытого ключа ---
    print("\n[2] Вычисление открытого ключа Q = d * G")
    Q = scalar_mult(d, G, p)
    print_point("    Q (открытый ключ)", Q)
    
    # Проверка: для d=2, Q = 2G
    G2 = point_double(G, p)
    print_point("    2G (для проверки)", G2)
    print(f"    Q совпадает с 2G: {Q == G2}")
    
    # --- Подписание сообщения ---
    print("\n[3] Подписание сообщения (Алиса)")
    z = 17  # Хеш сообщения
    k = 3   # Случайный сеансовый ключ
    
    print(f"    Хеш сообщения z = {z}")
    print(f"    Сеансовый ключ k = {k}")
    
    # R = k*G
    R = scalar_mult(k, G, p)
    print_point("    R = k*G", R)
    
    # r = xR mod n (координата x точки R по модулю n)
    r = R[0] % n
    print(f"    r = xR mod n = {R[0]} mod {n} = {r}")
    
    # S = (z + r*d) / k (mod n)
    # Внимание: деление по модулю n!
    k_inv = mod_inv(k, n)
    S = ((z + r * d) % n * k_inv) % n
    print(f"    S = (z + r * d) / k mod n = ({z} + {r} * {d}) / {k} mod {n} = {S}")
    
    print(f"\n    Подпись: (S, r) = ({S}, {r})")
    
    # --- Проверка подписи ---
    print("\n[4] Проверка подписи (Виктор)")
    print(f"    Получены: S = {S}, r = {r}")
    print(f"    Открытые данные: z = {z}, G = ({G[0]}, {G[1]}), Q = ({Q[0]}, {Q[1]})")
    
    # Проверка: 1 <= S <= n-1 и 1 <= r <= n-1
    if 1 <= S < n and 1 <= r < n:
        print("    ✓ Первая проверка: 1 <= S < n и 1 <= r < n")
    else:
        print("    ✗ Ошибка: S или r вне допустимого диапазона")
        return
    
    # w = S^(-1) mod n
    w = mod_inv(S, n)
    print(f"    w = S ^ (-1) mod n = {w}")
    
    # U = z * w mod n
    U = (z * w) % n
    print(f"    U = z * w mod n = {z} * {w} mod {n} = {U}")
    
    # V = r * w mod n
    V = (r * w) % n
    print(f"    V = r * w mod n = {r} * {w} mod {n} = {V}")
    
    # Вычисляем R' = U*G + V*Q
    print("\n[5] Вычисление R' = U * G + V * Q")
    
    UG = scalar_mult(U, G, p)
    print_point("    U * G", UG)
    
    VQ = scalar_mult(V, Q, p)
    print_point("    V * Q", VQ)
    
    R_prime = point_add(UG, VQ, p)
    print_point("    R' = U * G + V * Q", R_prime)
    
    # Финальная проверка: r == xR' mod n
    print("\n[6] Финальная проверка:")
    print(f"    r = {r}")
    print(f"    xR' mod n = {R_prime[0]} mod {n} = {R_prime[0] % n}")
    
    if r == R_prime[0] % n:
        print("    ✓ Подпись ВЕРНА! Виктор принимает подпись.")
    else:
        print("    ✗ Подпись НЕВЕРНА!")
    
    # --- Дополнительная проверка: пример взлома Sony ---
    print("\n" + "=" * 60)
    print("Дополнительно: демонстрация уязвимости при повторном k")
    print("=" * 60)
    
    # Если использовать то же k для другого сообщения
    z2 = 42  # Другой хеш
    print(f"\nАлиса подписывает другое сообщение с ТЕМ ЖЕ k = {k}")
    print(f"Хеш второго сообщения z2 = {z2}")
    
    S2 = ((z2 + r * d) % n * k_inv) % n
    print(f"S2 = ({z2} + {r} * {d}) / {k} mod {n} = {S2}")
    
    # Злоумышленник вычисляет k
    k_cracked = ((z - z2) % n * mod_inv((S - S2) % n, n)) % n
    print(f"\nЗлоумышленник вычисляет k = (z1 - z2) / (S1 - S2) mod n = {k_cracked}")
    print(f"Найденный k = {k_cracked}, исходный k = {k} -> {'Совпадает!' if k_cracked == k else 'Не совпадает'}")
    
    # Злоумышленник вычисляет закрытый ключ
    d_cracked = ((S * k - z) % n * mod_inv(r, n)) % n
    print(f"Злоумышленник вычисляет d = (S * k - z) / r mod n = {d_cracked}")
    print(f"Найденный закрытый ключ = {d_cracked}, исходный d = {d}")
    print("✓ КЛЮЧ ВЗЛОМАН! Вот почему нельзя повторять k в ECDSA!")

if __name__ == "__main__":
    main()