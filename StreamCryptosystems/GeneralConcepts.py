# 1 . Общие понятия
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поточная криптосистема Вернама (XOR-шифр)
Реализация на основе теоретических принципов:
C_i = m_i XOR k_i, где m_i - бит открытого текста, k_i - бит ключа
"""

import os
import secrets
import hashlib
from typing import Tuple, Optional


class VernamStreamCipher:
    """
    Класс, реализующий поточное XOR-шифрование.
    """
    
    @staticmethod
    def _xor_bytes(data: bytes, key: bytes) -> bytes:
        """
        Побайтовое XOR-сложение (аналог побитового для бинарного алфавита).
        Каждый байт обрабатывается как 8 бит.
        """
        return bytes(a ^ b for a, b in zip(data, key))
    
    # ================================================================
    # Режим 1: Одноразовый блокнот (One-Time Pad) — абсолютная секретность
    # ================================================================
    
    @staticmethod
    def generate_otp_key(length: int) -> bytes:
        """
        Генерирует истинно случайный ключ длиной `length` байт.
        Используется криптографически стойкий генератор (secrets).
        
        Свойства:
        - Ключ не короче сообщения
        - Каждый бит ключа независим и равновероятен
        - При соблюдении условий даёт абсолютную секретность по Шеннону
        """
        return secrets.token_bytes(length)
    
    @staticmethod
    def encrypt_otp(plaintext: bytes, key: bytes) -> bytes:
        """
        Шифрование в режиме одноразового блокнота.
        Требует: len(key) >= len(plaintext)
        """
        if len(key) < len(plaintext):
            raise ValueError("OTP: Длина ключа должна быть не короче сообщения")
        # Используем только первые len(plaintext) байт ключа
        return VernamStreamCipher._xor_bytes(plaintext, key[:len(plaintext)])
    
    @staticmethod
    def decrypt_otp(ciphertext: bytes, key: bytes) -> bytes:
        """
        Дешифрование в режиме одноразового блокнота.
        Операция полностью симметрична шифрованию (XOR).
        """
        if len(key) < len(ciphertext):
            raise ValueError("OTP: Длина ключа должна быть не короче шифротекста")
        return VernamStreamCipher._xor_bytes(ciphertext, key[:len(ciphertext)])
    
    # ================================================================
    # Режим 2: Поточный шифр с псевдослучайным генератором (практичный)
    # ================================================================
    
    @staticmethod
    def _pseudo_random_keystream(seed: bytes, length: int) -> bytes:
        """
        Генератор псевдослучайного ключевого потока на основе хеш-функции SHA-256.
        Имитирует работу регистра сдвига (LFSR) или современных поточных шифров.
        
        Внимание: это УЧЕБНЫЙ пример, не используйте для реальной защиты!
        Реальные поточные шифры (ChaCha20, Salsa20) значительно сложнее.
        """
        keystream = bytearray()
        counter = 0
        while len(keystream) < length:
            # Формируем вход: seed + счётчик
            data = seed + counter.to_bytes(8, byteorder='big')
            # Хешируем и добавляем к ключевому потоку
            hash_block = hashlib.sha256(data).digest()
            keystream.extend(hash_block)
            counter += 1
        return bytes(keystream[:length])
    
    @staticmethod
    def encrypt_stream(plaintext: bytes, user_key: bytes) -> Tuple[bytes, bytes]:
        """
        Шифрование с использованием короткого пользовательского ключа.
        Генерирует псевдослучайный ключевой поток из user_key.
        
        Возвращает: (ciphertext, keystream_used) - для демонстрации
        """
        keystream = VernamStreamCipher._pseudo_random_keystream(user_key, len(plaintext))
        ciphertext = VernamStreamCipher._xor_bytes(plaintext, keystream)
        return ciphertext, keystream
    
    @staticmethod
    def decrypt_stream(ciphertext: bytes, user_key: bytes) -> bytes:
        """
        Дешифрование с использованием того же пользовательского ключа.
        Генератор ключевого потока детерминирован, поэтому результат совпадает.
        """
        keystream = VernamStreamCipher._pseudo_random_keystream(user_key, len(ciphertext))
        return VernamStreamCipher._xor_bytes(ciphertext, keystream)


# ================================================================
# Демонстрация работы
# ================================================================

def demo_otp_absolute_secrecy():
    """Демонстрация режима одноразового блокнота (абсолютная секретность)"""
    print("\n" + "=" * 60)
    print("РЕЖИМ 1: ОДНОРАЗОВЫЙ БЛОКНОТ (Абсолютная секретность)")
    print("=" * 60)
    
    # Исходный текст (в бинарном представлении)
    message = b"Hello, Vernam! This is a secret message."
    print(f"Исходный текст: {message}")
    print(f"Длина сообщения: {len(message)} байт = {len(message) * 8} бит")
    
    # Генерация истинно случайного ключа (не короче сообщения)
    key = VernamStreamCipher.generate_otp_key(len(message))
    print(f"Случайный ключ (hex): {key.hex()}")
    print(f"Длина ключа: {len(key)} байт (не короче сообщения ✓)")
    
    # Шифрование
    ciphertext = VernamStreamCipher.encrypt_otp(message, key)
    print(f"Шифротекст (hex): {ciphertext.hex()}")
    
    # Дешифрование
    decrypted = VernamStreamCipher.decrypt_otp(ciphertext, key)
    print(f"Расшифрованный текст: {decrypted}")
    
    # Проверка
    assert decrypted == message, "Ошибка: расшифровка не совпала с исходным текстом"
    print("✓ Расшифровка успешна")
    
    # Демонстрация: частичная расшифровка не даёт информации об остатке
    partial_key = key[:5]  # знаем только первые 5 байт ключа
    partial_decrypt = VernamStreamCipher.decrypt_otp(ciphertext[:5], partial_key)
    print(f"\nЧастичная расшифровка (первые 5 байт): {partial_decrypt}")
    print("Остальная часть шифротекста остаётся абсолютно неопределённой.")


def demo_stream_cipher_practical():
    """Демонстрация практического поточного шифра с коротким ключом"""
    print("\n" + "=" * 60)
    print("РЕЖИМ 2: ПРАКТИЧЕСКИЙ ПОТОЧНЫЙ ШИФР (Короткий ключ)")
    print("=" * 60)
    
    # Исходный текст
    message = b"Stream cipher example with short key. Much faster and practical!"
    print(f"Исходный текст: {message[:60]}..." if len(message) > 60 else f"Исходный текст: {message}")
    print(f"Длина сообщения: {len(message)} байт")
    
    # Короткий пользовательский ключ (например, 256 бит = 32 байта)
    user_key = b"my_secret_key_256_bits_secure_!!!"  # 32 байта
    print(f"Пользовательский ключ (короткий): {user_key}")
    print(f"Длина ключа: {len(user_key)} байт << длины сообщения ({len(message)} байт)")
    
    # Шифрование с генерацией псевдослучайного ключевого потока
    ciphertext, keystream = VernamStreamCipher.encrypt_stream(message, user_key)
    print(f"\nСгенерированный ключевой поток (первые 32 байта hex): {keystream[:32].hex()}")
    print(f"Шифротекст (первые 32 байта hex): {ciphertext[:32].hex()}")
    
    # Дешифрование
    decrypted = VernamStreamCipher.decrypt_stream(ciphertext, user_key)
    print(f"Расшифрованный текст: {decrypted[:60]}..." if len(decrypted) > 60 else f"Расшифрованный текст: {decrypted}")
    
    assert decrypted == message, "Ошибка: расшифровка не совпала с исходным текстом"
    print("✓ Расшифровка успешна")
    
    # Демонстрация: изменение одного бита ключа даёт полностью другой ключевой поток
    wrong_key = b"my_secret_key_256_bits_secure_!!?"  # последний байт изменён
    wrong_decrypt = VernamStreamCipher.decrypt_stream(ciphertext, wrong_key)
    print(f"\nДешифрование с НЕВЕРНЫМ ключом (изменён 1 бит): {wrong_decrypt[:60]}...")
    print("Результат — бессмысленный текст, не похожий на исходный.")


def demo_bitwise_operation():
    """Демонстрация побитовой операции XOR на бинарном алфавите {0, 1}"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ПОБИТОВОЙ ОПЕРАЦИИ (бинарный алфавит {0, 1})")
    print("=" * 60)
    
    # Пример для наглядности: 8 бит открытого текста и 8 бит ключа
    m_bits = "10110010"  # открытый текст (биты)
    k_bits = "01101101"  # ключевой поток (биты)
    
    print(f"Открытый текст (m_i):   {m_bits}")
    print(f"Ключевой поток (k_i):   {k_bits}")
    print(f"Шифротекст (c_i = m_i XOR k_i): ", end = "")
    
    c_bits = ''.join(str(int(m_bits[i]) ^ int(k_bits[i])) for i in range(8))
    print(c_bits)
    
    # Проверка обратимости: шифротекст XOR ключ = открытый текст
    m_recovered = ''.join(str(int(c_bits[i]) ^ int(k_bits[i])) for i in range(8))
    print(f"Обратное преобразование (c_i XOR k_i): {m_recovered}")
    assert m_recovered == m_bits
    print("✓ Операция XOR обратима (симметрична)")


def demo_vulnerability_key_reuse():
    """Демонстрация уязвимости при повторном использовании ключа"""
    print("\n" + "=" * 60)
    print("УЯЗВИМОСТЬ: ПОВТОРНОЕ ИСПОЛЬЗОВАНИЕ КЛЮЧА")
    print("=" * 60)
    
    # Два разных сообщения, зашифрованных ОДНИМ И ТЕМ ЖЕ ключом
    message1 = b"Attack at dawn!!!"
    message2 = b"Retreat at dusk!!!"
    
    # Один и тот же ключ (нарушение правил безопасности)
    key = b"fixed_shared_key_"
    if len(key) < max(len(message1), len(message2)):
        key = key * (max(len(message1), len(message2)) // len(key) + 1)
    
    cipher1 = VernamStreamCipher.encrypt_otp(message1, key)
    cipher2 = VernamStreamCipher.encrypt_otp(message2, key)
    
    print(f"Сообщение 1: {message1}")
    print(f"Сообщение 2: {message2}")
    print(f"Шифротекст 1: {cipher1.hex()}")
    print(f"Шифротекст 2: {cipher2.hex()}")
    
    # Атака: XOR двух шифротекстов = XOR двух открытых текстов
    xor_ciphers = VernamStreamCipher._xor_bytes(cipher1, cipher2)
    xor_messages = VernamStreamCipher._xor_bytes(message1, message2)
    
    print(f"\nC1 XOR C2 = {xor_ciphers.hex()}")
    print(f"M1 XOR M2 = {xor_messages.hex()}")
    print("Они совпадают! Это позволяет криптоаналитикам восстанавливать сообщения.")
    print("⚠ НИКОГДА не используйте один и тот же ключ дважды в системе Вернама!")


# ================================================================
# Главная функция
# ================================================================

def main():
    """Запуск всех демонстраций"""
    print("\n" + "=" * 60)
    print("ПОТОЧНАЯ КРИПТОСИСТЕМА ВЕРНАМА")
    print("C_i = m_i XOR k_i, где m_i, k_i ∈ {0, 1}")
    print("=" * 60)
    
    demo_bitwise_operation()
    demo_otp_absolute_secrecy()
    demo_stream_cipher_practical()
    demo_vulnerability_key_reuse()
    
    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ ЗАМЕЧАНИЯ")
    print("=" * 60)
    print("""
        1. Одноразовый блокнот (OTP): абсолютная секретность, но требует
        ключа длины не короче сообщения.
        2. Практические поточные шифры: используют короткий ключ (128-256 бит)
        для генерации псевдослучайного ключевого потока.
        3. Ключевой поток НИКОГДА не должен повторяться.
        4. Современные поточные шифры: ChaCha20, Salsa20, Grain.
        5. Данная реализация — УЧЕБНАЯ, для реального использования
        применяйте стандартные библиотеки (cryptography, PyCryptodome).
    """)


if __name__ == "__main__":
    main()