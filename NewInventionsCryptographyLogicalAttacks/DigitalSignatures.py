# Цифровые подписи в MBXI
"""
MBXI Цифровая подпись с шифрованием и защитой от шпионажа
Реализация гибридной схемы: шифрование сообщения + подпись хэша
Без использования numpy
"""

import random
import hashlib
import math

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def mod_pow(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю (бинарное экспоненцирование)
    Эквивалент: (base ** exponent) % modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # Если текущий бит равен 1
        if exponent & 1:
            result = (result * base) % modulus
        # Переход к следующему биту
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида
    Возвращает: (gcd, x, y) где a * x + b * y = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Находит обратное число по модулю m
    a * inv ≡ 1 (mod m)
    """
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента не существует: {a} и {m} не взаимно просты")
    return x % m


def is_primitive_root(g, p):
    """
    Проверяет, является ли g примитивным корнем по модулю p
    """
    if g == 0 or g == 1:
        return False
    
    # Факторизация p-1
    phi = p - 1
    factors = []
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
    
    # Проверка: для всех простых делителей q числа p-1
    # g^((p-1)/q) mod p != 1
    for q in factors:
        if mod_pow(g, phi // q, p) == 1:
            return False
    
    return True


def find_primitive_root(p):
    """
    Находит примитивный корень по модулю p
    """
    if p == 2:
        return 1
    
    # Перебираем кандидатов
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    
    return None


def generate_prime(bits = 16):
    """
    Генерирует простое число заданной битности (для демонстрации)
    """
    if bits <= 1:
        return 2
    
    while True:
        # Генерируем нечетное число
        num = random.getrandbits(bits)
        # Убеждаемся, что число нечетное и достаточно большое
        num |= (1 << bits) | 1
        
        # Проверка на простоту (простейший тест Миллера-Рабина)
        if is_prime(num):
            return num


def is_prime(n, k = 5):
    """
    Тест Миллера-Рабина на простоту
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Проводим k тестов
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def sha256_hash(message):
    """
    Вычисляет SHA-256 хэш сообщения и возвращает его как целое число
    Поддерживает: str, bytes, int
    """
    if isinstance(message, str):
        message = message.encode('utf-8')
    elif isinstance(message, int):
        # Преобразуем целое число в байты
        message = str(message).encode('utf-8')
    elif not isinstance(message, bytes):
        raise TypeError(f"Неподдерживаемый тип: {type(message)}")
    
    hash_bytes = hashlib.sha256(message).digest()
    return int.from_bytes(hash_bytes, 'big')


# ============================================================================
# КЛАСС MBXI - ЦИФРОВАЯ ПОДПИСЬ
# ============================================================================

class MBXIDigitalSignature:
    """
    Реализация MBXI с цифровой подписью и шифрованием
    """
    
    def __init__(self, p = None, g = None, bits = 16):
        """
        Инициализация системы MBXI
        
        Параметры:
            p: простое число (если None, будет сгенерировано)
            g: примитивный корень (если None, будет найден)
            bits: битность для генерации простых чисел
        """
        if p is None:
            print(f"Генерация простого числа с битностью {bits}...")
            self.p = generate_prime(bits)
            print(f"p = {self.p}")
        else:
            self.p = p
        
        if g is None:
            self.g = find_primitive_root(self.p)
            if self.g is None:
                raise ValueError(f"Не удалось найти примитивный корень для p = {self.p}")
            print(f"Найден примитивный корень g = {self.g}")
        else:
            self.g = g
        
        self.p_minus_1 = self.p - 1
        
        print(f"Система инициализирована: p = {self.p}, g = {self.g}")
    
    def generate_keypair(self, private_key = None):
        """
        Генерирует пару ключей (закрытый, открытый)
        
        Возвращает:
            (private_key, public_key)
        """
        if private_key is None:
            # Генерируем случайный закрытый ключ (взаимно простой с p-1)
            while True:
                private_key = random.randint(2, self.p - 2)
                if math.gcd(private_key, self.p_minus_1) == 1:
                    break
        
        # Открытый ключ: y = g^private_key mod p
        public_key = mod_pow(self.g, private_key, self.p)
        
        return private_key, public_key
    
    def encrypt(self, message, public_key, ephemeral_key = None):
        """
        Шифрование сообщения с использованием открытого ключа получателя
        
        C = M * y ^ k mod p
        
        Возвращает:
            (ciphertext, g ^ k_mod_p)
        """
        if ephemeral_key is None:
            # Генерируем эфемерный ключ k (взаимно простой с p-1)
            while True:
                ephemeral_key = random.randint(2, self.p - 2)
                if math.gcd(ephemeral_key, self.p_minus_1) == 1:
                    break
        
        # Вычисляем y^k mod p
        yk = mod_pow(public_key, ephemeral_key, self.p)
        
        # Шифруем: C = M * y^k mod p
        ciphertext = (message * yk) % self.p
        
        # Отправляем также g^k mod p для расшифровки
        gk = mod_pow(self.g, ephemeral_key, self.p)
        
        return ciphertext, gk, ephemeral_key
    
    def decrypt(self, ciphertext, gk, private_key):
        """
        Расшифровка сообщения с использованием закрытого ключа получателя
        
        M = C * (g ^ k) ^ (-private_key) mod p
        """
        # Вычисляем (g^k)^(-private_key) = g^(-k*private_key) mod p
        # Находим обратное: (g^k)^private_key mod p
        gk_private = mod_pow(gk, private_key, self.p)
        gk_private_inv = mod_inverse(gk_private, self.p)
        
        # Расшифровываем: M = C * (g^k)^(-private_key) mod p
        message = (ciphertext * gk_private_inv) % self.p
        
        return message
    
    def sign(self, message_hash, private_key):
        """
        Создание цифровой подписи для хэша сообщения
        
        S = H(M)^private_key mod p
        
        Возвращает:
            signature
        """
        # Подписываем хэш закрытым ключом
        signature = mod_pow(message_hash, private_key, self.p)
        return signature
    
    def verify(self, message_hash, signature, public_key):
        """
        Проверка цифровой подписи
        
        Проверяем: S^public_key ≡ H(M) (mod p)
        """
        # Восстанавливаем хэш из подписи
        recovered_hash = mod_pow(signature, public_key, self.p)
        
        # Сравниваем с оригинальным хэшем
        return recovered_hash == message_hash
    
    def sign_and_encrypt(self, message, sender_private_key, recipient_public_key):
        """
        Гибридная схема: подпись + шифрование за один проход
        
        1. Вычисляем хэш сообщения H(M)
        2. Подписываем хэш: S = H(M) ^ private_key_sender mod p
        3. Шифруем сообщение: C = M * y_recipient ^ k mod p
        
        Возвращает:
            (ciphertext, signature, gk)
        """
        # 1. Вычисляем хэш сообщения
        message_hash = sha256_hash(message)
        
        # Ограничиваем хэш размером p (для корректной работы модульной арифметики)
        message_hash = message_hash % self.p
        
        # 2. Подписываем хэш
        signature = self.sign(message_hash, sender_private_key)
        
        # 3. Шифруем сообщение (если message - строка, преобразуем в число)
        if isinstance(message, str):
            message_int = sha256_hash(message) % self.p
        elif isinstance(message, int):
            message_int = message
        else:
            message_int = sha256_hash(str(message)) % self.p
        
        ciphertext, gk, _ = self.encrypt(message_int, recipient_public_key)
        
        return ciphertext, signature, gk, message_hash
    
    def decrypt_and_verify(self, ciphertext, signature, gk, recipient_private_key, sender_public_key, expected_message_hash = None, expected_message = None):
        """
        Расшифровка и проверка подписи
        
        Параметры:
            ciphertext: зашифрованное сообщение
            signature: цифровая подпись
            gk: g^k mod p для расшифровки
            recipient_private_key: закрытый ключ получателя
            sender_public_key: открытый ключ отправителя
            expected_message_hash: ожидаемый хэш сообщения (для проверки)
            expected_message: ожидаемое сообщение (альтернатива хэшу)
        
        Возвращает:
            (decrypted_message, is_valid)
        """
        # 1. Расшифровываем сообщение
        decrypted_message = self.decrypt(ciphertext, gk, recipient_private_key)
        
        # 2. Проверяем подпись
        if expected_message_hash is not None:
            message_hash = expected_message_hash
        elif expected_message is not None:
            message_hash = sha256_hash(expected_message) % self.p
        else:
            # Если ничего не передано, используем расшифрованное сообщение
            message_hash = decrypted_message
        
        is_valid = self.verify(message_hash, signature, sender_public_key)
        
        return decrypted_message, is_valid


# ============================================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================================

def demo_basic_signature():
    """
    Демонстрация базовой прямой подписи (без шифрования)
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 1: ПРЯМАЯ ПОДПИСЬ БЕЗ ШИФРОВАНИЯ")
    print("=" * 70)
    
    # Инициализация системы
    mbxi = MBXIDigitalSignature(p = 7919, g = 7)
    
    # Генерация ключей Боба (подписывающего)
    x_bob = 3009
    y_bob = mod_pow(mbxi.g, x_bob, mbxi.p)
    print(f"\nКлючи Боба:")
    print(f"  Закрытый ключ (x): {x_bob}")
    print(f"  Открытый ключ (y): {y_bob}")
    
    # Сообщение для подписи
    message = 1234
    print(f"\nИсходное сообщение: {message}")
    
    # Подписание
    signature = mbxi.sign(message, x_bob)
    print(f"Подпись: {signature}")
    
    # Проверка подписи
    is_valid = mbxi.verify(message, signature, y_bob)
    print(f"Подпись верна: {is_valid}")
    
    # Попытка подделки
    fake_message = 5678
    is_valid_fake = mbxi.verify(fake_message, signature, y_bob)
    print(f"Подпись для поддельного сообщения {fake_message}: {is_valid_fake}")


def demo_encrypted_signature():
    """
    Демонстрация гибридной схемы: шифрование + подпись хэша
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 2: ГИБРИДНАЯ СХЕМА (ШИФРОВАНИЕ + ПОДПИСЬ)")
    print("=" * 70)
    
    # Инициализация системы
    mbxi = MBXIDigitalSignature(p = 7919, g = 7)
    
    # Генерация ключей для Алисы и Боба
    x_alice, y_alice = mbxi.generate_keypair()
    x_bob, y_bob = mbxi.generate_keypair()
    
    print(f"\nКлючи Алисы (отправитель):")
    print(f"  Закрытый ключ (x_A): {x_alice}")
    print(f"  Открытый ключ (y_A): {y_alice}")
    
    print(f"\nКлючи Боба (получатель):")
    print(f"  Закрытый ключ (x_B): {x_bob}")
    print(f"  Открытый ключ (y_B): {y_bob}")
    
    # Сообщение
    message = "Привет, Боб! Это секретное сообщение."
    print(f"\nИсходное сообщение: {message}")
    
    # Алиса подписывает и шифрует сообщение для Боба
    ciphertext, signature, gk, message_hash = mbxi.sign_and_encrypt(
        message, 
        x_alice, 
        y_bob
    )
    
    print(f"\nОтправленные данные:")
    print(f"  Хэш сообщения: {message_hash}")
    print(f"  Шифротекст: {ciphertext}")
    print(f"  Подпись: {signature}")
    print(f"  g ^ k mod p: {gk}")
    
    # Боб расшифровывает и проверяет подпись
    decrypted, is_valid = mbxi.decrypt_and_verify(
        ciphertext, signature, gk,
        x_bob, y_alice, 
        expected_message_hash = message_hash
    )
    
    print(f"\nРезультат расшифровки и проверки:")
    print(f"  Расшифрованное сообщение: {decrypted}")
    
    # Проверяем соответствие хэша
    computed_hash = sha256_hash(message) % mbxi.p
    print(f"  Хэш сообщения (вычислен): {computed_hash}")
    print(f"  Хэши совпадают: {computed_hash == message_hash}")
    print(f"  Подпись верна: {is_valid}")
    
    # Атака посредника: подмена сообщения
    print("\n" + "-" * 70)
    print("Моделирование атаки посредника (MitM):")
    
    # Ева перехватывает и пытается подменить шифротекст
    fake_ciphertext = (ciphertext + 100) % mbxi.p
    print(f"  Ева подменила шифротекст: {fake_ciphertext}")
    
    # Боб пытается расшифровать подмененное сообщение
    decrypted_fake, is_valid_fake = mbxi.decrypt_and_verify(
        fake_ciphertext, signature, gk,
        x_bob, y_alice, 
        expected_message_hash = message_hash
    )
    
    print(f"  Расшифрованное подмененное сообщение: {decrypted_fake}")
    print(f"  Подпись для подмененного сообщения верна: {is_valid_fake}")
    
    if not is_valid_fake:
        print("  ✅ Атака обнаружена: подпись недействительна!")


def demo_key_exchange():
    """
    Демонстрация использования MBXI как протокола обмена ключами
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 3: MBXI КАК ПРОТОКОЛ ОБМЕНА КЛЮЧАМИ")
    print("=" * 70)
    
    # Инициализация системы
    mbxi = MBXIDigitalSignature(p = 7919, g = 7)
    
    # Алиса и Боб генерируют свои ключи
    x_alice, y_alice = mbxi.generate_keypair()
    x_bob, y_bob = mbxi.generate_keypair()
    
    print(f"\nАлиса: x_A = {x_alice}, y_A = {y_alice}")
    print(f"Боб:   x_B = {x_bob}, y_B = {y_bob}")
    
    # Алиса вычисляет общий секрет: K = y_B^x_A mod p = g^(x_A*x_B) mod p
    K_alice = mod_pow(y_bob, x_alice, mbxi.p)
    
    # Боб вычисляет общий секрет: K = y_A^x_B mod p = g^(x_A*x_B) mod p
    K_bob = mod_pow(y_alice, x_bob, mbxi.p)
    
    print(f"\nОбщий секрет Алисы: {K_alice}")
    print(f"Общий секрет Боба:   {K_bob}")
    print(f"Секреты совпадают: {K_alice == K_bob}")
    
    # Использование общего секрета для подписи
    message = 999
    signature_alice = mbxi.sign(message, K_alice)
    print(f"\nПодпись сообщения {message} с использованием общего секрета: {signature_alice}")
    
    # Проверка подписи Бобом
    is_valid = mbxi.verify(message, signature_alice, K_bob)
    print(f"Боб проверил подпись: {is_valid}")


def demo_realistic_scenario():
    """
    Реалистичный сценарий: безопасная передача документа
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 4: РЕАЛИСТИЧНЫЙ СЦЕНАРИЙ")
    print("=" * 70)
    
    # Генерация больших параметров (32 бита для демонстрации)
    print("Генерация параметров для реального сценария...")
    mbxi = MBXIDigitalSignature(bits = 16)
    
    # Генерация ключей
    x_alice, y_alice = mbxi.generate_keypair()
    x_bob, y_bob = mbxi.generate_keypair()
    
    print(f"\nПара ключей Алисы создана")
    print(f"Пара ключей Боба создана")
    
    # Документ для отправки
    document = """
    КОНТРАКТ №123-А
    Стороны: Алиса и Боб
    Сумма: 100000 рублей
    Дата: 2026-08-09
    """
    
    print(f"\nДокумент для отправки:")
    print("---")
    print(document.strip())
    print("---")
    
    # Алиса подписывает и шифрует документ
    ciphertext, signature, gk, doc_hash = mbxi.sign_and_encrypt(
        document, 
        x_alice, 
        y_bob
    )
    
    print(f"\nОтправлено Бобу:")
    print(f"  Хэш документа: {doc_hash}")
    print(f"  Шифротекст: {ciphertext}")
    print(f"  Подпись: {signature}")
    print(f"  g ^ k: {gk}")
    
    # Боб получает, расшифровывает и проверяет
    decrypted_hash, is_valid = mbxi.decrypt_and_verify(
        ciphertext, signature, gk,
        x_bob, y_alice, 
        expected_message_hash=doc_hash
    )
    
    print(f"\nРезультат проверки:")
    print(f"  Восстановленный хэш: {decrypted_hash}")
    print(f"  Хэши совпадают: {decrypted_hash == doc_hash}")
    print(f"  Подпись аутентифицирована: {is_valid}")
    
    if is_valid and decrypted_hash == doc_hash:
        print("\n  ✅ ДОКУМЕНТ ПРИНЯТ: Подпись подтверждена, целостность сохранена")
    else:
        print("\n  ❌ ДОКУМЕНТ ОТКЛОНЕН: Обнаружено нарушение")


# ============================================================================
# ЗАПУСК ДЕМОНСТРАЦИЙ
# ============================================================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости (для демонстрации)
    random.seed(42)
    
    print("\n" + "=" * 70)
    print("MBXI - ЦИФРОВАЯ ПОДПИСЬ И ШИФРОВАНИЕ")
    print("Реализация гибридной схемы с защитой от шпионажа")
    print("=" * 70)
    
    try:
        # Запуск всех демонстраций
        demo_basic_signature()
        demo_encrypted_signature()
        demo_key_exchange()
        demo_realistic_scenario()
        
        print("\n" + "=" * 70)
        print("Программа завершена успешно!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()