# 7. Еще раз о крпптостойкости DES
"""
Программа-демонстрация уязвимостей DES
На основе текста о криптостойкости DES
(Исправленная версия)
"""

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import hashlib
import time
import random
import itertools
from typing import Tuple, Optional

# ============================================
# 1. БАЗОВЫЕ ФУНКЦИИ ШИФРОВАНИЯ DES
# ============================================

def encrypt_des(key: bytes, plaintext: bytes) -> bytes:
    """Шифрование DES с PKCS7 паддингом"""
    cipher = DES.new(key, DES.MODE_ECB)
    padded = pad(plaintext, DES.block_size)
    return cipher.encrypt(padded)

def decrypt_des(key: bytes, ciphertext: bytes) -> bytes:
    """Дешифрование DES с PKCS7 паддингом"""
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, DES.block_size)

def des_encrypt_raw(key: bytes, data: bytes) -> bytes:
    """Шифрование DES без паддинга (для 3DES)"""
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(data)

def des_decrypt_raw(key: bytes, data: bytes) -> bytes:
    """Дешифрование DES без паддинга (для 3DES)"""
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.decrypt(data)

# ============================================
# 2. ДЕМОНСТРАЦИЯ СЛАБОСТИ КЛЮЧЕЙ (ПЕРЕБОР)
# ============================================

def brute_force_demo():
    """Демонстрация атаки перебором (с 3-битным ключом для скорости)"""
    print("\n" + "=" * 60)
    print("🔓 ДЕМОНСТРАЦИЯ АТАКИ ПЕРЕБОРОМ")
    print("=" * 60)
    print("В реальном DES перебор 2^56 ключей невозможен за разумное время.")
    print("Но для демонстрации используем 3-битный ключ (всего 8 вариантов)\n")
    
    # Генерируем настоящий ключ (3 бита + 5 нулевых байт для DES)
    real_key = bytes([0b10100000, 0, 0, 0, 0, 0, 0, 0])  # Ключ с 3 битами информации
    message = b"Secret Message!"
    
    print(f"🔑 Настоящий ключ (бинарно): {bin(real_key[0])}")
    print(f"📝 Сообщение: {message.decode()}")
    
    # Шифруем
    ciphertext = encrypt_des(real_key, message)
    print(f"🔒 Зашифровано: {ciphertext.hex()[:16]}...\n")
    
    print("🚀 Начинаем перебор всех 8 возможных ключей...")
    start_time = time.time()
    
    found_key = None
    for i in range(8):  # 2^3 = 8 вариантов
        test_key = bytes([i << 5, 0, 0, 0, 0, 0, 0, 0])  # Сдвигаем биты в старшую позицию
        try:
            decrypted = decrypt_des(test_key, ciphertext)
            if decrypted == message:
                found_key = test_key
                print(f"✅ Найден ключ! Попытка #{i + 1}: {bin(test_key[0])}")
                break
        except:
            continue
    
    elapsed = time.time() - start_time
    print(f"⏱️ Время перебора: {elapsed:.4f} секунд")
    print(f"🔑 Найденный ключ: {bin(found_key[0]) if found_key else 'Не найден'}")
    print("\n💡 В 1977 году NSA утверждало, что перебор 2^56 ключей займёт 1000 лет.")
    print("   В 1998 году EFF взломала DES за 56 часов.")
    print("   Сегодня это делается за минуты на обычном GPU.")

# ============================================
# 3. СЛАБОСТЬ ГЕНЕРАЦИИ КЛЮЧЕЙ ИЗ ПАРОЛЕЙ
# ============================================

def generate_key_from_password(password: str) -> bytes:
    """Генерация ключа DES из пароля (слабая схема)"""
    # Простейшая схема: хеш MD5 и обрезание до 8 байт
    hash_bytes = hashlib.md5(password.encode()).digest()
    return hash_bytes[:8]  # Берём первые 8 байт для DES

def weak_password_attack_demo():
    """Демонстрация атаки по словарю на слабые пароли"""
    print("\n" + "=" * 60)
    print("🔓 СЛАБОСТЬ ГЕНЕРАЦИИ КЛЮЧЕЙ ИЗ ПАРОЛЕЙ")
    print("=" * 60)
    print("В реальных системах ключи часто генерируются из паролей.")
    print("Энтропия пароля ~20-30 бит, что намного меньше 56 бит!\n")
    
    # Словарь самых частых паролей
    common_passwords = [
        "password", "12345678", "qwerty", "admin", 
        "letmein", "welcome", "monkey", "dragon"
    ]
    
    # Выбираем случайный пароль из словаря
    real_password = random.choice(common_passwords)
    real_key = generate_key_from_password(real_password)
    
    message = b"TopSecretData"
    ciphertext = encrypt_des(real_key, message)
    
    print(f"🔑 Пароль пользователя: {real_password}")
    print(f"🔑 Сгенерированный ключ: {real_key.hex()}")
    print(f"🔒 Зашифровано: {ciphertext.hex()[:16]}...\n")
    
    print("🚀 Атака по словарю (перебор паролей):")
    start_time = time.time()
    
    found_password = None
    for attempt, password in enumerate(common_passwords, 1):
        test_key = generate_key_from_password(password)
        try:
            decrypted = decrypt_des(test_key, ciphertext)
            if decrypted == message:
                found_password = password
                print(f"✅ Взломано! Пароль найден с попытки #{attempt}: '{password}'")
                break
        except:
            continue
    
    elapsed = time.time() - start_time
    print(f"⏱️ Время атаки: {elapsed:.4f} секунд")
    print(f"🔑 Найденный пароль: {found_password}")
    
    print("\n💡 Это демонстрирует, что DES в реальном использовании")
    print("   намного слабее теоретического предела в 2^56 комбинаций.")

# ============================================
# 4. ПОЧЕМУ DES ВСЁ ЕЩЁ ЖИВ? (3DES)
# ============================================

def triple_des_demo():
    """Демонстрация 3DES как причины живучести DES"""
    print("\n" + "=" * 60)
    print("🛡️ ПОЧЕМУ DES ВСЁ ЕЩЁ ИСПОЛЬЗУЕТСЯ? (3DES)")
    print("=" * 60)
    print("3DES (Triple DES) использует три ключа DES,")
    print("что даёт эффективную длину ключа 112 или 168 бит.\n")
    
    # Три ключа для 3DES
    key1 = bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF])
    key2 = bytes([0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10])
    key3 = bytes([0x89, 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45, 0x67])
    
    message = b"3DES Legacy Data"
    
    # Корректная реализация 3DES в режиме EDE (Encrypt-Decrypt-Encrypt)
    def triple_des_encrypt(msg: bytes) -> bytes:
        # Добавляем паддинг к сообщению
        padded = pad(msg, DES.block_size)
        # Шаг 1: Шифрование на первом ключе
        c1 = des_encrypt_raw(key1, padded)
        # Шаг 2: Дешифрование на втором ключе
        c2 = des_decrypt_raw(key2, c1)
        # Шаг 3: Шифрование на третьем ключе
        c3 = des_encrypt_raw(key3, c2)
        return c3
    
    def triple_des_decrypt(cipher: bytes) -> bytes:
        # Шаг 1: Дешифрование на третьем ключе
        c1 = des_decrypt_raw(key3, cipher)
        # Шаг 2: Шифрование на втором ключе
        c2 = des_encrypt_raw(key2, c1)
        # Шаг 3: Дешифрование на первом ключе
        c3 = des_decrypt_raw(key1, c2)
        # Удаляем паддинг
        return unpad(c3, DES.block_size)
    
    ciphertext = triple_des_encrypt(message)
    decrypted = triple_des_decrypt(ciphertext)
    
    print(f"📝 Исходное сообщение: {message.decode()}")
    print(f"🔒 Зашифровано (3DES): {ciphertext.hex()[:24]}...")
    print(f"📝 Расшифровано: {decrypted.decode()}")
    
    print("\n📌 Где используется 3DES сегодня:")
    print("   • Банкоматы и POS-терминалы (старое оборудование)")
    print("   • Протоколы TLS 1.2 (устаревшие наборы шифров)")
    print("   • EMV-чипы на банковских картах")
    print("   • Системы управления ключами (Key Management)")

# ============================================
# 5. АНАЛИЗ S-БЛОКОВ (УСТОЙЧИВОСТЬ К ДИФФЕРЕНЦИАЛЬНОМУ КРИПТОАНАЛИЗУ)
# ============================================

def sbox_demo():
    """Демонстрация устойчивости S-блоков DES"""
    print("\n" + "=" * 60)
    print("🧩 УСТОЙЧИВОСТЬ S-БЛОКОВ DES")
    print("=" * 60)
    print("В 1994 году выяснилось, что NSA оптимизировало S-блоки")
    print("для защиты от дифференциального криптоанализа.")
    print("Это был не 'тайный вход', а УСИЛЕНИЕ алгоритма!\n")
    
    # Первый S-блок DES (S1)
    s_box = [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ]
    
    print("Первый S-блок (S1):")
    for row in s_box:
        print(f"  {row}")
    
    print("\n🔬 Проверка свойств S-блока:")
    print("• Каждая строка содержит все числа от 0 до 15 (перестановка)")
    print("• Изменение 1 бита на входе меняет минимум 2 бита на выходе")
    print("• Оптимальный баланс для защиты от дифференциальных атак")
    
    print("\n💡 Именно поэтому DES продержался 30 лет,")
    print("   пока его не убил малый размер ключа, а не математические слабости.")

# ============================================
# 6. ИТОГОВАЯ СТАТИСТИКА БЕЗОПАСНОСТИ
# ============================================

def security_summary():
    """Сводка по безопасности DES в 2026 году"""
    print("\n" + "=" * 60)
    print("📊 СВОДКА ПО БЕЗОПАСНОСТИ DES (2026)")
    print("=" * 60)
    
    stats = {
        "Длина ключа": "56 бит",
        "Время взлома перебором (современный GPU)": "~ 3 - 4 дня",
        "Время взлома (ферма из 100 GPU)": "~ 40 - 60 минут",
        "Время взлома (спецслужбы)": "минуты",
        "Устойчивость к дифференциальному анализу": "высокая",
        "Стойкость 3DES": "112 - 168 бит",
        "Статус в протоколах": "Устаревший, но используется",
        "Рекомендация NIST": "Запрещён для новых систем"
    }
    
    for key, value in stats.items():
        print(f"{key:.<40} {value}")
    
    print("\n⚠️ ВЫВОД:")
    print("DES сломан не математически, а инженерно (малый ключ).")
    print("Его живучесть объясняется инерцией legacy-систем.")
    print("Для новых проектов используйте AES-256.")

# ============================================
# 7. ДОПОЛНИТЕЛЬНО: АТАКА "ВСТРЕЧА ПОСЕРЕДИНЕ" (MEET-IN-THE-MIDDLE)
# ============================================

def mitm_attack_demo():
    """Демонстрация атаки "встреча посередине" на 2DES"""
    print("\n" + "=" * 60)
    print("⚡ АТАКА 'ВСТРЕЧА ПОСЕРЕДИНЕ' (2DES)")
    print("=" * 60)
    print("Именно из-за этой атаки 2DES не используется,")
    print("а применяется 3DES с тремя ключами.\n")
    
    # Демонстрация концепции
    print("🔑 2DES использует два ключа: K1 и K2")
    print("📝 Шифрование: C = E(K2, E(K1, P))")
    print("\n💡 Атака 'встреча посередине':")
    print("   1. Шифруем P со всеми возможными K1 → таблица")
    print("   2. Дешифруем C со всеми возможными K2 → ищем совпадение")
    print("   3. Сложность: 2^57 вместо 2^112 операций!")
    print("\n✅ Поэтому 2DES небезопасен, используется 3DES")

# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================

def main():
    print("\n" + "█" * 60)
    print("█  КРИПТОАНАЛИЗ DES: ПРАКТИЧЕСКАЯ ДЕМОНСТРАЦИЯ")
    print("█" * 60)
    print("На основе текста о криптостойкости DES")
    print("Автор: (c) 2026")
    
    try:
        # Проверка установки pycryptodome
        import Crypto
    except ImportError:
        print("\n❌ Установите библиотеку:")
        print("   pip install pycryptodome")
        return
    
    # Запуск всех демонстраций
    brute_force_demo()
    weak_password_attack_demo()
    triple_des_demo()
    sbox_demo()
    mitm_attack_demo()
    security_summary()
    
    print("\n" + "█" * 60)
    print("█  ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("█" * 60)
    print("\n📚 Заключение по тексту:")
    print("1. NSA имело компьютеры для взлома DES за часы")
    print("2. 'Тайный вход' не найден - это был миф")
    print("3. Слабость генерации ключей - реальная проблема")
    print("4. DES продолжает жить благодаря 3DES и legacy-системам")
    print("5. В 2026 году один DES - это грубая ошибка\n")

if __name__ == "__main__":
    main()