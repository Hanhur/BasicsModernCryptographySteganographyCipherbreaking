# 2. Теоремы Ферма, Эйлера, Лагранжа
"""
Программа, иллюстрирующая теоремы Ферма, Эйлера и Лагранжа.
Основано на теоретическом материале о связи этих теорем с теорией групп.
"""

import math
from typing import List, Tuple


def euler_phi(n: int) -> int:
    """Вычисление функции Эйлера φ(n)."""
    if n <= 0:
        raise ValueError("n должно быть положительным")
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result


def small_fermat_test(a: int, p: int) -> bool:
    """
    Проверка малой теоремы Ферма:
    Если p простое и gcd(a, p) = 1, то a^(p-1) ≡ 1 (mod p).
    """
    if not _is_prime(p):
        raise ValueError(f"{p} не является простым числом")
    if math.gcd(a, p) != 1:
        raise ValueError(f"a и p не взаимно просты: gcd({a}, {p}) = {math.gcd(a, p)}")
    
    # Вычисляем a^(p-1) mod p
    result = pow(a, p - 1, p)
    return result == 1


def euler_theorem_test(a: int, n: int) -> bool:
    """
    Проверка теоремы Эйлера:
    Если gcd(a, n) = 1, то a^φ(n) ≡ 1 (mod n).
    """
    if n < 2:
        raise ValueError("n должно быть ≥ 2")
    if math.gcd(a, n) != 1:
        raise ValueError(f"a и n не взаимно просты: gcd({a}, {n}) = {math.gcd(a, n)}")
    
    phi_n = euler_phi(n)
    result = pow(a, phi_n, n)
    return result == 1


def _is_prime(n: int) -> bool:
    """Вспомогательная функция для проверки простоты числа."""
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


def lagrange_theorem_verify(group_order: int, subgroup_order: int) -> Tuple[bool, int]:
    """
    Проверка теоремы Лагранжа:
    Порядок группы делится на порядок подгруппы.
    
    Возвращает:
        (делится_ли, частное_от_деления)
    """
    if group_order % subgroup_order == 0:
        return True, group_order // subgroup_order
    return False, 0


def element_order_in_cyclic_group(group_order: int, element_power: int) -> int:
    """
    В циклической группе порядка n порядок элемента g^k равен n / gcd(n, k).
    """
    return group_order // math.gcd(group_order, element_power)


def demonstrate_fermat():
    """Демонстрация малой теоремы Ферма."""
    print("\n" + "=" * 50)
    print("МАЛАЯ ТЕОРЕМА ФЕРМА")
    print("=" * 50)
    
    p = 7  # простое число
    a = 3  # взаимно простое с p
    
    print(f"p = {p} (простое), a = {a}, gcd({a}, {p}) = {math.gcd(a, p)}")
    result = small_fermat_test(a, p)
    print(f"a ^ (p - 1) = {a} ^ {p - 1} = {pow(a, p - 1)}")
    print(f"a ^ (p - 1) mod p = {pow(a, p - 1, p)}")
    print(f"Теорема выполняется: {result}")
    
    # Группа Z_p^* имеет порядок p-1
    print(f"\nГруппа Z_{p}^* имеет порядок |G| = {p - 1}")
    print("По теореме Лагранжа любой элемент g ∈ G удовлетворяет g^{|G|} = 1")
    print(f"Проверка: {a}^{p - 1} mod {p} = 1")


def demonstrate_euler():
    """Демонстрация теоремы Эйлера."""
    print("\n" + "=" * 50)
    print("ТЕОРЕМА ЭЙЛЕРА")
    print("=" * 50)
    
    n = 10
    a = 3
    
    print(f"n = {n}, a = {a}, gcd({a}, {n}) = {math.gcd(a, n)}")
    phi_n = euler_phi(n)
    print(f"φ({n}) = {phi_n}")
    result = euler_theorem_test(a, n)
    print(f"a^φ(n) = {a} ^ {phi_n} = {pow(a, phi_n)}")
    print(f"a^φ(n) mod n = {pow(a, phi_n, n)}")
    print(f"Теорема выполняется: {result}")
    
    print(f"\nГруппа Z_{n}^* имеет порядок |G| = φ({n}) = {phi_n}")
    print("По теореме Лагранжа любой обратимый элемент удовлетворяет g^{|G|} = 1")


def demonstrate_lagrange():
    """Демонстрация теоремы Лагранжа."""
    print("\n" + "=" * 50)
    print("ТЕОРЕМА ЛАГРАНЖА")
    print("=" * 50)
    
    # Пример: циклическая группа Z_12 (сложение по модулю 12)
    group_order = 12
    subgroup_order = 4  # подгруппа {0, 3, 6, 9}
    
    divides, index = lagrange_theorem_verify(group_order, subgroup_order)
    print(f"Группа G порядка |G| = {group_order}")
    print(f"Подгруппа H порядка |H| = {subgroup_order}")
    print(f"|G| делится на |H|: {divides}")
    if divides:
        print(f"Индекс [G:H] = {index}")
    
    # Порядок элемента в группе
    print("\n" + "-" * 30)
    print("Порядок элемента в группе:")
    group_order = 12
    element_power = 2  # элемент g^2 в циклической группе порядка 12
    
    element_order = element_order_in_cyclic_group(group_order, element_power)
    print(f"В циклической группе порядка {group_order} элемент g^{element_power} имеет порядок = {element_order}")
    print(f"Проверка теоремы Лагранжа: {element_order} делит {group_order} — {group_order % element_order == 0}")


def demonstrate_propositions():
    """Демонстрация предложений 20-22 из текста."""
    print("\n" + "=" * 50)
    print("ПРЕДЛОЖЕНИЯ О ПОРЯДКАХ ЭЛЕМЕНТОВ")
    print("=" * 50)
    
    # Предложение 21: произведение элементов взаимно простых порядков
    print("\nПредложение 21 (абелева группа):")
    order_a = 3
    order_b = 4
    print(f"|a| = {order_a}, |b| = {order_b}, gcd({order_a}, {order_b}) = 1")
    print(f"Тогда |ab| = {order_a} * {order_b} = {order_a * order_b}")
    
    # Предложение 22: максимальный порядок в конечной абелевой группе
    print("\nПредложение 22 (конечная абелева группа):")
    print("Если элемент a имеет максимальный порядок m, то любой другой элемент b")
    print("имеет порядок, делящий m, следовательно b^m = 1")
    
    # Пример: группа Z_15^* (абелева, но не циклическая)
    n = 15
    print(f"\nПример: группа Z_{n}^* порядка φ({n}) = {euler_phi(n)}")
    print("Элементы и их порядки:")
    
    for a in range(1, n):
        if math.gcd(a, n) == 1:
            # Находим порядок элемента в группе
            order = 1
            phi_n = euler_phi(n)
            while order <= phi_n:
                if pow(a, order, n) == 1:
                    break
                order += 1
            print(f"  Элемент {a}: порядок = {order}")
    
    print("\nМаксимальный порядок = 4 (элементы 2, 7, 8, 13)")
    print("Все порядки (2, 4) делят максимальный порядок 4")


def main():
    """Главная функция программы."""
    print("ПРОГРАММА, ИЛЛЮСТРИРУЮЩАЯ ТЕОРЕМЫ ФЕРМА, ЭЙЛЕРА И ЛАГРАНЖА")
    print("На основе теоретического материала о связи этих теорем с теорией групп")
    
    demonstrate_fermat()
    demonstrate_euler()
    demonstrate_lagrange()
    demonstrate_propositions()
    
    print("\n" + "=" * 50)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 50)
    print("""Как видно из примеров:
    1. Малая теорема Ферма: a^(p-1) ≡ 1 (mod p) для простого p.
    2. Теорема Эйлера: a^φ(n) ≡ 1 (mod n) для взаимно простых a и n.
    3. Обе теоремы являются частными случаями теоремы Лагранжа:
       - Z_p^* — группа порядка p-1
       - Z_n^* — группа порядка φ(n)
       По теореме Лагранжа для любого элемента группы g^{|G|} = 1.
    """)


if __name__ == "__main__":
    main()