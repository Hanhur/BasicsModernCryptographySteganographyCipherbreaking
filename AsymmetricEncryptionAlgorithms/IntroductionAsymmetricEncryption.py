# Введение в асимметричное шифрование
"""
АСИММЕТРИЧНОЕ ШИФРОВАНИЕ (RSA)
Исправленная версия с корректной обработкой байтов и UTF-8
"""

import random
import math
import hashlib
import time
from typing import Tuple, Optional


class RSA:
    """
    Класс, реализующий асимметричное шифрование RSA
    """
    
    def __init__(self, key_size: int = 512):
        """
        Инициализация с указанием размера ключа в битах
        
        Args:
            key_size: размер простых чисел (рекомендуется 512, 1024, 2048). Для демонстрации используем 512 бит (в реальности 2048+)
        """
        self.key_size = key_size
        self.public_key = None  # (e, n)
        self.private_key = None  # (d, n)
        
    @staticmethod
    def is_prime(n: int, k: int = 40) -> bool:
        """
        Тест Миллера-Рабина для проверки простоты числа
        
        Args:
            n: проверяемое число
            k: количество итераций (чем больше, тем точнее)
        
        Returns:
            True если число простое с высокой вероятностью
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
            
        # Записываем n-1 как d * 2^r
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
            
        # Проверяем k раз
        for _ in range(k):
            a = random.randrange(2, n - 1)
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
    
    @staticmethod
    def generate_prime(bits: int) -> int:
        """
        Генерация простого числа заданной битности
        
        Args:
            bits: количество бит
        
        Returns:
            Простое число
        """
        while True:
            # Генерируем нечетное число нужного размера
            num = random.getrandbits(bits)
            # Убеждаемся, что число нечетное и достаточно большое
            num |= (1 << bits - 1) | 1
            
            if RSA.is_prime(num):
                return num
    
    @staticmethod
    def egcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида
        
        Returns:
            (gcd, x, y) где ax + by = gcd(a, b)
        """
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = RSA.egcd(b % a, a)
        return gcd, y1 - (b // a) * x1, x1
    
    @staticmethod
    def modinv(a: int, m: int) -> int:
        """
        Нахождение обратного элемента по модулю
        
        Args:
            a: число
            m: модуль
        
        Returns:
            x такое что (a * x) % m == 1
        """
        gcd, x, _ = RSA.egcd(a, m)
        if gcd != 1:
            raise ValueError(f"Обратный элемент не существует: {a} и {m} не взаимно просты")
        return x % m
    
    def generate_keys(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Генерация пары ключей RSA
        
        Returns:
            (public_key, private_key) где каждый ключ - (exponent, n)
        """
        print(f"\n{'=' * 60}")
        print(f"ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA (битность: {self.key_size})")
        print(f"{'=' * 60}")
        
        start_time = time.time()
        
        # Шаг 1: Генерируем два больших простых числа p и q
        print(f"Генерация простых чисел p и q...")
        p = self.generate_prime(self.key_size // 2)
        q = self.generate_prime(self.key_size // 2)
        
        # Шаг 2: Вычисляем n = p * q
        n = p * q
        print(f"p = {p}\nq = {q}")
        print(f"n = p * q = {n}")
        
        # Шаг 3: Вычисляем функцию Эйлера φ(n) = (p-1) * (q-1)
        phi_n = (p - 1) * (q - 1)
        print(f"φ(n) = (p - 1) * (q - 1) = {phi_n}")
        
        # Шаг 4: Выбираем e (открытая экспонента), взаимно простое с φ(n)
        e = 65537  # Стандартное значение для RSA
        # Проверяем, что e взаимно просто с φ(n)
        while math.gcd(e, phi_n) != 1:
            e = random.randrange(3, phi_n, 2)
        print(f"e = {e}")
        
        # Шаг 5: Вычисляем d (закрытая экспонента) как обратное к e по модулю φ(n)
        d = self.modinv(e, phi_n)
        print(f"d = {d}")
        
        self.public_key = (e, n)
        self.private_key = (d, n)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Ключи успешно сгенерированы за {elapsed:.2f} секунд")
        print(f"Размер открытого ключа: {n.bit_length()} бит")
        
        return self.public_key, self.private_key
    
    @staticmethod
    def encrypt_block(message_int: int, public_key: Tuple[int, int]) -> int:
        """
        Шифрование одного блока
        
        Args:
            message_int: целочисленное представление блока
            public_key: (e, n)
        
        Returns:
            Зашифрованный блок
        """
        e, n = public_key
        return pow(message_int, e, n)
    
    @staticmethod
    def decrypt_block(cipher_int: int, private_key: Tuple[int, int]) -> int:
        """
        Расшифрование одного блока
        
        Args:
            cipher_int: зашифрованный блок
            private_key: (d, n)
        
        Returns:
            Расшифрованный блок
        """
        d, n = private_key
        return pow(cipher_int, d, n)
    
    def encrypt(self, message: str, public_key: Tuple[int, int]) -> Tuple[list, int, int]:
        """
        Шифрование строки сообщения
        
        Args:
            message: исходное сообщение
            public_key: открытый ключ (e, n)
        
        Returns:
            (список зашифрованных блоков, размер блока, длина исходных данных)
        """
        e, n = public_key
        
        # Преобразуем строку в байты UTF-8
        message_bytes = message.encode('utf-8')
        original_length = len(message_bytes)
        
        # Определяем размер блока (на 11 байт меньше для безопасности)
        # Используем (n.bit_length() - 1) // 8 для безопасного размера
        block_size = (n.bit_length() - 1) // 8 - 11  # -11 для PKCS#1 padding (упрощенно)
        
        # Минимальный размер блока
        if block_size < 1:
            block_size = 1
        
        # Разбиваем на блоки
        encrypted_blocks = []
        for i in range(0, len(message_bytes), block_size):
            block = message_bytes[i:i + block_size]
            # Преобразуем блок в целое число
            block_int = int.from_bytes(block, 'big')
            encrypted_block = self.encrypt_block(block_int, public_key)
            encrypted_blocks.append(encrypted_block)
        
        return encrypted_blocks, block_size, original_length
    
    def decrypt(self, encrypted_blocks: list, private_key: Tuple[int, int], block_size: int, original_length: int) -> str:
        """
        Расшифрование списка блоков
        
        Args:
            encrypted_blocks: список зашифрованных блоков
            private_key: закрытый ключ (d, n)
            block_size: размер блока в байтах
            original_length: исходная длина данных в байтах
        
        Returns:
            Расшифрованное сообщение
        """
        d, n = private_key
        
        decrypted_bytes = bytearray()
        
        for i, block in enumerate(encrypted_blocks):
            # Расшифровываем блок
            decrypted_int = self.decrypt_block(block, private_key)
            
            # Определяем размер текущего блока
            # Для последнего блока используем остаток
            if i == len(encrypted_blocks) - 1:
                # Последний блок: вычисляем точный размер
                remaining = original_length - (i * block_size)
                current_block_size = remaining if remaining > 0 else block_size
            else:
                current_block_size = block_size
            
            # Преобразуем в байты с правильным размером
            try:
                block_bytes = decrypted_int.to_bytes(current_block_size, 'big')
            except OverflowError:
                # Если число слишком большое для указанного размера
                # пробуем определить реальный размер
                byte_length = (decrypted_int.bit_length() + 7) // 8
                block_bytes = decrypted_int.to_bytes(byte_length, 'big')
            
            decrypted_bytes.extend(block_bytes)
        
        # Обрезаем до оригинальной длины
        decrypted_bytes = decrypted_bytes[:original_length]
        
        # Декодируем UTF-8
        return decrypted_bytes.decode('utf-8')
    
    @staticmethod
    def sign(message: str, private_key: Tuple[int, int]) -> int:
        """
        Создание цифровой подписи (подписываем хеш сообщения)
        
        Args:
            message: сообщение
            private_key: закрытый ключ (d, n)
        
        Returns:
            Подпись (целое число)
        """
        d, n = private_key
        
        # Создаем хеш сообщения
        hash_bytes = hashlib.sha256(message.encode('utf-8')).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        
        # Подписываем хеш закрытым ключом
        signature = pow(hash_int, d, n)
        return signature
    
    @staticmethod
    def verify_signature(message: str, signature: int, public_key: Tuple[int, int]) -> bool:
        """
        Проверка цифровой подписи
        
        Args:
            message: сообщение
            signature: подпись
            public_key: открытый ключ (e, n)
        
        Returns:
            True если подпись верна
        """
        e, n = public_key
        
        # Вычисляем хеш сообщения
        hash_bytes = hashlib.sha256(message.encode('utf-8')).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        
        # Расшифровываем подпись открытым ключом
        decrypted_hash = pow(signature, e, n)
        
        # Сравниваем хеши
        return hash_int == decrypted_hash


class HybridCrypto:
    """
    Гибридная криптосистема (RSA + простой симметричный алгоритм)
    Демонстрирует, как на практике используется асимметричное шифрование
    """
    
    @staticmethod
    def simple_xor_encrypt(data: bytes, key: int) -> bytes:
        """
        Простой симметричный алгоритм (XOR с ключом)
        В реальности используется AES, но здесь показан принцип
        """
        result = bytearray()
        key_bytes = key.to_bytes(32, 'big')
        
        for i, byte in enumerate(data):
            result.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return bytes(result)
    
    @staticmethod
    def hybrid_encrypt(message: str, public_key: Tuple[int, int]) -> Tuple[bytes, int]:
        """
        Гибридное шифрование:
        1. Генерируем сессионный ключ
        2. Шифруем сообщение симметрично (XOR)
        3. Шифруем сессионный ключ асимметрично (RSA)
        """
        # 1. Генерируем случайный сессионный ключ
        session_key = random.getrandbits(256)
        
        # 2. Шифруем сообщение симметричным ключом
        message_bytes = message.encode('utf-8')
        encrypted_data = HybridCrypto.simple_xor_encrypt(message_bytes, session_key)
        
        # 3. Шифруем сессионный ключ открытым ключом
        e, n = public_key
        encrypted_key = pow(session_key, e, n)
        
        return encrypted_data, encrypted_key
    
    @staticmethod
    def hybrid_decrypt(encrypted_data: bytes, encrypted_key: int, private_key: Tuple[int, int]) -> str:
        """
        Гибридное расшифрование:
        1. Расшифровываем сессионный ключ асимметрично
        2. Расшифровываем данные симметричным ключом
        """
        d, n = private_key
        
        # 1. Расшифровываем сессионный ключ
        session_key = pow(encrypted_key, d, n)
        
        # 2. Расшифровываем данные
        decrypted_data = HybridCrypto.simple_xor_encrypt(encrypted_data, session_key)
        
        return decrypted_data.decode('utf-8')


def demo_rsa_encryption():
    """
    Демонстрация шифрования и расшифрования RSA
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ АСИММЕТРИЧНОГО ШИФРОВАНИЯ RSA")
    print("=" * 70)
    
    # Создаем экземпляр RSA
    rsa = RSA(key_size = 512)  # Для демонстрации 512 бит
    
    # Генерируем ключи
    public_key, private_key = rsa.generate_keys()
    
    # Исходное сообщение (с русскими символами)
    original_message = "Асимметричное шифрование революционизировало криптографию!"
    print(f"\n📝 Исходное сообщение:\n{original_message}")
    print(f"Длина сообщения: {len(original_message)} символов")
    
    # Шифрование
    print(f"\n{'=' * 60}")
    print("ШАГ 1: ШИФРОВАНИЕ ОТКРЫТЫМ КЛЮЧОМ")
    print(f"{'=' * 60}")
    
    start_time = time.time()
    encrypted_blocks, block_size, original_length = rsa.encrypt(original_message, public_key)
    encrypt_time = time.time() - start_time
    
    print(f"Зашифровано блоков: {len(encrypted_blocks)}")
    print(f"Размер блока: {block_size} байт")
    print(f"Исходная длина: {original_length} байт")
    print(f"Первый зашифрованный блок: {encrypted_blocks[0]}")
    print(f"⏱️ Время шифрования: {encrypt_time:.4f} секунд")
    
    # Расшифрование
    print(f"\n{'=' * 60}")
    print("ШАГ 2: РАСШИФРОВАНИЕ ЗАКРЫТЫМ КЛЮЧОМ")
    print(f"{'=' * 60}")
    
    start_time = time.time()
    decrypted_message = rsa.decrypt(encrypted_blocks, private_key, block_size, original_length)
    decrypt_time = time.time() - start_time
    
    print(f"📄 Расшифрованное сообщение:\n{decrypted_message}")
    print(f"⏱️ Время расшифрования: {decrypt_time:.4f} секунд")
    
    # Проверка
    print(f"\n{'=' * 60}")
    print("ПРОВЕРКА")
    print(f"{'=' * 60}")
    print(f"✅ Сообщения совпадают: {original_message == decrypted_message}")
    print(f"   Длина совпадает: {len(original_message)} == {len(decrypted_message)}")
    
    # Показываем байтовое представление
    print(f"\n📊 Байтовое представление:")
    original_bytes = original_message.encode('utf-8')
    print(f"   Исходные байты: {original_bytes[:20]}... (всего {len(original_bytes)} байт)")
    
    return rsa, public_key, private_key


def demo_digital_signature(rsa: RSA, public_key: Tuple[int, int], private_key: Tuple[int, int]):
    """
    Демонстрация цифровой подписи (отличие от шифрования)
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ЦИФРОВОЙ ПОДПИСИ (КРИПТОГРАФИЯ С ОТКРЫТЫМ КЛЮЧОМ)")
    print("=" * 70)
    
    message = "Важное сообщение: перевод 1000$ на счет #12345"
    print(f"\n📝 Сообщение для подписи:\n{message}")
    
    # Подпись
    print(f"\n{'=' * 60}")
    print("ШАГ 1: ПОДПИСЬ ЗАКРЫТЫМ КЛЮЧОМ")
    print(f"{'=' * 60}")
    
    signature = rsa.sign(message, private_key)
    print(f"🔑 Подпись (хеш, зашифрованный закрытым ключом):\n{signature}")
    
    # Проверка
    print(f"\n{'=' * 60}")
    print("ШАГ 2: ПРОВЕРКА ПОДПИСИ ОТКРЫТЫМ КЛЮЧОМ")
    print(f"{'=' * 60}")
    
    is_valid = rsa.verify_signature(message, signature, public_key)
    print(f"✅ Подпись верна: {is_valid}")
    
    # Попытка подделки
    print(f"\n{'=' * 60}")
    print("ШАГ 3: ПОПЫТКА ПОДДЕЛКИ")
    print(f"{'=' * 60}")
    
    fake_message = "Важное сообщение: перевод 9999$ на счет #99999"
    is_fake_valid = rsa.verify_signature(fake_message, signature, public_key)
    print(f"❌ Подпись для поддельного сообщения верна: {is_fake_valid}")
    print("   (должно быть False)")


def demo_hybrid_system():
    """
    Демонстрация гибридной криптосистемы (реальный мир)
    """
    print("\n" + "=" * 70)
    print("ГИБРИДНАЯ КРИПТОСИСТЕМА (RSA + СИММЕТРИЧНЫЙ АЛГОРИТМ)")
    print("=" * 70)
    
    print("\n📖 КАК РАБОТАЕТ В РЕАЛЬНОЙ ЖИЗНИ:")
    print("1. Генерируется случайный сессионный ключ (256 бит)")
    print("2. Большое сообщение шифруется СИММЕТРИЧНО (быстро)")
    print("3. Только сессионный ключ шифруется АСИММЕТРИЧНО (медленно)")
    print("4. Для расшифрования нужно сначала расшифровать ключ, затем данные")
    
    # Создаем RSA
    rsa = RSA(key_size = 512)
    public_key, private_key = rsa.generate_keys()
    
    # Большое сообщение
    message = """
    Это очень длинное сообщение, которое невозможно эффективно шифровать 
    через RSA напрямую. На практике RSA используется только для передачи 
    небольшого сессионного ключа (128-256 бит), а все данные шифруются 
    симметричными алгоритмами вроде AES. Такой подход называется 
    гибридной криптосистемой и используется в HTTPS, VPN, WhatsApp и т.д.
    """ * 3  # Увеличим для демонстрации
    
    print(f"\n📝 Размер сообщения: {len(message)} символов")
    
    # Сравнение времени
    print(f"\n{'=' * 60}")
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print(f"{'=' * 60}")
    
    # 1. Чистый RSA (только первая часть сообщения, т.к. RSA медленный)
    short_message = message[:50]
    print("\n1. ЧИСТЫЙ RSA (только 50 символов):")
    start = time.time()
    blocks, block_size, orig_len = rsa.encrypt(short_message, public_key)
    rsa_time = time.time() - start
    print(f"   Время шифрования: {rsa_time:.4f} сек")
    
    # 2. Гибридная схема
    print("\n2. ГИБРИДНАЯ СХЕМА (всё сообщение):")
    start = time.time()
    enc_data, enc_key = HybridCrypto.hybrid_encrypt(message, public_key)
    hybrid_time = time.time() - start
    print(f"   Время шифрования: {hybrid_time:.4f} сек")
    
    # Расшифрование гибридной схемы
    decrypted = HybridCrypto.hybrid_decrypt(enc_data, enc_key, private_key)
    print(f"   ✅ Расшифровано верно: {message == decrypted}")
    
    # Вывод сравнения
    if hybrid_time > 0:
        speedup = rsa_time / hybrid_time if rsa_time > 0 else 0
        print(f"\n📊 Итог: Гибридная схема быстрее в {speedup:.1f} раз")
    else:
        print(f"\n📊 Итог: Гибридная схема значительно быстрее")
    print("   (в реальности разница будет ещё больше, т.к. используется AES)")


def demo_key_exchange():
    """
    Демонстрация решения проблемы обмена ключами
    """
    print("\n" + "=" * 70)
    print("РЕШЕНИЕ ПРОБЛЕМЫ РАСПРЕДЕЛЕНИЯ КЛЮЧЕЙ")
    print("=" * 70)
    
    print("\n📜 ИСТОРИЧЕСКАЯ ПРОБЛЕМА:")
    print("   Банки отправляли ключи курьерами (как в вашем тексте)")
    print("   Это дорого, медленно и небезопасно")
    
    print("\n💡 РЕШЕНИЕ:")
    print("   Алиса генерирует пару ключей и публикует открытый ключ")
    print("   Боб шифрует сообщение открытым ключом Алисы")
    print("   Только Алиса может расшифровать своим закрытым ключом")
    
    # Создаем RSA
    rsa = RSA(key_size = 512)
    public_key, private_key = rsa.generate_keys()
    
    # Сценарий
    print("\n👤 АЛИСА (владелец закрытого ключа):")
    print(f"   Публикует открытый ключ: (e = {public_key[0]}, n = ...{str(public_key[1])[-10:]})")
    print(f"   Хранит в секрете закрытый ключ: (d = {private_key[0]}, n = ...{str(private_key[1])[-10:]})")
    
    print("\n👤 БОБ (отправитель):")
    message = "Секретный номер карты: 1234-5678-9012-3456"
    blocks, block_size, orig_len = rsa.encrypt(message, public_key)
    print(f"   Шифрует сообщение открытым ключом Алисы")
    print(f"   Отправляет зашифрованные блоки: {len(blocks)} блоков")
    print(f"   Первый блок: {blocks[0]}")
    
    print("\n👤 ЕВА (перехватчик):")
    print(f"   Перехватывает зашифрованные данные...")
    print(f"   Не может расшифровать без закрытого ключа Алисы ❌")
    
    print("\n👤 АЛИСА (получатель):")
    decrypted = rsa.decrypt(blocks, private_key, block_size, orig_len)
    print(f"   Расшифровывает своим закрытым ключом ✅")
    print(f"   Получает сообщение: {decrypted}")


def main():
    """
    Главная функция, запускающая все демонстрации
    """
    print("\n" + "=" * 70)
    print("АСИММЕТРИЧНОЕ ШИФРОВАНИЕ: ПОЛНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 70)
    print("Автор: на основе вашего текста о криптографии")
    print("=" * 70)
    
    # 1. Основное шифрование RSA
    rsa, public_key, private_key = demo_rsa_encryption()
    
    # 2. Цифровая подпись
    demo_digital_signature(rsa, public_key, private_key)
    
    # 3. Гибридная система
    demo_hybrid_system()
    
    # 4. Решение проблемы обмена ключами
    demo_key_exchange()
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ВЫВОДЫ ПО ТЕКСТУ:")
    print("=" * 70)
    print("1. Асимметричное шифрование решает проблему распределения ключей")
    print("2. Открытый ключ используется для шифрования, закрытый - для расшифрования")
    print("3. Цифровая подпись работает наоборот: подпись - закрытым, проверка - открытым")
    print("4. В реальности используется гибридный подход (RSA + AES)")
    print("5. Без асимметричной криптографии невозможен безопасный интернет")
    print("=" * 70)
    
    print("\n✅ Программа завершена успешно!")


if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости (опционально)
    random.seed(42)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()