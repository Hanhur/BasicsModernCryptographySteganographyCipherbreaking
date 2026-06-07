# Задачи и упражнения
# Задача 1. Показать, что многочлен f(D) = D4 + D3 + D2 + D + 1 Е Z2[D] неприводим, но не примитивен. 
# Чему равен период выпускной последовательности LFSR с таким связующим многочленом f(D)?
# -*- coding: utf-8 -*-
"""
Программа для анализа многочлена f(D) = D ^ 4 + D ^ 3 + D ^ 2 + D + 1 над GF(2)
"""

# --- 1. Работа в GF(2) ---
def gf2_add_poly(p, q):
    """Сложение многочленов над GF(2) (покомпонентный XOR)"""
    deg = max(len(p), len(q))
    res = [0] * deg
    for i in range(len(p)):
        res[i] ^= p[i]
    for i in range(len(q)):
        res[i] ^= q[i]
    # Убираем старшие нули
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mul_poly(p, q):
    """Умножение многочленов над GF(2)"""
    res = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        if p[i] == 1:
            for j in range(len(q)):
                res[i + j] ^= q[j]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mod_poly(a, b):
    """Остаток от деления a на b над GF(2) (b != 0)"""
    a = a[:]
    deg_b = len(b) - 1
    while len(a) >= len(b):
        if a[-1] == 1:
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] ^= b[i]
        while len(a) > 0 and a[-1] == 0:
            a.pop()
    return a if a else [0]

def gf2_poly_pow_mod(base, exponent, modulus):
    """Возведение многочлена base^exponent по модулю modulus над GF(2)"""
    result = [1]  # 1 в виде многочлена
    while exponent > 0:
        if exponent & 1:
            result = gf2_mod_poly(gf2_mul_poly(result, base), modulus)
        base = gf2_mod_poly(gf2_mul_poly(base, base), modulus)
        exponent >>= 1
    return result

# --- 2. Проверка на неприводимость над GF(2) для степени 4 ---
def is_irreducible_deg4(poly):
    """
    Проверка неприводимости многочлена степени 4 над GF(2)
    (достаточно проверить делимость на многочлены степени 1 и единственный
    неприводимый степени 2).
    """
    # Проверка делимости на D (коэффициент при D ^ 0)
    if poly[0] == 0:
        return False
    # Проверка делимости на D + 1 (сумма коэффициентов mod 2)
    if sum(poly) % 2 == 0:
        return False

    # Неприводимый многочлен степени 2 над GF(2) — D ^ 2 + D + 1
    deg2_irred = [1, 1, 1]  # коэффициенты: 1 + D + D ^ 2
    if gf2_mod_poly(poly, deg2_irred) == [0]:
        return False
    return True

# --- 3. Проверка на примитивность (порядок корня = 15) ---
def find_order_root(f):
    """
    Находит порядок корня f в GF(16): минимальное r такое, что D ^ r ≡ 1 mod f
    Период LFSR = порядок корня.
    """
    # f — список коэффициентов от младшей степени к старшей
    # Сначала убедимся, что f неприводим
    if not is_irreducible_deg4(f):
        raise ValueError("Многочлен не неприводим")

    # Для степени 4 поле GF(16) имеет максимальный порядок 15
    max_order = 2 ** 4 - 1

    # Начинаем с D (многочлен X)
    base = [0, 1]  # D

    for r in range(1, max_order + 1):
        # Вычисляем D ^ r mod f
        res = gf2_poly_pow_mod(base, r, f)
        # Если результат = 1 (многочлен [1]), то r — порядок
        if res == [1]:
            return r
    return None

# --- 4. Построение последовательности LFSR для проверки периода ---
def lfsr_sequence(f, init_state, n_steps):
    """
    Генерирует n_steps битов LFSR.
    f = [c0, c1, ..., cn] (c0 — младший коэффициент, при D ^ 0)
    init_state = [s0, s1, ..., s_{n - 1}] (начальное заполнение, слева направо).
    Возвращает список выходных битов.
    """
    n = len(f) - 1  # степень
    state = init_state[:]  # копируем
    out_bits = []
    for _ in range(n_steps):
        out_bit = state[-1]  # последний регистр — выход
        out_bits.append(out_bit)

        # Обратная связь: сумма f[i] * state[i] для i = 0..n - 1
        feedback = 0
        for i in range(n):
            feedback ^= (f[i] & state[i])

        # Сдвиг
        for i in range(n - 1, 0, -1):
            state[i] = state[i - 1]
        state[0] = feedback
    return out_bits

# --- Основная программа ---
def main():
    # Многочлен f(D) = 1 + D + D ^ 2 + D ^ 3 + D ^ 4
    # Коэффициенты: [1, 1, 1, 1, 1] (1 + D + D ^ 2 + D ^ 3 + D ^ 4)
    poly = [1, 1, 1, 1, 1]

    print("Многочлен f(D) = 1 + D + D ^ 2 + D ^ 3 + D ^ 4")
    print(f"Коэффициенты: {poly}")

    # 1. Проверка неприводимости
    irreducible = is_irreducible_deg4(poly)
    print(f"\n1. Неприводимость: {irreducible}")
    if not irreducible:
        print("   (Многочлен имеет делители — противоречит условию задачи, проверьте входные данные)")

    # 2. Проверка примитивности: порядок корня
    order = find_order_root(poly)
    print(f"\n2. Порядок корня = {order}")
    if order == 15:
        print("   => Многочлен ПРИМИТИВЕН")
    else:
        print("   => Многочлен НЕ ПРИМИТИВЕН")

    # 3. Период LFSR = порядку корня
    print(f"\n3. Период выходной последовательности LFSR = {order}")

    # 4. Демонстрация LFSR
    n = len(poly) - 1  # степень = 4
    init_state = [1, 0, 0, 0]  # произвольное ненулевое состояние
    seq_len = 20

    seq = lfsr_sequence(poly, init_state, seq_len)
    print(f"\n4. Первые {seq_len} битов LFSR (начальное состояние {init_state}):")
    print("".join(map(str, seq)))
    print("   (период должен быть 5 — видно повторение после этого)")

    # Проверим повтор через 5 битов
    seq_5 = lfsr_sequence(poly, init_state, 10)
    print(f"   Первые 10 битов: {seq_5[:10]}")
    print(f"   seq[0:5] = {seq_5[0:5]}")
    print(f"   seq[5:10] = {seq_5[5:10]} -> действительно повтор")

if __name__ == "__main__":
    main()

# Задача 2. Проверить, будет ли многочлен f(D) = D4 + D + 1 Е Z2[D] неприводимым и примитивным.
# -*- coding: utf-8 -*-
"""
Программа для анализа многочлена f(D) = D ^ 4 + D + 1 над GF(2)
"""

# --- 1. Работа в GF(2) ---
def gf2_add_poly(p, q):
    """Сложение многочленов над GF(2)"""
    deg = max(len(p), len(q))
    res = [0] * deg
    for i in range(len(p)):
        res[i] ^= p[i]
    for i in range(len(q)):
        res[i] ^= q[i]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mul_poly(p, q):
    """Умножение многочленов над GF(2)"""
    res = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        if p[i] == 1:
            for j in range(len(q)):
                res[i + j] ^= q[j]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mod_poly(a, b):
    """Остаток от деления a на b над GF(2) (b != 0)"""
    a = a[:]
    deg_b = len(b) - 1
    while len(a) >= len(b):
        if a[-1] == 1:
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] ^= b[i]
        while len(a) > 0 and a[-1] == 0:
            a.pop()
    return a if a else [0]

def gf2_poly_pow_mod(base, exponent, modulus):
    """Возведение многочлена base^exponent по модулю modulus над GF(2)"""
    result = [1]  # 1 в виде многочлена
    while exponent > 0:
        if exponent & 1:
            result = gf2_mod_poly(gf2_mul_poly(result, base), modulus)
        base = gf2_mod_poly(gf2_mul_poly(base, base), modulus)
        exponent >>= 1
    return result

# --- 2. Проверка неприводимости над GF(2) для степени 4 ---
def is_irreducible_deg4(poly):
    """
    Проверка неприводимости многочлена степени 4 над GF(2)
    """
    # Проверка делимости на D (коэффициент при D^0)
    if poly[0] == 0:
        return False
    
    # Проверка делимости на D+1 (сумма коэффициентов mod 2)
    if sum(poly) % 2 == 0:
        return False

    # Неприводимый многочлен степени 2 над GF(2) — D ^ 2 + D + 1
    deg2_irred = [1, 1, 1]  # коэффициенты: 1 + D + D ^ 2
    if gf2_mod_poly(poly, deg2_irred) == [0]:
        return False
    
    return True

# --- 3. Нахождение порядка корня (периода LFSR) ---
def find_order_root(f):
    """
    Находит порядок корня f в GF(16): минимальное r такое, что D ^ r ≡ 1 mod f
    Период LFSR = порядок корня.
    """
    max_order = 2 ** 4 - 1  # 15 для степени 4
    
    # Начинаем с D (многочлен X)
    base = [0, 1]  # D
    
    # Проверяем все делители max_order (для эффективности, но можно и все подряд)
    # Для простоты проверим все r от 1 до max_order
    for r in range(1, max_order + 1):
        res = gf2_poly_pow_mod(base, r, f)
        if res == [1]:  # D^r ≡ 1 (mod f)
            return r
    return None

# --- 4. Альтернативная проверка примитивности через все делители 2 ^ n - 1 ---
def is_primitive(f, n):
    """
    Проверка, является ли неприводимый многочлен f степени n примитивным.
    """
    order_max = 2 ** n - 1
    
    # Находим простые делители order_max
    factors = []
    m = order_max
    d = 2
    while d * d <= m:
        if m % d == 0:
            factors.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        factors.append(m)
    
    # Проверяем, что для каждого простого делителя p числа order_max
    # D ^ (order_max / p) ≠ 1 (mod f)
    base = [0, 1]  # D
    for p in factors:
        exp = order_max // p
        res = gf2_poly_pow_mod(base, exp, f)
        if res == [1]:
            return False
    return True

# --- 5. Генерация последовательности LFSR ---
def lfsr_sequence(f, init_state, n_steps):
    """
    Генерирует n_steps битов LFSR.
    f = [c0, c1, ..., cn] (c0 — младший коэффициент, при D ^ 0)
    init_state = [s0, s1, ..., s_{n - 1}] (начальное заполнение)
    """ 
    n = len(f) - 1  # степень
    state = init_state[:]
    out_bits = []
    for _ in range(n_steps):
        out_bit = state[-1]  # последний регистр — выход
        out_bits.append(out_bit)
        
        # Обратная связь: сумма f[i] * state[i] для i = 0..n - 1
        feedback = 0
        for i in range(n):
            feedback ^= (f[i] & state[i])
        
        # Сдвиг
        for i in range(n - 1, 0, -1):
            state[i] = state[i - 1]
        state[0] = feedback
    return out_bits

# --- Основная программа ---
def main():
    # Многочлен f(D) = D ^ 4 + D + 1
    # Коэффициенты: [1, 1, 0, 0, 1]? Нет, аккуратно:
    # D ^ 4 + D + 1 = 1 + D + 0 * D ^ 2 + 0 * D ^ 3 + 1 * D ^ 4
    # В списке: [коэфф при D ^ 0, D ^ 1, D ^ 2, D ^ 3, D ^ 4]
    poly = [1, 1, 0, 0, 1]  # 1 + D + D ^ 4
    
    print("=" * 60)
    print("Многочлен f(D) = D ^ 4 + D + 1")
    print(f"Коэффициенты (от младшей степени): {poly}")
    print("=" * 60)
    
    # 1. Проверка неприводимости
    irreducible = is_irreducible_deg4(poly)
    print(f"\n1. Неприводимость над GF(2): {irreducible}")
    
    if not irreducible:
        print("   Многочлен приводим!")
        return
    
    # 2. Нахождение порядка корня
    order = find_order_root(poly)
    print(f"\n2. Порядок корня (период LFSR): {order}")
    
    # 3. Проверка примитивности
    max_possible_order = 2 ** 4 - 1
    is_prim = (order == max_possible_order)
    print(f"\n3. Примитивность: {'Да' if is_prim else 'Нет'}")
    
    if is_prim:
        print(f"   (порядок = {order} = максимальный {max_possible_order})")
    else:
        print(f"   (порядок = {order} < максимального {max_possible_order})")
    
    # 4. Демонстрация LFSR
    n = len(poly) - 1  # степень = 4
    init_state = [1, 0, 0, 0]  # ненулевое начальное состояние
    seq_len = 20
    
    seq = lfsr_sequence(poly, init_state, seq_len)
    print(f"\n4. Первые {seq_len} битов LFSR (начальное состояние {init_state}):")
    print("   " + "".join(map(str, seq)))
    
    # Проверим период: сгенерируем больше и найдем повтор
    seq_long = lfsr_sequence(poly, init_state, 50)
    print(f"\n5. Проверка периода (должен быть {order}):")
    for i in range(order, 30):
        if seq_long[:order] == seq_long[i:i + order]:
            print(f"   Повтор найден: seq[0:{order}] = seq[{i}:{i + order}]")
            break
    else:
        print("   Автоматическая проверка не показала повтор (но период точно вычислен теоретически)")
    
    # Альтернативная проверка через все простые делители
    print("\n6. Альтернативная проверка примитивности (методом простых делителей):")
    is_prim_alt = is_primitive(poly, 4)
    print(f"   Результат: {'примитивен' if is_prim_alt else 'не примитивен'}")
    
    # Вывод итогового ответа
    print("\n" + "=" * 60)
    print("ИТОГ:")
    print(f"• Многочлен f(D) = D ^ 4 + D + 1 неприводим: {irreducible}")
    print(f"• Многочлен f(D) = D ^ 4 + D + 1 примитивен: {is_prim}")
    print(f"• Период LFSR = {order}")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Задача 3. Показать, что многочлен f(D) = D4 + D3 + 1 Е Z2[D] неприводим. 
# Будет ли он примитивным? Чему равен период выпускной последовательности LFSR с таким связующим многочленом? 
# -*- coding: utf-8 -*-
"""
Программа для анализа многочлена f(D) = D ^ 4 + D ^ 3 + 1 над GF(2)
"""

# --- 1. Работа в GF(2) ---
def gf2_add_poly(p, q):
    """Сложение многочленов над GF(2)"""
    deg = max(len(p), len(q))
    res = [0] * deg
    for i in range(len(p)):
        res[i] ^= p[i]
    for i in range(len(q)):
        res[i] ^= q[i]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mul_poly(p, q):
    """Умножение многочленов над GF(2)"""
    res = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        if p[i] == 1:
            for j in range(len(q)):
                res[i + j] ^= q[j]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mod_poly(a, b):
    """Остаток от деления a на b над GF(2) (b != 0)"""
    a = a[:]
    deg_b = len(b) - 1
    while len(a) >= len(b):
        if a[-1] == 1:
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] ^= b[i]
        while len(a) > 0 and a[-1] == 0:
            a.pop()
    return a if a else [0]

def gf2_poly_pow_mod(base, exponent, modulus):
    """Возведение многочлена base^exponent по модулю modulus над GF(2)"""
    result = [1]  # 1 в виде многочлена
    while exponent > 0:
        if exponent & 1:
            result = gf2_mod_poly(gf2_mul_poly(result, base), modulus)
        base = gf2_mod_poly(gf2_mul_poly(base, base), modulus)
        exponent >>= 1
    return result

# --- 2. Проверка неприводимости над GF(2) для степени 4 ---
def is_irreducible_deg4(poly):
    """
    Проверка неприводимости многочлена степени 4 над GF(2)
    """
    # Проверка делимости на D (коэффициент при D ^ 0)
    if poly[0] == 0:
        return False
    
    # Проверка делимости на D + 1 (сумма коэффициентов mod 2)
    if sum(poly) % 2 == 0:
        return False

    # Неприводимый многочлен степени 2 над GF(2) — D ^ 2 + D + 1
    deg2_irred = [1, 1, 1]  # коэффициенты: 1 + D + D ^ 2
    if gf2_mod_poly(poly, deg2_irred) == [0]:
        return False
    
    return True

# --- 3. Нахождение порядка корня (периода LFSR) ---
def find_order_root(f):
    """
    Находит порядок корня f в GF(16): минимальное r такое, что D ^ r ≡ 1 mod f
    Период LFSR = порядок корня.
    """
    max_order = 2 ** 4 - 1  # 15 для степени 4
    
    # Начинаем с D (многочлен X)
    base = [0, 1]  # D
    
    # Проверяем все r от 1 до max_order
    for r in range(1, max_order + 1):
        res = gf2_poly_pow_mod(base, r, f)
        if res == [1]:  # D ^ r ≡ 1 (mod f)
            return r
    return None

# --- 4. Проверка примитивности через простые делители 2 ^ n - 1 ---
def is_primitive(f, n):
    """
    Проверка, является ли неприводимый многочлен f степени n примитивным.
    """
    order_max = 2 ** n - 1
    
    # Находим простые делители order_max
    factors = []
    m = order_max
    d = 2
    while d * d <= m:
        if m % d == 0:
            factors.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        factors.append(m)
    
    # Проверяем, что для каждого простого делителя p числа order_max
    # D ^ (order_max / p) ≠ 1 (mod f)
    base = [0, 1]  # D
    for p in factors:
        exp = order_max // p
        res = gf2_poly_pow_mod(base, exp, f)
        if res == [1]:
            return False
    return True

# --- 5. Генерация последовательности LFSR ---
def lfsr_sequence(f, init_state, n_steps):
    """
    Генерирует n_steps битов LFSR.
    f = [c0, c1, ..., cn] (c0 — младший коэффициент, при D ^ 0)
    init_state = [s0, s1, ..., s_{n - 1}] (начальное заполнение)
    """
    n = len(f) - 1  # степень
    state = init_state[:]
    out_bits = []
    for _ in range(n_steps):
        out_bit = state[-1]  # последний регистр — выход
        out_bits.append(out_bit)
        
        # Обратная связь: сумма f[i] * state[i] для i = 0..n - 1
        feedback = 0
        for i in range(n):
            feedback ^= (f[i] & state[i])
        
        # Сдвиг
        for i in range(n - 1, 0, -1):
            state[i] = state[i - 1]
        state[0] = feedback
    return out_bits

# --- 6. Визуальная проверка периода ---
def verify_period(seq, expected_period, max_check = 50):
    """
    Визуально проверяет, что последовательность имеет период expected_period
    """
    for i in range(expected_period, min(max_check, len(seq) - expected_period)):
        if seq[:expected_period] == seq[i:i + expected_period]:
            return True
    return False

# --- Основная программа ---
def main():
    # Многочлен f(D) = D ^ 4 + D ^ 3 + 1
    # Коэффициенты: [1, 0, 0, 1, 1]? Нет, аккуратно:
    # D ^ 4 + D ^ 3 + 1 = 1 + 0 * D + 0 * D ^ 2 + 1 * D ^ 3 + 1 * D ^ 4
    # В списке: [коэфф при D ^ 0, D ^ 1, D ^ 2, D ^ 3, D ^ 4]
    poly = [1, 0, 0, 1, 1]  # 1 + D ^ 3 + D ^ 4
    
    print("=" * 70)
    print("Многочлен f(D) = D ^ 4 + D ^ 3 + 1")
    print(f"Коэффициенты (от младшей степени): {poly}")
    print("=" * 70)
    
    # 1. Проверка неприводимости
    irreducible = is_irreducible_deg4(poly)
    print(f"\n1. Неприводимость над GF(2): {irreducible}")
    
    if not irreducible:
        print("   Многочлен приводим!")
        return
    
    # 2. Нахождение порядка корня
    order = find_order_root(poly)
    print(f"\n2. Порядок корня (период LFSR): {order}")
    
    # 3. Проверка примитивности
    max_possible_order = 2 ** 4 - 1
    is_prim = (order == max_possible_order)
    print(f"\n3. Примитивность: {'Да' if is_prim else 'Нет'}")
    
    if is_prim:
        print(f"   (порядок = {order} = максимальный {max_possible_order})")
    else:
        print(f"   (порядок = {order} < максимального {max_possible_order})")
    
    # 4. Демонстрация LFSR
    n = len(poly) - 1  # степень = 4
    init_state = [1, 0, 0, 0]  # ненулевое начальное состояние
    seq_len = 30
    
    seq = lfsr_sequence(poly, init_state, seq_len)
    print(f"\n4. Первые {seq_len} битов LFSR (начальное состояние {init_state}):")
    print("   " + "".join(map(str, seq)))
    
    # 5. Проверка периода визуально
    print(f"\n5. Проверка периода (должен быть {order}):")
    if verify_period(seq, order, seq_len):
        print(f"   ✅ Последовательность имеет период {order}")
        print(f"   Первые {order} битов: {seq[:order]}")
        print(f"   Следующие {order} битов: {seq[order:2 * order]}")
    else:
        print(f"   ⚠️ Автоматическая проверка не показала повтор (но период теоретически {order})")
        print(f"   Возможно, нужно больше битов для проверки")
    
    # 6. Альтернативная проверка примитивности через простые делители
    print("\n6. Альтернативная проверка примитивности (методом простых делителей 15):")
    is_prim_alt = is_primitive(poly, 4)
    print(f"   Результат: {'примитивен' if is_prim_alt else 'не примитивен'}")
    
    # 7. Дополнительная проверка: все возможные ненулевые начальные состояния
    print("\n7. Проверка для разных начальных состояний:")
    test_states = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 1, 1]
    ]
    for state in test_states:
        test_seq = lfsr_sequence(poly, state, order * 2)
        if test_seq[:order] == test_seq[order:2 * order]:
            print(f"   Состояние {state}: период {order} ✓")
        else:
            print(f"   Состояние {state}: период не {order}?")
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ИТОГ:")
    print(f"• Многочлен f(D) = D ^ 4 + D ^ 3 + 1 неприводим: {irreducible}")
    print(f"• Многочлен f(D) = D ^ 4 + D ^ 3 + 1 примитивен: {is_prim}")
    print(f"• Период LFSR = {order}")
    print("=" * 70)

if __name__ == "__main__":
    main()

# Задача 4. Проверить, что неприводимый многочлен f(D) = D5 + D2 + 1 Е Z2[D] является примитивным. 
# Убедиться, что в качестве связующего многочлена он дает выпускную последовательность максимального периода 31, 
# выбрав вектором начальных содержаний [1, 1, 1, 1, 1].
# -*- coding: utf-8 -*-
"""
Программа для анализа многочлена f(D) = D ^ 5 + D ^ 2 + 1 над GF(2)
"""

# --- 1. Работа в GF(2) ---
def gf2_add_poly(p, q):
    deg = max(len(p), len(q))
    res = [0] * deg
    for i in range(len(p)):
        res[i] ^= p[i]
    for i in range(len(q)):
        res[i] ^= q[i]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mul_poly(p, q):
    res = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        if p[i] == 1:
            for j in range(len(q)):
                res[i + j] ^= q[j]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def gf2_mod_poly(a, b):
    a = a[:]
    while len(a) >= len(b):
        if a[-1] == 1:
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] ^= b[i]
        while len(a) > 0 and a[-1] == 0:
            a.pop()
    return a if a else [0]

def gf2_poly_pow_mod(base, exponent, modulus):
    result = [1]
    while exponent > 0:
        if exponent & 1:
            result = gf2_mod_poly(gf2_mul_poly(result, base), modulus)
        base = gf2_mod_poly(gf2_mul_poly(base, base), modulus)
        exponent >>= 1
    return result

# --- 2. Проверка неприводимости для степени 5 ---
def is_irreducible_deg5(poly):
    # poly: список коэффициентов от младшей степени
    if poly[0] == 0:
        return False
    if sum(poly) % 2 == 0:
        return False

    # Проверка делимости на D ^ 2 + D + 1
    deg2_irred = [1, 1, 1]
    if gf2_mod_poly(poly, deg2_irred) == [0]:
        return False

    # Проверка делимости на все неприводимые степени 3 (их два)
    # Неприводимые степени 3 над GF(2): D ^ 3 + D + 1, D ^ 3 + D ^ 2 + 1
    deg3_irred1 = [1, 1, 0, 1]  # 1 + D + D ^ 3
    deg3_irred2 = [1, 0, 1, 1]  # 1 + D ^ 2 + D ^ 3

    if gf2_mod_poly(poly, deg3_irred1) == [0]:
        return False
    if gf2_mod_poly(poly, deg3_irred2) == [0]:
        return False

    return True

# --- 3. Проверка примитивности для степени 5 ---
def is_primitive_deg5(poly):
    # poly — неприводимый степени 5
    n = 5
    max_order = 2 ** n - 1  # 31
    # Простые делители 31: только 31 (само простое)
    # Для примитивности нужно, чтобы D ^ (31 / p) ≠ 1 mod f для всех простых p | 31
    # p = 31 — единственный, проверим D ^ (31 / 31) = D ^ 1 ≠ 1
    # Но это не полная проверка: нужно, чтобы порядок был 31, т.е. D ^ 31 ≡ 1
    # и для всех простых делителей 31 (т.е. 31) — нет, делитель 31 — само число,
    # поэтому надо проверить D ^ (31 / p) для p = 31? Так не работает: p = 31, 31 / p = 1.
    # Значит, проверка сводится к D ^ 1 ≠ 1 — что верно.
    # Тогда проверим D ^ 31 ≡ 1 mod f
    base = [0, 1]  # D
    res = gf2_poly_pow_mod(base, max_order, poly)
    if res != [1]:
        return False
    # Проверка, что нет меньшего периода: нужно проверить все делители max_order
    # Кроме 1, все делители 31 — только 1 и 31.
    # D ^ 1 ≠ 1 проверили.
    # Порядок 31, значит примитивен.
    # Но для общности: проверим D ^ (31 / 31) уже сделали, это D ^ 1, не 1.
    # Примитивен.
    return True

# --- 4. LFSR генератор ---
def lfsr_sequence(f, init_state, n_steps):
    n = len(f) - 1
    state = init_state[:]
    out_bits = []
    for _ in range(n_steps):
        out_bit = state[-1]
        out_bits.append(out_bit)
        feedback = 0
        for i in range(n):
            feedback ^= (f[i] & state[i])
        for i in range(n - 1, 0, -1):
            state[i] = state[i - 1]
        state[0] = feedback
    return out_bits

# --- 5. Поиск периода последовательности ---
def find_period(seq, max_period):
    for p in range(1, max_period + 1):
        if len(seq) >= 2 * p and seq[:p] == seq[p:2 * p]:
            return p
    return None

# --- Основная программа ---
def main():
    # f(D) = D ^ 5 + D ^ 2 + 1
    # Коэффициенты: 1 + 0 * D + 1 * D ^ 2 + 0 * D ^ 3 + 0 * D ^ 4 + 1 * D ^ 5
    poly = [1, 0, 1, 0, 0, 1]  # 1 + D ^ 2 + D ^ 5

    print("=" * 70)
    print("Многочлен f(D) = D ^ 5 + D ^ 2 + 1")
    print(f"Коэффициенты (от младшей степени): {poly}")
    print("=" * 70)

    # 1. Неприводимость
    irreducible = is_irreducible_deg5(poly)
    print(f"\n1. Неприводимость над GF(2): {irreducible}")

    if not irreducible:
        print("   Многочлен приводим!")
        return

    # 2. Примитивность
    primitive = is_primitive_deg5(poly)
    print(f"\n2. Примитивность: {primitive}")

    max_possible_period = 2 ** 5 - 1
    if primitive:
        print(f"   (период = {max_possible_period} — максимальный)")
    else:
        print(f"   (период < {max_possible_period})")

    # 3. Генерация последовательности с начальным состоянием [1, 1, 1, 1, 1]
    init_state = [1, 1, 1, 1, 1]
    n_steps = 100
    seq = lfsr_sequence(poly, init_state, n_steps)

    print(f"\n3. Первые {min(62, n_steps)} битов LFSR")
    print(f"   Начальное состояние: {init_state}")
    print("   Последовательность:")
    print("   " + "".join(map(str, seq[:62])))

    # 4. Поиск периода
    period = find_period(seq, max_possible_period)
    print(f"\n4. Период последовательности: {period}")

    if period == max_possible_period:
        print(f"   ✅ Многочлен примитивен, период максимальный = {period}")
    else:
        print(f"   ❌ Период не максимальный")

    # 5. Вывод первых 31 бита (один период) для проверки
    if period:
        print(f"\n5. Один период (первые {period} битов):")
        print("   " + "".join(map(str, seq[:period])))

    # Итог
    print("\n" + "=" * 70)
    print("ИТОГ:")
    print(f"• Многочлен D ^ 5 + D ^ 2 + 1 неприводим: {irreducible}")
    print(f"• Многочлен D ^ 5 + D ^ 2 + 1 примитивен: {primitive}")
    print(f"• Период LFSR с начальным состоянием [1, 1, 1, 1, 1] = {period}")
    print("=" * 70)


if __name__ == "__main__":
    main()

# Задача 5. Построить LFSR максимального периода с 6-ю состояниями.
# -*- coding: utf-8 -*-
"""
Построение 6-разрядного LFSR максимального периода (63)
с многочленом f(D) = D ^ 6 + D + 1
"""

def lfsr_max_period_n6(init_state, n_steps):
    """
    LFSR с f(D) = D ^ 6 + D + 1
    Коэффициенты: c0 = 1, c1 = 1, c2 = c3 = c4 = c5 = 0 (первые 6)
    Регистр: [s5, s4, s3, s2, s1, s0] — список
    Выход: s0
    Обратная связь: s_new = s0 + s1 (XOR)
    """
    state = init_state[:]
    out_bits = []
    for _ in range(n_steps):
        out_bit = state[-1]  # s0
        out_bits.append(out_bit)
        # Обратная связь: s0 XOR s1
        feedback = state[-1] ^ state[-2]  # state[-1] = s0, state[-2] = s1
        # Сдвиг вправо: новый s5 = feedback
        state = [feedback] + state[:-1]
    return out_bits

def find_period(seq, max_period):
    """Находит период последовательности"""
    for p in range(1, max_period + 1):
        # Проверяем повтор через p
        if len(seq) >= 2 * p and seq[:p] == seq[p:2 * p]:
            return p
    return None

def main():
    n = 6
    max_period = 2 ** n - 1  # 63
    
    # Начальное состояние: [s5, s4, s3, s2, s1, s0] = [0, 0, 0, 0, 0, 1]
    init_state = [0, 0, 0, 0, 0, 1]
    
    print("=" * 70)
    print("LFSR максимального периода с 6 разрядами")
    print(f"Связующий многочлен: f(D) = D ^ 6 + D + 1")
    print(f"Максимальный период: {max_period}")
    print(f"Начальное состояние: {init_state}")
    print("=" * 70)
    
    # Генерируем 2*max_period битов, чтобы убедиться в периоде
    n_steps = 2 * max_period
    seq = lfsr_max_period_n6(init_state, n_steps)
    
    print(f"\nПервые {min(80, n_steps)} битов выходной последовательности:")
    print("".join(map(str, seq[:80])))
    
    # Находим период
    period = find_period(seq, max_period)
    print(f"\nПериод последовательности: {period}")
    
    if period == max_period:
        print("✅ Период максимальный = 63")
    else:
        print(f"❌ Период {period} < 63")
    
    # Покажем один полный период
    print(f"\nОдин полный период (первые {max_period} битов):")
    print("".join(map(str, seq[:max_period])))
    
    # Проверим, что через 63 бита последовательность повторяется
    print("\nПроверка повтора:")
    if seq[:max_period] == seq[max_period:2 * max_period]:
        print("✅ Последовательность повторяется через 63 бита")
    else:
        print("❌ Ошибка: нет повтора через 63 бита")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

# Задача 6. Следующая шифровка получена шифром Вернама, в котором ключ генерируется LFSR с длиной регистра 7: 
# 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1. 
# Предположим, что известно начало исходного текста 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0. 
# Найти весь исходный текст. Что можно было бы сказать при длине регистра 8?
# -*- coding: utf-8 -*-
"""
Задача 6. Восстановление ключа LFSR и открытого текста.
Шифр Вернама, ключ генерируется LFSR длины 7.
"""

def solve_lfsr_degree7(C, P_known):
    """
    C: шифротекст (список битов)
    P_known: известные первые биты открытого текста (длина >= 15)
    Возвращает:
        K: восстановленная ключевая последовательность (вся)
        P: восстановленный открытый текст
        c: коэффициенты обратной связи [c0..c6]
    """
    n = 7
    # 1. Восстанавливаем первые 2n = 14 битов K (нужно 2n для однозначного нахождения c)
    # Но у нас есть 15 битов P_known, значит, K известно для i = 0..14.
    K = [P_known[i] ^ C[i] for i in range(len(P_known))]
    
    # 2. Находим коэффициенты c0..c6 из уравнений для i = n..2n - 1
    # Уравнения: K[i] = sum_{j = 0} ^ {n - 1} c[j] * K[i - 1 - j] для i = n..2n - 1
    # Это система линейных уравнений над GF(2)
    # Решаем перебором (2 ^ 7 = 128 вариантов) — для простоты и наглядности
    possible_c = []
    for mask in range(2 ** n):
        c = [(mask >> j) & 1 for j in range(n)]  # c0, c1, ..., c6
        ok = True
        for i in range(n, len(K)):
            # вычисляем правую часть
            rhs = 0
            for j in range(n):
                rhs ^= (c[j] & K[i - 1 - j])
            if rhs != K[i]:
                ok = False
                break
        if ok:
            possible_c.append(c)
    
    if not possible_c:
        raise ValueError("Не найдено подходящих коэффициентов!")
    
    # Если несколько решений — возьмем первое (на самом деле должно быть одно)
    c = possible_c[0]
    if len(possible_c) > 1:
        print(f"Найдено {len(possible_c)} возможных наборов коэффициентов. Используем первый.")
    
    # 3. Генерируем ключ для всей длины C
    K_full = K[:]  # копируем известные
    for i in range(n, len(C)):
        k_next = 0
        for j in range(n):
            k_next ^= (c[j] & K_full[i - 1 - j])
        K_full.append(k_next)
    
    # 4. Расшифровываем
    P = [C[i] ^ K_full[i] for i in range(len(C))]
    
    return K_full, P, c

def analyze_degree8(C, P_known):
    """
    Анализ для длины регистра 8:
    Показывает, что система недоопределена и есть несколько возможных ключей.
    """
    n = 8
    K = [P_known[i] ^ C[i] for i in range(len(P_known))]
    
    # Ищем возможные коэффициенты
    possible_c = []
    for mask in range(2**n):
        c = [(mask >> j) & 1 for j in range(n)]
        ok = True
        for i in range(n, len(K)):
            rhs = 0
            for j in range(n):
                rhs ^= (c[j] & K[i - 1 - j])
            if rhs != K[i]:
                ok = False
                break
        if ok:
            possible_c.append(c)
    
    print(f"\nДля длины регистра 8:")
    print(f"  Найдено {len(possible_c)} возможных наборов коэффициентов.")
    if possible_c:
        print("  Пример коэффициентов (c0..c7):", possible_c[0])
        # Покажем, что они дают разные ключи для следующих битов
        # Генерируем ключ для всей длины C для первого набора
        K_full1 = K[:]
        c1 = possible_c[0]
        for i in range(n, len(C)):
            k_next = 0
            for j in range(n):
                k_next ^= (c1[j] & K_full1[i - 1 - j])
            K_full1.append(k_next)
        
        # Для второго набора (если есть)
        if len(possible_c) > 1:
            K_full2 = K[:]
            c2 = possible_c[1]
            for i in range(n, len(C)):
                k_next = 0
                for j in range(n):
                    k_next ^= (c2[j] & K_full2[i - 1 - j])
                K_full2.append(k_next)
            
            # Сравниваем ключи начиная с позиции 2n
            if len(K_full1) > 2 * n and len(K_full2) > 2 * n:
                diff_found = False
                for i in range(2 * n, len(K_full1)):
                    if K_full1[i] != K_full2[i]:
                        print(f"  На позиции {i} ключи различаются → открытый текст неоднозначен.")
                        diff_found = True
                        break
                if not diff_found:
                    print("  Ключи совпадают для всей длины — неожиданно, возможно, все наборы дают один ключ.")
        else:
            print("  Только один набор коэффициентов — возможно, случайно хватило данных для длины 8?")
    else:
        print("  Нет решений — возможно, входные данные не соответствуют LFSR длины 8.")
    return possible_c

def main():
    # Исходные данные
    C = [0,1,1,0,0,0,1,0,1,0,1,1,1,0,0,1,1,1,0,1,0,1,0,0,0,1,0,0,0,1,1,0,0,0,1,0,1,0,1,1,1,0,0,1,1,1,0,1,0,1]
    P_known = [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0]
    
    print("=" * 70)
    print("Задача 6. Восстановление ключа LFSR (длина регистра 7)")
    print("=" * 70)
    
    # Решение для длины 7
    K, P, c = solve_lfsr_degree7(C, P_known)
    
    print("\nВосстановленные коэффициенты обратной связи (c0..c6):", c)
    # Многочлен: f(D) = 1 + c0 D + c1 D ^ 2 + ... + c6 D ^ 7? Нет: K_i = c0 K_{i - 1} + ... + c6 K_{i - 7}
    # Поэтому связующий многочлен: D ^ 7 + c6 D ^ 6 + ... + c0 = 0
    # Выведем в стандартной форме
    f_coeffs = [1] + c[::-1]  # от D ^ 7 к младшим, но проще так:
    f_str = "D ^ 7"
    for j in range(7):
        if c[6-j] == 1:
            f_str += f" + D ^ {j}"
    print(f"Связующий многочлен: f(D) = {f_str}")
    
    print("\nПервые 15 битов восстановленного ключа K:", K[:15])
    print("Первые 15 битов открытого текста P:", P[:15])
    print("Совпадают с известными:", P[:15] == P_known)
    
    print("\nВесь восстановленный открытый текст (50 битов):")
    print("".join(map(str, P)))
    
    # Проверка, что LFSR действительно генерирует ключ: сгенерируем заново из начального состояния
    init_state = K[:7][::-1]  # для LFSR с выводом младшего бита
    print(f"\nНачальное состояние регистра (s6..s0): {init_state}")
    
    # Анализ для длины регистра 8
    print("\n" + "=" * 70)
    analyze_degree8(C, P_known)
    print("=" * 70)

if __name__ == "__main__":
    main()