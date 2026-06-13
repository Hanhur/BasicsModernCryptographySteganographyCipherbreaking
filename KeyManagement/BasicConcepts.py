# 1. Основные понятия
import os
import time
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ===============================
# 1. Принцип Керкгоффса
# ===============================
def kerckhoffs_demo():
    print("\n=== 1. Принцип Керкгоффса ===")
    print("Шифр известен, вся стойкость в ключе.")
    print("Демонстрация: AES (алгоритм открыт) с разными ключами.\n")
    
    message = b"Secret data"
    key1 = os.urandom(16)  # 128 бит
    key2 = os.urandom(16)
    iv = os.urandom(16)  # Вектор инициализации (не секретный)
    
    # Используем современный режим GCM (аутентифицированное шифрование)
    cipher1 = Cipher(algorithms.AES(key1), modes.GCM(iv), backend = default_backend())
    cipher2 = Cipher(algorithms.AES(key2), modes.GCM(iv), backend = default_backend())
    
    encryptor1 = cipher1.encryptor()
    encryptor2 = cipher2.encryptor()
    
    ct1 = encryptor1.update(message) + encryptor1.finalize()
    ct2 = encryptor2.update(message) + encryptor2.finalize()
    
    print(f"Исходное сообщение: {message}")
    print(f"Шифротекст с ключом 1: {ct1.hex()[:32]}...")
    print(f"Шифротекст с ключом 2: {ct2.hex()[:32]}...")
    print("Вывод: алгоритм один, но разные ключи дают разный шифротекст.")
    print("Без правильного ключа расшифровать невозможно.\n")


# ===============================
# 2. Оценка стойкости перебором
# ===============================
def brute_force_estimate():
    print("\n=== 2. Оценка стойкости перебором ===")
    bits = [40, 56, 64, 80, 128]
    checks_per_sec = 10 ** 6  # 1 млн ключей/сек
    
    for b in bits:
        total_keys = 2 ** b
        seconds = total_keys / checks_per_sec
        years = seconds / (365.25 * 24 * 3600)
        print(f"Ключ {b:3d} бит: {total_keys:.2e} ключей, перебор ≈ {years:.2e} лет")
    
    print("\nПо тексту: 64 бита → 5–6 тыс. лет при 10⁶ проверок/сек.")
    print("56 бит перебирается практически, 512 бит RSA вскрыт в 1999 году.\n")


# ===============================
# 3. Симметричное шифрование
# ===============================
def symmetric_key_demo():
    print("\n=== 3. Симметричное шифрование (сессионный ключ) ===")
    session_key = os.urandom(32)  # 256 бит
    print(f"Сгенерирован сессионный ключ (256 бит): {session_key.hex()[:16]}...")
    
    message = b"Confidential report: budget 2026"
    iv = os.urandom(12)  # GCM рекомендует 12 байт nonce
    cipher = Cipher(algorithms.AES(session_key), modes.GCM(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()
    
    print(f"Исходное сообщение: {message}")
    print(f"Зашифровано (AES-256-GCM): {ciphertext.hex()[:32]}...")
    
    # Расшифровка (требуется тот же nonce и тег аутентичности)
    decryptor = Cipher(algorithms.AES(session_key), modes.GCM(iv, encryptor.tag), backend = default_backend()).decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize()
    print(f"Расшифровано: {decrypted}\n")


# ===============================
# 4. Асимметричное шифрование (RSA)
# ===============================
def asymmetric_key_demo():
    print("\n=== 4. Асимметричное шифрование (RSA) ===")
    print("Генерация RSA ключей (1024 бита для демонстрации, реально ≥2048)...")
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 1024,
        backend = default_backend()
    )
    public_key = private_key.public_key()
    
    message = b"Open message for encryption with public key"
    print(f"Сообщение: {message}")
    
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(mgf = padding.MGF1(algorithm = hashes.SHA256()), algorithm = hashes.SHA256(), label = None)
    )
    print(f"Зашифровано открытым ключом: {ciphertext.hex()[:32]}...")
    
    decrypted = private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf = padding.MGF1(algorithm = hashes.SHA256()), algorithm = hashes.SHA256(), label = None)
    )
    print(f"Расшифровано закрытым ключом: {decrypted}\n")


# ===============================
# 5. Управление ключами
# ===============================
class KeyManager:
    def __init__(self):
        self.keys = {}
    
    def generate_key(self, name, key_size = 32):
        key = os.urandom(key_size)
        self.keys[name] = {
            "key": key,
            "type": "symmetric",
            "created": time.time()
        }
        print(f"✓ Ключ '{name}' сгенерирован (размер {key_size * 8} бит).")
        return key
    
    def rotate_key(self, name):
        if name in self.keys:
            old_created = self.keys[name]["created"]
            new_key = os.urandom(len(self.keys[name]["key"]))
            self.keys[name]["key"] = new_key
            self.keys[name]["created"] = time.time()
            print(f"⟳ Ключ '{name}' заменён. Предыдущий создан: {time.ctime(old_created)}")
        else:
            print(f"✗ Ключ '{name}' не найден.")
    
    def destroy_key(self, name):
        if name in self.keys:
            self.keys[name]["key"] = b'\x00' * len(self.keys[name]["key"])
            del self.keys[name]
            print(f"✗ Ключ '{name}' уничтожен (затёрт нулями).")
        else:
            print(f"✗ Ключ '{name}' не найден.")
    
    def list_keys(self):
        if not self.keys:
            print("  (нет активных ключей)")
        for name, info in self.keys.items():
            print(f"  - {name}: {info['type']}, создан {time.ctime(info['created'])}")


def key_management_demo():
    print("\n=== 5. Управление ключами (жизненный цикл) ===")
    km = KeyManager()
    
    print("\n[Генерация]")
    km.generate_key("master_key", 32)
    km.generate_key("session_20260613", 16)
    
    print("\n[Хранение] — ключи в оперативной памяти (в защищённом хранилище)")
    km.list_keys()
    
    print("\n[Замена]")
    km.rotate_key("session_20260613")
    
    print("\n[Уничтожение]")
    km.destroy_key("session_20260613")
    km.list_keys()
    print()


# ===============================
# 6. Типы ключей
# ===============================
def key_types_demo():
    print("\n=== 6. Типы ключей ===")
    master_key = os.urandom(32)
    print(f"🔐 Мастер-ключ (сервера): {master_key.hex()[:16]}... (хранится долго)")
    
    session_key = os.urandom(16)
    print(f"🔑 Сессионный ключ: {session_key.hex()[:16]}... (живёт одну сессию)")
    
    file_key = os.urandom(32)
    print(f"📁 Ключ шифрования файла: {file_key.hex()[:16]}...")
    
    # Имитация защиты сессионного ключа мастер-ключом
    encrypted_session = bytes(a ^ b for a, b in zip(session_key, master_key[:len(session_key)]))
    print(f"🔒 Сессионный ключ, зашифрованный мастер-ключом (XOR): {encrypted_session.hex()[:16]}...")
    print("(В реальности используется асимметричное шифрование или KDF)\n")


# ===============================
# Главная функция
# ===============================
def main():
    print("=" * 70)
    print(" ДЕМОНСТРАЦИЯ КРИПТОГРАФИЧЕСКИХ ПОНЯТИЙ")
    print(" (Керкгоффс, управление ключами, стойкость перебору)")
    print("=" * 70)
    
    kerckhoffs_demo()
    brute_force_estimate()
    symmetric_key_demo()
    asymmetric_key_demo()
    key_management_demo()
    key_types_demo()
    
    print("=" * 70)
    print("Примечания:")
    print("• Режим GCM заменён вместо CFB (нет предупреждений)")
    print("• Реальные ключи: симметричные ≥128 бит, RSA ≥2048 бит")
    print("• В тексте указано: 80 бит (симметричные), 768 бит (асимметричные)")
    print("=" * 70)


if __name__ == "__main__":
    main()