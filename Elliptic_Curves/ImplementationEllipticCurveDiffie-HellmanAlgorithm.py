# Реализация алгоритма Диффи — Хеллмана на эллиптических кривых
"""
Реализация алгоритма Диффи-Хеллмана на эллиптических кривых E: y ^ 2 = x ^ 3 + ax + b (mod p)
На основе материала из главы о ECDH
"""

class EllipticCurve:
    """Класс для работы с эллиптической кривой над конечным полем"""
    
    def __init__(self, a, b, p):
        """
        Инициализация кривой y ^ 2 = x ^ 3 + ax + b (mod p)
        """
        self.a = a
        self.b = b
        self.p = p
    
    def is_on_curve(self, point):
        """
        Проверка, принадлежит ли точка кривой
        """
        if point is None:  # Бесконечно удаленная точка
            return True
        
        x, y = point
        left = (y * y) % self.p
        right = (x * x * x + self.a * x + self.b) % self.p
        return left == right
    
    def add_points(self, P, Q):
        """
        Сложение двух точек на кривой
        Возвращает P + Q
        """
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        p = self.p
        a = self.a
        
        # Если точки противоположны (P = -Q)
        if x1 == x2 and (y1 + y2) % p == 0:
            return None  # Бесконечно удаленная точка
        
        # Вычисление наклона (slope)
        if x1 == x2 and y1 == y2:
            # Удвоение точки: s = (3*x1^2 + a) / (2*y1)
            numerator = (3 * x1 * x1 + a) % p
            denominator = (2 * y1) % p
            s = numerator * self._mod_inverse(denominator) % p
        else:
            # Сложение разных точек: s = (y2 - y1) / (x2 - x1)
            numerator = (y2 - y1) % p
            denominator = (x2 - x1) % p
            s = numerator * self._mod_inverse(denominator) % p
        
        # Вычисление координат результирующей точки
        x3 = (s * s - x1 - x2) % p
        y3 = (s * (x1 - x3) - y1) % p
        
        return (x3, y3)
    
    def scalar_multiply(self, k, P):
        """
        Умножение точки на скаляр k (алгоритм "двоичного возведения в степень")
        Возвращает k * P
        """
        if P is None or k == 0:
            return None
        
        result = None  # Бесконечно удаленная точка (нейтральный элемент)
        addend = P
        
        # Двоичный метод
        while k > 0:
            if k & 1:  # Если младший бит = 1
                result = self.add_points(result, addend)
            addend = self.add_points(addend, addend)  # Удвоение точки
            k >>= 1  # Сдвиг вправо
        
        return result
    
    def _mod_inverse(self, a):
        """
        Нахождение обратного элемента по модулю p
        Используется расширенный алгоритм Евклида
        """
        p = self.p
        # Расширенный алгоритм Евклида
        t, new_t = 0, 1
        r, new_r = p, a
        
        while new_r != 0:
            quotient = r // new_r
            t, new_t = new_t, t - quotient * new_t
            r, new_r = new_r, r - quotient * new_r
        
        if r > 1:
            raise ValueError(f"Элемент {a} не имеет обратного по модулю {p}")
        if t < 0:
            t = t + p
        
        return t
    
    def find_all_points(self):
        """
        Находит все точки на кривой (для малых p)
        Используется для демонстрации и проверки порядка
        """
        points = []
        
        # Проверяем все возможные x от 0 до p-1
        for x in range(self.p):
            # Вычисляем y^2 = x^3 + ax + b (mod p)
            y_squared = (x * x * x + self.a * x + self.b) % self.p
            
            # Находим квадратные корни по модулю p
            for y in range(self.p):
                if (y * y) % self.p == y_squared:
                    points.append((x, y))
        
        # Добавляем бесконечно удаленную точку (представлена как None)
        return points
    
    def find_order(self, G):
        """
        Находит порядок точки G (наименьшее n, такое что n * G = O)
        """
        if G is None:
            return 1
        
        point = G
        k = 1
        
        while True:
            point = self.add_points(point, G)
            k += 1
            if point is None:  # Достигли бесконечно удаленной точки
                return k


def diffie_hellman_ecdh():
    """
    Основная функция, реализующая алгоритм Диффи-Хеллмана на эллиптических кривых
    """
    print("=" * 70)
    print("АЛГОРИТМ ДИФФИ-ХЕЛЛМАНА НА ЭЛЛИПТИЧЕСКИХ КРИВЫХ (ECDH)")
    print("=" * 70)
    
    # Шаг 1: Инициализация параметров
    print("\n[ШАГ 1] Инициализация параметров кривой")
    print("-" * 70)
    
    # Параметры из числового примера в тексте
    p = 17
    a = 2
    b = 2
    G = (5, 1)  # Образующий элемент (базовая точка)
    
    print(f"Кривая E: y ^ 2 = x ^ 3 + {a}x + {b} (mod {p})")
    print(f"Базовая точка G = {G}")
    
    # Создаем объект кривой
    curve = EllipticCurve(a, b, p)
    
    # Проверяем, что G лежит на кривой
    if curve.is_on_curve(G):
        print(f"✓ Точка G лежит на кривой")
    else:
        print(f"✗ ОШИБКА: Точка G не лежит на кривой!")
        return
    
    # Шаг 2: Находим порядок точки G
    print("\n[ШАГ 2] Определение порядка точки G (n)")
    print("-" * 70)
    
    n = curve.find_order(G)
    print(f"Порядок точки G: n = {n}")
    print(f"Проверка: {n}G = O (бесконечно удаленная точка)")
    
    # Находим все точки на кривой для проверки
    all_points = curve.find_all_points()
    print(f"Количество точек на кривой: {len(all_points) + 1} (включая O)")
    
    # Вычисляем кофактор
    h = (len(all_points) + 1) // n
    print(f"Кофактор h = {h}")
    
    if h == 1:
        print("✓ Оптимальный кофактор h = 1")
    elif h > 4:
        print(f"⚠ ВНИМАНИЕ: h = {h} > 4, кривая уязвима к атакам!")
    else:
        print(f"Кофактор h = {h}")
    
    # Демонстрация всех точек кратных G
    print("\n[ДЕМОНСТРАЦИЯ] Точки, порождаемые G:")
    print("-" * 70)
    for k in range(1, min(n + 1, 20)):
        point = curve.scalar_multiply(k, G)
        if point is None:
            print(f"{k:2d}G = O (бесконечно удаленная точка)")
        else:
            print(f"{k:2d}G = {point}")
    
    # Шаг 3: Генерация ключей
    print("\n[ШАГ 3] Генерация открытых и закрытых ключей")
    print("-" * 70)
    
    # Алиса выбирает закрытый ключ
    alpha = 3  # Из числового примера
    print(f"Алиса выбирает закрытый ключ α = {alpha} (1 ≤ α ≤ n - 1)")
    
    # Боб выбирает закрытый ключ
    beta = 9   # Из числового примера
    print(f"Боб выбирает закрытый ключ β = {beta} (1 ≤ β ≤ n - 1)")
    
    # Вычисление открытых ключей
    A = curve.scalar_multiply(alpha, G)  # Открытый ключ Алисы
    B = curve.scalar_multiply(beta, G)   # Открытый ключ Боба
    
    print(f"\nАлиса вычисляет открытый ключ A = α·G = {A}")
    print(f"Боб вычисляет открытый ключ B = β·G = {B}")
    
    # Шаг 4: Обмен ключами
    print("\n[ШАГ 4] Обмен открытыми ключами")
    print("-" * 70)
    print("Алиса → Боб: A =", A)
    print("Боб → Алиса: B =", B)
    
    # Шаг 5: Вычисление общего секрета
    print("\n[ШАГ 5] Вычисление общего секретного ключа")
    print("-" * 70)
    
    # Боб вычисляет общий ключ: K = β·A
    K_bob = curve.scalar_multiply(beta, A)
    print(f"Боб вычисляет K = β·A = {beta}·{A} = {K_bob}")
    
    # Алиса вычисляет общий ключ: K = α·B
    K_alice = curve.scalar_multiply(alpha, B)
    print(f"Алиса вычисляет K = α·B = {alpha}·{B} = {K_alice}")
    
    # Проверка совпадения
    print("\n[РЕЗУЛЬТАТ]")
    print("-" * 70)
    if K_alice == K_bob:
        print(f"✓ ОБЩИЙ СЕКРЕТНЫЙ КЛЮЧ: K = {K_alice}")
        print("  Ключи совпадают! Обмен прошел успешно.")
        
        # Проверяем, что это действительно 8G (из примера)
        K_expected = curve.scalar_multiply(8, G)
        print(f"\n  Проверка: K = 8G = {K_expected}")
        if K_alice == K_expected:
            print("  ✓ Совпадает с примером из текста: (13, 7)")
    else:
        print("✗ ОШИБКА: Ключи не совпадают!")
        print(f"  Алиса: {K_alice}")
        print(f"  Боб:   {K_bob}")
    
    # Шаг 6: Информация о безопасности
    print("\n[ИНФОРМАЦИЯ О БЕЗОПАСНОСТИ]")
    print("-" * 70)
    print("Для взлома Еве (злоумышленнику) необходимо решить задачу")
    print("дискретного логарифмирования на эллиптической кривой:")
    print(f"  Найти α из уравнения: A = α·G")
    print(f"  Или найти β из уравнения: B = β·G")
    print(f"\n  Размер группы: {n} элементов")
    print(f"  Сложность: O(√n) операций (алгоритм Полига-Хеллмана)")
    
    if n < 100:
        print("  ⚠ Параметры слишком малы для реального применения!")
        print("  В реальной криптографии используются простые числа ~ 2 ^ 256")
    
    print("\n" + "=" * 70)
    print("Программа завершена успешно!")
    print("=" * 70)


def demo_with_custom_parameters():
    """
    Демонстрация работы с пользовательскими параметрами
    """
    print("\n\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ С ПОЛЬЗОВАТЕЛЬСКИМИ ПАРАМЕТРАМИ")
    print("=" * 70)
    
    # Пользователь может изменить эти параметры
    # Внимание: не все параметры дадут циклическую группу!
    p = 23
    a = 1
    b = 1
    G = (3, 10)  # Должна лежать на кривой y^2 = x^3 + x + 1 (mod 23)
    
    print(f"\nКривая: y ^ 2 = x ^ 3 + {a}x + {b} (mod {p})")
    print(f"Точка G = {G}")
    
    curve = EllipticCurve(a, b, p)
    
    if not curve.is_on_curve(G):
        print("ОШИБКА: Точка не лежит на кривой!")
        return
    
    # Находим порядок
    n = curve.find_order(G)
    print(f"Порядок G: n = {n}")
    
    # Если порядок мал, показываем все точки
    if n <= 20:
        print("\nВсе кратные точки:")
        for k in range(1, n + 1):
            point = curve.scalar_multiply(k, G)
            if point is None:
                print(f"{k:2d}G = O")
            else:
                print(f"{k:2d}G = {point}")
    
    # Пример обмена ключами
    alpha = 5
    beta = 7
    
    A = curve.scalar_multiply(alpha, G)
    B = curve.scalar_multiply(beta, G)
    
    K_alice = curve.scalar_multiply(alpha, B)
    K_bob = curve.scalar_multiply(beta, A)
    
    print(f"\nОткрытый ключ Алисы: A = {A}")
    print(f"Открытый ключ Боба: B = {B}")
    print(f"Общий ключ: {K_alice if K_alice == K_bob else 'НЕ СОВПАДАЕТ!'}")


if __name__ == "__main__":
    # Запуск основной программы
    diffie_hellman_ecdh()
    
    # Раскомментируйте следующую строку для демонстрации с другими параметрами
    demo_with_custom_parameters()