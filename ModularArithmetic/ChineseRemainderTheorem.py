# 3. Китайская теорема об остатках
def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), такие что a * x + b * y = g = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a, m):
    """
    Находит обратный элемент к a по модулю m.
    Требует, чтобы gcd(a, m) = 1.
    """
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Обратный элемент не существует: gcd({a}, {m}) = {g}")
    return x % m


def chinese_remainder_theorem(b_list, n_list):
    """
    Решает систему сравнений:
        x ≡ b1 (mod n1)
        x ≡ b2 (mod n2)
        ...
        x ≡ bk (mod nk)

    Аргументы:
        b_list: список остатков [b1, b2, ..., bk]
        n_list: список модулей [n1, n2, ..., nk] (попарно взаимно простые)

    Возвращает:
        (x0, N), где x0 — частное решение (0 ≤ x0 < N),
        N = n1 * n2 * ... * nk — общий модуль,
        и все решения имеют вид x = x0 + t * N, t ∈ Z.

    Если модули не являются попарно взаимно простыми, функция
    выбрасывает исключение ValueError.
    """
    k = len(b_list)
    if k != len(n_list):
        raise ValueError("Списки b_list и n_list должны быть одинаковой длины")

    # Проверка попарной взаимной простоты модулей
    for i in range(k):
        for j in range(i + 1, k):
            if extended_gcd(n_list[i], n_list[j])[0] != 1:
                raise ValueError(f"Модули {n_list[i]} и {n_list[j]} не взаимно просты")

    # Вычисляем N = произведение всех модулей
    N = 1
    for n in n_list:
        N *= n

    # Вычисляем частное решение по формуле x = Σ (b_i * N_i * M_i)
    x = 0
    for i in range(k):
        N_i = N // n_list[i]  # произведение всех модулей, кроме n_i
        M_i = mod_inverse(N_i, n_list[i])  # обратный к N_i по модулю n_i
        x += b_list[i] * N_i * M_i

    # Приводим к наименьшему неотрицательному остатку
    x0 = x % N

    return x0, N


def solve_system(b_list, n_list):
    """
    Удобная обёртка: выводит решение системы сравнений.
    """
    try:
        x0, N = chinese_remainder_theorem(b_list, n_list)
        print("Система сравнений:")
        for b, n in zip(b_list, n_list):
            print(f"  x ≡ {b} (mod {n})")
        print(f"\nРешение: x ≡ {x0} (mod {N})")
        print(f"Проверка:")
        for b, n in zip(b_list, n_list):
            print(f"  {x0} mod {n} = {x0 % n} (должно быть {b})")
        return x0, N
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None, None


# Пример из вашего текста (исправленный: n3 = 42)
if __name__ == "__main__":
    print("=" * 50)
    print("Пример 1 (из текста):")
    b_list = [5, 4, 3]
    n_list = [11, 13, 42]
    solve_system(b_list, n_list)

    print("\n" + "=" * 50)
    print("Пример 2 (простой тест):")
    # x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
    b_list2 = [2, 3, 2]
    n_list2 = [3, 5, 7]
    solve_system(b_list2, n_list2)

    print("\n" + "=" * 50)
    print("Пример 3 (система из двух уравнений):")
    b_list3 = [1, 2]
    n_list3 = [4, 9]
    solve_system(b_list3, n_list3)