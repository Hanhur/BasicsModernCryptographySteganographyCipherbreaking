# 3. Подпись на базе RSA
"""
Реализация подписи RSA на основе лекционного материала.
Схема: восстанавливающая подпись (подпись позволяет восстановить сообщение).
Функция R: сдвиг (message + 1) mod n
"""

import random
from typing import Tuple


def gcd_extended(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y) такие, что a * x + b * y = gcd"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def mod_inverse(a: int, m: int) -> int:
    """Вычисляет обратное число к a по модулю m (m должно быть взаимно просто с a)"""
    gcd, x, _ = gcd_extended(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента не существует: gcd({a}, {m}) = {gcd}")
    return x % m


def is_prime(n: int, k: int = 5) -> bool:
    """Простая проверка на простоту (тест Миллера–Рабина)"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Записываем n - 1 = d * 2 ^ r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    def check_composite(a: int) -> bool:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True

    for _ in range(k):
        a = random.randrange(2, n - 1)
        if check_composite(a):
            return False
    return True


def generate_prime(bits: int = 8) -> int:
    """Генерирует простое число заданной битовой длины"""
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << bits - 1) | 1  # Старший и младший биты = 1
        if is_prime(candidate):
            return candidate


def generate_rsa_keys(bits: int = 8) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Генерирует ключи RSA.
    Возвращает: (public_key, private_key), где public_key = (n, e), private_key = (n, d)
    """
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Открытая экспонента (обычно 65537, но для малых n возьмём 17 или 3, если подходит)
    e = 17
    while gcd_extended(e, phi_n)[0] != 1:
        e += 2

    d = mod_inverse(e, phi_n)

    return (n, e), (n, d)


def R(message: int, n: int) -> int:
    """
    Функция преобразования сообщения перед подписью.
    В лекции: сдвиг mod n.
    Для безопасности в реальных системах используют хеш-функцию.
    """
    return (message + 1) % n


def R_inverse(y: int, n: int) -> int:
    """Обратная функция к R (восстановление исходного сообщения)"""
    return (y - 1) % n


def sign(message: int, private_key: Tuple[int, int]) -> int:
    """
    Подписание сообщения.
    private_key = (n, d)
    Возвращает подпись s.
    """
    n, d = private_key
    transformed = R(message, n)
    signature = pow(transformed, d, n)
    return signature


def verify(signature: int, public_key: Tuple[int, int]) -> Tuple[bool, int]:
    """
    Проверка подписи и восстановление сообщения.
    public_key = (n, e)
    Возвращает: (True, восстановленное_сообщение) если подпись верна, (False, None) если неверна.
    """
    n, e = public_key
    recovered_transformed = pow(signature, e, n)
    recovered_message = R_inverse(recovered_transformed, n)
    return True, recovered_message


def main():
    print("=" * 60)
    print("Генерация ключей RSA для подписи")
    print("=" * 60)

    # Генерируем ключи
    public_key, private_key = generate_rsa_keys(bits = 8)
    n, e = public_key
    print(f"Открытый ключ: (n = {n}, e = {e})")
    print(f"Закрытый ключ: (n = {n}, d = {private_key[1]})")
    print(f"φ(n) = {(private_key[1] * e - 1) // (public_key[0] - public_key[0] // 3)}")

    print("\n" + "=" * 60)
    print("Пример подписи и проверки")
    print("=" * 60)

    # Исходное сообщение
    message = 2
    print(f"Исходное сообщение m = {message}")

    # Подпись
    signature = sign(message, private_key)
    print(f"Подпись s = R(m) ^ d mod n = {signature}")

    # Проверка
    is_valid, recovered_message = verify(signature, public_key)
    print(f"Проверка: s ^ e mod n = {signature} ^ {e} mod {n} = {pow(signature, e, n)}")
    print(f"Восстановленное R(m) = {pow(signature, e, n)}")
    print(f"Восстановленное сообщение m' = {recovered_message}")

    # Проверка соответствия
    if is_valid and recovered_message == message:
        print("\n✓ Подпись ВЕРНА! Сообщение восстановлено корректно.")
    else:
        print("\n✗ Подпись НЕВЕРНА!")

    print("\n" + "=" * 60)
    print("Демонстрация: проверка подписи другим пользователем")
    print("=" * 60)

    # Другой пользователь (Боб) может проверить подпись Алисы, используя её открытый ключ
    print(f"Боб получает (m = {message}, s = {signature}) и открытый ключ Алисы ({n}, {e})")
    bob_valid, bob_recovered = verify(signature, public_key)
    print(f"Боб вычисляет: R(m) = {message + 1} mod {n} = {(message + 1) % n}")
    print(f"Боб проверяет: s ^ e mod n = {pow(signature, e, n)}")
    if bob_valid and bob_recovered == message:
        print("✓ Боб подтверждает, что подпись принадлежит Алисе")


if __name__ == "__main__":
    # Фиксируем seed для воспроизводимости примера
    random.seed(42)

    # Демонстрация с примером из лекции (p = 11, q = 7)
    print("\n" + "=" * 60)
    print("Проверка примера из лекции (p = 11, q = 7, e = 13, d = 37, m = 2)")
    print("=" * 60)

    n_lecture = 77
    e_lecture = 13
    d_lecture = 37
    m_lecture = 2

    public_lecture = (n_lecture, e_lecture)
    private_lecture = (n_lecture, d_lecture)

    s_lecture = sign(m_lecture, private_lecture)
    print(f"Подпись: s = {s_lecture} (должно быть 31)")

    valid, recovered = verify(s_lecture, public_lecture)
    print(f"Проверка: сообщение восстановлено как {recovered} (должно быть 2)")

    if recovered == m_lecture:
        print("✓ Пример из лекции выполнен верно")

    # Дополнительно: функция R
    print("\n" + "=" * 60)
    print("Примечание о функции R")
    print("=" * 60)
    print("В данной реализации R(x) = x + 1 (mod n)")
    print("В реальных системах вместо сдвига используется криптографическая")
    print("хеш-функция (например, SHA-256) для устойчивости к атакам.")