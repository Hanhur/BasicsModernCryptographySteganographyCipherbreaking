# 2. Пакет PGP
import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
import secrets

class SimplePGP:
    """
    Упрощенная реализация принципов PGP (гибридное шифрование + подпись)
    """
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    # ---------- 1. Генерация ключевой пары (асимметричное шифрование) ----------
    def generate_keys(self, key_size = 2048):
        """Генерирует пару RSA-ключей (аналог генерации связки в PGP)"""
        self.private_key = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = key_size
        )
        self.public_key = self.private_key.public_key()
        print(f"[+] Ключевая пара RSA ({key_size} бит) успешно сгенерирована.")
        return self.private_key, self.public_key
    
    # ---------- 2. Гибридное шифрование (PGP-стиль) ----------
    def hybrid_encrypt(self, plaintext: bytes, receiver_public_key) -> dict:
        """
        Шифрует сообщение:
        1. Генерирует случайный сессионный ключ (AES-256).
        2. Шифрует данные этим ключом (симметрично).
        3. Шифрует сессионный ключ публичным ключом получателя (асимметрично).
        Возвращает словарь с зашифрованными данными и ключом.
        """
        # 1. Генерируем случайный сессионный ключ (32 байта = 256 бит)
        session_key = secrets.token_bytes(32)
        
        # 2. Симметричное шифрование данных (AES в режиме GCM - обеспечивает аутентификацию)
        iv = secrets.token_bytes(16)  # Вектор инициализации
        cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # 3. Асимметричное шифрование сессионного ключа (RSA)
        encrypted_session_key = receiver_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf = padding.MGF1(algorithm = hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        
        # Возвращаем все компоненты (как в PGP-пакете)
        return {
            "encrypted_session_key": base64.b64encode(encrypted_session_key).decode('utf-8'),
            "iv": base64.b64encode(iv).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')  # Для проверки целостности
        }
    
    # ---------- 3. Гибридное дешифрование ----------
    def hybrid_decrypt(self, encrypted_package: dict, receiver_private_key) -> bytes:
        """
        Расшифровывает пакет:
        1. Расшифровывает сессионный ключ своим приватным ключом.
        2. Расшифровывает данные симметричным ключом.
        """
        # 1. Декодируем компоненты из Base64
        encrypted_session_key = base64.b64decode(encrypted_package["encrypted_session_key"])
        iv = base64.b64decode(encrypted_package["iv"])
        ciphertext = base64.b64decode(encrypted_package["ciphertext"])
        tag = base64.b64decode(encrypted_package["tag"])
        
        # 2. Расшифровываем сессионный ключ (RSA)
        session_key = receiver_private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf = padding.MGF1(algorithm = hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
        
        # 3. Расшифровываем данные (AES-GCM)
        cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    # ---------- 4. Цифровая подпись (как в PGP) ----------
    def sign_message(self, message: bytes, signing_private_key) -> str:
        """Подписывает сообщение приватным ключом отправителя"""
        signature = signing_private_key.sign(
            message,
            padding.PSS(
                mgf = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, message: bytes, signature_b64: str, signer_public_key) -> bool:
        """Проверяет подпись публичным ключом отправителя"""
        signature = base64.b64decode(signature_b64)
        try:
            signer_public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf = padding.MGF1(hashes.SHA256()),
                    salt_length = padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False


# ---------- ДЕМОНСТРАЦИЯ РАБОТЫ (как в тексте про Фила Циммермана) ----------
if __name__ == "__main__":
    print("=" * 60)
    print("  PGP-подобная гибридная криптосистема (Python)")
    print("  Вдохновлено идеями Фила Циммермана")
    print("=" * 60)
    
    # 1. Создаем двух абонентов: Алису (отправитель) и Боба (получатель)
    alice = SimplePGP()
    bob = SimplePGP()
    
    # Генерируем ключи
    print("\n[1] Генерация ключей...")
    alice.generate_keys(2048)
    bob.generate_keys(2048)
    
    # 2. Алиса хочет отправить секретное сообщение Бобу
    # ИСПРАВЛЕНО: используем обычную строку и кодируем в UTF-8
    original_text = "Привет, Боб! Это секретное сообщение, зашифрованное по принципам PGP. Свобода шифрования важна!"
    original_message = original_text.encode('utf-8')
    print(f"\n[2] Исходное сообщение: {original_text}")
    
    # 3. Шифрование (Алиса шифрует публичным ключом Боба)
    print("\n[3] Шифрование (гибридная схема AES-256 + RSA)...")
    encrypted_packet = alice.hybrid_encrypt(original_message, bob.public_key)
    print(f"    Зашифрованный сессионный ключ (RSA): {encrypted_packet['encrypted_session_key'][:30]}...")
    print(f"    Зашифрованные данные (AES): {encrypted_packet['ciphertext'][:30]}...")
    
    # 4. Цифровая подпись (Алиса подписывает своим приватным ключом)
    print("\n[4] Создание цифровой подписи (приватный ключ Алисы)...")
    signature = alice.sign_message(original_message, alice.private_key)
    print(f"    Подпись: {signature[:30]}...")
    
    # 5. Боб расшифровывает (своим приватным ключом)
    print("\n[5] Боб расшифровывает сообщение...")
    decrypted_bytes = bob.hybrid_decrypt(encrypted_packet, bob.private_key)
    decrypted_text = decrypted_bytes.decode('utf-8')
    print(f"    Расшифровано: {decrypted_text}")
    
    # 6. Боб проверяет подпись (публичным ключом Алисы)
    print("\n[6] Проверка цифровой подписи (публичный ключ Алисы)...")
    is_valid = bob.verify_signature(decrypted_bytes, signature, alice.public_key)
    print(f"    Статус подписи: {'✅ ПОДПИСЬ ВЕРНА (сообщение не изменено)' if is_valid else '❌ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА'}")
    
    # 7. Имитация атаки (изменение сообщения)
    print("\n[7] Имитация взлома (изменение 1 байта в сообщении)...")
    tampered_bytes = decrypted_bytes[:-1] + b'!'  # Меняем последний байт
    is_valid_tampered = bob.verify_signature(tampered_bytes, signature, alice.public_key)
    print(f"    Статус подписи для изменённого текста: {'✅ ВЕРНА' if is_valid_tampered else '❌ НЕДЕЙСТВИТЕЛЬНА (обнаружена модификация)'}")
    
    print("\n" + "=" * 60)
    print("  Программа демонстрирует принципы, заложенные в PGP:")
    print("  1. Гибридное шифрование (быстро + безопасно)")
    print("  2. Цифровая подпись для аутентификации")
    print("  3. Разделение ролей: шифрование для всех, дешифрование для владельца")
    print("=" * 60)