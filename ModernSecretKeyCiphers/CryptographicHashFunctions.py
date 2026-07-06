# Криптографические хеш-функции 
"""
Криптографическая хеш-функция на основе блочного шифра
Реализация двух алгоритмов из раздела 8.5

Алгоритм 1: h = E_h(X_i) XOR X_i  (ключ = предыдущий хеш)
Алгоритм 2: h = E_{X_i}(h) XOR h  (ключ = блок сообщения)
"""

import struct
import hashlib  # только для сравнения, не используется в основной логике


class SimpleBlockCipher:
    """
    Упрощённый учебный блочный шифр для демонстрации.
    Размер блока: 64 бита (8 байт)
    Размер ключа: 64 бита (8 байт)
    
    Реальные шифры (AES, ГОСТ 28147-89) работают аналогично,
    но с более сложными преобразованиями.
    """
    
    BLOCK_SIZE = 8  # 64 бита
    KEY_SIZE = 8     # 64 бита
    ROUNDS = 8      # количество раундов
    
    def __init__(self):
        # Фиксированные константы для раундов (как в реальных шифрах)
        self.round_constants = [0x3C, 0x5A, 0x7E, 0x9F, 0xB3, 0xC7, 0xDB, 0xEF]
    
    def _bytes_to_blocks(self, data):
        """Преобразует байты в список 64-битных блоков"""
        blocks = []
        for i in range(0, len(data), self.BLOCK_SIZE):
            block = data[i:i + self.BLOCK_SIZE]
            if len(block) < self.BLOCK_SIZE:
                # Дополнение нулями
                block = block + b'\x00' * (self.BLOCK_SIZE - len(block))
            blocks.append(block)
        return blocks
    
    def _xor_bytes(self, a, b):
        """Побайтовый XOR двух байтовых строк"""
        return bytes(x ^ y for x, y in zip(a, b))
    
    def _key_schedule(self, key):
        """Разворачивание ключа для раундов"""
        # Простое разворачивание: каждый раунд использует циклический сдвиг
        round_keys = []
        for r in range(self.ROUNDS):
            # XOR с константой и циклический сдвиг
            round_key = bytes(
                (key[i] ^ self.round_constants[r]) for i in range(len(key))
            )
            # Циклический сдвиг вправо на r бит
            round_key = self._rot_right(round_key, r % 8)
            round_keys.append(round_key)
        return round_keys
    
    def _rot_right(self, data, shift):
        """Циклический сдвиг вправо на shift бит"""
        if shift == 0:
            return data
        # Преобразуем в число, делаем сдвиг, возвращаем обратно
        num = int.from_bytes(data, byteorder = 'big')
        bits = len(data) * 8
        num = ((num >> shift) | (num << (bits - shift))) & ((1 << bits) - 1)
        return num.to_bytes(len(data), byteorder = 'big')
    
    def _rot_left(self, data, shift):
        """Циклический сдвиг влево на shift бит"""
        if shift == 0:
            return data
        num = int.from_bytes(data, byteorder = 'big')
        bits = len(data) * 8
        num = ((num << shift) | (num >> (bits - shift))) & ((1 << bits) - 1)
        return num.to_bytes(len(data), byteorder = 'big')
    
    def _feistel_round(self, block, round_key):
        """Один раунд шифрования (сеть Фейстеля)"""
        # Разбиваем на левую и правую половины
        half = len(block) // 2
        left = block[:half]
        right = block[half:]
        
        # Функция F: XOR с ключом, замена байтов (S-блок)
        # Используем простую замену с циклическим сдвигом
        f_result = self._xor_bytes(right, round_key[:len(right)])
        # Применяем нелинейное преобразование: заменяем каждый байт
        f_result = bytes((b * 7 + 3) % 256 for b in f_result)
        # Перестановка: циклический сдвиг
        f_result = self._rot_left(f_result, 3)
        
        # Новый правый блок = старый левый XOR результат функции
        new_right = self._xor_bytes(left, f_result)
        # Новый левый блок = старый правый
        new_left = right
        
        return new_left + new_right
    
    def encrypt_block(self, plaintext, key):
        """
        Шифрование одного блока (64 бита)
        plaintext: bytes (8 байт)
        key: bytes (8 байт)
        return: bytes (8 байт) - зашифрованный блок
        """
        if len(plaintext) != self.BLOCK_SIZE or len(key) != self.KEY_SIZE:
            raise ValueError(f"Блок и ключ должны быть размером {self.BLOCK_SIZE} байт")
        
        block = plaintext
        round_keys = self._key_schedule(key)
        
        # Применяем раунды шифрования
        for r in range(self.ROUNDS):
            block = self._feistel_round(block, round_keys[r])
        
        return block
    
    def encrypt(self, plaintext, key):
        """
        Шифрование сообщения произвольной длины (режим ECB для простоты)
        """
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"Ключ должен быть размером {self.KEY_SIZE} байт")
        
        blocks = self._bytes_to_blocks(plaintext)
        ciphertext = b''.join(self.encrypt_block(block, key) for block in blocks)
        return ciphertext


class CryptographicHash:
    """
    Криптографическая хеш-функция на основе блочного шифра
    """
    
    def __init__(self, block_cipher = None):
        self.cipher = block_cipher or SimpleBlockCipher()
        self.block_size = self.cipher.BLOCK_SIZE
        self.hash_size = self.block_size  # размер хеша равен размеру блока
    
    def _pad_message(self, message, block_size):
        """
        Дополнение сообщения до кратности block_size
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Добавляем длину сообщения в конец (как в алгоритмах MD/SHA)
        msg_len = len(message)
        len_bytes = struct.pack('>Q', msg_len)  # 8 байт для длины
        
        # Дополняем до кратности block_size
        padding_len = (block_size - (len(message) + len(len_bytes)) % block_size) % block_size
        padding = b'\x00' * padding_len
        
        return message + padding + len_bytes
    
    def _split_into_blocks(self, data, block_size):
        """Разбивает данные на блоки фиксированного размера"""
        blocks = []
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            if len(block) < block_size:
                block = block + b'\x00' * (block_size - len(block))
            blocks.append(block)
        return blocks
    
    def hash_algorithm1(self, message):
        """
        Алгоритм 1: h ← E_h(Xi) ⊕ Xi
        Где Xi - блок сообщения, h - предыдущее значение хеша (ключ)
        
        Требование: длина ключа шифра = длина блока
        """
        # Дополняем сообщение
        padded = self._pad_message(message, self.block_size)
        blocks = self._split_into_blocks(padded, self.block_size)
        
        # Инициализация хеша нулевым блоком
        h = b'\x00' * self.block_size
        
        # Итерационный процесс
        for i, block in enumerate(blocks):
            # h = E_h(block) XOR block
            encrypted = self.cipher.encrypt_block(block, h)  # ключ = h
            h = bytes(a ^ b for a, b in zip(encrypted, block))
        
        return h.hex()
    
    def hash_algorithm2(self, message):
        """
        Алгоритм 2: h ← E_{Xi}(h) ⊕ h
        Где Xi - блок сообщения (ключ), h - предыдущее значение хеша
        
        Используется, когда длина ключа шифра > длины блока
        """
        # Дополняем сообщение
        padded = self._pad_message(message, self.cipher.KEY_SIZE)  # ключ = блок
        blocks = self._split_into_blocks(padded, self.cipher.KEY_SIZE)
        
        # Инициализация хеша нулевым блоком
        h = b'\x00' * self.block_size
        
        # Итерационный процесс
        for i, block in enumerate(blocks):
            # h = E_{block}(h) XOR h
            encrypted = self.cipher.encrypt_block(h, block)  # ключ = block
            h = bytes(a ^ b for a, b in zip(encrypted, h))
        
        return h.hex()
    
    def hash(self, message, algorithm = 1):
        """
        Универсальный метод хеширования
        algorithm: 1 или 2
        """
        if algorithm == 1:
            return self.hash_algorithm1(message)
        elif algorithm == 2:
            return self.hash_algorithm2(message)
        else:
            raise ValueError("Алгоритм должен быть 1 или 2")


def demonstrate():
    """Демонстрация работы программы"""
    
    print("=" * 70)
    print("КРИПТОГРАФИЧЕСКАЯ ХЕШ-ФУНКЦИЯ НА ОСНОВЕ БЛОЧНОГО ШИФРА")
    print("=" * 70)
    
    # Создаём экземпляр хеш-функции
    hasher = CryptographicHash()
    
    # Тестовые сообщения
    messages = [
        "Hello, World!",
        "Hello, World?",  # Отличается одним символом
        "Криптография",
        "Криптографiя",   # Отличается одной буквой
        "A" * 100,        # Длинное сообщение
    ]
    
    print("\n1. ДЕМОНСТРАЦИЯ АЛГОРИТМА 1 (ключ = предыдущий хеш)")
    print("-" * 70)
    print(f"{'Сообщение':<20} {'Хеш (алгоритм 1)':<40}")
    print("-" * 70)
    
    prev_hash = None
    for msg in messages[:3]:
        hash_val = hasher.hash(msg, algorithm = 1)
        display = msg[:17] + "..." if len(msg) > 17 else msg
        print(f"{display:<20} {hash_val}")
        if prev_hash:
            # Проверяем, что хеши разные для разных сообщений
            if hash_val != prev_hash:
                print(f"{'':<20} ✓ Хеш изменился (как и ожидалось)")
        prev_hash = hash_val
    
    print("\n2. ДЕМОНСТРАЦИЯ АЛГОРИТМА 2 (ключ = блок сообщения)")
    print("-" * 70)
    print(f"{'Сообщение':<20} {'Хеш (алгоритм 2)':<40}")
    print("-" * 70)
    
    for msg in messages[:3]:
        hash_val = hasher.hash(msg, algorithm = 2)
        display = msg[:17] + "..." if len(msg) > 17 else msg
        print(f"{display:<20} {hash_val}")
    
    print("\n3. СРАВНЕНИЕ АЛГОРИТМОВ ДЛЯ ОДНОГО СООБЩЕНИЯ")
    print("-" * 70)
    msg = "Тестовое сообщение"
    h1 = hasher.hash(msg, algorithm = 1)
    h2 = hasher.hash(msg, algorithm = 2)
    print(f"Сообщение: {msg}")
    print(f"Хеш (алг. 1): {h1}")
    print(f"Хеш (алг. 2): {h2}")
    print(f"Хеши разные: {h1 != h2}")
    
    print("\n4. ПРОВЕРКА ЛАВИННОГО ЭФФЕКТА (изменение 1 символа)")
    print("-" * 70)
    msg1 = "Hello World"
    msg2 = "Hello Worle"  # Изменена последняя буква
    
    h1a = hasher.hash(msg1, algorithm = 1)
    h1b = hasher.hash(msg2, algorithm = 1)
    h2a = hasher.hash(msg1, algorithm = 2)
    h2b = hasher.hash(msg2, algorithm = 2)
    
    print(f"'{msg1}' -> {h1a[:16]}...")
    print(f"'{msg2}' -> {h1b[:16]}...")
    print(f"Алг. 1: хеши {'разные' if h1a != h1b else 'одинаковые'} (должны быть разные)")
    print(f"Алг. 2: хеши {'разные' if h2a != h2b else 'одинаковые'} (должны быть разные)")
    
    print("\n5. ТЕСТ НА ДЛИННОМ СООБЩЕНИИ (100 символов 'A')")
    print("-" * 70)
    long_msg = "A" * 100
    h_long = hasher.hash(long_msg, algorithm = 1)
    print(f"Длина сообщения: {len(long_msg)} символов")
    print(f"Хеш (алг. 1): {h_long}")
    print(f"Размер хеша: {len(h_long) // 2} байт ({len(h_long) * 4} бит)")
    
    print("\n" + "=" * 70)
    print("ПРИМЕЧАНИЕ:")
    print("1. Используется упрощённый учебный блочный шифр (не для реального применения)")
    print("2. Реальные стандарты (ГОСТ Р 34.11-94, SHA-2) используют более сложные алгоритмы")
    print("3. В реальности используются блочные шифры как AES, Кузнечик и другие")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate()