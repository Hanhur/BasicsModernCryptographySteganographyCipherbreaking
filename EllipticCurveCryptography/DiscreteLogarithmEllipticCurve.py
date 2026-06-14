# 2. Дискретный логарифм над эллиптической кривой
"""
Программа для демонстрации проблемы дискретного логарифма
на эллиптической кривой (ECDLP) на основе текста.

Реализован алгоритм "шаг младенца — шаг великана" для решения
уравнения x * B = P, где B и P — точки эллиптической кривой.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple


@dataclass(frozen=True)
class Point:
    """Точка эллиптической кривой."""
    x: Optional[int]
    y: Optional[int]
    
    def __post_init__(self):
        """Проверка корректности точки."""
        if self.x is None and self.y is None:
            # Бесконечно удалённая точка (нейтральный элемент)
            return
        if self.x is None or self.y is None:
            raise ValueError("Неверное представление точки")
    
    @property
    def is_infinity(self) -> bool:
        """Проверка, является ли точка бесконечно удалённой."""
        return self.x is None and self.y is None
    
    def __str__(self) -> str:
        if self.is_infinity:
            return "∞"
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        if self.is_infinity:
            return hash((None, None))
        return hash((self.x, self.y))


class EllipticCurve:
    """
    Эллиптическая кривая над полем Fp: y ^ 2 = x ^ 3 + a * x + b (mod p)
    """
    
    def __init__(self, a: int, b: int, p: int):
        """
        Инициализация кривой.
        
        Args:
            a, b: Коэффициенты уравнения
            p: Характеристика поля (простое число)
        """
        self.a = a % p
        self.b = b % p
        self.p = p
        
        # Проверка дискриминанта (4a^3 + 27b^2 != 0 mod p)
        delta = (4 * pow(self.a, 3, p) + 27 * pow(self.b, 2, p)) % p
        if delta == 0:
            raise ValueError(f"Дискриминант равен 0: кривая сингулярна")
    
    def __str__(self) -> str:
        a_str = f"+ {self.a}" if self.a >= 0 else f"- {-self.a}"
        b_str = f"+ {self.b}" if self.b >= 0 else f"- {-self.b}"
        return f"y ^ 2 = x ^ 3 {a_str}x {b_str} over F_{self.p}"
    
    def is_on_curve(self, point: Point) -> bool:
        """Проверка, лежит ли точка на кривой."""
        if point.is_infinity:
            return True
        x, y = point.x, point.y
        left = pow(y, 2, self.p)
        right = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
        return left == right
    
    def negate(self, point: Point) -> Point:
        """
        Обратная точка: (x, -y mod p)
        """
        if point.is_infinity:
            return point
        return Point(point.x, (-point.y) % self.p)
    
    def double(self, point: Point) -> Point:
        """Удвоение точки."""
        if point.is_infinity:
            return point
        
        x1, y1 = point.x, point.y
        
        # Если y1 == 0, удвоение даёт бесконечно удалённую точку
        if y1 == 0:
            return Point(None, None)
        
        # lambda = (3*x1^2 + a) / (2*y1)
        numerator = (3 * pow(x1, 2, self.p) + self.a) % self.p
        denominator = (2 * y1) % self.p
        
        # Модульное деление через обратный элемент
        inv_den = pow(denominator, self.p - 2, self.p)
        lam = (numerator * inv_den) % self.p
        
        # x3 = lambda^2 - 2*x1
        x3 = (pow(lam, 2, self.p) - 2 * x1) % self.p
        # y3 = lambda*(x1 - x3) - y1
        y3 = (lam * (x1 - x3) - y1) % self.p
        
        return Point(x3, y3)
    
    def add(self, point1: Point, point2: Point) -> Point:
        """Сложение двух точек на кривой."""
        # Проверка на бесконечно удалённую точку
        if point1.is_infinity:
            return point2
        if point2.is_infinity:
            return point1
        
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y
        
        # Сложение точки с самой собой (удвоение)
        if point1 == point2:
            return self.double(point1)
        
        # Если x1 == x2 и y1 != y2, то сумма — бесконечно удалённая точка
        if x1 == x2:
            return Point(None, None)
        
        # lambda = (y2 - y1) / (x2 - x1)
        numerator = (y2 - y1) % self.p
        denominator = (x2 - x1) % self.p
        inv_den = pow(denominator, self.p - 2, self.p)
        lam = (numerator * inv_den) % self.p
        
        # x3 = lambda^2 - x1 - x2
        x3 = (pow(lam, 2, self.p) - x1 - x2) % self.p
        # y3 = lambda*(x1 - x3) - y1
        y3 = (lam * (x1 - x3) - y1) % self.p
        
        return Point(x3, y3)
    
    def subtract(self, point1: Point, point2: Point) -> Point:
        """
        Вычитание: point1 - point2 = point1 + (-point2)
        """
        return self.add(point1, self.negate(point2))
    
    def multiply(self, k: int, point: Point) -> Point:
        """
        Умножение точки на скаляр: k * point = point + point + ... + point (k раз).
        Используется алгоритм "удваивай и складывай" (double-and-add).
        Поддерживаются только неотрицательные скаляры.
        """
        if point.is_infinity:
            return point
        if k < 0:
            raise ValueError("Поддерживаются только неотрицательные скаляры")
        if k == 0:
            return Point(None, None)
        
        result = Point(None, None)  # Бесконечно удалённая точка
        current = point
        exp = k
        
        while exp > 0:
            if exp & 1:
                result = self.add(result, current)
            current = self.double(current)
            exp >>= 1
        
        return result
    
    def order(self, point: Point, max_order: int = 10000) -> Optional[int]:
        """
        Нахождение порядка точки (минимальное n > 0: n * point = ∞).
        Примечание: для больших порядков max_order следует увеличить.
        """
        if point.is_infinity:
            return 1
        
        current = point
        for n in range(1, max_order + 1):
            if current.is_infinity:
                return n
            current = self.add(current, point)
        
        return None  # Порядок не найден в пределах max_order
    
    def baby_step_giant_step(self, B: Point, P: Point, max_order: int = None) -> Optional[int]:
        """
        Решение ECDLP: нахождение x такого, что x * B = P.
        
        Алгоритм "шаг младенца — шаг великана" (Baby-Step Giant-Step).
        
        Args:
            B: Базисная точка (порождающая)
            P: Целевая точка (логарифм которой ищем)
            max_order: Максимальный порядок для поиска (если None — вычисляется)
        
        Returns:
            x (целое число) или None, если решение не найдено
        """
        # Определяем границы поиска
        if max_order is None:
            order = self.order(B)
            if order is None:
                raise ValueError("Не удалось определить порядок точки B")
        else:
            order = max_order
        
        m = int(order ** 0.5) + 1
        
        print(f"  Порядок точки: {order}")
        print(f"  Параметр m = ⌈√N⌉ = {m}")
        
        # Baby steps: вычисляем j*B для j = 0..m-1
        print("  Вычисление baby steps...")
        baby_steps: Dict[Point, int] = {}
        current = Point(None, None)  # 0*B = ∞
        for j in range(m):
            baby_steps[current] = j
            current = self.add(current, B)
        
        # Giant steps: вычисляем m * B
        print("  Вычисление giant steps...")
        mB = self.multiply(m, B)
        
        # giant = P - i*m*B  (i от 0 до m-1)
        # Используем вычитание через сложение с обратной точкой
        giant = P
        for i in range(m):
            if giant in baby_steps:
                x = baby_steps[giant] + i * m
                # Проверяем, что x действительно является решением
                if self.multiply(x, B) == P:
                    return x
            # giant = giant - mB  (вычитаем mB)
            giant = self.subtract(giant, mB)
        
        return None


def find_generator(curve: EllipticCurve, max_attempts: int = 100) -> Optional[Point]:
    """
    Поиск порождающей точки (генератора) группы.
    
    Args:
        curve: Эллиптическая кривая
        max_attempts: Максимальное количество попыток
    
    Returns:
        Порождающая точка или None, если не найдена
    """
    # Для небольшого поля просто перебираем все возможные x
    p = curve.p
    print("  Поиск подходящей базисной точки...")
    
    for x in range(p):
        rhs = (pow(x, 3, p) + curve.a * x + curve.b) % p
        # Проверяем, является ли rhs квадратичным вычетом
        # Простой способ: найти y, такой что y^2 ≡ rhs (mod p)
        for y in range(p):
            if (y * y) % p == rhs:
                point = Point(x, y)
                # Проверяем порядок точки
                order = curve.order(point, max_order = p + 1 + 2 * int(p ** 0.5) + 10)
                if order is not None and order == p + 1:  # Для простой кривой порядок может быть p+1
                    return point
    return None


def demo():
    """Демонстрация работы программы."""
    print("=" * 70)
    print("ДИСКРЕТНЫЙ ЛОГАРИФМ НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ (ECDLP)")
    print("=" * 70)
    
    # Пример: кривая y^2 = x^3 + 2x + 2 над F_17
    # Это небольшая кривая, удобная для демонстрации.
    a, b, p = 2, 2, 17
    curve = EllipticCurve(a, b, p)
    print(f"\nКривая: {curve}")
    print(f"Поле: F_{p}")
    
    # Найдём порождающую точку B
    # Для демонстрации используем известную точку на этой кривой
    B = Point(5, 1)  # (5,1) лежит на кривой: 1^2 = 1, 5^3+2*5+2 = 125+10+2=137 ≡ 1 mod 17
    
    if not curve.is_on_curve(B):
        print(f"Точка {B} не лежит на кривой!")
        return
    
    print(f"\nБазисная точка B = {B}")
    
    # Находим порядок B
    order = curve.order(B)
    if order is None:
        print("Не удалось определить порядок B (возможно, он слишком велик)")
        order = 19  # Для этой кривой порядок группы 19
    print(f"Порядок B: N = {order}")
    
    # Выбираем случайный секретный x и вычисляем P = x*B
    import random
    secret_x = random.randint(1, order - 1)
    P = curve.multiply(secret_x, B)
    print(f"\nСекретный логарифм (искомое x): {secret_x}")
    print(f"Целевая точка P = {secret_x} * B = {P}")
    
    # Проверяем, что P действительно лежит на кривой
    if curve.is_on_curve(P):
        print("✓ Точка P лежит на кривой")
    else:
        print("✗ Точка P не лежит на кривой!")
    
    # Решаем ECDLP: находим x по B и P
    print("\nЗапуск алгоритма baby-step giant-step...")
    found_x = curve.baby_step_giant_step(B, P, max_order = order)
    
    if found_x is not None:
        print(f"\n✅ Найденный логарифм: x = {found_x}")
        if found_x == secret_x:
            print("   (Совпадает с секретным значением!)")
        else:
            print(f"   ВНИМАНИЕ: не совпадает с секретным ({secret_x})")
    else:
        print("\n❌ Логарифм не найден")
    
    # Дополнительная проверка
    print("\n" + "-" * 70)
    print("ПРОВЕРКА:")
    test_P = curve.multiply(found_x, B) if found_x is not None else None
    if test_P is not None:
        print(f"  {found_x} * B = {test_P}")
        print(f"  Исходное P = {P}")
        if test_P == P:
            print("  ✓ Решение верно!")
    
    print("\n" + "=" * 70)
    print("ОБЪЯСНЕНИЕ (по тексту):")
    print("1. ECDLP — задача нахождения x: x·B = P")
    print("2. Алгоритм baby-step giant-step работает за O(√N) шагов")
    print("3. Для N ∼ 2²⁵⁶ это требует 2¹²⁸ операций — непрактично")
    print("4. Суперсингулярные кривые уязвимы к атаке через спаривание")
    print("5. Обычные кривые (как в примере) такой уязвимости не имеют")
    print("=" * 70)


def demo_simple():
    """Упрощённая демонстрация с заранее известными параметрами."""
    print("\n" + "=" * 70)
    print("УПРОЩЁННАЯ ДЕМОНСТРАЦИЯ (без автоматического поиска)")
    print("=" * 70)
    
    # Кривая secp256k1 (используется в Bitcoin) — упрощённый пример
    # Для демонстрации используем очень маленькую кривую
    a, b, p = 0, 7, 23  # y^2 = x^3 + 7 over F_23
    
    curve = EllipticCurve(a, b, p)
    print(f"\nКривая: {curve}")
    
    # Найдём все точки на кривой (для наглядности)
    points = []
    for x in range(p):
        rhs = (pow(x, 3, p) + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                points.append(Point(x, y))
    points.append(Point(None, None))  # Бесконечно удалённая точка
    
    print(f"Количество точек на кривой: {len(points)}")
    
    # Выберем базисную точку
    B = Point(3, 6)  # 6^2=36≡13, 3^3+7=27+7=34≡11 — не подходит
    # Найдём правильную точку
    for point in points:
        if not point.is_infinity and point.x == 3:
            B = point
            break
    
    if B.is_infinity:
        B = points[1]  # Берём первую не бесконечную точку
    
    print(f"Базисная точка B = {B}")
    
    # Вычисляем порядок
    order = curve.order(B)
    print(f"Порядок B: {order}")
    
    if order is None or order > 50:
        print("Порядок слишком велик для демонстрации, используем ограничение")
        order = 17
    
    # Простой тест
    for x in range(1, min(order, 10)):
        P = curve.multiply(x, B)
        print(f"{x} * B = {P}")
    
    print("\nДля решения ECDLP используется baby-step giant-step")
    print("с временем O(√N) и памятью O(√N).")


if __name__ == "__main__":
    demo()
    # demo_simple()  # Раскомментировать для упрощённой демонстрации