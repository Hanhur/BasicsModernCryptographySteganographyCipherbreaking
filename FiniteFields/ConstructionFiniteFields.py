# 2. Построение конечных полей
import sys
from typing import Tuple, List

class FiniteFieldElement:
    """Элемент конечного поля F_{p^r}, задаваемый многочленом степени < r."""
    
    def __init__(self, coeffs: List[int], field: 'FiniteField'):
        """
        coeffs: список коэффициентов [a0, a1, ..., a_{r - 1}], где a_i ∈ Z_p
        field: ссылка на поле, к которому принадлежит элемент
        """
        self.field = field
        self.coeffs = coeffs[:]
        # Приводим коэффициенты по модулю p
        for i in range(len(self.coeffs)):
            self.coeffs[i] %= field.p
        # Дополняем нулями до степени r-1
        while len(self.coeffs) < field.r:
            self.coeffs.append(0)
    
    def __repr__(self):
        terms = []
        for i, coeff in enumerate(self.coeffs):
            if coeff == 0:
                continue
            if i == 0:
                terms.append(f"{coeff}")
            elif i == 1:
                if coeff == 1:
                    terms.append("x")
                else:
                    terms.append(f"{coeff} x")
            else:
                if coeff == 1:
                    terms.append(f"x ^ {i}")
                else:
                    terms.append(f"{coeff} x ^ {i}")
        if not terms:
            return "0"
        return " + ".join(reversed(terms))
    
    def __add__(self, other):
        if not isinstance(other, FiniteFieldElement) or self.field != other.field:
            raise TypeError("Элементы должны принадлежать одному полю")
        new_coeffs = [(self.coeffs[i] + other.coeffs[i]) % self.field.p for i in range(self.field.r)]
        return FiniteFieldElement(new_coeffs, self.field)
    
    def __sub__(self, other):
        if not isinstance(other, FiniteFieldElement) or self.field != other.field:
            raise TypeError("Элементы должны принадлежать одному полю")
        new_coeffs = [(self.coeffs[i] - other.coeffs[i]) % self.field.p for i in range(self.field.r)]
        return FiniteFieldElement(new_coeffs, self.field)
    
    def __mul__(self, other):
        if not isinstance(other, FiniteFieldElement) or self.field != other.field:
            raise TypeError("Элементы должны принадлежать одному полю")
        # Умножение многочленов в Z_p[x]
        prod_coeffs = [0] * (2 * self.field.r - 1)
        for i in range(self.field.r):
            for j in range(self.field.r):
                prod_coeffs[i + j] = (prod_coeffs[i + j] + self.coeffs[i] * other.coeffs[j]) % self.field.p
        # Приведение по модулю f(x)
        # Степени >= r заменяем с помощью f(x) = x ^ r - (b_{r - 1} x ^ {r-1} + ... + b_0)
        # Но проще реализовать деление многочленов с остатком
        remainder = self.field._poly_mod(prod_coeffs)
        return FiniteFieldElement(remainder, self.field)
    
    def __pow__(self, exponent: int):
        """Возведение в степень (бинарное возведение в степень)."""
        if exponent == 0:
            # Возвращаем 1 (многочлен 1)
            coeffs = [0] * self.field.r
            coeffs[0] = 1
            return FiniteFieldElement(coeffs, self.field)
        result = self
        for _ in range(exponent - 1):
            result = result * self
        return result
    
    def inverse(self):
        """Обратный элемент с помощью расширенного алгоритма Евклида."""
        if self.is_zero():
            raise ZeroDivisionError("Нулевой элемент не имеет обратного")
        # Расширенный алгоритм Евклида для многочленов над Z_p
        # Ищем u(x), v(x): u(x)*self(x) + v(x)*f(x) = 1
        gcd, u, _ = self.field._extended_gcd(self.coeffs, self.field.f_coeffs)
        # Проверяем, что НОД = 1 (константа)
        if len(gcd) != 1 or gcd[0] == 0:
            raise ArithmeticError("Элемент не обратим (НОД не константа)")
        # Нормируем, чтобы u * self ≡ 1 mod f
        inv_coeffs = [ (c * pow(gcd[0], -1, self.field.p)) % self.field.p for c in u ]
        # Приводим степень
        while len(inv_coeffs) >= self.field.r:
            inv_coeffs = self.field._poly_mod(inv_coeffs)
        return FiniteFieldElement(inv_coeffs, self.field)
    
    def is_zero(self) -> bool:
        return all(c == 0 for c in self.coeffs)
    
    def is_one(self) -> bool:
        return self.coeffs[0] == 1 and all(c == 0 for c in self.coeffs[1:])


class FiniteField:
    """Конечное поле F_{p ^ r} с заданным неприводимым многочленом f(x)."""
    
    def __init__(self, p: int, r: int, f_coeffs: List[int]):
        """
        p: простое число (характеристика)
        r: степень расширения
        f_coeffs: коэффициенты неприводимого многочлена f(x) степени r
                  в порядке возрастания степени, например:
                  x ^ 2 + x + 2 → [2, 1, 1]
        """
        self.p = p
        self.r = r
        # Приводим коэффициенты f(x) по модулю p
        self.f_coeffs = [c % p for c in f_coeffs]
        if len(self.f_coeffs) != r + 1:
            raise ValueError(f"Многочлен должен иметь степень {r}, получено {len(self.f_coeffs) - 1}")
        if self.f_coeffs[r] == 0:
            raise ValueError("Старший коэффициент не должен быть нулём")
        # Нормируем (делаем старший коэффициент равным 1)
        inv_lead = pow(self.f_coeffs[r], -1, p)
        self.f_coeffs = [(c * inv_lead) % p for c in self.f_coeffs]
        # Проверка неприводимости (упрощённая: поиск корней для r=2,3)
        if r == 2:
            self._check_irreducible_quadratic()
        # Поле для хранения элементов (для удобства)
        self.elements = []
        
    def _check_irreducible_quadratic(self):
        """Проверка неприводимости квадратного трёхчлена (отсутствие корней в Z_p)."""
        if self.r != 2:
            return  # Для больших r проверка сложнее, доверяем пользователю
        # f(x) = a x^2 + b x + c, a ≠ 0
        a = self.f_coeffs[2]
        b = self.f_coeffs[1]
        c = self.f_coeffs[0]
        for x in range(self.p):
            val = (a * x * x + b * x + c) % self.p
            if val == 0:
                raise ValueError(f"Многочлен {self._poly_to_str(self.f_coeffs)} имеет корень {x} в Z_{self.p}, он не неприводим")
    
    def _poly_to_str(self, coeffs):
        """Красивое представление многочлена."""
        terms = []
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            if i == 0:
                terms.append(f"{c}")
            elif i == 1:
                if c == 1:
                    terms.append("x")
                else:
                    terms.append(f"{c} x")
            else:
                if c == 1:
                    terms.append(f"x ^ {i}")
                else:
                    terms.append(f"{c} x ^ {i}")
        if not terms:
            return "0"
        return " + ".join(reversed(terms))
    
    def _poly_divmod(self, a_coeffs, b_coeffs):
        """Деление многочленов с остатком над Z_p."""
        # a = b*q + r, степень r < степени b
        a = a_coeffs[:]
        b = b_coeffs[:]
        deg_b = len(b) - 1
        inv_lead = pow(b[deg_b], -1, self.p)
        q = [0] * (len(a) - deg_b) if len(a) >= deg_b else [0]
        for i in range(len(a) - deg_b - 1, -1, -1):
            if a[deg_b + i] != 0:
                factor = (a[deg_b + i] * inv_lead) % self.p
                q[i] = factor
                for j in range(deg_b + 1):
                    a[i + j] = (a[i + j] - factor * b[j]) % self.p
        # Обрезаем ведущие нули
        while len(a) > 0 and a[-1] == 0:
            a.pop()
        # q тоже обрезаем
        while len(q) > 0 and q[-1] == 0:
            q.pop()
        return q, a
    
    def _poly_mod(self, a_coeffs):
        """Остаток от деления a_coeffs на f(x)."""
        _, rem = self._poly_divmod(a_coeffs, self.f_coeffs)
        return rem if rem else [0]
    
    def _poly_gcd(self, a_coeffs, b_coeffs):
        """НОД двух многочленов над Z_p."""
        while b_coeffs:
            _, rem = self._poly_divmod(a_coeffs, b_coeffs)
            a_coeffs, b_coeffs = b_coeffs, rem
        if a_coeffs and a_coeffs[-1] != 0:
            # Нормируем
            inv_lead = pow(a_coeffs[-1], -1, self.p)
            a_coeffs = [(c * inv_lead) % self.p for c in a_coeffs]
        return a_coeffs
    
    def _extended_gcd(self, a_coeffs, b_coeffs):
        """Расширенный алгоритм Евклида: возвращает (gcd, u, v), где u * a + v * b = gcd."""
        if not b_coeffs:
            if a_coeffs and a_coeffs[-1] != 0:
                inv_lead = pow(a_coeffs[-1], -1, self.p)
                a_coeffs = [(c * inv_lead) % self.p for c in a_coeffs]
            return a_coeffs, [1], [0]
        q, r = self._poly_divmod(a_coeffs, b_coeffs)
        gcd, u1, v1 = self._extended_gcd(b_coeffs, r)
        # u = v1, v = u1 - q*v1
        # Умножение q на v1
        qv1 = [0] * (len(q) + len(v1) - 1)
        for i in range(len(q)):
            for j in range(len(v1)):
                qv1[i + j] = (qv1[i + j] + q[i] * v1[j]) % self.p
        # u1 - qv1
        u = [0] * max(len(u1), len(qv1))
        for i in range(len(u1)):
            u[i] = u1[i]
        for i in range(len(qv1)):
            u[i] = (u[i] - qv1[i]) % self.p
        while len(u) > 0 and u[-1] == 0:
            u.pop()
        if not u:
            u = [0]
        v = v1[:]
        return gcd, u, v
    
    def element(self, coeffs: List[int]):
        """Создаёт элемент поля."""
        return FiniteFieldElement(coeffs, self)
    
    def zero(self):
        """Нулевой элемент."""
        return FiniteFieldElement([0] * self.r, self)
    
    def one(self):
        """Единичный элемент."""
        coeffs = [0] * self.r
        coeffs[0] = 1
        return FiniteFieldElement(coeffs, self)
    
    def __repr__(self):
        return f"F_{self.p}^{self.r} with irreducible polynomial f(x) = {self._poly_to_str(self.f_coeffs)}"


def main():
    # Пример из текста: F_{5^2} с f(x) = x^2 + x + 2
    print("=" * 60)
    print("Построение конечного поля F_{5 ^ 2}")
    print("Неприводимый многочлен: f(x) = x ^ 2 + x + 2")
    print("=" * 60)
    
    F = FiniteField(p = 5, r = 2, f_coeffs = [2, 1, 1])
    print(F)
    print()
    
    # Создаём элемент g = 3x + 1
    g = F.element([1, 3])  # 3x + 1
    print(f"g(x) = {g}")
    
    # Находим обратный
    g_inv = g.inverse()
    print(f"g ^ {-1}(x) = {g_inv}")
    
    # Проверка: g * g^{-1} = 1
    prod = g * g_inv
    print(f"g * g ^ {-1} = {prod}")
    
    # Проверка сложения
    h = F.element([2, 4])  # 4x + 2
    print(f"\nh(x) = {h}")
    print(f"g + h = {g + h}")
    
    # Проверка умножения
    print(f"g * h = {g * h}")
    
    # Проверка возведения в степень
    print(f"g ^ 3 = {g ** 3}")
    
    # Пример поля F_{2 ^ 3} с f(x) = x ^ 3 + x + 1 (неприводим над Z_2)
    print("\n" + "=" * 60)
    print("Построение конечного поля F_{2 ^ 3}")
    print("Неприводимый многочлен: f(x) = x ^ 3 + x + 1")
    print("=" * 60)
    
    F2 = FiniteField(p = 2, r = 3, f_coeffs = [1, 1, 0, 1])  # x ^ 3 + x + 1
    print(F2)
    
    a = F2.element([1, 1, 0])  # x + 1
    b = F2.element([1, 0, 1])  # x ^ 2 + 1
    print(f"a(x) = {a}")
    print(f"b(x) = {b}")
    print(f"a + b = {a + b}")
    print(f"a * b = {a * b}")
    print(f"a ^ {-1} = {a.inverse()}")
    print(f"a * a ^ {-1} = {a * a.inverse()}")


if __name__ == "__main__":
    main()