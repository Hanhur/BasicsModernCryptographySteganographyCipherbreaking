# 1 . Определение дискретного логарифма
import random
import math
from typing import Optional

def is_prime(n: int) -> bool:
    """Проверка числа на простоту (для небольших чисел)."""
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

def factorize(n: int) -> list[int]:
    """Разложение числа на простые множители (для небольших чисел)."""
    factors = []
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors

def is_primitive_element(g: int, p: int, factors: list[int]) -> bool:
    """
    Проверка, является ли g примитивным элементом поля F_p.
    Условие: для каждого простого делителя q из p - 1, g ^ ((p - 1) / q) != 1 (mod p).
    """
    if g % p == 0:
        return False
    for q in set(factors):  # set для уникальности простых делителей
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True

def find_primitive_element(p: int) -> Optional[int]:
    """Поиск примитивного элемента в поле F_p (p — простое)."""
    if not is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    
    factors = factorize(p - 1)
    # Случайный поиск — эффективен для больших p, для малых можно простым перебором
    for g in range(2, p):
        if is_primitive_element(g, p, factors):
            return g
    return None  # Не должно произойти для простых p

def discrete_log_bruteforce(g: int, h: int, p: int) -> Optional[int]:
    """
    Вычисление дискретного логарифма x: g ^ x ≡ h (mod p).
    Полный перебор — только для маленьких p (учебный пример).
    Возвращает x ∈ [0, p - 2] или None, если не найден.
    """
    # Проверка примитивности g (для корректности)
    # В реальных задачах этого не делают из-за сложности, здесь — для гарантии
    if not is_primitive_element(g, p, factorize(p - 1)):
        # Если g не примитивный, логарифм может не существовать для некоторых h
        # Для простоты просто предупредим
        print(f"Предупреждение: {g} не является примитивным элементом F_{p}")
    
    current = 1
    for x in range(0, p - 1):
        if current == h % p:
            return x
        current = (current * g) % p
    return None

def modular_pow(g: int, x: int, p: int) -> int:
    """Быстрое возведение в степень по модулю: g ^ x mod p."""
    return pow(g, x, p)

def main():
    # Пример: небольшое поле F_p
    p = 23  # Простое число, мультипликативная группа порядка 22
    print(f"Работаем с полем F_{p} (целые числа по модулю {p})")
    
    # 1. Находим примитивный элемент
    g = find_primitive_element(p)
    if g is None:
        print("Не удалось найти примитивный элемент.")
        return
    
    print(f"Примитивный элемент (порождающий) g = {g}")
    print(f"Порядок мультипликативной группы: {p - 1}")
    
    # 2. Демонстрация: выбираем случайный секретный показатель x
    secret_x = random.randint(1, p - 2)
    print(f"\nСлучайно выбранный x (секретный показатель): {secret_x}")
    
    # 3. Вычисляем f = g^x mod p (прямая задача — легко)
    f = modular_pow(g, secret_x, p)
    print(f"Вычисляем f = g ^ x mod p = {g} ^ {secret_x} mod {p} = {f}")
    
    # 4. Пробуем найти x по f (обратная задача — дискретный логарифм)
    print("\nПытаемся найти дискретный логарифм x = log_g(f) полным перебором...")
    found_x = discrete_log_bruteforce(g, f, p)
    
    if found_x is not None:
        print(f"Дискретный логарифм найден: x = {found_x}")
        if found_x == secret_x:
            print("Совпадает с исходным секретным показателем ✓")
        else:
            print("Не совпадает — ошибка! (такого не должно быть для примитивного g)")
    else:
        print("Не удалось найти дискретный логарифм.")
    
    # 5. Демонстрация для всех элементов группы (проверка биекции)
    print("\n--- Проверка: отображение x -> g ^ x для всех x от 0 до p-2 ---")
    for x_test in range(p - 1):
        val = pow(g, x_test, p)
        print(f"x = {x_test:2d} -> g ^ x mod p = {val:2d}", end = "   ")
        if (x_test + 1) % 5 == 0:
            print()
    print("\n(Все значения различны и покрывают все ненулевые элементы поля)")
    
    # 6. Трудность задачи: увеличение размера поля
    print("\n--- Замечание о вычислительной сложности ---")
    print(f"Для p = {p} перебор занял {p - 2} шагов в худшем случае.")
    print("Для криптографических размеров (например, p ~ 2 ^ 256) перебор невозможен.")
    print("Поэтому функция f(x) = g ^ x считается односторонней (one-way function).")

if __name__ == "__main__":
    main()