# 1. Определения и основные факты
"""
Модуль для работы с эллиптическими кривыми над полями F_p (p ≠ 2, 3)
на основе теоретического материала.
Реализованы: проверка условий эллиптичности, групповой закон,
теорема Хассе, вывод всех точек.
"""

from dataclasses import dataclass
from typing import Optional, Set, Tuple, List


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y), где ax + by = gcd."""
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def modinv(a: int, p: int) -> int:
    """Обратный элемент по модулю p (p простое)."""
    g, x, _ = extended_gcd(a % p, p)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {p} не существует")
    return x % p


@dataclass(frozen = True)
class Point:
    """Точка эллиптической кривой: (x, y) или O (точка на бесконечности)."""
    x: Optional[int]
    y: Optional[int]
    
    def __post_init__(self):
        if self.x is None and self.y is None:
            # Точка на бесконечности O
            pass
        elif self.x is None or self.y is None:
            raise ValueError("Некорректная точка: оба поля должны быть None для O")
    
    @staticmethod
    def infinity() -> 'Point':
        """Возвращает точку на бесконечности O."""
        return Point(None, None)
    
    def is_infinity(self) -> bool:
        """Проверка, является ли точка точкой на бесконечности."""
        return self.x is None and self.y is None
    
    def __str__(self) -> str:
        if self.is_infinity():
            return "O"
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        if self.is_infinity() and other.is_infinity():
            return True
        if self.is_infinity() or other.is_infinity():
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        if self.is_infinity():
            return hash("infinity")
        return hash((self.x, self.y))
    
    def __lt__(self, other: 'Point') -> bool:
        """Для сортировки точек."""
        if self.is_infinity():
            return False
        if other.is_infinity():
            return True
        if self.x != other.x:
            return self.x < other.x
        return self.y < other.y


class EllipticCurve:
    """
    Эллиптическая кривая над полем F_p (p ≠ 2, 3) вида y² = x³ + a·x + b.
    Дискриминант Δ = 4a³ + 27b² ≠ 0 (условие отсутствия кратных корней).
    """
    
    def __init__(self, a: int, b: int, p: int, debug: bool = False):
        """
        Инициализация кривой.
        
        Args:
            a: коэффициент a в уравнении
            b: коэффициент b в уравнении
            p: характеристика поля (простое число, p ≠ 2, 3)
            debug: режим отладки
        """
        self.a = a % p
        self.b = b % p
        self.p = p
        self.debug = debug
        
        # Проверка условия эллиптичности (дискриминант ≠ 0 mod p)
        delta = (4 * pow(self.a, 3, p) + 27 * pow(self.b, 2, p)) % p
        if delta == 0:
            raise ValueError(f"Кривая не эллиптическая: дискриминант Δ ≡ 0 (mod {p})")
        
        # Кэш для точек
        self._points_cache: Optional[Set[Point]] = None
        self._group_order_cache: Optional[int] = None
    
    def discriminant(self) -> int:
        """Возвращает дискриминант кривой (как целое число, не по модулю)."""
        return 4 * self.a ** 3 + 27 * self.b ** 2
    
    def is_on_curve(self, point: Point) -> bool:
        """Проверяет, лежит ли точка на кривой."""
        if point.is_infinity():
            return True
        x, y = point.x, point.y
        # y² ≡ x³ + a·x + b (mod p)
        left = (y * y) % self.p
        right = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
        return left == right
    
    def neg(self, point: Point) -> Point:
        """Возвращает точку -P = (x, -y)."""
        if point.is_infinity():
            return point
        return Point(point.x, (-point.y) % self.p)
    
    def add(self, P: Point, Q: Point) -> Point:
        """
        Сложение двух точек на кривой: P + Q.
        """
        # Проверка, что точки принадлежат кривой
        if not self.is_on_curve(P):
            raise ValueError(f"Точка {P} не лежит на кривой")
        if not self.is_on_curve(Q):
            raise ValueError(f"Точка {Q} не лежит на кривой")
        
        # Случай 1: O + P = P
        if P.is_infinity():
            return Q
        if Q.is_infinity():
            return P
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        
        # Случай 2: P = -Q (противоположные точки)
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return Point.infinity()
        
        # Вычисление наклона λ
        if x1 != x2:
            # Случай 3: разные точки
            lam = ((y2 - y1) % self.p) * modinv((x2 - x1) % self.p, self.p) % self.p
        else:
            # Случай 4: P = Q (удвоение)
            if y1 == 0:
                return Point.infinity()
            # λ = (3·x1² + a) / (2·y1)
            numerator = (3 * pow(x1, 2, self.p) + self.a) % self.p
            denominator = (2 * y1) % self.p
            lam = numerator * modinv(denominator, self.p) % self.p
        
        # Вычисляем сумму
        # x3 = λ² - x1 - x2
        x3 = (lam * lam - x1 - x2) % self.p
        # y3 = λ·(x1 - x3) - y1
        y3 = (lam * (x1 - x3) - y1) % self.p
        
        result = Point(x3, y3)
        
        if self.debug:
            print(f"  add({P}, {Q})")
            print(f"    λ = {lam}")
            print(f"    x3 = {x3}")
            print(f"    y3 = {y3}")
            print(f"    результат = {result}")
        
        # Проверка результата (только если не отладочный режим)
        if not self.is_on_curve(result):
            raise RuntimeError(f"Результат {result} не лежит на кривой")
        
        return result
    
    def double(self, P: Point) -> Point:
        """Удвоение точки."""
        return self.add(P, P)
    
    def mul(self, k: int, P: Point) -> Point:
        """Умножение точки на скаляр."""
        if k < 0:
            return self.mul(-k, self.neg(P))
        result = Point.infinity()
        current = P
        n = k
        while n > 0:
            if n & 1:
                result = self.add(result, current)
            current = self.double(current)
            n >>= 1
        return result
    
    def order(self, P: Point) -> int:
        """Возвращает порядок точки P."""
        if P.is_infinity():
            return 1
        if not self.is_on_curve(P):
            raise ValueError(f"Точка {P} не лежит на кривой")
        
        max_order = self.group_order()
        current = P
        n = 1
        
        while not current.is_infinity():
            if n >= max_order:
                raise RuntimeError(f"Не удалось найти порядок точки {P} после {n} итераций")
            current = self.add(current, P)
            n += 1
        
        return n
    
    def all_points(self) -> Set[Point]:
        """Возвращает множество всех точек кривой."""
        if self._points_cache is not None:
            return self._points_cache
        
        points: Set[Point] = {Point.infinity()}
        
        for x in range(self.p):
            rhs = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y) % self.p == rhs:
                    points.add(Point(x, y))
        
        self._points_cache = points
        return points
    
    def get_all_points_sorted(self) -> List[Point]:
        """Возвращает отсортированный список всех точек."""
        points = self.all_points()
        return sorted(points, key = lambda pt: (pt.x is None, pt.x if pt.x is not None else -1, pt.y if pt.y is not None else 0))
    
    def group_order(self) -> int:
        """Возвращает порядок группы точек кривой."""
        if self._group_order_cache is not None:
            return self._group_order_cache
        self._group_order_cache = len(self.all_points())
        return self._group_order_cache
    
    def hasse_bound(self) -> Tuple[int, int]:
        """Возвращает границы Хассе."""
        q = self.p
        sqrt_q = q ** 0.5
        lower = int(q + 1 - 2 * sqrt_q)
        upper = int(q + 1 + 2 * sqrt_q)
        return (lower, upper)
    
    def trace(self) -> int:
        """Возвращает след Фробениуса."""
        return self.p + 1 - self.group_order()
    
    def is_supersingular(self) -> bool:
        """Проверка суперсингулярности."""
        t = self.trace()
        return t % self.p == 0
    
    def print_info(self):
        """Выводит информацию о кривой."""
        print(f"\nКривая: y² = x³ + {self.a}·x + {self.b} над F_{self.p}")
        print(f"Дискриминант Δ = {self.discriminant()}")
        print(f"Δ mod {self.p} = {(4 * self.a ** 3 + 27 * self.b ** 2) % self.p}")
        
        N = self.group_order()
        lower, upper = self.hasse_bound()
        t = self.trace()
        sqrt_p = self.p ** 0.5
        
        print(f"Порядок группы N = |G(E)| = {N}")
        print(f"Границы Хассе: {lower} ≤ N ≤ {upper}")
        print(f"t = p+1 - N = {t}")
        print(f"|t| = {abs(t)} ≤ 2√p = {2 * sqrt_p:.4f} → {'Выполняется' if abs(t) <= 2 * sqrt_p + 1e-9 else 'НЕ выполняется!'}")
        print(f"Суперсингулярная: {'Да' if self.is_supersingular() else 'Нет'}")
        
        points = self.get_all_points_sorted()
        if len(points) <= 50:
            print(f"Все точки ({len(points)}): {', '.join(str(p) for p in points)}")
        else:
            print(f"Всего точек: {len(points)}")


def test_double_point():
    """Тест удвоения точек."""
    print("=" * 60)
    print("ТЕСТ УДВОЕНИЯ ТОЧЕК")
    print("=" * 60)
    
    E = EllipticCurve(a = 2, b = 1, p = 5, debug = True)
    
    # Тестируем удвоение (0,4)
    P = Point(0, 4)
    print(f"\nУдвоение точки {P}:")
    double_P = E.double(P)
    print(f"Результат: {double_P}")
    print(f"Ожидается: (1, 2)")
    
    # Тестируем удвоение (0,1)
    P2 = Point(0, 1)
    print(f"\nУдвоение точки {P2}:")
    double_P2 = E.double(P2)
    print(f"Результат: {double_P2}")
    print(f"Ожидается: (0, 4)")


def verify_group_properties():
    """Проверка свойств группы для кривой из примера 66."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВОЙСТВ ГРУППЫ")
    print("=" * 60)
    
    E = EllipticCurve(a = 2, b = 1, p = 5, debug = False)
    points = E.get_all_points_sorted()
    
    print(f"Группа из {len(points)} точек: {', '.join(str(p) for p in points)}")
    
    # Проверка нейтрального элемента
    O = Point.infinity()
    print(f"\n1. Нейтральный элемент: {O}")
    for P in points:
        assert E.add(P, O) == P, f"{P} + O != {P}"
        assert E.add(O, P) == P, f"O + {P} != {P}"
    print("   ✓ O + P = P + O = P для всех P")
    
    # Проверка обратных элементов
    print("\n2. Обратные элементы:")
    for P in points:
        neg_P = E.neg(P)
        sum_result = E.add(P, neg_P)
        assert sum_result == O, f"{P} + {neg_P} = {sum_result} != O"
        print(f"   {P} + {neg_P} = {sum_result}")
    
    # Проверка коммутативности
    print("\n3. Коммутативность:")
    non_zero = [p for p in points if not p.is_infinity()]
    for P in non_zero:
        for Q in non_zero:
            pq = E.add(P, Q)
            qp = E.add(Q, P)
            assert pq == qp, f"{P} + {Q} = {pq} != {qp} = {Q} + {P}"
    print("   ✓ P + Q = Q + P для всех P, Q")
    
    # Проверка ассоциативности
    print("\n4. Ассоциативность:")
    for P in points:
        for Q in points:
            for R in points:
                left = E.add(E.add(P, Q), R)
                right = E.add(P, E.add(Q, R))
                if left != right:
                    print(f"   ОШИБКА: ({P} + {Q}) + {R} = {left} ≠ {right} = {P} + ({Q} + {R})")
                    # Выводим промежуточные вычисления
                    print(f"     {P} + {Q} = {E.add(P, Q)}")
                    print(f"     {Q} + {R} = {E.add(Q, R)}")
                    raise AssertionError(f"Ассоциативность нарушена")
    print("   ✓ (P + Q) + R = P + (Q + R) для всех P, Q, R")
    
    print("\n✓ Все свойства группы выполнены!")


if __name__ == "__main__":
    test_double_point()
    verify_group_properties()