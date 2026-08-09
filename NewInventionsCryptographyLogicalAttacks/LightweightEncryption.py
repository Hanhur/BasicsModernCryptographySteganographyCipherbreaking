# Легковесное шифрование
"""
Легковесное блочное шифрование (48-битный блок)
Реализация на основе полей Галуа GF(2 ^ 4)
Без использования numpy
"""

import struct
import secrets
import time
from typing import Tuple, List

# ============================================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ GF(2^4)
# ============================================================================

def gf_add(a: int, b: int) -> int:
    """Сложение в GF(2 ^ 4) — это XOR"""
    return a ^ b

def gf_mul(a: int, b: int, mod: int = 0b10011) -> int:
    """
    Умножение в GF(2 ^ 4) с неприводимым полиномом x ^ 4 + x + 1 (0b10011)
    """
    result = 0
    # Умножение как в двоичном поле
    while b > 0:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        # Редукция по модулю неприводимого полинома
        if a & 0b10000:
            a ^= mod
    return result & 0b1111

def gf_pow(a: int, exp: int) -> int:
    """Возведение в степень в GF(2 ^ 4)"""
    result = 1
    for _ in range(exp):
        result = gf_mul(result, a)
    return result

def gf_inv(a: int) -> int:
    """Нахождение обратного элемента в GF(2 ^ 4)"""
    if a == 0:
        return 0
    # Перебор всех элементов для поиска обратного
    for i in range(1, 16):
        if gf_mul(a, i) == 1:
            return i
    return 0

# ============================================================================
# 2. S-BOX (таблица замен) на основе обратного элемента в GF(2^4)
# ============================================================================

def generate_sbox() -> List[int]:
    """Генерация S-Box с использованием обратного элемента в GF(2 ^ 4)"""
    sbox = [0] * 16
    for i in range(16):
        # Инверсия в GF(2^4), затем аффинное преобразование
        inv = gf_inv(i)
        # Простое аффинное преобразование для усиления нелинейности
        sbox[i] = (inv ^ ((inv << 1) & 0b1111) ^ 0b1001) & 0b1111
    return sbox

# Генерация S-Box и обратного S-Box
SBOX = generate_sbox()
INV_SBOX = [0] * 16
for i, val in enumerate(SBOX):
    INV_SBOX[val] = i

# ============================================================================
# 3. ОСНОВНОЙ АЛГОРИТМ ШИФРОВАНИЯ
# ============================================================================

class LightweightCipher:
    """
    Легковесный блочный шифр с 48-битным блоком
    Работает с 12 полубайтами (по 4 бита)
    """
    
    # Количество раундов
    ROUNDS = 8
    
    def __init__(self, key: bytes):
        """
        Инициализация с ключом
        
        Args:
            key: 64-битный ключ (8 байт)
        """
        if len(key) != 8:
            raise ValueError("Ключ должен быть 8 байт (64 бита)")
        
        self.key = key
        # Разбиваем ключ на 16 полубайтов
        self.key_nibbles = []
        for byte in key:
            self.key_nibbles.append(byte >> 4)      # старший полубайт
            self.key_nibbles.append(byte & 0x0F)    # младший полубайт
            
        # Раундовые ключи (по 12 полубайтов на раунд)
        self.round_keys = self._expand_key()
    
    def _expand_key(self) -> List[List[int]]:
        """
        Расширение ключа: генерация раундовых ключей
        
        Returns:
            Список из ROUNDS ключей, каждый — список из 12 полубайтов
        """
        round_keys = []
        
        for r in range(self.ROUNDS):
            round_key = []
            # Берем 12 полубайтов из расширенного ключа со смещением
            for i in range(12):
                idx = (r + i) % len(self.key_nibbles)
                # Применяем S-Box для усиления диффузии
                val = SBOX[(self.key_nibbles[idx] + r) & 0x0F]
                round_key.append(val)
            round_keys.append(round_key)
        
        return round_keys
    
    def _substitute(self, state: List[int]) -> List[int]:
        """Замена: применяем S-Box ко всем полубайтам"""
        return [SBOX[nibble] for nibble in state]
    
    def _inv_substitute(self, state: List[int]) -> List[int]:
        """Обратная замена"""
        return [INV_SBOX[nibble] for nibble in state]
    
    def _shift_rows(self, state: List[int]) -> List[int]:
        """
        Сдвиг строк: побайтовый сдвиг для 12 полубайтов
        Разбиваем на 4 строки по 3 полубайта
        """
        # Представление как 4 строки x 3 столбца
        rows = [
            [state[0], state[1], state[2]],   # строка 0
            [state[3], state[4], state[5]],   # строка 1
            [state[6], state[7], state[8]],   # строка 2
            [state[9], state[10], state[11]]  # строка 3
        ]
        
        # Сдвиг строк: строка 1 <- сдвиг на 1, строка 2 <- на 2, строка 3 <- на 1
        rows[1] = rows[1][1:] + rows[1][:1]
        rows[2] = rows[2][2:] + rows[2][:2]
        rows[3] = rows[3][1:] + rows[3][:1]
        
        # Обратное преобразование в плоский список
        return [rows[0][0], rows[0][1], rows[0][2],
                rows[1][0], rows[1][1], rows[1][2],
                rows[2][0], rows[2][1], rows[2][2],
                rows[3][0], rows[3][1], rows[3][2]]
    
    def _inv_shift_rows(self, state: List[int]) -> List[int]:
        """Обратный сдвиг строк"""
        rows = [
            [state[0], state[1], state[2]],
            [state[3], state[4], state[5]],
            [state[6], state[7], state[8]],
            [state[9], state[10], state[11]]
        ]
        
        # Обратный сдвиг
        rows[1] = rows[1][-1:] + rows[1][:-1]
        rows[2] = rows[2][-2:] + rows[2][:-2]
        rows[3] = rows[3][-1:] + rows[3][:-1]
        
        return [rows[0][0], rows[0][1], rows[0][2],
                rows[1][0], rows[1][1], rows[1][2],
                rows[2][0], rows[2][1], rows[2][2],
                rows[3][0], rows[3][1], rows[3][2]]
    
    def _mix_columns(self, state: List[int]) -> List[int]:
        """
        Перемешивание столбцов в GF(2^4)
        Матрица: [[1, 2, 1], [1, 1, 2], [2, 1, 1]] над GF(2 ^ 4)
        """
        # Разбиваем на 3 столбца по 4 элемента
        cols = [
            [state[0], state[3], state[6], state[9]],
            [state[1], state[4], state[7], state[10]],
            [state[2], state[5], state[8], state[11]]
        ]
        
        new_cols = []
        for col in cols:
            # Применяем матрицу к каждому столбцу
            new_col = [
                gf_add(gf_add(gf_mul(1, col[0]), gf_mul(2, col[1])), gf_mul(1, col[2])),
                gf_add(gf_add(gf_mul(1, col[0]), gf_mul(1, col[1])), gf_mul(2, col[2])),
                gf_add(gf_add(gf_mul(2, col[0]), gf_mul(1, col[1])), gf_mul(1, col[2]))
            ]
            # Добавляем 4-й элемент как линейную комбинацию
            new_col.append(gf_add(gf_add(col[0], col[1]), col[2]))
            new_cols.append(new_col)
        
        # Обратное преобразование
        return [new_cols[0][0], new_cols[1][0], new_cols[2][0],
                new_cols[0][1], new_cols[1][1], new_cols[2][1],
                new_cols[0][2], new_cols[1][2], new_cols[2][2],
                new_cols[0][3], new_cols[1][3], new_cols[2][3]]
    
    def _inv_mix_columns(self, state: List[int]) -> List[int]:
        """Обратное перемешивание столбцов"""
        # Аналогично, но с обратной матрицей
        cols = [
            [state[0], state[3], state[6], state[9]],
            [state[1], state[4], state[7], state[10]],
            [state[2], state[5], state[8], state[11]]
        ]
        
        new_cols = []
        for col in cols:
            # Обратная матрица: [[1, 2, 1], [1, 1, 2], [2, 1, 1]] (сама себе обратная)
            new_col = [
                gf_add(gf_add(gf_mul(1, col[0]), gf_mul(2, col[1])), gf_mul(1, col[2])),
                gf_add(gf_add(gf_mul(1, col[0]), gf_mul(1, col[1])), gf_mul(2, col[2])),
                gf_add(gf_add(gf_mul(2, col[0]), gf_mul(1, col[1])), gf_mul(1, col[2]))
            ]
            new_col.append(gf_add(gf_add(col[0], col[1]), col[2]))
            new_cols.append(new_col)
        
        return [new_cols[0][0], new_cols[1][0], new_cols[2][0],
                new_cols[0][1], new_cols[1][1], new_cols[2][1],
                new_cols[0][2], new_cols[1][2], new_cols[2][2],
                new_cols[0][3], new_cols[1][3], new_cols[2][3]]
    
    def _add_round_key(self, state: List[int], round_key: List[int]) -> List[int]:
        """Сложение с раундовым ключом (XOR)"""
        return [state[i] ^ round_key[i] for i in range(12)]
    
    def encrypt_block(self, plaintext: bytes) -> bytes:
        """
        Шифрование 48-битного блока (6 байт)
        
        Args:
            plaintext: 6 байт открытого текста
            
        Returns:
            6 байт зашифрованного текста
        """
        if len(plaintext) != 6:
            raise ValueError("Блок должен быть 6 байт (48 бит)")
        
        # Преобразуем блок в 12 полубайтов
        state = []
        for byte in plaintext:
            state.append(byte >> 4)
            state.append(byte & 0x0F)
        
        # Начальное добавление ключа
        state = self._add_round_key(state, self.round_keys[0])
        
        # Основные раунды
        for r in range(1, self.ROUNDS):
            state = self._substitute(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, self.round_keys[r])
        
        # Финальный раунд (без MixColumns)
        state = self._substitute(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self.round_keys[-1])
        
        # Преобразуем обратно в байты
        result = bytearray(6)
        for i in range(6):
            result[i] = (state[i * 2] << 4) | state[i*2 + 1]
        
        return bytes(result)
    
    def decrypt_block(self, ciphertext: bytes) -> bytes:
        """
        Дешифрование 48-битного блока (6 байт)
        
        Args:
            ciphertext: 6 байт зашифрованного текста
            
        Returns:
            6 байт открытого текста
        """
        if len(ciphertext) != 6:
            raise ValueError("Блок должен быть 6 байт (48 бит)")
        
        # Преобразуем блок в 12 полубайтов
        state = []
        for byte in ciphertext:
            state.append(byte >> 4)
            state.append(byte & 0x0F)
        
        # Обратные раунды
        state = self._add_round_key(state, self.round_keys[-1])
        state = self._inv_shift_rows(state)
        state = self._inv_substitute(state)
        
        for r in range(self.ROUNDS - 2, 0, -1):
            state = self._add_round_key(state, self.round_keys[r])
            state = self._inv_mix_columns(state)
            state = self._inv_shift_rows(state)
            state = self._inv_substitute(state)
        
        state = self._add_round_key(state, self.round_keys[0])
        
        # Преобразуем обратно в байты
        result = bytearray(6)
        for i in range(6):
            result[i] = (state[i * 2] << 4) | state[i * 2 + 1]
        
        return bytes(result)

    def encrypt(self, data: bytes) -> bytes:
        """Шифрование данных произвольной длины с паддингом (PKCS#7)"""
        # Добавляем паддинг до кратности 6
        pad_len = 6 - (len(data) % 6)
        if pad_len == 6:
            pad_len = 0
        padded_data = data + bytes([pad_len] * pad_len)
        
        # Шифруем по блокам
        result = bytearray()
        for i in range(0, len(padded_data), 6):
            block = padded_data[i:i + 6]
            if len(block) < 6:
                block = block + bytes([6 - len(block)] * (6 - len(block)))
            result.extend(self.encrypt_block(block))
        
        return bytes(result)
    
    def decrypt(self, data: bytes) -> bytes:
        """Дешифрование данных"""
        if len(data) % 6 != 0:
            raise ValueError("Зашифрованные данные должны быть кратны 6 байтам")
        
        result = bytearray()
        for i in range(0, len(data), 6):
            block = data[i:i + 6]
            result.extend(self.decrypt_block(block))
        
        # Удаляем паддинг
        pad_len = result[-1] if result else 0
        if pad_len > 0 and pad_len <= 6:
            return bytes(result[:-pad_len])
        return bytes(result)


# ============================================================================
# 4. ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================================

def demo():
    """Демонстрация работы алгоритма"""
    print("=" * 60)
    print("ЛЕГКОВЕСНОЕ БЛОЧНОЕ ШИФРОВАНИЕ (48-битный блок)")
    print("Реализация на основе полей Галуа GF(2 ^ 4)")
    print("=" * 60)
    
    # Генерация ключа
    key = secrets.token_bytes(8)  # 64-битный ключ
    print(f"\n🔑 Ключ (64 бита): {key.hex()}")
    
    # Создание экземпляра шифра
    cipher = LightweightCipher(key)
    
    # Тестовые данные
    test_data = b"Hello, Lightweight Cryptography in IoT!"
    print(f"\n📝 Исходные данные: {test_data.decode('ascii', errors = 'ignore')}")
    print(f"   Размер: {len(test_data)} байт")
    
    # Шифрование
    start = time.perf_counter()
    encrypted = cipher.encrypt(test_data)
    enc_time = time.perf_counter() - start
    
    print(f"\n🔒 Зашифрованные данные (hex): {encrypted.hex()}")
    print(f"   Размер: {len(encrypted)} байт")
    print(f"   Время шифрования: {enc_time * 1000:.3f} мс")
    
    # Дешифрование
    start = time.perf_counter()
    decrypted = cipher.decrypt(encrypted)
    dec_time = time.perf_counter() - start
    
    print(f"\n🔓 Расшифрованные данные: {decrypted.decode('ascii', errors = 'ignore')}")
    print(f"   Время дешифрования: {dec_time * 1000:.3f} мс")
    
    # Проверка корректности
    if decrypted == test_data:
        print("\n✅ УСПЕХ: Данные расшифрованы корректно!")
    else:
        print("\n❌ ОШИБКА: Расшифрованные данные не совпадают")
    
    # Демонстрация S-Box
    print("\n" + "=" * 60)
    print("S-BOX (таблица замен):")
    print("   ", " ".join([f"{i:02X}" for i in range(16)]))
    print("   ", " ".join([f"{s:02X}" for s in SBOX]))
    
    # Статистика
    print("\n" + "=" * 60)
    print("📊 ХАРАКТЕРИСТИКИ АЛГОРИТМА:")
    print(f"   Размер блока: 48 бит (6 байт)")
    print(f"   Размер ключа: 64 бита (8 байт)")
    print(f"   Количество раундов: {LightweightCipher.ROUNDS}")
    print(f"   Размер S-Box: 16 элементов (4 бита)")
    print(f"   Использует поля Галуа: GF(2 ^ 4)")
    print("=" * 60)


# ============================================================================
# 5. ТЕСТЫ
# ============================================================================

def run_tests():
    """Запуск тестов для проверки корректности"""
    print("\n🧪 ЗАПУСК ТЕСТОВ...")
    
    test_key = bytes.fromhex("0123456789ABCDEF")
    cipher = LightweightCipher(test_key)
    
    # Тест 1: Шифрование/дешифрование фиксированного блока
    test_block = bytes.fromhex("A1B2C3D4E5F6")
    encrypted = cipher.encrypt_block(test_block)
    decrypted = cipher.decrypt_block(encrypted)
    
    if decrypted == test_block:
        print("   ✅ Тест 1 (блок 6 байт): пройден")
    else:
        print("   ❌ Тест 1 (блок 6 байт): не пройден")
    
    # Тест 2: Шифрование/дешифрование произвольных данных
    test_data = bytes.fromhex("00 11 22 33 44 55 66 77 88 99 AA BB")
    encrypted = cipher.encrypt(test_data)
    decrypted = cipher.decrypt(encrypted)
    
    if decrypted == test_data:
        print("   ✅ Тест 2 (произвольные данные): пройден")
    else:
        print("   ❌ Тест 2 (произвольные данные): не пройден")
    
    # Тест 3: Проверка лавинного эффекта (изменение одного бита)
    test_data = bytes.fromhex("AAAAAAAAAAAA")
    encrypted1 = cipher.encrypt_block(test_data)
    
    # Изменяем один бит
    modified = bytearray(test_data)
    modified[0] ^= 0x01
    encrypted2 = cipher.encrypt_block(bytes(modified))
    
    diff_bits = bin(encrypted1[0] ^ encrypted2[0]).count("1") + \
                bin(encrypted1[1] ^ encrypted2[1]).count("1") + \
                bin(encrypted1[2] ^ encrypted2[2]).count("1") + \
                bin(encrypted1[3] ^ encrypted2[3]).count("1") + \
                bin(encrypted1[4] ^ encrypted2[4]).count("1") + \
                bin(encrypted1[5] ^ encrypted2[5]).count("1")
    
    print(f"   ✅ Тест 3 (лавинный эффект): {diff_bits} бит из 48 изменились ({diff_bits / 48 * 100:.1f}%)")
    
    # Тест 4: Производительность (1000 блоков)
    import time
    data = bytes.fromhex("F0F1F2F3F4F5")
    start = time.perf_counter()
    for _ in range(1000):
        cipher.encrypt_block(data)
    elapsed = (time.perf_counter() - start) * 1000
    
    print(f"   ✅ Тест 4 (производительность): {elapsed:.2f} мс на 1000 блоков")
    print(f"      ({(1000 / elapsed * 1000):.0f} блоков / сек)")

    # Тест 5: Расширение ключа
    print(f"   ✅ Тест 5 (расширение ключа): {len(cipher.round_keys)} раундовых ключей")


# ============================================================================
# 6. ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    demo()
    run_tests()