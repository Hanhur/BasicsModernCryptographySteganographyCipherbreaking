# Аутентификация и цифровые подписи 
import hashlib
import random
import math
from typing import Tuple, Optional, List

# ==============================================
# 1. ВСПОМОГАТЕЛЬНЫЕ МАТЕМАТИЧЕСКИЕ ФУНКЦИИ
# ==============================================

def gcd(a: int, b: int) -> int:
    """Алгоритм Евклида для НОД"""
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), где a * x + b * y = g = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a: int, m: int) -> int:
    """
    Вычисляет обратное число по модулю m: a ^ (-1) mod m
    """
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    return x % m

def is_prime(n: int, k: int = 10) -> bool:
    """
    Тест Миллера-Рабина для проверки простоты числа
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Представляем n-1 как d * 2^s
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

def generate_prime(bits: int = 8) -> int:
    """
    Генерирует простое число заданной битности
    """
    while True:
        # Генерируем нечетное число
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # Старший и младший биты = 1
        if is_prime(n):
            return n

# ==============================================
# 2. КЛАССЫ И АЛГОРИТМЫ RSA
# ==============================================

class RSAKeyPair:
    """Пара ключей RSA: (public_key, private_key)"""
    
    def __init__(self, bits: int = 16):
        """
        Генерирует новую пару ключей RSA
        
        Args:
            bits: Размерность ключа в битах (для демонстрации используем 16 бит)
        """
        self.bits = bits
        
        # Шаг 1: Выбираем два простых числа p и q
        p = generate_prime(bits // 2)
        q = generate_prime(bits // 2)
        while p == q:  # Чтобы p и q были разными
            q = generate_prime(bits // 2)
        
        # Шаг 2: Вычисляем n = p * q
        self.n = p * q
        
        # Шаг 3: Вычисляем функцию Эйлера φ(n) = (p-1)*(q-1)
        phi = (p - 1) * (q - 1)
        
        # Шаг 4: Выбираем открытую экспоненту e (обычно 65537 или 17)
        self.e = 17
        while gcd(self.e, phi) != 1:
            self.e += 2
        
        # Шаг 5: Вычисляем закрытую экспоненту d: e*d ≡ 1 (mod phi)
        self.d = mod_inverse(self.e, phi)
        
        # Открытый ключ: (e, n), Закрытый ключ: (d, n)
        print(f"Сгенерированы ключи RSA ({bits} бит)")
        print(f"  p = {p}, q = {q}, n = {self.n}")
        print(f"  e = {self.e}, d = {self.d}")
    
    def get_public_key(self) -> Tuple[int, int]:
        """Возвращает открытый ключ (e, n)"""
        return (self.e, self.n)
    
    def get_private_key(self) -> Tuple[int, int]:
        """Возвращает закрытый ключ (d, n)"""
        return (self.d, self.n)
    
    def get_max_block_size(self) -> int:
        """Возвращает максимальный размер блока в байтах для шифрования"""
        return (self.n.bit_length() - 1) // 8

def rsa_encrypt(message: int, public_key: Tuple[int, int]) -> int:
    """
    Шифрование RSA: c = m ^ e mod n
    
    Args:
        message: Числовое сообщение (должно быть меньше n)
        public_key: (e, n)
    """
    e, n = public_key
    if message >= n:
        raise ValueError(f"Сообщение {message} больше модуля n = {n}")
    return pow(message, e, n)

def rsa_decrypt(ciphertext: int, private_key: Tuple[int, int]) -> int:
    """
    Расшифрование RSA: m = c ^ d mod n
    
    Args:
        ciphertext: Зашифрованное число
        private_key: (d, n)
    """
    d, n = private_key
    return pow(ciphertext, d, n)

# ==============================================
# 3. ФУНКЦИИ ДЛЯ РАБОТЫ С ТЕКСТОМ И ХЕШАМИ
# ==============================================

def text_to_int(text: str) -> int:
    """Преобразует текст в число (для шифрования)"""
    return int.from_bytes(text.encode('utf-8'), byteorder = 'big')

def int_to_text(num: int) -> str:
    """Преобразует число обратно в текст"""
    try:
        return num.to_bytes((num.bit_length() + 7) // 8, byteorder = 'big').decode('utf-8')
    except:
        return str(num)

def split_text_to_blocks(text: str, block_size: int) -> List[int]:
    """
    Разбивает текст на блоки фиксированного размера и преобразует в числа
    
    Args:
        text: Исходный текст
        block_size: Максимальный размер блока в байтах
    
    Returns:
        Список чисел, каждое < 2 ^ (block_size*8)
    """
    text_bytes = text.encode('utf-8')
    blocks = []
    
    for i in range(0, len(text_bytes), block_size):
        block_bytes = text_bytes[i:i + block_size]
        block_int = int.from_bytes(block_bytes, byteorder = 'big')
        blocks.append(block_int)
    
    return blocks

def join_blocks_to_text(blocks: List[int], block_size: int) -> str:
    """
    Объединяет числовые блоки обратно в текст
    
    Args:
        blocks: Список чисел
        block_size: Размер блока в байтах
    
    Returns:
        Восстановленный текст
    """
    text_bytes = b''
    for block in blocks:
        # Преобразуем число в байты с фиксированной длиной
        block_bytes = block.to_bytes(block_size, byteorder = 'big')
        text_bytes += block_bytes
    
    # Удаляем возможные нулевые байты в конце (из-за padding)
    return text_bytes.decode('utf-8').rstrip('\x00')

def hash_message(message: str) -> int:
    """
    Вычисляет хеш сообщения с помощью SHA-256
    Возвращает число, меньшее 2^256
    """
    hash_bytes = hashlib.sha256(message.encode('utf-8')).digest()
    return int.from_bytes(hash_bytes, byteorder = 'big')

def hash_to_fit_modulus(hash_value: int, modulus: int) -> int:
    """
    Обрезает хеш до размера модуля n
    Это упрощенный подход для демонстрации (в реальности используется PSS)
    """
    # Берем хеш по модулю n, но гарантируем, что результат < n
    return hash_value % modulus

def sign_message(message: str, private_key: Tuple[int, int]) -> int:
    """
    Создает цифровую подпись для сообщения
    Алгоритм: подпись = hash(message) ^ d mod n
    
    Args:
        message: Исходное сообщение
        private_key: (d, n) - закрытый ключ отправителя
    
    Returns:
        Цифровая подпись (число)
    """
    d, n = private_key
    
    # Шаг 1: Вычисляем хеш сообщения
    message_hash = hash_message(message)
    
    # Шаг 2: Обрезаем хеш до размера модуля
    hash_fitted = hash_to_fit_modulus(message_hash, n)
    
    # Шаг 3: Шифруем обрезанный хеш закрытым ключом (это и есть подпись)
    signature = pow(hash_fitted, d, n)
    
    return signature

def verify_signature(message: str, signature: int, public_key: Tuple[int, int]) -> bool:
    """
    Проверяет цифровую подпись
    
    Args:
        message: Исходное сообщение
        signature: Цифровая подпись (число)
        public_key: (e, n) - открытый ключ отправителя
    
    Returns:
        True, если подпись верна, иначе False
    """
    e, n = public_key
    
    # Шаг 1: Расшифровываем подпись открытым ключом
    decrypted_hash = pow(signature, e, n)
    
    # Шаг 2: Вычисляем хеш полученного сообщения и обрезаем его
    current_hash = hash_message(message)
    current_hash_fitted = hash_to_fit_modulus(current_hash, n)
    
    # Шаг 3: Сравниваем хеши
    return decrypted_hash == current_hash_fitted

# ==============================================
# 4. ОСНОВНОЙ КЛИЕНТСКИЙ КЛАСС
# ==============================================

class SecureMessenger:
    """
    Безопасный мессенджер с аутентификацией и цифровыми подписями
    Реализует протокол: Подписать своим → Зашифровать чужим
    """
    
    def __init__(self, name: str, bits: int = 16):
        """
        Инициализация пользователя
        
        Args:
            name: Имя пользователя (Алиса, Боб и т.д.)
            bits: Размер ключа в битах (для демонстрации)
        """
        self.name = name
        self.key_pair = RSAKeyPair(bits)
        self.public_key = self.key_pair.get_public_key()
        self.private_key = self.key_pair.get_private_key()
        self.max_block_size = self.key_pair.get_max_block_size()
        
        print(f"Пользователь {name} инициализирован")
        print(f"  Открытый ключ: {self.public_key}")
        print(f"  Закрытый ключ: {self.private_key}")
        print(f"  Макс. размер блока: {self.max_block_size} байт\n")
    
    def send_secure_message(self, message: str, recipient_public_key: Tuple[int, int]) -> Tuple[List[int], int, int]:
        """
        Отправляет защищенное сообщение получателю
        
        Протокол:
        1. Подписываем сообщение своим закрытым ключом
        2. Шифруем блоки сообщения открытым ключом получателя
        
        Args:
            message: Текст сообщения
            recipient_public_key: (e, n) открытый ключ получателя
        
        Returns:
            (encrypted_blocks, signature, n) для передачи
        """
        print(f"\n--- {self.name} отправляет сообщение ---")
        print(f"Исходное сообщение: '{message}'")
        
        # Шаг 1: Создаем цифровую подпись
        signature = sign_message(message, self.private_key)
        print(f"Создана подпись: {signature}")
        
        # Шаг 2: Разбиваем сообщение на блоки
        _, recipient_n = recipient_public_key
        block_size = (recipient_n.bit_length() - 1) // 8
        blocks = split_text_to_blocks(message, block_size)
        print(f"Разбито на {len(blocks)} блоков по {block_size} байт")
        
        # Шаг 3: Шифруем каждый блок открытым ключом получателя
        encrypted_blocks = []
        for i, block in enumerate(blocks):
            encrypted = rsa_encrypt(block, recipient_public_key)
            encrypted_blocks.append(encrypted)
            print(f"  Блок {i + 1}: {block} -> {encrypted}")
        
        # Шаг 4: Возвращаем зашифрованные блоки и подпись
        return encrypted_blocks, signature, self.public_key[1]
    
    def receive_secure_message(self, encrypted_blocks: List[int], signature: int, sender_n: int, sender_public_key: Tuple[int, int]) -> Optional[str]:
        """
        Принимает и проверяет защищенное сообщение
        
        Args:
            encrypted_blocks: Список зашифрованных блоков
            signature: Цифровая подпись отправителя
            sender_n: Модуль n отправителя (используется для восстановления полного ключа)
            sender_public_key: (e, n) открытый ключ отправителя
        
        Returns:
            Расшифрованное сообщение или None при ошибке
        """
        print(f"\n--- {self.name} получает сообщение ---")
        
        # Шаг 1: Расшифровываем каждый блок своим закрытым ключом
        decrypted_blocks = []
        block_size = (self.public_key[1].bit_length() - 1) // 8
        
        try:
            for i, encrypted in enumerate(encrypted_blocks):
                decrypted = rsa_decrypt(encrypted, self.private_key)
                decrypted_blocks.append(decrypted)
                print(f"  Блок {i + 1}: {encrypted} -> {decrypted}")
        except Exception as e:
            print(f"Ошибка расшифрования: {e}")
            return None
        
        # Шаг 2: Объединяем блоки в текст
        try:
            decrypted_message = join_blocks_to_text(decrypted_blocks, block_size)
            print(f"Расшифрованное сообщение: '{decrypted_message}'")
        except Exception as e:
            print(f"Ошибка преобразования: {e}")
            return None
        
        # Шаг 3: Проверяем подпись
        is_valid = verify_signature(decrypted_message, signature, sender_public_key)
        
        if is_valid:
            print("✅ ПОДПИСЬ ВЕРНА! Аутентификация и целостность подтверждены.")
            print(f"   Сообщение отправлено владельцем ключа {sender_public_key}")
            return decrypted_message
        else:
            print("❌ ПОДПИСЬ НЕВЕРНА! Сообщение было изменено или подделано.")
            return None

# ==============================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ
# ==============================================

def demo_secure_communication():
    """Демонстрирует безопасный обмен сообщениями между Алисой и Бобом"""
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ БЕЗОПАСНОЙ ПЕРЕДАЧИ СООБЩЕНИЙ")
    print("=" * 60)
    
    # Создаем пользователей с 16-битными ключами (достаточно для демонстрации)
    print("\n1. ГЕНЕРАЦИЯ КЛЮЧЕЙ")
    print("-" * 40)
    alice = SecureMessenger("Алиса", bits = 16)
    bob = SecureMessenger("Боб", bits = 16)
    
    # Отправляем сообщение от Алисы к Бобу
    print("\n2. ОТПРАВКА СООБЩЕНИЯ")
    print("-" * 40)
    original_message = "Привет, Боб!"
    
    # Алиса отправляет
    enc_blocks, signature, alice_n = alice.send_secure_message(
        original_message, 
        bob.public_key
    )
    
    # Боб получает
    print("\n3. ПРИЕМ И ПРОВЕРКА")
    print("-" * 40)
    received = bob.receive_secure_message(
        enc_blocks, 
        signature, 
        alice_n,
        alice.public_key
    )
    
    # Проверяем, что сообщение не изменилось
    print("\n4. РЕЗУЛЬТАТ")
    print("-" * 40)
    if received == original_message:
        print("✅ УСПЕХ! Сообщение доставлено без изменений!")
    else:
        print("❌ ОШИБКА! Сообщение было изменено!")
    
    # ===== ДЕМОНСТРАЦИЯ АТАКИ =====
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АТАКИ (подделка сообщения)")
    print("=" * 60)
    
    # Злоумышленник перехватывает и изменяет сообщение
    print("\nЗлоумышленник перехватил сообщение и изменил его...")
    tampered_blocks = enc_blocks.copy()
    tampered_blocks[0] = tampered_blocks[0] + 1  # Изменяем первый блок
    
    print("\nБоб пытается расшифровать измененное сообщение:")
    bad_received = bob.receive_secure_message(
        tampered_blocks,
        signature,
        alice_n,
        alice.public_key
    )
    
    if bad_received is None:
        print("✅ Атака обнаружена! Подпись не совпала.")
    
    # ===== ДЕМОНСТРАЦИЯ ПЕРЕХВАТА =====
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОБЛЕМЫ ШПИОНАЖА (перехват без ключа)")
    print("=" * 60)
    
    print("\nЗлоумышленник перехватил зашифрованное сообщение:")
    print(f"  Зашифрованные блоки: {enc_blocks}")
    print(f"  Подпись: {signature}")
    print("Без закрытого ключа Боба расшифровать невозможно!")

def demo_long_message():
    """Демонстрирует отправку длинного сообщения с разбивкой на блоки"""
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ДЛИННОГО СООБЩЕНИЯ")
    print("=" * 60)
    
    # Создаем пользователей с 32-битными ключами
    alice = SecureMessenger("Алиса", bits = 32)
    bob = SecureMessenger("Боб", bits = 32)
    
    # Длинное сообщение
    long_message = "Привет, Боб! Это очень длинное секретное сообщение, которое нужно разбить на несколько блоков для шифрования."
    
    print(f"\nДлина сообщения: {len(long_message)} символов")
    
    # Отправляем
    enc_blocks, signature, _ = alice.send_secure_message(long_message, bob.public_key)
    
    # Получаем
    received = bob.receive_secure_message(enc_blocks, signature, alice.public_key[1], alice.public_key)
    
    if received == long_message:
        print("\n✅ Длинное сообщение успешно передано!")
    else:
        print("\n❌ Ошибка при передаче длинного сообщения!")

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запускаем основную демонстрацию
    demo_secure_communication()
    
    # Дополнительная демонстрация с длинным сообщением
    demo_long_message()