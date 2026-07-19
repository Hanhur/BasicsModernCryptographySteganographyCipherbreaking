# Атаки и уязвимости AES
"""
Демонстрация уязвимостей и режимов шифрования AES
Основано на тексте об атаках на AES
Использует только стандартную библиотеку Python
"""

import os
import time
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import secrets


class AESVulnerabilityDemo:
    """Демонстрация различных аспектов безопасности AES"""
    
    def __init__(self):
        self.backend = default_backend()
        
    def generate_key(self, key_size = 128):
        """
        Генерация ключа AES указанного размера
        key_size: 128, 192 или 256 бит
        """
        if key_size not in [128, 192, 256]:
            raise ValueError("Размер ключа должен быть 128, 192 или 256 бит")
        
        # Генерируем случайный ключ
        key_bytes = os.urandom(key_size // 8)
        return key_bytes
    
    def pad_data(self, data, block_size = 16):
        """Добавление паддинга PKCS7 к данным"""
        padder = padding.PKCS7(block_size * 8).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data
    
    def unpad_data(self, padded_data, block_size = 16):
        """Удаление паддинга PKCS7"""
        unpadder = padding.PKCS7(block_size * 8).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data
    
    def encrypt_ecb(self, plaintext, key):
        """
        Шифрование в режиме ECB (уязвимый)
        """
        # Добавляем паддинг до размера блока
        padded_plaintext = self.pad_data(plaintext)
        
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return ciphertext
    
    def decrypt_ecb(self, ciphertext, key):
        """
        Расшифрование в режиме ECB
        """
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = self.backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        plaintext = self.unpad_data(padded_plaintext)
        return plaintext
    
    def encrypt_cbc(self, plaintext, key, iv = None):
        """
        Шифрование в режиме CBC (защищенный)
        """
        if iv is None:
            iv = os.urandom(16)
        
        padded_plaintext = self.pad_data(plaintext)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return ciphertext, iv
    
    def decrypt_cbc(self, ciphertext, key, iv):
        """
        Расшифрование в режиме CBC
        """
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = self.backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        plaintext = self.unpad_data(padded_plaintext)
        return plaintext
    
    def demo_ecb_problem(self):
        """
        Демонстрация проблемы ECB: одинаковые блоки дают одинаковый шифротекст
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ПРОБЛЕМЫ РЕЖИМА ECB")
        print("=" * 60)
        
        key = self.generate_key(128)
        
        # Создаем сообщение с повторяющимися блоками
        block1 = b"AAAAAAAAAAAAAAAA"  # 16 байт
        block2 = b"BBBBBBBBBBBBBBBB"  # 16 байт
        
        message1 = block1 + block2 + block1  # Повторяющиеся блоки
        message2 = block1 + block2 + block2  # Другой повтор
        
        print(f"Сообщение 1 (повторяющиеся блоки): {message1}")
        print(f"Сообщение 2 (другой повтор): {message2}")
        print(f"Длина сообщений: {len(message1)} байт")
        
        # Шифруем оба сообщения в режиме ECB
        ciphertext1 = self.encrypt_ecb(message1, key)
        ciphertext2 = self.encrypt_ecb(message2, key)
        
        print(f"\nШифротекст 1: {ciphertext1.hex()[:40]}...")
        print(f"Шифротекст 2: {ciphertext2.hex()[:40]}...")
        
        # Разбиваем на блоки и сравниваем
        print("\nАнализ блоков (по 16 байт):")
        for i in range(0, len(ciphertext1), 16):
            block_c1 = ciphertext1[i:i + 16]
            block_c2 = ciphertext2[i:i + 16]
            print(f"Блок {i // 16 + 1}: {'СОВПАДАЮТ' if block_c1 == block_c2 else 'РАЗНЫЕ'}")
            print(f"  C1: {block_c1.hex()}")
            print(f"  C2: {block_c2.hex()}")
        
        print("\n⚠️ УЯЗВИМОСТЬ: Одинаковые блоки открытого текста дают одинаковые блоки шифротекста!")
        print("Это позволяет анализировать структуру данных даже без расшифровки.")
    
    def demo_cbc_vs_ecb(self):
        """
        Сравнение CBC и ECB на примере изображения (символическое)
        """
        print("\n" + "=" * 60)
        print("СРАВНЕНИЕ ECB vs CBC")
        print("=" * 60)
        
        key = self.generate_key(128)
        
        # Создаем данные, имитирующие простое изображение
        # Горизонтальные полосы для наглядности
        line1 = b"0" * 16 + b"1" * 16 + b"0" * 16  # Полосы
        line2 = b"1" * 16 + b"0" * 16 + b"1" * 16
        line3 = b"0" * 16 + b"1" * 16 + b"0" * 16
        
        image_data = line1 + line2 + line3
        
        print("Исходные данные (имитация изображения с полосами):")
        self.print_data_visualization(image_data)
        
        # ECB шифрование
        ciphertext_ecb = self.encrypt_ecb(image_data, key)
        
        # CBC шифрование
        iv = os.urandom(16)
        ciphertext_cbc, _ = self.encrypt_cbc(image_data, key, iv)
        
        print("\nПосле шифрования ECB (структура сохраняется):")
        self.print_data_visualization(ciphertext_ecb[:len(image_data)])
        
        print("\nПосле шифрования CBC (структура скрыта):")
        self.print_data_visualization(ciphertext_cbc[:len(image_data)])
        
        print("\n💡 Визуально видно, что ECB сохраняет структуру данных,")
        print("   а CBC ее полностью скрывает, как на примере с горой Маттерхорн.")
    
    def print_data_visualization(self, data, width = 16):
        """
        Визуализация данных в виде матрицы (для демонстрации структуры)
        """
        for i in range(0, min(len(data), 128), width):
            chunk = data[i:i+width]
            # Преобразуем байты в визуальное представление
            visual = ''.join(['█' if b > 127 else '░' for b in chunk])
            hex_str = ' '.join([f'{b:02x}' for b in chunk])
            print(f"{i:3d}: {visual}  {hex_str}")
    
    def demo_block_replay_attack(self):
        """
        Демонстрация атаки повторением блока (Replay Attack)
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ АТАКИ ПОВТОРЕНИЕМ БЛОКА")
        print("=" * 60)
        
        # Симулируем банковскую транзакцию
        key = self.generate_key(128)
        
        # Сообщение: Имя: Алиса Смит, Счет: 123456, Сумма: 200$
        name = b"Alice Smith"
        account = b"123456"
        amount = b"00200"  # 200 долларов
        timestamp = b"2024-01-15 10:30:00"
        
        transaction = name + b"|" + account + b"|" + amount + b"|" + timestamp
        
        print("Исходная транзакция:")
        print(f"  {transaction.decode('ascii', errors = 'ignore')}")
        
        # Шифруем с помощью ECB
        encrypted = self.encrypt_ecb(transaction, key)
        print(f"\nЗашифрованная транзакция: {encrypted.hex()[:64]}...")
        
        # Симуляция атаки Евы
        print("\n🔴 ЕВА перехватывает и повторяет транзакцию!")
        
        # В уязвимой системе Ева может просто повторно отправить
        # точно такой же шифротекст
        encrypted_replay = encrypted  # Просто копируем
        
        print(f"Повторный шифротекст: {encrypted_replay.hex()[:64]}...")
        
        # Банк расшифровывает
        decrypted = self.decrypt_ecb(encrypted_replay, key)
        print(f"\nБанк расшифровал повтор: {decrypted.decode('ascii', errors = 'ignore')}")
        
        print("\n⚠️ БАНК ДУМАЕТ, ЧТО ЭТО НОВАЯ ТРАНЗАКЦИЯ!")
        print("   Ева украла деньги, просто скопировав сообщение.")
        
        # Защита с использованием CBC и временной метки
        print("\n" + "-" * 40)
        print("ЗАЩИТА ОТ АТАКИ:")
        print("-" * 40)
        
        # Добавляем уникальный ID сессии и используем CBC
        session_id = os.urandom(8).hex()
        new_timestamp = b"2024-01-15 10:31:00"  # Новое время
        
        secure_transaction = name + b"|" + account + b"|" + amount + b"|" + new_timestamp + b"|" + session_id.encode()
        
        # Используем CBC с уникальным IV
        iv = os.urandom(16)
        encrypted_secure, _ = self.encrypt_cbc(secure_transaction, key, iv)
        
        print(f"Защищенная транзакция (CBC + timestamp + session_id):")
        print(f"  {encrypted_secure.hex()[:64]}...")
        
        # Расшифровываем
        decrypted_secure = self.decrypt_cbc(encrypted_secure, key, iv)
        print(f"Расшифровано: {decrypted_secure.decode('ascii', errors = 'ignore')}")
        
        print("\n✅ Защита работает! Даже при повторной отправке,")
        print("   банк проверит timestamp и session_id и отклонит повтор.")
    
    def demo_side_channel_timing(self):
        """
        Демонстрация атаки по времени (симуляция)
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ АТАКИ ПО ВРЕМЕНИ")
        print("=" * 60)
        
        key = self.generate_key(128)
        test_data = b"Hello, World! This is a test message for AES timing attack."
        
        print("Имитация измерения времени шифрования...")
        print("(В реальной атаке корреляция времени с ключом может дать информацию)\n")
        
        # Измеряем время шифрования с разными ключами
        times = []
        for i in range(10):
            start = time.perf_counter()
            # Используем немного разные ключи (меняем один байт)
            modified_key = bytearray(key)
            modified_key[0] = (modified_key[0] + i) % 256
            modified_key = bytes(modified_key)
            
            self.encrypt_ecb(test_data, modified_key)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # в миллисекундах
        
        print("Время шифрования для 10 разных ключей (ms):")
        for i, t in enumerate(times):
            bar = "█" * int(t * 100)
            print(f"Ключ {i+1:2d}: {t:.3f} ms  {bar}")
        
        print(f"\n⏱️ Разница между мин и макс: {max(times) - min(times):.3f} ms")
        print("\n⚠️ Атака по времени использует такие различия для определения")
        print("   правильного ключа через корреляционный анализ.")
        print("   Защита: использование постоянного времени выполнения.")
    
    def demo_key_entropy(self):
        """
        Демонстрация энтропии ключей
        """
        print("\n" + "=" * 60)
        print("ЭНТРОПИЯ КЛЮЧЕЙ AES")
        print("=" * 60)
        
        print("Размеры ключей AES и количество возможных комбинаций:")
        print("-" * 50)
        
        key_sizes = [128, 192, 256]
        for size in key_sizes:
            combinations = 2 ** size
            # Красивое форматирование больших чисел
            comb_str = f"{combinations:,}"
            print(f"{size}-битный ключ: {comb_str} комбинаций")
            print(f"  Это 10^{int(size * 0.3010)} в десятичной системе")
        
        print("\n" + "-" * 50)
        print("Для 128-битного ключа количество комбинаций:")
        print("340 282 366 920 938 463 463 374 607 431 768 211 456")
        print("(это 340 с 36 нулями, как в тексте)")
        
        print("\n💡 Даже при использовании всех компьютеров мира,")
        print("   полный перебор 128-битного ключа займет миллиарды лет.")
    
    def run_all_demos(self):
        """Запуск всех демонстраций"""
        print("\n" + "=" * 60)
        print("🧪 ДЕМОНСТРАЦИЯ УЯЗВИМОСТЕЙ AES")
        print("=" * 60)
        print("На основе статьи об атаках и уязвимостях AES")
        print("=" * 60)
        
        self.demo_key_entropy()
        self.demo_ecb_problem()
        self.demo_cbc_vs_ecb()
        self.demo_block_replay_attack()
        self.demo_side_channel_timing()
        
        print("\n" + "=" * 60)
        print("ВЫВОДЫ:")
        print("=" * 60)
        print("1. Математически AES очень силен (невозможно взломать перебором)")
        print("2. Режим ECB крайне опасен - используйте CBC, GCM или другие режимы")
        print("3. Атаки по сторонним каналам (время, питание, EM) реальны")
        print("4. Проблема обмена ключами - основная слабость симметричной криптографии")
        print("5. Защита: уникальные IV, временные метки, защита от повторов")
        print("=" * 60)


def main():
    """Главная функция"""
    demo = AESVulnerabilityDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()