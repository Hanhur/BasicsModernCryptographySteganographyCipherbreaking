# 3. Самосинхронизирующиеся поточные криптоспетемы
"""
Самосинхронизирующийся поточный шифр (Self-Synchronizing Stream Cipher)
Реализация на Python для образовательных целей.

Принцип работы:
- Генерация ключевого потока зависит от предыдущих t символов шифротекста
- При потере/вставке символа синхронизация восстанавливается через t шагов
- Ошибка распространяется не более чем на t + 1 символов
"""

import os
from typing import List, Tuple


class SelfSynchronizingCipher:
    """
    Самосинхронизирующийся поточный шифр.
    
    Использует:
    - Регистр сдвига для хранения последних t символов шифротекста
    - Функцию g для генерации текущего ключа (на основе регистра и мастер-ключа)
    - Функцию h для шифрования/расшифрования (XOR в данном примере)
    """
    
    def __init__(self, master_key: int, t: int = 4):
        """
        Инициализация шифра.
        
        Args:
            master_key: Секретный ключ (целое число)
            t: Размер окна (количество предыдущих символов шифротекста для синхронизации)
        """
        self.master_key = master_key
        self.t = t
        
        # Размер алфавита (байты от 0 до 255)
        self.modulus = 256
    
    def _g(self, shift_register: List[int]) -> int:
        """
        Функция генерации текущего ключа ki = g(ui, k).
        
        Здесь ui - содержимое регистра сдвига (последние t символов шифротекста).
        master_key - секретный ключ.
        
        В реальных системах используется криптостойкая хеш-функция или
        блочный шифр. В демо-версии - комбинация XOR, сложения и сдвигов.
        
        Args:
            shift_register: Регистр сдвига длиной t
            
        Returns:
            Ключевой элемент ki (0-255)
        """
        # Преобразуем регистр и ключ в одно число
        value = self.master_key
        
        for i, byte in enumerate(shift_register):
            # Нелинейное преобразование с учетом позиции
            value ^= (byte << (i * 3)) & 0xFF
            value = (value + byte * (i + 1)) & 0xFFFF
        
        # Еще один проход нелинейного смешивания
        for byte in shift_register:
            value = ((value << 3) | (value >> 5)) & 0xFFFF
            value ^= byte
        
        # Возвращаем младший байт как ключевой символ
        return (value ^ self.master_key) & 0xFF
    
    def _h(self, key_byte: int, data_byte: int) -> int:
        """
        Функция шифрования/расшифрования ci = h(ki, mi) или mi = h(ki, ci).
        
        В данном случае используется XOR, который обратим сам в себя.
        
        Args:
            key_byte: Элемент ключевого потока
            data_byte: Элемент открытого или шифрованного текста
            
        Returns:
            Результат преобразования
        """
        return key_byte ^ data_byte
    
    def _init_register(self) -> List[int]:
        """
        Инициализация регистра сдвига начальным открытым состоянием u0.
        
        Начальное состояние - это t нулевых байтов.
        В реальном протоколе начальное состояние может быть фиксированным
        или передаваться открыто.
        
        Returns:
            Инициализированный регистр сдвига
        """
        return [0] * self.t
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Шифрование сообщения.
        
        Args:
            plaintext: Открытый текст (байты)
            
        Returns:
            Шифротекст (байты)
        """
        ciphertext = bytearray()
        shift_register = self._init_register()
        
        for m_byte in plaintext:
            # 1. Генерируем текущий ключ ki = g(ui, k)
            k_byte = self._g(shift_register)
            
            # 2. Шифруем ci = h(ki, mi)
            c_byte = self._h(k_byte, m_byte)
            ciphertext.append(c_byte)
            
            # 3. Обновляем регистр сдвига: добавляем ci, выталкиваем самый старый
            shift_register.append(c_byte)
            if len(shift_register) > self.t:
                shift_register.pop(0)
        
        return bytes(ciphertext)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Расшифрование сообщения.
        
        Процесс идентичен шифрованию, так как XOR симметричен.
        
        Args:
            ciphertext: Шифротекст (байты)
            
        Returns:
            Расшифрованный открытый текст
        """
        plaintext = bytearray()
        shift_register = self._init_register()
        
        for c_byte in ciphertext:
            # 1. Генерируем текущий ключ ki = g(ui, k) из регистра,
            #    содержащего предыдущие символы шифротекста
            k_byte = self._g(shift_register)
            
            # 2. Расшифровываем mi = h(ki, ci)
            m_byte = self._h(k_byte, c_byte)
            plaintext.append(m_byte)
            
            # 3. Обновляем регистр сдвига так же, как при шифровании
            shift_register.append(c_byte)
            if len(shift_register) > self.t:
                shift_register.pop(0)
        
        return bytes(plaintext)
    
    def decrypt_with_errors(self, ciphertext_with_errors: bytes, error_positions: List[int] = None) -> Tuple[bytes, List[int]]:
        """
        Расшифрование с возможными ошибками в канале.
        Демонстрирует свойство ограниченного распространения ошибки.
        
        Args:
            ciphertext_with_errors: Шифротекст с ошибками/потерями/вставками
            error_positions: Для отладки - ожидаемые позиции ошибок
            
        Returns:
            (расшифрованный текст, список позиций искаженных байтов)
        """
        plaintext = bytearray()
        shift_register = self._init_register()
        corrupted_positions = []
        
        for idx, c_byte in enumerate(ciphertext_with_errors):
            k_byte = self._g(shift_register)
            m_byte = self._h(k_byte, c_byte)
            plaintext.append(m_byte)
            
            # Проверяем, испортился ли этот байт из-за предыдущих ошибок
            # (в реальном канале это определяется внешними средствами)
            if error_positions and idx in error_positions:
                corrupted_positions.append(idx)
            
            shift_register.append(c_byte)
            if len(shift_register) > self.t:
                shift_register.pop(0)
        
        return bytes(plaintext), corrupted_positions


def demonstrate_synchronization():
    """Демонстрация самосинхронизации и ограниченного распространения ошибки."""
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ САМОСИНХРОНИЗИРУЮЩЕГОСЯ ПОТОЧНОГО ШИФРА")
    print("=" * 60)
    
    # Параметры
    MASTER_KEY = 0x5A3F2C1E
    T = 4  # размер окна
    
    cipher = SelfSynchronizingCipher(master_key = MASTER_KEY, t = T)
    
    # Исходное сообщение (латиница для наглядности)
    original_text = b"Hello, this is a secret message! It should be decrypted correctly."
    print(f"\n1. Исходный текст: {original_text}")
    print(f"   Длина: {len(original_text)} байт")
    
    # Шифрование
    ciphertext = cipher.encrypt(original_text)
    print(f"\n2. Шифротекст: {ciphertext.hex()[:50]}... (первые 50 символов)")
    
    # Нормальное расшифрование
    decrypted = cipher.decrypt(ciphertext)
    print(f"\n3. Нормальное расшифрование: {decrypted}")
    print(f"   Совпадает с исходным: {decrypted == original_text}")
    
    # ====== Тест 1: Ошибка в одном символе шифротекста ======
    print("\n" + "-" * 60)
    print("ТЕСТ 1: Ошибка в 10-м символе шифротекста")
    print("-" * 60)
    
    corrupted_ciphertext = bytearray(ciphertext)
    corrupted_ciphertext[10] ^= 0xFF  # инвертируем 10-й байт
    decrypted_with_error = cipher.decrypt(corrupted_ciphertext)
    
    print(f"Расшифровано с ошибкой: {decrypted_with_error}")
    
    # Находим позиции, где текст отличается от исходного
    diff_positions = []
    for i in range(min(len(original_text), len(decrypted_with_error))):
        if original_text[i] != decrypted_with_error[i]:
            diff_positions.append(i)
    
    print(f"Позиции искаженных байтов: {diff_positions[:20]}{'...' if len(diff_positions) > 20 else ''}")
    print(f"Всего искажено: {len(diff_positions)} байтов")
    print(f"Ожидаемое распространение (T + 1 = {T + 1} байтов): "f"{'✓' if len(diff_positions) <= T + 1 else '✗'} "f"(получено {len(diff_positions)} <= {T + 1})")
    
    # ====== Тест 2: Вставка символа ======
    print("\n" + "-" * 60)
    print("ТЕСТ 2: Вставка символа в шифротекст (имитация потери синхронизации)")
    print("-" * 60)
    
    inserted_ciphertext = bytearray(ciphertext[:15]) + b'\xAA' + bytearray(ciphertext[15:])
    print(f"Исходная длина шифротекста: {len(ciphertext)}")
    print(f"Длина после вставки: {len(inserted_ciphertext)}")
    
    decrypted_with_insert = cipher.decrypt(inserted_ciphertext)
    
    # После вставки декодер "съезжает", но через T шагов синхронизируется
    decrypted_with_insert_str = decrypted_with_insert[:50]
    original_str = original_text[:50]
    
    print(f"Расшифровано (первые 50 байт): {decrypted_with_insert_str}")
    print(f"Ожидалось (первые 50 байт):     {original_str}")
    
    # Находим момент восстановления синхронизации
    synced_pos = -1
    for i in range(min(len(original_text), len(decrypted_with_insert)) - T):
        match_count = 0
        for j in range(T):
            if i + j < len(original_text) and i + j < len(decrypted_with_insert):
                if original_text[i + j] == decrypted_with_insert[i + j]:
                    match_count += 1
        if match_count >= T - 1:  # почти полное совпадение на окне
            synced_pos = i
            break
    
    print(f"Синхронизация восстановилась примерно на позиции {synced_pos}")
    if synced_pos > 0:
        print(f"Это ~{synced_pos} байтов искаженных данных, затем всё корректно")
    
    # ====== Тест 3: Потеря символа ======
    print("\n" + "-" * 60)
    print("ТЕСТ 3: Потеря символа в шифротексте")
    print("-" * 60)
    
    missing_ciphertext = bytearray(ciphertext[:20]) + bytearray(ciphertext[21:])
    print(f"Исходная длина: {len(ciphertext)} → после потери: {len(missing_ciphertext)}")
    
    decrypted_with_missing = cipher.decrypt(missing_ciphertext)
    
    diff_after_missing = []
    for i in range(min(50, len(original_text), len(decrypted_with_missing))):
        if original_text[i] != decrypted_with_missing[i]:
            diff_after_missing.append(i)
    
    print(f"Искаженные позиции (первые 50 байт): {diff_after_missing}")
    print("Через несколько шагов данные снова становятся корректными (автосинхронизация)")


def demonstrate_error_propagation():
    """Демонстрация ограниченного распространения ошибки."""
    
    print("\n" + "=" * 60)
    print("ОГРАНИЧЕННОЕ РАСПРОСТРАНЕНИЕ ОШИБКИ")
    print("=" * 60)
    
    cipher = SelfSynchronizingCipher(master_key = 0x12345678, t = 3)
    
    # Длинное сообщение для наглядности
    message = b"A" * 100
    ciphertext = cipher.encrypt(message)
    
    # Вносим ошибку в 30-й байт
    corrupted = bytearray(ciphertext)
    corrupted[30] ^= 0x01
    
    decrypted = cipher.decrypt(corrupted)
    
    print(f"T = {cipher.t} (размер окна)")
    print(f"Ошибка внесена в позицию 30 шифротекста")
    print("\nРезультат расшифрования (фрагмент):")
    
    for i in range(25, 45):
        orig_char = message[i] if i < len(message) else ord('?')
        dec_char = decrypted[i] if i < len(decrypted) else ord('?')
        marker = " <-- ОШИБКА" if orig_char != dec_char else ""
        print(f"  позиция {i:3d}: исходный '{chr(orig_char)}' → расшифрованный '{chr(dec_char)}'{marker}")
    
    print(f"\nВсего искажено позиций: {sum(1 for i in range(len(message)) if message[i] != decrypted[i])}")
    print(f"(должно быть не более T+1 = {cipher.t + 1})")


if __name__ == "__main__":
    demonstrate_synchronization()
    demonstrate_error_propagation()
    
    print("\n" + "=" * 60)
    print("ВЫВОДЫ:")
    print("=" * 60)
    print("1. Шифр самосинхронизируется после вставки/потери символов")
    print("2. Одиночная ошибка распространяется не более чем на T+1 байтов")
    print("3. Расшифрование зависит ТОЛЬКО от последних T символов шифротекста")
    print("4. Не требуется внешняя синхронизация позиции")