# 3. Атаки на дискретный логарифм
import math
from functools import reduce

def prime_factors(n):
    """Разложение числа n на простые множители с показателями степеней."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def extended_gcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y), где a * x + b * y = g = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def crt(residues, moduli):
    """Китайская теорема об остатках: решает систему x ≡ residues[i] (mod moduli[i]).
       Возвращает x mod (произведение moduli)."""
    total = 0
    prod = reduce(lambda a, b: a * b, moduli)
    for r, m in zip(residues, moduli):
        p = prod // m
        _, inv, _ = extended_gcd(p, m)
        total += r * p * inv
    return total % prod

class PohligHellman:
    def __init__(self, g, q):
        """
        g — порождающий элемент мультипликативной группы F_q^*.
        q — порядок поля F_q (простое или степень простого).
        Предполагается, что q-1 имеет только малые простые делители.
        """
        self.g = g
        self.q = q
        self.n = q - 1          # порядок группы
        self.factors = prime_factors(self.n)
        
        # Предварительное вычисление таблиц корней p-й степени из 1 для каждого простого p
        self.roots = {}
        for p in self.factors:
            # Вычисляем r_{p, j} = g ^ {j * (q - 1) / p} для j = 0..p - 1
            exponent_base = self.n // p
            roots_p = {}
            for j in range(p):
                # Элемент g ^ {j * (q - 1) / p}
                root = pow(g, (j * exponent_base) % self.n, q)
                roots_p[root] = j   # отображение значения -> j
            self.roots[p] = roots_p
    
    def log(self, y):
        """
        Вычисляет дискретный логарифм x: g ^ x ≡ y (mod q).
        """
        residues = []
        moduli = []
        
        for p, a in self.factors.items():
            # Находим x mod p^a
            xp = 0
            factor = 1
            y_cur = y
            
            for k in range(a):
                # Вычисляем y_cur ^ {(q - 1) / p ^ {k + 1}}
                exp = self.n // (p ** (k + 1))
                val = pow(y_cur, exp, self.q)
                
                # Ищем j такое, что val == g ^ {j * (q - 1) / p}
                # Используем предвычисленную таблицу для p
                if val not in self.roots[p]:
                    raise ValueError(f"Не удалось найти корень {val} для p = {p}")
                j = self.roots[p][val]
                
                # Добавляем к xp: xp += j * p ^ k
                xp += j * factor
                factor *= p
                
                # Обновляем y_cur для следующей итерации: y_cur = y_cur * g ^ {-j * p ^ k}
                # То есть y_cur = y_cur * (g ^ {-j * p ^ k})
                # Лучше: y_cur = y_cur * g ^ {-j * p ^ k}  (в поле)
                # Поскольку g — порождающий, g ^ {-m} = pow(g, n - m, q)
                if k < a - 1:
                    exponent_corr = j * (p ** k)
                    # Умножаем на обратный элемент: g^{-exponent_corr}
                    inv_factor = pow(g, self.n - exponent_corr, self.q)
                    y_cur = (y_cur * inv_factor) % self.q
            
            residues.append(xp)
            moduli.append(p ** a)
        
        # Китайская теорема об остатках
        x = crt(residues, moduli)
        return x

# ============= Пример использования =============
if __name__ == "__main__":
    # Пример из лекции: F_37, g = 2, ищем log_2(28)
    q = 37
    g = 2
    y = 28
    
    ph = PohligHellman(g, q)
    x = ph.log(y)
    
    print(f"Дискретный логарифм log_{g}({y}) в поле F_{q} = {x}")
    print(f"Проверка: {g} ^ {x} mod {q} = {pow(g, x, q)}")
    
    # Дополнительный тест: случайное y
    import random
    random.seed(42)
    test_x = random.randint(1, q - 2)
    test_y = pow(g, test_x, q)
    computed_x = ph.log(test_y)
    print(f"\nТест со случайным x: загадали x = {test_x}, получили y = {test_y}, вычислили log = {computed_x}")
    assert test_x == computed_x, "Ошибка: логарифм вычислен неверно"
    print("Тест пройден успешно.")