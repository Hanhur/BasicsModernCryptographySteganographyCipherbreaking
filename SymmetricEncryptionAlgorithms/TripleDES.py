# Triple DES
"""
Упрощенная учебная реализация Triple DES (3DES)
Демонстрирует три этапа шифрования и расшифрования
без использования внешних библиотек (numpy не используется)
"""

import struct
import os

# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БИТАМИ И БАЙТАМИ
# =========================================================

def bytes_to_bits(data):
    """Преобразует байты в список битов (0 и 1)"""
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_bytes(bits):
    """Преобразует список битов обратно в байты"""
    if len(bits) % 8 != 0:
        raise ValueError("Количество битов должно быть кратно 8")
    
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        bytes_data.append(byte)
    return bytes(bytes_data)

def xor_bits(bits1, bits2):
    """Побитовое XOR двух списков битов"""
    if len(bits1) != len(bits2):
        raise ValueError("Длины битовых последовательностей должны совпадать")
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

def split_64bit_block(block_bits):
    """Разбивает 64-битный блок на левую и правую половины (по 32 бита)"""
    if len(block_bits) != 64:
        raise ValueError("Блок должен быть 64 бита")
    return block_bits[:32], block_bits[32:]

def merge_halves(left, right):
    """Объединяет левую и правую половины в 64-битный блок"""
    return left + right

def pad_to_64bit(data):
    """
    Дополняет данные до кратности 64 битам (8 байт)
    Использует PKCS#7 паддинг
    """
    pad_len = 8 - (len(data) % 8)
    if pad_len == 8:
        pad_len = 0  # Если данные уже кратны 8, не добавляем блок
    return data + bytes([pad_len] * pad_len) if pad_len > 0 else data

def unpad(data):
    """Удаляет PKCS#7 паддинг"""
    if len(data) == 0:
        return data
    pad_len = data[-1]
    if pad_len > 8:
        raise ValueError("Некорректный паддинг")
    return data[:-pad_len] if pad_len > 0 else data

# =========================================================
# УПРОЩЕННЫЙ АЛГОРИТМ DES (ДЛЯ ДЕМОНСТРАЦИИ 3DES)
# =========================================================

class SimpleDES:
    """
    Упрощенная реализация DES для демонстрации 3DES
    Использует XOR с раундовыми ключами вместо сложных S-боксов
    """
    
    def __init__(self, key):
        """
        key: 8 байт (64 бита) - ключ DES
        """
        if len(key) != 8:
            raise ValueError("Ключ DES должен быть 8 байт (64 бита)")
        self.key_bits = bytes_to_bits(key)
        self.round_keys = self._generate_round_keys()
    
    def _generate_round_keys(self):
        """
        Генерирует 16 раундовых ключей по 48 бит
        (упрощенная версия для демонстрации)
        """
        round_keys = []
        # Для простоты используем циклический сдвиг битов ключа
        key = self.key_bits.copy()
        
        for round_num in range(16):
            # Сдвигаем ключ влево на 1 бит (циклически)
            shift = 1
            key = key[shift:] + key[:shift]
            
            # Берем первые 48 бит как раундовый ключ
            round_key = key[:48]
            round_keys.append(round_key)
        
        return round_keys
    
    def _feistel_function(self, half_block, round_key):
        """
        Функция Фейстеля: принимает 32 бита и раундовый ключ,
        возвращает 32 бита
        """
        # Расширяем 32 бита до 48 бит (простое дублирование для демо)
        expanded = []
        for i in range(48):
            expanded.append(half_block[i % 32])
        
        # XOR с раундовым ключом
        xored = xor_bits(expanded, round_key)
        
        # Сжимаем обратно до 32 бит (берем первые 32)
        return xored[:32]
    
    def _des_round(self, left, right, round_key):
        """Один раунд сети Фейстеля"""
        new_left = right
        new_right = xor_bits(left, self._feistel_function(right, round_key))
        return new_left, new_right
    
    def encrypt_block(self, block_bits):
        """
        Шифрует один 64-битный блок
        """
        if len(block_bits) != 64:
            raise ValueError("Блок должен быть 64 бита")
        
        # Начальная перестановка (пропускаем для простоты)
        left, right = split_64bit_block(block_bits)
        
        # 16 раундов
        for i in range(16):
            left, right = self._des_round(left, right, self.round_keys[i])
        
        # Финальная перестановка (меняем местами left и right)
        result = merge_halves(right, left)
        return result
    
    def decrypt_block(self, block_bits):
        """
        Расшифровывает один 64-битный блок (обратный порядок ключей)
        """
        if len(block_bits) != 64:
            raise ValueError("Блок должен быть 64 бита")
        
        # Начальная перестановка (пропускаем для простоты)
        left, right = split_64bit_block(block_bits)
        
        # 16 раундов (ключи в обратном порядке)
        for i in range(15, -1, -1):
            left, right = self._des_round(left, right, self.round_keys[i])
        
        # Финальная перестановка
        result = merge_halves(right, left)
        return result

# =========================================================
# TRIPLE DES (3DES)
# =========================================================

class TripleDES:
    """
    Реализация Triple DES с тремя ключами (K1, K2, K3)
    Шифрование: E(K1) -> D(K2) -> E(K3)
    Расшифрование: D(K3) -> E(K2) -> D(K1)
    """
    
    def __init__(self, key1, key2, key3):
        """
        key1, key2, key3: 8 байт каждый (64 бита)
        """
        self.des1 = SimpleDES(key1)
        self.des2 = SimpleDES(key2)
        self.des3 = SimpleDES(key3)
    
    def encrypt(self, plaintext):
        """
        Шифрование данных (произвольная длина)
        1. Шифрование блоков открытого текста с помощью DES и ключа K1
        2. Расшифровка результата шага 1 с помощью DES и ключа K2
        3. Шифрование результата шага 2 с помощью DES и ключа K3
        """
        # Дополняем данные до кратности 64 битам
        padded = pad_to_64bit(plaintext)
        
        ciphertext = bytearray()
        
        # Обрабатываем блоки по 8 байт (64 бита)
        for i in range(0, len(padded), 8):
            block = padded[i:i + 8]
            block_bits = bytes_to_bits(block)
            
            print(f"\n{'=' * 60}")
            print(f"Обработка блока {i // 8 + 1}: {block.hex().upper()}")
            
            # ШАГ 1: Шифрование с K1
            print(f"\n[Шаг 1] Шифрование с K1")
            step1_bits = self.des1.encrypt_block(block_bits)
            step1_bytes = bits_to_bytes(step1_bits)
            print(f"  Результат: {step1_bytes.hex().upper()}")
            
            # ШАГ 2: Расшифровка с K2
            print(f"\n[Шаг 2] Расшифровка с K2")
            step2_bits = self.des2.decrypt_block(step1_bits)
            step2_bytes = bits_to_bytes(step2_bits)
            print(f"  Результат: {step2_bytes.hex().upper()}")
            
            # ШАГ 3: Шифрование с K3
            print(f"\n[Шаг 3] Шифрование с K3")
            step3_bits = self.des3.encrypt_block(step2_bits)
            step3_bytes = bits_to_bytes(step3_bits)
            print(f"  Результат (шифротекст): {step3_bytes.hex().upper()}")
            
            ciphertext.extend(step3_bytes)
        
        return bytes(ciphertext)
    
    def decrypt(self, ciphertext):
        """
        Расшифрование данных
        1. Расшифровка с K3
        2. Шифрование с K2
        3. Расшифровка с K1
        """
        if len(ciphertext) % 8 != 0:
            raise ValueError("Длина шифротекста должна быть кратна 8 байтам")
        
        plaintext = bytearray()
        
        for i in range(0, len(ciphertext), 8):
            block = ciphertext[i:i + 8]
            block_bits = bytes_to_bits(block)
            
            print(f"\n{'=' * 60}")
            print(f"Расшифровка блока {i // 8 + 1}: {block.hex().upper()}")
            
            # ШАГ 1: Расшифровка с K3
            print(f"\n[Шаг 1] Расшифровка с K3")
            step1_bits = self.des3.decrypt_block(block_bits)
            step1_bytes = bits_to_bytes(step1_bits)
            print(f"  Результат: {step1_bytes.hex().upper()}")
            
            # ШАГ 2: Шифрование с K2
            print(f"\n[Шаг 2] Шифрование с K2")
            step2_bits = self.des2.encrypt_block(step1_bits)
            step2_bytes = bits_to_bytes(step2_bits)
            print(f"  Результат: {step2_bytes.hex().upper()}")
            
            # ШАГ 3: Расшифровка с K1
            print(f"\n[Шаг 3] Расшифровка с K1")
            step3_bits = self.des1.decrypt_block(step2_bits)
            step3_bytes = bits_to_bytes(step3_bits)
            print(f"  Результат (открытый текст): {step3_bytes.hex().upper()}")
            
            plaintext.extend(step3_bytes)
        
        # Удаляем паддинг
        return unpad(bytes(plaintext))

# =========================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# =========================================================

def main():
    print("=" * 70)
    print("TRIPLE DES (3DES) - УЧЕБНАЯ РЕАЛИЗАЦИЯ")
    print("=" * 70)
    
    # Генерируем 3 случайных ключа по 8 байт (64 бита)
    key1 = os.urandom(8)
    key2 = os.urandom(8)
    key3 = os.urandom(8)
    
    print(f"\nКлюч K1 (HEX): {key1.hex().upper()}")
    print(f"Ключ K2 (HEX): {key2.hex().upper()}")
    print(f"Ключ K3 (HEX): {key3.hex().upper()}")
    
    # Создаем экземпляр Triple DES
    triple_des = TripleDES(key1, key2, key3)
    
    # Исходное сообщение
    plaintext = b"Hello 3DES! This is a test message."
    print(f"\nИсходное сообщение: {plaintext.decode('utf-8', errors = 'replace')}")
    print(f"Длина: {len(plaintext)} байт")
    
    # ШИФРОВАНИЕ
    print("\n" + "=" * 70)
    print("ПРОЦЕСС ШИФРОВАНИЯ 3DES")
    print("=" * 70)
    ciphertext = triple_des.encrypt(plaintext)
    
    print(f"\nШифротекст (HEX): {ciphertext.hex().upper()}")
    print(f"Длина шифротекста: {len(ciphertext)} байт")
    
    # РАСШИФРОВАНИЕ
    print("\n" + "=" * 70)
    print("ПРОЦЕСС РАСШИФРОВАНИЯ 3DES")
    print("=" * 70)
    decrypted = triple_des.decrypt(ciphertext)
    
    print(f"\nРасшифрованное сообщение: {decrypted.decode('utf-8', errors = 'replace')}")
    
    # Проверка
    print("\n" + "=" * 70)
    print("ПРОВЕРКА")
    print("=" * 70)
    if plaintext == decrypted:
        print("✅ УСПЕШНО! Расшифрованные данные совпадают с исходными.")
    else:
        print("❌ ОШИБКА! Данные не совпадают.")
        print(f"Оригинал: {plaintext}")
        print(f"Расшифровано: {decrypted}")

if __name__ == "__main__":
    main()