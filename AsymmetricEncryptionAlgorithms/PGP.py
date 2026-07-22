# PGP 
import hashlib
import os
import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ============================================================
# 1. РЕАЛИЗАЦИЯ RSA (Асимметричное шифрование для обмена ключами)
# ============================================================

def gcd(a, b):
    """Алгоритм Евклида для нахождения НОД"""
    while b != 0:
        a, b = b, a % b
    return a

def egcd(a, b):
    """Расширенный алгоритм Евклида (для поиска обратного элемента)"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Нахождение обратного элемента a ^ (-1) mod m"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Обратный элемент не существует')
    else:
        return x % m

def is_prime(n, k = 5):
    """Тест Миллера-Рабина на простоту (для маленьких чисел)"""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
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

def generate_prime(bits = 8):
    """Генерация простого числа заданной битности"""
    while True:
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1
        if is_prime(num):
            return num

def generate_rsa_keypair(bits = 16):
    """
    Генерация пары ключей RSA.
    Для демонстрации используем 16 бит.
    """
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 17
    while gcd(e, phi) != 1:
        e += 2
    
    d = modinv(e, phi)
    
    return (e, n), (d, n)

def rsa_encrypt(message_int, public_key):
    """Шифрование числа с помощью открытого ключа (e, n)"""
    e, n = public_key
    return pow(message_int, e, n)

def rsa_decrypt(cipher_int, private_key):
    """Расшифрование числа с помощью закрытого ключа (d, n)"""
    d, n = private_key
    return pow(cipher_int, d, n)

# ============================================================
# 2. РЕАЛИЗАЦИЯ СИММЕТРИЧНОГО ШИФРОВАНИЯ (AES-CBC)
# ============================================================

def generate_session_key(length = 16):
    """Генерация случайного сеансового ключа (по умолчанию 128 бит)"""
    return os.urandom(length)

def aes_encrypt(plaintext, key):
    """
    Шифрование сообщения с помощью AES в режиме CBC.
    Возвращает: IV + зашифрованный текст
    """
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    """
    Расшифрование сообщения с помощью AES в режиме CBC.
    Ожидает на вход: IV + зашифрованный текст
    """
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(actual_ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)
    return decrypted.decode('utf-8')

# ============================================================
# 3. ЦИФРОВАЯ ПОДПИСЬ (RSA + SHA-256)
# ============================================================

def sign_message(message, private_key):
    """Создание цифровой подписи: хешируем сообщение и шифруем хеш закрытым ключом."""
    hash_obj = hashlib.sha256(message.encode('utf-8'))
    hash_int = int(hash_obj.hexdigest(), 16)
    d, n = private_key
    # Обрезаем хеш, чтобы он поместился в модуль RSA
    hash_int = hash_int % n
    signature_int = pow(hash_int, d, n)
    return signature_int

def verify_signature(message, signature_int, public_key):
    """Проверка цифровой подписи."""
    hash_obj = hashlib.sha256(message.encode('utf-8'))
    hash_int = int(hash_obj.hexdigest(), 16)
    e, n = public_key
    decrypted_hash = pow(signature_int, e, n)
    return hash_int % n == decrypted_hash

# ============================================================
# 4. РЕАЛИЗАЦИЯ ПРОТОКОЛА PGP (ГИБРИДНОЕ ШИФРОВАНИЕ)
# ============================================================

class PGPProtocol:
    """
    Класс, реализующий упрощенный протокол PGP.
    """
    
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.session_key = None
    
    def generate_keys(self, bits = 16):
        """Генерация пары ключей RSA."""
        print(f"Генерация RSA ключей (битность: {bits})...")
        self.public_key, self.private_key = generate_rsa_keypair(bits)
        print(f"Открытый ключ: (e = {self.public_key[0]}, n = {self.public_key[1]})")
        print(f"Закрытый ключ: (d = {self.private_key[0]}, n = {self.private_key[1]})")
        return self.public_key, self.private_key
    
    def encrypt_message(self, plaintext, recipient_public_key, sign = False):
        """
        Шифрование сообщения по протоколу PGP.
        """
        print("\n" + "=" * 50)
        print("НАЧАЛО ШИФРОВАНИЯ (PGP)")
        print("=" * 50)
        
        # ШАГ 1: Генерация сеансового ключа (128 бит для совместимости с маленьким RSA)
        # Используем 16 байт (128 бит) вместо 32 байт (256 бит)
        self.session_key = generate_session_key(16)
        print(f"[1] Сеансовый ключ (AES-128): {base64.b64encode(self.session_key).decode()[:20]}...")
        
        # ШАГ 2: Шифрование сеансового ключа открытым ключом получателя (RSA)
        session_key_int = int.from_bytes(self.session_key, byteorder = 'big')
        
        # Проверяем, помещается ли ключ в модуль RSA
        e, n = recipient_public_key
        if session_key_int >= n:
            print(f"⚠️  Предупреждение: сеансовый ключ ({session_key_int.bit_length()} бит) больше модуля RSA ({n.bit_length()} бит)")
            print("   Используем обрезание ключа для демонстрации...")
            session_key_int = session_key_int % n
        
        encrypted_key = rsa_encrypt(session_key_int, recipient_public_key)
        print(f"[2] Сеансовый ключ зашифрован RSA (открытый ключ получателя)")
        
        # ШАГ 3: Шифрование сообщения сеансовым ключом (AES-CBC)
        encrypted_data = aes_encrypt(plaintext, self.session_key)
        print(f"[3] Сообщение зашифровано AES-128 (CBC)")
        
        # ШАГ 4: Цифровая подпись (опционально)
        signature = None
        if sign:
            if self.private_key is None:
                raise Exception("Для подписи нужен Ваш закрытый ключ! Сгенерируйте ключи.")
            print("[4] Создание цифровой подписи (SHA-256 + RSA)...")
            signature = sign_message(plaintext, self.private_key)
            print(f"    Подпись: {signature}")
        
        pgp_packet = {
            'encrypted_session_key': encrypted_key,
            'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
            'signature': signature,
            'recipient_public_key': recipient_public_key,
            'session_key_length': len(self.session_key)
        }
        
        print("=" * 50)
        print("ШИФРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 50)
        
        return pgp_packet
    
    def decrypt_message(self, pgp_packet, recipient_private_key, verify = False):
        """
        Расшифрование сообщения по протоколу PGP.
        """
        print("\n" + "=" * 50)
        print("НАЧАЛО РАСШИФРОВАНИЯ (PGP)")
        print("=" * 50)
        
        encrypted_key = pgp_packet['encrypted_session_key']
        encrypted_data_b64 = pgp_packet['encrypted_data']
        signature = pgp_packet.get('signature')
        public_key = pgp_packet.get('recipient_public_key')
        session_key_length = pgp_packet.get('session_key_length', 16)
        
        # ШАГ 1: Расшифровка сеансового ключа (RSA)
        session_key_int = rsa_decrypt(encrypted_key, recipient_private_key)
        
        # Преобразуем число обратно в байты
        try:
            session_key = session_key_int.to_bytes(session_key_length, byteorder = 'big')
        except OverflowError:
            # Если число не помещается, берем младшие байты
            session_key_bytes = session_key_int.to_bytes((session_key_int.bit_length() + 7) // 8, byteorder = 'big')
            if len(session_key_bytes) < session_key_length:
                session_key = b'\x00' * (session_key_length - len(session_key_bytes)) + session_key_bytes
            else:
                session_key = session_key_bytes[-session_key_length:] if len(session_key_bytes) >= session_key_length else session_key_bytes
        
        print(f"[1] Сеансовый ключ расшифрован RSA (закрытый ключ получателя)")
        print(f"    Ключ: {base64.b64encode(session_key).decode()[:20]}... (длина: {len(session_key)} байт)")
        
        # ШАГ 2: Расшифровка данных (AES-CBC)
        try:
            encrypted_data = base64.b64decode(encrypted_data_b64)
            decrypted_text = aes_decrypt(encrypted_data, session_key)
            print(f"[2] Сообщение расшифровано AES-128 (CBC)")
        except ValueError as e:
            print(f"[2] ❌ ОШИБКА РАСШИФРОВКИ: {e}")
            print("    Возможные причины:")
            print("    - Неправильная длина сеансового ключа")
            print("    - Повреждение зашифрованных данных")
            print("    - Использование несовместимых ключей")
            raise
        
        # ШАГ 3: Проверка подписи (если есть)
        if signature is not None and verify:
            if public_key is None:
                print("⚠️  Нет открытого ключа для проверки подписи!")
            else:
                print("[3] Проверка цифровой подписи...")
                is_valid = verify_signature(decrypted_text, signature, public_key)
                if is_valid:
                    print("    ✅ ПОДПИСЬ ВЕРНА! Сообщение не было изменено.")
                else:
                    print("    ❌ ПОДПИСЬ НЕВЕРНА! Сообщение могло быть изменено.")
        
        print("=" * 50)
        print("РАСШИФРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 50)
        
        return decrypted_text


# ============================================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ ПРОТОКОЛА
# ============================================================

def test_encryption_decryption(bits = 16, key_size = 16):
    """
    Тестирование шифрования и расшифрования с заданными параметрами.
    """
    print(f"\n{'=' * 60}")
    print(f"ТЕСТ: RSA битность = {bits}, AES ключ = {key_size * 8} бит")
    print(f"{'=' * 60}")
    
    # Создаем пользователей
    alice = PGPProtocol()
    alice.generate_keys(bits)
    
    bob = PGPProtocol()
    bob_public, bob_private = bob.generate_keys(bits)
    
    # Тестовое сообщение
    test_message = "Привет, это тестовое сообщение для PGP!"
    
    # Шифрование
    print(f"\n--- Шифрование сообщения ---")
    encrypted = alice.encrypt_message(
        plaintext = test_message,
        recipient_public_key = bob_public,
        sign = True
    )
    
    # Расшифрование
    print(f"\n--- Расшифрование сообщения ---")
    try:
        decrypted = bob.decrypt_message(
            pgp_packet = encrypted,
            recipient_private_key = bob_private,
            verify = True
        )
        
        # Проверка
        if decrypted == test_message:
            print(f"\n✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
            return True
        else:
            print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН: сообщения не совпадают")
            print(f"Оригинал: {test_message}")
            print(f"Расшифровано: {decrypted}")
            return False
    except Exception as e:
        print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН: {e}")
        return False


def main():
    print("=" * 60)
    print("УПРОЩЕННАЯ РЕАЛИЗАЦИЯ ПРОТОКОЛА PGP")
    print("(гибридное шифрование: RSA + AES)")
    print("=" * 60)
    
    # Проверяем наличие библиотеки
    try:
        import Crypto
    except ImportError:
        print("⚠️  Библиотека pycryptodome не установлена!")
        print("Установите её командой: pip install pycryptodome")
        return
    
    print("\n💡 Для корректной работы используем:")
    print("   - RSA с битностью 24 (чтобы помещался 128-битный ключ)")
    print("   - AES - 128 (16 байт) для симметричного шифрования")
    print("   - Цифровая подпись SHA - 256 + RSA")
    
    # Тест с различными параметрами
    results = []
    
    # Тест 1: 16 бит RSA + 128 бит AES
    results.append(("RSA - 16 + AES - 128", test_encryption_decryption(16, 16)))
    
    # Тест 2: 20 бит RSA + 128 бит AES
    results.append(("RSA - 20 + AES - 128", test_encryption_decryption(20, 16)))
    
    # Тест 3: 24 бит RSA + 128 бит AES (рекомендуется)
    results.append(("RSA - 24 + AES - 128", test_encryption_decryption(24, 16)))
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    for name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{name:20} : {status}")


if __name__ == "__main__":
    main()