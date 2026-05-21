# 1. Кольцо целых чисел
"""
Модуль для демонстрации кольца целых чисел Z и кольца вычетов Zn.
Основано на свойствах:
- Ассоциативность, коммутативность, дистрибутивность.
- Деление с остатком.
- Арифметика по модулю n.
"""

def divide_with_remainder(a: int, b: int) -> tuple:
    """
    Деление с остатком в кольце целых чисел.
    Для пары (a, b), b != 0, находит c и r такие, что:
    a = b * c + r, где 0 <= r < |b|.

    Args:
        a: делимое
        b: делитель (b != 0)

    Returns:
        tuple: (частное, остаток)

    Raises:
        ValueError: если b == 0
    """
    if b == 0:
        raise ValueError("Деление на ноль невозможно")

    # Знак остатка всегда неотрицателен
    # В Python оператор % уже даёт остаток от 0 до |b|-1, но переопределим явно
    r = a % abs(b)
    c = (a - r) // b  # Частное, которое может быть отрицательным
    return c, r


class Zn:
    """
    Кольцо вычетов по модулю n (Z_n).
    Элементы: 0, 1, 2, ..., n-1.
    Операции выполняются по модулю n.
    """

    def __init__(self, n: int, value: int):
        """
        Args:
            n: модуль (n >= 2)
            value: целое число, которое будет приведено к вычету по модулю n
        """
        if n < 2:
            raise ValueError("Модуль n должен быть >= 2")
        self.n = n
        self.value = value % n  # Приводим к остатку [0, n-1]

    def __add__(self, other):
        """Сложение в Zn: (a + b) mod n"""
        if self.n != other.n:
            raise TypeError("Нельзя складывать элементы разных колец Zn")
        return Zn(self.n, self.value + other.value)

    def __sub__(self, other):
        """Вычитание в Zn: (a - b) mod n"""
        if self.n != other.n:
            raise TypeError("Нельзя вычитать элементы разных колец Zn")
        return Zn(self.n, self.value - other.value)

    def __mul__(self, other):
        """Умножение в Zn: (a * b) mod n"""
        if self.n != other.n:
            raise TypeError("Нельзя умножать элементы разных колец Zn")
        return Zn(self.n, self.value * other.value)

    def __eq__(self, other):
        """Сравнение элементов Zn"""
        return self.n == other.n and self.value == other.value

    def __repr__(self):
        return f"Zn({self.n}, {self.value})"

    def __str__(self):
        return f"{self.value} (mod {self.n})"


# Демонстрация работы кода
if __name__ == "__main__":
    print("=== 1. Кольцо целых чисел Z ===")
    a, b = 12, 5
    c, r = divide_with_remainder(a, b)
    print(f"Деление с остатком: {a} = {b} * {c} + {r} (0 <= {r} < {abs(b)})")

    a, b = -14, 9
    c, r = divide_with_remainder(a, b)
    print(f"Деление с остатком: {a} = {b} * {c} + {r} (0 <= {r} < {abs(b)})")

    a, b = 15, 8
    c, r = divide_with_remainder(a, b)
    print(f"Деление с остатком: {a} = {b} * {c} + {r} (0 <= {r} < {abs(b)})")

    print("\n=== 2. Кольцо вычетов Zn (арифметика остатков) ===")
    n = 7
    print(f"Модуль n = {n}")

    x = Zn(n, 5)
    y = Zn(n, 3)

    print(f"x = {x}")
    print(f"y = {y}")
    print(f"x + y = {x + y}  # (5 + 3) mod 7")
    print(f"x - y = {x - y}  # (5 - 3) mod 7")
    print(f"x * y = {x * y}  # (5 * 3) mod 7")

    print("\n=== 3. Проверка свойств кольца на Zn ===")
    n2 = 6
    a1 = Zn(n2, 2)
    a2 = Zn(n2, 4)
    a3 = Zn(n2, 5)
    zero = Zn(n2, 0)
    one = Zn(n2, 1)

    print(f"Z_{n2}: a = {a1}, b = {a2}, c = {a3}, 0 = {zero}, 1 = {one}")

    # Ассоциативность сложения
    assert (a1 + a2) + a3 == a1 + (a2 + a3)
    print("✓ (a + b) + c == a + (b + c)")

    # Существование нуля
    assert a1 + zero == a1 == zero + a1
    print("✓ a + 0 == a == 0 + a")

    # Существование противоположного
    opp = Zn(n2, -a1.value)
    assert a1 + opp == zero
    print(f"✓ Противоположный для {a1}: {opp}")

    # Коммутативность сложения
    assert a1 + a2 == a2 + a1
    print("✓ a + b == b + a")

    # Дистрибутивность
    assert a1 * (a2 + a3) == a1 * a2 + a1 * a3
    assert (a1 + a2) * a3 == a1 * a3 + a2 * a3
    print("✓ a * (b + c) == a * b + a * c и (a + b) * c == a * c + b * c")

    # Ассоциативность умножения
    assert (a1 * a2) * a3 == a1 * (a2 * a3)
    print("✓ (a * b) * c == a * (b * c)")

    # Существование единицы
    assert a1 * one == a1 == one * a1
    print("✓ a * 1 == a == 1 * a")

    # Коммутативность умножения
    assert a1 * a2 == a2 * a1
    print("✓ a * b == b * a")

    print("\n=== 4. Пример из криптографии: степени по модулю ===")
    # В Zn возведение в степень — основа RSA
    base = Zn(13, 7)
    exp = 4
    result = base
    for _ in range(exp - 1):
        result = result * base
    print(f"7^{exp} mod 13 = {result}")

    # Встроенный способ (для проверки)
    print(f"Проверка: pow(7, 4, 13) = {pow(7, 4, 13)}")