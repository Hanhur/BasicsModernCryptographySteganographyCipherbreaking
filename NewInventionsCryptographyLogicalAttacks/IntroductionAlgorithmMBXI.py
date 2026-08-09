import random
import math

# =====================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# =====================================================

def egcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y) такие, что a * x + b * y = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = egcd(b, a % b)
    return gcd, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """
    Находит обратное число к 'a' по модулю 'm' 
    (расширенный алгоритм Евклида).
    Возвращает x такой, что (a * x) % m == 1.
    """
    a = a % m
    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        return None  # обратного не существует
    return x % m

def mod_pow(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю (бинароный метод).
    Эквивалент (base ** exponent) % modulus, но работает быстрее.
    """
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result

def is_primitive_root(g, p):
    """
    Проверяет, является ли 'g' первообразным корнем по модулю 'p'.
    Для простоты проверяем, что g ^ ( (p - 1) / q ) != 1 для всех простых q | (p - 1).
    """
    if g % p == 0:
        return False
    
    # Находим все простые делители числа (p-1)
    phi = p - 1
    factors = []
    n = phi
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
        i += 1
    if n > 1:
        factors.append(n)
    
    # Проверяем условие первообразного корня
    for q in factors:
        if mod_pow(g, phi // q, p) == 1:
            return False
    return True

def find_primitive_root(p):
    """
    Находит какой-либо первообразный корень по модулю p.
    """
    if p == 2:
        return 1
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    return None

def generate_prime(bits = 16):
    """
    Генерирует простое число заданной битности (для демонстрации).
    В реальных приложениях битность должна быть >= 2048.
    """
    while True:
        # Генерируем нечётное число
        candidate = random.getrandbits(bits)
        # Убеждаемся, что число нечётное и достаточно большое
        candidate |= (1 << bits) | 1
        
        # Проверяем на простоту (перебор делителей до sqrt)
        if is_prime(candidate):
            return candidate

def is_prime(n):
    """
    Простая проверка на простоту (для демонстрации).
    Для реальных приложений используйте Miller-Rabin.
    """
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def find_valid_eB(H, p_minus_1, start_from = 1):
    """
    Находит подходящее значение eB такое, что:
    1. eB > 0
    2. gcd(H + eB, p_minus_1) = 1
    3. eB взаимно просто с p_minus_1 (не обязательно, но желательно)
    """
    eB = start_from
    while True:
        if math.gcd(H + eB, p_minus_1) == 1:
            return eB
        eB += 1

# =====================================================
#  ОСНОВНАЯ РЕАЛИЗАЦИЯ MBXI
# =====================================================

class MBXI:
    """
    Реализация алгоритма MBXI (гибридный криптоалгоритм).
    """
    
    def __init__(self, p = None, g = None, bits = 16):
        """
        Инициализация общих параметров.
        Если p и g не заданы, генерируются автоматически.
        """
        if p is None:
            self.p = generate_prime(bits)
        else:
            self.p = p
        
        if g is None:
            self.g = find_primitive_root(self.p)
        else:
            self.g = g
        
        # Проверяем, что g - первообразный корень
        if not is_primitive_root(self.g, self.p):
            raise ValueError(f"Число {self.g} не является первообразным корнем по модулю {self.p}")
        
        print(f"=== ОБЩИЕ ПАРАМЕТРЫ ===")
        print(f"Простое число p = {self.p}")
        print(f"Первообразный корень g = {self.g}")
        print()
    
    def generate_keypair(self, name = "Участник", secret_key = None):
        """
        Генерирует пару ключей (закрытый, открытый) для участника.
        Если secret_key задан, использует его (для воспроизводимости примера).
        Возвращает (секретный_ключ, открытый_ключ)
        """
        if secret_key is None:
            # Закрытый ключ: случайное число в диапазоне [2, p-2]
            secret = random.randint(2, self.p - 2)
        else:
            secret = secret_key % (self.p - 1)
            if secret < 2:
                secret = 2
        
        # Открытый ключ: g^secret mod p
        public = mod_pow(self.g, secret, self.p)
        
        print(f"=== ГЕНЕРАЦИЯ КЛЮЧЕЙ ДЛЯ {name.upper()} ===")
        print(f"Закрытый ключ = {secret}")
        print(f"Открытый ключ = {public}")
        print()
        
        return secret, public
    
    def encrypt(self, message, alice_public_key, bob_secret_key, eB = None):
        """
        Шифрование сообщения (Боб отправляет Алисе).
        
        Параметры:
            message (int): исходное сообщение M (должно быть < p)
            alice_public_key (int): открытый ключ Алисы (KA)
            bob_secret_key (int): закрытый ключ Боба (b)
            eB (int, optional): случайный параметр. Если None - генерируется автоматически.
        
        Возвращает:
            (C, eB, KB) - криптограмма, параметр eB, открытый ключ Боба
        """
        if message >= self.p:
            raise ValueError(f"Сообщение {message} должно быть меньше p = {self.p}")
        
        # Вычисляем открытый ключ Боба (KB = g^b mod p)
        KB = mod_pow(self.g, bob_secret_key, self.p)
        
        # Вычисляем общий секрет H = KA^b mod p
        H = mod_pow(alice_public_key, bob_secret_key, self.p)
        
        # Выбираем параметр eB (должен быть взаимно прост с p-1)
        if eB is None:
            # Автоматически находим подходящее eB
            eB = find_valid_eB(H, self.p - 1, start_from = 1)
        else:
            # Проверяем, что выбранное eB подходит
            if math.gcd(H + eB, self.p - 1) != 1:
                print(f"  ВНИМАНИЕ: eB = {eB} не подходит для H = {H}.")
                print(f"  Ищем другое значение...")
                eB = find_valid_eB(H, self.p - 1, start_from = eB + 1)
        
        # Решаем обратное модульное уравнение для x:
        # (H + eB) * x ≡ 1 (mod p-1)
        a = (H + eB) % (self.p - 1)
        x = mod_inverse(a, self.p - 1)
        
        if x is None:
            raise RuntimeError(f"Не удалось найти обратное для a = {a} по модулю {self.p - 1}")
        
        # Вычисляем криптограмму C = M^x mod p
        C = mod_pow(message, x, self.p)
        
        print(f"=== ШИФРОВАНИЕ (БОБ -> АЛИСА) ===")
        print(f"Исходное сообщение M = {message}")
        print(f"Открытый ключ Алисы KA = {alice_public_key}")
        print(f"Закрытый ключ Боба b = {bob_secret_key}")
        print(f"Открытый ключ Боба KB = {KB}")
        print(f"Общий секрет H = KA ^ b mod p = {H}")
        print(f"Параметр eB = {eB}")
        print(f"a = (H + eB) mod (p - 1) = {a}")
        print(f"Секретный ключ шифрования x = {x}")
        print(f"Криптограмма C = {C}")
        print()
        
        return C, eB, KB
    
    def decrypt(self, C, eB, bob_public_key, alice_secret_key):
        """
        Расшифрование сообщения (Алиса получает от Боба).
        
        Параметры:
            C (int): криптограмма
            eB (int): параметр от Боба
            bob_public_key (int): открытый ключ Боба (KB)
            alice_secret_key (int): закрытый ключ Алисы (a)
        
        Возвращает:
            int: расшифрованное сообщение M
        """
        # Вычисляем общий секрет H = KB^a mod p
        H = mod_pow(bob_public_key, alice_secret_key, self.p)
        
        # Решаем обратное модульное уравнение для y:
        # (H + eB) * y ≡ 1 (mod p-1)
        a = (H + eB) % (self.p - 1)
        y = mod_inverse(a, self.p - 1)
        
        if y is None:
            raise RuntimeError(f"Не удалось найти обратное для a = {a} по модулю {self.p - 1}")
        
        # Восстанавливаем сообщение M = C^y mod p
        M = mod_pow(C, y, self.p)
        
        print(f"=== РАСШИФРОВАНИЕ (АЛИСА) ===")
        print(f"Криптограмма C = {C}")
        print(f"Параметр eB = {eB}")
        print(f"Открытый ключ Боба KB = {bob_public_key}")
        print(f"Закрытый ключ Алисы a = {alice_secret_key}")
        print(f"Общий секрет H = KB ^ a mod p = {H}")
        print(f"a = (H + eB) mod (p - 1) = {a}")
        print(f"Секретный ключ расшифрования y = {y}")
        print(f"Расшифрованное сообщение M = {M}")
        print()
        
        return M

# =====================================================
#  ДЕМОНСТРАЦИЯ РАБОТЫ АЛГОРИТМА
# =====================================================

def main():
    print("=" * 70)
    print(" АЛГОРИТМ MBXI - ДЕМОНСТРАЦИОННЫЙ ПРИМЕР")
    print("=" * 70)
    print()
    
    # 1. Инициализация общих параметров
    # Используем p=7919, g=7 (как в вашем примере)
    p = 7919
    g = 7
    
    # Проверяем, что g - первообразный корень
    if not is_primitive_root(g, p):
        print(f"ОШИБКА: {g} не является первообразным корнем по модулю {p}")
        return
    
    # Создаём экземпляр алгоритма
    mbxi = MBXI(p = p, g = g)
    
    # 2. Генерация ключей с заданными значениями (как в вашем примере)
    print("=" * 70)
    print(" ШАГ 1: ГЕНЕРАЦИЯ КЛЮЧЕЙ")
    print("=" * 70)
    
    # Используем ваши числа из примера
    alice_secret = 123456
    bob_secret = 543210
    
    alice_secret, alice_public = mbxi.generate_keypair("Алиса", alice_secret)
    bob_secret, bob_public = mbxi.generate_keypair("Боб", bob_secret)
    
    # Проверяем, что открытые ключи соответствуют вашему примеру
    print(f"Проверка: KA = {alice_public} (ожидается 7036)")
    print(f"Проверка: KB = {bob_public} (ожидается 4997)")
    print()
    
    # 3. Шифрование (Боб отправляет сообщение Алисе)
    print("=" * 70)
    print(" ШАГ 2: ШИФРОВАНИЕ (БОБ)")
    print("=" * 70)
    
    M = 88  # Исходное сообщение (как в вашем примере)
    eB = 1  # Для демонстрации пробуем eB=1 (если не подойдёт, автоматически изменится)
    
    C, eB_used, KB = mbxi.encrypt(
        message = M,
        alice_public_key = alice_public,
        bob_secret_key = bob_secret,
        eB = eB
    )
    
    # 4. Расшифрование (Алиса получает сообщение)
    print("=" * 70)
    print(" ШАГ 3: РАСШИФРОВАНИЕ (АЛИСА)")
    print("=" * 70)
    
    decrypted_M = mbxi.decrypt(
        C = C,
        eB = eB_used,
        bob_public_key = KB,
        alice_secret_key = alice_secret
    )
    
    # 5. Проверка результата
    print("=" * 70)
    print(" РЕЗУЛЬТАТ")
    print("=" * 70)
    print(f"Исходное сообщение: {M}")
    print(f"Расшифрованное сообщение: {decrypted_M}")
    print(f"Успешно: {'ДА ✓' if M == decrypted_M else 'НЕТ ✗'}")
    print()
    
    # 6. Дополнительный тест с другим сообщением и автоматическим подбором eB
    print("=" * 70)
    print(" ДОПОЛНИТЕЛЬНЫЙ ТЕСТ (автоматический подбор eB)")
    print("=" * 70)
    
    M2 = 1234
    
    C2, eB_used2, KB2 = mbxi.encrypt(
        message = M2,
        alice_public_key = alice_public,
        bob_secret_key = bob_secret,
        eB = None  # Автоматический подбор
    )
    
    decrypted_M2 = mbxi.decrypt(
        C = C2,
        eB = eB_used2,
        bob_public_key = KB2,
        alice_secret_key = alice_secret
    )
    
    print(f"Исходное сообщение (2): {M2}")
    print(f"Расшифрованное сообщение (2): {decrypted_M2}")
    print(f"Успешно: {'ДА ✓' if M2 == decrypted_M2 else 'НЕТ ✗'}")
    
    print()
    print("=" * 70)
    print(" КОНЕЦ ДЕМОНСТРАЦИИ")
    print("=" * 70)

if __name__ == "__main__":
    main()