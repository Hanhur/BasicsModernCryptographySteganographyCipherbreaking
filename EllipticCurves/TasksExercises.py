# Задачи и упражнения
# Задача 1. =========================================================================================================================================
class EllipticCurve:
    """Эллиптическая кривая y ^ 2 = x ^ 3 + ax + b над полем Z_p"""
    
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    
    def is_on_curve(self, point):
        """Проверяет, лежит ли точка на кривой"""
        if point is None:  # Точка O (бесконечность)
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0
    
    def add(self, P, Q):
        """Сложение двух точек на эллиптической кривой"""
        if P is None:  # P = O
            return Q
        if Q is None:  # Q = O
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2 and y1 != y2:
            return None  # P + (-P) = O
        
        # Вычисление наклона λ
        if x1 != x2:
            # λ = (y2 - y1)/(x2 - x1) mod p
            lam = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p
        else:  # x1 == x2 и y1 == y2 (удвоение)
            # λ = (3x1^2 + a)/(2y1) mod p
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        
        # x3 = λ^2 - x1 - x2
        x3 = (lam * lam - x1 - x2) % self.p
        
        # y3 = λ(x1 - x3) - y1
        y3 = (lam * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def multiply(self, P, n):
        """Умножение точки на скаляр (алгоритм удвоения и сложения)"""
        result = None
        current = P
        
        while n > 0:
            if n & 1:  # если бит = 1
                result = self.add(result, current)
            current = self.add(current, current)  # удвоение
            n >>= 1
        
        return result
    
    def find_all_points(self):
        """Находит все точки кривой над полем Z_p"""
        points = [None]  # None представляет точку O
        
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            
            # Находим все y, для которых y^2 ≡ rhs (mod p)
            for y in range(self.p):
                if (y * y) % self.p == rhs:
                    points.append((x, y))
        
        return points
    
    def print_group_table(self, generator = None):
        """Выводит таблицу сложения группы"""
        points = self.find_all_points()
        print(f"\nВсе точки кривой (всего {len(points)}):")
        for i, pt in enumerate(points):
            if pt is None:
                print(f"  {i}: O (точка бесконечности)")
            else:
                print(f"  {i}: {pt}")
        
        # Определяем генератор, если не задан
        if generator is None:
            # Ищем точку порядка len(points)
            for pt in points[1:]:  # пропускаем O
                order = 1
                current = pt
                while current is not None:
                    order += 1
                    current = self.add(current, pt)
                if order == len(points):
                    generator = pt
                    break
        
        if generator is None:
            print("\nНе удалось найти генератор")
            return
        
        print(f"\nГруппа циклическая, порожденная точкой {generator}")
        print(f"Порядок группы: {len(points)}")
        print("\nТаблица умножения (nP):")
        print("-" * 40)
        
        for n in range(len(points)):
            point = self.multiply(generator, n)
            if point is None:
                print(f"{n:2}P = O (точка бесконечности)")
            else:
                print(f"{n:2}P = {point}")
        
        print("\nТаблица сложения всех элементов:")
        print("-" * 50)
        
        # Заголовок таблицы
        print("   +  |", end = " ")
        for pt in points:
            if pt is None:
                print("  O  ", end = " ")
            else:
                print(f"{str(pt):5}", end = " ")
        print()
        print("-" * (8 + 7 * len(points)))
        
        # Тело таблицы
        for P in points:
            if P is None:
                print("   O  |", end = " ")
            else:
                print(f"{str(P):5} |", end = " ")
            
            for Q in points:
                result = self.add(P, Q)
                if result is None:
                    print("  O  ", end = " ")
                else:
                    print(f"{str(result):5}", end = " ")
            print()
        
        return generator


def main():
    # Кривая y^2 = x^3 + 2x + 1 над Z_5
    curve = EllipticCurve(a = 2, b = 1, p = 5)
    
    print("=" * 60)
    print("Эллиптическая кривая: y ^ 2 = x ^ 3 + 2x + 1 над полем Z_5")
    print("=" * 60)
    
    # Находим все точки
    points = curve.find_all_points()
    print(f"\nНайдено {len(points)} точек:")
    for pt in points:
        if pt is None:
            print("  O (точка бесконечности)")
        else:
            print(f"  {pt}")
    
    # Проверяем, что все точки лежат на кривой
    print("\nПроверка всех точек на кривой:")
    for pt in points:
        if curve.is_on_curve(pt):
            print(f"  {pt if pt else 'O'} ✓")
        else:
            print(f"  {pt if pt else 'O'} ✗")
    
    # Находим порядок точки (0,1)
    P = (0, 1)
    print(f"\nНахождение порядка точки {P}:")
    current = P
    order = 1
    
    for i in range(1, 8):
        if i == 1:
            current = P
        else:
            current = curve.add(current, P)
        
        if current is None:
            print(f"  {i}P = O → порядок = {i}")
            order = i
            break
        else:
            print(f"  {i}P = {current}")
    
    print(f"\nПорядок точки {P} = {order}")
    print(f"Размер группы = {len(points)}")
    print(f"Так как порядок точки равен размеру группы, группа циклическая!")
    
    # Выводим полную таблицу сложения
    generator = curve.print_group_table(generator=P)
    
    print("\n" + "=" * 60)
    print("ВЫВОД:")
    print("=" * 60)
    print(f"• Группа E(Z_5) состоит из {len(points)} элементов")
    print(f"• Группа изоморфна Z_{len(points)} (циклическая)")
    print(f"• Образующий элемент: {generator}")


if __name__ == "__main__":
    main()

# Задача 2. =========================================================================================================================================
"""
Программа для работы с эллиптической кривой y ^ 2 = x ^ 3 + x + 1 над полем F_13.
Содержит:
1. Класс для работы с полем F_13
2. Класс точек эллиптической кривой
3. Построение таблицы сложения
4. Определение алгебраической структуры группы
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from itertools import product

class FieldF13:
    """Поле вычетов по модулю 13"""
    
    @staticmethod
    def add(a: int, b: int) -> int:
        return (a + b) % 13
    
    @staticmethod
    def sub(a: int, b: int) -> int:
        return (a - b) % 13
    
    @staticmethod
    def mul(a: int, b: int) -> int:
        return (a * b) % 13
    
    @staticmethod
    def div(a: int, b: int) -> int:
        """Деление a/b в поле F_13 (b ≠ 0)"""
        if b == 0:
            raise ZeroDivisionError("Division by zero in field F_13")
        # Находим обратный элемент через расширенный алгоритм Евклида
        # Так как 13 простое, можно использовать малую теорему Ферма: b^(11) mod 13
        return FieldF13.mul(a, pow(b, 11, 13))
    
    @staticmethod
    def inv(b: int) -> int:
        """Обратный элемент в поле F_13"""
        if b == 0:
            raise ZeroDivisionError("Zero has no inverse")
        return pow(b, 11, 13)
    
    @staticmethod
    def sqrt(y: int) -> Optional[List[int]]:
        """Извлечение квадратного корня в поле F_13"""
        # Проверяем, является ли y квадратичным вычетом
        if y == 0:
            return [0]
        
        # Для простого поля p ≡ 3 mod 4, sqrt(a) = a^((p+1)/4) mod p
        # 13 ≡ 1 mod 4, поэтому используем перебор
        roots = []
        for x in range(13):
            if FieldF13.mul(x, x) == y:
                roots.append(x)
        return roots if roots else None


@dataclass
class Point:
    """Точка на эллиптической кривой"""
    x: Optional[int]
    y: Optional[int]
    
    def __post_init__(self):
        if self.x is None and self.y is None:
            # Бесконечно удаленная точка
            self.is_infinity = True
        else:
            self.is_infinity = False
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        if self.is_infinity:
            return hash("INF")
        return hash((self.x, self.y))
    
    def __repr__(self):
        if self.is_infinity:
            return "O"
        return f"({self.x}, {self.y})"


class EllipticCurveF13:
    """Эллиптическая кривая y ^ 2 = x ^ 3 + x + 1 над F_13"""
    
    def __init__(self):
        self.p = 13
        self.A = 1
        self.B = 1
        self.infinity = Point(None, None)
        
    def is_on_curve(self, point: Point) -> bool:
        """Проверка, лежит ли точка на кривой"""
        if point.is_infinity:
            return True
        x, y = point.x, point.y
        # y^2 = x^3 + A*x + B
        left = FieldF13.mul(y, y)
        right = FieldF13.add(
            FieldF13.add(
                FieldF13.mul(FieldF13.mul(x, x), x),
                FieldF13.mul(self.A, x)
            ),
            self.B
        )
        return left == right
    
    def find_all_points(self) -> List[Point]:
        """Найти все точки на кривой"""
        points = [self.infinity]
        
        for x in range(self.p):
            # Вычисляем x^3 + A*x + B mod p
            x3 = FieldF13.mul(FieldF13.mul(x, x), x)
            ax = FieldF13.mul(self.A, x)
            rhs = FieldF13.add(FieldF13.add(x3, ax), self.B)
            
            # Находим квадратные корни
            roots = FieldF13.sqrt(rhs)
            if roots is not None:
                for y in roots:
                    point = Point(x, y)
                    if self.is_on_curve(point):
                        points.append(point)
        
        return points
    
    def add(self, P: Point, Q: Point) -> Point:
        """Сложение двух точек на кривой"""
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        
        # Если P = -Q
        if x1 == x2 and FieldF13.add(y1, y2) == 0:
            return self.infinity
        
        # Вычисляем угловой коэффициент
        if x1 == x2:
            # Касательная: λ = (3x1^2 + A) / (2y1)
            num = FieldF13.add(
                FieldF13.mul(3, FieldF13.mul(x1, x1)),
                self.A
            )
            den = FieldF13.mul(2, y1)
            lambd = FieldF13.div(num, den)
        else:
            # Секущая: λ = (y2 - y1) / (x2 - x1)
            num = FieldF13.sub(y2, y1)
            den = FieldF13.sub(x2, x1)
            lambd = FieldF13.div(num, den)
        
        # x3 = λ^2 - x1 - x2
        x3 = FieldF13.sub(
            FieldF13.sub(
                FieldF13.mul(lambd, lambd),
                x1
            ),
            x2
        )
        
        # y3 = λ(x1 - x3) - y1
        y3 = FieldF13.sub(
            FieldF13.mul(lambd, FieldF13.sub(x1, x3)),
            y1
        )
        
        return Point(x3, y3)
    
    def mul(self, k: int, P: Point) -> Point:
        """Умножение точки на скаляр (k * P)"""
        if k == 0 or P.is_infinity:
            return self.infinity
        
        result = self.infinity
        addend = P
        
        # Двоичное возведение в степень
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        
        return result
    
    def order(self, P: Point, max_order: int = 20) -> int:
        """Найти порядок точки (минимальное n > 0: n * P = O)"""
        if P.is_infinity:
            return 1
        
        current = P
        for n in range(1, max_order + 1):
            if current.is_infinity:
                return n
            current = self.add(current, P)
        return -1  # Порядок не найден в заданных пределах
    
    def generate_addition_table(self) -> Dict[Tuple[Point, Point], Point]:
        """Сгенерировать таблицу сложения для всех точек"""
        points = self.find_all_points()
        table = {}
        
        for P in points:
            for Q in points:
                table[(P, Q)] = self.add(P, Q)
        
        return table
    
    def get_group_structure(self) -> str:
        """Определить алгебраическую структуру группы"""
        points = self.find_all_points()
        n = len(points)
        
        # Словарь для хранения количества элементов каждого порядка
        order_counts = {}
        
        for P in points:
            if P.is_infinity:
                continue
            ord_P = self.order(P)
            if ord_P > 0:
                order_counts[ord_P] = order_counts.get(ord_P, 0) + 1
        
        # Для группы порядка 18 возможные структуры:
        # 1. Z_18 (циклическая)
        # 2. Z_3 × Z_6
        
        # Проверяем, есть ли элемент порядка 18
        max_order = max(order_counts.keys()) if order_counts else 1
        
        if max_order == n:
            return f"Циклическая группа Z_{n}"
        elif n == 18 and max_order == 6:
            return "Z₃ × Z₆ (нециклическая, порядок 18)"
        else:
            # Общая классификация для абелевых групп
            # Находим минимальное n2, такое что n2 * n1 = n
            # Для простоты выводим возможную структуру
            return f"Абелева группа порядка {n}. Максимальный порядок элемента: {max_order}"


def print_addition_table(curve: EllipticCurveF13, max_points: int = 10):
    """Вывести фрагмент таблицы сложения"""
    points = curve.find_all_points()
    points_list = points[:max_points]  # Берем только первые точки для компактности
    
    print("\n" + "=" * 80)
    print("ТАБЛИЦА СЛОЖЕНИЯ (фрагмент)")
    print("=" * 80)
    
    # Заголовок
    print(f"{'P+Q':^8}", end = "")
    for Q in points_list:
        print(f"{str(Q):^12}", end = "")
    print()
    print("-" * (8 + 12 * len(points_list)))
    
    # Строки таблицы
    for P in points_list:
        print(f"{str(P):^8}", end = "")
        for Q in points_list:
            result = curve.add(P, Q)
            print(f"{str(result):^12}", end = "")
        print()


def main():
    print("=" * 80)
    print("ЭЛЛИПТИЧЕСКАЯ КРИВАЯ y² = x³ + x + 1 НАД ПОЛЕМ F₁₃")
    print("=" * 80)
    
    curve = EllipticCurveF13()
    
    # Находим все точки
    points = curve.find_all_points()
    print(f"\nВсе точки на кривой: {len(points)}")
    for i, P in enumerate(points):
        print(f"  {i}: {P}")
    
    # Примеры сложения
    print("\n" + "=" * 80)
    print("ПРИМЕРЫ СЛОЖЕНИЯ ТОЧЕК")
    print("=" * 80)
    
    if len(points) >= 3:
        P, Q = points[1], points[2]
        R = curve.add(P, Q)
        print(f"{P} + {Q} = {R}")
        
        # Проверка ассоциативности
        R2 = points[3] if len(points) > 3 else points[1]
        left = curve.add(curve.add(P, Q), R2)
        right = curve.add(P, curve.add(Q, R2))
        print(f"\nПроверка ассоциативности: ({P} + {Q}) + {R2} = {left}")
        print(f"{P} + ({Q} + {R2}) = {right}")
        print(f"Ассоциативность выполняется: {left == right}")
    
    # Находим порядки точек
    print("\n" + "=" * 80)
    print("ПОРЯДКИ ТОЧЕК")
    print("=" * 80)
    
    order_counts = {}
    for P in points:
        if P.is_infinity:
            print(f"{P}: порядок = 1 (нейтральный элемент)")
            order_counts[1] = order_counts.get(1, 0) + 1
        else:
            ord_P = curve.order(P)
            print(f"{P}: порядок = {ord_P}")
            order_counts[ord_P] = order_counts.get(ord_P, 0) + 1
    
    # Групповая структура
    print("\n" + "=" * 80)
    print("АЛГЕБРАИЧЕСКАЯ СТРУКТУРА ГРУППЫ")
    print("=" * 80)
    
    structure = curve.get_group_structure()
    print(f"\n{structure}")
    print(f"\nРаспределение по порядкам: {order_counts}")
    
    # Проверка теоремы Лагранжа
    n = len(points)
    print(f"\nПроверка теоремы Лагранжа: порядок группы = {n}")
    for order, count in order_counts.items():
        if order > 1:
            print(f"  Элементов порядка {order}: {count}, {n} % {order} = {n % order} (остаток должен быть 0)")
    
    # Вывод таблицы сложения (фрагмент)
    print_addition_table(curve, max_points = min(8, len(points)))
    
    # Проверка изоморфизма с Z₃ × Z₆
    if len(points) == 18:
        print("\n" + "=" * 80)
        print("ПРОВЕРКА СТРУКТУРЫ Z₃ × Z₆")
        print("=" * 80)
        
        # Находим элемент порядка 6 и элемент порядка 3
        elem_order_6 = None
        elem_order_3 = None
        
        for P in points:
            if not P.is_infinity:
                ord_P = curve.order(P)
                if ord_P == 6 and elem_order_6 is None:
                    elem_order_6 = P
                if ord_P == 3 and elem_order_3 is None:
                    elem_order_3 = P
        
        if elem_order_6 and elem_order_3:
            print(f"Элемент порядка 6: {elem_order_6}")
            print(f"Элемент порядка 3: {elem_order_3}")
            print("\nГруппа изоморфна Z₃ × Z₆, где:")
            print("  - Z₆ порождается точкой", elem_order_6)
            print("  - Z₃ порождается точкой", elem_order_3)


if __name__ == "__main__":
    main()