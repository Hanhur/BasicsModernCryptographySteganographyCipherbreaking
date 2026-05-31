# Задачи и упражнения
# Задача 1. Построить конечные поля F24 , F33 и F52 , указав соответствующие многочлены f(x). 
# Найти порождающие элементы мультипликативных групп построенных полей. 
# Будет ли элемент х (в каждом случае свой) порождать мультипликативную группу?
import sympy as sp
from sympy import symbols, Poly
from sympy.ntheory import factorint

def build_finite_field(p, n, poly_coeffs):
    """
    Строит конечное поле GF(p ^ n) по модулю заданного полинома.
    poly_coeffs: список коэффициентов от старшей степени к младшей.
    Возвращает: (множество элементов поля, функцию приведения, символ x, порядок поля)
    """
    x = symbols('x')
    # Многочлен над GF(p)
    modulus = Poly(poly_coeffs, x, modulus = p)
    
    # Функция для приведения элемента (числа или полинома) к элементу поля
    def reduce_element(expr):
        if isinstance(expr, int):
            expr = Poly(expr, x, modulus = p)
        elif isinstance(expr, Poly):
            expr = expr.set_modulus(p)
        else:
            expr = Poly(expr, x, modulus = p)
        # Делим с остатком на modulus
        _, rem = expr.div(modulus)
        return rem
    
    return reduce_element, x, modulus, p ** n

def is_generator(reduce_func, element, order, p, modulus):
    """
    Проверяет, порождает ли element мультипликативную группу поля.
    """
    if element == 0:
        return False
    
    # Получаем все простые делители порядка группы
    factors = factorint(order)
    
    for q in factors.keys():
        # Вычисляем element^(order/q) в поле
        exp_val = 1
        base = element
        
        # Возведение в степень в поле
        exp = order // q
        result = Poly(1, modulus.gens[0], modulus = p)
        base_poly = base if isinstance(base, Poly) else Poly(base, modulus.gens[0], modulus = p)
        
        while exp > 0:
            if exp & 1:
                result = (result * base_poly) % modulus
            base_poly = (base_poly * base_poly) % modulus
            exp >>= 1
        
        result = reduce_func(result)
        if result == Poly(1, modulus.gens[0], modulus = p):
            return False
    
    return True

def poly_to_str(poly, x):
    """Преобразует полином в читаемую строку"""
    if poly == 0:
        return "0"
    terms = []
    coeffs = poly.all_coeffs()
    deg = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = deg - i
        if coeff == 0:
            continue
        if power == 0:
            terms.append(f"{coeff}")
        elif power == 1:
            terms.append(f"{coeff} * {x}" if coeff != 1 else f"{x}")
        else:
            terms.append(f"{coeff} * {x} ^ {power}" if coeff != 1 else f"{x} ^ {power}")
    return " + ".join(terms)

def main():
    x = symbols('x')
    
    # --- Поле F_{2 ^ 4} ---
    print("=" * 60)
    print("Поле F_{2 ^ 4}")
    print("=" * 60)
    p1, n1 = 2, 4
    poly1 = [1, 0, 0, 1, 1]  # x ^ 4 + x + 1
    reduce1, _, mod1, order1 = build_finite_field(p1, n1, poly1)
    
    print(f"Многочлен: {poly_to_str(Poly(poly1, x, modulus = p1), 'x')}")
    print(f"Порядок мультипликативной группы: {order1 - 1}")
    
    # Элемент x
    elem_x1 = Poly([1, 0], x, modulus = p1)  # Полином x
    elem_x1_reduced = reduce1(elem_x1)
    is_gen1 = is_generator(reduce1, elem_x1_reduced, order1 - 1, p1, mod1)
    
    print(f"Элемент x порождает группу? {'Да' if is_gen1 else 'Нет'}")
    if is_gen1:
        print(f"Порождающий элемент: x")
    else:
        # Поиск порождающего элемента
        print("Поиск порождающего элемента...")
        # Пробуем элементы вида a * x + b
        found = False
        for a in range(p1):
            for b in range(p1):
                if a == 0 and b == 0:
                    continue
                test_elem = Poly([a, b], x, modulus = p1)
                test_elem_reduced = reduce1(test_elem)
                if is_generator(reduce1, test_elem_reduced, order1 - 1, p1, mod1):
                    print(f"Порождающий элемент: {poly_to_str(test_elem, 'x')}")
                    found = True
                    break
            if found:
                break
        if not found:
            print("Не удалось найти порождающий элемент (проверьте многочлен)")
    
    # --- Поле F_{3 ^ 3} ---
    print("\n" + "=" * 60)
    print("Поле F_{3 ^ 3}")
    print("=" * 60)
    p2, n2 = 3, 3
    poly2 = [1, 0, 2, 1]  # x ^ 3 + 2x + 1
    reduce2, _, mod2, order2 = build_finite_field(p2, n2, poly2)
    
    print(f"Многочлен: {poly_to_str(Poly(poly2, x, modulus = p2), 'x')}")
    print(f"Порядок мультипликативной группы: {order2 - 1}")
    
    # Элемент x
    elem_x2 = Poly([1, 0], x, modulus = p2)  # Полином x
    elem_x2_reduced = reduce2(elem_x2)
    is_gen2 = is_generator(reduce2, elem_x2_reduced, order2 - 1, p2, mod2)
    
    print(f"Элемент x порождает группу? {'Да' if is_gen2 else 'Нет'}")
    if is_gen2:
        print(f"Порождающий элемент: x")
    else:
        # Поиск порождающего элемента
        print("Поиск порождающего элемента...")
        found = False
        # Пробуем элементы вида a*x^2 + b*x + c
        for a in range(p2):
            for b in range(p2):
                for c in range(p2):
                    if a == 0 and b == 0 and c == 0:
                        continue
                    test_elem = Poly([a, b, c], x, modulus = p2)
                    test_elem_reduced = reduce2(test_elem)
                    if is_generator(reduce2, test_elem_reduced, order2 - 1, p2, mod2):
                        print(f"Порождающий элемент: {poly_to_str(test_elem, 'x')}")
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            print("Не удалось найти порождающий элемент (проверьте многочлен)")
    
    # --- Поле F_{5 ^ 2} ---
    print("\n" + "=" * 60)
    print("Поле F_{5 ^ 2}")
    print("=" * 60)
    p3, n3 = 5, 2
    poly3 = [1, 0, 2]  # x ^ 2 + 2
    reduce3, _, mod3, order3 = build_finite_field(p3, n3, poly3)
    
    print(f"Многочлен: {poly_to_str(Poly(poly3, x, modulus = p3), 'x')}")
    print(f"Порядок мультипликативной группы: {order3 - 1}")
    
    # Элемент x
    elem_x3 = Poly([1, 0], x, modulus = p3)  # Полином x
    elem_x3_reduced = reduce3(elem_x3)
    is_gen3 = is_generator(reduce3, elem_x3_reduced, order3 - 1, p3, mod3)
    
    print(f"Элемент x порождает группу? {'Да' if is_gen3 else 'Нет'}")
    if is_gen3:
        print(f"Порождающий элемент: x")
    else:
        # Поиск порождающего элемента
        print("Поиск порождающего элемента...")
        found = False
        # Пробуем элементы вида a * x + b
        for a in range(p3):
            for b in range(p3):
                if a == 0 and b == 0:
                    continue
                test_elem = Poly([a, b], x, modulus = p3)
                test_elem_reduced = reduce3(test_elem)
                if is_generator(reduce3, test_elem_reduced, order3 - 1, p3, mod3):
                    print(f"Порождающий элемент: {poly_to_str(test_elem, 'x')}")
                    found = True
                    break
            if found:
                break
        if not found:
            print("Не удалось найти порождающий элемент (проверьте многочлен)")

if __name__ == "__main__":
    main()

# Задача 2. Доказать, что в любом поле Fpk содержится единственный (тривиальный) корень р-й степени из 1.
import sympy as sp
from sympy import symbols, Poly
from itertools import product

def build_finite_field(p, k, poly_coeffs = None):
    """
    Строит конечное поле GF(p^k)
    
    Параметры:
    p - характеристика поля
    k - степень расширения
    poly_coeffs - коэффициенты неприводимого многочлена степени k (опционально)
    
    Возвращает:
    elements - список всех элементов поля в виде полиномов
    reduce_func - функция приведения к элементу поля
    modulus - модулярный полином
    """
    x = symbols('x')
    
    # Если многочлен не задан, нужно найти неприводимый многочлен степени k
    if poly_coeffs is None:
        # Для простоты используем стандартные неприводимые многочлены
        if p == 2 and k == 4:
            poly_coeffs = [1, 0, 0, 1, 1]  # x ^ 4 + x + 1
        elif p == 3 and k == 3:
            poly_coeffs = [1, 0, 2, 1]     # x ^ 3 + 2x + 1
        elif p == 5 and k == 2:
            poly_coeffs = [1, 0, 2]        # x ^ 2 + 2
        else:
            raise ValueError(f"Для p = {p}, k = {k} нужно явно задать неприводимый многочлен")
    
    modulus = Poly(poly_coeffs, x, modulus = p)
    
    # Функция приведения элемента к полю
    def reduce_element(expr):
        if isinstance(expr, int):
            expr = Poly(expr, x, modulus = p)
        elif isinstance(expr, (list, tuple)):
            expr = Poly(expr, x, modulus = p)
        elif not isinstance(expr, Poly):
            expr = Poly(expr, x, modulus = p)
        
        expr = expr.set_modulus(p)
        _, rem = expr.div(modulus)
        return rem
    
    # Генерация всех элементов поля
    elements = []
    # Элементы поля - это полиномы степени < k с коэффициентами из GF(p)
    for coeffs in product(range(p), repeat = k):
        poly = Poly(list(coeffs), x, modulus = p)
        elements.append(poly)
    
    return elements, reduce_element, modulus

def is_root_of_unity(element, p, reduce_func, modulus):
    """
    Проверяет, является ли элемент корнем p-й степени из 1
    То есть проверяет: element^p = 1 в поле
    """
    if element == 0:
        return False
    
    x = modulus.gens[0]
    
    # Вычисляем element^p
    result = Poly(1, x, modulus = p)
    base = element
    exp = p
    
    # Быстрое возведение в степень
    while exp > 0:
        if exp & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exp >>= 1
    
    result = reduce_func(result)
    
    # Проверяем, равно ли result 1
    one = Poly(1, x, modulus = p)
    return result == one

def polynomial_to_string(poly, x):
    """Преобразует полином в читаемую строку"""
    if poly == 0 or poly == Poly(0, x):
        return "0"
    
    terms = []
    coeffs = poly.all_coeffs()
    deg = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        power = deg - i
        if coeff == 0:
            continue
        
        # Приводим коэффициент к числу
        if hasattr(coeff, 'p'):
            coeff_val = coeff.args[0] if coeff.args else 0
        else:
            coeff_val = int(coeff) if hasattr(coeff, '__int__') else coeff
        
        if power == 0:
            terms.append(str(coeff_val))
        elif power == 1:
            if coeff_val == 1:
                terms.append(f"{x}")
            elif coeff_val == -1:
                terms.append(f" - {x}")
            else:
                terms.append(f"{coeff_val} * {x}")
        else:
            if coeff_val == 1:
                terms.append(f"{x} ^ {power}")
            elif coeff_val == -1:
                terms.append(f" - {x} ^ {power}")
            else:
                terms.append(f"{coeff_val} * {x} ^ {power}")
    
    return " + ".join(terms)

def demonstrate_pth_root_unity(p, k, poly_coeffs = None, field_name = None):
    """
    Демонстрирует, что в поле GF(p ^ k) есть единственный корень p-й степени из 1
    """
    if field_name is None:
        field_name = f"F_{p} ^ {{{k}}}"
    
    print("=" * 70)
    print(f"Поле {field_name}")
    print("=" * 70)
    
    # Строим поле
    elements, reduce_func, modulus = build_finite_field(p, k, poly_coeffs)
    x = modulus.gens[0]
    
    # Выводим информацию о поле
    print(f"Характеристика поля: {p}")
    print(f"Степень расширения: {k}")
    print(f"Размер поля: {p} ^ {k} = {p ** k}")
    print(f"Модулярный многочлен: {polynomial_to_string(modulus, x)}")
    print(f"Порядок мультипликативной группы: {p ** k - 1}")
    print()
    
    # Находим все корни p-й степени из 1
    roots = []
    for elem in elements:
        if is_root_of_unity(elem, p, reduce_func, modulus):
            roots.append(elem)
    
    # Выводим результаты
    print(f"Уравнение: x ^ {p} = 1")
    print(f"Найдено корней: {len(roots)}")
    print()
    
    if len(roots) == 1:
        print("✓ Единственный корень:")
        root_str = polynomial_to_string(roots[0], x)
        if roots[0] == Poly(1, x, modulus = p):
            print(f"  x = {root_str} (единица поля)")
        else:
            print(f"  x = {root_str}")
        print()
        print("Доказательство:")
        print(f"  1. В поле характеристики {p} выполняется (a + b) ^ {p} = a ^ {p} + b ^ {p}")
        print(f"  2. Тогда (x - 1) ^ {p} = x ^ {p} - 1")
        print(f"  3. Если x ^ {p} = 1, то (x - 1) ^ {p} = 0")
        print(f"  4. В поле нет делителей нуля, поэтому x - 1 = 0")
        print(f"  5. Следовательно, x = 1") 
    else:
        print("✗ Найдено несколько корней (что противоречит теории!)")
        print("Корни:")
        for i, root in enumerate(roots, 1):
            print(f"  {i}. {polynomial_to_string(root, x)}")
    
    print()

def main():
    """
    Демонстрация для различных конечных полей
    """
    # Пример 1: Поле F_{2 ^ 4}
    demonstrate_pth_root_unity(
        p = 2, k = 4,
        poly_coeffs = [1, 0, 0, 1, 1],  # x ^ 4 + x + 1
        field_name = "F_{2 ^ 4}"
    )
    
    # Пример 2: Поле F_{3 ^ 3}
    demonstrate_pth_root_unity(
        p = 3, k = 3,
        poly_coeffs = [1, 0, 2, 1],     # x ^ 3 + 2x + 1
        field_name = "F_{3 ^ 3}"
    )
    
    # Пример 3: Поле F_{5 ^ 2}
    demonstrate_pth_root_unity(
        p = 5, k = 2,
        poly_coeffs = [1, 0, 2],        # x ^ 2 + 2
        field_name = "F_{5 ^ 2}"
    )
    
    # Дополнительный пример: Простое поле F_7
    print("=" * 70)
    print("Простое поле F_7")
    print("=" * 70)
    print(f"Характеристика: 7")
    print(f"Размер поля: 7")
    print(f"Уравнение: x ^ 7 = 1")
    print()
    
    # В простом поле F_7 проверяем все элементы
    roots = []
    for x in range(7):
        if pow(x, 7, 7) == 1 % 7:
            roots.append(x)
    
    print(f"Найдено корней: {len(roots)}")
    if len(roots) == 1:
        print(f"✓ Единственный корень: x = {roots[0]}")
    else:
        print(f"✗ Найдено корней: {roots}")
    
    print("\n" + "=" * 70)
    print("Вывод:")
    print("=" * 70)
    print("Во всех рассмотренных полях характеристики p")
    print("уравнение x ^ p = 1 имеет единственное решение x = 1,")
    print("что подтверждает теоретическое доказательство.")

if __name__ == "__main__":
    main()

# Задача 3. Пусть поле F24 построено по многочлену f(x) = х4 + х3 + 1 Е Z2[x]. 
# Перечислить все элементы а Е F24 , для которых разрешимо уравнение у3 = а.
import sympy as sp
from sympy import symbols, Poly
from itertools import product

def build_field_f16():
    """
    Строит поле F_16 = F_2[x] / (x ^ 4 + x ^ 3 + 1)
    Возвращает:
    - elements: список всех элементов поля (полиномы степени < 4)
    - mul: функцию умножения в поле
    - pow3: функцию возведения в куб
    - x: символ
    - modulus: модулярный полином
    """
    x = symbols('x')
    p = 2
    # Многочлен x ^ 4 + x ^ 3 + 1
    modulus = Poly([1, 1, 0, 0, 1], x, modulus = p)  # коэффициенты: x ^ 4 + x ^ 3 + 1
    
    # Все элементы поля: полиномы степени < 4 с коэффициентами из F_2
    elements = []
    for coeffs in product(range(p), repeat = 4):
        poly = Poly(list(coeffs), x, modulus = p)
        elements.append(poly)
    
    def reduce_element(expr):
        """Приводит элемент к полю (остаток от деления на modulus)"""
        if isinstance(expr, int):
            expr = Poly(expr, x, modulus = p)
        if not isinstance(expr, Poly):
            expr = Poly(expr, x, modulus = p)
        expr = expr.set_modulus(p)
        _, rem = expr.div(modulus)
        return rem
    
    def multiply(a, b):
        """Умножение в поле"""
        prod = (a * b) % modulus
        return prod
    
    def cube(y):
        """Возведение в куб в поле"""
        return multiply(multiply(y, y), y)
    
    return elements, multiply, cube, x, modulus, reduce_element

def poly_to_string(poly, x):
    """Преобразует полином в читаемую строку"""
    if poly == 0 or poly == Poly(0, x):
        return "0"
    
    terms = []
    coeffs = poly.all_coeffs()
    deg = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        power = deg - i
        if coeff == 0:
            continue
        
        # Приводим коэффициент к числу
        if hasattr(coeff, 'p'):
            coeff_val = coeff.args[0] if coeff.args else 0
        else:
            coeff_val = int(coeff) if hasattr(coeff, '__int__') else coeff
        
        if power == 0:
            terms.append(f"{coeff_val}")
        elif power == 1:
            if coeff_val == 1:
                terms.append(f"{x}")
            else:
                terms.append(f"{coeff_val} * {x}")
        else:
            if coeff_val == 1:
                terms.append(f"{x} ^ {power}")
            else:
                terms.append(f"{coeff_val} * {x} ^ {power}")
    
    return " + ".join(terms)

def main():
    print("=" * 70)
    print("Задача 8.3: Поле F_2 ^ 4 по многочлену f(x) = x ^ 4 + x ^ 3 + 1")
    print("=" * 70)
    
    # Строим поле
    elements, multiply, cube, x, modulus, reduce_element = build_field_f16()
    
    print(f"Многочлен: {poly_to_string(modulus, x)}")
    print(f"Характеристика: 2")
    print(f"Размер поля: 2 ^ 4 = {len(elements)}")
    print()
    
    # Находим все a, для которых уравнение y ^ 3 = a разрешимо
    solvable_elements = []
    
    print("Перебор всех элементов поля...")
    print()
    
    for a in elements:
        # Проверяем, существует ли y такой, что y ^ 3 = a
        found = False
        for y in elements:
            if cube(y) == a:
                found = True
                break
        if found:
            solvable_elements.append(a)
    
    # Выводим результаты
    print(f"Найдено элементов a, для которых уравнение y ^ 3 = a разрешимо: {len(solvable_elements)}")
    print()
    
    print("Список таких элементов a (в виде полиномов от x):")
    print("-" * 50)
    for i, elem in enumerate(solvable_elements, 1):
        elem_str = poly_to_string(elem, x)
        if elem == Poly(1, x, modulus = 2):
            elem_str = "1"
        elif elem == Poly(0, x):
            elem_str = "0"
        print(f"{i:2d}. {elem_str}")
    
    print()
    print("=" * 70)
    print("Проверка теоретического результата:")
    print("=" * 70)
    print("По теореме: элементы, являющиеся кубами в F_16* — это подгруппа порядка 5")
    print("(все элементы порядка, делящего 5) плюс 0.")
    print(f"Всего должно быть 1 (ноль) + 5 = 6 элементов.")
    print(f"Получено: {len(solvable_elements)} элементов.")
    
    if len(solvable_elements) == 6:
        print("✓ Результат совпадает с теорией.")
    
    print()
    print("Дополнительно: найдём порождающий элемент мультипликативной группы")
    print("и выразим кубы через него.")
    
    # Найдём примитивный элемент (порождающий F_16*)
    # Проверяем элементы на порядок 15
    primitive_element = None
    for elem in elements:
        if elem == Poly(0, x):
            continue
        
        # Проверяем, что elem ^ 5 != 1 и elem ^ 3 != 1
        elem_cube = cube(elem)
        elem_5 = multiply(multiply(multiply(multiply(elem, elem), elem), elem), elem)
        
        # В F_16* порядок 15 если elem ^ 5 != 1 и elem ^ 3 != 1
        one = Poly(1, x, modulus = 2)
        if elem_cube != one and elem_5 != one:
            # Проверим, что elem ^ 15 = 1 (должно быть по теореме Лагранжа)
            primitive_element = elem
            break
    
    if primitive_element is not None:
        print(f"Найден примитивный элемент: g = {poly_to_string(primitive_element, x)}")
        print("Тогда кубами являются: g ^ 0, g ^ 3, g ^ 6, g ^ 9, g ^ 12 и 0.")
        print("Проверим:")
        
        # Вычисляем степени примитивного элемента
        g = primitive_element
        g_powers = [Poly(1, x, modulus = 2)]  # g ^ 0 = 1
        current = g
        for i in range(1, 15):
            g_powers.append(current)
            current = multiply(current, g)
        
        cubes_from_g = [g_powers[0], g_powers[3], g_powers[6], g_powers[9], g_powers[12]]
        
        print("Кубы из теории (через g):")
        for i, elem in enumerate(cubes_from_g):
            print(f"  g ^ {{{i * 3}}} = {poly_to_string(elem, x)}")
        
        # Сравниваем с найденными кубами (исключая 0)
        found_cubes_nonzero = [e for e in solvable_elements if e != Poly(0, x)]
        print()
        print("Найденные кубы (ненулевые):")
        for elem in found_cubes_nonzero:
            print(f"  {poly_to_string(elem, x)}")
        
        # Проверяем совпадение множеств
        set_found = set(str(e) for e in found_cubes_nonzero)
        set_theory = set(str(e) for e in cubes_from_g)
        
        if set_found == set_theory:
            print("✓ Множества совпадают")
        else:
            print("✗ Множества не совпадают (возможны проблемы с представлением)")
    else:
        print("Не удалось найти примитивный элемент автоматически.")

if __name__ == "__main__":
    main()

# Задача 4. Доказать, что в поле F26 для любого а Е F26 разрешимо уравнение у5 = а.
import sympy as sp
from sympy import symbols, Poly
from itertools import product

def build_field_f64():
    """
    Строит поле F_64 = F_2[x] / (x ^ 6 + x + 1)
    Возвращает:
    - elements: список всех элементов поля
    - multiply: функция умножения
    - power5: функция возведения в 5-ю степень
    - x: символ
    - modulus: модулярный полином
    - reduce_element: функция приведения
    """
    x = symbols('x')
    p = 2
    # Неприводимый многочлен x ^ 6 + x + 1 для F_64
    # Коэффициенты: x ^ 6 + x + 1 = 1 * x ^ 6 + 0 * x ^ 5 + 0 * x ^ 4 + 0 * x ^ 3 + 0 * x ^ 2 + 1 * x + 1
    modulus = Poly([1, 0, 0, 0, 0, 1, 1], x, modulus = p)
    
    # Все элементы поля: полиномы степени < 6 с коэффициентами из F_2
    elements = []
    for coeffs in product(range(p), repeat = 6):
        poly = Poly(list(coeffs), x, modulus = p)
        elements.append(poly)
    
    def reduce_element(expr):
        """Приводит элемент к полю (остаток от деления на modulus)"""
        if isinstance(expr, int):
            expr = Poly(expr, x, modulus = p)
        if not isinstance(expr, Poly):
            expr = Poly(expr, x, modulus = p)
        expr = expr.set_modulus(p)
        _, rem = expr.div(modulus)
        return rem
    
    def multiply(a, b):
        """Умножение в поле"""
        prod = (a * b) % modulus
        return prod
    
    def power5(y):
        """Возведение в 5-ю степень: y ^ 5 = y ^ 2 * y ^ 2 * y"""
        y2 = multiply(y, y)
        y4 = multiply(y2, y2)
        return multiply(y4, y)
    
    return elements, multiply, power5, x, modulus, reduce_element

def poly_to_string(poly, x, max_deg = 6):
    """Преобразует полином в читаемую строку (только для малых полей)"""
    if poly == 0 or poly == Poly(0, x):
        return "0"
    
    terms = []
    coeffs = poly.all_coeffs()
    deg = len(coeffs) - 1
    
    for i, coeff in enumerate(coeffs):
        power = deg - i
        if coeff == 0:
            continue
        
        if hasattr(coeff, 'p'):
            coeff_val = coeff.args[0] if coeff.args else 0
        else:
            coeff_val = int(coeff) if hasattr(coeff, '__int__') else coeff
        
        if power == 0:
            terms.append("1")
        elif power == 1:
            terms.append("x")
        else:
            terms.append(f"x ^ {power}")
    
    if not terms:
        return "0"
    return " + ".join(terms)

def element_to_index(elem, elements):
    """Находит индекс элемента в списке (для отображения)"""
    for i, e in enumerate(elements):
        if e == elem:
            return i
    return -1

def main():
    print("=" * 70)
    print("Задача 4: Поле F_2 ^ 6")
    print("Доказательство, что для любого a ∈ F_64 уравнение y ^ 5 = a разрешимо")
    print("=" * 70)
    
    # Строим поле
    elements, multiply, power5, x, modulus, reduce_element = build_field_f64()
    
    print(f"Многочлен: x ^ 6 + x + 1")
    print(f"Характеристика: 2")
    print(f"Размер поля: 2 ^ 6 = {len(elements)}")
    print(f"Порядок мультипликативной группы: {2 ** 6 - 1} = 63")
    print()
    
    # Проверяем для всех a, существует ли y: y ^ 5 = a
    print("Проверка уравнения y ^ 5 = a для всех a ∈ F_64...")
    print()
    
    unsolvable_elements = []
    solvable_count = 0
    
    # Для каждого a ищем y
    for a in elements:
        found = False
        for y in elements:
            if power5(y) == a:
                found = True
                break
        if found:
            solvable_count += 1
        else:
            unsolvable_elements.append(a)
    
    print(f"Найдено элементов a, для которых уравнение разрешимо: {solvable_count} из {len(elements)}")
    print(f"Неразрешимых элементов: {len(unsolvable_elements)}")
    
    if len(unsolvable_elements) == 0:
        print("\n✓ РЕЗУЛЬТАТ: Для ВСЕХ a ∈ F_64 уравнение y ^ 5 = a имеет решение!")
    else:
        print("\n✗ Найдены неразрешимые элементы (противоречит теории):")
        for a in unsolvable_elements[:10]:  # Покажем первые 10
            print(f"  {poly_to_string(a, x)}")
    
    print()
    print("=" * 70)
    print("Теоретическое обоснование:")
    print("=" * 70)
    print("1. |F_64 ^ * | = 63 = 3²·7")
    print("2. Рассмотрим отображение φ: y → y ^ 5 на F_64 ^ *")
    print("3. Ядро: y ^ 5 = 1 ⇒ |ker φ| = gcd(5,63) = 1")
    print("4. Значит, φ инъективно, а т.к. группа конечна, то и биективно")
    print("5. Следовательно, каждый ненулевой a является 5-й степенью")
    print("6. Для a = 0 решение: y = 0")
    print("7. ИТОГО: ∀a∈F_64 ∃y∈F_64: y ^ 5 = a")
    print()
    
    # Дополнительно: проверим, что отображение y → y ^ 5 биективно
    print("=" * 70)
    print("Проверка биективности отображения y → y ^ 5 на F_64 ^ *")
    print("=" * 70)
    
    # Ненулевые элементы
    nonzero_elements = [e for e in elements if e != Poly(0, x)]
    
    # Вычисляем образы
    images = [power5(y) for y in nonzero_elements]
    
    # Проверяем, все ли образы различны
    unique_images = set(str(img) for img in images)
    
    print(f"Ненулевых элементов: {len(nonzero_elements)}")
    print(f"Различных образов: {len(unique_images)}")
    
    if len(unique_images) == len(nonzero_elements):
        print("✓ Отображение инъективно (различные y дают различные y ^ 5)")
        print("✓ В конечной группе инъективность ⇔ биективность")
        print("✓ Значит, каждый ненулевой элемент является 5-й степенью")
    else:
        print("✗ Отображение не инъективно (противоречие!)")
    
    # Покажем несколько примеров
    print()
    print("Примеры решений уравнения y ^ 5 = a:")
    print("-" * 50)
    
    # Найдём несколько решений для демонстрации
    examples = []
    for a in nonzero_elements[:5]:  # Первые 5 ненулевых элементов
        for y in nonzero_elements:
            if power5(y) == a:
                examples.append((a, y))
                break
    
    for a, y in examples:
        a_str = poly_to_string(a, x) if a != Poly(1, x) else "1"
        y_str = poly_to_string(y, x)
        print(f"a = {a_str:15s}  →  y = {y_str}")
    
    print()
    print("=" * 70)
    print("ВЫВОД: Уравнение y ^ 5 = a разрешимо для ЛЮБОГО a ∈ F_64")
    print("=" * 70)

if __name__ == "__main__":
    main()