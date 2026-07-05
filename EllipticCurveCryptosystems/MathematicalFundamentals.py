# Математические основы
"""
Реализация эллиптической кривой над простым полем F_p
на основе материала из раздела 6.2 "Математические основы"

E: Y ^ 2 = X ^ 3 + aX + b (mod p)
где 4a ^ 3 + 27b ^ 2 != 0 (mod p)
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import math


@dataclass
class Point:
    """Точка на эллиптической кривой"""
    x: Optional[int] = None
    y: Optional[int] = None
    is_infinity: bool = False
    
    def __post_init__(self):
        """Точка в бесконечности имеет координаты None"""
        if self.is_infinity:
            self.x = None
            self.y = None
    
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
            return "O (точка в бесконечности)"
        return f"({self.x}, {self.y})"


class EllipticCurve:
    """
    Эллиптическая кривая E: Y ^ 2 = X ^ 3 + aX + b (mod p)
    """
    
    def __init__(self, a: int, b: int, p: int):
        """
        Инициализация кривой
        
        Args:
            a, b: коэффициенты кривой
            p: модуль (простое число)
        
        Raises:
            ValueError: если кривая сингулярная или p не простое
        """
        self.a = a
        self.b = b
        self.p = p
        
        # Проверка, что p - простое число (для простоты используем небольшую проверку)
        if not self._is_prime(p):
            raise ValueError(f"Модуль p = {p} должен быть простым числом")
        
        # Проверка условия несингулярности: 4a^3 + 27b^2 != 0 (mod p)
        discriminant = (4 * a ** 3 + 27 * b ** 2) % p
        if discriminant == 0:
            raise ValueError(
                f"Кривая сингулярна! 4a ^ 3 + 27b ^ 2 = {discriminant} (mod {p})"
            )
        
        self.discriminant = discriminant
        
        # Точка в бесконечности (нейтральный элемент)
        self.O = Point(is_infinity = True)
    
    @staticmethod
    def _is_prime(n: int) -> bool:
        """Проверка на простоту (для небольших чисел)"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _mod_inverse(self, v: int) -> int:
        """
        Обратный элемент по модулю p (расширенный алгоритм Евклида)
        """
        if v % self.p == 0:
            raise ValueError(f"Число {v} не имеет обратного по модулю {self.p}")
        
        # Расширенный алгоритм Евклида
        def egcd(a, b):
            if a == 0:
                return (b, 0, 1)
            else:
                g, x, y = egcd(b % a, a)
                return (g, y - (b // a) * x, x)
        
        g, x, _ = egcd(v % self.p, self.p)
        if g != 1:
            raise ValueError(f"Обратного элемента не существует для {v} mod {self.p}")
        return x % self.p
    
    def is_on_curve(self, point: Point) -> bool:
        """
        Проверяет, принадлежит ли точка кривой
        
        Точка (x, y) принадлежит кривой, если y ^ 2 = x ^ 3 + ax + b (mod p)
        """
        if point.is_infinity:
            return True
        
        x, y = point.x, point.y
        left = (y * y) % self.p
        right = (x ** 3 + self.a * x + self.b) % self.p
        return left == right
    
    def add(self, P: Point, Q: Point) -> Point:
        """
        Сложение двух точек P + Q на эллиптической кривой
        
        Реализует формулы из текста:
        - Если P = O, возвращаем Q
        - Если Q = O, возвращаем P
        - Если P = -Q, возвращаем O
        - Если P = Q, используем удвоение
        - Иначе используем формулу сложения
        """
        # Проверка, что точки лежат на кривой
        if not self.is_on_curve(P):
            raise ValueError(f"Точка {P} не лежит на кривой")
        if not self.is_on_curve(Q):
            raise ValueError(f"Точка {Q} не лежит на кривой")
        
        # Случай с точкой в бесконечности
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        
        # Проверка: P = -Q (вертикальная прямая)
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return self.O  # P + (-P) = O
        
        # Вычисление углового коэффициента k
        if P == Q:
            # Удвоение точки: k = (3x1^2 + a) / (2y1)
            if y1 % self.p == 0:
                # Касательная вертикальна, [2]P = O
                return self.O
            
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
            k = numerator * self._mod_inverse(denominator) % self.p
        else:
            # Сложение разных точек: k = (y2 - y1) / (x2 - x1)
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
            k = numerator * self._mod_inverse(denominator) % self.p
        
        # Вычисление координат результата
        # x3 = k^2 - x1 - x2 (mod p)
        x3 = (k * k - x1 - x2) % self.p
        
        # y3 = k(x1 - x3) - y1 (mod p)
        y3 = (k * (x1 - x3) - y1) % self.p
        
        result = Point(x3, y3)
        
        # Проверка, что результат лежит на кривой
        if not self.is_on_curve(result):
            raise RuntimeError(f"Внутренняя ошибка: {result} не лежит на кривой")
        
        return result
    
    def multiply(self, P: Point, m: int) -> Point:
        """
        Скалярное умножение [m]P = P + P + ... + P (m раз)
        
        Использует метод двоичного разложения (аналогично быстрому возведению в степень)
        """
        if not self.is_on_curve(P):
            raise ValueError(f"Точка {P} не лежит на кривой")
        
        if m == 0:
            return self.O
        
        # Обработка отрицательного m
        if m < 0:
            return self.multiply(self.negate(P), -m)
        
        # Бинарный метод (double-and-add)
        result = self.O
        base = P
        n = m
        
        while n > 0:
            if n & 1:  # Если текущий бит равен 1
                result = self.add(result, base)
            base = self.add(base, base)  # Удвоение
            n >>= 1  # Сдвиг вправо
        
        return result
    
    def negate(self, P: Point) -> Point:
        """
        Возвращает точку -P = (x, -y)
        """
        if P.is_infinity:
            return self.O
        return Point(P.x, (-P.y) % self.p)
    
    def find_points(self, max_x: Optional[int] = None) -> list:
        """
        Находит все точки на кривой (для малых p)
        
        Args:
            max_x: максимальное значение x (по умолчанию p - 1)
        
        Returns:
            Список всех точек (включая O)
        """
        if max_x is None:
            max_x = self.p - 1
        
        points = [self.O]
        
        for x in range(min(max_x + 1, self.p)):
            # Вычисляем y^2 = x^3 + ax + b (mod p)
            y_squared = (x ** 3 + self.a * x + self.b) % self.p
            
            # Находим квадратные корни по модулю p
            # Для простоты используем перебор (только для маленьких p)
            for y in range(self.p):
                if (y * y) % self.p == y_squared:
                    points.append(Point(x, y))
        
        return points
    
    def order(self, P: Point, max_steps: int = 10000) -> int:
        """
        Находит порядок точки P (наименьшее m > 0, такое что [m]P = O)
        """
        if P.is_infinity:
            return 1
        
        current = P
        for i in range(1, max_steps + 1):
            current = self.add(current, P) if i > 1 else P
            if current == self.O:
                return i + 1  # +1 потому что мы начали с P
        
        raise ValueError(f"Порядок точки не найден за {max_steps} шагов")


def main():
    """Демонстрация работы с эллиптической кривой"""
    
    print("=" * 60)
    print("РЕАЛИЗАЦИЯ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("E: Y ^ 2 = X ^ 3 + aX + b (mod p)")
    print("=" * 60)
    
    # Пример из текста: E7(2, 6)
    print("\n1. СОЗДАНИЕ КРИВОЙ E7(2, 6)")
    print("-" * 40)
    
    curve = EllipticCurve(a = 2, b = 6, p = 7)
    print(f"Кривая: Y ^ 2 = X ^ 3 + {curve.a}X + {curve.b} (mod {curve.p})")
    print(f"Дискриминант: {curve.discriminant} (не равен 0, кривая несингулярна)")
    
    # Находим все точки
    print("\n2. ВСЕ ТОЧКИ НА КРИВОЙ")
    print("-" * 40)
    points = curve.find_points()
    print(f"Всего точек (включая O): {len(points)}")
    for i, point in enumerate(points):
        print(f"  {i + 1:2d}. {point}")
    
    # Проверка точки (5, 1)
    print("\n3. ПРОВЕРКА ТОЧКИ (5, 1)")
    print("-" * 40)
    P = Point(5, 1)
    print(f"Точка P = {P}")
    print(f"Лежит на кривой: {curve.is_on_curve(P)}")
    
    # Удвоение точки [2]P
    print("\n4. УДВОЕНИЕ ТОЧКИ [2]P")
    print("-" * 40)
    P2 = curve.multiply(P, 2)
    print(f"[2]P = {P2}")
    print(f"Лежит на кривой: {curve.is_on_curve(P2)}")
    
    # [3]P
    print("\n5. [3]P = P + [2]P")
    print("-" * 40)
    P3 = curve.multiply(P, 3)
    print(f"[3]P = {P3}")
    print(f"Лежит на кривой: {curve.is_on_curve(P3)}")
    
    # Проверка групповых свойств
    print("\n6. ПРОВЕРКА ГРУППОВЫХ СВОЙСТВ")
    print("-" * 40)
    
    Q = Point(4, 6)  # [2]P
    S = Point(2, 5)  # [3]P
    
    print(f"P = {P}")
    print(f"Q = {Q}")
    print(f"S = {S}")
    
    # 1) Коммутативность: P + Q = Q + P
    PQ = curve.add(P, Q)
    QP = curve.add(Q, P)
    print(f"\n1) Коммутативность: P + Q = {PQ}, Q + P = {QP}")
    print(f"   P + Q == Q + P: {PQ == QP}")
    
    # 2) Ассоциативность: (P + Q) + S = P + (Q + S)
    PQ_S = curve.add(curve.add(P, Q), S)
    P_QS = curve.add(P, curve.add(Q, S))
    print(f"\n2) Ассоциативность: (P + Q) + S = {PQ_S}, P + (Q + S) = {P_QS}")
    print(f"   (P + Q) + S == P + (Q + S): {PQ_S == P_QS}")
    
    # 3) Нейтральный элемент: P + O = P
    P_O = curve.add(P, curve.O)
    print(f"\n3) Нейтральный элемент: P + O = {P_O}")
    print(f"   P + O == P: {P_O == P}")
    
    # 4) Обратный элемент: P + (-P) = O
    neg_P = curve.negate(P)
    P_negP = curve.add(P, neg_P)
    print(f"\n4) Обратный элемент: -P = {neg_P}")
    print(f"   P + (-P) = {P_negP}")
    print(f"   P + (-P) == O: {P_negP == curve.O}")
    
    # Порядок точки
    print("\n7. ПОРЯДОК ТОЧКИ P")
    print("-" * 40)
    try:
        order = curve.order(P)
        print(f"Порядок точки P: {order}")
        print(f"[{order}]P = {curve.multiply(P, order)}")
    except ValueError as e:
        print(f"Не удалось найти порядок: {e}")
    
    # Вычисление [m]P для разных m
    print("\n8. ВЫЧИСЛЕНИЕ [m]P")
    print("-" * 40)
    for m in range(1, 8):
        result = curve.multiply(P, m)
        print(f"[{m}]P = {result}")
        if result == curve.O:
            print(f"  ! Достигнута точка O при m = {m}")
    
    # Дополнительный пример с другой кривой
    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНЫЙ ПРИМЕР: КРИВАЯ E23(1, 1)")
    print("=" * 60)
    
    curve2 = EllipticCurve(a = 1, b = 1, p = 23)
    print(f"Кривая: Y ^ 2 = X ^ 3 + X + 1 (mod 23)")
    
    # Находим точку G
    G = Point(0, 1)  # Проверяем: 1^2 = 0^3 + 0 + 1 = 1 (mod 23)
    print(f"\nГенератор G = {G}")
    
    # Вычисляем степени G
    print("\nСтепени точки G:")
    for m in range(1, 10):
        result = curve2.multiply(G, m)
        print(f"[{m:2d}]G = {result}")
    
    # Демонстрация сложности дискретного логарифмирования
    print("\n" + "=" * 60)
    print("ДИСКРЕТНОЕ ЛОГАРИФМИРОВАНИЕ (ECDLC)")
    print("=" * 60)
    print("Задача: найти m, такое что [m]P = Q")
    print("Это сложная задача (экспоненциальная сложность)")
    print("Для демонстрации найдем m перебором для малой кривой:")
    
    # Для маленькой кривой найдем логарифм перебором
    P_small = Point(0, 1)
    Q_small = Point(6, 19)  # Это [7]P на кривой E23(1,1)
    
    print(f"\nP = {P_small}")
    print(f"Q = {Q_small}")
    
    found = False
    for m in range(1, 30):
        if curve2.multiply(P_small, m) == Q_small:
            print(f"Найдено: [{m}]P = Q")
            found = True
            break
    
    if not found:
        print("Q не является кратным P (в пределах проверенных m)")


if __name__ == "__main__":
    main()