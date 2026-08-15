# Обзор эллиптических кривых
"""
Реализация эллиптической кривой secp256k1 на чистом Python
Без использования numpy, только встроенные типы данных
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import hashlib
import random
import secrets  # Для криптостойкой генерации случайных чисел

# ============================================================================
# ПАРАМЕТРЫ КРИВОЙ SECP256K1 (используется в Биткоине)
# ============================================================================

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F  # Простое число (модуль)
A = 0  # Коэффициент a в уравнении y² = x³ + ax + b
B = 7  # Коэффициент b
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798  # X координата генератора
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8  # Y координата генератора
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # Порядок группы
H = 1  # Кофактор


@dataclass
class Point:
    """Точка на эллиптической кривой"""
    x: int
    y: int
    is_infinity: bool = False  # Если True - это точка в бесконечности (нейтральный элемент)
    
    def __post_init__(self):
        if not self.is_infinity:
            # Валидация отключена для скорости, но можно включить при отладке
            # if not is_on_curve(self):
            #     raise ValueError(f"Точка ({self.x}, {self.y}) не лежит на кривой")
            pass
    
    def __eq__(self, other):
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        if self.is_infinity:
            return "∞ (Точка в бесконечности)"
        return f"({hex(self.x)}, {hex(self.y)})"


# ============================================================================
# БАЗОВЫЕ МАТЕМАТИЧЕСКИЕ ОПЕРАЦИИ В ПОЛЕ ПО МОДУЛЮ P
# ============================================================================

def mod_inv(a: int, p: int) -> int:
    """
    Обратное число по модулю p (расширенный алгоритм Евклида)
    a^(-1) mod p
    """
    if a == 0:
        raise ZeroDivisionError("Деление на ноль по модулю")
    
    # Используем расширенный алгоритм Евклида
    old_r, r = a, p
    old_s, s = 1, 0
    
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    
    if old_r != 1:
        raise ValueError(f"Элемент {a} не обратим по модулю {p}")
    
    return old_s % p


def mod_add(a: int, b: int, p: int) -> int:
    """Сложение по модулю p"""
    return (a + b) % p


def mod_sub(a: int, b: int, p: int) -> int:
    """Вычитание по модулю p"""
    return (a - b) % p


def mod_mul(a: int, b: int, p: int) -> int:
    """Умножение по модулю p"""
    return (a * b) % p


def mod_div(a: int, b: int, p: int) -> int:
    """Деление по модулю p: a * b^(-1) mod p"""
    return mod_mul(a, mod_inv(b, p), p)


# ============================================================================
# ОПЕРАЦИИ НАД ТОЧКАМИ ЭЛЛИПТИЧЕСКОЙ КРИВОЙ
# ============================================================================

def is_on_curve(point: Point) -> bool:
    """
    Проверяет, лежит ли точка на кривой y² = x³ + ax + b
    """
    if point.is_infinity:
        return True
    
    x, y = point.x, point.y
    left_side = (y * y) % P
    right_side = (x * x * x + A * x + B) % P
    return left_side == right_side


def point_add(p1: Point, p2: Point) -> Point:
    """
    Сложение двух точек на эллиптической кривой (геометрическое правило хорды и зеркала)
    """
    # Проверка на нейтральный элемент (точка в бесконечности)
    if p1.is_infinity:
        return Point(p2.x, p2.y, p2.is_infinity)
    if p2.is_infinity:
        return Point(p1.x, p1.y, p1.is_infinity)
    
    # Если точки совпадают - используем удвоение
    if p1.x == p2.x and p1.y == p2.y:
        return point_double(p1)
    
    # Если точки являются противоположными (p1 + (-p1) = ∞)
    if p1.x == p2.x and (p1.y + p2.y) % P == 0:
        return Point(0, 0, is_infinity = True)
    
    # Вычисление наклона (λ) секущей: (y2 - y1) / (x2 - x1) mod P
    λ = mod_div(mod_sub(p2.y, p1.y, P), mod_sub(p2.x, p1.x, P), P)
    
    # Координаты суммы: x3 = λ² - x1 - x2, y3 = λ(x1 - x3) - y1
    x3 = mod_sub(mod_sub(mod_mul(λ, λ, P), p1.x, P), p2.x, P)
    y3 = mod_sub(mod_mul(λ, mod_sub(p1.x, x3, P), P), p1.y, P)
    
    return Point(x3, y3)


def point_double(point: Point) -> Point:
    """
    Удвоение точки: 2P
    """
    if point.is_infinity:
        return Point(0, 0, is_infinity = True)
    
    x, y = point.x, point.y
    
    # Если y = 0, то касательная вертикальна -> результат ∞
    if y == 0:
        return Point(0, 0, is_infinity = True)
    
    # Вычисление наклона (λ) касательной: (3x² + a) / (2y) mod P
    # Для secp256k1: a = 0, поэтому λ = 3x² / (2y)
    numerator = mod_mul(3, mod_mul(x, x, P), P)  # 3x²
    denominator = mod_mul(2, y, P)               # 2y
    λ = mod_div(numerator, denominator, P)
    
    # Координаты удвоенной точки: x3 = λ² - 2x, y3 = λ(x - x3) - y
    x3 = mod_sub(mod_mul(λ, λ, P), mod_mul(2, x, P), P)
    y3 = mod_sub(mod_mul(λ, mod_sub(x, x3, P), P), y, P)
    
    return Point(x3, y3)


def scalar_mul(k: int, point: Point) -> Point:
    """
    Умножение скаляра на точку (Double-and-Add алгоритм)
    Результат: k * point
    """
    if point.is_infinity:
        return Point(0, 0, is_infinity = True)
    
    # Для отрицательного k: k*P = -(k*P)
    if k < 0:
        result = scalar_mul(-k, point)
        return negate_point(result)
    
    result = Point(0, 0, is_infinity = True)  # Начальное значение: нейтральный элемент
    base = Point(point.x, point.y, point.is_infinity)
    
    # Двоичный метод (Double-and-Add)
    while k > 0:
        if k & 1:  # Если младший бит = 1, добавляем базовую точку
            result = point_add(result, base)
        base = point_double(base)  # Удваиваем базовую точку
        k >>= 1  # Сдвигаем биты вправо
    
    return result


def negate_point(point: Point) -> Point:
    """
    Обратная точка: -P = (x, -y mod P)
    """
    if point.is_infinity:
        return Point(0, 0, is_infinity = True)
    return Point(point.x, (-point.y) % P, is_infinity = False)


# ============================================================================
# ГЕНЕРАТОР И БАЗОВЫЕ ТОЧКИ
# ============================================================================

G = Point(G_X, G_Y, is_infinity = False)  # Генераторная точка


def generate_private_key() -> int:
    """Генерирует случайный закрытый ключ (1 ≤ k ≤ N-1)"""
    # Используем secrets для криптостойкой генерации
    return secrets.randbelow(N - 1) + 1


def private_to_public(private_key: int) -> Point:
    """
    Преобразование закрытого ключа в открытый ключ
    PublicKey = PrivateKey * G (генераторная точка)
    """
    return scalar_mul(private_key, G)


# ============================================================================
# ECDSA: ЦИФРОВАЯ ПОДПИСЬ НА ЭЛЛИПТИЧЕСКИХ КРИВЫХ
# ============================================================================

def hash_message(message: bytes) -> int:
    """SHA-256 хеш сообщения как целое число"""
    return int.from_bytes(hashlib.sha256(message).digest(), 'big')


def ecdsa_sign(private_key: int, message: bytes) -> Tuple[int, int]:
    """
    Создание цифровой подписи ECDSA
    Возвращает (r, s)
    """
    z = hash_message(message) % N
    
    # Генерация случайного nonce (k) - используем secrets
    # НИКОГДА не повторяйте k для разных подписей!
    k = secrets.randbelow(N - 1) + 1
    
    # Вычисляем точку R = k * G
    R = scalar_mul(k, G)
    if R.is_infinity:
        raise RuntimeError("Ошибка: R - точка в бесконечности")
    
    r = R.x % N
    if r == 0:
        raise RuntimeError("r == 0, нужно перегенерировать k")
    
    # s = (z + r * private_key) / k mod N
    k_inv = mod_inv(k, N)
    s = mod_mul(mod_add(z, mod_mul(r, private_key, N), N), k_inv, N)
    
    if s == 0:
        raise RuntimeError("s == 0, нужно перегенерировать k")
    
    return (r, s)


def ecdsa_verify(public_key: Point, message: bytes, signature: Tuple[int, int]) -> bool:
    """
    Проверка ECDSA подписи
    """
    r, s = signature
    
    # Проверки: r и s должны быть в диапазоне [1, N-1]
    if r <= 0 or r >= N:
        return False
    if s <= 0 or s >= N:
        return False
    
    # Хеш сообщения
    z = hash_message(message) % N
    
    # Вычисляем: u1 = z / s mod N, u2 = r / s mod N
    s_inv = mod_inv(s, N)
    u1 = mod_mul(z, s_inv, N)
    u2 = mod_mul(r, s_inv, N)
    
    # Вычисляем точку: P = u1 * G + u2 * PublicKey
    point1 = scalar_mul(u1, G)
    point2 = scalar_mul(u2, public_key)
    P = point_add(point1, point2)
    
    # Подпись верна, если X-координата P совпадает с r
    return not P.is_infinity and P.x % N == r


# ============================================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================================

def demo():
    """Демонстрация всех возможностей программы"""
    print("=" * 70)
    print("ЭЛЛИПТИЧЕСКАЯ КРИВОГРАФИЯ НА SECP256K1")
    print("=" * 70)
    
    # 1. Проверка генераторной точки
    print("\n1. Генераторная точка G:")
    print(f"   G = {G}")
    print(f"   Лежит на кривой: {is_on_curve(G)}")
    
    # 2. Сложение точек
    print("\n2. Сложение точек:")
    P1 = G
    P2 = scalar_mul(2, G)  # 2G
    P3 = point_add(P1, P2)  # G + 2G = 3G
    print(f"   G + 2G = {P3}")
    print(f"   Должно быть равно 3G: {scalar_mul(3, G)}")
    
    # 3. Удвоение точек
    print("\n3. Удвоение точек:")
    doubled = point_double(G)
    print(f"   2G = {doubled}")
    print(f"   Должно быть равно G + G: {point_add(G, G)}")
    
    # 4. Генерация ключей
    print("\n4. Генерация ключей:")
    private_key = generate_private_key()
    public_key = private_to_public(private_key)
    print(f"   Закрытый ключ: {hex(private_key)[:20]}...")
    print(f"   Открытый ключ: {public_key}")
    
    # 5. ECDSA: Подпись и проверка
    print("\n5. ECDSA - Цифровая подпись:")
    # ИСПРАВЛЕНИЕ: Используем строку и кодируем в байты
    message = "Биткоин - это революция!"
    message_bytes = message.encode('utf-8')
    print(f"   Сообщение: '{message}'")
    
    # Подписываем
    signature = ecdsa_sign(private_key, message_bytes)
    r, s = signature
    print(f"   Подпись: r = {hex(r)[:15]}..., s = {hex(s)[:15]}...")
    
    # Проверяем
    is_valid = ecdsa_verify(public_key, message_bytes, signature)
    print(f"   Подпись верна: {is_valid}")
    
    # 6. Проверка подписи с измененным сообщением
    print("\n6. Проверка с измененным сообщением:")
    fake_message = "Биткоин - это пузырь!"
    fake_message_bytes = fake_message.encode('utf-8')
    is_valid_fake = ecdsa_verify(public_key, fake_message_bytes, signature)
    print(f"   Сообщение: '{fake_message}'")
    print(f"   Подпись верна: {is_valid_fake}")
    print(f"   (Должно быть False, т.к. сообщение изменено)")
    
    # 7. Умножение скаляра (демонстрация)
    print("\n7. Демонстрация умножения скаляра:")
    k = 5
    result = scalar_mul(k, G)
    print(f"   {k} * G = {result}")
    
    # Пошаговое отображение Double-and-Add для 5 (101 в двоичной)
    print(f"   Пошагово для {k} (101₂):")
    steps = []
    base = G
    temp_k = k
    while temp_k > 0:
        steps.append(f"бит = {temp_k & 1}")
        temp_k >>= 1
    print(f"   {' -> '.join(steps)}")
    
    # 8. Валидация криптографических свойств
    print("\n8. Криптографические проверки:")
    
    # Проверка: (N * G) должно дать ∞ (нейтральный элемент)
    infinity_check = scalar_mul(N, G)
    print(f"   N * G = {infinity_check} (должно быть ∞)")
    
    # Проверка коммутативности: aG + bG = (a+b)G
    a, b = 7, 13
    left = point_add(scalar_mul(a, G), scalar_mul(b, G))
    right = scalar_mul((a + b) % N, G)
    print(f"   {a}G + {b}G = (a + b)G: {left == right}")
    
    # 9. Дополнительная проверка: подпись не должна валидироваться с другим ключом
    print("\n9. Проверка с другим ключом:")
    another_private = generate_private_key()
    another_public = private_to_public(another_private)
    is_valid_other = ecdsa_verify(another_public, message_bytes, signature)
    print(f"   Подпись с другим открытым ключом: {is_valid_other}")
    print(f"   (Должно быть False, т.к. ключ не соответствует)")
    
    print("\n" + "=" * 70)
    print("Демонстрация завершена!")


# ============================================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================================

if __name__ == "__main__":
    demo()