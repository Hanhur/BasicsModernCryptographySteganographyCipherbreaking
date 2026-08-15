# Операции, выполняемые на эллиптических кривых
"""
Реализация эллиптической кривой E: y² = x³ + ax + b над полем действительных чисел.
БЕЗ использования NumPy.
"""

import math


class EllipticCurve:
    """Класс эллиптической кривой y² = x³ + a·x + b"""
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def is_on_curve(self, point):
        """Проверяет, лежит ли точка на кривой"""
        if point is None:  # Бесконечно удаленная точка
            return True
        x, y = point
        return abs(y ** 2 - (x ** 3 + self.a * x + self.b)) < 1e-10
    
    def __repr__(self):
        return f"E: y² = x³ + {self.a}·x + {self.b}"


class PointOperations:
    """Операции над точками эллиптической кривой"""
    
    def __init__(self, curve):
        self.curve = curve
        self.O = None  # Бесконечно удаленная точка (нейтральный элемент)
    
    def add(self, P, Q):
        """
        Сложение двух точек P + Q.
        Возвращает R = P + Q.
        """
        # Если P = O (бесконечность)
        if P is None:
            return Q
        # Если Q = O (бесконечность)
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        # Если точки симметричны относительно оси X (P = -Q)
        if x1 == x2 and abs(y1 + y2) < 1e-10:
            return None  # Результат - бесконечно удаленная точка O
        
        # Случай P = Q (удвоение)
        if P == Q:
            return self.double(P)
        
        # Общий случай: P ≠ Q
        # Вычисляем наклон s = (y1 - y2) / (x1 - x2)
        s = (y1 - y2) / (x1 - x2)
        
        # Координаты точки R
        x3 = s ** 2 - x1 - x2
        y3 = s * (x1 - x3) - y1
        
        return (x3, y3)
    
    def double(self, P):
        """
        Удвоение точки: 2P = P + P.
        """
        if P is None:
            return None
        
        x1, y1 = P
        
        # Если точка лежит на оси X (y = 0), то 2P = O
        if abs(y1) < 1e-10:
            return None
        
        # Вычисляем наклон касательной:
        # t = (3·x1² + a) / (2·y1)
        t = (3 * x1 ** 2 + self.curve.a) / (2 * y1)
        
        # Координаты точки R = 2P
        x3 = t ** 2 - 2 * x1
        y3 = t * (x1 - x3) - y1
        
        return (x3, y3)
    
    def multiply(self, P, n):
        """
        Скалярное умножение: n·P = P + P + ... + P (n раз)
        Использует алгоритм "Удваивай и складывай" (Double-and-Add)
        """
        if P is None or n == 0:
            return None
        
        # Бинарное представление n
        result = None  # Бесконечно удаленная точка (нейтральный элемент)
        base = P
        
        # Проходим по битам n от младшего к старшему
        while n > 0:
            if n & 1:  # Если текущий бит = 1
                result = self.add(result, base)
            base = self.double(base)
            n >>= 1  # Сдвигаем вправо
        
        return result


class PointVisualizer:
    """Визуализация точек на кривой в консоли"""
    
    @staticmethod
    def plot_points(curve, points, x_range = (-10, 10), y_range = (-10, 10), width = 50, height = 30):
        """
        Рисует ASCII-график кривой и отмеченных точек.
        """
        a, b = curve.a, curve.b
        
        # Масштабирование
        x_min, x_max = x_range
        y_min, y_max = y_range
        
        # Создаем пустую сетку
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Рисуем оси
        x_zero = int((-x_min) / (x_max - x_min) * width)
        y_zero = int((y_max) / (y_max - y_min) * height)
        
        for i in range(width):
            grid[y_zero][i] = '-' if i != x_zero else '+'
        for i in range(height):
            grid[i][x_zero] = '|' if i != y_zero else '+'
        
        # Рисуем кривую (приближенно)
        for i in range(width):
            x = x_min + (x_max - x_min) * i / width
            try:
                # y² = x³ + a·x + b
                y_sq = x ** 3 + a * x + b
                if y_sq >= 0:
                    y = math.sqrt(y_sq)
                    # Верхняя ветвь
                    j1 = int((y_max - y) / (y_max - y_min) * height)
                    if 0 <= j1 < height and grid[j1][i] == ' ':
                        grid[j1][i] = '·'
                    # Нижняя ветвь
                    j2 = int((y_max + y) / (y_max - y_min) * height)
                    if 0 <= j2 < height and grid[j2][i] == ' ':
                        grid[j2][i] = '·'
            except:
                pass
        
        # Отмечаем точки
        for idx, point in enumerate(points):
            if point is None:
                print("  O (бесконечно удаленная точка)")
                continue
            x, y = point
            if x_min <= x <= x_max and y_min <= y <= y_max:
                i = int((x - x_min) / (x_max - x_min) * width)
                j = int((y_max - y) / (y_max - y_min) * height)
                if 0 <= i < width and 0 <= j < height:
                    # Используем буквы для обозначения точек
                    label = chr(ord('A') + idx) if idx < 26 else '?'
                    grid[j][i] = label
        
        # Печатаем сетку
        print("\n" + "=" * (width + 2))
        for row in grid:
            print(' ' + ''.join(row))
        print("=" * (width + 2))
        print(f"Кривая: y² = x³ + {a}·x + {b}")
        print(f"Диапазон X: [{x_min}, {x_max}], Y: [{y_min}, {y_max}]")


def demo():
    """Демонстрация работы всех операций"""
    
    print("=" * 60)
    print("ЭЛЛИПТИЧЕСКИЕ КРИВЫЕ - ДЕМОНСТРАЦИЯ ОПЕРАЦИЙ")
    print("=" * 60)
    
    # Создаем кривую E: y² = x³ + 73 (как в вашем тексте)
    curve = EllipticCurve(a = 0, b = 73)
    ops = PointOperations(curve)
    
    print(f"\nКривая: {curve}")
    print(f"Дискриминант: Δ = -16·(4·a³ + 27·b²) = { -16 * (4 * 0 ** 3 + 27 * 73 ** 2) }")
    
    # Точки для демонстрации
    P = (1, math.sqrt(1 ** 3 + 73))  # (1, √74)
    Q = (2, math.sqrt(2 ** 3 + 73))  # (2, √81 = 9)
    
    print(f"\nИсходные точки:")
    print(f"  P = {P} (на кривой: {curve.is_on_curve(P)})")
    print(f"  Q = {Q} (на кривой: {curve.is_on_curve(Q)})")
    
    # 1. Сложение P + Q
    R = ops.add(P, Q)
    print(f"\n1. СЛОЖЕНИЕ: P + Q = R")
    print(f"   R = {R}")
    print(f"   R на кривой: {curve.is_on_curve(R)}")
    
    # 2. Удвоение 2P
    P2 = ops.double(P)
    print(f"\n2. УДВОЕНИЕ: 2P = P + P")
    print(f"   2P = {P2}")
    print(f"   2P на кривой: {curve.is_on_curve(P2)}")
    
    # 3. Скалярное умножение
    k = 5
    kP = ops.multiply(P, k)
    print(f"\n3. СКАЛЯРНОЕ УМНОЖЕНИЕ: {k}·P")
    print(f"   {k}P = {kP}")
    print(f"   {k}P на кривой: {curve.is_on_curve(kP)}")
    
    # Проверка ассоциативности: (P + Q) + R = P + (Q + R)
    print(f"\n4. ПРОВЕРКА АССОЦИАТИВНОСТИ:")
    left = ops.add(ops.add(P, Q), R)
    right = ops.add(P, ops.add(Q, R))
    print(f"   (P + Q) + R = {left}")
    print(f"   P + (Q + R) = {right}")
    print(f"   Равенство: {left == right}")
    
    # 5. Вертикальная линия (P + (-P) = O)
    minus_P = (P[0], -P[1])
    sum_zero = ops.add(P, minus_P)
    print(f"\n5. ВЕРТИКАЛЬНАЯ ЛИНИЯ: P + (-P) = O")
    print(f"   -P = {minus_P}")
    print(f"   P + (-P) = {sum_zero} (бесконечно удаленная точка)")
    
    # 6. Визуализация
    print("\n6. ВИЗУАЛИЗАЦИЯ НА ГРАФИКЕ:")
    viz = PointVisualizer()
    points_to_plot = [P, Q, R, P2, kP, minus_P]
    labels = ['P', 'Q', 'R', '2P', '5P', '-P']
    
    print("\nОтмеченные точки на графике:")
    for label, point in zip(labels, points_to_plot):
        if point is None:
            print(f"  {label}: O (бесконечность)")
        else:
            print(f"  {label}: ({point[0]:.2f}, {point[1]:.2f})")
    
    viz.plot_points(
        curve, 
        points_to_plot,
        x_range = (-5, 10),
        y_range = (-12, 12),
        width = 60,
        height = 25
    )
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    demo()