# 4. Аналог протокола Масси - Омуры
"""
Аналог протокола Масси - Омуры для эллиптических кривых
Исправленная версия с корректной работой с библиотекой ecpy
"""

from random import randint
from math import gcd


def mod_inverse(a: int, n: int) -> int:
    """
    Находит обратный элемент a ^ (-1) mod n
    Используется расширенный алгоритм Евклида
    """
    # Расширенный алгоритм Евклида
    t, new_t = 0, 1
    r, new_r = n, a
    
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    
    if r > 1:
        raise ValueError(f"Обратный элемент не существует: gcd({a}, {n}) = {r}")
    
    if t < 0:
        t += n
    
    return t


def generate_coprime(n: int, max_val: int = None) -> int:
    """
    Генерирует случайное число e, взаимно простое с n
    """
    if max_val is None:
        max_val = n - 1
    
    while True:
        e = randint(2, max_val)
        if gcd(e, n) == 1:
            return e


class SimpleEllipticCurve:
    """
    Простая реализация эллиптической кривой для демонстрации протокола
    y^2 = x^3 + ax + b mod p
    """
    
    def __init__(self, a: int, b: int, p: int, generator: tuple = None, order: int = None):
        self.a = a
        self.b = b
        self.p = p  # модуль (простое число)
        self.generator = generator  # базовая точка G
        self.order = order  # порядок кривой
        
        # Проверка дискриминанта
        disc = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
        if disc == 0:
            raise ValueError("Кривая сингулярна!")
    
    def is_on_curve(self, point):
        """Проверяет, лежит ли точка на кривой"""
        if point is None:
            return True  # нулевая точка (бесконечность)
        
        x, y = point
        left = pow(y, 2, self.p)
        right = (pow(x, 3, self.p) + self.a * x + self.b) % self.p
        return left == right
    
    def add(self, P, Q):
        """Сложение двух точек на кривой"""
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2 and y1 == y2:
            # Удвоение точки
            if y1 == 0:
                return None  # бесконечно удалённая точка
            # slope = (3x1^2 + a) / (2y1)
            slope_num = (3 * x1 * x1 + self.a) % self.p
            slope_den = (2 * y1) % self.p
            slope = slope_num * pow(slope_den, -2, self.p) % self.p
        else:
            # Обычное сложение
            if x1 == x2:
                return None
            slope_num = (y2 - y1) % self.p
            slope_den = (x2 - x1) % self.p
            slope = slope_num * pow(slope_den, -2, self.p) % self.p
        
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def multiply(self, k: int, P):
        """Умножение точки на скаляр (бинарный метод)"""
        if k == 0 or P is None:
            return None
        
        result = None
        current = P
        
        while k > 0:
            if k & 1:
                result = self.add(result, current)
            current = self.add(current, current)
            k >>= 1
        
        return result
    
    def find_order(self, P):
        """Находит порядок точки P (упрощённо, только для малых p)"""
        if P is None:
            return 1
        
        count = 1
        current = P
        while True:
            current = self.add(current, P)
            count += 1
            if current == P or count > self.p * 2:
                break
        
        return count


class MasseyOmuraProtocol:
    """
    Реализация протокола Масси-Омуры для эллиптических кривых
    """
    
    def __init__(self, curve: SimpleEllipticCurve, order: int):
        """
        Инициализация протокола
        
        Параметры:
            curve: эллиптическая кривая
            order: порядок кривой N = |E(F_q)|
        """
        self.curve = curve
        self.order = order
        self.e = None      # открытый ключ (шифрование)
        self.d = None      # закрытый ключ (дешифрование)
    
    def generate_keys(self):
        """
        Генерирует ключевую пару (e, d) для корреспондента
        e * d ≡ 1 (mod N)
        """
        self.e = generate_coprime(self.order)
        self.d = mod_inverse(self.e, self.order)
        return self.e, self.d
    
    def set_keys(self, e: int, d: int):
        """
        Устанавливает готовую ключевую пару
        """
        self.e = e
        self.d = d
    
    def encrypt(self, point, key: int = None):
        """
        Шифрует точку: умножает на ключ e
        """
        if key is None:
            key = self.e
        
        if point is None:
            return None
        
        return self.curve.multiply(key, point)
    
    def decrypt(self, point, key: int = None):
        """
        Дешифрует точку: умножает на ключ d
        """
        if key is None:
            key = self.d
        
        if point is None:
            return None
        
        return self.curve.multiply(key, point)


def find_all_points(curve: SimpleEllipticCurve):
    """Находит все точки на эллиптической кривой (для малых p)"""
    points = []
    
    # Нулевая точка (бесконечность)
    points.append(None)
    
    # Ищем все точки с целыми координатами
    for x in range(curve.p):
        # Вычисляем y^2 = x^3 + ax + b mod p
        y2 = (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p
        
        # Находим квадратные корни
        for y in range(curve.p):
            if (y * y) % curve.p == y2:
                points.append((x, y))
    
    return points


def find_generator_and_order(curve: SimpleEllipticCurve):
    """Находит генератор группы и её порядок (для малых p)"""
    all_points = find_all_points(curve)
    group_order = len(all_points)
    
    # Ищем точку максимального порядка
    for point in all_points[1:]:  # пропускаем нулевую точку
        order = curve.find_order(point)
        if order == group_order:
            return point, group_order
    
    # Если не нашли генератор, возвращаем первую не-нулевую точку
    return all_points[1], group_order


def main():
    """
    Демонстрация работы протокола
    """
    print("=" * 60)
    print("Аналог протокола Масси - Омуры для эллиптических кривых")
    print("=" * 60)
    
    # 1. Выбор эллиптической кривой
    print("\n1. Инициализация параметров...")
    
    # Используем небольшую кривую для наглядной демонстрации
    # y^2 = x^3 + 2x + 3 mod 97
    p = 97  # простое поле
    a = 2
    b = 3
    
    curve = SimpleEllipticCurve(a, b, p)
    print(f"Кривая: y ^ 2 = x ^ 3 + {a} x + {b} mod {p}")
    
    # Находим генератор и порядок группы
    generator, order = find_generator_and_order(curve)
    print(f"Найдена точка-генератор: {generator}")
    print(f"Порядок кривой N = {order}")
    
    # 2. Создание корреспондентов
    print("\n2. Генерация ключевых пар...")
    
    alice = MasseyOmuraProtocol(curve, order)
    bob = MasseyOmuraProtocol(curve, order)
    
    eA, dA = alice.generate_keys()
    eB, dB = bob.generate_keys()
    
    print(f"Алиса: eA = {eA}, dA = {dA}")
    print(f"Проверка: eA * dA ≡ {(eA * dA) % order} (mod {order})")
    print(f"Боб:   eB = {eB}, dB = {dB}")
    print(f"Проверка: eB * dB ≡ {(eB * dB) % order} (mod {order})")
    
    # 3. Сообщение для передачи
    print("\n3. Сообщение для передачи...")
    # Используем простую точку на кривой для демонстрации
    # Возьмём точку, кратную генератору
    message_scalar = 7
    Pm = curve.multiply(message_scalar, generator)
    
    print(f"Исходное сообщение (точка Pm) = {Pm}")
    print(f"Проверка: точка лежит на кривой? {curve.is_on_curve(Pm)}")
    
    # 4. Выполнение протокола
    print("\n4. Выполнение протокола...")
    print("-" * 40)
    
    # Шаг 1: Алиса -> Боб: eA * Pm
    step1 = alice.encrypt(Pm)
    print(f"Шаг 1: Алиса → Боб: eA * Pm = {step1}")
    
    # Шаг 2: Боб -> Алиса: eB * (eA * Pm)
    step2 = bob.encrypt(step1)
    print(f"Шаг 2: Боб → Алиса: eB * eA * Pm = {step2}")
    
    # Шаг 3: Алиса -> Боб: dA * (eB*eA*Pm)
    step3 = alice.decrypt(step2)
    print(f"Шаг 3: Алиса → Боб: dA * eB * eA * Pm = eB * Pm = {step3}")
    
    # Шаг 4: Боб расшифровывает: dB * (eB*Pm)
    final_point = bob.decrypt(step3)
    print(f"Шаг 4: Боб: dB * eB * Pm = Pm = {final_point}")
    
    # 5. Проверка
    print("\n5. Проверка результатов...")
    print("-" * 40)
    
    # Сравниваем точки
    if final_point == Pm:
        print("✓ УСПЕХ! Боб получил исходную точку Pm")
        print(f"  Полученная точка: {final_point}")
        print(f"  Исходная точка:   {Pm}")
    else:
        print("✗ ОШИБКА! Точки не совпадают")
        print(f"  Получено: {final_point}")
        print(f"  Ожидалось: {Pm}")
    
    # 6. Демонстрация с несколькими сообщениями
    print("\n6. Дополнительная демонстрация...")
    print("-" * 40)
    
    test_values = [3, 5, 11, 42]
    
    for val in test_values:
        P_test = curve.multiply(val, generator)
        
        # Выполняем протокол
        s1 = alice.encrypt(P_test)
        s2 = bob.encrypt(s1)
        s3 = alice.decrypt(s2)
        result = bob.decrypt(s3)
        
        if result == P_test:
            print(f"  ✓ Сообщение {val} → успешно")
        else:
            print(f"  ✗ Сообщение {val} → ошибка")


def demonstrate_attack_prevention():
    """
    Демонстрирует, почему протокол безопасен
    """
    print("\n" + "=" * 60)
    print("Демонстрация безопасности")
    print("=" * 60)
    
    # Параметры кривой
    p = 97
    a = 2
    b = 3
    
    curve = SimpleEllipticCurve(a, b, p)
    generator, order = find_generator_and_order(curve)
    
    # Создаём участников
    alice = MasseyOmuraProtocol(curve, order)
    bob = MasseyOmuraProtocol(curve, order)
    
    eA, dA = alice.generate_keys()
    eB, dB = bob.generate_keys()
    
    print(f"\nПараметры:")
    print(f"  Кривая: y ^ 2 = x ^ 3 + {a}x + {b} mod {p}")
    print(f"  Порядок группы: {order}")
    print(f"  eA = {eA}, eB = {eB}")
    
    # Сообщение
    message_scalar = 7
    Pm = curve.multiply(message_scalar, generator)
    print(f"  Секретное сообщение: P = {Pm}")
    
    print("\nПерехват трафика (злоумышленник видит только точки):")
    print("-" * 40)
    
    # Перехваченные точки
    step1 = eA * message_scalar if isinstance(Pm, tuple) else curve.multiply(eA, Pm)
    if Pm is not None and isinstance(Pm, tuple):
        step1 = alice.encrypt(Pm)
        step2 = bob.encrypt(step1)
        step3 = alice.decrypt(step2)
    
    print(f"Перехвачено 1: eA * Pm = {step1}")
    print(f"Перехвачено 2: eB * eA * Pm = {step2}")
    print(f"Перехвачено 3: eB * Pm = {step3}")
    
    print("\nДля получения Pm злоумышленнику нужно:")
    print("1. Решить задачу дискретного логарифмирования (ECDLP)")
    print("2. Найти eA из step1 и Pm ИЛИ eB из step3 и Pm")
    print("3. При больших порядках кривой (~2 ^ 256) это вычислительно невозможно")
    
    print("\n✓ Протокол безопасен при условии выбора криптостойкой кривой")


def demonstrate_mathematical_correctness():
    """
    Демонстрирует математическую корректность протокола
    """
    print("\n" + "=" * 60)
    print("Математическое обоснование")
    print("=" * 60)
    
    p = 97
    a = 2
    b = 3
    
    curve = SimpleEllipticCurve(a, b, p)
    generator, order = find_generator_and_order(curve)
    
    print(f"\nГруппа точек кривой E(F_{p}) имеет порядок N = {order}")
    print(f"eA * dA ≡ 1 mod N, eB * dB ≡ 1 mod N")
    
    # Произвольные ключи
    eA = 13
    eB = 17
    
    # Находим обратные
    dA = mod_inverse(eA, order)
    dB = mod_inverse(eB, order)
    
    print(f"\neA = {eA}, dA = {dA}")
    print(f"eB = {eB}, dB = {dB}")
    
    # Проверяем
    print(f"\nПроверка: {eA} * {dA} = {eA * dA} ≡ {(eA * dA) % order} (mod {order})")
    print(f"Проверка: {eB} * {dB} = {eB * dB} ≡ {(eB * dB) % order} (mod {order})")
    
    # Исходное сообщение
    P = generator
    print(f"\nИсходная точка: P = {P}")
    
    # Вычисления по протоколу
    step1 = curve.multiply(eA, P)
    print(f"Шаг 1: eA·P = {step1}")
    
    step2 = curve.multiply(eB, step1)
    print(f"Шаг 2: eB·(eA·P) = {step2}")
    
    step3 = curve.multiply(dA, step2)
    print(f"Шаг 3: dA·(eB·eA·P) = {step3}")
    
    result = curve.multiply(dB, step3)
    print(f"Шаг 4: dB·(eB·P) = {result}")
    
    print("\nМатематическое доказательство:")
    print("dB·(dA·(eB·(eA·P))) = dB·((dA·eA)·(eB·P)) = dB·(eB·P) = (dB·eB)·P = P")
    print("Благодаря коммутативности умножения скаляров и свойству e·d ≡ 1 (mod N)")


if __name__ == "__main__":
    main()
    demonstrate_attack_prevention()
    demonstrate_mathematical_correctness()