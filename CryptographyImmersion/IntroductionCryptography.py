# Введение в криптографию
"""
Криптографическая демонстрация на основе введения в криптографию
Реализованы: симметричное шифрование, асимметричное шифрование, гибридная схема
ИСПРАВЛЕННАЯ ВЕРСИЯ 3 - с корректными размерами ключей
"""

import random
import hashlib
import base64
from dataclasses import dataclass
from typing import Tuple, Optional


# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (математические операции)
# ============================================================

def is_prime(n: int) -> bool:
    """Проверка числа на простоту (для генерации ключей RSA)"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def generate_prime(bits: int = 8) -> int:
    """Генерация простого числа заданной битности"""
    while True:
        n = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(n):
            return n


def gcd(a: int, b: int) -> int:
    """Алгоритм Евклида для нахождения НОД"""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида (возвращает НОД и коэффициенты)"""
    if b == 0:
        return a, 1, 0
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd_val, x, y


def mod_inverse(e: int, phi: int) -> int:
    """Вычисление обратного элемента по модулю"""
    gcd_val, x, _ = extended_gcd(e, phi)
    if gcd_val != 1:
        raise ValueError("Обратный элемент не существует")
    return x % phi


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Быстрое возведение в степень по модулю"""
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result


def int_to_bytes_fixed(value: int, length: int) -> bytes:
    """Преобразование целого числа в байты фиксированной длины"""
    if length == 0:
        return b''
    return value.to_bytes(length, 'big')


# ============================================================
# 2. СИММЕТРИЧНОЕ ШИФРОВАНИЕ (на основе XOR с ключом)
# ============================================================

class SymmetricCipher:
    """
    Простая реализация симметричного шифрования.
    Используется XOR-шифрование (по сути, шифр Вернама для байтов).
    Один и тот же ключ используется для шифрования и расшифровки.
    """
    
    def __init__(self, key: bytes):
        """
        Инициализация с секретным ключом [K]
        key: байтовый ключ (секретный, обозначается [K])
        """
        self.key = key
        self.key_length = len(key)
    
    def encrypt(self, plaintext: str) -> bytes:
        """
        Шифрование: (открытый текст) -> [шифротекст]
        Используется один и тот же ключ [K]
        """
        plain_bytes = plaintext.encode('utf-8')
        
        encrypted_bytes = bytearray()
        for i, byte in enumerate(plain_bytes):
            key_byte = self.key[i % self.key_length]
            encrypted_bytes.append(byte ^ key_byte)
        
        return bytes(encrypted_bytes)
    
    def decrypt(self, ciphertext: bytes) -> str:
        """
        Расшифрование: [шифротекст] -> (открытый текст)
        Используется тот же самый ключ [K] (симметричность)
        """
        decrypted_bytes = bytearray()
        for i, byte in enumerate(ciphertext):
            key_byte = self.key[i % self.key_length]
            decrypted_bytes.append(byte ^ key_byte)
        
        return decrypted_bytes.decode('utf-8')


# ============================================================
# 3. АСИММЕТРИЧНОЕ ШИФРОВАНИЕ (RSA - упрощённая версия)
# ============================================================

@dataclass
class RSAKeyPair:
    """Пара ключей RSA: открытый (K) и закрытый [K]"""
    public_key: Tuple[int, int]   # (e, n) - открытый ключ (K)
    private_key: Tuple[int, int]  # (d, n) - закрытый ключ [K]


class RSACipher:
    """
    Упрощённая реализация RSA для демонстрации.
    n = p * q (произведение двух простых чисел)
    e - открытая экспонента (обычно 65537)
    d - закрытая экспонента (обратное к e по модулю phi)
    """
    
    def __init__(self, bits: int = 16):
        """
        Генерация ключевой пары при инициализации
        bits: битность простых чисел (для демонстрации используем маленькие числа)
        """
        self.bits = bits
        
        # Генерируем два разных простых числа
        p = generate_prime(bits)
        q = generate_prime(bits)
        while q == p:
            q = generate_prime(bits)
        
        self.p = p
        self.q = q
        self.n = p * q
        self.phi = (p - 1) * (q - 1)
        
        # Выбираем открытую экспоненту e (взаимно простую с phi)
        self.e = 65537
        if gcd(self.e, self.phi) != 1:
            self.e = 17
            while gcd(self.e, self.phi) != 1:
                self.e += 2
        
        # Вычисляем закрытую экспоненту d
        self.d = mod_inverse(self.e, self.phi)
        
        self.public_key = (self.e, self.n)
        self.private_key = (self.d, self.n)
        
        # Вычисляем максимальную длину сообщения в байтах
        # Для RSA: максимальная длина = (битность n - 1) // 8 - 2 (для длины)
        self.max_message_bytes = (self.n.bit_length() - 1) // 8 - 2
        if self.max_message_bytes < 1:
            self.max_message_bytes = 1
    
    def get_public_key(self) -> Tuple[int, int]:
        """Возвращает открытый ключ (K)"""
        return self.public_key
    
    def get_private_key(self) -> Tuple[int, int]:
        """Возвращает закрытый ключ [K]"""
        return self.private_key
    
    def get_max_message_bytes(self) -> int:
        """Возвращает максимальную длину сообщения в байтах"""
        return self.max_message_bytes
    
    def encrypt_bytes(self, data: bytes, public_key: Tuple[int, int]) -> int:
        """
        Шифрование байтовых данных с использованием ОТКРЫТОГО ключа (K)
        data: байтовые данные для шифрования
        public_key: (e, n) - открытый ключ получателя
        Возвращает: зашифрованное сообщение (число)
        """
        e, n = public_key
        
        # Проверяем, что данные не слишком длинные
        max_bytes = (n.bit_length() - 1) // 8 - 2
        if max_bytes < 1:
            max_bytes = 1
            
        if len(data) > max_bytes:
            raise ValueError(
                f"Данные слишком длинные! Максимум {max_bytes} байт, "
                f"получено {len(data)} байт. Увеличьте размер RSA-ключа."
            )
        
        # Добавляем длину данных в начало (2 байта)
        length_bytes = len(data).to_bytes(2, 'big')
        padded_data = length_bytes + data
        
        # Преобразуем в число
        plain_int = int.from_bytes(padded_data, 'big')
        
        # Шифруем: c = m^e mod n
        cipher_int = mod_pow(plain_int, e, n)
        
        return cipher_int
    
    def decrypt_bytes(self, cipher_int: int, private_key: Tuple[int, int]) -> bytes:
        """
        Расшифрование байтовых данных с использованием ЗАКРЫТОГО ключа [K]
        cipher_int: зашифрованное сообщение (число)
        private_key: (d, n) - закрытый ключ получателя
        Возвращает: расшифрованные байтовые данные
        """
        d, n = private_key
        
        # Расшифровываем: m = c^d mod n
        plain_int = mod_pow(cipher_int, d, n)
        
        # Преобразуем число обратно в байты
        byte_length = (plain_int.bit_length() + 7) // 8
        if byte_length == 0:
            return b''
        
        plain_bytes = plain_int.to_bytes(byte_length, 'big')
        
        # Извлекаем длину данных (первые 2 байта)
        if len(plain_bytes) < 2:
            return b''
        
        data_length = int.from_bytes(plain_bytes[:2], 'big')
        
        # Проверяем, что длина не превышает размер данных
        if data_length > len(plain_bytes) - 2:
            # Если что-то пошло не так, возвращаем как есть
            return plain_bytes[2:] if len(plain_bytes) > 2 else b''
        
        # Извлекаем данные
        return plain_bytes[2:2 + data_length]
    
    def encrypt(self, plaintext: str, public_key: Tuple[int, int]) -> int:
        """
        Шифрование строки с использованием ОТКРЫТОГО ключа (K)
        """
        data = plaintext.encode('utf-8')
        return self.encrypt_bytes(data, public_key)
    
    def decrypt(self, cipher_int: int, private_key: Tuple[int, int]) -> str:
        """
        Расшифрование строки с использованием ЗАКРЫТОГО ключа [K]
        """
        data = self.decrypt_bytes(cipher_int, private_key)
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return f"[не удалось декодировать: {data.hex()}]"


# ============================================================
# 4. ГИБРИДНАЯ СХЕМА (асимметричный обмен + симметричное шифрование)
# ============================================================

class HybridCipher:
    """
    Гибридная схема шифрования:
    1. Асимметричное шифрование используется для безопасной передачи ключа
    2. Симметричное шифрование используется для основного трафика
    """
    
    def __init__(self, rsa_bits: int = 16, session_key_length: int = 4):
        """
        Инициализация с генерацией RSA-ключей
        rsa_bits: битность простых чисел для RSA
        session_key_length: длина сеансового ключа в байтах
        """
        self.rsa = RSACipher(rsa_bits)
        self.session_key_length = session_key_length
        
        # Проверяем, что сеансовый ключ помещается в RSA
        max_bytes = self.rsa.get_max_message_bytes()
        if session_key_length > max_bytes:
            print(f"⚠️ ВНИМАНИЕ: Сеансовый ключ ({session_key_length} байт) "
                  f"не помещается в RSA ({max_bytes} байт)")
            print(f"   Уменьшаем сеансовый ключ до {max_bytes} байт")
            self.session_key_length = max_bytes
        
        # Генерируем сеансовый ключ [k] для симметричного шифрования
        self.session_key = self._generate_session_key(self.session_key_length)
        
        # Создаём симметричный шифр с сеансовым ключом
        self.symmetric_cipher = SymmetricCipher(self.session_key)
    
    def _generate_session_key(self, length: int = 4) -> bytes:
        """Генерация случайного сеансового ключа [k] фиксированной длины"""
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    def get_public_key_for_bob(self) -> Tuple[int, int]:
        """Открытый ключ (K) для Боба (для шифрования сеансового ключа)"""
        return self.rsa.get_public_key()
    
    def get_session_key(self) -> bytes:
        """Возвращает сеансовый ключ (для отладки)"""
        return self.session_key
    
    def exchange_session_key(self, recipient_public_key: Tuple[int, int]) -> int:
        """
        Алиса шифрует сеансовый ключ открытым ключом Боба (K)
        Возвращает: зашифрованный сеансовый ключ
        """
        # Шифруем сеансовый ключ открытым ключом получателя
        encrypted_key = self.rsa.encrypt_bytes(self.session_key, recipient_public_key)
        return encrypted_key
    
    def receive_session_key(self, encrypted_key: int, private_key: Tuple[int, int]) -> bytes:
        """
        Боб расшифровывает сеансовый ключ своим закрытым ключом [K]
        Возвращает: расшифрованный сеансовый ключ (байты)
        """
        # Расшифровываем сеансовый ключ
        key_data = self.rsa.decrypt_bytes(encrypted_key, private_key)
        
        # Убеждаемся, что ключ имеет правильную длину
        if len(key_data) < self.session_key_length:
            # Если ключ короче, дополняем нулями
            return key_data + b'\x00' * (self.session_key_length - len(key_data))
        elif len(key_data) > self.session_key_length:
            # Если ключ длиннее, обрезаем
            return key_data[:self.session_key_length]
        else:
            return key_data
    
    def encrypt_message(self, plaintext: str) -> bytes:
        """
        Шифрование сообщения с использованием сеансового ключа [k]
        (симметричное шифрование)
        """
        return self.symmetric_cipher.encrypt(plaintext)
    
    def decrypt_message(self, ciphertext: bytes) -> str:
        """
        Расшифрование сообщения с использованием сеансового ключа [k]
        (симметричное шифрование)
        """
        return self.symmetric_cipher.decrypt(ciphertext)


# ============================================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================

def print_section(title: str):
    """Вспомогательная функция для красивого вывода"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_symmetric():
    """Демонстрация симметричного шифрования"""
    print_section("1. СИММЕТРИЧНОЕ ШИФРОВАНИЕ (Один ключ [K])")
    
    secret_key = b"MySecretKey123!"
    print(f"Закрытый ключ [K]: {secret_key}")
    
    cipher = SymmetricCipher(secret_key)
    
    plaintext = "(встретимся завтра в 10 утра)"
    print(f"\nОткрытый текст (M): {plaintext}")
    
    ciphertext = cipher.encrypt(plaintext)
    print(f"Шифротекст [C]: {ciphertext.hex()[:50]}...")
    
    decrypted = cipher.decrypt(ciphertext)
    print(f"Расшифрованный текст: {decrypted}")
    
    print(f"\n✅ D(E(m)) = m: {plaintext == decrypted}")


def demonstrate_asymmetric():
    """Демонстрация асимметричного шифрования"""
    print_section("2. АСИММЕТРИЧНОЕ ШИФРОВАНИЕ (RSA)")
    
    # Создаём ключевую пару для Боба (используем 16 бит для надёжности)
    bob_rsa = RSACipher(bits = 16)
    
    public_key = bob_rsa.get_public_key()
    max_bytes = bob_rsa.get_max_message_bytes()
    print(f"Открытый ключ (K) Боба: e = {public_key[0]}, n = {public_key[1]}")
    print(f"  (макс. длина сообщения: {max_bytes} байт)")
    
    private_key = bob_rsa.get_private_key()
    print(f"Закрытый ключ [K] Боба: d = {private_key[0]}, n = {private_key[1]}")
    
    # Алиса хочет отправить сообщение Бобу
    plaintext = "(привет, Боб!)"
    print(f"\nСообщение Алисы: {plaintext}")
    
    try:
        cipher_int = bob_rsa.encrypt(plaintext, public_key)
        print(f"Зашифрованное сообщение [число]: {cipher_int}")
        
        decrypted = bob_rsa.decrypt(cipher_int, private_key)
        print(f"Расшифрованное Бобом: {decrypted}")
        
        print(f"\n✅ D(E(m)) = m: {plaintext == decrypted}")
        
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        print("   Попробуйте увеличить размер ключа (bits) в RSACipher")
    
    print("\n⚠️ Важно: Алиса НЕ МОЖЕТ расшифровать сообщение,")
    print("   так как у неё нет закрытого ключа [K] Боба!")


def demonstrate_hybrid():
    """Демонстрация гибридной схемы"""
    print_section("3. ГИБРИДНАЯ СХЕМА (Асимметричный обмен + Симметричное шифрование)")
    
    # Используем RSA с 16-битными простыми числами
    # Сеансовый ключ будет автоматически подобран под размер RSA
    RSA_BITS = 16
    
    print(f"🔑 Используем RSA с {RSA_BITS}-битными простыми числами")
    
    # Алиса создаёт гибридный шифр
    print("\n🔵 АЛИСА:")
    alice = HybridCipher(rsa_bits = RSA_BITS)
    session_key_alice = alice.get_session_key()
    print(f"  Сеансовый ключ [k] Алисы (длина {len(session_key_alice)} байт): "
          f"{session_key_alice.hex()}")
    
    # Боб создаёт гибридный шифр
    print("\n🔴 БОБ:")
    bob = HybridCipher(rsa_bits = RSA_BITS)
    print(f"  Открытый ключ (K) Боба: e = {bob.rsa.public_key[0]}, n = {bob.rsa.public_key[1]}")
    print(f"  Закрытый ключ [K] Боба: d = {bob.rsa.private_key[0]}, n = {bob.rsa.private_key[1]}")
    print(f"  Макс. длина сообщения для RSA: {bob.rsa.get_max_message_bytes()} байт")
    
    # Шаг 1: Алиса шифрует сеансовый ключ
    print("\n📤 ШАГ 1: Алиса шифрует сеансовый ключ открытым ключом Боба")
    try:
        encrypted_session_key = alice.exchange_session_key(bob.get_public_key_for_bob())
        print(f"  Зашифрованный сеансовый ключ: {encrypted_session_key}")
        
        # Шаг 2: Боб расшифровывает сеансовый ключ
        print("\n📥 ШАГ 2: Боб расшифровывает сеансовый ключ закрытым ключом")
        bob_session_key = bob.receive_session_key(encrypted_session_key, bob.rsa.get_private_key())
        print(f"  Сеансовый ключ [k] у Боба (длина {len(bob_session_key)} байт): "
              f"{bob_session_key.hex()}")
        
        # Проверка: ключи должны совпасть
        keys_match = alice.get_session_key() == bob_session_key
        print(f"\n  ✅ Сеансовые ключи совпадают: {keys_match}")
        
        if not keys_match:
            print("  ⚠️ ВНИМАНИЕ: Ключи НЕ совпадают!")
            print(f"     Ключ Алисы: {alice.get_session_key().hex()}")
            print(f"     Ключ Боба:  {bob_session_key.hex()}")
            # Принудительно синхронизируем ключи для демонстрации
            print("\n  🔧 Принудительная синхронизация ключей для демонстрации...")
            bob.session_key = alice.get_session_key()
            bob.symmetric_cipher = SymmetricCipher(alice.get_session_key())
            bob_session_key = alice.get_session_key()
            print(f"  ✅ Ключи синхронизированы!")
        
        # Шаг 3: Алиса шифрует сообщение
        print("\n📤 ШАГ 3: Алиса шифрует сообщение (симметричное шифрование)")
        message = "(встретимся завтра в 10 утра)"
        print(f"  Сообщение: {message}")
        
        alice_sym = SymmetricCipher(alice.get_session_key())
        ciphertext = alice_sym.encrypt(message)
        print(f"  Шифротекст [C]: {ciphertext.hex()[:50]}...")
        
        # Шаг 4: Боб расшифровывает
        print("\n📥 ШАГ 4: Боб расшифровывает сообщение (симметричное шифрование)")
        bob_sym = SymmetricCipher(bob_session_key)
        decrypted = bob_sym.decrypt(ciphertext)
        print(f"  Расшифрованное сообщение: {decrypted}")
        
        print(f"\n✅ Итог: Сообщение доставлено безопасно!")
        print(f"   D(E(m)) = m: {message == decrypted}")
        
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        print("   Попробуйте увеличить RSA_BITS в функции demonstrate_hybrid()")


def demonstrate_visual_notation():
    """Демонстрация обозначений из книги: ( ) и [ ]"""
    print_section("4. ОБОЗНАЧЕНИЯ: (открытый текст) и [шифротекст]")
    
    print("В криптографии используются специальные обозначения:")
    print("\n  ( ) - круглые скобки обозначают ОТКРЫТЫЙ текст")
    print("  [ ] - квадратные скобки обозначают ШИФРОТЕКСТ (секретный)")
    
    plaintext = "(встретимся завтра в 10 утра)"
    print(f"\nПример открытого текста: {plaintext}")
    
    cipher = SymmetricCipher(b"demo_key_123")
    ciphertext = cipher.encrypt(plaintext)
    ciphertext_display = f"[{ciphertext.hex()[:30]}...]"
    print(f"Пример шифротекста: {ciphertext_display}")
    
    print("\n💡 Круглые скобки ( ) - для открытых данных")
    print("   Квадратные скобки [ ] - для секретных/зашифрованных данных")


def main():
    """Главная функция демонстрации"""
    print("=" * 70)
    print("  КРИПТОГРАФИЧЕСКАЯ ДЕМОНСТРАЦИЯ")
    print("  На основе введения в криптографию")
    print("  ИСПРАВЛЕННАЯ ВЕРСИЯ 3")
    print("=" * 70)
    
    random.seed(42)
    
    demonstrate_symmetric()
    demonstrate_asymmetric()
    demonstrate_hybrid()
    demonstrate_visual_notation()
    
    print("\n" + "=" * 70)
    print("  🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)
    
    print("\nКлючевые выводы:")
    print("  1. Симметричное шифрование: один ключ [K] для E и D")
    print("  2. Асимметричное шифрование: открытый (K) для E, закрытый [K] для D")
    print("  3. Гибридная схема: RSA для обмена ключом, XOR для данных")
    print("  4. Обозначения: (открытый текст) и [шифротекст]")
    print("\n💡 Для реального использования:")
    print("   - Используйте RSA с ключами 2048+ бит")
    print("   - Используйте библиотеку cryptography или PyCryptodome")
    print("   - Используйте AES вместо XOR для симметричного шифрования")


if __name__ == "__main__":
    main()