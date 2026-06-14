# 1. Аналог возведения в степень
"""
Демонстрация аналогии: возведение в степень в мультипликативной группе поля
vs умножение точки на число в группе эллиптической кривой.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import random

# ========== Часть 1. Маленькая эллиптическая кривая для обучения ==========

@dataclass
class Point:
    """Точка на эллиптической кривой y ^ 2 = x ^ 3 + ax + b над полем F_p."""
    x: Optional[int]
    y: Optional[int]
    # Бесконечно удаленная точка (нейтральный элемент) представляется как (None, None)
    
    def __post_init__(self):
        self.is_inf = (self.x is None or self.y is None)
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self.is_inf and other.is_inf:
            return True
        if self.is_inf or other.is_inf:
            return False
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        if self.is_inf:
            return "О (точка в бесконечности)"
        return f"({self.x}, {self.y})"


class EllipticCurve:
    """
    Эллиптическая кривая: y ^ 2 = x ^ 3 + a * x + b (mod p)
    """
    def __init__(self, a: int, b: int, p: int):
        self.a = a
        self.b = b
        self.p = p
        # Проверка: 4a^3 + 27b^2 != 0 mod p (кривая неособая)
        delta = (4 * a ** 3 + 27 * b ** 2) % p
        if delta == 0:
            raise ValueError("Дискриминант равен 0 -> кривая особая, не подходит")
    
    def is_on_curve(self, point: Point) -> bool:
        """Проверяет, лежит ли точка на кривой."""
        if point.is_inf:
            return True
        x, y = point.x, point.y
        left = (y * y) % self.p
        right = (x * x * x + self.a * x + self.b) % self.p
        return left == right
    
    def add(self, P: Point, Q: Point) -> Point:
        """Сложение двух точек на эллиптической кривой."""
        if P.is_inf:
            return Q
        if Q.is_inf:
            return P
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        
        # Если точки разные
        if x1 != x2:
            lam = ((y2 - y1) * pow(x2 - x1, -1, self.p)) % self.p
        else:
            # Если точки совпадают (удвоение) и y != 0
            if y1 == 0:
                # Это приводит к бесконечно удалённой точке
                return Point(None, None)
            lam = ((3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p)) % self.p
        
        x3 = (lam * lam - x1 - x2) % self.p
        y3 = (lam * (x1 - x3) - y1) % self.p
        
        return Point(x3, y3)
    
    def mul(self, k: int, P: Point) -> Point:
        """
        Умножение точки на число: k * P = P + P + ... + P (k раз)
        Аналог возведения в степень в мультипликативной группе.
        Используется бинарный алгоритм (удвоение-и-сложение).
        """
        if k == 0 or P.is_inf:
            return Point(None, None)
        
        result = Point(None, None)  # нейтральный элемент
        base = P
        n = k
        while n > 0:
            if n & 1:
                result = self.add(result, base)
            base = self.add(base, base)
            n >>= 1
        return result
    
    def order(self, P: Point) -> int:
        """Находит порядок точки P (наименьшее n > 0 такое, что nP = O)."""
        if P.is_inf:
            return 1
        count = 1
        current = P
        while not current.is_inf:
            current = self.add(current, P)
            count += 1
            if count > self.p * 2:  # защита от бесконечного цикла
                return -1
        return count
    
    def generate_random_point(self) -> Point:
        """Генерирует случайную точку на кривой (для маленьких p — перебором)."""
        for _ in range(1000):
            x = random.randint(0, self.p - 1)
            # Вычисляем правую часть: x^3 + a*x + b mod p
            rhs = (x * x * x + self.a * x + self.b) % self.p
            # Ищем квадратный корень по модулю p (p должно быть простым)
            # Здесь для простоты используем квадратичный вычет через pow для p=3 mod 4
            if pow(rhs, (self.p - 1) // 2, self.p) != 1:
                continue
            y = pow(rhs, (self.p + 1) // 4, self.p)  # работает для p ≡ 3 mod 4
            return Point(x, y)
        raise RuntimeError("Не удалось найти точку на кривой")


# ========== Часть 2. Использование готовой кривой secp256k1 (как в Биткоине) ==========

def demo_secp256k1():
    """
    Демонстрация на реальной кривой из криптографии (secp256k1)
    через библиотеку ecdsa.
    """
    try:
        from ecdsa import SECP256k1, ellipticcurve
    except ImportError:
        print("\n[SKIP] Установите ecdsa: pip install ecdsa")
        return
    
    print("\n" + "=" * 60)
    print("Демонстрация на кривой secp256k1 (используется в Bitcoin)")
    print("=" * 60)
    
    # Параметры кривой
    curve = SECP256k1.curve
    generator = SECP256k1.generator
    order = SECP256k1.order
    
    print(f"Порядок группы: {order} ( ~2 ^ 256 )")
    print(f"Базовый элемент G: ({generator.x()}, {generator.y()})")
    
    # Генерируем закрытый ключ (k) и открытый ключ (K = k*G)
    private_key = 0x123456789abcdef  # пример (маленький для демо, в реальности огромен)
    public_key = private_key * generator
    
    print(f"\nЗакрытый ключ (k): {private_key}")
    print(f"Открытый ключ (K = k * G): ({public_key.x()}, {public_key.y()})")
    
    # Проверяем: подпись ECDSA использует те же операции
    print("\nАналогия операции 'возведение в степень' (g ^ k):")
    print(f"  В поле:   g ^ {private_key} = ...")
    print(f"  На кривой: {private_key} * G = вычисленная точка")
    
    # ECDLP: трудно найти k по G и k*G
    print("\n*** Проблема ECDLP: по G и k * G найти k — вычислительно сложно ***")


# ========== Часть 3. Демонстрация на маленькой кривой (понятный пример) ==========

def demo_small_curve():
    print("\n" + "=" * 60)
    print("Демонстрация на маленькой эллиптической кривой для обучения")
    print("=" * 60)
    
    # Кривая y^2 = x^3 + x + 1 над полем F_23
    # (порядок группы N = 29 для этой кривой, найдено экспериментально)
    p = 23
    a = 1
    b = 1
    curve = EllipticCurve(a, b, p)
    
    # Базовые точки
    G = Point(0, 1)  # 0^3+0+1=1, y^2=1 -> y=1 — подходит
    if not curve.is_on_curve(G):
        print("Ошибка: G не лежит на кривой")
        return
    
    print(f"Кривая: y ^ 2 = x ^ 3 + {a} x + {b} over F_{p}")
    print(f"Базовая точка G: {G}")
    
    # Вычисляем несколько кратных точек (аналог степеней)
    print("\nУмножение точки на число (аналог возведения в степень):")
    for k in range(1, 10):
        kG = curve.mul(k, G)
        print(f"{k} * G = {kG}")
    
    # Находим порядок точки G
    order_G = curve.order(G)
    print(f"\nПорядок точки G: {order_G}")
    print(f"Проверка: {order_G} * G = {curve.mul(order_G, G)} (нейтральный элемент)")
    
    # ECDLP на маленькой кривой
    print("\n*** Демонстрация проблемы дискретного логарифма (ECDLP) ***")
    private = 7
    public = curve.mul(private, G)
    print(f"Закрытый ключ (секрет): {private}")
    print(f"Открытый ключ (публичный): {public}")
    print(f"Зная G и {public}, найти private — это ECDLP.")
    
    # Атака перебором для маленькой кривой (только чтобы показать идею)
    print("\nДля маленькой кривой можно перебрать все k от 1 до порядка:")
    for k in range(1, order_G + 1):
        if curve.mul(k, G) == public:
            print(f"Найден логарифм: k = {k}")
            break
    
    print("\nВ реальной криптографии порядок группы огромен (~2 ^ 256), поэтому перебор невозможен.")


# ========== Часть 4. Аналогия со сравнением сложности (DLP vs ECDLP) ==========

def show_analogy_table():
    print("\n" + "=" * 60)
    print("Явная аналогия между группами")
    print("=" * 60)
    
    print("""
    ┌──────────────────────────────┬─────────────────────────────────────┐
    │  Мультипликативная группа Fp*│ Группа точек эллиптической кривой E │
    ├──────────────────────────────┼─────────────────────────────────────┤
    │ Групповая операция: умножение │ Групповая операция: сложение        │
    │ Нейтральный элемент: 1        │ Нейтральный элемент: O (бесконечность)│
    │ Обратный: g⁻¹ mod p           │ Обратный: -P (отражение по y)        │
    │ "Возведение в степень": g ^ k │ "Возведение в степень": k * P         │
    │ Проблема: DLP (g, g ^ k -> k) │ Проблема: ECDLP (P, kP -> k)        │
    └──────────────────────────────┴─────────────────────────────────────┘
    """)


# ========== Главная функция ==========

def main():
    print("=" * 60)
    print("АНАЛОГ ВОЗВЕДЕНИЯ В СТЕПЕНЬ НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("Из лекции: g ^ k (в поле)  →  kP (на кривой)")
    print("=" * 60)
    
    # Показываем таблицу аналогий
    show_analogy_table()
    
    # Демонстрация на маленькой понятной кривой
    demo_small_curve()
    
    # Демонстрация на реальной кривой secp256k1 (если установлена ecdsa)
    demo_secp256k1()
    
    print("\n" + "=" * 60)
    print("ВЫВОД: Ключевая идея — замена операции g ^ k на k * P")
    print("позволяет строить криптосистемы, аналогичные ElGamal или DSA,")
    print("но с меньшим размером ключа (256 бит вместо 3072) при той же стойкости.")
    print("=" * 60)


if __name__ == "__main__":
    main()