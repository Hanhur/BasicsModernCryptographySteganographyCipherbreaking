# 2. Алгоритм (функция) шифрования
"""
Программа, демонстрирующая принципы криптографии из текста:
- Функция шифрования E(m) = c
- Функция дешифрования D(c, key) = m
- Односторонняя функция с секретом (ключом)
- «Легко» — с ключом, «трудно» — без ключа
"""

from cryptography.fernet import Fernet
import base64
import hashlib
import os


def generate_key():
    """
    Генерирует случайный ключ шифрования (секрет).
    В реальных системах ключ должен храниться в безопасности.
    """
    return Fernet.generate_key()


def derive_key_from_password(password: str) -> bytes:
    """
    Получает ключ из пароля (для демонстрации, что знание секрета позволяет расшифровать).
    Это не сам ключ, а его детерминированное преобразование.
    """
    # Используем PBKDF2 для получения надёжного ключа из пароля
    salt = b'some_static_salt_16b'  # В реальных системах соль должна быть случайной и храниться
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.urlsafe_b64encode(key[:32])  # Fernet требует 32 байта в base64


def encrypt(plaintext: str, key: bytes) -> bytes:
    """
    Функция шифрования E(m, key) = c.
    Легко вычисляется с ключом.
    """
    f = Fernet(key)
    ciphertext = f.encrypt(plaintext.encode('utf-8'))
    return ciphertext


def decrypt(ciphertext: bytes, key: bytes) -> str:
    """
    Функция дешифрования D(c, key) = m.
    Легко вычисляется ТОЛЬКО с правильным ключом.
    """
    f = Fernet(key)
    plaintext = f.decrypt(ciphertext)
    return plaintext.decode('utf-8')


def try_decrypt_without_key(ciphertext: bytes):
    """
    Демонстрация того, что без ключа восстановить текст «трудно».
    Здесь мы просто показываем, что случайный ключ не подойдёт.
    """
    print("\n[Попытка взлома без знания ключа]")
    fake_key = generate_key()  # случайный ключ
    try:
        wrong_decryption = decrypt(ciphertext, fake_key)
        print(f"Удалось расшифровать: {wrong_decryption}")
    except Exception as e:
        print(f"Не удалось расшифровать: {e}")
        print("Это иллюстрирует, что без правильного ключа восстановить текст трудно.")


def main():
    print("=== Криптосистема: односторонняя функция с секретом ===\n")
    
    # 1. Исходный текст (m)
    plaintext = input("Введите текст для шифрования: ")
    
    # 2. Генерация ключа (секрет)
    key = generate_key()
    print(f"\n[Ключ сгенерирован] (в реальной системе он хранится в тайне): {key.decode()}")
    
    # 3. Шифрование (лёгкая операция с ключом)
    ciphertext = encrypt(plaintext, key)
    print(f"\n[Зашифрованный текст] (c = E(m)): {ciphertext}")
    
    # 4. Дешифрование легитимным пользователем (легко с ключом)
    decrypted_text = decrypt(ciphertext, key)
    print(f"\n[Дешифрование с ключом] (легко): {decrypted_text}")
    
    # 5. Проверка, что текст восстановлен однозначно
    assert plaintext == decrypted_text, "Ошибка: текст не восстановился!"
    print("\n[Успех] Исходный текст однозначно восстановлен.")
    
    # 6. Попытка взлома без ключа (трудно)
    try_decrypt_without_key(ciphertext)
    
    # 7. Дополнительно: демонстрация, что знание пароля (секрета) даёт ключ
    print("\n=== Демонстрация: дешифрование по паролю (секрет) ===")
    password = input("Задайте пароль-секрет (тот, кто знает его, сможет расшифровать): ")
    key_from_password = derive_key_from_password(password)
    ciphertext2 = encrypt(plaintext, key_from_password)
    print(f"Текст зашифрован с ключом из пароля.")
    
    check_password = input("Введите пароль для расшифровки: ")
    key_check = derive_key_from_password(check_password)
    try:
        recovered = decrypt(ciphertext2, key_check)
        print(f"Расшифровано: {recovered}")
        if check_password == password:
            print("✅ Пароль верен. Легитимный пользователь восстановил текст.")
        else:
            print("❌ Пароль неверен — это демонстрирует, что без правильного секрета текст не восстановить.")
    except Exception:
        print("❌ Неверный пароль. Текст не расшифрован.")


if __name__ == "__main__":
    main()