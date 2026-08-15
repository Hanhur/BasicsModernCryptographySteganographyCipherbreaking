# Эллиптическая кривая secp256k1 — цифровая подпись для «Биткойна»
"""
Реализация ECDSA на кривой secp256k1 (чистый Python, без numpy)
Для образовательных целей
"""

import hashlib
import random
import sys

# ============================================================================
# ПАРАМЕТРЫ КРИВОЙ secp256k1
# ============================================================================

# Простое число p (модуль поля)
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
# Коэффициенты кривой: y^2 = x^3 + a*x + b
A = 0
B = 7
# Базовая точка G (генератор)
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
# Порядок базовой точки n
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


# ============================================================================
# АРИФМЕТИКА В КОНЕЧНОМ ПОЛЕ (mod P)
# ============================================================================

def mod_inv(a, mod):
    """Находит обратное число к a по модулю mod (расширенный алгоритм Евклида)"""
    # Для маленьких чисел можно использовать pow(a, -1, mod), но для совместимости
    # с Python < 3.8 реализуем вручную
    if mod == 1:
        return 0
    
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    
    g, x, _ = egcd(a % mod, mod)
    if g != 1:
        raise ValueError(f"Нет обратного элемента для {a} по модулю {mod}")
    return x % mod


# ============================================================================
# АРИФМЕТИКА НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ
# ============================================================================

class Point:
    """Точка на эллиптической кривой secp256k1"""
    
    def __init__(self, x, y, a = A, b = B, mod = P):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.mod = mod
        
        # Проверка: точка не должна быть нулевой (бесконечность)
        if x is None or y is None:
            self.infinity = True
            return
        
        self.infinity = False
        
        # Проверяем, что точка лежит на кривой (y^2 = x^3 + a*x + b mod p)
        # Для учебных целей проверяем, но можно закомментировать для скорости
        left = (y * y) % mod
        right = (x * x * x + a * x + b) % mod
        if left != right:
            raise ValueError(f"Точка ({x}, {y}) не лежит на кривой!")
    
    def __eq__(self, other):
        if self.infinity and other.infinity:
            return True
        if self.infinity or other.infinity:
            return False
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        if self.infinity:
            return "Point(Infinity)"
        return f"Point({hex(self.x)}, {hex(self.y)})"
    
    def __add__(self, other):
        """Сложение двух точек на кривой"""
        # Если одна из точек - бесконечность
        if self.infinity:
            return other
        if other.infinity:
            return self
        
        # Если точки противоположны (x совпадают, y разные)
        if self.x == other.x and self.y == (-other.y) % self.mod:
            return Point(None, None)  # Бесконечность
        
        # Вычисляем наклон (slope)
        if self == other:
            # Удвоение точки: s = (3*x^2 + a) / (2*y)
            num = (3 * self.x * self.x + self.a) % self.mod
            den = (2 * self.y) % self.mod
            s = (num * mod_inv(den, self.mod)) % self.mod
        else:
            # Сложение разных точек: s = (y2 - y1) / (x2 - x1)
            num = (other.y - self.y) % self.mod
            den = (other.x - self.x) % self.mod
            s = (num * mod_inv(den, self.mod)) % self.mod
        
        # Вычисляем координаты новой точки
        x3 = (s * s - self.x - other.x) % self.mod
        y3 = (s * (self.x - x3) - self.y) % self.mod
        
        return Point(x3, y3, self.a, self.b, self.mod)
    
    def __mul__(self, scalar):
        """Умножение точки на скаляр (алгоритм удвоения-сложения)"""
        if self.infinity or scalar == 0:
            return Point(None, None)
        
        result = Point(None, None)  # Бесконечность
        base = self
        n = scalar
        
        while n > 0:
            if n & 1:  # Если бит = 1
                result = result + base
            base = base + base  # Удвоение точки
            n >>= 1
        
        return result
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)


# ============================================================================
# ГЕНЕРАЦИЯ КЛЮЧЕЙ
# ============================================================================

def generate_private_key():
    """
    Генерирует закрытый ключ в диапазоне [1, N-1]
    с использованием SHA-256 для обеспечения 256-битной энтропии
    """
    while True:
        # Генерируем 32 байта (256 бит) случайных данных
        random_bytes = random.getrandbits(256).to_bytes(32, 'big')
        # Хешируем для получения равномерного распределения
        key_bytes = hashlib.sha256(random_bytes).digest()
        # Преобразуем в целое число
        d = int.from_bytes(key_bytes, 'big')
        # Проверяем, что ключ в допустимом диапазоне
        if 1 <= d < N:
            return d


def private_to_public(d):
    """
    Вычисляет открытый ключ Q = d * G
    """
    G = Point(GX, GY)
    Q = d * G
    return Q


# ============================================================================
# ECDSA: ПОДПИСЬ И ПРОВЕРКА
# ============================================================================

def sign_message(private_key, message):
    """
    Подписывает сообщение с использованием закрытого ключа.
    Возвращает (r, S) - подпись
    """
    # Шаг 1: Вычисляем хеш сообщения
    if isinstance(message, str):
        message = message.encode('utf-8')
    z_bytes = hashlib.sha256(message).digest()
    z = int.from_bytes(z_bytes, 'big')
    
    G = Point(GX, GY)
    
    # Шаг 2: Создаем подпись
    while True:
        # Выбираем случайный эфемерный ключ k
        k = random.randint(1, N - 1)
        
        # Вычисляем R = k * G
        R = k * G
        if R.infinity:
            continue
        
        # Вычисляем r = x_R mod N
        r = R.x % N
        if r == 0:
            continue
        
        # Вычисляем S = (z + r * d) / k mod N
        # Важно: используем mod N, а не mod P!
        k_inv = mod_inv(k, N)
        S = ((z + r * private_key) * k_inv) % N
        
        if S == 0:
            continue
        
        return (r, S)


def verify_signature(public_key, message, signature):
    """
    Проверяет подпись сообщения с использованием открытого ключа.
    Возвращает True, если подпись корректна
    """
    r, S = signature
    
    # Шаг 1: Проверяем, что r и S в диапазоне [1, N-1]
    if not (1 <= r < N) or not (1 <= S < N):
        print("Ошибка: r или S вне диапазона")
        return False
    
    # Шаг 2: Вычисляем хеш сообщения
    if isinstance(message, str):
        message = message.encode('utf-8')
    z_bytes = hashlib.sha256(message).digest()
    z = int.from_bytes(z_bytes, 'big')
    
    G = Point(GX, GY)
    
    # Шаг 3: Проверка подписи
    # w = S^(-1) mod N
    w = mod_inv(S, N)
    
    # u1 = z * w mod N
    u1 = (z * w) % N
    
    # u2 = r * w mod N
    u2 = (r * w) % N
    
    # R' = u1 * G + u2 * Q
    point1 = u1 * G
    point2 = u2 * public_key
    R_prime = point1 + point2
    
    if R_prime.infinity:
        print("Ошибка: R' = infinity")
        return False
    
    # Проверяем, что r ≡ x_R' (mod N)
    return r == (R_prime.x % N)


# ============================================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================================

def main():
    print("=" * 70)
    print("ECDSA на кривой secp256k1 - Демонстрация")
    print("=" * 70)
    
    # 1. Генерация ключей
    print("\n[1] Генерация ключей")
    print("-" * 50)
    priv_key = generate_private_key()
    print(f"Закрытый ключ: {hex(priv_key)}")
    
    pub_key = private_to_public(priv_key)
    print(f"Открытый ключ: ({hex(pub_key.x)}, {hex(pub_key.y)})")
    
    # 2. Подпись сообщения
    print("\n[2] Подпись сообщения")
    print("-" * 50)
    message = "Перевод 0.5 BTC на адрес 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    print(f"Сообщение: {message}")
    
    signature = sign_message(priv_key, message)
    r, S = signature
    print(f"Подпись:")
    print(f"  r = {hex(r)}")
    print(f"  S = {hex(S)}")
    
    # 3. Проверка подписи
    print("\n[3] Проверка подписи")
    print("-" * 50)
    is_valid = verify_signature(pub_key, message, signature)
    print(f"Результат проверки: {'✅ ПОДПИСЬ ВЕРНА' if is_valid else '❌ ПОДПИСЬ НЕВЕРНА'}")
    
    # 4. Демонстрация: изменение сообщения
    print("\n[4] Проверка подписи с измененным сообщением")
    print("-" * 50)
    fake_message = "Перевод 100 BTC на адрес 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    print(f"Измененное сообщение: {fake_message}")
    is_valid_fake = verify_signature(pub_key, fake_message, signature)
    print(f"Результат проверки: {'✅ ПОДПИСЬ ВЕРНА' if is_valid_fake else '❌ ПОДПИСЬ НЕВЕРНА'}")
    
    # 5. Информация о параметрах кривой
    print("\n[5] Параметры кривой secp256k1")
    print("-" * 50)
    print(f"p (модуль) = {hex(P)}")
    print(f"n (порядок) = {hex(N)}")
    print(f"a = {A}, b = {B}")
    print(f"G = ({hex(GX)}, {hex(GY)})")
    
    print("\n" + "=" * 70)
    print("Демонстрация завершена!")
    print("=" * 70)


if __name__ == "__main__":
    main()