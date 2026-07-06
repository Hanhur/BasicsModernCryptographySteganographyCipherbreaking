# Потоковые шифры 
"""
Потоковые шифры
Реализация на основе главы 8.4
"""

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii


class StreamCipherOFB:
    """
    Режим OFB (Output FeedBack) на основе AES
    """
    def __init__(self, key, iv):
        """
        key: секретный ключ (16, 24 или 32 байта)
        iv: инициализирующий вектор (16 байт)
        """
        # Проверяем длину ключа
        if len(key) not in [16, 24, 32]:
            raise ValueError("Ключ должен быть 16, 24 или 32 байта")
        
        # Проверяем длину IV
        if len(iv) != AES.block_size:
            raise ValueError(f"IV должен быть {AES.block_size} байт")
        
        self.key = key
        self.iv = iv
        self.block_size = AES.block_size  # 16 байт
        self.cipher = AES.new(key, AES.MODE_ECB)
        self.y = iv  # текущее состояние
        
    def _generate_keystream(self, length):
        """
        Генерирует псевдослучайную последовательность z
        длиной length байт
        """
        keystream = b''
        y = self.y
        
        while len(keystream) < length:
            # Yi = EK(Yi-1)
            # y всегда имеет длину block_size, поэтому ECB работает корректно
            y = self.cipher.encrypt(y)
            # zi = r старших бит Yi (берем весь блок)
            keystream += y
            
        return keystream[:length]
    
    def encrypt(self, plaintext):
        """
        Шифрование: yi = xi ⊕ zi
        """
        keystream = self._generate_keystream(len(plaintext))
        ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])
        return ciphertext
    
    def decrypt(self, ciphertext):
        """
        Дешифрование: xi = yi ⊕ zi
        """
        # Для OFB дешифрование идентично шифрованию
        return self.encrypt(ciphertext)
    
    def reset(self):
        """Сброс генератора в начальное состояние"""
        self.y = self.iv


class StreamCipherCTR:
    """
    Режим CTR (Counter) на основе AES
    """
    def __init__(self, key, iv):
        """
        key: секретный ключ (16, 24 или 32 байта)
        iv: начальное значение счетчика (16 байт)
        """
        # Проверяем длину ключа
        if len(key) not in [16, 24, 32]:
            raise ValueError("Ключ должен быть 16, 24 или 32 байта")
        
        # Проверяем длину IV
        if len(iv) != AES.block_size:
            raise ValueError(f"IV должен быть {AES.block_size} байт")
        
        self.key = key
        self.iv = iv
        self.block_size = AES.block_size
        self.cipher = AES.new(key, AES.MODE_ECB)
        self.counter = int.from_bytes(iv, 'big')
        
    def _generate_keystream(self, length):
        """
        Генерирует псевдослучайную последовательность z
        длиной length байт
        """
        keystream = b''
        counter = self.counter
        
        while len(keystream) < length:
            # zi = EK(Y0 + i)
            counter_bytes = counter.to_bytes(self.block_size, 'big')
            block = self.cipher.encrypt(counter_bytes)
            keystream += block
            counter += 1
            
        return keystream[:length]
    
    def encrypt(self, plaintext):
        """
        Шифрование: yi = xi ⊕ zi
        """
        keystream = self._generate_keystream(len(plaintext))
        ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])
        return ciphertext
    
    def decrypt(self, ciphertext):
        """
        Дешифрование: xi = yi ⊕ zi
        """
        return self.encrypt(ciphertext)
    
    def reset(self):
        """Сброс генератора в начальное состояние"""
        self.counter = int.from_bytes(self.iv, 'big')


class RC4:
    """
    Алгоритм RC4 (Rivest Cipher 4)
    Работает с n-битовыми словами (по умолчанию n=8)
    """
    def __init__(self, key, n = 8):
        """
        key: секретный ключ (байтовая строка)
        n: размер слова в битах (обычно 8)
        """
        self.n = n
        self.mod = 1 << n  # 2^n
        self.key = key
        self.S = list(range(self.mod))
        self.i = 0
        self.j = 0
        self._ksa()  # инициализация
        
    def _ksa(self):
        """
        Key Scheduling Algorithm (KSA)
        Начальное перемешивание таблицы S
        """
        j = 0
        L = len(self.key)
        
        for i in range(self.mod):
            j = (j + self.S[i] + self.key[i % L]) % self.mod
            # Swap S[i] и S[j]
            self.S[i], self.S[j] = self.S[j], self.S[i]
            
        self.i = 0
        self.j = 0
        
    def _prga(self):
        """
        Pseudo-Random Generation Algorithm (PRGA)
        Генерация очередного псевдослучайного слова zi
        """
        self.i = (self.i + 1) % self.mod
        self.j = (self.j + self.S[self.i]) % self.mod
        # Swap S[i] и S[j]
        self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]
        t = (self.S[self.i] + self.S[self.j]) % self.mod
        return self.S[t]
    
    def generate_keystream(self, length):
        """
        Генерирует псевдослучайную последовательность zi
        длиной length слов (байт)
        """
        keystream = bytearray()
        for _ in range(length):
            keystream.append(self._prga())
        return bytes(keystream)
    
    def encrypt(self, plaintext):
        """
        Шифрование: yi = xi ⊕ zi
        plaintext: байтовая строка
        """
        keystream = self.generate_keystream(len(plaintext))
        ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])
        return ciphertext
    
    def decrypt(self, ciphertext):
        """
        Дешифрование: xi = yi ⊕ zi
        """
        return self.encrypt(ciphertext)
    
    def reset(self):
        """Сброс генератора в начальное состояние"""
        self.S = list(range(self.mod))
        self._ksa()


def demonstrate_stream_ciphers():
    """Демонстрация работы всех потоковых шифров"""
    
    print("=" * 70)
    print("ПОТОКОВЫЕ ШИФРЫ")
    print("=" * 70)
    
    # Исходное сообщение
    plaintext = b"Hello, World! This is a test message for stream ciphers."
    print(f"\nИсходное сообщение: {plaintext.decode('utf-8')}")
    print(f"Длина сообщения: {len(plaintext)} байт")
    
    # 1. OFB
    print("\n" + "-" * 70)
    print("1. РЕЖИМ OFB (Output Feedback)")
    print("-" * 70)
    
    key = os.urandom(16)  # 128-битный ключ
    iv = os.urandom(16)   # 128-битный IV
    
    try:
        ofb = StreamCipherOFB(key, iv)
        ciphertext_ofb = ofb.encrypt(plaintext)
        print(f"Зашифрованное сообщение (hex): {binascii.hexlify(ciphertext_ofb)[:50]}...")
        
        ofb.reset()
        decrypted_ofb = ofb.decrypt(ciphertext_ofb)
        print(f"Расшифрованное сообщение: {decrypted_ofb.decode('utf-8')}")
        print(f"Успешно: {plaintext == decrypted_ofb}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # 2. CTR
    print("\n" + "-" * 70)
    print("2. РЕЖИМ CTR (Counter)")
    print("-" * 70)
    
    try:
        ctr = StreamCipherCTR(key, iv)
        ciphertext_ctr = ctr.encrypt(plaintext)
        print(f"Зашифрованное сообщение (hex): {binascii.hexlify(ciphertext_ctr)[:50]}...")
        
        ctr.reset()
        decrypted_ctr = ctr.decrypt(ciphertext_ctr)
        print(f"Расшифрованное сообщение: {decrypted_ctr.decode('utf-8')}")
        print(f"Успешно: {plaintext == decrypted_ctr}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # 3. RC4
    print("\n" + "-" * 70)
    print("3. АЛГОРИТМ RC4")
    print("-" * 70)
    
    rc4_key = b"SecretKey123"  # ключ для RC4
    rc4 = RC4(rc4_key)
    ciphertext_rc4 = rc4.encrypt(plaintext)
    print(f"Зашифрованное сообщение (hex): {binascii.hexlify(ciphertext_rc4)[:50]}...")
    
    rc4.reset()
    decrypted_rc4 = rc4.decrypt(ciphertext_rc4)
    print(f"Расшифрованное сообщение: {decrypted_rc4.decode('utf-8')}")
    print(f"Успешно: {plaintext == decrypted_rc4}")
    
    return plaintext, key, iv, rc4_key


def demonstrate_problem_reusing_keystream():
    """
    Демонстрация проблемы повторного использования ключевого потока
    (как описано в тексте)
    """
    print("\n" + "=" * 70)
    print("ПРОБЛЕМА ПОВТОРНОГО ИСПОЛЬЗОВАНИЯ КЛЮЧЕВОГО ПОТОКА")
    print("=" * 70)
    
    # Два разных сообщения
    message1 = b"Attack at dawn! Confidential data."
    message2 = b"Defend the castle! Top secret info."
    
    print(f"\nСообщение 1: {message1.decode('utf-8')}")
    print(f"Сообщение 2: {message2.decode('utf-8')}")
    
    # Используем один и тот же ключ и IV (ОШИБКА!)
    # Ключ должен быть 16 байт
    key = b"FixedKey12345678"  # 16 байт
    iv = b"FixedIV12345678"   # 16 байт
    
    print("\n[ОШИБКА] Используем ОДИНАКОВЫЙ ключевой поток для обоих сообщений")
    
    try:
        # Шифруем с одинаковым ключом
        ofb1 = StreamCipherOFB(key, iv)
        ciphertext1 = ofb1.encrypt(message1)
        
        ofb2 = StreamCipherOFB(key, iv)
        ciphertext2 = ofb2.encrypt(message2)
        
        print(f"Шифротекст 1 (hex): {binascii.hexlify(ciphertext1)[:30]}...")
        print(f"Шифротекст 2 (hex): {binascii.hexlify(ciphertext2)[:30]}...")
        
        # Атака: XOR шифротекстов
        # Получаем: c1 ⊕ c2 = (m1 ⊕ z) ⊕ (m2 ⊕ z) = m1 ⊕ m2
        xor_ciphertexts = bytes([c1 ^ c2 for c1, c2 in zip(ciphertext1, ciphertext2)])
        
        print(f"\nРезультат XOR шифротекстов (hex): {binascii.hexlify(xor_ciphertexts)[:30]}...")
        print("Это эквивалентно XOR исходных сообщений: m1 ⊕ m2")
        
        # Показываем, что это действительно m1 ⊕ m2
        xor_messages = bytes([m1 ^ m2 for m1, m2 in zip(message1, message2)])
        print(f"XOR исходных сообщений (hex): {binascii.hexlify(xor_messages)[:30]}...")
        print(f"Совпадают: {xor_ciphertexts == xor_messages}")
        
        print("\n[ВЫВОД] Зная m1 ⊕ m2, можно восстановить оба сообщения")
        print("статистическим анализом из-за избыточности текстов!")
        print("НИКОГДА не используйте один ключевой поток дважды!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Проверьте, что ключ и IV имеют правильную длину (16 байт)")


def demonstrate_rc4_from_example():
    """
    Демонстрация RC4 из примера в тексте
    (n=3, K=25, L=2)
    """
    print("\n" + "=" * 70)
    print("ПРИМЕР RC4 ИЗ ТЕКСТА")
    print("=" * 70)
    
    # Из примера: n=3, K=25 (в бинарном виде: 11001)
    # L=2, значит ключ [2, 5] 
    # В тексте используется K=25, и показано K=[2,5]
    
    print("\nПараметры:")
    print("  n = 3 (размер слова 3 бита)")
    print("  K = 25 (ключ интерпретируется как K0 = 2, K1 = 5)")
    print("  L = 2 (длина ключа в словах)")
    print("  mod = 8 (2 ^ n)")
    
    # Создаем ключ как байты [2, 5]
    key = bytes([2, 5])
    
    rc4 = RC4(key, n=3)
    
    print("\nНачальное состояние S:", rc4.S)
    
    # Генерируем первые 6 слов как в примере
    print("\nГенерация псевдослучайной последовательности:")
    print("(сравните с примером в тексте)")
    
    generated = []
    for i in range(6):
        z = rc4._prga()
        generated.append(z)
        print(f"  z{i + 1} = {z} (двоичный: {z:03b})")
    
    print(f"\nПолученная последовательность z = {generated}")
    print("В двоичном виде:", ' '.join(f'{z:03b}' for z in generated))
    
    # Если бы мы шифровали текст, то каждый символ (3 бита) XOR-ился бы с zi
    print("\nПример шифрования (как в формуле 8.12):")
    # Предположим, что исходное сообщение - байты 0,1,2,3,4,5 (как 3-битные числа)
    plaintext = bytes([0, 1, 2, 3, 4, 5])
    print(f"  Исходное сообщение (3-битные): {[p for p in plaintext]}")
    print(f"  Ключевой поток: {generated}")
    
    ciphertext = bytes([p ^ z for p, z in zip(plaintext, generated)])
    print(f"  Зашифрованное: {[c for c in ciphertext]}")
    
    rc4.reset()
    decrypted = bytes([c ^ z for c, z in zip(ciphertext, generated)])
    print(f"  Расшифрованное: {[d for d in decrypted]}")
    print(f"  Успешно: {plaintext == decrypted}")


def main():
    """Главная функция"""
    try:
        # Демонстрация работы всех шифров
        demonstrate_stream_ciphers()
        
        # Демонстрация проблемы повторного использования ключа
        demonstrate_problem_reusing_keystream()
        
        # Демонстрация RC4 из примера
        demonstrate_rc4_from_example()
        
        print("\n" + "=" * 70)
        print("ЗАКЛЮЧЕНИЕ")
        print("=" * 70)
        print("""
        1. Потоковые шифры используют псевдослучайные последовательности (не случайные)
        2. Они НЕ являются совершенно секретными, но практически стойкими
        3. OFB и CTR - режимы блочных шифров для создания потоковых
        4. RC4 - быстрый алгоритм, специально разработанный для потоковых шифров
        5. НИКОГДА не используйте один ключевой поток дважды!
        6. Для каждого сообщения нужны разные K и/или Y0
        """)
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("\nУбедитесь, что установлена библиотека pycryptodome:")
        print("pip install pycryptodome")


if __name__ == "__main__":
    main()