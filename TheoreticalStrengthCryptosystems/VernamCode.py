# Шифр Вернама
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ШИФР ВЕРНАМА (One-Time Pad)
================================
Реализация абсолютно стойкого шифра на основе XOR.
Соответствует описанию из учебника (Теорема 7.2).

Автор: Программа на основе текста
Дата: 2026
"""

import os
import sys
import argparse
import secrets
from typing import Union


# ============================================================================
# ЧАСТЬ 1. ЯДРО ШИФРА (базовые функции)
# ============================================================================

def vernam_encrypt(message: bytes, key: bytes) -> bytes:
    """
    Шифрование сообщения XOR с ключом (побайтово).
    
    Аргументы:
        message: открытый текст в виде байтов
        key: ключ той же длины в виде байтов
    
    Возвращает:
        зашифрованное сообщение (шифротекст)
    
    Исключения:
        ValueError: если длины message и key не совпадают
    """
    if len(message) != len(key):
        raise ValueError(f"Длина сообщения ({len(message)}) и ключа ({len(key)}) должны совпадать!")
    
    # XOR каждого байта (списковое включение)
    ciphertext = bytes([m ^ k for m, k in zip(message, key)])
    return ciphertext


def vernam_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Дешифрование сообщения (симметрично шифрованию).
    
    Аргументы:
        ciphertext: зашифрованное сообщение
        key: ключ той же длины
    
    Возвращает:
        расшифрованное сообщение (открытый текст)
    """
    # Так как XOR обратим сам себе, дешифрование = шифрование
    return vernam_encrypt(ciphertext, key)


def generate_key(length: int) -> bytes:
    """
    Генерация криптографически безопасного случайного ключа.
    
    Аргументы:
        length: длина ключа в байтах
    
    Возвращает:
        случайный ключ заданной длины
    
    Примечание:
        Используется secrets.token_bytes() - криптографически стойкий ГПСЧ,
        а не обычный random (который предсказуем).
    """
    return secrets.token_bytes(length)


# ============================================================================
# ЧАСТЬ 2. РАБОТА С ФАЙЛАМИ (класс для одноразового блокнота)
# ============================================================================

class VernamCipher:
    """
    Класс для работы с шифром Вернама (одноразовый блокнот).
    
    Особенности:
        - Автоматически отслеживает использованные байты ключа
        - Гарантирует одноразовость (нельзя использовать ключ дважды)
        - Работает с файлами любого размера
    """
    
    def __init__(self, key_file: str):
        """
        Инициализация с указанием файла ключа.
        
        Аргументы:
            key_file: путь к файлу с одноразовым блокнотом
        """
        self.key_file = key_file
        self.used_bytes = 0  # Счётчик использованных байт ключа
        
        # Проверяем существование файла ключа
        if not os.path.exists(key_file):
            raise FileNotFoundError(f"Файл ключа '{key_file}' не найден!")
    
    def get_key_size(self) -> int:
        """Возвращает общий размер ключа в байтах."""
        return os.path.getsize(self.key_file)
    
    def get_remaining_bytes(self) -> int:
        """Возвращает количество неизрасходованных байт ключа."""
        return self.get_key_size() - self.used_bytes
    
    def get_next_bytes(self, length: int) -> bytes:
        """
        Извлечение следующих length байт из файла ключа.
        
        Аргументы:
            length: количество байт для извлечения
        
        Возвращает:
            байты ключа
        
        Исключения:
            ValueError: если запрошено больше байт, чем осталось в ключе
        """
        if not os.path.exists(self.key_file):
            raise FileNotFoundError(f"Файл ключа '{self.key_file}' не найден!")
        
        # Проверяем, достаточно ли осталось ключа
        remaining = self.get_remaining_bytes()
        if remaining < length:
            raise ValueError(
                f"Недостаточно ключа! Осталось {remaining} байт, запрошено {length} байт. "
                f"Ключ израсходован полностью и не может быть переиспользован!"
            )
        
        # Читаем нужное количество байт с текущей позиции
        with open(self.key_file, 'rb') as f:
            f.seek(self.used_bytes)
            key_bytes = f.read(length)
            
            if len(key_bytes) < length:
                raise ValueError(f"Не удалось прочитать {length} байт из файла ключа!")
            
            # Обновляем позицию (отмечаем байты как использованные)
            self.used_bytes += length
        
        return key_bytes
    
    def encrypt_file(self, input_file: str, output_file: str) -> int:
        """
        Шифрование файла с использованием следующих байт ключа.
        
        Аргументы:
            input_file: путь к файлу с открытым текстом
            output_file: путь для сохранения шифротекста
        
        Возвращает:
            количество зашифрованных байт
        """
        # Читаем исходный файл
        with open(input_file, 'rb') as f:
            plaintext = f.read()
        
        if len(plaintext) == 0:
            print(f"⚠️  Предупреждение: файл '{input_file}' пуст!")
            # Создаём пустой выходной файл
            with open(output_file, 'wb') as f:
                f.write(b'')
            return 0
        
        # Получаем ключ нужной длины
        key = self.get_next_bytes(len(plaintext))
        
        # Шифруем
        ciphertext = vernam_encrypt(plaintext, key)
        
        # Сохраняем шифротекст
        with open(output_file, 'wb') as f:
            f.write(ciphertext)
        
        print(f"✅ Файл '{input_file}' зашифрован в '{output_file}'")
        print(f"   Размер: {len(plaintext)} байт, использовано ключа: {len(plaintext)} байт")
        return len(plaintext)
    
    def decrypt_file(self, input_file: str, output_file: str) -> int:
        """
        Дешифрование файла (симметрично шифрованию).
        
        Аргументы:
            input_file: путь к файлу с шифротекстом
            output_file: путь для сохранения открытого текста
        
        Возвращает:
            количество расшифрованных байт
        """
        # Читаем шифротекст
        with open(input_file, 'rb') as f:
            ciphertext = f.read()
        
        if len(ciphertext) == 0:
            print(f"⚠️  Предупреждение: файл '{input_file}' пуст!")
            with open(output_file, 'wb') as f:
                f.write(b'')
            return 0
        
        # Получаем ключ (те же байты, что и при шифровании!)
        key = self.get_next_bytes(len(ciphertext))
        
        # Дешифруем (XOR)
        plaintext = vernam_decrypt(ciphertext, key)
        
        # Сохраняем результат
        with open(output_file, 'wb') as f:
            f.write(plaintext)
        
        print(f"✅ Файл '{input_file}' расшифрован в '{output_file}'")
        print(f"   Размер: {len(ciphertext)} байт, использовано ключа: {len(ciphertext)} байт")
        return len(ciphertext)
    
    def reset(self):
        """
        Сброс счётчика использованных байт.
        ВНИМАНИЕ: Использовать только для тестирования!
        """
        self.used_bytes = 0
        print("⚠️  Счётчик ключа сброшен (только для тестирования!)")


# ============================================================================
# ЧАСТЬ 3. УТИЛИТЫ ДЛЯ РАБОТЫ С КЛЮЧАМИ
# ============================================================================

def generate_one_time_pad(filename: str, size_mb: float = 1.44, verbose: bool = True) -> str:
    """
    Генерация файла одноразового блокнота (криптографически безопасно).
    
    Аргументы:
        filename: имя файла для сохранения ключа
        size_mb: размер в мегабайтах (по умолчанию 1.44 МБ)
        verbose: выводить ли информацию о процессе
    
    Возвращает:
        имя созданного файла
    """
    size_bytes = int(size_mb * 1024 * 1024)
    
    if verbose:
        print(f"Генерация ключа размером {size_mb} МБ ({size_bytes} байт)...")
        print("⚠️  Используется криптографически безопасный генератор (secrets)")
    
    # Генерируем ключ
    key = generate_key(size_bytes)
    
    # Сохраняем в файл
    with open(filename, 'wb') as f:
        f.write(key)
    
    if verbose:
        print(f"✅ Ключ сохранён в '{filename}'")
        print(f"   Размер: {len(key)} байт ({len(key) / (1024 * 1024):.2f} МБ)")
    
    return filename


def copy_key_file(source: str, destination: str) -> bool:
    """
    Копирование файла ключа (для создания копий Алисы и Боба).
    
    Аргументы:
        source: исходный файл
        destination: файл-копия
    
    Возвращает:
        True в случае успеха, False в случае ошибки
    """
    try:
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            dst.write(src.read())
        print(f"✅ Ключ скопирован: '{source}' -> '{destination}'")
        return True
    except Exception as e:
        print(f"❌ Ошибка копирования: {e}")
        return False


# ============================================================================
# ЧАСТЬ 4. ДЕМОНСТРАЦИОННЫЕ ПРИМЕРЫ
# ============================================================================

def example_string():
    """Демонстрация работы с строками."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 1: Шифрование и дешифрование строки")
    print("=" * 60)
    
    # Исходное сообщение
    message_text = "Привет, Алиса! Это секретное сообщение."
    message = message_text.encode('utf-8')
    print(f"Исходное сообщение: '{message_text}'")
    print(f"Длина: {len(message)} байт")
    
    # Генерируем ключ
    key = generate_key(len(message))
    print(f"Ключ (HEX): {key.hex()[:40]}... (показаны первые 40 символов)")
    print(f"Длина ключа: {len(key)} байт")
    
    # Шифрование
    ciphertext = vernam_encrypt(message, key)
    print(f"Шифротекст (HEX): {ciphertext.hex()[:40]}...")
    
    # Дешифрование
    decrypted = vernam_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    print(f"Расшифрованное сообщение: '{decrypted_text}'")
    
    # Проверка
    if message == decrypted:
        print("✅ Успех! Сообщения совпадают.")
    else:
        print("❌ Ошибка! Сообщения НЕ совпадают.")
    
    return message == decrypted


def simulate_alice_and_bob():
    """Симуляция переписки Алисы и Боба (из текста)."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Симуляция переписки Алисы и Боба")
    print("=" * 60)
    
    # Создаём временные файлы
    key_master = "temp_key_master.key"
    alice_key = "temp_alice_key.key"
    bob_key = "temp_bob_key.key"
    alice_message = "temp_alice_message.txt"
    encrypted_message = "temp_encrypted.bin"
    bob_received = "temp_bob_received.txt"
    
    try:
        # 1. До расставания Алиса и Боб создают общий ключ
        print("\n1. ДО РАССТАВАНИЯ:")
        print("   Алиса и Боб встречаются и создают общий ключ (one-time pad)")
        generate_one_time_pad(key_master, size_mb = 0.001)  # 1 КБ для примера
        
        # Создаём две копии ключа
        copy_key_file(key_master, alice_key)
        copy_key_file(key_master, bob_key)
        print("   ✅ У Алисы и Боба есть идентичные копии ключа")
        
        # 2. Алиса пишет письмо
        print("\n2. АЛИСА ОТПРАВЛЯЕТ ПИСЬМО:")
        message_text = "Привет, Боб! Как твои каникулы? У меня всё отлично! Жду встречи!"
        with open(alice_message, 'w', encoding = 'utf-8') as f:
            f.write(message_text)
        print(f"   Алиса написала письмо: '{message_text}'")
        print(f"   Размер письма: {len(message_text)} байт")
        
        # Алиса шифрует письмо
        alice_cipher = VernamCipher(alice_key)
        alice_cipher.encrypt_file(alice_message, encrypted_message)
        print("   📤 Алиса отправляет зашифрованное письмо Бобу по открытому каналу...")
        
        # 3. Боб получает и расшифровывает
        print("\n3. БОБ ПОЛУЧАЕТ И РАСШИФРОВЫВАЕТ:")
        bob_cipher = VernamCipher(bob_key)
        bob_cipher.decrypt_file(encrypted_message, bob_received)
        
        # Проверяем
        with open(bob_received, 'r', encoding = 'utf-8') as f:
            received_text = f.read()
        
        print(f"\n   📩 Боб прочитал: '{received_text}'")
        
        if message_text == received_text:
            print("   ✅ Всё совпадает! Переписка полностью защищена!")
        else:
            print("   ❌ Ошибка: сообщения не совпадают!")
            return False
        
        # 4. Показываем одноразовость
        print("\n4. ПРОВЕРКА ОДНОРАЗОВОСТИ:")
        print("   Пытаемся переиспользовать ключ...")
        try:
            alice_cipher.encrypt_file(alice_message, "temp_second_encrypted.bin")
        except ValueError as e:
            print(f"   ❌ Ошибка: {e}")
            print("   ✅ Ключ НЕ может быть переиспользован (одноразовость соблюдена)")
        
        return True
        
    finally:
        # Очистка временных файлов
        temp_files = [
            key_master, alice_key, bob_key,
            alice_message, encrypted_message, bob_received,
            "temp_second_encrypted.bin"
        ]
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        print("\n   🧹 Временные файлы удалены")


def example_with_large_text():
    """Демонстрация с большим текстом (цитата из текста)."""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Шифрование цитаты из учебника")
    print("=" * 60)
    
    # Берем цитату из текста
    quote = """Шифр Вернама был предложен в 1926 году американским инженером
Вернамом (Gilbert Vernam) и использовался на практике, но доказательство 
его невскрываемости было получено значительно позже Шенноном."""
    
    message = quote.encode('utf-8')
    print(f"Исходный текст (первые 100 символов):\n{quote[:100]}...")
    print(f"Длина: {len(message)} байт")
    
    # Генерируем ключ
    key = generate_key(len(message))
    
    # Шифруем
    ciphertext = vernam_encrypt(message, key)
    print(f"Шифротекст (HEX): {ciphertext.hex()[:60]}...")
    
    # Дешифруем
    decrypted = vernam_decrypt(ciphertext, key)
    decrypted_text = decrypted.decode('utf-8')
    
    # Проверяем
    if quote == decrypted_text:
        print("✅ Успех! Текст полностью восстановлен.")
    else:
        print("❌ Ошибка!")
    
    return quote == decrypted_text


# ============================================================================
# ЧАСТЬ 5. ИНТЕРФЕЙС КОМАНДНОЙ СТРОКИ
# ============================================================================

def create_parser():
    """Создание парсера аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description = "ШИФР ВЕРНАМА (One-Time Pad) - абсолютно стойкое шифрование",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = """
Примеры использования:
  # Показать демонстрационные примеры
  python vernam_cipher.py --demo
  
  # Сгенерировать ключ размером 1.44 МБ
  python vernam_cipher.py generate --key my_key.key --size 1.44
  
  # Зашифровать файл
  python vernam_cipher.py encrypt --input secret.txt --output secret.enc --key my_key.key
  
  # Расшифровать файл
  python vernam_cipher.py decrypt --input secret.enc --output secret_decrypted.txt --key my_key.key
  
  # Показать информацию о ключе
  python vernam_cipher.py info --key my_key.key
        """
    )
    
    parser.add_argument('--demo', action = 'store_true', help = 'Запустить демонстрационные примеры')
    
    subparsers = parser.add_subparsers(dest = 'command', help = 'Команда')
    
    # Команда: generate
    gen_parser = subparsers.add_parser('generate', help = 'Генерация ключа')
    gen_parser.add_argument('--key', required = True, help = 'Путь к файлу ключа')
    gen_parser.add_argument('--size', type = float, default = 1.44, help = 'Размер ключа в МБ (по умолчанию: 1.44)')
    
    # Команда: encrypt
    enc_parser = subparsers.add_parser('encrypt', help = 'Шифрование файла')
    enc_parser.add_argument('--input', required = True, help = 'Входной файл (открытый текст)')
    enc_parser.add_argument('--output', required = True, help = 'Выходной файл (шифротекст)')
    enc_parser.add_argument('--key', required = True, help = 'Файл ключа')
    
    # Команда: decrypt
    dec_parser = subparsers.add_parser('decrypt', help = 'Дешифрование файла')
    dec_parser.add_argument('--input', required = True, help = 'Входной файл (шифротекст)')
    dec_parser.add_argument('--output', required = True, help = 'Выходной файл (открытый текст)')
    dec_parser.add_argument('--key', required = True, help = 'Файл ключа')
    
    # Команда: info
    info_parser = subparsers.add_parser('info', help = 'Информация о ключе')
    info_parser.add_argument('--key', required = True, help = 'Файл ключа')
    
    return parser


def main():
    """Главная функция программы."""
    
    # Если нет аргументов, показываем help
    if len(sys.argv) == 1:
        print("Запустите с --demo для демонстрации или используйте команды:")
        print("  python vernam_cipher.py --help")
        return
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Режим демонстрации
    if args.demo:
        print("\n" + "=" * 60)
        print("ШИФР ВЕРНАМА - ДЕМОНСТРАЦИЯ")
        print("=" * 60)
        
        success = True
        success &= example_string()
        success &= example_with_large_text()
        success &= simulate_alice_and_bob()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ УСПЕШНО!")
        else:
            print("❌ НЕКОТОРЫЕ ДЕМОНСТРАЦИИ ЗАВЕРШИЛИСЬ С ОШИБКОЙ!")
        print("=" * 60)
        return
    
    # Команды
    try:
        if args.command == 'generate':
            generate_one_time_pad(args.key, args.size)
        
        elif args.command == 'encrypt':
            cipher = VernamCipher(args.key)
            cipher.encrypt_file(args.input, args.output)
        
        elif args.command == 'decrypt':
            cipher = VernamCipher(args.key)
            cipher.decrypt_file(args.input, args.output)
        
        elif args.command == 'info':
            if not os.path.exists(args.key):
                print(f"❌ Файл ключа '{args.key}' не найден!")
                return
            
            size = os.path.getsize(args.key)
            print(f"📁 Файл ключа: {args.key}")
            print(f"   Размер: {size} байт ({size / (1024 * 1024):.2f} МБ)")
            print(f"   Размер в битах: {size * 8}")
            
            # Проверяем случайность (первые 32 байта)
            with open(args.key, 'rb') as f:
                first_bytes = f.read(32)
            print(f"   Первые 32 байта (HEX): {first_bytes.hex()}")
            print(f"   Использовано: 0 байт (ключ новый)")
        
        else:
            parser.print_help()
    
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)


# ============================================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================================

if __name__ == "__main__":
    # Если запускаем без аргументов, но не как модуль - показываем демо
    if len(sys.argv) == 1:
        print("=" * 60)
        print("ШИФР ВЕРНАМА (One-Time Pad)")
        print("=" * 60)
        print("\nДля демонстрации работы программы запустите:")
        print("  python vernam_cipher.py --demo")
        print("\nДля работы с файлами используйте команды:")
        print("  python vernam_cipher.py --help")
        print("\nЗапускаю демонстрационный режим...")
        
        # Автоматически запускаем демо при прямом запуске без аргументов
        sys.argv.append('--demo')
    
    main()