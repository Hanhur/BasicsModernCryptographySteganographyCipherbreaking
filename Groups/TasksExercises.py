# Задачи и упражнения
# Задача 1. =========================================================================================================================================
from math import gcd

# Группа Z_21^*
units = [n for n in range(1, 21) if gcd(n, 21) == 1]

# Функция для прямого перебора решений x^2 ≡ b (mod 21) в Z_21^*
def brute_force_solutions(b):
    solutions = []
    for x in units:
        if (x * x) % 21 == b % 21:
            solutions.append(x)
    return solutions

print("Аналитический результат (по выводу задачи) и проверка перебором:\n")
print("b\tаналитически\tрешения (перебором)")

for b in units:
    # Аналитический результат
    if b % 3 == 2:
        analytic = 0
    elif b % 3 == 1:
        if b % 7 in (1, 2, 4):
            analytic = 4
        else:
            analytic = 0
    else:
        analytic = 0

    # Перебор
    sols = brute_force_solutions(b)
    brute = len(sols)

    # Проверка
    if analytic != brute:
        print(f"ОШИБКА для b={b}: аналитически {analytic}, перебором {brute}")
    else:
        print(f"{b}\t{analytic}\t\t{sols}")

# Задача 2. =========================================================================================================================================
from math import gcd

def is_cyclic_analytical():
    """
    Аналитическое решение на основе теории:
    Z_24^* ≅ Z_8^* × Z_3^* ≅ (C2 × C2) × C2 ≅ C2 × C2 × C2
    Это элементарная абелева 2-группа, нециклическая.
    """
    return False

def get_units_mod_n(n):
    """Возвращает список всех обратимых элементов по модулю n."""
    return [a for a in range(1, n) if gcd(a, n) == 1]

def multiplicative_order(a, n, units):
    """
    Вычисляет порядок элемента a в мультипликативной группе Z_n^*.
    """
    if a not in units:
        return None
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
    return order

def is_cyclic_bruteforce(n):
    """
    Перебором проверяет, является ли Z_n^* циклической.
    Группа циклическая, если существует элемент порядка φ(n).
    """
    units = get_units_mod_n(n)
    group_order = len(units)
    
    for a in units:
        if multiplicative_order(a, n, units) == group_order:
            return True
    return False

# Основная программа
n = 24
units = get_units_mod_n(n)
group_order = len(units)

print(f"Мультипликативная группа Z_{n}^*")
print(f"Элементы: {units}")
print(f"Порядок группы: φ({n}) = {group_order}\n")

# Аналитический метод
analytical_result = is_cyclic_analytical()
print(f"Аналитический вывод (на основе теории): {'ЦИКЛИЧЕСКАЯ' if analytical_result else 'НЕ ЦИКЛИЧЕСКАЯ'}")

# Переборный метод
bruteforce_result = is_cyclic_bruteforce(n)
print(f"Переборный вывод (проверка порядков элементов): {'ЦИКЛИЧЕСКАЯ' if bruteforce_result else 'НЕ ЦИКЛИЧЕСКАЯ'}")

# Дополнительно: вычислим порядки всех элементов
print("\nПорядки элементов в Z_24^*:")
for a in units:
    ord_a = multiplicative_order(a, n, units)
    print(f"{a:2d} → порядок = {ord_a}")

# Проверка, есть ли элемент порядка group_order
max_order = max(multiplicative_order(a, n, units) for a in units)
print(f"\nМаксимальный порядок элемента: {max_order}")
print(f"Размер группы: {group_order}")
if max_order == group_order:
    print("→ Есть элемент порядка |G| → ГРУППА ЦИКЛИЧЕСКАЯ")
else:
    print("→ Нет элемента порядка |G| → ГРУППА НЕ ЦИКЛИЧЕСКАЯ")

# Задача 3. =========================================================================================================================================
import math

def phi(n):
    """Функция Эйлера: количество чисел от 1 до n, взаимно простых с n."""
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result

def multiplicative_order(a, p):
    """Порядок элемента a в мультипликативной группе Z_p^* (p простое)."""
    # Группа имеет порядок p-1
    order = 1
    current = a % p
    while current != 1:
        current = (current * a) % p
        order += 1
    return order

def find_generators(p):
    """Находит все порождающие элементы (первообразные корни) по модулю p."""
    # Группа Z_p^* циклическая порядка p-1
    group_order = p - 1
    generators = []
    
    # Для всех a от 2 до p-1 (1 не подходит, так как 1^n = 1)
    for a in range(2, p):
        if multiplicative_order(a, p) == group_order:
            generators.append(a)
    
    return generators

# Основная программа
p = 23
group_order = p - 1  # 22

print(f"Мультипликативная группа Z_{p}^*")
print(f"Порядок группы: {group_order}\n")

# Аналитическое решение
generators_count_analytic = phi(group_order)
print(f"Аналитический метод: количество порождающих = φ({group_order}) = φ({group_order}) = {generators_count_analytic}")

# Переборное решение (проверка)
generators = find_generators(p)
generators_count_bruteforce = len(generators)

print(f"\nПереборный метод: найдено {generators_count_bruteforce} порождающих элементов")
print(f"Порождающие элементы: {generators}")

# Проверка соответствия
if generators_count_analytic == generators_count_bruteforce:
    print(f"\n✅ Результаты совпадают: {generators_count_analytic} порождающих элементов")
else:
    print(f"\n❌ Ошибка: аналитически {generators_count_analytic}, перебором {generators_count_bruteforce}")

# Дополнительно: покажем порядки всех элементов для наглядности
print("\nПорядки элементов в Z_23^*:")
for a in range(1, p):
    if math.gcd(a, p) == 1:  # a принадлежит группе
        order_a = multiplicative_order(a, p)
        print(f"{a:2d} → порядок = {order_a}")

# Задача 4. =========================================================================================================================================
from itertools import product

def is_cyclic_group(elements, mult_table):
    """
    Проверяет, является ли группа (elements, mult_table) циклической.
    elements: список элементов (строки/числа)
    mult_table: словарь {(a, b): a * b}
    """
    n = len(elements)
    for g in elements:
        order = 1
        current = g
        # Ищем порядок элемента g
        while current != elements[0]:  # elements[0] — нейтральный элемент
            current = mult_table[(current, g)]
            order += 1
            if order > n:
                break
        if order == n:
            return True
    return False

def build_Cn(n, name = "a"):
    """Строит циклическую группу порядка n с образующим name."""
    elements = [f"{name}^{i}" for i in range(n)]
    neutral = elements[0]
    mult_table = {}
    for i in range(n):
        for j in range(n):
            mult_table[(elements[i], elements[j])] = elements[(i + j) % n]
    return elements, mult_table, neutral

def build_Cn_direct_Cm(n, m, name1 = "a", name2 = "b"):
    """Строит прямое произведение C_n × C_m."""
    elements = [(i, j) for i in range(n) for j in range(m)]
    neutral = (0, 0)
    mult_table = {}
    for a in elements:
        for b in elements:
            mult_table[(a, b)] = ((a[0] + b[0]) % n, (a[1] + b[1]) % m)
    # Преобразуем в читаемый вид
    str_elements = [f"{name1} ^ {i}{name2} ^ {j}" for (i, j) in elements]
    str_to_tuple = {str_elements[k]: elements[k] for k in range(len(elements))}
    tuple_to_str = {v: k for k, v in str_to_tuple.items()}
    
    new_mult_table = {}
    for (x, y) in product(elements, repeat = 2):
        new_mult_table[(tuple_to_str[x], tuple_to_str[y])] = tuple_to_str[mult_table[(x, y)]]
    
    return str_elements, new_mult_table, tuple_to_str[neutral]

def build_semidirect_Cq_by_Cp(p, q, aut_order, aut_map_int):
    """
    Строит полупрямое произведение C_q ⋊ C_p,
    где aut_map_int: Z_q^* → элемент порядка p, заданный умножением на k.
    Группа G: { (x, y) | x in C_q, y in C_p }
    Умножение: (x1, y1) * (x2, y2) = (x1 + k ^ {y1} * x2, y1 + y2)
    Здесь k — число в Z_q^* порядка p.
    """
    if pow(aut_map_int, p, q) != 1 or aut_map_int == 1:
        raise ValueError("aut_map_int не имеет порядка p в Z_q^*")
    
    # Элементы: пары (x, y), x = 0..q - 1, y = 0..p-1
    elements = [(x, y) for x in range(q) for y in range(p)]
    neutral = (0, 0)
    
    mult_table = {}
    for a in elements:
        for b in elements:
            x1, y1 = a
            x2, y2 = b
            # (x1, y1) * (x2, y2) = (x1 + k ^ {y1} * x2 mod q, y1 + y2 mod p)
            new_x = (x1 + pow(aut_map_int, y1, q) * x2) % q
            new_y = (y1 + y2) % p
            mult_table[(a, b)] = (new_x, new_y)
    
    # Преобразуем в читаемый вид
    str_elements = [f"a ^ {x}b ^ {y}" for (x, y) in elements]
    tuple_to_str = {elements[i]: str_elements[i] for i in range(len(elements))}
    str_to_tuple = {v: k for k, v in tuple_to_str.items()}
    
    new_mult_table = {}
    for x, y in product(str_elements, repeat = 2):
        new_mult_table[(x, y)] = tuple_to_str[mult_table[(str_to_tuple[x], str_to_tuple[y])]]
    
    return str_elements, new_mult_table, tuple_to_str[neutral]

# Пример 1: C_3 × C_5 (абелева, порядка 15)
p, q = 3, 5
elements1, table1, neutral1 = build_Cn_direct_Cm(p, q, "a", "b")
print(f"Группа C_{p} × C_{q}: порядок = {len(elements1)}")
print(f"Циклическая? {is_cyclic_group(elements1, table1)}")
print("Пример элемента:", elements1[1])
print()

# Пример 2: C_3 × C_3 (абелева, порядка 9)
p2 = 3
elements2, table2, neutral2 = build_Cn_direct_Cm(p2, p2, "x", "y")
print(f"Группа C_{p2} × C_{p2}: порядок = {len(elements2)}")
print(f"Циклическая? {is_cyclic_group(elements2, table2)}")
print("Она нециклическая, так как все элементы (кроме нейтрального) порядка 3")
print()

# Пример 3: Неабелева группа порядка 21 = C_7 ⋊ C_3
q3, p3 = 7, 3
# В C_7^* элемент 2 имеет порядок 3 (2^3=8≡1 mod7)
aut_int = 2
elements3, table3, neutral3 = build_semidirect_Cq_by_Cp(p3, q3, p3, aut_int)
print(f"Неабелева группа C_{q3} ⋊ C_{p3} порядка {len(elements3)}")
print(f"Циклическая? {is_cyclic_group(elements3, table3)}")
# Проверим неабелевость: найдём a, b с a*b != b*a
for a in elements3[:5]:  # берём несколько элементов
    for b in elements3[:5]:
        if table3[(a, b)] != table3[(b, a)]:
            print(f"Неабелева: {a} * {b} = {table3[(a, b)]} != {table3[(b, a)]} = {b} * {a}")
            break
    else:
        continue
    break
else:
    print("Похоже абелева? Ошибка в построении.")