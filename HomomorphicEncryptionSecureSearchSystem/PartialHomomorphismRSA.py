# Частичный гомоморфизм в RSA
# -*- coding: utf-8 -*-
"""
Демонстрация частичного (мультипликативного) гомоморфизма RSA.
Основано на тексте: шифрование, перемножение шифротекстов, расшифровка.
Без использования numpy.
"""

def egcd(a, b):
    """Расширенный алгоритм Евклида для нахождения НОД и коэффициентов."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    """
    Нахождение закрытого ключа d, обратного к e по модулю phi.
    Используется расширенный алгоритм Евклида.
    """
    gcd, x, _ = egcd(e, phi)
    if gcd != 1:
        raise ValueError(f"Обратного элемента не существует: НОД({e}, {phi}) != 1")
    return x % phi

def rsa_encrypt(message, e, n):
    """Шифрование сообщения: c = m ^ e mod n."""
    return pow(message, e, n)

def rsa_decrypt(ciphertext, d, n):
    """Расшифрование криптограммы: m = c ^ d mod n."""
    return pow(ciphertext, d, n)

def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ЧАСТИЧНОГО ГОМОМОРФИЗМА RSA")
    print("=" * 60)

    # --- 1. Исходные данные из вашего текста ---
    M1 = 11
    M2 = 8
    e = 7
    p = 13
    q = 17
    N = p * q  # 221

    # Вычисляем функцию Эйлера
    phi = (p - 1) * (q - 1)  # 192

    # Находим закрытый ключ d (обратный элемент к e по модулю phi)
    d = mod_inverse(e, phi)  # Должен получиться 55

    print("Исходные параметры:")
    print(f"  M1 = {M1}, M2 = {M2}")
    print(f"  e = {e}, d = {d}")
    print(f"  p = {p}, q = {q}, N = {N}, phi(N) = {phi}")
    print("-" * 60)

    # --- 2. Шифрование сообщений (получаем c1 и c2) ---
    c1 = rsa_encrypt(M1, e, N)
    c2 = rsa_encrypt(M2, e, N)

    print("УРОВЕНЬ 1: Шифрование отдельных сообщений")
    print(f"  c1 = {M1} ^ {e} mod {N} = {c1}")
    print(f"  c2 = {M2} ^ {e} mod {N} = {c2}")
    print("-" * 60)

    # --- 3. Гомоморфная операция: перемножение шифротекстов ---
    # Первый уровень: c3 = c1 * c2 (mod N)
    c3_from_cipher = (c1 * c2) % N

    # Второй уровень: c3 = (M1 * M2)^e (mod N) — теоретическое вычисление
    M_product = M1 * M2
    c3_from_plain = rsa_encrypt(M_product, e, N)

    print("УРОВЕНЬ 2: Гомоморфное умножение шифротекстов")
    print(f"  c3 (через перемножение c1 и c2) = {c1} * {c2} mod {N} = {c3_from_cipher}")
    print(f"  c3 (через шифрование M1*M2)     = ({M1} * {M2}) ^ {e} mod {N} = {c3_from_plain}")
    print(f"  Результаты совпадают? {c3_from_cipher == c3_from_plain}")
    print("-" * 60)

    # --- 4. Расшифровка c3 и получение произведения сообщений ---
    decrypted_product = rsa_decrypt(c3_from_cipher, d, N)

    print("УРОВЕНЬ 3: Расшифровка результата гомоморфной операции")
    print(f"  Расшифровка c3 = {c3_from_cipher} ^ {d} mod {N} = {decrypted_product}")
    print(f"  Ожидаемый результат M1 * M2 = {M1} * {M2} = {M_product}")
    print(f"  Расшифровка верна? {decrypted_product == M_product}")
    print("-" * 60)

    # --- 5. Дополнительная проверка: независимая расшифровка c1 и c2 ---
    decrypted_m1 = rsa_decrypt(c1, d, N)
    decrypted_m2 = rsa_decrypt(c2, d, N)

    print("ПРОВЕРКА: Расшифровка исходных криптограмм по отдельности")
    print(f"  Расшифровка c1 -> {decrypted_m1} (было {M1})")
    print(f"  Расшифровка c2 -> {decrypted_m2} (было {M2})")
    print(f"  Произведение расшифрованных: {decrypted_m1} * {decrypted_m2} = {decrypted_m1 * decrypted_m2}")
    print("=" * 60)

    # Финальный вывод, соответствующий вашему тексту
    print("\nВЫВОД:")
    print("RSA действительно обладает свойством частичного (мультипликативного) гомоморфизма.")
    print(f"Алиса, расшифровав c3 = {c3_from_cipher} своим закрытым ключом d={d},")
    print(f"получает результат умножения сообщений: {M1} * {M2} = {decrypted_product}.")
    print("Это именно то, что мы ожидали!")

if __name__ == "__main__":
    main()