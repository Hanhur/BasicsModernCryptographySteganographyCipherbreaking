# 4. Правильный выбор параметров
import random
import math
from functools import reduce

# ---------- Вспомогательные функции ----------
def is_prime(n, k = 10):
    """Простая проверка на простоту (Миллер-Рабин)"""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits = 512):
    """Генерация простого числа заданной битовой длины"""
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1  # Старший и младший биты = 1
        if is_prime(p):
            return p

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def egcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y)"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратное число по модулю m"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("Обратного элемента не существует")
    return x % m

def crt(rems, mods):
    """
    Китайская теорема об остатках.
    rems: список остатков [r1, r2, ..., rk]
    mods: список модулей [m1, m2, ..., mk] (попарно взаимно простые)
    Возвращает x такое, что x ≡ ri (mod mi) для всех i
    """
    total = 0
    prod = reduce(lambda x, y: x * y, mods)
    for r, m in zip(rems, mods):
        p = prod // m
        total += r * modinv(p, m) * p
    return total % prod

def integer_nth_root(n, k):
    """
    Целочисленный корень k-й степени из n.
    Возвращает (root, is_exact)
    """
    if n < 0:
        if k % 2 == 0:
            return None, False
        return -integer_nth_root(-n, k)[0], True
    if n == 0:
        return 0, True
    low, high = 1, 1
    while high ** k <= n:
        high *= 2
    while low <= high:
        mid = (low + high) // 2
        mid_k = mid ** k
        if mid_k == n:
            return mid, True
        elif mid_k < n:
            low = mid + 1
        else:
            high = mid - 1
    return high, False


# ---------- Основная программа ----------
def main():
    print("=" * 60)
    print("Демонстрация атаки Хастада (Håstad's broadcast attack)")
    print("=" * 60)

    # Параметры
    BITS = 256          # Длина простых чисел p, q (чтобы не ждать долго)
    E = 3               # Открытый ключ (общий для всех)
    K = 3               # Количество пользователей (должно быть >= E)

    print(f"\nПараметры:")
    print(f"  - Открытый ключ e = {E}")
    print(f"  - Количество пользователей = {K}")
    print(f"  - Длина простых чисел = {BITS} бит")

    # Генерация ключей для K пользователей
    users = []  # каждый элемент: (n, e, d)
    print("\nГенерация ключей RSA для пользователей...")

    for i in range(K):
        while True:
            p = generate_prime(BITS)
            q = generate_prime(BITS)
            n = p * q
            phi = (p - 1) * (q - 1)

            # Убедимся, что e и phi взаимно просты
            if gcd(E, phi) != 1:
                continue

            d = modinv(E, phi)
            users.append((n, E, d))
            print(f"  Пользователь {i + 1}: n = {n} (размер {n.bit_length()} бит)")
            break

    # Проверка взаимной простоты модулей
    print("\nПроверка попарной взаимной простоты модулей...")
    for i in range(K):
        for j in range(i + 1, K):
            g = gcd(users[i][0], users[j][0])
            if g != 1:
                print(f"  ВНИМАНИЕ: gcd(n{i + 1}, n{j + 1}) = {g} (не взаимно просты!)")
            else:
                print(f"  gcd(n{i + 1}, n{j + 1}) = 1 ✓")

    # Исходное сообщение
    # Выбираем сообщение меньше самого маленького модуля
    min_n = min(n for n, _, _ in users)
    message = random.randint(2, min(10000, min_n - 1))
    print(f"\nИсходное сообщение m = {message}")

    # Шифрование: каждому пользователю отправляется одно и то же сообщение
    ciphertexts = []
    print("\nШифрование (каждый пользователь получает одно и то же m):")
    for i, (n, e, _) in enumerate(users):
        c = pow(message, e, n)
        ciphertexts.append(c)
        print(f"  Пользователь {i + 1}: c_{i + 1} = {c}")

    # ---------- АТАКА ----------
    print("\n" + "=" * 60)
    print("Злоумышленник перехватил шифротексты и пытается восстановить m")
    print("=" * 60)

    # Шаг 1: решаем систему сравнений
    # x ≡ c1 (mod n1)
    # x ≡ c2 (mod n2)
    # ...
    mods = [n for n, _, _ in users]
    rems = ciphertexts

    print("\nШаг 1: Применение Китайской теоремы об остатках")
    print(f"  Модули: {mods}")
    print(f"  Остатки: {rems}")

    x = crt(rems, mods)
    print(f"  Найдено X = {x}")
    print(f"  Размер X: {x.bit_length()} бит")

    # Шаг 2: извлекаем корень e-й степени
    print(f"\nШаг 2: Извлечение корня степени e = {E} из X")
    m_recovered, exact = integer_nth_root(x, E)

    if exact:
        print(f"  Корень извлечён точно!")
        print(f"  Восстановленное сообщение: {m_recovered}")
    else:
        print(f"  Корень не является целым числом (возможно, m^e >= произведение модулей)")
        print(f"  Ближайшее целое: {m_recovered}")

    # Проверка
    print("\n" + "-" * 60)
    if exact and m_recovered == message:
        print("✅ АТАКА УСПЕШНА! Сообщение полностью восстановлено.")
    else:
        print("❌ Атака не удалась (возможно, не выполняется условие m ^ e < n1 * n2 * ... * nk)")

    print("=" * 60)

    # Дополнительное объяснение условия успеха
    print("\nУсловие успеха атаки:")
    prod_n = reduce(lambda x, y: x * y, mods)
    me = message ** E
    print(f"  m ^ e = {me}")
    print(f"  Произведение модулей N = {prod_n}")
    if me < prod_n:
        print("  ✓ m ^ e < N → X = m ^ e как целое число → корень извлекается точно")
    else:
        print("  ✗ m ^ e >= N → китайская теорема даёт m ^ e mod N, а не само m ^ e → атака не работает")


if __name__ == "__main__":
    main()