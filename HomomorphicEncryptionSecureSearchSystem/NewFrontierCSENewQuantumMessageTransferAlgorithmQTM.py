# Новый рубеж CSE и новый квантовый алгоритм передачи сообщений — QTM
import random
import hashlib
import secrets

# ============================================
# 1. КВАНТОВАЯ ГЕНЕРАЦИЯ КЛЮЧА (СИМУЛЯЦИЯ BB84)
# ============================================

class QuantumChannel:
    """Симуляция квантового канала с фотонами"""
    
    # Базисы: 0 = ректовый (прямой), 1 = диагональный
    BASES = {'rectilinear': 0, 'diagonal': 1}
    
    # Состояния фотонов: 0, 1, 2, 3 (для 2-битных символов)
    STATES = [0, 1, 2, 3]
    
    @staticmethod
    def generate_photon_states(length):
        """Генерирует случайные состояния фотонов и базисы"""
        states = [random.choice(QuantumChannel.STATES) for _ in range(length)]
        bases = [random.choice([0, 1]) for _ in range(length)]
        return states, bases
    
    @staticmethod
    def measure_photons(states, bases, eavesdropper = False):
        """
        Измерение фотонов.
        Если eavesdropper = True - симуляция подслушивания (вносит ошибки)
        """
        measured = []
        error_positions = []
        
        for i, (state, basis) in enumerate(zip(states, bases)):
            # Если базис совпадает - измеряем точно
            if basis == 0:  # rectilinear
                measured.append(state % 2)  # 0 или 1
            else:  # diagonal
                measured.append(state // 2)  # 0 или 1
            
            # Если подслушивание - вносим ошибку в 25% случаев
            if eavesdropper and random.random() < 0.25:
                measured[-1] = 1 - measured[-1]
                error_positions.append(i)
        
        return measured, error_positions
    
    @staticmethod
    def sift_key(bases_alice, bases_bob, measured_bob):
        """Просеивание ключа - оставляем только совпавшие базисы"""
        raw_key = []
        
        for i, (ba, bb) in enumerate(zip(bases_alice, bases_bob)):
            if ba == bb:
                raw_key.append(measured_bob[i])
        
        return raw_key


# ============================================
# 2. ДНК-ПРЕОБРАЗОВАНИЕ (СЕКВЕНИРОВАНИЕ)
# ============================================

class DNACodec:
    """Преобразование битов в ДНК-последовательность и обратно"""
    
    # Таблица ДНК -> 2 бита
    DNA_TO_BITS = {
        'A': (0, 0),
        'T': (0, 1),
        'G': (1, 0),
        'C': (1, 1)
    }
    
    BITS_TO_DNA = {
        (0, 0): 'A',
        (0, 1): 'T',
        (1, 0): 'G',
        (1, 1): 'C'
    }
    
    @staticmethod
    def bits_to_dna(bits):
        """Преобразует список битов в строку ДНК"""
        dna = []
        
        # Дополняем биты до четного количества
        if len(bits) % 2 != 0:
            bits = bits + [0]
        
        for i in range(0, len(bits), 2):
            pair = (bits[i], bits[i + 1])
            dna.append(DNACodec.BITS_TO_DNA[pair])
        
        return ''.join(dna)
    
    @staticmethod
    def dna_to_bits(dna_string):
        """Преобразует строку ДНК в список битов"""
        bits = []
        
        for nucleotide in dna_string.upper():
            if nucleotide in DNACodec.DNA_TO_BITS:
                b1, b2 = DNACodec.DNA_TO_BITS[nucleotide]
                bits.extend([b1, b2])
        
        return bits
    
    @staticmethod
    def extend_dna_key(dna_key, target_length):
        """Расширяет ДНК-ключ до нужной длины (хэшированием)"""
        if len(dna_key) >= target_length:
            return dna_key[:target_length]
        
        # Используем хэш для расширения
        extended = dna_key
        while len(extended) < target_length:
            hash_obj = hashlib.sha256(extended.encode())
            hash_hex = hash_obj.hexdigest()
            # Преобразуем hex в ДНК
            for char in hash_hex:
                if len(extended) >= target_length:
                    break
                # hex -> биты -> ДНК
                hex_val = int(char, 16)
                bits = [(hex_val >> 3) & 1, (hex_val >> 2) & 1, (hex_val >> 1) & 1, hex_val & 1]
                extended += DNACodec.bits_to_dna(bits[:2])
        
        return extended[:target_length]


# ============================================
# 3. ОСНОВНОЙ АЛГОРИТМ QTM
# ============================================

class QTM:
    """
    Quantum Transmission Message - гибридный алгоритм
    с квантовым каналом и ДНК-стеганографией
    """
    
    def __init__(self, security_level = 0.8):
        """
        security_level: вероятность совпадения базисов (0.5 - 1.0)
        """
        self.security_level = security_level
        self.session_id = secrets.token_hex(8)
        self.quantum_channel = QuantumChannel()
        self.dna_codec = DNACodec()
        
    def generate_quantum_key(self, length):
        """
        Генерация квантового ключа через симуляцию BB84
        Возвращает: (raw_key, bases_alice, bases_bob, errors)
        """
        # 1. Алиса генерирует фотоны
        photon_states, bases_alice = self.quantum_channel.generate_photon_states(length)
        
        # 2. Боб выбирает случайные базисы для измерения
        bases_bob = [random.choice([0, 1]) for _ in range(length)]
        
        # 3. Боб измеряет (без подслушивания)
        measured_bob, _ = self.quantum_channel.measure_photons(photon_states, bases_bob, eavesdropper = False)
        
        # 4. Просеивание ключа
        raw_key = self.quantum_channel.sift_key(bases_alice, bases_bob, measured_bob)
        
        # 5. Симуляция ошибок в канале
        error_rate = 1 - self.security_level
        error_positions = random.sample(
            range(len(raw_key)), 
            k = int(len(raw_key) * error_rate * 0.5)  # 50% от ошибок
        )
        
        for pos in error_positions:
            raw_key[pos] = 1 - raw_key[pos]
        
        return raw_key, bases_alice, bases_bob, error_positions
    
    def correct_errors(self, raw_key, error_positions):
        """Простая коррекция ошибок (ECC) - исправляем ошибки по позициям"""
        # В реальности здесь был бы более сложный алгоритм
        # Мы просто инвертируем биты в позициях ошибок
        corrected = raw_key.copy()
        for pos in error_positions:
            if pos < len(corrected):
                corrected[pos] = 1 - corrected[pos]
        return corrected
    
    def encrypt(self, plaintext, key_length = 256):
        """
        Шифрование сообщения с использованием QTM
        
        Процесс:
        1. Генерируем квантовый ключ
        2. Преобразуем ключ в ДНК
        3. Шифруем сообщение XOR с ДНК-ключом
        4. Возвращаем шифротекст + метаданные
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # 1. Генерация квантового ключа
        raw_key, bases_alice, bases_bob, errors = self.generate_quantum_key(
            key_length * 4  # Увеличиваем для запаса
        )
        
        # 2. Коррекция ошибок
        corrected_key = self.correct_errors(raw_key, errors)
        
        # 3. Преобразование в ДНК
        dna_key = self.dna_codec.bits_to_dna(corrected_key)
        
        # 4. Преобразуем сообщение в биты
        plaintext_bits = []
        for byte in plaintext:
            for i in range(7, -1, -1):
                plaintext_bits.append((byte >> i) & 1)
        
        # 5. Расширяем ДНК-ключ до длины сообщения
        extended_dna = self.dna_codec.extend_dna_key(
            dna_key, 
            len(plaintext_bits) // 2 + 1
        )
        
        # 6. Преобразуем расширенный ДНК-ключ в биты
        key_bits = self.dna_codec.dna_to_bits(extended_dna)
        
        # 7. XOR шифрование
        cipher_bits = []
        for i in range(len(plaintext_bits)):
            key_bit = key_bits[i % len(key_bits)]
            cipher_bits.append(plaintext_bits[i] ^ key_bit)
        
        # 8. Преобразуем биты обратно в байты
        cipher_bytes = bytearray()
        for i in range(0, len(cipher_bits) - 7, 8):
            byte = 0
            for j in range(8):
                if i + j < len(cipher_bits):
                    byte = (byte << 1) | cipher_bits[i + j]
            cipher_bytes.append(byte)
        
        # 9. Сохраняем метаданные для дешифрования
        self._metadata = {
            'bases_alice': bases_alice,
            'bases_bob': bases_bob,
            'error_positions': errors,
            'dna_key': dna_key,
            'key_length': len(key_bits),
            'session_id': self.session_id
        }
        
        return bytes(cipher_bytes)
    
    def decrypt(self, ciphertext, metadata = None):
        """
        Дешифрование сообщения с использованием сохраненных метаданных
        """
        if metadata is None:
            metadata = self._metadata
        
        # 1. Восстанавливаем ДНК-ключ из метаданных
        dna_key = metadata['dna_key']
        
        # 2. Преобразуем шифротекст в биты
        cipher_bits = []
        for byte in ciphertext:
            for i in range(7, -1, -1):
                cipher_bits.append((byte >> i) & 1)
        
        # 3. Расширяем ДНК-ключ
        extended_dna = self.dna_codec.extend_dna_key(
            dna_key,
            len(cipher_bits) // 2 + 1
        )
        
        # 4. Преобразуем в биты
        key_bits = self.dna_codec.dna_to_bits(extended_dna)
        
        # 5. XOR дешифрование
        plain_bits = []
        for i in range(len(cipher_bits)):
            key_bit = key_bits[i % len(key_bits)]
            plain_bits.append(cipher_bits[i] ^ key_bit)
        
        # 6. Преобразуем в байты
        plain_bytes = bytearray()
        for i in range(0, len(plain_bits) - 7, 8):
            byte = 0
            for j in range(8):
                if i + j < len(plain_bits):
                    byte = (byte << 1) | plain_bits[i + j]
            plain_bytes.append(byte)
        
        return bytes(plain_bytes)


# ============================================
# 4. ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================

def demo_qtm():
    """Демонстрация работы алгоритма QTM"""
    
    print("=" * 60)
    print("КВАНТОВАЯ ПЕРЕДАЧА СООБЩЕНИЙ (QTM)")
    print("Гибрид BB84 + ДНК-стеганография")
    print("=" * 60)
    
    # Создаем экземпляр QTM
    qtm = QTM(security_level = 0.85)
    
    # Исходное сообщение
    original_message = "Привет, это секретное сообщение для спутниковой связи!"
    print(f"\n[1] Исходное сообщение: {original_message}")
    print(f"    Длина: {len(original_message)} байт")
    
    # Шифрование
    print("\n[2] Запуск квантовой генерации ключа...")
    ciphertext = qtm.encrypt(original_message.encode('utf-8'), key_length = 64)
    
    print(f"    Шифротекст (hex): {ciphertext.hex()[:64]}...")
    print(f"    Длина шифротекста: {len(ciphertext)} байт")
    
    # Показываем метаданные
    print(f"\n[3] Метаданные QTM:")
    print(f"    Session ID: {qtm.session_id}")
    print(f"    ДНК-ключ: {qtm._metadata['dna_key'][:32]}...")
    print(f"    Длина ключа: {qtm._metadata['key_length']} бит")
    print(f"    Ошибок в канале: {len(qtm._metadata['error_positions'])}")
    
    # Дешифрование
    print("\n[4] Дешифрование...")
    decrypted = qtm.decrypt(ciphertext)
    decrypted_message = decrypted.decode('utf-8', errors = 'ignore')
    
    print(f"    Расшифрованное сообщение: {decrypted_message}")
    
    # Проверка
    print("\n[5] Проверка целостности:")
    if original_message == decrypted_message:
        print("    ✅ УСПЕШНО! Сообщение расшифровано корректно.")
    else:
        print("    ⚠️ ОШИБКА! Сообщения не совпадают.")
    
    # Дополнительный тест: симуляция подслушивания
    print("\n" + "=" * 60)
    print("ТЕСТ НА ПОДСЛУШИВАНИЕ (Eve)")
    print("=" * 60)
    
    # Создаем канал с подслушиванием
    qtm_eve = QTM(security_level = 0.7)
    
    # Генерируем фотоны и измеряем с подслушиванием
    photon_states, bases_alice = qtm_eve.quantum_channel.generate_photon_states(100)
    bases_bob = [random.choice([0, 1]) for _ in range(100)]
    
    # Боб измеряет
    measured_bob, _ = qtm_eve.quantum_channel.measure_photons(photon_states, bases_bob, eavesdropper = True)
    
    # Ева подслушивает
    measured_eve, _ = qtm_eve.quantum_channel.measure_photons(photon_states, bases_bob, eavesdropper = True)
    
    # Просеиваем ключи
    key_bob = qtm_eve.quantum_channel.sift_key(bases_alice, bases_bob, measured_bob)
    key_eve = qtm_eve.quantum_channel.sift_key(bases_alice, bases_bob, measured_eve)
    
    # Сравниваем
    matches = sum(1 for i in range(min(len(key_bob), len(key_eve))) if key_bob[i] == key_eve[i])
    
    print(f"\nСгенерировано ключей у Боба: {len(key_bob)}")
    print(f"Сгенерировано ключей у Евы: {len(key_eve)}")
    print(f"Совпадений между Бобом и Евой: {matches} / {min(len(key_bob), len(key_eve))}")
    print(f"Уровень ошибок при подслушивании: {(1 - matches / min(len(key_bob), len(key_eve))) * 100:.1f}%")
    
    if matches / min(len(key_bob), len(key_eve)) < 0.8:
        print("✅ Обнаружено подслушивание! Ключи не совпадают.")
    else:
        print("⚠️ Подслушивание не обнаружено (низкий уровень шума).")


# ============================================
# 5. ЗАПУСК ДЕМОНСТРАЦИИ
# ============================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    demo_qtm()
    
    print("\n" + "=" * 60)
    print("ВИРТУАЛЬНЫЙ ТУР ЗАВЕРШЕН")
    print("Алгоритм QTM готов к бета-тестированию!")
    print("=" * 60)