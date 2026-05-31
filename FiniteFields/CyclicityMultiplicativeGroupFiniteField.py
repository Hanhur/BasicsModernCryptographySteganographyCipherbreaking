# 3. Цикличность мультипликативной группы конечного поля
def factorize(n: int):
    """
    Возвращает множество простых делителей числа n.
    """
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def is_primitive_root(g: int, p: int, factors_of_phi: set) -> bool:
    """
    Проверяет, является ли g порождающим элементом (первообразным корнем)
    мультипликативной группы поля F_p.
    
    g — кандидат,
    p — простое число (характеристика поля),
    factors_of_phi — множество простых делителей числа p - 1.
    
    Условие: g ^ ( (p - 1) / q ) != 1 (mod p) для всех простых q | (p - 1).
    """
    if g % p == 0:
        return False
    for q in factors_of_phi:
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True

def find_primitive_roots(p: int):
    """
    Возвращает список всех порождающих элементов поля F_p.
    p должно быть простым числом.
    """
    if p < 2:
        return []
    phi = p - 1
    factors = factorize(phi)
    roots = []
    for g in range(2, p):
        if is_primitive_root(g, p, factors):
            roots.append(g)
    return roots

def demo_F7():
    """
    Демонстрация на примере F_7 из текста:
    3 — порождающий, 2 — не порождающий.
    """
    p = 7
    print(f"Поле F_{p}")
    print(f"Мультипликативная группа F_{p}* порядка {p - 1}")
    
    # Проверяем элемент 3
    g1 = 3
    order_g1 = None
    # Найдем порядок 3 перебором (только для маленьких p)
    for exp in range(1, p):
        if pow(g1, exp, p) == 1:
            order_g1 = exp
            break
    print(f"Элемент {g1}: порядок = {order_g1} -> {'порождающий' if order_g1 == p-1 else 'не порождающий'}")
    
    # Проверяем элемент 2
    g2 = 2
    order_g2 = None
    for exp in range(1, p):
        if pow(g2, exp, p) == 1:
            order_g2 = exp
            break
    print(f"Элемент {g2}: порядок = {order_g2} -> {'порождающий' if order_g2 == p - 1 else 'не порождающий'}")
    
    # Степени 3 (порождающего)
    print(f"\nСтепени {g1} (порождающий):")
    powers = [pow(g1, i, p) for i in range(1, p)]
    print("  " + " ".join(f"{g1} ^ {i} = {val}" for i, val in enumerate(powers, start = 1)))
    print(f"  Все элементы F_{p}*: {set(powers)}")
    
    # Степени 2 (не порождающего)
    print(f"\nСтепени {g2} (не порождающий):")
    powers2 = []
    val = 1
    for i in range(1, p):
        val = (val * g2) % p
        powers2.append(val)
    print("  " + " ".join(f"{g2} ^ {i} = {val}" for i, val in enumerate(powers2, start = 1)))
    print(f"  Множество получено: {set(powers2)} (не совпадает с F_{p}* )")
    
def main():
    # Пример 1: F_7 из текста
    demo_F7()
    
    print("\n" + "=" * 60 + "\n")
    
    # Пример 2: F_13
    p = 13
    print(f"Поле F_{p}")
    roots = find_primitive_roots(p)
    print(f"Все порождающие элементы F_{p}*: {roots}")
    print(f"Количество порождающих: {len(roots)} (φ({p - 1}) = {p - 2}? Нет, φ({p  -1}) = { __import__('math').gcd(p - 1, p - 1) if p - 1==1 else None } — правильно вычислено как {len(roots)})")
    
    # Вычислим φ(p - 1) вручную для проверки
    phi_val = p-1
    for q in factorize(p - 1):
        phi_val = phi_val // q * (q - 1)
    print(f"φ({p - 1}) = {phi_val} — совпадает с количеством порождающих")
    
    # Покажем, что все порождающие имеют порядок p-1
    print("\nПроверка порядка для каждого порождающего:")
    for g in roots:
        order = 1
        for exp in range(1, p):
            if pow(g, exp, p) == 1:
                order = exp
                break
        print(f"  g = {g}, порядок = {order}")


if __name__ == "__main__":
    main()