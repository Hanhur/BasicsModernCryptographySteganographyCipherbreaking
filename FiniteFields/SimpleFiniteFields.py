# # 1. Простые конечные поля
# import math
# from typing import Tuple, Optional

# def is_prime(n: int) -> bool:
#     """Проверка, является ли число n простым."""
#     if n < 2:
#         return False
#     if n == 2:
#         return True
#     if n % 2 == 0:
#         return False
#     for i in range(3, int(math.sqrt(n)) + 1, 2):
#         if n % i == 0:
#             return False
#     return True

# def is_field_Zn(n: int) -> bool:
#     """
#     Лемма 23: Кольцо вычетов Zn является полем тогда и только тогда,
#     когда n = p - простое число.
#     """
#     return is_prime(n)

# def characteristic_from_order(order: int) -> Optional[int]:
#     """
#     По порядку конечного поля (pr) возвращает характеристику p.
#     Если порядок не является степенью простого числа, возвращает None,
#     так как такого поля не существует (из текста: |F| = p^r).
#     """
#     if order <= 1:
#         return None
#     # Находим простой делитель порядка
#     for p in range(2, order + 1):
#         if is_prime(p) and order % p == 0:
#             # Проверяем, что order = p^r
#             temp = order
#             while temp % p == 0:
#                 temp //= p
#             if temp == 1:
#                 return p
#             else:
#                 return None
#     return None

# def is_prime_field(order: int) -> bool:
#     """
#     Проверка, является ли поле порядка order простым.
#     Простое поле не содержит собственных подполей <=> его порядок - простое число.
#     """
#     return is_prime(order)

# class PrimeField:
#     """Класс для работы в простом поле Z_p."""

#     def __init__(self, p: int):
#         if not is_prime(p):
#             raise ValueError(f"p = {p} не является простым числом, Z_p не поле.")
#         self.p = p
#         self.characteristic = p

#     def add(self, a: int, b: int) -> int:
#         """Сложение в Z_p."""
#         return (a + b) % self.p

#     def sub(self, a: int, b: int) -> int:
#         """Вычитание в Z_p."""
#         return (a - b) % self.p

#     def mul(self, a: int, b: int) -> int:
#         """Умножение в Z_p."""
#         return (a * b) % self.p

#     def power(self, a: int, exp: int) -> int:
#         """Возведение в степень в Z_p."""
#         return pow(a, exp, self.p)

#     def inverse(self, a: int) -> int:
#         """
#         Обратный элемент в Z_p.
#         Из текста: в Z_p обратимы все ненулевые элементы.
#         """
#         a = a % self.p
#         if a == 0:
#             raise ZeroDivisionError("Ноль не имеет обратного элемента в поле.")
#         # Расширенный алгоритм Евклида
#         # По малой теореме Ферма: a^(p-2) mod p — обратный, но для общности используем gcd
#         return pow(a, -1, self.p)  # в Python 3.8+ работает для взаимно простых

#     def divide(self, a: int, b: int) -> int:
#         """Деление a / b в Z_p (b != 0)."""
#         return self.mul(a, self.inverse(b))

#     def __repr__(self):
#         return f"PrimeField(Z_{self.p})"


# # Пример использования
# if __name__ == "__main__":
#     # Проверка Zn на поле
#     for n in range(2, 20):
#         if is_field_Zn(n):
#             print(f"Z_{n} - поле (простое поле порядка {n})")
#         else:
#             print(f"Z_{n} - не поле")

#     print("\n--- Характеристики полей ---")
#     for order in [2, 3, 4, 5, 7, 8, 9, 10, 11, 16, 32, 12]:
#         ch = characteristic_from_order(order)
#         if ch is not None:
#             print(f"Порядок {order}: характеристика {ch}, простое поле: {is_prime_field(order)}")
#         else:
#             print(f"Порядок {order}: не является степенью простого -> поля не существует")

#     print("\n--- Работа в простом поле Z_7 ---")
#     F7 = PrimeField(7)
#     print(f"Поле: {F7}")
#     print(f"3 + 5 = {F7.add(3, 5)}")
#     print(f"3 * 5 = {F7.mul(3, 5)}")
#     print(f"Обратный к 3: {F7.inverse(3)}")
#     print(f"Проверка: 3 * (3 ^ {-1}) = {F7.mul(3, F7.inverse(3))}")
#     print(f"4 / 2 = {F7.divide(4, 2)}")

# ===================================================================================================================================================

import math

# ============================================================
# 1. Проверка, является ли Zn полем (т.е. n — простое число)
# ============================================================

def is_prime(n: int) -> bool:
    """Базовая проверка на простоту."""
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

def is_field_Zn(n: int) -> bool:
    """
    Лемма 23: Zn является полем <=> n — простое число.
    """
    return is_prime(n)


# ============================================================
# 2. Характеристика конечного поля по его порядку p^r
# ============================================================

def characteristic_of_finite_field(order: int):
    """
    По порядку поля (должен быть p^r) возвращает характеристику p.
    Если порядок не является степенью простого числа — возвращает None.
    """
    if order < 2:
        return None

    # Ищем первый простой делитель
    for p in range(2, order + 1):
        if is_prime(p) and order % p == 0:
            # Проверяем, что order = p^r
            temp = order
            while temp % p == 0:
                temp //= p
            if temp == 1:
                return p
            else:
                return None
    return None


# ============================================================
# 3. Работа в простом поле Z_p
# ============================================================

class PrimeField:
    """Простое поле Z_p (p — простое)."""

    def __init__(self, p: int):
        if not is_prime(p):
            raise ValueError(f"{p} не является простым, Z_p не будет полем.")
        self.p = p
        self.characteristic = p

    def add(self, a: int, b: int) -> int:
        """Сложение в Z_p."""
        return (a + b) % self.p

    def sub(self, a: int, b: int) -> int:
        """Вычитание в Z_p."""
        return (a - b) % self.p

    def mul(self, a: int, b: int) -> int:
        """Умножение в Z_p."""
        return (a * b) % self.p

    def inverse(self, a: int) -> int:
        """
        Обратный элемент к a в Z_p.
        Из текста: в Z_p обратимы все ненулевые элементы.
        """
        a = a % self.p
        if a == 0:
            raise ZeroDivisionError("Ноль не имеет обратного элемента.")
        # Через расширенный алгоритм Евклида (Python 3.8+)
        return pow(a, -1, self.p)

    def divide(self, a: int, b: int) -> int:
        """Деление a / b в Z_p (b != 0)."""
        return self.mul(a, self.inverse(b))

    def __repr__(self):
        return f"PrimeField(Z_{self.p})"


# ============================================================
# 4. Проверка, является ли поле простым (не имеет собственных подполей)
# ============================================================

def is_prime_field(order: int) -> bool:
    """
    Поле является простым <=> его порядок — простое число.
    (Из текста: простые поля не содержат собственных подполей,
     и это верно только для Z_p, p — простое.)
    """
    return is_prime(order)


# ============================================================
# Демонстрация
# ============================================================

if __name__ == "__main__":
    print("=== 1. Проверка Zn на поле ===")
    for n in range(2, 21):
        if is_field_Zn(n):
            print(f"Z_{n} — поле (простое поле порядка {n})")
        else:
            print(f"Z_{n} — не поле")

    print("\n=== 2. Характеристика по порядку поля ===")
    test_orders = [2, 3, 4, 5, 7, 8, 9, 10, 11, 16, 32, 12, 1, 27]
    for order in test_orders:
        ch = characteristic_of_finite_field(order)
        if ch is not None:
            print(f"Порядок {order}: характеристика = {ch}")
        else:
            print(f"Порядок {order}: не является степенью простого → поля не существует")

    print("\n=== 3. Работа в простом поле Z_13 ===")
    F = PrimeField(13)
    print(F)
    print(f"5 + 8 = {F.add(5, 8)}")
    print(f"5 * 8 = {F.mul(5, 8)}")
    print(f"Обратный к 4: {F.inverse(4)}")
    print(f"Проверка: 4 * 4^(-1) = {F.mul(4, F.inverse(4))}")
    print(f"7 / 2 = {F.divide(7, 2)}")

    print("\n=== 4. Проверка, является ли поле простым ===")
    for order in [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17]:
        print(f"Порядок {order}: простое поле? {is_prime_field(order)}")