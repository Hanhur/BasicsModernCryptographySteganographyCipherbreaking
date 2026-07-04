# Электронная подпись RSA
import random
import hashlib
import math

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (расширенный алгоритм Евклида,
#    проверка простоты, генерация простых чисел)
# ============================================================

def egcd(a, b):
    """Расширенный алгоритм Евклида.
       Возвращает (g, x, y), где g = gcd(a, b) и a * x + b * y = g."""
    if a == 0:
        return (b, 0, 1)
    else:
        g, x1, y1 = egcd(b % a, a)
        return (g, y1 - (b // a) * x1, x1)

def modinv(a, m):
    """Вычисляет обратное число к a по модулю m: a ^ (-1) mod m."""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception(f"Обратного элемента не существует: gcd({a}, {m}) = {g}")
    return x % m

def is_prime(n, k=10):
    """Тест Миллера-Рабина для проверки простоты числа."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проводим k раундов теста
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

def generate_prime(bits=8):
    """Генерирует простое число заданной битности."""
    while True:
        # Генерируем нечётное число
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # Ставим старший и младший биты в 1
        if is_prime(n):
            return n

def gcd(a, b):
    """Наибольший общий делитель."""
    while b:
        a, b = b, a % b
    return a

# ============================================================
# 2. КЛАСС RSA ПОДПИСИ
# ============================================================

class RSASignature:
    """
    Реализация электронной подписи RSA.
    В точности соответствует описанию из текста.
    """
    
    def __init__(self, bits = 8):
        """
        Инициализация: генерация ключей.
        bits - битность простых чисел P и Q.
        """
        # Выбираем два больших простых числа P и Q
        self.P = generate_prime(bits)
        self.Q = generate_prime(bits)
        while self.P == self.Q:  # Чтобы P и Q были разные
            self.Q = generate_prime(bits)
        
        # Вычисляем N = P * Q
        self.N = self.P * self.Q
        
        # Вычисляем φ = (P-1) * (Q-1)
        self.phi = (self.P - 1) * (self.Q - 1)
        
        # Выбираем d, взаимно простое с φ
        self.d = self._choose_d()
        
        # Вычисляем c = d^(-1) mod φ (секретный ключ)
        self.c = modinv(self.d, self.phi)
        
        print(f"[Генерация ключей]")
        print(f"  P = {self.P}, Q = {self.Q}")
        print(f"  N = {self.N}")
        print(f"  φ = {self.phi}")
        print(f"  d (открытый) = {self.d}")
        print(f"  c (секретный) = {self.c}")
        print()
    
    def _choose_d(self):
        """Выбирает d, взаимно простое с φ."""
        # Начинаем с 3 и увеличиваем, пока не найдём взаимно простое
        d = 3
        while gcd(d, self.phi) != 1:
            d += 1
            if d >= self.phi:
                raise Exception("Не удалось найти d")
        return d
    
    def hash_message(self, message):
        """
        Вычисляет хеш-функцию от сообщения.
        В тексте используется абстрактная h(m1,...,mn).
        Здесь используем SHA-256 и приводим к числу, 
        меньшему N (как в примере, где y = 13).
        """
        # Вычисляем SHA-256 хеш
        h = hashlib.sha256(message.encode('utf-8')).hexdigest()
        # Переводим в число и берём по модулю N
        y = int(h, 16) % self.N
        # Гарантируем, что y > 1 (для безопасности)
        if y < 2:
            y += 2
        return y
    
    def sign(self, message):
        """
        Подписывает сообщение.
        s = y^c mod N, где y = h(message)
        Возвращает подпись s.
        """
        y = self.hash_message(message)
        s = pow(y, self.c, self.N)
        print(f"[Подписание]")
        print(f"  Сообщение: {message}")
        print(f"  y = h(message) = {y}")
        print(f"  s = y ^ c mod N = {y} ^ {self.c} mod {self.N} = {s}")
        print()
        return s
    
    def verify(self, message, signature):
        """
        Проверяет подпись.
        w = s ^ d mod N
        Возвращает True, если w == h(message), иначе False.
        """
        y = self.hash_message(message)
        w = pow(signature, self.d, self.N)
        
        print(f"[Проверка подписи]")
        print(f"  Сообщение: {message}")
        print(f"  y = h(message) = {y}")
        print(f"  w = s ^ d mod N = {signature} ^ {self.d} mod {self.N} = {w}")
        print(f"  Результат: {'✓ ПОДПИСЬ ВЕРНА' if w == y else '✗ ПОДПИСЬ НЕВЕРНА'}")
        print()
        return w == y


# ============================================================
# 3. ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================

def demo_from_text():
    """
    Демонстрация в точности по примеру из текста:
    P = 5, Q = 11, N = 55, d = 3, c = 27.
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПО ПРИМЕРУ ИЗ ТЕКСТА")
    print("=" * 60)
    print()
    
    # Создаём объект с заданными параметрами (ручная установка)
    rsa = RSASignature(bits = 4)  # Будет сгенерировано случайно, но мы переопределим
    
    # Переопределяем параметры как в тексте
    rsa.P = 5
    rsa.Q = 11
    rsa.N = 55
    rsa.phi = 40
    rsa.d = 3
    rsa.c = 27  # 3^(-1) mod 40 = 27
    
    print("Параметры (как в тексте):")
    print(f"  P = 5, Q = 11, N = 55, φ = 40")
    print(f"  d = 3, c = 27")
    print()
    
    # Сообщение из примера
    message = "abbbaa"
    
    # Хеш-функция для демонстрации — в тексте сказано, что h(abbbaa) = 13
    # Переопределяем метод, чтобы он возвращал 13 для этого сообщения
    original_hash = rsa.hash_message
    
    def custom_hash(msg):
        if msg == "abbbaa":
            return 13
        return original_hash(msg)
    
    rsa.hash_message = custom_hash
    
    # Подписываем
    signature = rsa.sign(message)  # Должно быть 7
    
    # Проверяем
    rsa.verify(message, signature)
    
    # Показываем, что подпись не подходит для другого сообщения
    print("Проверка подписи на другом сообщении:")
    rsa.verify("abbbab", signature)


def demo_random_keys():
    """
    Демонстрация с генерацией случайных ключей.
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ СО СЛУЧАЙНЫМИ КЛЮЧАМИ")
    print("=" * 60)
    print()
    
    # Генерируем ключи (8-битные простые числа для наглядности)
    rsa = RSASignature(bits = 8)
    
    # Сообщение
    message = "Привет, мир! Это тестовое сообщение для RSA подписи."
    
    # Подписываем
    signature = rsa.sign(message)
    
    # Проверяем (должно быть успешно)
    rsa.verify(message, signature)
    
    # Проверяем с изменённым сообщением (должно быть неуспешно)
    print("Проверка с ИЗМЕНЁННЫМ сообщением:")
    rsa.verify(message + " (изменено)", signature)


def demo_attack_impossible():
    """
    Демонстрация того, что подделать подпись невозможно
    без знания секретного ключа c.
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ НЕВОЗМОЖНОСТИ ПОДДЕЛКИ")
    print("=" * 60)
    print()
    
    rsa = RSASignature(bits = 8)
    message = "Важный контракт"
    
    # Алиса подписывает
    signature = rsa.sign(message)
    print(f"Алиса подписала сообщение: {message}")
    print(f"Подпись: {signature}")
    print()
    
    # Злоумышленник пытается подделать подпись для другого сообщения
    fake_message = "Поддельный контракт"
    
    # Он не знает c, поэтому просто подбирает случайное число
    fake_signature = random.randint(2, rsa.N - 1)
    
    print(f"Злоумышленник пытается подписать: {fake_message}")
    print(f"Случайная подпись: {fake_signature}")
    
    # Проверка показывает, что подпись неверна
    rsa.verify(fake_message, fake_signature)


# ============================================================
# 4. ЗАПУСК ВСЕХ ДЕМОНСТРАЦИЙ
# ============================================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запускаем все демонстрации
    demo_from_text()
    print("\n" + "=" * 60 + "\n")
    
    demo_random_keys()
    print("\n" + "=" * 60 + "\n")
    
    demo_attack_impossible()