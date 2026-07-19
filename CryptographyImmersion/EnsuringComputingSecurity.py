# Обеспечение безопасности и вычислений
"""
Криптографический демонстратор
Основан на принципах из текста:
- Принцип Керкхоффа (алгоритм открыт)
- Симметричные vs асимметричные алгоритмы
- Проблема передачи ключа
- Факторизация как основа RSA
- Слабое звено в цепи безопасности
"""

import random
import math
import time
from typing import Tuple, List

# ============================================================================
# ЧАСТЬ 1: ВСПОМОГАТЕЛЬНЫЕ МАТЕМАТИЧЕСКИЕ ФУНКЦИИ (без numpy)
# ============================================================================

def is_prime(n: int, k: int = 5) -> bool:
    """Проверка на простоту (тест Миллера-Рабина)"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Проводим k раундов теста
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits: int = 8) -> int:
    """Генерация простого числа заданной битности"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # Убеждаемся, что число нечетное и нужной длины
        if is_prime(n):
            return n

def gcd(a: int, b: int) -> int:
    """Наибольший общий делитель (алгоритм Евклида)"""
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a: int, m: int) -> int:
    """Обратное число по модулю (расширенный алгоритм Евклида)"""
    # Расширенный алгоритм Евклида
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, x1, y1 = egcd(b % a, a)
        return (g, y1 - (b // a) * x1, x1)
    
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента не существует: gcd({a}, {m}) = {g}")
    return x % m

def factorize(n: int) -> Tuple[int, int]:
    """
    Факторизация числа (пробное деление - для демонстрации)
    В реальности для RSA-250 это невозможно, но для маленьких чисел - работает
    """
    if n < 2:
        return (1, n)
    
    # Проверка на четность
    if n % 2 == 0:
        return (2, n // 2)
    
    # Пробное деление до sqrt(n)
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return (i, n // i)
    
    return (1, n)  # Если не разложилось (на самом деле простое)

# ============================================================================
# ЧАСТЬ 2: СИММЕТРИЧНОЕ ШИФРОВАНИЕ (Демонстрация проблемы ключа)
# ============================================================================

class SymmetricCipher:
    """
    Простой симметричный шифр (XOR с ключом)
    Демонстрирует: алгоритм открыт, но ключ должен быть секретным
    """
    
    def __init__(self, key: bytes):
        self.key = key
        print(f"[СИММЕТРИЯ] Создан шифр с ключом: {key.hex()}")
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """Шифрование (XOR с повторяющимся ключом)"""
        result = bytearray()
        for i, byte in enumerate(plaintext):
            result.append(byte ^ self.key[i % len(self.key)])
        return bytes(result)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """Дешифрование (XOR - симметричная операция)"""
        # XOR симметричен: шифрование и дешифрование идентичны
        return self.encrypt(ciphertext)


# ============================================================================
# ЧАСТЬ 3: АСИММЕТРИЧНОЕ ШИФРОВАНИЕ (RSA на основе факторизации)
# ============================================================================

class RSA:
    """
    Реализация RSA (учебная, с малыми ключами)
    Безопасность основана на сложности факторизации
    """
    
    def __init__(self, bits: int = 8):
        """
        Генерация ключей
        bits: битность простых чисел (для демонстрации используем малые значения)
        """
        print(f"\n[RSA] Генерация ключей с битностью {bits}")
        
        # Генерируем два различных простых числа
        self.p = generate_prime(bits)
        self.q = generate_prime(bits)
        while self.p == self.q:
            self.q = generate_prime(bits)
        
        # Вычисляем n = p * q (основа безопасности!)
        self.n = self.p * self.q
        
        # Функция Эйлера: φ(n) = (p-1) * (q-1)
        self.phi = (self.p - 1) * (self.q - 1)
        
        # Выбираем открытую экспоненту e (обычно 65537, но для малых чисел берем 3)
        self.e = 3
        while gcd(self.e, self.phi) != 1:
            self.e += 2
        
        # Вычисляем закрытую экспоненту d (обратное к e по модулю φ(n))
        self.d = mod_inverse(self.e, self.phi)
        
        # Открытый ключ: (e, n), Закрытый ключ: (d, n)
        print(f"  p = {self.p}, q = {self.q}")
        print(f"  n = {self.n} (произведение p*q)")
        print(f"  φ(n) = {self.phi}")
        print(f"  Открытый ключ: e = {self.e}, n = {self.n}")
        print(f"  Закрытый ключ: d = {self.d}, n = {self.n}")
        print(f"  [ПРИНЦИП КЕРКХОФФА] Алгоритм открыт, секретны только: p, q, d")
    
    def encrypt(self, message: int) -> int:
        """Шифрование: c = m^e mod n"""
        if message >= self.n:
            raise ValueError(f"Сообщение {message} >= n = {self.n}. Используйте меньшее число.")
        return pow(message, self.e, self.n)
    
    def decrypt(self, ciphertext: int) -> int:
        """Дешифрование: m = c ^ d mod n"""
        return pow(ciphertext, self.d, self.n)
    
    def break_by_factorization(self) -> Tuple[int, int]:
        """
        Атака на RSA через факторизацию (демонстрация "слабого звена")
        Если мы сможем разложить n на p и q, то сможем вычислить закрытый ключ
        """
        print(f"\n  [АТАКА] Пытаемся разложить n = {self.n} на множители...")
        start_time = time.time()
        
        p_found, q_found = factorize(self.n)
        elapsed = time.time() - start_time
        
        if p_found != 1 and q_found != 1:
            print(f"  [УСПЕШНО] n = {p_found} * {q_found} за {elapsed:.4f} сек")
            # Вычисляем закрытый ключ
            phi_found = (p_found - 1) * (q_found - 1)
            d_found = mod_inverse(self.e, phi_found)
            print(f"  [КОМПРОМЕТАЦИЯ] Закрытый ключ d = {d_found} вычислен через факторизацию!")
            return (p_found, q_found)
        else:
            print(f"  [НЕУДАЧНО] Не удалось разложить {self.n} простым перебором")
            return (0, 0)


# ============================================================================
# ЧАСТЬ 4: ДЕМОНСТРАЦИЯ "СЛАБОГО ЗВЕНА" (плохая реализация)
# ============================================================================

class WeakRSA(RSA):
    """
    Умышленно ослабленная версия RSA с утечкой информации
    Демонстрирует: сложность - враг безопасности
    """
    
    def __init__(self, bits: int = 8):
        super().__init__(bits)
        # Слабое звено: храним p и q в открытом виде для "отладки"
        self.debug_p = self.p
        self.debug_q = self.q
        print(f"  [СЛАБОЕ ЗВЕНО] p и q сохранены в открытом доступе (debug_p, debug_q)")
        print(f"  [НАРУШЕНИЕ] Это нарушает принцип Керкхоффа - секретность алгоритма нарушена!")
    
    def get_private_info(self):
        """Метод, который не должен существовать - утечка секретных данных"""
        return {
            'p': self.debug_p,
            'q': self.debug_q,
            'd': self.d
        }


# ============================================================================
# ЧАСТЬ 5: СОВЕРШЕННАЯ СЕКРЕТНОСТЬ (Шифр Вернама - теоретически)
# ============================================================================

class VernamCipher:
    """
    Шифр Вернама (одноразовый блокнот)
    Теоретически совершенная секретность, но практически нереализуем
    """
    
    @staticmethod
    def generate_key(length: int) -> bytes:
        """Генерация ключа той же длины, что и сообщение"""
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> bytes:
        """Шифрование: c = m ⊕ k"""
        if len(key) != len(plaintext):
            raise ValueError("Длина ключа должна совпадать с длиной сообщения!")
        return bytes([p ^ k for p, k in zip(plaintext, key)])
    
    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes) -> bytes:
        """Дешифрование: m = c ⊕ k (та же операция)"""
        return VernamCipher.encrypt(ciphertext, key)


# ============================================================================
# ЧАСТЬ 6: ГЛАВНАЯ ДЕМОНСТРАЦИЯ
# ============================================================================

def main():
    print("=" * 70)
    print("КРИПТОГРАФИЧЕСКИЙ ДЕМОНСТРАТОР")
    print("Основан на принципах: Керкхофф, факторизация, сложность реализации")
    print("=" * 70)
    
    # ==========================================
    # 1. Демонстрация симметричного шифрования
    # ==========================================
    print("\n" + "=" * 70)
    print("ЧАСТЬ 1: СИММЕТРИЧНОЕ ШИФРОВАНИЕ")
    print("Проблема: как безопасно передать ключ?")
    print("=" * 70)
    
    message = b"Hello, World!"
    key = b"secret"
    
    symmetric = SymmetricCipher(key)
    ciphertext_sym = symmetric.encrypt(message)
    decrypted_sym = symmetric.decrypt(ciphertext_sym)
    
    print(f"  Исходное сообщение: {message}")
    print(f"  Зашифровано: {ciphertext_sym.hex()}")
    print(f"  Расшифровано: {decrypted_sym}")
    print(f"  [ПРОБЛЕМА] Ключ '{key}' должен быть передан получателю по защищенному каналу")
    print(f"  [ПРИНЦИП] Алгоритм открыт (XOR), секретен только ключ")
    
    # ==========================================
    # 2. Демонстрация RSA (асимметричное шифрование)
    # ==========================================
    print("\n" + "=" * 70)
    print("ЧАСТЬ 2: АСИММЕТРИЧНОЕ ШИФРОВАНИЕ (RSA)")
    print("Безопасность основана на сложности факторизации")
    print("=" * 70)
    
    # Создаем RSA с малыми ключами (для демонстрации)
    rsa = RSA(bits = 8)  # 8-битные простые числа = n ~ 256-512
    
    # Шифруем сообщение (число меньше n)
    plaintext_num = 42
    ciphertext_rsa = rsa.encrypt(plaintext_num)
    decrypted_rsa = rsa.decrypt(ciphertext_rsa)
    
    print(f"\n  Исходное сообщение (число): {plaintext_num}")
    print(f"  Зашифровано: {ciphertext_rsa}")
    print(f"  Расшифровано: {decrypted_rsa}")
    print(f"  [УСПЕШНО] Расшифровка работает!")
    
    # Показываем, что факторизация - это основа безопасности
    print(f"\n  [БЕЗОПАСНОСТЬ] Чтобы взломать RSA, нужно разложить n = {rsa.n} на p и q")
    rsa.break_by_factorization()
    
    # ==========================================
    # 3. Демонстрация "слабого звена"
    # ==========================================
    print("\n" + "=" * 70)
    print("ЧАСТЬ 3: СЛАБОЕ ЗВЕНО В ЦЕПИ")
    print("Сложность реализации - враг безопасности")
    print("=" * 70)
    
    weak = WeakRSA(bits = 8)
    print("\n  [ЭКСПЛУАТАЦИЯ] Злоумышленник находит утечку...")
    leaked = weak.get_private_info()
    print(f"  [ВЗЛОМ] Получены секретные данные: p = {leaked['p']}, q = {leaked['q']}, d = {leaked['d']}")
    print(f"  [ИТОГ] Криптосистема скомпрометирована из-за ошибки реализации!")
    print(f"  [ПРИНЦИП] Слабое звено разрушает всю цепь безопасности")
    
    # ==========================================
    # 4. Шифр Вернама (совершенная секретность)
    # ==========================================
    print("\n" + "=" * 70)
    print("ЧАСТЬ 4: СОВЕРШЕННАЯ СЕКРЕТНОСТЬ (Шифр Вернама)")
    print("Теоретически невзламываем, но практически нереализуем")
    print("=" * 70)
    
    msg = b"Secret message"
    vernam_key = VernamCipher.generate_key(len(msg))
    ciphertext_vernam = VernamCipher.encrypt(msg, vernam_key)
    decrypted_vernam = VernamCipher.decrypt(ciphertext_vernam, vernam_key)
    
    print(f"  Сообщение: {msg}")
    print(f"  Ключ (случайный, длина {len(vernam_key)} байт): {vernam_key.hex()}")
    print(f"  Шифротекст: {ciphertext_vernam.hex()}")
    print(f"  Расшифровано: {decrypted_vernam}")
    print(f"  [ТЕОРИЯ] Абсолютно стойкая система (P(M|C) = P(M))")
    print(f"  [ПРАКТИКА] Нереализуема для больших сообщений (ключ должен быть таким же длинным)")
    print(f"  [ПРОБЛЕМА] Как безопасно передать ключ длиной {len(msg)} байт?")
    
    # ==========================================
    # 5. Заключительный вывод
    # ==========================================
    print("\n" + "=" * 70)
    print("ВЫВОДЫ (на основе текста)")
    print("=" * 70)
    print("1. Симметричные шифры быстры, но есть проблема передачи ключа")
    print("2. RSA решает эту проблему, но опирается на факторизацию")
    print("3. Принцип Керкхоффа: алгоритм должен быть открытым, ключ - секретным")
    print("4. Сложность реализации создает уязвимости (слабое звено)")
    print("5. Совершенная секретность (Вернам) - только теория")
    print("6. Безопасность - изменчивое понятие (зависит от вычислительных мощностей)")
    print("\n[ГЛАВНАЯ МЕТАФОРА] Слабое звено разрушает всю цепь!")
    print("=" * 70)


if __name__ == "__main__":
    main()