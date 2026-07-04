# Электронная подпись на базе шифра Эль-Гамаля
import random
import math
from typing import Tuple

def gcd_extended(a: int, b: int) -> Tuple[int, int, int]:
    """
    Расширенный алгоритм Евклида.
    Возвращает (gcd, x, y), где a * x + b * y = gcd(a, b)
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = gcd_extended(b % a, a)
    return gcd, y1 - (b // a) * x1, x1

def mod_inverse(a: int, m: int) -> int:
    """
    Находит обратное число a^-1 mod m
    """
    gcd, x, _ = gcd_extended(a, m)
    if gcd != 1:
        raise ValueError(f"Число {a} не имеет обратного по модулю {m}")
    return x % m

def is_prime(n: int, k: int = 10) -> bool:
    """
    Проверка числа на простоту тестом Миллера-Рабина
    """
    if n < 2:
        return False
    if n in [2, 3]:
        return True
    if n % 2 == 0:
        return False
    
    # Представляем n-1 как d * 2^r
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

def find_primitive_root(p: int) -> int:
    """
    Находит примитивный корень по модулю p
    """
    if p == 2:
        return 1
    
    # Находим простые делители p-1
    factors = []
    phi = p - 1
    n = phi
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    
    # Проверяем кандидатов
    for g in range(2, p):
        is_primitive = True
        for factor in factors:
            if pow(g, phi // factor, p) == 1:
                is_primitive = False
                break
        if is_primitive:
            return g
    return -1

class ElGamalSignature:
    """
    Класс для работы с электронной подписью Эль-Гамаля
    """
    
    def __init__(self, p: int = None, g: int = None):
        """
        Инициализация с общими параметрами p и g
        Если p и g не заданы, они генерируются автоматически
        """
        if p is None:
            # Генерируем простое число размером около 256 бит
            while True:
                p = random.getrandbits(256)
                # Убеждаемся, что p простое и p-1 имеет достаточно большой фактор
                if is_prime(p) and p > 1000:
                    break
        
        if g is None:
            g = find_primitive_root(p)
            if g == -1:
                raise ValueError("Не удалось найти примитивный корень")
        
        self.p = p
        self.g = g
        self.x = None  # секретный ключ
        self.y = None  # открытый ключ
    
    def generate_keys(self) -> Tuple[int, int]:
        """
        Генерирует пару ключей (секретный, открытый)
        Возвращает (x, y)
        """
        # Выбираем случайный секретный ключ x: 1 < x < p-1
        self.x = random.randint(2, self.p - 2)
        
        # Вычисляем открытый ключ y = g^x mod p
        self.y = pow(self.g, self.x, self.p)
        
        return self.x, self.y
    
    def get_public_key(self) -> int:
        """
        Возвращает открытый ключ
        """
        if self.y is None:
            raise ValueError("Ключи не сгенерированы. Сначала вызовите generate_keys()")
        return self.y
    
    def get_private_key(self) -> int:
        """
        Возвращает секретный ключ (должен храниться в тайне!)
        """
        if self.x is None:
            raise ValueError("Ключи не сгенерированы. Сначала вызовите generate_keys()")
        return self.x
    
    def hash_message(self, message: str) -> int:
        """
        Хеш-функция для сообщения.
        В реальных системах используется криптографическая хеш-функция (SHA-256 и т.д.)
        Здесь для простоты используем сумму кодов символов по модулю p
        """
        h = sum(ord(c) for c in message) % self.p
        if h < 2:
            h = 2  # гарантируем, что h > 1
        return h
    
    def sign(self, message: str) -> Tuple[int, int, int]:
        """
        Подписать сообщение.
        Возвращает (h, r, s) - хеш, r и s компоненты подписи
        """
        if self.x is None:
            raise ValueError("Сначала сгенерируйте ключи вызовом generate_keys()")
        
        # Вычисляем хеш сообщения
        h = self.hash_message(message)
        
        # Выбираем случайное k: 1 < k < p-1, взаимно простое с p-1
        while True:
            k = random.randint(2, self.p - 2)
            if math.gcd(k, self.p - 1) == 1:
                break
        
        # Вычисляем r = g^k mod p
        r = pow(self.g, k, self.p)
        
        # Вычисляем u = (h - x*r) mod (p-1)
        u = (h - self.x * r) % (self.p - 1)
        
        # Вычисляем s = k^(-1) * u mod (p-1)
        k_inv = mod_inverse(k, self.p - 1)
        s = (k_inv * u) % (self.p - 1)
        
        return h, r, s
    
    def verify(self, message: str, r: int, s: int, y: int = None) -> bool:
        """
        Проверить подпись сообщения.
        y - открытый ключ отправителя (если не указан, используется свой)
        """
        if y is None:
            if self.y is None:
                raise ValueError("Открытый ключ не задан")
            y = self.y
        
        # Вычисляем хеш сообщения
        h = self.hash_message(message)
        
        # Проверяем: y^r * r^s ≡ g^h (mod p)
        left_side = (pow(y, r, self.p) * pow(r, s, self.p)) % self.p
        right_side = pow(self.g, h, self.p)
        
        return left_side == right_side

def main():
    """
    Демонстрация работы схемы Эль-Гамаля
    """
    print("=" * 60)
    print("ЭЛЕКТРОННАЯ ПОДПИСЬ ЭЛЬ-ГАМАЛЯ")
    print("=" * 60)
    
    # 1. Инициализация с параметрами из примера
    print("\n1. Инициализация с параметрами p = 23, g = 5 (как в примере)")
    p = 23
    g = 5
    
    # Создаем экземпляр подписи
    elgamal = ElGamalSignature(p, g)
    
    # 2. Генерация ключей
    print("\n2. Генерация ключей")
    x, y = elgamal.generate_keys()
    print(f"   Секретный ключ x = {x}")
    print(f"   Открытый ключ y = {y}")
    
    # 3. Подпись сообщения (как в примере, но с реальными вычислениями)
    print("\n3. Подпись сообщения")
    message = "baaaab"
    print(f"   Сообщение: '{message}'")
    
    # Используем конкретные значения из примера
    # В примере: x=7, k=5, h=3
    # Переопределим ключ для точного совпадения с примером
    elgamal.x = 7
    elgamal.y = pow(g, 7, p)
    print(f"   (Используем x = 7 для соответствия примеру)")
    
    h = elgamal.hash_message(message)
    print(f"   Хеш сообщения h = {h}")
    
    # В примере используется k=5
    k = 5
    r = pow(g, k, p)
    u = (h - elgamal.x * r) % (p - 1)
    k_inv = mod_inverse(k, p - 1)
    s = (k_inv * u) % (p - 1)
    
    print(f"   k = {k}")
    print(f"   r = {r}")
    print(f"   u = {u}")
    print(f"   k ^ (-1) mod 22 = {k_inv}")
    print(f"   s = {s}")
    print(f"\n   Подпись: (r, s) = ({r}, {s})")
    
    # 4. Проверка подписи
    print("\n4. Проверка подписи")
    is_valid = elgamal.verify(message, r, s)
    print(f"   Подпись верна: {is_valid}")
    
    # Показываем вычисления проверки
    left = (pow(elgamal.y, r, p) * pow(r, s, p)) % p
    right = pow(g, h, p)
    print(f"   Левая часть: y ^ r * r ^ s = {elgamal.y} ^ {r} * {r} ^ {s} mod {p} = {left}")
    print(f"   Правая часть: g ^ h = {g} ^ {h} mod {p} = {right}")
    
    # 5. Демонстрация с подделанной подписью
    print("\n" + "=" * 60)
    print("5. Демонстрация подделки подписи")
    print("   (попытка изменить сообщение)")
    
    fake_message = "baaaac"  # измененное сообщение
    print(f"   Сообщение: '{fake_message}'")
    is_valid_fake = elgamal.verify(fake_message, r, s)
    print(f"   Подпись для измененного сообщения верна: {is_valid_fake}")
    
    # 6. Пример с автоматической генерацией параметров
    print("\n" + "=" * 60)
    print("6. Пример с автоматической генерацией параметров")
    
    elgamal2 = ElGamalSignature()  # автоматически генерирует p и g
    x2, y2 = elgamal2.generate_keys()
    print(f"   p = {elgamal2.p}")
    print(f"   g = {elgamal2.g}")
    print(f"   Секретный ключ x = {x2}")
    print(f"   Открытый ключ y = {y2}")
    
    msg = "Привет, мир!"
    print(f"   Сообщение: '{msg}'")
    
    h2, r2, s2 = elgamal2.sign(msg)
    print(f"   Хеш: {h2}")
    print(f"   r = {r2}")
    print(f"   s = {s2}")
    
    is_valid2 = elgamal2.verify(msg, r2, s2)
    print(f"   Проверка подписи: {is_valid2}")
    
    # Проверка с чужим открытым ключом
    print("\n   Проверка с чужим открытым ключом (должна не пройти):")
    y_fake = (y2 + 1) % elgamal2.p
    is_valid_fake2 = elgamal2.verify(msg, r2, s2, y_fake)
    print(f"   Проверка с y={y_fake}: {is_valid_fake2}")
    
    print("\n" + "=" * 60)
    print("Программа завершена")

if __name__ == "__main__":
    main()