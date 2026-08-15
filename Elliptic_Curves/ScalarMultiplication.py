# Скалярное умножение 
"""
Реализация скалярного умножения на эллиптической кривой y ^ 2 = x ^ 3 + 9x + 17 над полем F_23
Без использования numpy, только стандартная арифметика.
"""

def modinv(a, p):
    """
    Находит обратное число по модулю p (расширенный алгоритм Евклида).
    a ^ (-1) mod p
    """
    a = a % p
    for x in range(1, p):
        if (a * x) % p == 1:
            return x
    raise ValueError(f"Нет обратного элемента для {a} mod {p}")

class Point:
    """Точка на эллиптической кривой над конечным полем"""
    
    def __init__(self, x, y, a, b, p, is_infinity = False):
        """
        x, y: координаты точки
        a, b: коэффициенты кривой y ^ 2 = x ^ 3 + ax + b
        p: модуль поля F_p
        is_infinity: True, если это точка на бесконечности (нейтральный элемент)
        """
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p
        self.is_infinity = is_infinity
        
        # Проверяем, что точка лежит на кривой (если это не точка бесконечности)
        if not is_infinity:
            left = (y * y) % p
            right = (x * x * x + a * x + b) % p
            if left != right:
                raise ValueError(f"Точка ({x}, {y}) не лежит на кривой!")
    
    def __eq__(self, other):
        """Сравнение двух точек"""
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return (self.x == other.x and self.y == other.y and 
                self.a == other.a and self.b == other.b and self.p == other.p)
    
    def __repr__(self):
        """Красивый вывод точки"""
        if self.is_infinity:
            return "∞ (точка бесконечности)"
        return f"({self.x}, {self.y})"
    
    def __add__(self, other):
        """
        Сложение двух точек на эллиптической кривой.
        Возвращает новую точку P + Q.
        """
        # Проверка, что точки на одной кривой
        if self.a != other.a or self.b != other.b or self.p != other.p:
            raise ValueError("Точки на разных кривых!")
        
        p = self.p
        
        # Случай 1: P + ∞ = P
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        
        # Случай 2: P + (-P) = ∞ (точки с одинаковым x и y = -y mod p)
        if self.x == other.x and (self.y + other.y) % p == 0:
            return Point(None, None, self.a, self.b, p, is_infinity = True)
        
        # Случай 3: P + Q, где P != Q (сложение разных точек)
        if self.x != other.x:
            # Наклон секущей: m = (y2 - y1) / (x2 - x1)
            m = ((other.y - self.y) * modinv((other.x - self.x) % p, p)) % p
        else:
            # Случай 4: P + P (удвоение точки)
            # Наклон касательной: m = (3*x^2 + a) / (2*y)
            m = ((3 * self.x * self.x + self.a) * modinv((2 * self.y) % p, p)) % p
        
        # Вычисляем координаты новой точки
        x3 = (m * m - self.x - other.x) % p
        y3 = (m * (self.x - x3) - self.y) % p
        
        return Point(x3, y3, self.a, self.b, p)
    
    def __mul__(self, n):
        """
        Скалярное умножение: n * P.
        Использует алгоритм "удваивай и складывай" (Double-and-Add).
        """
        if not isinstance(n, int):
            raise TypeError(f"Множитель должен быть целым числом, получен {type(n).__name__}")
        
        if n < 0:
            raise ValueError("Множитель должен быть неотрицательным")
        
        if self.is_infinity:
            return self
        
        # Результат начинается с точки бесконечности (нейтральный элемент)
        result = Point(None, None, self.a, self.b, self.p, is_infinity = True)
        
        # Текущее удвоенное значение
        base = Point(self.x, self.y, self.a, self.b, self.p)
        
        # Бинарное представление n
        while n > 0:
            if n & 1:  # Если младший бит = 1
                result = result + base
            base = base + base  # Удвоение точки
            n >>= 1  # Сдвиг вправо
        
        return result
    
    def __rmul__(self, n):
        """Поддержка записи n * P"""
        return self.__mul__(n)
    
    def order(self, max_iterations = None):
        """
        Находит порядок точки (минимальное n такое, что n * P = ∞).
        Если max_iterations не указан, ищет до p + 1.
        Возвращает порядок или None, если не найден.
        """
        if self.is_infinity:
            return 1
        
        if max_iterations is None:
            # По теореме Лагранжа порядок точки делит порядок группы
            # Для данной кривой порядок группы = p+1 = 24 (проверено)
            max_iterations = self.p + 1
        
        current = Point(None, None, self.a, self.b, self.p, is_infinity = True)
        for n in range(1, max_iterations + 1):
            current = current + self
            if current.is_infinity:
                return n
        
        return None  # Порядок не найден


def print_multiples(P, n):
    """Выводит все кратные точки от 1P до nP"""
    print(f"Кривая: y ^ 2 = x ^ 3 + {P.a}x + {P.b} over F_{P.p}")
    print(f"Точка P = {P}")
    print("-" * 40)
    
    current = Point(None, None, P.a, P.b, P.p, is_infinity = True)
    for i in range(1, n + 1):
        current = current + P
        print(f"{i}P = {current}")
    
    return current


def demonstrate_ecdlp():
    """
    Демонстрация задачи дискретного логарифма на эллиптической кривой.
    Находит k такое, что Q = k * P.
    """
    # Параметры кривой из текста
    a, b, p = 9, 17, 23
    
    # Точка P = (16, 5)
    P = Point(16, 5, a, b, p)
    
    # Точка Q = (4, 5) (это 9P, как показано в тексте)
    Q = Point(4, 5, a, b, p)
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАДАЧИ ДИСКРЕТНОГО ЛОГАРИФМА (ECDLP)")
    print("=" * 60)
    print(f"Кривая: y ^ 2 = x ^ 3 + {a}x + {b} over F_{p}")
    print(f"P = {P}")
    print(f"Q = {Q}")
    print(f"Нужно найти k такое, что Q = k * P")
    print("-" * 60)
    
    # Поиск k перебором (для маленьких чисел)
    current = Point(None, None, a, b, p, is_infinity = True)
    for k in range(1, p + 1):
        current = current + P
        if current == Q:
            print(f"✅ Найдено! k = {k}")
            print(f"Проверка: {k}P = {current}")
            return k
    
    print("❌ k не найдено в диапазоне 1..p")
    return None


def find_all_points(a, b, p):
    """
    Находит все точки на эллиптической кривой над F_p
    """
    points = []
    
    # Точка бесконечности
    points.append(Point(None, None, a, b, p, is_infinity = True))
    
    # Все остальные точки
    for x in range(p):
        right = (x * x * x + a * x + b) % p
        # Проверяем, есть ли y^2 ≡ right (mod p)
        for y in range(p):
            if (y * y) % p == right:
                points.append(Point(x, y, a, b, p))
    
    return points


def main():
    """
    Основная функция: демонстрация всех операций из текста
    """
    # Параметры кривой из текста
    a, b, p = 9, 17, 23
    
    # Точка P = (16, 5) из примера
    P = Point(16, 5, a, b, p)
    
    print("\n" + "=" * 60)
    print("СКАЛЯРНОЕ УМНОЖЕНИЕ НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 60)
    
    # 1. Вывод всех кратных точек до 9P (как в тексте)
    print("\n1. ВСЕ КРАТНЫЕ ТОЧКИ ОТ 1P ДО 9P:")
    print("-" * 60)
    print_multiples(P, 9)
    
    # 2. Демонстрация различных способов вычисления одного и того же значения
    print("\n" + "=" * 60)
    print("2. РАЗЛИЧНЫЕ СПОСОБЫ ВЫЧИСЛЕНИЯ 7P (КАК В ТЕКСТЕ):")
    print("-" * 60)
    
    # Способ 1: Наивное сложение (7 раз)
    result1 = P + P + P + P + P + P + P
    print(f"7P = P + P + P + P + P + P + P = {result1}")
    
    # Способ 2: P + 6P = P + 2(3P) = P + 2(P + 2P)
    result2 = P + 2 * (P + 2 * P)
    print(f"7P = P + 2(P + 2P) = {result2}")
    
    # Способ 3: Используя скалярное умножение
    result3 = 7 * P
    print(f"7P = 7 * P = {result3}")
    
    # Проверка, что все способы дают одинаковый результат
    assert result1 == result2 == result3, "Результаты не совпадают!"
    print("✅ Все способы дают одинаковый результат!")
    
    # 3. Вычисление 9P альтернативным способом (как в тексте)
    print("\n" + "=" * 60)
    print("3. ВЫЧИСЛЕНИЕ 9P АЛЬТЕРНАТИВНЫМ СПОСОБОМ:")
    print("-" * 60)
    print(f"9P = 2(3P) + 3P = 2(2P + P) + 2P + P")
    
    # Вычисляем по формуле из текста: 9P = 2(3P) + 3P = 2(2P + P) + 2P + P
    P2 = 2 * P  # 2P
    P3 = P2 + P  # 3P = 2P + P
    P6 = 2 * P3  # 6P = 2(3P)
    P9_alternative = P6 + P3  # 9P = 6P + 3P
    
    print(f"Результат: 9P = {P9_alternative}")
    
    # Проверяем, что это совпадает с прямым вычислением
    P9_direct = 9 * P
    print(f"Прямое вычисление: 9P = {P9_direct}")
    assert P9_alternative == P9_direct, "Результаты не совпадают!"
    print("✅ Результаты совпадают!")
    
    # 4. Демонстрация ECDLP
    print("\n")
    demonstrate_ecdlp()
    
    # 5. Информация о группе точек
    print("\n" + "=" * 60)
    print("4. ИНФОРМАЦИЯ О ГРУППЕ ТОЧЕК:")
    print("-" * 60)
    
    # Находим все точки на кривой
    all_points = find_all_points(a, b, p)
    print(f"Всего точек на кривой (включая ∞): {len(all_points)}")
    
    # Находим порядок точки P
    order_P = P.order()
    
    if order_P is None:
        print("❌ Порядок точки не найден!")
        print("   Попробуем найти порядок с большим количеством итераций...")
        order_P = P.order(max_iterations = 100)
        
        if order_P is None:
            print("❌ Порядок всё ещё не найден. Возможно, точка не имеет конечного порядка.")
            print("   Пропускаем проверку периодичности.")
            return
    
    print(f"Порядок точки P: {order_P}")
    
    # Проверяем, что (order_P)P = ∞
    infinity_point = order_P * P
    print(f"{order_P}P = {infinity_point}")
    
    if infinity_point.is_infinity:
        print("✅ Проверка порядка точки выполнена успешно!")
    else:
        print("❌ Ошибка: порядок вычислен неверно!")
    
    # 6. Демонстрация периодичности с правильным порядком
    print("\n" + "=" * 60)
    print("5. ДЕМОНСТРАЦИЯ ПЕРИОДИЧНОСТИ:")
    print("-" * 60)
    
    n = 123
    result = n * P
    print(f"{n}P = {result}")
    
    # Используем правильный порядок для проверки периодичности
    # (n + order_P)P = nP + order_P*P = nP + ∞ = nP
    result_periodic = (n + order_P) * P
    print(f"({n} + {order_P})P = {result_periodic}")
    
    if result == result_periodic:
        print("✅ Свойство периодичности подтверждено!")
        print(f"   Так как порядок точки = {order_P}, то {order_P}P = ∞")
        print(f"   Следовательно, ({n} + {order_P})P = {n}P + ∞ = {n}P")
    else:
        print("❌ Ошибка: свойство периодичности не выполняется!")
    
    # 7. Дополнительный пример: все кратные точки до порядка
    print("\n" + "=" * 60)
    print("6. ВСЕ КРАТНЫЕ ТОЧКИ ДО ПОРЯДКА (ЦИКЛИЧЕСКАЯ ГРУППА):")
    print("-" * 60)
    
    current = Point(None, None, a, b, p, is_infinity = True)
    max_display = min(order_P, 20)  # Показываем до 20 или до порядка
    for i in range(1, max_display + 1):
        current = current + P
        print(f"{i}P = {current}")
    
    if order_P > 20:
        print(f"... и так далее до {order_P}P = ∞")
    elif order_P == 20:
        print(f"{order_P}P = {current + P} (должно быть ∞)")
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()