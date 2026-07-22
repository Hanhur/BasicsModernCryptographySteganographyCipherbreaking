# Нетипичные атаки
"""
Нетипичные атаки на RSA
Исправленная версия с корректной генерацией ключей
"""

import math
import random
import time
from typing import Tuple, Optional

# ============================================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def is_prime(n: int, k: int = 10) -> bool:
    """Тест Миллера-Рабина"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
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

def gcd(a: int, b: int) -> int:
    """Алгоритм Евклида"""
    while b:
        a, b = b, a % b
    return a

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1

def modinv(a: int, m: int) -> int:
    """Обратное число по модулю m"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует (gcd = {g})")
    return x % m

def integer_nth_root(n: int, k: int) -> int:
    """Целочисленный корень k-й степени"""
    if k == 2:
        return int(math.isqrt(n))
    
    # Для кубического корня используем оптимизированный метод
    if k == 3:
        # Начальное приближение
        x = int(round(n ** (1 / 3)))
        # Уточняем
        while (x + 1) ** 3 <= n:
            x += 1
        while x ** 3 > n:
            x -= 1
        return x
    
    # Для других степеней - бинарный поиск
    low = 0
    high = min(n, 10 ** (len(str(n)) // k + 2))
    while low <= high:
        mid = (low + high) // 2
        if mid ** k < n:
            low = mid + 1
        elif mid ** k > n:
            high = mid - 1
        else:
            return mid
    return high

# ============================================================================
# 2. ГЕНЕРАЦИЯ RSA КЛЮЧЕЙ
# ============================================================================

def generate_rsa_keypair(bits: int = 512, close_primes: bool = False, e: int = None) -> dict:
    """
    Генерирует пару ключей RSA.
    Если close_primes = True, генерирует p и q близкими.
    Если e задан, пытается использовать его (если gcd(e, phi) = 1)
    """
    print(f"\n🔐 Генерация RSA-ключей ({bits} бит)...")
    
    if close_primes:
        print("   (Режим: близкие простые числа для демонстрации атаки)")
        # Генерируем близкие простые
        p_base = random.getrandbits(bits // 2)
        p = p_base | 1
        while not is_prime(p):
            p += 2
        
        q = p + random.randint(2, 10000)
        while not is_prime(q):
            q += 1
    else:
        p = random.getrandbits(bits // 2) | 1
        while not is_prime(p):
            p += 2
        
        q = random.getrandbits(bits // 2) | 1
        while not is_prime(q):
            q += 2
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e
    if e is None:
        e = 65537
        while gcd(e, phi) != 1:
            e += 2
    else:
        # Проверяем, что e взаимно просто с phi
        if gcd(e, phi) != 1:
            print(f"   ⚠️  gcd({e}, {phi}) = {gcd(e, phi)} != 1")
            print(f"   🔄 Генерируем новые p и q для e = {e}...")
            # Рекурсивно генерируем новые ключи с этим e
            return generate_rsa_keypair(bits, close_primes, e)
    
    d = modinv(e, phi)
    
    print(f"   ✅ p = {p}")
    print(f"   ✅ q = {q}")
    print(f"   ✅ n = {n}")
    print(f"   ✅ phi = {phi}")
    print(f"   ✅ e = {e} (gcd(e, phi) = {gcd(e, phi)})")
    
    return {
        'p': p, 'q': q, 'n': n, 'phi': phi,
        'public': (e, n),
        'private': (d, n)
    }

# ============================================================================
# 3. АТАКА NEXT PRIME (ФЕРМА)
# ============================================================================

def attack_nextprime(n: int, max_iterations: int = 100000) -> Optional[Tuple[int, int]]:
    """Атака NextPrime для близких p и q"""
    print(f"\n🔍 Запуск атаки NextPrime для n = {n}")
    print(f"   (основано на методе факторизации Ферма)")
    
    start_time = time.time()
    
    if n % 2 == 0:
        return (2, n // 2)
    
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    
    iterations = 0
    while iterations < max_iterations:
        b2 = a * a - n
        b = math.isqrt(b2)
        
        if b * b == b2:
            p = a - b
            q = a + b
            if p > 1 and q > 1:
                elapsed = time.time() - start_time
                print(f"   ✅ Найдено за {iterations} итераций ({elapsed:.3f} сек)")
                print(f"   p = {p}, q = {q}")
                return (p, q)
        
        a += 1
        iterations += 1
        
        if iterations % 10000 == 0:
            print(f"   ... {iterations} итераций, a = {a}")
    
    print(f"   ❌ Атака не удалась: достигнут лимит итераций")
    return None

# ============================================================================
# 4. АТАКА МАЛОЙ ЭКСПОНЕНТЫ (e=3)
# ============================================================================

def attack_small_e(ciphertext: int, e: int, n: int, message_bits: int = None) -> Optional[int]:
    """
    Атака на малую экспоненту.
    Если M^e < n, то M = root_e(ciphertext)
    """
    print(f"\n🔍 Проверка атаки на малую экспоненту e = {e}")
    print(f"   Шифротекст C = {ciphertext}")
    print(f"   Модуль n = {n}")
    
    if e == 3:
        root = integer_nth_root(ciphertext, 3)
        if root ** 3 == ciphertext:
            print(f"   ✅ УСПЕХ! M = {root}")
            print(f"   M ^ 3 = {root ** 3} < n = {n}")
            return root
        else:
            print(f"   ❌ Не удалось: M ^ 3 > n (нужна факторизация)")
            print(f"   Cube root = {root}, {root} ^ 3 = {root ** 3}")
            return None
    else:
        print(f"   ⚠️  Атака работает только для e = 3, текущее e = {e}")
        # Для других малых e можно попробовать общий подход
        root = integer_nth_root(ciphertext, e)
        if root ** e == ciphertext:
            print(f"   ✅ УСПЕХ! M = {root}")
            return root
        return None

# ============================================================================
# 5. АТАКА НА ОБЩИЙ МОДУЛЬ
# ============================================================================

def attack_common_modulus(c1: int, c2: int, e1: int, e2: int, n: int) -> Optional[int]:
    """Атака на общий модуль"""
    print(f"\n🔍 Атака на общий модуль (n = {n})")
    print(f"   c1 зашифровано с e1 = {e1}, c2 с e2 = {e2}")
    
    g, a, b = egcd(e1, e2)
    
    if g != 1:
        print(f"   ❌ Не удалось: gcd(e1, e2) = {g} != 1")
        return None
    
    print(f"   Найдены a = {a}, b = {b}, где a * e1 + b * e2 = {g}")
    
    if a < 0:
        c1_inv = modinv(c1, n)
        c1_pow = pow(c1_inv, -a, n)
    else:
        c1_pow = pow(c1, a, n)
    
    if b < 0:
        c2_inv = modinv(c2, n)
        c2_pow = pow(c2_inv, -b, n)
    else:
        c2_pow = pow(c2, b, n)
    
    message = (c1_pow * c2_pow) % n
    print(f"   ✅ Восстановлено M = {message}")
    return message

# ============================================================================
# 6. ДЕМОНСТРАЦИЯ
# ============================================================================

def demo_all_attacks():
    """Демонстрация всех атак"""
    
    print("\n" + "=" * 70)
    print("🛡️  НЕТИПИЧНЫЕ АТАКИ НА RSA - ИСПРАВЛЕННАЯ ВЕРСИЯ")
    print("=" * 70)
    
    # ------------------------------------------------------------------------
    # 1. Атака NextPrime
    # ------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 СЦЕНАРИЙ 1: АТАКА NEXT PRIME")
    print("-" * 70)
    
    key_close = generate_rsa_keypair(bits = 256, close_primes = True)
    n_close = key_close['n']
    e_close = key_close['public'][0]
    
    test_msg = 123456789
    cipher = pow(test_msg, e_close, n_close)
    print(f"\n📨 Исходное сообщение: {test_msg}")
    print(f"🔒 Шифротекст: {cipher}")
    
    factors = attack_nextprime(n_close)
    if factors:
        p, q = factors
        phi = (p - 1) * (q - 1)
        d = modinv(e_close, phi)
        recovered = pow(cipher, d, n_close)
        print(f"\n💡 Восстановленное сообщение: {recovered}")
        print(f"   Совпадает: {recovered == test_msg}")
    
    # ------------------------------------------------------------------------
    # 2. Атака малой экспоненты (e=3)
    # ------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 СЦЕНАРИЙ 2: АТАКА НА МАЛУЮ ЭКСПОНЕНТУ (e = 3)")
    print("-" * 70)
    
    # Пробуем сгенерировать ключи с e=3
    print("   Генерация ключей с e = 3 ...")
    try:
        key_small = generate_rsa_keypair(bits = 128, close_primes = False, e = 3)
        n_small = key_small['n']
        e_small = key_small['public'][0]
        
        # Сообщение должно быть маленьким, чтобы M^3 < n
        # Для 128-битного n (≈ 10^38), M должно быть < 10^12
        msg_small = 12345
        print(f"\n   Исходное сообщение M = {msg_small}")
        print(f"   M ^ 3 = {msg_small ** 3}")
        print(f"   n = {n_small}")
        
        if msg_small ** 3 < n_small:
            print(f"   ✅ M ^ 3 < n - атака возможна!")
            c_small = pow(msg_small, e_small, n_small)
            print(f"   Шифротекст C = {c_small}")
            
            recovered_small = attack_small_e(c_small, e_small, n_small)
            if recovered_small:
                print(f"   ✅ Восстановлено: {recovered_small}")
                print(f"   Совпадает: {recovered_small == msg_small}")
        else:
            print(f"   ⚠️  M ^ 3 > n - атака не работает (нужно меньшее M)")
            print(f"   Попробуем с меньшим M...")
            
            # Ищем подходящее M
            for test_m in range(10, 1000):
                if test_m ** 3 < n_small:
                    msg_small = test_m
                    break
            
            if msg_small ** 3 < n_small:
                c_small = pow(msg_small, e_small, n_small)
                print(f"   Новое M = {msg_small}, C = {c_small}")
                recovered_small = attack_small_e(c_small, e_small, n_small)
                if recovered_small:
                    print(f"   ✅ Восстановлено: {recovered_small}")
            else:
                print(f"   ❌ Не найдено подходящее M")
                
    except ValueError as e:
        print(f"   ❌ Ошибка генерации ключей: {e}")
        print("   Пробуем другой подход...")
        
        # Ручной подход для демонстрации
        print("\n   Ручная демонстрация атаки e = 3:")
        # Берем заведомо маленький модуль
        p_man = 47
        q_man = 53
        n_man = p_man * q_man
        phi_man = (p_man - 1) * (q_man - 1)
        
        # Проверяем, что 3 взаимно просто с phi_man
        if gcd(3, phi_man) == 1:
            e_man = 3
            d_man = modinv(e_man, phi_man)
            msg_man = 42
            c_man = pow(msg_man, e_man, n_man)
            
            print(f"   p = {p_man}, q = {q_man}, n = {n_man}, phi = {phi_man}")
            print(f"   M = {msg_man}, M ^ 3 = {msg_man ** 3}")
            print(f"   C = {c_man}")
            
            # Атака: извлекаем кубический корень
            root = integer_nth_root(c_man, 3)
            print(f"   Кубический корень из C = {root}")
            print(f"   Проверка: {root} ^ 3 = {root ** 3}")
            if root ** 3 == c_man:
                print(f"   ✅ Восстановлено M = {root}")
            else:
                print(f"   ❌ Атака не удалась")
        else:
            print(f"   gcd(3, {phi_man}) = {gcd(3, phi_man)} - нужно менять p и q")
    
    # ------------------------------------------------------------------------
    # 3. Атака на общий модуль
    # ------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 СЦЕНАРИЙ 3: АТАКА НА ОБЩИЙ МОДУЛЬ")
    print("-" * 70)
    
    # Используем небольшой модуль для демонстрации
    p_common = 101
    q_common = 103
    n_common = p_common * q_common
    phi_common = (p_common - 1) * (q_common - 1)
    
    # Выбираем e, которые взаимно просты с phi_common
    e1 = 17
    e2 = 19
    
    # Проверяем, что они взаимно просты с phi
    if gcd(e1, phi_common) == 1 and gcd(e2, phi_common) == 1:
        d1 = modinv(e1, phi_common)
        d2 = modinv(e2, phi_common)
        
        msg_common = 777
        c1 = pow(msg_common, e1, n_common)
        c2 = pow(msg_common, e2, n_common)
        
        print(f"   Общий n = {n_common}, phi = {phi_common}")
        print(f"   Алиса: e = {e1}, шифр = {c1}")
        print(f"   Боб: e = {e2}, шифр = {c2}")
        
        recovered_common = attack_common_modulus(c1, c2, e1, e2, n_common)
        if recovered_common:
            print(f"   ✅ Восстановлено: {recovered_common}")
            print(f"   Совпадает: {recovered_common == msg_common}")
    else:
        print(f"   ❌ Неподходящие e для phi = {phi_common}")
    
    print("\n" + "=" * 70)
    print("🏁 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)

# ============================================================================
# 7. ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    random.seed(42)
    demo_all_attacks()