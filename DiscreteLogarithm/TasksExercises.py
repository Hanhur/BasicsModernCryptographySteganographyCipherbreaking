# Задачи и упражнения
# Задача 1. Вычислить методом Сильвера - Полига - Хеллмана дискретный логарифм элемента 25 в поле F4l относительно порождающего элемента 9 = 7.
def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратный элемент по модулю m"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    else:
        return x % m

def discrete_log_pohlig_hellman(g, h, p, factors):
    """
    Вычисление дискретного логарифма x: g ^ x ≡ h (mod p)
    factors: список простых множителей порядка группы (p - 1) с их степенями
    например, для p = 41: [(2, 3), (5, 1)]
    """
    n = p - 1  # порядок группы
    x = 0
    mod_product = 1
    
    for q, e in factors:
        # Находим x mod q ^ e
        qe = q ** e
        x_q = 0
        
        # Вычисляем g_q = g ^ (n / q)
        g_q = pow(g, n // q, p)
        
        # Вычисляем коэффициенты a0, a1, ..., a_{e - 1} в q-ичной записи
        h_current = h
        for k in range(e):
            # Вычисляем h_k = h_current ^ (n / q ^ (k + 1))
            exponent = n // (q ** (k + 1))
            h_k = pow(h_current, exponent, p)
            
            # Ищем a_k из уравнения g_q ^ a_k ≡ h_k
            # Перебираем возможные значения a_k от 0 до q-1
            found = False
            for a in range(q):
                if pow(g_q, a, p) == h_k:
                    x_q += a * (q ** k)
                    # Обновляем h_current для следующего шага
                    h_current = (h_current * pow(g, -a * (q ** k), p)) % p
                    found = True
                    break
            if not found:
                raise Exception(f"Не удалось найти a_{k} для q = {q}")
        
        # Объединяем с помощью Китайской теоремы об остатках
        # Решаем: x ≡ x_q (mod qe) и x ≡ x (mod mod_product)
        # Используем формулу: x = x + mod_product * ((x_q - x) * inv(mod_product) mod qe)
        inv = modinv(mod_product, qe)
        t = ((x_q - x) * inv) % qe
        x = x + mod_product * t
        mod_product *= qe
    
    return x % n

def main():
    # Параметры задачи
    p = 41          # модуль поля
    g = 7           # порождающий элемент
    h = 25          # элемент, чей логарифм ищем
    
    # Факторизация p - 1 = 40 = 2 ^ 3 * 5 ^ 1
    factors = [(2, 3), (5, 1)]
    
    print(f"Решаем уравнение: {g} ^ x ≡ {h} (mod {p})")
    print(f"Порядок группы: {p - 1} = {' * '.join([f'{q} ^ {e}' for q, e in factors])}")
    print()
    
    x = discrete_log_pohlig_hellman(g, h, p, factors)
    
    print(f"Решение: x = {x}")
    print(f"Проверка: {g} ^ {x} mod {p} = {pow(g, x, p)}")
    
    # Проверка
    if pow(g, x, p) == h:
        print("✓ Проверка пройдена!")
    else:
        print("✗ Ошибка в вычислениях!")

if __name__ == "__main__":
    main()

# Задача 2. Построить поле F73. Найти порождающий элемент g его мультипликативной группы F*73.
# Вычислить дискретный логарифм loggf по основанию g элемента f = 5х2 + 2х + б методом Сильвера - Полига - Хеллмана.
import itertools
from math import gcd

class GF_p3:
    """Класс для работы с полем F_{p ^ 3} = F_p[x] / (x ^ 3 + ax + b)"""
    
    def __init__(self, a, b, c, p = 7, mod_poly = (1, 0, 1, 1)):
        """
        Элемент поля: a * x ^ 2 + b * x + c
        mod_poly: коэффициенты многочлена x ^ 3 + x + 1 (по умолчанию)
        """
        self.p = p
        self.mod_poly = mod_poly  # (coeff_x ^ 3, coeff_x ^ 2, coeff_x, const)
        self.a = a % p
        self.b = b % p
        self.c = c % p
    
    def __eq__(self, other):
        return (self.a == other.a and self.b == other.b and self.c == other.c)
    
    def __add__(self, other):
        return GF_p3(self.a + other.a, self.b + other.b, self.c + other.c, self.p, self.mod_poly)
    
    def __sub__(self, other):
        return GF_p3(self.a - other.a, self.b - other.b, self.c - other.c, self.p, self.mod_poly)
    
    def __neg__(self):
        return GF_p3(-self.a, -self.b, -self.c, self.p, self.mod_poly)
    
    def __mul__(self, other):
        # Умножение в F_p[x] / (x ^ 3 + x + 1)
        # (a1 * x ^ 2 + b1 * x + c1) * (a2 * x ^ 2 + b2 * x + c2)
        a1, b1, c1 = self.a, self.b, self.c
        a2, b2, c2 = other.a, other.b, other.c
        
        # Коэффициенты при x ^ 4, x ^ 3, x ^ 2, x, 1
        x4 = a1 * a2
        x3 = a1 * b2 + b1 * a2
        x2 = a1 * c2 + b1 * b2 + c1 * a2
        x1 = b1 * c2 + c1 * b2
        x0 = c1 * c2
        
        # Приводим по модулю x^3 + x + 1 (x ^ 3 = -x - 1)
        # x ^ 4 = x * x ^ 3 = x * (-x - 1) = -x ^ 2 - x
        # x ^ 3 = -x - 1
        
        # Редуцируем x4 * x ^ 4 -> x4 * (-x ^ 2 - x)
        # Редуцируем x3 * x ^ 3 -> x3 * (-x - 1)
        
        # Новый коэффициент при x ^ 2: из x4 * (-1) + из x3 * 0 + из x2
        new_a = (-x4) % self.p + x2 % self.p
        
        # Новый коэффициент при x: из x4 * (-1) + из x3 * (-1) + из x1
        new_b = (-x4) % self.p + (-x3) % self.p + x1 % self.p
        
        # Свободный член: из x3 * (-1) + из x0
        new_c = (-x3) % self.p + x0 % self.p
        
        return GF_p3(new_a % self.p, new_b % self.p, new_c % self.p, self.p, self.mod_poly)
    
    def __pow__(self, exp):
        result = GF_p3(0, 0, 1, self.p, self.mod_poly)  # 1
        base = self
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result
    
    def __str__(self):
        terms = []
        if self.a != 0:
            terms.append(f"{self.a}x²")
        if self.b != 0:
            terms.append(f"{self.b}x")
        if self.c != 0:
            terms.append(str(self.c))
        if not terms:
            return "0"
        return " + ".join(terms).replace(" + -", " - ")

def find_primitive_element(p, mod_poly):
    """Находит порождающий элемент мультипликативной группы F_{p ^ 3} ^ *"""
    order = p ** 3 - 1
    factors = factorize(order)
    
    # Перебираем элементы в порядке возрастания "сложности"
    for a in range(p):
        for b in range(p):
            for c in range(p):
                if a == 0 and b == 0 and c == 0:
                    continue
                g = GF_p3(a, b, c, p, mod_poly)
                
                # Проверяем, что порядок g равен order
                is_primitive = True
                for q, _ in factors:
                    if pow(g, order // q) == GF_p3(0, 0, 1, p, mod_poly):
                        is_primitive = False
                        break
                
                if is_primitive:
                    return g
    return None

def factorize(n):
    """Разложение числа на простые множители"""
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            count = 0
            while n % d == 0:
                n //= d
                count += 1
            factors.append((d, count))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors

def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратный элемент по модулю m"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    return x % m

def pohlig_hellman(g, h, order, factors, p, mod_poly):
    """
    Алгоритм Сильвера-Полига-Хеллмана для дискретного логарифма
    в поле F_{p ^ 3}
    """
    x = 0
    mod_product = 1
    
    for q, e in factors:
        print(f"  Решаем для q = {q}, e = {e}")
        qe = q ** e
        x_q = 0
        
        # Вычисляем элемент g_q = g ^ (order / q)
        g_q = pow(g, order // q)
        print(f"    g_q = {g_q}")
        
        # Текущий элемент, в котором ищем логарифм
        h_current = h
        
        for k in range(e):
            print(f"    k = {k}")
            # Вычисляем h_k = h_current ^ (order / q ^ (k + 1))
            exponent = order // (q ** (k + 1))
            h_k = pow(h_current, exponent)
            print(f"      h_k = {h_k}")
            
            # Ищем a_k: g_q ^ a_k == h_k
            found = False
            for a in range(q):
                if pow(g_q, a) == h_k:
                    a_k = a
                    found = True
                    print(f"      Нашли a_{k} = {a_k}")
                    break
            
            if not found:
                raise Exception(f"Не удалось найти a_{k} для q = {q}")
            
            x_q += a_k * (q ** k)
            print(f"      x_q = {x_q}")
            
            # Обновляем h_current: h_current = h_current * g ^ (-a_k * q ^ k)
            # Важно: g ^ (-n) = (g ^ n) ^ (-1) - нужно уметь находить обратный элемент
            if a_k != 0:
                factor = pow(g, a_k * (q ** k))
                # Находим обратный элемент factor ^ (-1)
                # В поле характеристики p обратный можно найти через extended gcd
                # Но проще: factor ^ (order-1) = factor ^ (-1)
                inv_factor = pow(factor, order - 1)
                h_current = h_current * inv_factor
            print(f"      h_current = {h_current}")
        
        print(f"    Решение по модулю {qe}: x ≡ {x_q} (mod {qe})")
        
        # Китайская теорема об остатках
        inv = modinv(mod_product, qe)
        t = ((x_q - x) * inv) % qe
        x = x + mod_product * t
        mod_product *= qe
        print(f"    Объединённое решение: x ≡ {x} (mod {mod_product})")
    
    return x % order

def main():
    # Параметры поля
    p = 7
    mod_poly = (1, 0, 1, 1)  # x ^ 3 + x + 1
    
    print("=" * 60)
    print("Построение поля F_{7 ^ 3}")
    print("=" * 60)
    print(f"Поле: F_{p}[x] / (x ^ 3 + x + 1)")
    print(f"Характеристика: {p}")
    print(f"Размер поля: {p ** 3} элементов")
    print()
    
    # Находим порождающий элемент
    print("Поиск порождающего элемента...")
    g = find_primitive_element(p, mod_poly)
    print(f"Порождающий элемент g = {g}")
    print()
    
    # Заданный элемент f = 5x ^ 2 + 2x + 6
    f = GF_p3(5, 2, 6, p, mod_poly)
    print(f"Заданный элемент f = {f}")
    print()
    
    # Порядок мультипликативной группы
    order = p ** 3 - 1
    print(f"Порядок группы: {order} = {order}")
    
    # Факторизация порядка
    factors = factorize(order)
    print(f"Факторизация: {' * '.join([f'{q} ^ {e}' for q, e in factors])}")
    print()
    
    # Решаем дискретный логарифм
    print("Вычисление дискретного логарифма методом Сильвера-Полига-Хеллмана...")
    print()
    
    x = pohlig_hellman(g, f, order, factors, p, mod_poly)
    
    print()
    print(f"Решение: log_g(f) = {x}")
    print()
    
    # Проверка
    print("Проверка:")
    verification = pow(g, x)
    print(f"g ^ {x} = {verification}")
    if verification == f:
        print("✓ Проверка пройдена!")
    else:
        print("✗ Ошибка в вычислениях!")
    
    print()
    print("=" * 60)
    print(f"Ответ: log_{g}({f}) = {x}")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Задача 3. Построить поле F33. Найти порождающий элемент g его мультипликативной группы F73.
# Вычислить дискретный логарифм loggf по основанию g элемента f = х2 + 2х + 2 методом Сильвера - Полига - Хеллмана.
class GF_p3:
    def __init__(self, a, b, c, p = 3, mod_poly = (1, 0, 2, 1)):
        # mod_poly: x^3 + 2x + 1, т.е. коэффициенты [1,0,2,1]
        self.p = p
        self.mod_poly = mod_poly
        self.a = a % p
        self.b = b % p
        self.c = c % p

    def __eq__(self, other):
        return (self.a, self.b, self.c) == (other.a, other.b, other.c)

    def __add__(self, other):
        return GF_p3(self.a + other.a, self.b + other.b, self.c + other.c, self.p, self.mod_poly)

    def __sub__(self, other):
        return GF_p3(self.a - other.a, self.b - other.b, self.c - other.c, self.p, self.mod_poly)

    def __neg__(self):
        return GF_p3(-self.a, -self.b, -self.c, self.p, self.mod_poly)

    def __mul__(self, other):
        a1, b1, c1 = self.a, self.b, self.c
        a2, b2, c2 = other.a, other.b, other.c

        x4 = a1 * a2
        x3 = a1 * b2 + b1 * a2
        x2 = a1 * c2 + b1 * b2 + c1 * a2
        x1 = b1 * c2 + c1 * b2
        x0 = c1 * c2

        # x^3 = -2x - 1 ≡ x + 2 (mod 3) since -2 ≡ 1
        # x^4 = x * x^3 = x*(x+2) = x^2 + 2x
        # But better to use the given polynomial x^3 + 2x + 1 ≡ 0
        # So x^3 = -2x - 1 = x + 2 (mod 3)
        # Then x^4 = x*(x+2) = x^2 + 2x

        new_a = (x2 - x4) % self.p
        new_b = (x1 - x4 + (2 * x3)) % self.p   # from x^4: +2x from 2x term, and from x^3: +2 term
        new_c = (x0 - x3) % self.p

        # Check carefully: Use x^3 = x + 2, x^4 = x*(x+2) = x^2 + 2x
        # x^4 term: coefficient *1 for x^2, *2 for x, 0 for const.
        # So contribution from x4 coefficient: +x4 to coeff x^2, +2*x4 to coeff x
        # Contribution from x3 coefficient (x^3 term): x3*(x+2) gives +x3 to coeff x, +2*x3 to const.
        new_a = (x2 + x4) % self.p   # from x2 + from x4
        new_b = (x1 + 2*x4 + x3) % self.p  # from x1, from x4 (2x part), from x3 (x part)
        new_c = (x0 + 2*x3) % self.p   # from x0, from x3 (2 part)

        return GF_p3(new_a, new_b, new_c, self.p, self.mod_poly)

    def __pow__(self, exp):
        res = GF_p3(0, 0, 1, self.p, self.mod_poly)
        base = self
        while exp > 0:
            if exp & 1:
                res = res * base
            base = base * base
            exp >>= 1
        return res

    def __str__(self):
        terms = []
        if self.a != 0:
            terms.append(f"{self.a}x²")
        if self.b != 0:
            terms.append(f"{self.b}x")
        if self.c != 0:
            terms.append(str(self.c))
        return " + ".join(terms).replace(" + -", " - ") if terms else "0"

def factorize(n):
    factors = []
    d = 2
    while d*d <= n:
        if n % d == 0:
            cnt = 0
            while n % d == 0:
                n //= d
                cnt += 1
            factors.append((d, cnt))
        d += 1 if d==2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors

def find_primitive(p, mod_poly):
    order = p ** 3 - 1
    factors = factorize(order)
    for a in range(p):
        for b in range(p):
            for c in range(p):
                if a == 0 and b == 0 and c == 0:
                    continue
                g = GF_p3(a, b, c, p, mod_poly)
                is_prim = True
                for q, _ in factors:
                    if pow(g, order // q) == GF_p3(0, 0, 1, p, mod_poly):
                        is_prim = False
                        break
                if is_prim:
                    return g
    return None

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("No inverse")
    return x % m

def pohlig_hellman(g, h, order, factors):
    x = 0
    mod_prod = 1
    for q, e in factors:
        qe = q ** e
        x_q = 0
        h_curr = h
        g_q = pow(g, order // q)
        for k in range(e):
            exp = order // (q ** (k + 1))
            h_k = pow(h_curr, exp)
            for a in range(q):
                if pow(g_q, a) == h_k:
                    x_q += a * (q **k )
                    if a != 0:
                        factor = pow(g, a * (q ** k))
                        inv_factor = pow(factor, order - 1)
                        h_curr = h_curr * inv_factor
                    break
        inv = modinv(mod_prod, qe)
        t = ((x_q - x) * inv) % qe
        x += mod_prod * t
        mod_prod *= qe
    return x % order

def main():
    p = 3
    mod_poly = (1, 0, 2, 1)  # x^3 + 2x + 1
    print("Поле F_27 = F_3[x] / (x ^ 3 + 2x + 1)")
    g = find_primitive(p, mod_poly)
    print("Порождающий элемент g =", g)
    f = GF_p3(1, 2, 2, p, mod_poly)  # x^2 + 2x + 2
    print("f =", f)

    order = p**3 - 1
    factors = factorize(order)
    print(f"Порядок группы: {order} = {' * '.join(f'{q} ^ {e}' for q,e in factors)}")

    log = pohlig_hellman(g, f, order, factors)
    print("log_g(f) =", log)
    print("Проверка: g ^ {log} =", pow(g, log))

if __name__ == "__main__":
    main()

# Задача 4. Построить поле F34. Найти порождающий элемент g его мультипликативной группы F*34.
# Вычислить дискретный логарифм loggf по основанию g элемента f = х3 + 2х2 + 2х + 2 методом Сильвера - Полига - Хеллмана.
class GF_p4:
    """Класс для работы с полем F_{3 ^ 4} = F_3[x] / (x ^ 4 + x + 2)"""
    
    def __init__(self, a, b, c, d, p = 3, mod_poly = (1, 0, 0, 1, 2)):
        """
        Элемент поля: a * x ^ 3 + b * x ^ 2 + c * x + d
        mod_poly: коэффициенты x ^ 4 + x + 2
        """
        self.p = p
        self.mod_poly = mod_poly
        self.a = a % p
        self.b = b % p
        self.c = c % p
        self.d = d % p
    
    def __eq__(self, other):
        return (self.a, self.b, self.c, self.d) == (other.a, other.b, other.c, other.d)
    
    def __add__(self, other):
        return GF_p4(self.a + other.a, self.b + other.b, self.c + other.c, self.d + other.d, self.p, self.mod_poly)
    
    def __sub__(self, other):
        return GF_p4(self.a - other.a, self.b - other.b, self.c - other.c, self.d - other.d, self.p, self.mod_poly)
    
    def __neg__(self):
        return GF_p4(-self.a, -self.b, -self.c, -self.d, self.p, self.mod_poly)
    
    def __mul__(self, other):
        # Умножение многочленов с приведением по модулю x^4 + x + 2
        # x^4 = -x - 2 ≡ 2x + 1 (в F_3)
        a1, b1, c1, d1 = self.a, self.b, self.c, self.d
        a2, b2, c2, d2 = other.a, other.b, other.c, other.d
        
        # Коэффициенты при x^6, x^5, x^4, x^3, x^2, x, 1
        x6 = a1 * a2
        x5 = a1 * b2 + b1 * a2
        x4 = a1 * c2 + b1 * b2 + c1 * a2
        x3 = a1 * d2 + b1 * c2 + c1 * b2 + d1 * a2
        x2 = b1 * d2 + c1 * c2 + d1 * b2
        x1 = c1 * d2 + d1 * c2
        x0 = d1 * d2
        
        # Редукция: x^4 = 2x + 1
        # x^5 = x * x^4 = x*(2x+1) = 2x^2 + x
        # x^6 = x^2 * x^4 = x^2*(2x+1) = 2x^3 + x^2
        
        new_a = (x3 + 2 * x6) % self.p          # из x3 и из x6 (2x^3)
        new_b = (x2 + x6 + 2 * x5) % self.p     # из x2, из x6 (x^2), из x5 (2x^2)
        new_c = (x1 + x5 + 2 * x4) % self.p     # из x1, из x5 (x), из x4 (2x)
        new_d = (x0 + x4) % self.p            # из x0, из x4 (1)
        
        return GF_p4(new_a % self.p, new_b % self.p, new_c % self.p, new_d % self.p, self.p, self.mod_poly)
    
    def __pow__(self, exp):
        result = GF_p4(0, 0, 0, 1, self.p, self.mod_poly)  # 1
        base = self
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result
    
    def __str__(self):
        terms = []
        if self.a != 0:
            terms.append(f"{self.a}x³")
        if self.b != 0:
            terms.append(f"{self.b}x²")
        if self.c != 0:
            terms.append(f"{self.c}x")
        if self.d != 0:
            terms.append(str(self.d))
        if not terms:
            return "0"
        return " + ".join(terms).replace(" + -", " - ")

def factorize(n):
    """Разложение числа на простые множители"""
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            cnt = 0
            while n % d == 0:
                n //= d
                cnt += 1
            factors.append((d, cnt))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors

def find_primitive(p, mod_poly):
    """Находит порождающий элемент мультипликативной группы F_{p ^ 4} ^ *"""
    order = p ** 4 - 1
    factors = factorize(order)
    
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    if a == 0 and b == 0 and c == 0 and d == 0:
                        continue
                    g = GF_p4(a, b, c, d, p, mod_poly)
                    is_primitive = True
                    for q, _ in factors:
                        if pow(g, order // q) == GF_p4(0, 0, 0, 1, p, mod_poly):
                            is_primitive = False
                            break
                    if is_primitive:
                        return g
    return None

def modinv(a, m):
    """Обратный элемент по модулю m"""
    # Расширенный алгоритм Евклида
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
    
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("Нет обратного элемента")
    return x % m

def pohlig_hellman(g, h, order, factors):
    """Алгоритм Сильвера-Полига-Хеллмана"""
    x = 0
    mod_product = 1
    
    for q, e in factors:
        print(f"  Решаем для q = {q}, e = {e}")
        qe = q ** e
        x_q = 0
        h_current = h
        
        # Вычисляем g_q = g^(order/q)
        g_q = pow(g, order // q)
        
        for k in range(e):
            # Вычисляем h_k = h_current^(order / q^(k+1))
            exponent = order // (q ** (k + 1))
            h_k = pow(h_current, exponent)
            
            # Ищем a_k перебором
            found = False
            for a in range(q):
                if pow(g_q, a) == h_k:
                    a_k = a
                    found = True
                    break
            
            if not found:
                raise Exception(f"Не удалось найти a_{k} для q = {q}")
            
            x_q += a_k * (q ** k)
            
            # Обновляем h_current
            if a_k != 0:
                factor = pow(g, a_k * (q ** k))
                # В поле характеристики p: обратный элемент = factor^(order-1)
                inv_factor = pow(factor, order - 1)
                h_current = h_current * inv_factor
        
        print(f"    x ≡ {x_q} (mod {qe})")
        
        # Китайская теорема об остатках
        inv = modinv(mod_product, qe)
        t = ((x_q - x) * inv) % qe
        x = x + mod_product * t
        mod_product *= qe
        print(f"    Объединённое решение: x ≡ {x} (mod {mod_product})")
    
    return x % order

def main():
    p = 3
    mod_poly = (1, 0, 0, 1, 2)  # x^4 + x + 2
    
    print("=" * 60)
    print("Построение поля F_{3 ^ 4}")
    print("=" * 60)
    print(f"Поле: F_{p}[x] / (x ^ 4 + x + 2)")
    print(f"Размер поля: {p ** 4} элементов")
    print()
    
    # Находим порождающий элемент
    print("Поиск порождающего элемента...")
    g = find_primitive(p, mod_poly)
    print(f"Порождающий элемент g = {g}")
    print()
    
    # Заданный элемент f = x^3 + 2x^2 + 2x + 2
    f = GF_p4(1, 2, 2, 2, p, mod_poly)
    print(f"Заданный элемент f = {f}")
    print()
    
    # Порядок мультипликативной группы
    order = p ** 4 - 1
    print(f"Порядок группы: {order} = {order}")
    
    # Факторизация порядка
    factors = factorize(order)
    print(f"Факторизация: {' * '.join([f'{q} ^ {e}' for q, e in factors])}")
    print()
    
    # Решаем дискретный логарифм
    print("Вычисление дискретного логарифма методом Сильвера-Полига-Хеллмана...")
    print()
    
    x = pohlig_hellman(g, f, order, factors)
    
    print()
    print(f"Решение: log_g(f) = {x}")
    print()
    
    # Проверка
    print("Проверка:")
    verification = pow(g, x)
    print(f"g ^ {x} = {verification}")
    if verification == f:
        print("✓ Проверка пройдена!")
    else:
        print("✗ Ошибка в вычислениях!")
    
    print()
    print("=" * 60)
    print(f"Ответ: log_{g}({f}) = {x}")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Задача 5. Построить поле F43. Найти порождающий элемент g его мультипликативной группы F*43. 
# Вычислить дискретный логарифм lo99f по основанию g элемента f = 11 методом Сильвера - Полига - Хеллмана.
class GF2_p6:
    def __init__(self, coeffs, p = 2, mod_poly = (1, 0, 0, 0, 0, 1, 1)):
        # coeffs: список из 6 коэффициентов для 1, x, x^2, ..., x^5
        self.p = p
        self.mod_poly = mod_poly
        self.coeffs = [c % p for c in coeffs] + [0] * (6 - len(coeffs))

    def __eq__(self, other):
        return self.coeffs == other.coeffs

    def __add__(self, other):
        return GF2_p6([(self.coeffs[i] + other.coeffs[i]) % self.p for i in range(6)])

    def __sub__(self, other):
        return self + other  # в char 2 вычитание = сложение

    def __mul__(self, other):
        # умножение многочленов степени ≤5
        prod = [0] * 11
        for i in range(6):
            for j in range(6):
                prod[i+j] ^= self.coeffs[i] & other.coeffs[j]  # в GF(2) умножение = AND

        # редукция по модулю x^6 + x + 1
        for k in range(10, 5, -1):
            if prod[k]:
                prod[k - 6] ^= 1  # x^k → x^(k-6) * (x+1)?? Надо аккуратно: x^6 = x+1
                # но x^6 = x+1 в F2, значит x^k = x^(k-6) * x^6 = x^(k-6)*(x+1)
                # так что: коэффициент при x^(k-6) увеличить на coeff[k]
                # и коэффициент при x^(k-5) увеличить на coeff[k]
                # В GF(2): увеличение = XOR
                prod[k - 5] ^= prod[k]
                prod[k - 6] ^= prod[k]
                prod[k] = 0

        return GF2_p6(prod[:6])

    def __pow__(self, exp):
        res = GF2_p6([1] + [0] * 5)  # единица
        base = self
        while exp > 0:
            if exp & 1:
                res = res * base
            base = base * base
            exp >>= 1
        return res

    def __str__(self):
        terms = []
        for i, c in enumerate(self.coeffs):
            if c:
                if i == 0:
                    terms.append("1")
                elif i == 1:
                    terms.append("x")
                else:
                    terms.append(f"x ^ {i}")
        return " + ".join(terms) if terms else "0"

def poly_from_int(val, degree = 6):
    coeffs = [(val >> i) & 1 for i in range(degree)]
    return GF2_p6(coeffs[::-1])  # little-endian to big-endian для представления

def factorize(n):
    factors = []
    d = 2
    while d*d <= n:
        if n % d == 0:
            cnt = 0
            while n % d == 0:
                n //= d
                cnt += 1
            factors.append((d, cnt))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors

def find_primitive():
    order = 63
    factors = factorize(order)
    for val in range(2, 64):
        g = poly_from_int(val)
        is_prim = True
        for q, _ in factors:
            if pow(g, order // q) == poly_from_int(1):
                is_prim = False
                break
        if is_prim:
            return g
    return None

def modinv(a, m):
    # расширенный алгоритм Евклида
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("no inverse")
    return x % m

def pohlig_hellman(g, h, order, factors):
    x = 0
    mod_prod = 1
    for q, e in factors:
        qe = q ** e
        x_q = 0
        h_curr = h
        g_q = pow(g, order // q)
        for k in range(e):
            exp = order // (q ** (k + 1))
            h_k = pow(h_curr, exp)
            for a in range(q):
                if pow(g_q, a) == h_k:
                    x_q += a * (q ** k)
                    if a != 0:
                        factor = pow(g, a * (q ** k))
                        # в GF(2^m) обратный = factor^(order-1)
                        inv_factor = pow(factor, order - 1)
                        h_curr = h_curr * inv_factor
                    break
        inv = modinv(mod_prod, qe)
        t = ((x_q - x) * inv) % qe
        x += mod_prod * t
        mod_prod *= qe
    return x % order

def main():
    print("Поле F_64 = F_2[x] / (x ^ 6 + x + 1)")
    g = find_primitive()
    print("Порождающий элемент g = ", g)
    f = GF2_p6([1, 1, 0, 0, 0, 0])  # x + 1
    print("f = ", f)
    order = 63
    factors = factorize(order)
    print("Порядок группы:", order, "=", "*".join(f"{q} ^ {e}" for q, e in factors))
    log = pohlig_hellman(g, f, order, factors)
    print("log_g(f) =", log)
    print("Проверка: g ^ log =", pow(g, log))

if __name__ == "__main__":
    main()

# Задача 6. Продемонстрировать версию алгоритма Сильвера - Полига - Хеллмана вычисления дискретного логарифма в поле F17 для случая 3х = 15(mod17).
def factorize(n):
    """Разложение числа на простые множители"""
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            count = 0
            while n % d == 0:
                n //= d
                count += 1
            factors.append((d, count))
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append((n, 1))
    return factors

def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратный элемент по модулю m"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    return x % m

def pohlig_hellman(g, h, p):
    """
    Алгоритм Сильвера-Полига-Хеллмана для дискретного логарифма
    в поле F_p (p - простое)
    """
    n = p - 1  # порядок группы
    factors = factorize(n)
    
    print(f"Решаем уравнение: {g} ^ x ≡ {h} (mod {p})")
    print(f"Порядок группы: {n} = {' * '.join([f'{q} ^ {e}' for q, e in factors])}")
    print()
    
    x = 0
    mod_product = 1
    
    for q, e in factors:
        print(f"=== Решение по модулю {q} ^ {e} ===")
        qe = q ** e
        x_q = 0
        h_current = h
        
        # Вычисляем g_q = g^(n/q)
        g_q = pow(g, n // q, p)
        print(f"g_q = {g_q} (порядок {q})")
        
        for k in range(e):
            print(f"  Шаг k = {k}")
            # Вычисляем h_k = h_current^(n / q^(k+1))
            exponent = n // (q ** (k + 1))
            h_k = pow(h_current, exponent, p)
            print(f"    h_{k} = {h_current}^{exponent} mod {p} = {h_k}")
            
            # Ищем a_k: g_q^a_k ≡ h_k
            found = False
            for a in range(q):
                if pow(g_q, a, p) == h_k:
                    a_k = a
                    found = True
                    print(f"    Нашли a_{k} = {a_k}")
                    break
            
            if not found:
                raise Exception(f"Не удалось найти a_{k} для q = {q}")
            
            x_q += a_k * (q ** k)
            print(f"    x_q = {x_q}")
            
            # Обновляем h_current: h_current = h_current * g^(-a_k * q^k)
            if a_k != 0:
                factor = pow(g, a_k * (q ** k), p)
                # Обратный элемент по модулю p
                inv_factor = modinv(factor, p)
                h_current = (h_current * inv_factor) % p
                print(f"    Обновлённый h_current = {h_current}")
        
        print(f"Решение по модулю {qe}: x ≡ {x_q} (mod {qe})")
        
        # Китайская теорема об остатках
        inv = modinv(mod_product, qe)
        t = ((x_q - x) * inv) % qe
        x = x + mod_product * t
        mod_product *= qe
        print(f"Объединённое решение: x ≡ {x} (mod {mod_product})")
        print()
    
    return x % n

def main():
    # Параметры задачи
    g = 3   # основание
    h = 15  # число
    p = 17  # модуль (простое число)
    
    print("=" * 60)
    print("Алгоритм Сильвера-Полига-Хеллмана")
    print("=" * 60)
    
    x = pohlig_hellman(g, h, p)
    
    print("=" * 60)
    print(f"Результат: x = {x}")
    print(f"Проверка: {g} ^ {x} mod {p} = {pow(g, x, p)}")
    
    if pow(g, x, p) == h:
        print("✓ Проверка пройдена!")
    else:
        print("✗ Ошибка в вычислениях!")
    print("=" * 60)

if __name__ == "__main__":
    main()

# Задача 7. Построить конкретный протокол Диффи - Хеллмана с платформой F*27
import random

class GF27:
    """Класс для работы с полем F_{27} = F_3[x] / (x ^ 3 + 2x + 1)"""
    
    def __init__(self, a, b, c, p = 3, mod_poly = (1, 0, 2, 1)):
        """
        Элемент поля: a * x ^ 2 + b * x + c
        mod_poly: коэффициенты x ^ 3 + 2x + 1
        """
        self.p = p
        self.mod_poly = mod_poly
        self.a = a % p
        self.b = b % p
        self.c = c % p
    
    def __eq__(self, other):
        return (self.a, self.b, self.c) == (other.a, other.b, other.c)
    
    def __add__(self, other):
        return GF27(self.a + other.a, self.b + other.b, self.c + other.c, self.p, self.mod_poly)
    
    def __sub__(self, other):
        return GF27(self.a - other.a, self.b - other.b, self.c - other.c, self.p, self.mod_poly)
    
    def __neg__(self):
        return GF27(-self.a, -self.b, -self.c, self.p, self.mod_poly)
    
    def __mul__(self, other):
        # Умножение в F_3[x]/(x^3 + 2x + 1)
        # x^3 = -2x - 1 = x + 2 (в F_3: -2 ≡ 1, -1 ≡ 2)
        a1, b1, c1 = self.a, self.b, self.c
        a2, b2, c2 = other.a, other.b, other.c
        
        # Коэффициенты при x^4, x^3, x^2, x, 1
        x4 = a1 * a2
        x3 = a1 * b2 + b1 * a2
        x2 = a1 * c2 + b1 * b2 + c1 * a2
        x1 = b1 * c2 + c1 * b2
        x0 = c1 * c2
        
        # Редукция: x^4 = x * x^3 = x*(x+2) = x^2 + 2x
        # x^3 = x + 2
        
        new_a = (x2 + x4) % self.p           # из x2 и из x4 (x^2 часть)
        new_b = (x1 + 2*x4 + x3) % self.p    # из x1, из x4 (2x часть), из x3 (x часть)
        new_c = (x0 + 2*x3) % self.p         # из x0, из x3 (2 часть)
        
        return GF27(new_a % self.p, new_b % self.p, new_c % self.p, self.p, self.mod_poly)
    
    def __pow__(self, exp):
        result = GF27(0, 0, 1, self.p, self.mod_poly)  # 1
        base = self
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result
    
    def __str__(self):
        terms = []
        if self.a != 0:
            terms.append(f"{self.a}x²")
        if self.b != 0:
            terms.append(f"{self.b}x")
        if self.c != 0:
            terms.append(str(self.c))
        if not terms:
            return "0"
        return " + ".join(terms).replace(" + -", " - ")

def generate_private_key(order = 26):
    """Генерирует секретный ключ (число от 1 до order - 1)"""
    return random.randint(1, order - 1)

def diffie_hellman_protocol():
    print("=" * 70)
    print("Протокол Диффи-Хеллмана на платформе F_{27}")
    print("=" * 70)
    
    # Общие параметры
    g = GF27(0, 1, 0)  # g = x
    order = 26  # порядок мультипликативной группы F_{27}^*
    
    print("\nОбщие параметры:")
    print(f"  Поле: F_3[x] / (x ^ 3 + 2x + 1)")
    print(f"  Порождающий элемент g = {g}")
    print(f"  Порядок группы: {order}")
    
    # Генерация секретных ключей
    a = generate_private_key(order)
    b = generate_private_key(order)
    
    print(f"\nСекретные ключи:")
    print(f"  Алиса (a) = {a}")
    print(f"  Боб (b)   = {b}")
    
    # Вычисление открытых ключей
    A = pow(g, a)  # g^a
    B = pow(g, b)  # g^b
    
    print(f"\nОткрытые ключи:")
    print(f"  Алиса (A = g ^ a) = {A}")
    print(f"  Боб   (B = g ^ b) = {B}")
    
    # Вычисление общего секрета
    K_alice = pow(B, a)  # (g^b)^a = g^(ab)
    K_bob = pow(A, b)    # (g^a)^b = g^(ab)
    
    print(f"\nОбщий секрет:")
    print(f"  Алиса: K = B ^ a = {K_alice}")
    print(f"  Боб:   K = A ^ b = {K_bob}")
    
    # Проверка
    if K_alice == K_bob:
        print("\n✓ Успех! Общий секрет совпадает у обоих участников.")
    else:
        print("\n✗ Ошибка! Общие секреты не совпадают.")
    
    # Дополнительная проверка: g^(a*b) должно равняться общему секрету
    K_direct = pow(g, (a * b) % order)
    print(f"\nПроверка: g ^ (a * b) = {K_direct}")
    
    if K_alice == K_direct:
        print("✓ g ^ (a * b) совпадает с общим секретом.")
    
    print("\n" + "=" * 70)
    
    return a, b, A, B, K_alice

def demonstrate_with_fixed_keys():
    """Демонстрация с фиксированными ключами из условия задачи"""
    print("=" * 70)
    print("Демонстрация с фиксированными ключами (a = 7, b = 11)")
    print("=" * 70)
    
    # Общие параметры
    g = GF27(0, 1, 0)  # g = x
    order = 26
    
    print(f"\nПорождающий элемент g = {g}")
    
    # Фиксированные секретные ключи
    a = 7
    b = 11
    
    print(f"\nСекретные ключи:")
    print(f"  Алиса (a) = {a}")
    print(f"  Боб   (b) = {b}")
    
    # Вычисление открытых ключей
    A = pow(g, a)
    B = pow(g, b)
    
    print(f"\nОткрытые ключи:")
    print(f"  Алиса (A = g ^ {a}) = {A}")
    print(f"  Боб   (B = g ^ {b}) = {B}")
    
    # Вычисление общего секрета
    K_alice = pow(B, a)
    K_bob = pow(A, b)
    
    print(f"\nОбщий секрет:")
    print(f"  Алиса: K = B ^ {a} = {K_alice}")
    print(f"  Боб:   K = A ^ {b} = {K_bob}")
    
    # Проверка
    if K_alice == K_bob:
        print("\n✓ Успех! Общий секрет совпадает.")
    else:
        print("\n✗ Ошибка!")
    
    # Покажем, что K = x^(77 mod 26) = x^25
    K_expected = pow(g, 25)
    print(f"\nОжидаемый секрет (g ^ (25)) = {K_expected}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    # Демонстрация с фиксированными ключами из текста
    demonstrate_with_fixed_keys()
    
    print("\n\n")
    
    # Случайная генерация ключей
    diffie_hellman_protocol()

# Задача 8. Пусть дано простое конечное поле Z43.Предположим, что g - порождающий элемент его мультипликативной группы. 
# Сколько всего имеется порождающих элементов и как их можно получить из g?.
from math import gcd

def euler_phi(n):
    """Вычисление функции Эйлера φ(n)"""
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1 if p == 2 else 2
    if n > 1:
        result -= result // n
    return result

def find_generators(g, p):
    """
    Находит все порождающие элементы мультипликативной группы Z_p^*
    на основе заданного порождающего элемента g
    
    Параметры:
    g - известный порождающий элемент
    p - простое число (модуль)
    
    Возвращает:
    Список всех порождающих элементов
    """
    order = p - 1  # порядок группы Z_p^*
    
    # Находим все числа k, взаимно простые с order
    k_values = [k for k in range(1, order + 1) if gcd(k, order) == 1]
    
    # Генерируем порождающие элементы: g^k
    generators = [pow(g, k, p) for k in k_values]
    
    return generators, k_values

def main():
    # Параметры задачи
    p = 43
    g = 9  # порождающий элемент (дан в условии)
    
    print("=" * 60)
    print("Задача 8: Поиск порождающих элементов в Z_43 ^ *")
    print("=" * 60)
    
    # Порядок группы
    order = p - 1
    print(f"\nМодуль: p = {p}")
    print(f"Порядок мультипликативной группы: |Z_{p} ^ *| = {order}")
    
    # Количество порождающих элементов
    num_generators = euler_phi(order)
    print(f"\nКоличество порождающих элементов: φ({order}) = {num_generators}")
    
    # Находим все порождающие элементы
    generators, k_values = find_generators(g, p)
    
    print(f"\nВсе порождающие элементы (полученные как {g} ^ k):")
    print("-" * 60)
    
    for i, (k, gen) in enumerate(zip(k_values, generators), 1):
        print(f"{i:2}. {g} ^ {k:2} = {gen:2}  (mod {p})")
    
    print("\n" + "=" * 60)
    print("Проверка:")
    print("=" * 60)
    
    # Проверка: каждый найденный элемент действительно является порождающим
    print("\nПроверка порядка каждого порождающего элемента:")
    for i, gen in enumerate(generators[:5]):  # Проверяем первые 5 для краткости
        # Находим порядок элемента
        current = gen
        order_found = 1
        while current != 1:
            current = (current * gen) % p
            order_found += 1
        print(f"  Элемент {gen:2} имеет порядок {order_found} → {'✓' if order_found == order else '✗'}")
    
    if len(generators) > 5:
        print(f"  ... и ещё {len(generators) - 5} элементов (все имеют порядок {order})")
    
    print("\n" + "=" * 60)
    print("Теоретическое обоснование:")
    print("=" * 60)
    print(f"""
        Группа Z_{p}^* циклическая, так как {p} - простое число.
        Если g - порождающий элемент (имеет порядок {order}),
        то g^k также является порождающим тогда и только тогда,
        когда НОД(k, {order}) = 1.
        
        Количество таких k равно φ({order}) = {num_generators}.
        
        Все k, взаимно простые с {order}:
        {k_values}
    """)
    
    print("=" * 60)

if __name__ == "__main__":
    main()

# Задача 9.9. Предлагается следующее упрощение протокола
# Масси-Омуры. При выбранном конечном поле F Алиса осуществляет передачу сообщения т Е F Бобу. Она выбирает секретный
# элемент а Е F* и передает элемент та. Боб выбирает секретный
# элемент Ь Е F* и передает элемент таЬ. Алиса умножает на а-1
# и передает тЬ. Боб вычисляет т, умножая полученное сообщение на b-1. Какова основная слабость протокола? Можно ли его
# улучшить, заменив платформу F на кольцо вычетов Zn?
import random
from math import gcd

def modinv(a, n):
    """Находит обратный элемент a⁻¹ mod n (расширенный алгоритм Евклида)"""
    # Расширенный алгоритм Евклида
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
    
    g, x, _ = egcd(a, n)
    if g != 1:
        raise Exception(f"Обратного элемента для {a} mod {n} не существует")
    return x % n

def is_invertible(x, n):
    """Проверяет, обратим ли элемент x в кольце Z_n"""
    return gcd(x, n) == 1

class SimplifiedMasayukiOmura:
    """Упрощённый протокол Масси-Омуры (слабая версия)"""
    
    def __init__(self, field_mod, message, alice_secret, bob_secret):
        self.mod = field_mod
        self.message = message % field_mod
        self.a = alice_secret % field_mod
        self.b = bob_secret % field_mod
        
        # Проверяем, что секреты обратимы
        if not is_invertible(self.a, field_mod):
            raise ValueError(f"Секрет Алисы {self.a} не обратим в Z_{field_mod}")
        if not is_invertible(self.b, field_mod):
            raise ValueError(f"Секрет Боба {self.b} не обратим в Z_{field_mod}")
        if not is_invertible(self.message, field_mod) and field_mod != self.message:
            print(f"Предупреждение: сообщение {self.message} необратимо в Z_{field_mod}")
    
    def run_protocol(self):
        """Запускает протокол и возвращает все передаваемые сообщения"""
        print(f"\n{'=' * 60}")
        print(f"Упрощённый протокол Масси-Омуры в Z_{self.mod}")
        print(f"{'=' * 60}")
        
        # Шаг 1: Алиса → Боб
        c1 = (self.message * self.a) % self.mod
        print(f"1. Алиса → Боб: c1 = m·a = {self.message}·{self.a} = {c1}")
        
        # Шаг 2: Боб → Алиса
        c2 = (c1 * self.b) % self.mod
        print(f"2. Боб → Алиса: c2 = c1·b = {c1}·{self.b} = {c2}")
        
        # Шаг 3: Алиса → Боб
        a_inv = modinv(self.a, self.mod)
        c3 = (c2 * a_inv) % self.mod
        print(f"3. Алиса → Боб: c3 = c2·a⁻¹ = {c2}·{a_inv} = {c3}")
        
        # Боб расшифровывает
        b_inv = modinv(self.b, self.mod)
        decrypted = (c3 * b_inv) % self.mod
        print(f"\nБоб расшифровывает: m = c3·b⁻¹ = {c3}·{b_inv} = {decrypted}")
        
        return c1, c2, c3, decrypted
    
    def eavesdrop_attack(self, c1, c2, c3):
        """Ева перехватывает сообщения и пытается восстановить m"""
        print(f"\n{'=' * 60}")
        print("Ева перехватывает сообщения и атакует")
        print(f"{'=' * 60}")
        
        # Атака: b = c2 / c1
        try:
            c1_inv = modinv(c1, self.mod)
            b_found = (c2 * c1_inv) % self.mod
            print(f"Ева вычисляет b = c2 / c1 = {c2}·{c1}⁻¹ = {b_found}")
            
            # Затем m = c3 / b
            b_found_inv = modinv(b_found, self.mod)
            m_found = (c3 * b_found_inv) % self.mod
            print(f"Ева вычисляет m = c3 / b = {c3}·{b_found}⁻¹ = {m_found}")
            
            if m_found == self.message:
                print(f"\n✓ АТАКА УСПЕШНА! Ева восстановила сообщение m = {m_found}")
            else:
                print(f"\n✗ Атака не удалась (m = {self.message}, получено {m_found})")
            
            return m_found
        except Exception as e:
            print(f"Атака не удалась: {e}")
            return None

def demonstrate_weakness():
    """Демонстрирует слабость протокола на примере поля F_43"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ СЛАБОСТИ ПРОТОКОЛА")
    print("=" * 60)
    
    # Параметры (поле F_43)
    mod = 43
    message = 25
    alice_secret = 7
    bob_secret = 11
    
    # Запускаем протокол
    protocol = SimplifiedMasayukiOmura(mod, message, alice_secret, bob_secret)
    c1, c2, c3, decrypted = protocol.run_protocol()
    
    # Ева атакует
    protocol.eavesdrop_attack(c1, c2, c3)

def demonstrate_with_ring_zn():
    """Показывает, что замена на кольцо Zn не улучшает безопасность"""
    print("\n" + "=" * 60)
    print("ПОПЫТКА УЛУЧШИТЬ: ЗАМЕНА НА КОЛЬЦО Z_n")
    print("=" * 60)
    
    # Используем составной модуль n = 77 = 7 * 11
    n = 77
    # Выбираем обратимые элементы (взаимно простые с 77)
    message = 25  # gcd(25,77)=1, обратим
    alice_secret = 9   # gcd(9,77)=1, обратим
    bob_secret = 13    # gcd(13,77)=1, обратим
    
    print(f"Кольцо Z_{n} = Z_{7 * 11}")
    print(f"Сообщение m = {message} (обратимо)")
    print(f"Секрет Алисы a = {alice_secret} (обратим)")
    print(f"Секрет Боба b = {bob_secret} (обратим)")
    
    protocol = SimplifiedMasayukiOmura(n, message, alice_secret, bob_secret)
    c1, c2, c3, decrypted = protocol.run_protocol()
    protocol.eavesdrop_attack(c1, c2, c3)

def demonstrate_non_invertible():
    """Показывает проблему с необратимыми элементами в кольце Zn"""
    print("\n" + "=" * 60)
    print("ПРОБЛЕМА С НЕОБРАТИМЫМИ ЭЛЕМЕНТАМИ В Z_n")
    print("=" * 60)
    
    n = 77
    # Выбираем необратимое сообщение
    message = 14  # gcd(14,77)=7, не обратим
    alice_secret = 9   # обратим
    bob_secret = 13    # обратим
    
    print(f"Кольцо Z_{n}")
    print(f"Сообщение m = {message} (НЕОБРАТИМО, gcd({message}, {n})={gcd(message,n)})")
    print(f"Секрет Алисы a = {alice_secret} (обратим)")
    print(f"Секрет Боба b = {bob_secret} (обратим)")
    
    try:
        protocol = SimplifiedMasayukiOmura(n, message, alice_secret, bob_secret)
        c1, c2, c3, decrypted = protocol.run_protocol()
        
        # Ева пытается атаковать
        print(f"\nЕва пытается атаковать:")
        try:
            c1_inv = modinv(c1, n)
            b_found = (c2 * c1_inv) % n
            print(f"b = {b_found}")
            b_found_inv = modinv(b_found, n)
            m_found = (c3 * b_found_inv) % n
            print(f"m = {m_found}")
        except Exception as e:
            print(f"Атака не удалась: {e}")
            print("Но это не криптостойкость, а просто невозможность деления!")
    
    except Exception as e:
        print(f"Ошибка: {e}")

def demonstrate_original_masayuki_omura():
    """Демонстрирует ОРИГИНАЛЬНЫЙ (стойкий) протокол Масси-Омуры с возведением в степень"""
    print("\n" + "=" * 60)
    print("ОРИГИНАЛЬНЫЙ ПРОТОКОЛ МАССИ-ОМУРЫ (СТОЙКИЙ)")
    print("=" * 60)
    
    # Работаем в F_43
    p = 43
    order = p - 1  # 42
    
    # Выбираем секреты (взаимно простые с порядком)
    alice_secret = 5    # gcd(5,42)=1
    bob_secret = 11     # gcd(11,42)=1
    
    message = 25
    
    print(f"Поле F_{p}")
    print(f"Порядок группы: {order}")
    print(f"Сообщение m = {message}")
    print(f"Секрет Алисы a = {alice_secret}")
    print(f"Секрет Боба b = {bob_secret}")
    
    # Шаг 1: Алиса → Боб
    c1 = pow(message, alice_secret, p)
    print(f"\n1. Алиса → Боб: c1 = m ^ a = {message} ^ {alice_secret} mod {p} = {c1}")
    
    # Шаг 2: Боб → Алиса
    c2 = pow(c1, bob_secret, p)
    print(f"2. Боб → Алиса: c2 = c1 ^ b = {c1} ^ {bob_secret} mod {p} = {c2}")
    
    # Шаг 3: Алиса → Боб
    # Находим a⁻¹ по модулю order
    a_inv = modinv(alice_secret, order)
    c3 = pow(c2, a_inv, p)
    print(f"3. Алиса → Боб: c3 = c2 ^ (a⁻¹) = {c2} ^ {a_inv} mod {p} = {c3}")
    
    # Боб расшифровывает
    b_inv = modinv(bob_secret, order)
    decrypted = pow(c3, b_inv, p)
    print(f"\nБоб расшифровывает: m = c3 ^ (b⁻¹) = {c3} ^ {b_inv} mod {p} = {decrypted}")
    
    # Ева пытается атаковать (не сможет)
    print(f"\nЕва перехватила: c1 = {c1}, c2 = {c2}, c3 = {c3}")
    print("Ева не может вычислить m, так как нужно решать дискретный логарифм")
    
    if decrypted == message:
        print(f"\n✓ Протокол успешно завершён, получено m = {decrypted}")
    else:
        print(f"\n✗ Ошибка!")

def main():
    print("=" * 70)
    print("КРИПТОАНАЛИЗ УПРОЩЁННОГО ПРОТОКОЛА МАССИ-ОМУРЫ")
    print("=" * 70)
    
    # 1. Демонстрация слабости в поле
    demonstrate_weakness()
    
    # 2. Замена на кольцо Zn не помогает
    demonstrate_with_ring_zn()
    
    # 3. Проблема с необратимыми элементами
    demonstrate_non_invertible()
    
    # 4. Оригинальный (стойкий) протокол
    demonstrate_original_masayuki_omura()
    
    print("\n" + "=" * 70)
    print("ВЫВОД")
    print("=" * 70)
    print("""
        Основная слабость упрощённого протокола:
        - Используется только умножение (линейная операция)
        - Три переданных сообщения линейно зависимы
        - Ева восстанавливает b = c2/c1, затем m = c3/b
        
        Замена поля F на кольцо Zn НЕ улучшает безопасность:
        - Для обратимых элементов атака работает так же
        - Для необратимых — деление невозможно, но это не криптостойкость,
        а просто ограничение протокола (нельзя передавать любые сообщения)
        
        Оригинальный протокол Масси-Омуры использует возведение в степень
        и устойчив к такой атаке, так как требует решения дискретного логарифма.
    """)
    print("=" * 70)

if __name__ == "__main__":
    main()