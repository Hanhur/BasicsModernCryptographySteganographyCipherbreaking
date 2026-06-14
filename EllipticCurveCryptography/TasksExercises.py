# Задачи и упражнения
# Задача 1. =========================================================================================================================================
import math
import random
from dataclasses import dataclass
from typing import Optional, List, Tuple


class FieldElement:
    """Элемент простого поля F_p или поля характеристики 2 F_{2 ^ m}"""
    def __init__(self, value, mod = None, poly_mod = None, m = None):
        if mod is not None and not isinstance(value, FieldElement):
            self.value = value % mod
        else:
            self.value = value
        self.mod = mod
        self.poly_mod = poly_mod
        self.m = m
        self.is_binary = poly_mod is not None

    def __eq__(self, other):
        if not isinstance(other, FieldElement):
            return False
        return (self.value == other.value and self.mod == other.mod and 
                self.poly_mod == other.poly_mod)

    def __hash__(self):
        return hash((self.value, self.mod, self.poly_mod))

    def __repr__(self):
        if self.is_binary:
            return f"F2^{self.m}({bin(self.value)})"
        return f"F{self.mod}({self.value})"

    def __add__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        if self.is_binary:
            val = self.value ^ other.value
            return FieldElement(val, poly_mod = self.poly_mod, m = self.m)
        val = (self.value + other.value) % self.mod
        return FieldElement(val, mod = self.mod)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        if self.is_binary:
            return self + other
        val = (self.value - other.value) % self.mod
        return FieldElement(val, mod = self.mod)

    def __rsub__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        return other - self

    def __mul__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        if self.is_binary:
            return self._mul_binary(other)
        val = (self.value * other.value) % self.mod
        return FieldElement(val, mod = self.mod)

    def __rmul__(self, other):
        return self.__mul__(other)

    def _mul_binary(self, other):
        """Умножение в F_{2 ^ m} через полиномы с редукцией"""
        a, b = self.value, other.value
        res = 0
        while b:
            if b & 1:
                res ^= a
            a <<= 1
            if a & (1 << self.m):
                a ^= self.poly_mod
            b >>= 1
        return FieldElement(res, poly_mod = self.poly_mod, m = self.m)

    def __truediv__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        if other.value == 0:
            raise ZeroDivisionError("Division by zero")
        if self.is_binary:
            return self * other.inverse()
        inv = pow(other.value, -1, self.mod)
        return FieldElement((self.value * inv) % self.mod, mod = self.mod)

    def __rtruediv__(self, other):
        if isinstance(other, int):
            other = FieldElement(other, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        return other.__truediv__(self)

    def inverse(self):
        if self.value == 0:
            raise ZeroDivisionError("No inverse for zero")
        if self.is_binary:
            return FieldElement(self._poly_inv(), poly_mod = self.poly_mod, m = self.m)
        inv = pow(self.value, -1, self.mod)
        return FieldElement(inv, mod = self.mod)

    def _poly_inv(self):
        """Находит обратный полином в F_{2 ^ m} через расширенный алгоритм Евклида"""
        a, b = self.value, self.poly_mod
        inv, _ = self._poly_ext_gcd(a, b)
        return inv

    @staticmethod
    def _poly_ext_gcd(a, b):
        """Расширенный алгоритм Евклида для полиномов над GF(2)"""
        u, v = a, b
        x1, x2 = 1, 0
        while v:
            deg_u = u.bit_length() - 1
            deg_v = v.bit_length() - 1
            if deg_u < deg_v:
                u, v = v, u
                x1, x2 = x2, x1
                continue
            shift = deg_u - deg_v
            q = 1 << shift
            u ^= (v << shift)
            x1 ^= (x2 << shift)
        return x1, u

    def __pow__(self, exp):
        res = FieldElement(1 if not self.is_binary else 1, mod = self.mod, poly_mod = self.poly_mod, m = self.m)
        base = self
        while exp > 0:
            if exp & 1:
                res = res * base
            base = base * base
            exp >>= 1
        return res


class EllipticCurve:
    """Эллиптическая кривая над F_p или F_{2 ^ m}"""
    def __init__(self, a, b, field_mod = None, binary = False, m = None, poly_mod = None):
        """
        Для F_p: curve y ^ 2 = x ^ 3 + a * x + b
        Для F_{2 ^ m}: curve y ^ 2 + x * y = x ^ 3 + a * x ^ 2 + b
        """
        self.binary = binary
        if binary:
            self.m = m
            self.poly_mod = poly_mod
            self.a = FieldElement(a, poly_mod = poly_mod, m = m)
            self.b = FieldElement(b, poly_mod = poly_mod, m = m)
        else:
            self.mod = field_mod
            self.a = FieldElement(a, mod = field_mod)
            self.b = FieldElement(b, mod = field_mod)

    def point(self, x, y):
        return Point(self, x, y)

    def infinity(self):
        return Point(self, None, None)

    def is_on_curve(self, p):
        if p.is_infinity:
            return True
        if self.binary:
            left = p.y * p.y + p.x * p.y
            right = p.x * p.x * p.x + self.a * p.x * p.x + self.b
        else:
            left = p.y * p.y
            right = p.x * p.x * p.x + self.a * p.x + self.b
        return left == right
    
    def get_all_points(self) -> List[Point]:
        """Находит все точки на кривой (только для маленьких полей)"""
        points = [self.infinity()]
        if self.binary:
            # Для F_{2^m}
            for x_val in range(1 << self.m):
                x = FieldElement(x_val, poly_mod = self.poly_mod, m = self.m)
                # Решаем y^2 + x*y = x^3 + a*x^2 + b
                # y^2 + x*y + (x^3 + a*x^2 + b) = 0
                # Это квадратное уравнение над GF(2^m)
                right = x * x * x + self.a * x * x + self.b
                # Trace для проверки существования решения
                # Упрощённо: перебираем y
                for y_val in range(1 << self.m):
                    y = FieldElement(y_val, poly_mod = self.poly_mod, m = self.m)
                    if y * y + x * y == right:
                        points.append(self.point(x, y))
        else:
            # Для F_p
            for x_val in range(self.mod):
                x = FieldElement(x_val, mod = self.mod)
                right = x * x * x + self.a * x + self.b
                # Находим y = sqrt(right) (если существует)
                for y_val in range(self.mod):
                    y = FieldElement(y_val, mod = self.mod)
                    if y * y == right:
                        points.append(self.point(x, y))
        return points


@dataclass
class Point:
    curve: EllipticCurve
    x: Optional[FieldElement]
    y: Optional[FieldElement]

    @property
    def is_infinity(self):
        return self.x is None or self.y is None

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        if self.is_infinity:
            return "Infinity"
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        if self == other:
            return self._double()
        if self.x == other.x:
            return self.curve.infinity()
        return self._add(other)

    def _add(self, other):
        """P + Q, P != Q, P != -Q"""
        if self.curve.binary:
            lam = (self.y + other.y) / (self.x + other.x)
            x3 = lam * lam + lam + self.x + other.x + self.curve.a
            y3 = lam * (self.x + x3) + x3 + self.y
        else:
            lam = (other.y - self.y) / (other.x - self.x)
            x3 = lam * lam - self.x - other.x
            y3 = lam * (self.x - x3) - self.y
        return Point(self.curve, x3, y3)

    def _double(self):
        """2P"""
        if self.curve.binary:
            if self.x.value == 0:
                return self.curve.infinity()
            lam = self.x + self.y / self.x
            x3 = lam * lam + lam + self.curve.a
            y3 = self.x * self.x + lam * x3 + x3
        else:
            three = FieldElement(3, mod=self.curve.mod)
            two = FieldElement(2, mod=self.curve.mod)
            lam = (three * self.x * self.x + self.curve.a) / (two * self.y)
            x3 = lam * lam - two * self.x
            y3 = lam * (self.x - x3) - self.y
        return Point(self.curve, x3, y3)

    def __mul__(self, k):
        """Скалярное умножение k * P"""
        if not isinstance(k, int):
            raise TypeError("Scalar must be integer")
        result = self.curve.infinity()
        addend = self
        n = k
        while n:
            if n & 1:
                result = result + addend
            addend = addend + addend
            n >>= 1
        return result

    def __rmul__(self, k):
        return self.__mul__(k)

    def order(self):
        """Находит порядок точки (только для маленьких полей)"""
        if self.is_infinity:
            return 1
        cnt = 1
        current = self
        while True:
            current = current + self
            cnt += 1
            if current.is_infinity:
                return cnt


# ========== Протоколы ==========

def ecdh(curve, P, alice_priv, bob_priv):
    """
    Протокол Диффи-Хеллмана на эллиптических кривых.
    Возвращает общий секрет (точку).
    """
    A = alice_priv * P
    B = bob_priv * P
    secret_alice = alice_priv * B
    secret_bob = bob_priv * A
    assert secret_alice == secret_bob, "ECDH failed: secrets don't match"
    return secret_alice


def massey_omura(curve, M, alice_key, bob_key):
    """
    Протокол Масси-Омуры на эллиптических кривых.
    M - точка-сообщение.
    alice_key, bob_key - секретные ключи (должны быть взаимно просты с порядком M)
    """
    n = M.order()
    
    # Проверка обратимости ключей
    if math.gcd(alice_key, n) != 1:
        raise ValueError(f"alice_key {alice_key} not invertible modulo {n}")
    if math.gcd(bob_key, n) != 1:
        raise ValueError(f"bob_key {bob_key} not invertible modulo {n}")
    
    # Шаг 1: Алиса -> Боб
    C1 = alice_key * M
    
    # Шаг 2: Боб -> Алиса
    C2 = bob_key * C1
    
    # Шаг 3: Алиса -> Боб (снимает свой ключ)
    alice_inv = pow(alice_key, -1, n)
    C3 = alice_inv * C2
    
    # Шаг 4: Боб снимает свой ключ
    bob_inv = pow(bob_key, -1, n)
    decrypted = bob_inv * C3
    
    return decrypted


# ========== Демонстрация ==========

def demo_f5():
    print("\n" + "=" * 60)
    print("Демонстрация над F5")
    print("=" * 60)
    # Кривая: y^2 = x^3 + x + 1
    curve = EllipticCurve(a = 1, b = 1, field_mod = 5)
    
    # Точка P = (0,1) порядка 4
    P = curve.point(FieldElement(0, mod = 5), FieldElement(1, mod = 5))
    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a.value} x + {curve.b.value}")
    print(f"Точка P = {P}, порядок = {P.order()}")
    
    # ECDH
    alice_priv = 2
    bob_priv = 3
    shared = ecdh(curve, P, alice_priv, bob_priv)
    print(f"\nECDH: общий секрет = {shared}")
    
    # Massey-Omura
    M = curve.point(FieldElement(2, mod = 5), FieldElement(1, mod = 5))
    print(f"\nMassey-Omura для M = {M}")
    alice_k = 2
    bob_k = 1
    decrypted = massey_omura(curve, M, alice_k, bob_k)
    print(f"Расшифрованная точка = {decrypted}")
    print(f"Успех: {decrypted == M}")


def demo_f13():
    print("\n" + "=" * 60)
    print("Демонстрация над F13")
    print("=" * 60)
    # Кривая: y^2 = x^3 + 3x + 8
    curve = EllipticCurve(a = 3, b = 8, field_mod = 13)
    # P = (2,5) - порядок 5
    P = curve.point(FieldElement(2, mod = 13), FieldElement(5, mod = 13))
    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a.value} x + {curve.b.value}")
    print(f"Точка P = {P}, порядок = {P.order()}")
    
    # ECDH
    alice_priv = 2
    bob_priv = 4
    shared = ecdh(curve, P, alice_priv, bob_priv)
    print(f"\nECDH: общий секрет = {shared}")
    
    # Massey-Omura
    M = curve.point(FieldElement(5, mod = 13), FieldElement(9, mod = 13))
    print(f"\nMassey-Omura для M = {M}")
    alice_k = 3
    bob_k = 7
    decrypted = massey_omura(curve, M, alice_k, bob_k)
    print(f"Расшифрованная точка = {decrypted}")
    print(f"Успех: {decrypted == M}")


def demo_f24():
    print("\n" + "=" * 60)
    print("Демонстрация над F_{2 ^ 4}")
    print("=" * 60)
    # Поле F_{2^4} с неприводимым x^4 + x + 1 (0b10011)
    m = 4
    poly_mod = 0b10011  # x^4 + x + 1
    
    # Кривая: y^2 + x*y = x^3 + a*x^2 + b, a=1, b=1
    a = 1
    b = 1
    curve = EllipticCurve(a = a, b = b, binary = True, m = m, poly_mod = poly_mod)
    
    # Найдём все точки на кривой
    print("Нахождение всех точек на кривой...")
    all_points = curve.get_all_points()
    print(f"Всего точек: {len(all_points)} (включая бесконечность)")
    
    # Найдём точки с порядком > 2 для демонстрации
    points_with_orders = []
    for pt in all_points:
        if not pt.is_infinity:
            order = pt.order()
            points_with_orders.append((pt, order))
    
    # Отобразим точки и их порядки
    print("\nТочки на кривой и их порядки:")
    for pt, order in points_with_orders[:10]:  # покажем первые 10
        print(f"  {pt} -> порядок {order}")
    
    # Выберем базовую точку P для ECDH (порядка 15 или большого)
    P = None
    for pt, order in points_with_orders:
        if order > 10:  # ищем точку большого порядка
            P = pt
            print(f"\nВыбрана точка P = {P} с порядком {order}")
            break
    
    if P is None:
        P = points_with_orders[0][0]
        print(f"\nИспользуем точку P = {P} с порядком {P.order()}")
    
    # ECDH
    alice_priv = 3
    bob_priv = 7
    print(f"\nECDH: Алиса секрет={alice_priv}, Боб секрет={bob_priv}")
    shared = ecdh(curve, P, alice_priv, bob_priv)
    print(f"Общий секрет = {shared}")
    
    # Massey-Omura - выберем точку с порядком, имеющим много обратимых ключей
    M = None
    for pt, order in points_with_orders:
        # Ищем точку с порядком, у которого есть обратимые ключи (не 2)
        if order not in [2, 4, 6] and order > 1:
            M = pt
            print(f"\nДля Massey-Omura выбрана точка M = {M} с порядком {order}")
            break
    
    if M is None:
        M = points_with_orders[1][0]
    
    n = M.order()
    # Выбираем ключи, взаимно простые с n
    alice_k = 3
    bob_k = 5
    # Проверяем взаимную простоту
    while math.gcd(alice_k, n) != 1:
        alice_k = (alice_k + 1) % n
        if alice_k == 0:
            alice_k = 2
    while math.gcd(bob_k, n) != 1:
        bob_k = (bob_k + 1) % n
        if bob_k == 0:
            bob_k = 2
    
    print(f"\nMassey-Omura: M = {M}")
    print(f"Порядок M = {n}")
    print(f"Ключи: Алиса = {alice_k}, Боб = {bob_k}")
    
    decrypted = massey_omura(curve, M, alice_k, bob_k)
    print(f"Расшифрованная точка = {decrypted}")
    print(f"Успех: {decrypted == M}")


if __name__ == "__main__":
    demo_f5()
    demo_f13()
    demo_f24()

# Задача 2. =========================================================================================================================================
"""
Программа для проверки, что на эллиптической кривой y ^ 2 + y = x ^ 3 над F_16
выполняется 3P = O для всех точек.
"""

# 1. Реализация поля GF(16) с неприводимым многочленом x^4 + x + 1

class GF16:
    """Поле GF(16) с многочленом x ^ 4 + x + 1"""
    
    # Неприводимый многочлен: x^4 + x + 1
    # В двоичном виде: 10011 (1*x^4 + 0*x^3 + 0*x^2 + 1*x + 1)
    MOD = 0b10011  # 19 в десятичной
    
    def __init__(self, value):
        """value - целое число от 0 до 15, представляющее элемент поля"""
        self.val = value & 0b1111  # 4 бита
    
    def __add__(self, other):
        """Сложение в GF(16) - это XOR"""
        return GF16(self.val ^ other.val)
    
    def __sub__(self, other):
        """Вычитание совпадает со сложением в характеристике 2"""
        return self.__add__(other)
    
    def __mul__(self, other):
        """Умножение в GF(16) через полиномиальное умножение и редукцию"""
        # Полиномиальное умножение
        product = 0
        a, b = self.val, other.val
        for i in range(4):
            if b & (1 << i):
                product ^= (a << i)
        
        # Редукция по модулю x^4 + x + 1
        # Пока есть биты выше 3-го
        for i in range(7, 3, -1):
            if product & (1 << i):
                # Вычитаем (x^i) и добавляем (x^(i-4) * (x^4 + x + 1))
                # x^(i-4) * (x^4 + x + 1) = x^i + x^(i-3) + x^(i-4)
                product ^= (1 << i)  # убираем x^i
                product ^= (1 << (i - 3))  # добавляем x^(i-3)
                product ^= (1 << (i - 4))  # добавляем x^(i-4)
        
        return GF16(product & 0b1111)
    
    def __pow__(self, exp):
        """Возведение в степень (exp - целое неотрицательное)"""
        if exp == 0:
            return GF16(1)
        result = GF16(1)
        base = self
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result
    
    def __eq__(self, other):
        return self.val == other.val
    
    def __repr__(self):
        return f"GF16({self.val:04b})"
    
    def __int__(self):
        return self.val

# Предопределённые элементы
GF16_ZERO = GF16(0)
GF16_ONE = GF16(1)

# 2. Все элементы GF(16)
all_elements = [GF16(i) for i in range(16)]

# 3. Реализация эллиптической кривой y^2 + y = x^3

class Point:
    """Точка на эллиптической кривой y ^ 2 + y = x ^ 3 над GF(16)"""
    
    def __init__(self, x, y, is_infinity = False):
        self.x = x  # элемент GF16
        self.y = y  # элемент GF16
        self.is_infinity = is_infinity
    
    def __eq__(self, other):
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y
    
    def __neg__(self):
        """Обратная точка: -(x, y) = (x, y + 1) в характеристике 2"""
        if self.is_infinity:
            return self
        return Point(self.x, self.y + GF16_ONE)
    
    def __add__(self, other):
        """Сложение точек на кривой"""
        # Бесконечно удалённая точка
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        
        # Если точки противоположны
        if self == -other:
            return Point(None, None, is_infinity = True)
        
        # Если точки совпадают (удвоение)
        if self == other:
            return self.double()
        
        # Общий случай: разные точки
        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y
        
        # λ = (y1 + y2) / (x1 + x2)
        # В характеристике 2 деление - это умножение на обратный элемент
        if (x1 + x2) == GF16_ZERO:
            # x1 == x2, но точки не противоположны - такого быть не может на этой кривой
            # Значит, точки одинаковые (уже обработано) или одна из них бесконечность
            raise ValueError("Некорректная ситуация при сложении")
        
        # Находим обратный элемент к (x1 + x2)
        inv_den = self.inverse(x1 + x2)
        lam = (y1 + y2) * inv_den
        
        # x3 = λ^2 + λ + x1 + x2
        x3 = lam * lam + lam + x1 + x2
        
        # y3 = λ*(x1 + x3) + y1 + 1
        y3 = lam * (x1 + x3) + y1 + GF16_ONE
        
        return Point(x3, y3)
    
    def double(self):
        """Удвоение точки: 2P"""
        x1, y1 = self.x, self.y
        
        # λ = x^2
        lam = x1 * x1
        
        # x3 = λ^2 + λ
        x3 = lam * lam + lam
        
        # y3 = λ*(x1 + x3) + y1 + 1
        y3 = lam * (x1 + x3) + y1 + GF16_ONE
        
        return Point(x3, y3)
    
    def __mul__(self, n):
        """Умножение точки на целое число (скалярное умножение)"""
        if n == 0 or self.is_infinity:
            return Point(None, None, is_infinity = True)
        
        result = Point(None, None, is_infinity = True)
        base = self
        
        while n > 0:
            if n & 1:
                result = result + base
            base = base.double()
            n >>= 1
        
        return result
    
    def __rmul__(self, n):
        return self.__mul__(n)
    
    @staticmethod
    def inverse(a):
        """Находит обратный элемент в GF(16)"""
        # a^(14) = a^(-1) в GF(16), так как a^15 = 1 для a ≠ 0
        if a == GF16_ZERO:
            raise ZeroDivisionError("Деление на ноль")
        
        # Возводим в степень 14
        return a ** 14
    
    def __repr__(self):
        if self.is_infinity:
            return "O (бесконечно удалённая точка)"
        return f"({int(self.x):04b}, {int(self.y):04b})"
    
    def order(self, max_order = 20):
        """Находит порядок точки"""
        if self.is_infinity:
            return 1
        
        P = self
        n = 1
        while n < max_order:
            P = P + self
            n += 1
            if P.is_infinity:
                return n
        return None  # Не нашли порядок в пределах max_order

# 4. Поиск всех точек на кривой

def find_all_points():
    """Находит все точки на кривой y ^ 2 + y = x ^ 3 над GF(16)"""
    points = []
    
    # Бесконечно удалённая точка
    points.append(Point(None, None, is_infinity = True))
    
    # Перебираем все x из GF(16)
    for x in all_elements:
        x3 = x * x * x  # x^3
        
        # Ищем y, такие что y^2 + y = x^3
        for y in all_elements:
            if y * y + y == x3:
                points.append(Point(x, y))
    
    return points

# 5. Основная проверка

def main():
    print("=" * 60)
    print("Проверка свойства 3P = O на кривой y ^ 2 + y = x ^ 3 над GF(16)")
    print("=" * 60)
    
    # Находим все точки
    all_points = find_all_points()
    print(f"\nВсего точек на кривой: {len(all_points)}")
    
    # Проверяем 3P = O для каждой точки
    print("\nПроверка 3P = O для всех точек:")
    all_good = True
    
    for i, P in enumerate(all_points):
        P3 = P * 3
        if not P3.is_infinity:
            print(f"  ❌ Точка {P}: 3P = {P3} (не бесконечность!)")
            all_good = False
        else:
            print(f"  ✅ Точка {i}: {P} → 3P = O")
    
    if all_good:
        print("\n✓ ВСЕ точки удовлетворяют 3P = O")
    else:
        print("\n✗ НЕ все точки удовлетворяют 3P = O")
    
    # Анализ структуры группы
    print("\n" + "=" * 60)
    print("Анализ структуры группы")
    print("=" * 60)
    
    orders = []
    for P in all_points:
        ord_P = P.order()
        orders.append(ord_P)
        if ord_P is not None:
            print(f"Точка {P}: порядок = {ord_P}")
        else:
            print(f"Точка {P}: порядок не найден (возможно > 20)")
    
    from collections import Counter
    order_counts = Counter(orders)
    print(f"\nРаспределение порядков: {dict(order_counts)}")
    
    # Вывод о структуре
    if all(ord in [1, 3] for ord in orders if ord is not None):
        print("\nВывод: все ненулевые точки имеют порядок 3.")
        print("Группа изоморфна Z / 3Z × Z / 3Z и содержит 9 точек.")
    elif len(all_points) == 9:
        print("\nВывод: группа содержит 9 точек, и 3P=O для всех P.")
        print("Следовательно, группа изоморфна Z / 3Z × Z / 3Z.")

if __name__ == "__main__":
    main()