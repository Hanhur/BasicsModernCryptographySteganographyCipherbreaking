# 3. Сложные задачи, обеспечивающие криптостойкость RSA
import random
import math
from sympy import nextprime, gcd

def generate_rsa_keys(bit_length = 512):
    """Генерация ключей RSA (учебный пример)"""
    # Генерируем два простых числа
    p = nextprime(random.getrandbits(bit_length))
    q = nextprime(random.getrandbits(bit_length))
    while p == q:
        q = nextprime(random.getrandbits(bit_length))
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Открытая экспонента (обычно 65537)
    e = 65537
    # Проверяем, что e взаимно просто с phi
    while math.gcd(e, phi) != 1:
        e = nextprime(e)
    
    # Секретная экспонента
    d = pow(e, -1, phi)  # Python 3.8+ поддерживает обратный элемент по модулю
    
    return {
        'p': p, 'q': q, 'n': n, 'phi': phi,
        'e': e, 'd': d
    }

def factorize_via_phi(n, phi):
    """
    Факторизация n = p * q через знание phi = (p - 1)(q - 1)
    (из текста: знание phi равносильно факторизации)
    """
    # p+q = n - phi + 1
    sum_pq = n - phi + 1
    # Решаем квадратное уравнение x^2 - (p+q)x + pq = 0
    D = sum_pq * sum_pq - 4 * n
    sqrt_D = int(math.isqrt(D))
    if sqrt_D * sqrt_D != D:
        return None
    p = (sum_pq - sqrt_D) // 2
    q = (sum_pq + sqrt_D) // 2
    return (p, q)

def find_all_square_roots_of_one(n, p, q):
    """
    Находит все 4 корня уравнения y ^ 2 ≡ 1 (mod n)
    когда известно разложение n = p * q
    """
    # Решения по модулю p: y ≡ ±1 mod p
    # Решения по модулю q: y ≡ ±1 mod q
    
    # Китайская теорема об остатках для 4 комбинаций
    roots = []
    for rp in (1, -1):
        for rq in (1, -1):
            # Решаем систему:
            # y ≡ rp (mod p)
            # y ≡ rq (mod q)
            
            # Используем формулу КТО:
            # y = rp * q * inv_q_mod_p + rq * p * inv_p_mod_q (mod n)
            
            inv_q_mod_p = pow(q, -1, p)   # q^{-1} mod p
            inv_p_mod_q = pow(p, -1, q)   # p^{-1} mod q
            
            y = (rp * q * inv_q_mod_p + rq * p * inv_p_mod_q) % n
            roots.append(y)
    
    return roots

def factorize_via_nontrivial_root(y, n):
    """
    Факторизация n через нетривиальный корень y из 1 (y ≠ ±1 mod n)
    (из текста: (y - 1)(y + 1) = kn, и gcd(y ± 1, n) даёт множители)
    """
    if y % n == 1 or y % n == n-1:
        return None  # тривиальный корень
    
    factor1 = math.gcd(y - 1, n)
    factor2 = math.gcd(y + 1, n)
    
    if 1 < factor1 < n:
        return (factor1, n // factor1)
    if 1 < factor2 < n:
        return (factor2, n // factor2)
    return None

def demonstrate_rsa_encrypt_decrypt(message_int, n, e, d):
    """Демонстрация шифрования и расшифрования RSA"""
    ciphertext = pow(message_int, e, n)
    decrypted = pow(ciphertext, d, n)
    return ciphertext, decrypted

def main():
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ КРИПТОСТОЙКОСТИ RSA И ЭКВИВАЛЕНТНЫХ ЗАДАЧ")
    print("=" * 70)
    
    # 1. Генерация ключей
    keys = generate_rsa_keys(bit_length = 20)  # маленькие числа для наглядности
    p, q, n, phi, e, d = keys.values()
    
    print(f"\n1. ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA:")
    print(f"   p = {p}")
    print(f"   q = {q}")
    print(f"   n = p * q = {n}")
    print(f"   φ(n) = {phi}")
    print(f"   Открытый ключ: (e, n) = ({e}, {n})")
    print(f"   Секретный ключ: d = {d}")
    print(f"   Проверка: e * d ≡ {e * d} ≡ 1 mod φ(n)? {(e * d) % phi == 1}")
    
    # 2. Демонстрация эквивалентности φ(n) и факторизации
    print(f"\n2. ЭКВИВАЛЕНТНОСТЬ φ(n) И ФАКТОРИЗАЦИИ:")
    print(f"   Из текста: знание φ(n) позволяет найти p и q")
    p_recovered, q_recovered = factorize_via_phi(n, phi)
    print(f"   p + q = n - φ(n) + 1 = {n - phi + 1}")
    print(f"   Восстановленные множители: p = {p_recovered}, q = {q_recovered}")
    print(f"   Совпадают с исходными? {p_recovered == p and q_recovered == q}")
    
    # 3. Все корни второй степени из 1
    print(f"\n3. КОРНИ ВТОРОЙ СТЕПЕНИ ИЗ 1 ПО МОДУЛЮ n:")
    roots = find_all_square_roots_of_one(n, p, q)
    print(f"   Найдено корней: {len(roots)} (должно быть 4)")
    for i, root in enumerate(roots, 1):
        print(f"   y_{i} = {root} (проверка: {root}^2 mod n = {pow(root, 2, n)})")
    
    # 4. Нетривиальный корень → факторизация
    print(f"\n4. ИСПОЛЬЗОВАНИЕ НЕТРИВИАЛЬНОГО КОРНЯ ДЛЯ ФАКТОРИЗАЦИИ:")
    # Находим нетривиальный корень (не ±1)
    nontrivial_root = None
    for root in roots:
        if root % n not in (1, n - 1):
            nontrivial_root = root
            break
    
    if nontrivial_root:
        print(f"   Нетривиальный корень: y = {nontrivial_root}")
        print(f"   y ^ 2 mod n = {pow(nontrivial_root, 2, n)}")
        print(f"   Вычисляем gcd(y-1, n) и gcd(y+1, n):")
        factor1, factor2 = factorize_via_nontrivial_root(nontrivial_root, n)
        print(f"   Полученные множители: {factor1}, {factor2}")
        print(f"   Совпадают с исходными {p}, {q}? {set([factor1, factor2]) == set([p, q])}")
    else:
        print("   Не удалось найти нетривиальный корень (все корни тривиальны?)")
    
    # 5. Демонстрация шифрования/расшифрования
    print(f"\n5. РАБОТА RSA (ШИФРОВАНИЕ И РАСШИФРОВАНИЕ):")
    message = 42
    cipher, decrypted = demonstrate_rsa_encrypt_decrypt(message, n, e, d)
    print(f"   Исходное сообщение: {message}")
    print(f"   Зашифрованное: {cipher}")
    print(f"   Расшифрованное: {decrypted}")
    print(f"   Успешно? {message == decrypted}")
    
    # 6. Вывод о криптостойкости
    print(f"\n6. ВЫВОД ИЗ ТЕКСТА:")
    print(f"   - Факторизация n = {n} сложна (при больших p,q)")
    print(f"   - Знание φ(n) или нахождение нетривиального корня y ^ 2 ≡ 1 mod n")
    print(f"     позволяет факторизовать n за полиномиальное время.")
    print(f"   - Все эти задачи эквивалентны по сложности.")
    print(f"   - Пока эффективный алгоритм не найден — RSA криптостоек.\n")

if __name__ == "__main__":
    main()