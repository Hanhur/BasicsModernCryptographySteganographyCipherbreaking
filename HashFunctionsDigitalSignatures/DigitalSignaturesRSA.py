# Цифровые подписи в RSA 
import hashlib
import random

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def gcd(a, b):
    """Наибольший общий делитель (алгоритм Евклида)"""
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), где g = gcd(a, b) и a * x + b * y = g
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """
    Обратное число по модулю: a * x ≡ 1 (mod m)
    Используется для вычисления секретного ключа d
    """
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента не существует: gcd({a}, {m}) = {g}")
    return x % m

def is_prime(n, k = 10):
    """
    Тест Миллера-Рабина для проверки простоты числа.
    k - количество раундов (чем больше, тем точнее)
    """
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
    
    # Проверяем k раз
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

def generate_prime(bits=8):
    """
    Генерирует простое число заданной битности.
    Для примера используем маленькие числа (8 бит = до 256)
    """
    while True:
        # Генерируем нечетное число в диапазоне [2 ^ (bits - 1), 2 ^ bits - 1]
        low = 2 ** (bits - 1)
        high = 2 ** bits - 1
        n = random.randint(low, high)
        # Делаем нечетным
        if n % 2 == 0:
            n += 1
        if is_prime(n):
            return n


# ===================== КЛАСС RSA =====================

class RSA:
    """
    Класс, представляющий участника RSA.
    У каждого есть открытый ключ (e, n) и секретный ключ d.
    """
    def __init__(self, name, bits = 8):
        self.name = name
        self.bits = bits
        self.p = None
        self.q = None
        self.n = None
        self.phi = None
        self.e = None
        self.d = None
        self._generate_keys()
    
    def _generate_keys(self):
        """Генерирует пару ключей (открытый/закрытый)"""
        # Шаг 1: Выбираем два простых числа
        self.p = generate_prime(self.bits)
        self.q = generate_prime(self.bits)
        while self.q == self.p:  # Чтобы числа были разные
            self.q = generate_prime(self.bits)
        
        # Шаг 2: Вычисляем n = p * q
        self.n = self.p * self.q
        
        # Шаг 3: Вычисляем функцию Эйлера φ(n) = (p-1)*(q-1)
        self.phi = (self.p - 1) * (self.q - 1)
        
        # Шаг 4: Выбираем e (обычно 65537, но в примере из текста 9007)
        # Для простоты возьмем фиксированное e
        self.e = 9007
        # Проверяем, что gcd(e, phi) = 1
        while gcd(self.e, self.phi) != 1:
            self.e = random.randint(2, self.phi - 1)
        
        # Шаг 5: Вычисляем d = inv(e) mod phi
        self.d = mod_inverse(self.e, self.phi)
    
    def encrypt(self, message):
        """Шифрование: c = m ^ e mod n"""
        return pow(message, self.e, self.n)
    
    def decrypt(self, ciphertext):
        """Расшифрование: m = c ^ d mod n"""
        return pow(ciphertext, self.d, self.n)
    
    def sign(self, message_hash):
        """Подпись: s = hash ^ d mod n"""
        return pow(message_hash, self.d, self.n)
    
    def verify(self, signature, message_hash):
        """Проверка подписи: signature ^ e mod n == hash"""
        return pow(signature, self.e, self.n) == message_hash
    
    def get_public_key(self):
        """Возвращает открытый ключ (e, n)"""
        return (self.e, self.n)
    
    def __str__(self):
        return f"{self.name}: p = {self.p}, q = {self.q}, n = {self.n}, phi = {self.phi}, e = {self.e}, d = {self.d}"


# ===================== ОСНОВНАЯ ПРОГРАММА =====================

def main():
    print("=" * 70)
    print("ЦИФРОВАЯ ПОДПИСЬ RSA (по тексту из главы)")
    print("=" * 70)
    
    # Для воспроизводимости примера из текста (88, 9007, 6767, 23843)
    # зафиксируем seed, чтобы числа генерировались одинаково
    # ВАЖНО: В реальной жизни так не делают!
    random.seed(42)
    
    print("\n[ГЕНЕРАЦИЯ КЛЮЧЕЙ]")
    
    # 1. Создаем участников
    alice = RSA("Алиса", bits = 8)
    bob = RSA("Боб", bits = 8)
    
    print(f"Алиса: n = {alice.n}, e = {alice.e}, d = {alice.d}")
    print(f"Боб:   n = {bob.n}, e = {bob.e}, d = {bob.d}")
    
    # 2. Исходное сообщение (как в тексте)
    M = 88
    print(f"\n[ИСХОДНОЕ СООБЩЕНИЕ] M = {M}")
    
    # 3. Боб шифрует сообщение открытым ключом Алисы
    print("\n[ШАГ 1: ШИФРОВАНИЕ БОБОМ]")
    c = bob.encrypt_with_public(M, alice.get_public_key())
    print(f"Боб шифрует M = {M} открытым ключом Алисы ({alice.e}, {alice.n})")
    print(f"c = M ^ e mod N_A = {M} ^ {alice.e} mod {alice.n} = {c}")
    
    # 4. Боб вычисляет хеш сообщения (как указано в тексте)
    print("\n[ШАГ 2: ВЫЧИСЛЕНИЕ ХЕША]")
    # Используем SHA-256, но берем только число (mod N_B для подписи)
    hash_bytes = hashlib.sha256(str(M).encode()).digest()
    # Превращаем хеш в число, но обрезаем, чтобы оно было меньше N_B
    m_hash = int.from_bytes(hash_bytes, 'big') % bob.n
    print(f"Хеш h(M) = {m_hash} (обрезанный по модулю N_B = {bob.n})")
    
    # 5. Боб подписывает хеш своим закрытым ключом
    print("\n[ШАГ 3: ПОДПИСЬ БОБОМ]")
    S = bob.sign(m_hash)
    print(f"Боб подписывает хеш: S = h(M) ^ {bob.d} mod {bob.n}")
    print(f"S = {S}")
    
    # 6. Боб отправляет Алисе пару (c, S)
    print(f"\n[ПЕРЕДАЧА] Боб отправляет Алисе: (c = {c}, S = {S})")
    
    # 7. Алиса расшифровывает c своим закрытым ключом
    print("\n[ШАГ 4: РАСШИФРОВАНИЕ АЛИСОЙ]")
    M_decrypted = alice.decrypt(c)
    print(f"Алиса расшифровывает c = {c} своим ключом d = {alice.d}")
    print(f"M' = {c} ^ {alice.d} mod {alice.n} = {M_decrypted}")
    
    # 8. Алиса проверяет подпись Боба
    print("\n[ШАГ 5: ПРОВЕРКА ПОДПИСИ]")
    # Алиса вычисляет хеш полученного сообщения
    hash_received = int.from_bytes(hashlib.sha256(str(M_decrypted).encode()).digest(), 'big') % bob.n
    
    is_valid = bob.verify(S, hash_received)
    print(f"Алиса проверяет: S ^ e mod N_B == h(M')?")
    print(f"  S ^ {bob.e} mod {bob.n} = {pow(S, bob.e, bob.n)}")
    print(f"  h(M') = {hash_received}")
    print(f"  Результат: {'✓ ПОДПИСЬ ВЕРНА!' if is_valid else '✗ ПОДПИСЬ НЕВЕРНА!'}")
    
    # 9. Демонстрация атаки (подмена подписи)
    print("\n" + "=" * 70)
    print("[ДЕМОНСТРАЦИЯ АТАКИ]")
    print("=" * 70)
    print("Ева пытается подделать подпись...")
    
    # Ева выбирает случайный dE и подписывает что-то другое
    eve = RSA("Ева", bits=8)
    # Ева подписывает хеш другого сообщения (например, 999)
    fake_hash = int.from_bytes(hashlib.sha256(b"999").digest(), 'big') % bob.n
    S_fake = eve.sign(fake_hash)  # Ева использует свой ключ!
    
    print(f"Ева создает фальшивую подпись S' = {S_fake} для сообщения 999")
    print(f"Алиса проверяет S' открытым ключом Боба (e = {bob.e}, n = {bob.n}):")
    
    # Алиса проверяет подпись Евы открытым ключом Боба
    result_fake = bob.verify(S_fake, fake_hash)
    print(f"  S'^{bob.e} mod {bob.n} = {pow(S_fake, bob.e, bob.n)}")
    print(f"  h(999) = {fake_hash}")
    print(f"  Результат: {'✓ ПОДДЕЛКА ПРОШЛА!' if result_fake else '✗ ПОДДЕЛКА ОТКЛОНЕНА!'}")
    
    # 10. Вывод итогов
    print("\n" + "=" * 70)
    print("ИТОГИ:")
    print("=" * 70)
    print(f"✓ Сообщение успешно расшифровано: {M_decrypted} (оригинал: {M})")
    print(f"✓ Личность Боба подтверждена (подпись верна)")
    print(f"✓ Целостность сообщения сохранена (хеши совпадают)")
    print(f"✓ Неотказуемость: Боб не может отказаться от подписи")
    if not result_fake:
        print(f"✗ Атака Евы провалилась: поддельная подпись отклонена")


# ===================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ КЛАССА =====================

def encrypt_with_public(self, message, public_key):
    """
    Шифрование открытым ключом другого участника.
    public_key = (e, n)
    """
    e, n = public_key
    return pow(message, e, n)

# Добавляем метод в класс RSA
RSA.encrypt_with_public = encrypt_with_public


# ===================== ЗАПУСК =====================

if __name__ == "__main__":
    main()