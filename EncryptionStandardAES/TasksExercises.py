# Задачи и упражнения
# Задача 1. =========================================================================================================================================
"""
Программа для проверки неприводимости многочлена f(x) = x ^ 8 + x ^ 4 + x ^ 3 + x + 1 над GF(2)
на основе математического доказательства.
"""

from itertools import product

# Работаем в поле GF(2)
GF2 = [0, 1]

def poly_add(p1, p2):
    """Сложение многочленов над GF(2) (XOR коэффициентов)."""
    n = max(len(p1), len(p2))
    result = [0] * n
    for i in range(n):
        coeff1 = p1[i] if i < len(p1) else 0
        coeff2 = p2[i] if i < len(p2) else 0
        result[i] = (coeff1 + coeff2) % 2
    return result

def poly_mul(p1, p2):
    """Умножение многочленов над GF(2)."""
    result = [0] * (len(p1) + len(p2) - 1)
    for i, a in enumerate(p1):
        if a == 0:
            continue
        for j, b in enumerate(p2):
            if b == 0:
                continue
            result[i + j] = (result[i + j] + a * b) % 2
    return result

def poly_divmod(p1, p2):
    """
    Деление многочленов над GF(2).
    Возвращает (частное, остаток).
    """
    # Копируем делимое
    remainder = p1[:]
    divisor = p2[:]
    
    # Удаляем ведущие нули
    while len(remainder) > 0 and remainder[-1] == 0:
        remainder.pop()
    while len(divisor) > 0 and divisor[-1] == 0:
        divisor.pop()
    
    if len(divisor) == 0:
        raise ValueError("Деление на нулевой многочлен")
    
    if len(remainder) < len(divisor):
        return [0], remainder
    
    quotient = [0] * (len(remainder) - len(divisor) + 1)
    
    while len(remainder) >= len(divisor) and len(remainder) > 0:
        # Степень разности
        shift = len(remainder) - len(divisor)
        quotient[shift] = 1
        
        # Вычитаем (XOR) divisor * x^shift
        for i in range(len(divisor)):
            if divisor[i] == 1:
                remainder[shift + i] = (remainder[shift + i] + 1) % 2
        
        # Убираем ведущие нули
        while len(remainder) > 0 and remainder[-1] == 0:
            remainder.pop()
    
    return quotient, remainder

def poly_mod(p1, p2):
    """Остаток от деления многочленов над GF(2)."""
    _, remainder = poly_divmod(p1, p2)
    return remainder if remainder else [0]

def poly_str(poly):
    """Красивый вывод многочлена."""
    if not poly or all(c == 0 for c in poly):
        return "0"
    
    terms = []
    for i, coeff in enumerate(poly):
        if coeff == 0:
            continue
        if i == 0:
            terms.append("1")
        elif i == 1:
            terms.append("x")
        else:
            terms.append(f"x ^ {i}")
    
    return " + ".join(reversed(terms))

def evaluate_poly(poly, x, field_elements = None):
    """
    Вычисляет значение многочлена в точке x.
    Для GF(2) просто подстановка.
    """
    result = 0
    for i, coeff in enumerate(poly):
        if coeff == 1:
            result ^= x ** i  # В GF(2) сложение = XOR
    return result

# ----------------------------------------------------------------------
# 1. Заданный многочлен f(x) = x^8 + x^4 + x^3 + x + 1
# Коэффициенты по возрастанию степеней: [const, x, x^2, x^3, x^4, x^5, x^6, x^7, x^8]
f = [1, 1, 0, 1, 1, 0, 0, 0, 1]  # 1 + x + x^3 + x^4 + x^8

print("=" * 60)
print("Проверка неприводимости многочлена над GF(2)")
print(f"f(x) = {poly_str(f)}")
print("=" * 60)

# ----------------------------------------------------------------------
# 2. Проверка корней в GF(2) (линейные множители)
print("\n1. Проверка линейных множителей (корни в GF(2)):")
roots_found = False
for x in GF2:
    val = evaluate_poly(f, x)
    print(f"   f({x}) = {val}")
    if val == 0:
        roots_found = True

if roots_found:
    print("   -> Найден корень! Многочлен приводим.")
else:
    print("   -> Корней нет, линейных множителей нет.")

# ----------------------------------------------------------------------
# 3. Генерация всех неприводимых многочленов заданной степени над GF(2)
def is_irreducible(poly):
    """Проверка неприводимости многочлена над GF(2) перебором."""
    if len(poly) == 0 or all(c == 0 for c in poly):
        return False
    
    # Проверяем корни (линейные множители)
    for x in GF2:
        if evaluate_poly(poly, x) == 0:
            return False
    
    # Проверяем делимость на многочлены меньшей степени
    n = len(poly) - 1  # степень многочлена
    for d in range(2, n // 2 + 1):
        # Генерируем все многочлены степени d
        for coeffs in product([0, 1], repeat = d):
            if coeffs[-1] == 0:  # старший коэффициент должен быть 1
                continue
            divisor = list(coeffs)
            divisor.append(1)  # добавляем старший член
            if all(c == 0 for c in divisor):
                continue
            _, rem = poly_divmod(poly, divisor)
            if rem and all(c == 0 for c in rem):
                return False
    return True

def generate_irreducible_polys(degree):
    """Генерирует все неприводимые многочлены степени degree над GF(2)."""
    result = []
    for coeffs in product([0, 1], repeat = degree):
        if coeffs[-1] == 0:  # старший коэффициент должен быть 1
            continue
        poly = list(coeffs) + [1]
        if is_irreducible(poly):
            result.append(poly)
    return result

# ----------------------------------------------------------------------
# 4. Проверка отсутствия множителей степени 2
print("\n2. Проверка множителей степени 2:")
irr_deg2 = generate_irreducible_polys(2)
print(f"   Неприводимые многочлены степени 2: {[poly_str(p) for p in irr_deg2]}")

has_factor_deg2 = False
for p in irr_deg2:
    _, rem = poly_divmod(f, p)
    if rem and all(c == 0 for c in rem):
        has_factor_deg2 = True
        print(f"   f(x) делится на {poly_str(p)}")
        break
if not has_factor_deg2:
    print("   -> Множителей степени 2 нет.")

# ----------------------------------------------------------------------
# 5. Проверка отсутствия множителей степени 3
print("\n3. Проверка множителей степени 3:")
irr_deg3 = generate_irreducible_polys(3)
print(f"   Неприводимые многочлены степени 3: {[poly_str(p) for p in irr_deg3]}")

has_factor_deg3 = False
for p in irr_deg3:
    _, rem = poly_divmod(f, p)
    if rem and all(c == 0 for c in rem):
        has_factor_deg3 = True
        print(f"   f(x) делится на {poly_str(p)}")
        break
if not has_factor_deg3:
    print("   -> Множителей степени 3 нет.")

# ----------------------------------------------------------------------
# 6. Проверка отсутствия множителей степени 4
print("\n4. Проверка множителей степени 4:")
irr_deg4 = generate_irreducible_polys(4)
print(f"   Неприводимые многочлены степени 4: {[poly_str(p) for p in irr_deg4]}")

has_factor_deg4 = False
for p in irr_deg4:
    _, rem = poly_divmod(f, p)
    if rem and all(c == 0 for c in rem):
        has_factor_deg4 = True
        print(f"   f(x) делится на {poly_str(p)}")
        break
if not has_factor_deg4:
    print("   -> Множителей степени 4 нет.")

# ----------------------------------------------------------------------
# 7. Итоговый вывод
print("\n" + "=" * 60)
print("РЕЗУЛЬТАТ:")

if not roots_found and not has_factor_deg2 and not has_factor_deg3 and not has_factor_deg4:
    print("✅ Многочлен f(x) НЕПРИВОДИМ над GF(2).")
    print("   Поле GF(2^8) может быть построено по этому многочлену.")
else:
    print("❌ Многочлен f(x) ПРИВОДИМ над GF(2).")

print("=" * 60)

# ----------------------------------------------------------------------
# 8. Дополнительно: прямая проверка с помощью библиотечной функции (если доступна)
try:
    import sympy as sp
    from sympy import Poly, GF
    
    print("\nДополнительная проверка с использованием SymPy:")
    x = sp.symbols('x')
    f_sym = Poly(x ** 8 + x ** 4 + x ** 3 + x + 1, x, modulus = 2)
    if f_sym.is_irreducible:
        print("   ✅ SymPy подтверждает: многочлен неприводим.")
    else:
        print("   ❌ SymPy: многочлен приводим.")
except ImportError:
    print("\n   (Для дополнительной проверки установите SymPy: pip install sympy)")

# Задача 2. =========================================================================================================================================
import sympy as sp
from sympy.polys.domains import FF

def find_inverse_mod(g_coeffs, mod_coeffs):
    """
    Находит обратный многочлен g'(y) такой, что
    g(y) * g'(y) ≡ 1 (mod mod(y))
    над полем Z_2.
    
    Параметры:
        g_coeffs : list[int] - коэффициенты многочлена g(y) (начиная со старшей степени, например [1, 1, 1, 1] для y ^ 3 + y ^ 2 + y + 1)
        mod_coeffs: list[int] - коэффициенты многочлена-модуля (например [1, 0, 0, 0, 1] для y ^ 4 + 1)
    
    Возвращает:
        список коэффициентов обратного многочлена или None, если обратного нет.
    """
    y = sp.symbols('y')
    
    # Строим многочлены над полем Z_2
    F2 = FF(2)
    g_poly = sp.Poly(g_coeffs, y, domain = F2)
    mod_poly = sp.Poly(mod_coeffs, y, domain = F2)
    
    # Проверяем взаимную простоту (обратимый ⇔ gcd=1)
    gcd_poly = sp.gcd(g_poly, mod_poly)
    if gcd_poly.degree() > 0:
        print(f"НОД(g, mod) = {gcd_poly} ≠ 1 → обратного не существует")
        return None
    
    # Расширенный алгоритм Евклида в кольце многочленов
    # В sympy есть функция invert
    try:
        inv_poly = sp.invert(g_poly, mod_poly)
        # Приводим к списку коэффициентов по возрастанию степени
        coeffs = inv_poly.all_coeffs()[::-1]  # от младшей к старшей
        return coeffs
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# ============ Примеры ============

if __name__ == "__main__":
    # Модуль: y^4 + 1 (в Z_2 это коэффициенты [1, 0, 0, 0, 1])
    mod = [1, 0, 0, 0, 1]
    
    # Пример 1: g(y) = y^3 + y^2 + y + 1  (как в вашем тексте)
    print("=== Пример 1: g = [1, 1, 1, 1] ===")
    g1 = [1, 1, 1, 1]  # y^3 + y^2 + y + 1
    inv1 = find_inverse_mod(g1, mod)
    if inv1 is not None:
        print(f"g'(y) = {inv1} (коэфф. от младшей степени)")
        # Проверка
        y = sp.symbols('y')
        F2 = FF(2)
        g_poly = sp.Poly(g1, y, domain = F2)
        inv_poly = sp.Poly(inv1, y, domain = F2)
        mod_poly = sp.Poly(mod, y, domain = F2)
        prod = (g_poly * inv_poly) % mod_poly
        print(f"Проверка: g * g' mod (y ^ 4 + 1) = {prod}")
    
    # Пример 2: g(y) = y^2 + y + 1  (обратимый, т.к. не делится на y+1)
    print("\n=== Пример 2: g = [1, 1, 1] ===")
    g2 = [1, 1, 1]  # y^2 + y + 1
    inv2 = find_inverse_mod(g2, mod)
    if inv2 is not None:
        print(f"g'(y) = {inv2} (коэфф. от младшей степени)")
        y = sp.symbols('y')
        F2 = FF(2)
        g_poly = sp.Poly(g2, y, domain = F2)
        inv_poly = sp.Poly(inv2, y, domain = F2)
        mod_poly = sp.Poly(mod, y, domain = F2)
        prod = (g_poly * inv_poly) % mod_poly
        print(f"Проверка: g * g' mod (y ^ 4 + 1) = {prod}")
    
    # Пример 3: g(y) = y + 1 (необратим, т.к. делит модуль)
    print("\n=== Пример 3: g = [1, 1] ===")
    g3 = [1, 1]  # y + 1
    inv3 = find_inverse_mod(g3, mod)
    if inv3 is not None:
        print(f"g'(y) = {inv3}")
    else:
        print("Обратного нет (что и ожидалось)")