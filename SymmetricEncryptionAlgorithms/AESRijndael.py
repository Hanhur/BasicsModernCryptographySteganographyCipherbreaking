# AES Rijndael
"""
AES Rijndael - Полная демонстрация
Основано на тексте: NIST, режимы работы (ECB, CBC, CFB, OFB, CTR, GCM),
поддержка ключей 128 / 192 / 256 бит и практические аспекты (IV, Nonce).
Без использования NumPy.
"""

import os
import hashlib
import warnings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Подавляем предупреждения о депрекации OFB и CFB
warnings.filterwarnings("ignore", category = DeprecationWarning)
warnings.filterwarnings("ignore", category = UserWarning)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def generate_key(key_size_bits: int) -> bytes:
    """
    Генерирует случайный ключ указанного размера.
    Поддерживает: 128, 192, 256 бит (соответствует AES-128, AES-192, AES-256).
    """
    if key_size_bits not in [128, 192, 256]:
        raise ValueError("Размер ключа должен быть 128, 192 или 256 бит")
    return os.urandom(key_size_bits // 8)

def derive_key_from_password(password: str, key_size_bits: int, salt: bytes = None) -> tuple:
    """
    Создаёт ключ из пароля с использованием PBKDF2 (защита от словарных атак).
    Возвращает (ключ, соль).
    """
    if salt is None:
        salt = os.urandom(16)
    # 100 000 итераций - современный стандарт (рекомендовано OWASP)
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000, 
        dklen=key_size_bits // 8
    )
    return key, salt

def pad_data(data: bytes) -> bytes:
    """Дополняет данные до размера, кратного 16 байтам (AES block size)."""
    padder = padding.PKCS7(128).padder()
    return padder.update(data) + padder.finalize()

def unpad_data(padded_data: bytes) -> bytes:
    """Удаляет дополнение после расшифровки."""
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

# ==================== ФУНКЦИИ ШИФРОВАНИЯ ====================

def encrypt_aes_ecb(key: bytes, plaintext: bytes) -> bytes:
    """
    Режим ECB - САМЫЙ ПРОСТОЙ, НО НЕБЕЗОПАСНЫЙ ДЛЯ ПОВТОРЯЮЩИХСЯ ДАННЫХ.
    Продемонстрирован для полноты (упоминается в тексте).
    """
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = default_backend())
    encryptor = cipher.encryptor()
    padded_data = pad_data(plaintext)
    return encryptor.update(padded_data) + encryptor.finalize()

def decrypt_aes_ecb(key: bytes, ciphertext: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend = default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return unpad_data(padded_data)

def encrypt_aes_cbc(key: bytes, plaintext: bytes, iv: bytes = None) -> tuple:
    """
    Режим CBC (Cipher Block Chaining) - сцепление блоков.
    Требует случайный IV (Initialization Vector).
    """
    if iv is None:
        iv = os.urandom(16)  # 16 байт = размер блока AES
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    padded_data = pad_data(plaintext)
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext, iv

def decrypt_aes_cbc(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return unpad_data(padded_data)

def encrypt_aes_ctr(key: bytes, plaintext: bytes, nonce: bytes = None) -> tuple:
    """
    Режим CTR (Counter) - современный, безопасный, параллелизуемый.
    Не требует дополнения (padding)!
    """
    if nonce is None:
        nonce = os.urandom(16)  # 16 байт для счетчика
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, nonce

def decrypt_aes_ctr(key: bytes, ciphertext: bytes, nonce: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_aes_ofb(key: bytes, plaintext: bytes, iv: bytes = None) -> tuple:
    """
    Режим OFB (Output Feedback) - превращает блочный шифр в потоковый.
    Не требует дополнения.
    """
    if iv is None:
        iv = os.urandom(16)
    # Используем стандартный Cipher с modes.OFB (будет предупреждение, но работает)
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, iv

def decrypt_aes_ofb(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_aes_cfb(key: bytes, plaintext: bytes, iv: bytes = None) -> tuple:
    """
    Режим CFB (Cipher Feedback) - тоже потоковый, но с обратной связью.
    """
    if iv is None:
        iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, iv

def decrypt_aes_cfb(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_aes_gcm(key: bytes, plaintext: bytes, nonce: bytes = None) -> tuple:
    """
    Режим GCM (Galois/Counter Mode) - РЕКОМЕНДУЕТСЯ ДЛЯ ПЕРЕДАЧИ ПО СЕТИ!
    Обеспечивает шифрование + аутентификацию (защита от подмены).
    """
    if nonce is None:
        nonce = os.urandom(12)  # 12 байт рекомендуется для GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, nonce, encryptor.tag

def decrypt_aes_gcm(key: bytes, ciphertext: bytes, nonce: bytes, tag: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend = default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# ==================== ДЕМОНСТРАЦИЯ ====================

def demo():
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ AES (Rijndael) - Все режимы и размеры ключей")
    print("=" * 70)
    
    # Исходное сообщение (из текста про виртуальные машины и CSE)
    plaintext_str = "Передача данных между виртуальными машинами в системе CSE"
    plaintext = plaintext_str.encode('utf-8')
    
    print(f"\nИсходные данные: {plaintext_str}")
    print(f"Длина: {len(plaintext)} байт (в UTF-8)")
    
    # ---- 1. Тестируем разные размеры ключей ----
    for key_size in [128, 192, 256]:
        print(f"\n--- AES-{key_size} (ключ {key_size} бит) ---")
        key = generate_key(key_size)
        print(f"Ключ (hex): {key.hex()[:16]}... (первые 16 байт)")
        
        # ---- 2. Тестируем все режимы ----
        
        # ECB (только для демонстрации, не использовать в продакшене!)
        ecb_ct = encrypt_aes_ecb(key, plaintext)
        ecb_pt = decrypt_aes_ecb(key, ecb_ct)
        print(f"  ECB: {ecb_ct.hex()[:32]}... -> {ecb_pt.decode('utf-8')[:20]}...")
        
        # CBC
        cbc_ct, iv_cbc = encrypt_aes_cbc(key, plaintext)
        cbc_pt = decrypt_aes_cbc(key, cbc_ct, iv_cbc)
        print(f"  CBC: {cbc_ct.hex()[:32]}... (IV = {iv_cbc.hex()[:8]}...) -> {cbc_pt.decode('utf-8')[:20]}...")
        
        # CTR (самый современный)
        ctr_ct, nonce = encrypt_aes_ctr(key, plaintext)
        ctr_pt = decrypt_aes_ctr(key, ctr_ct, nonce)
        print(f"  CTR: {ctr_ct.hex()[:32]}... (Nonce = {nonce.hex()[:8]}...) -> {ctr_pt.decode('utf-8')[:20]}...")
        
        # GCM (рекомендуемый для сетей)
        gcm_ct, gcm_nonce, gcm_tag = encrypt_aes_gcm(key, plaintext)
        gcm_pt = decrypt_aes_gcm(key, gcm_ct, gcm_nonce, gcm_tag)
        print(f"  GCM: {gcm_ct.hex()[:32]}... (Nonce = {gcm_nonce.hex()[:8]}..., Tag = {gcm_tag.hex()[:8]}...) -> {gcm_pt.decode('utf-8')[:20]}...")
        
        # OFB
        ofb_ct, iv_ofb = encrypt_aes_ofb(key, plaintext)
        ofb_pt = decrypt_aes_ofb(key, ofb_ct, iv_ofb)
        print(f"  OFB: {ofb_ct.hex()[:32]}... -> {ofb_pt.decode('utf-8')[:20]}...")
        
        # CFB
        cfb_ct, iv_cfb = encrypt_aes_cfb(key, plaintext)
        cfb_pt = decrypt_aes_cfb(key, cfb_ct, iv_cfb)
        print(f"  CFB: {cfb_ct.hex()[:32]}... -> {cfb_pt.decode('utf-8')[:20]}...")
    
    # ---- 3. Демонстрация управления ключами из пароля (как в реальных системах) ----
    print("\n" + "=" * 70)
    print("УПРАВЛЕНИЕ КЛЮЧАМИ: Генерация ключа из пароля (PBKDF2)")
    print("=" * 70)
    
    password = "MySuperSecurePassword_ForCSE_2026"
    salt = os.urandom(16)
    key_from_pass, _ = derive_key_from_password(password, 256, salt)
    print(f"Пароль: {password}")
    print(f"Соль: {salt.hex()}")
    print(f"Ключ (256 бит): {key_from_pass.hex()}")
    
    # Шифруем с использованием ключа из пароля (используем GCM для защиты)
    ct_pass, iv_pass, tag_pass = encrypt_aes_gcm(key_from_pass, plaintext)
    pt_pass = decrypt_aes_gcm(key_from_pass, ct_pass, iv_pass, tag_pass)
    print(f"Расшифровано: {pt_pass.decode('utf-8')}")
    
    # ---- 4. Демонстрация защиты от подмены (аутентификация в GCM) ----
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ ПОДМЕНЫ (GCM аутентификация)")
    print("=" * 70)
    
    msg_str = "Важный платёж на сумму 1000$"
    msg = msg_str.encode('utf-8')
    key_auth = generate_key(128)
    ct_auth, nonce_auth, tag_auth = encrypt_aes_gcm(key_auth, msg)
    
    print(f"Сообщение: {msg_str}")
    print(f"Шифротекст: {ct_auth.hex()[:32]}...")
    print(f"Тег аутентификации: {tag_auth.hex()}")
    
    # Пытаемся подменить данные (злоумышленник меняет один байт)
    corrupted_ct = bytearray(ct_auth)
    corrupted_ct[0] ^= 0x01  # Меняем первый байт
    
    try:
        decrypt_aes_gcm(key_auth, bytes(corrupted_ct), nonce_auth, tag_auth)
        print("ОШИБКА: Данные были подменены, но расшифровка прошла! (так быть не должно)")
    except Exception as e:
        print(f"✅ Защита сработала! Подмена обнаружена: {e}")
    
    # ---- 5. Важное предупреждение о безопасности (как в тексте) ----
    print("\n" + "=" * 70)
    print("ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ (как в вашем тексте)")
    print("=" * 70)
    print("1. Никогда не используйте ECB для данных с паттернами (рисунки, текст)!")
    print("2. Всегда используйте случайный IV/Nonce для CBC / CTR / OFB / CFB / GCM.")
    print("3. Для передачи между VM ОБЯЗАТЕЛЬНО используйте GCM (шифрование + аутентификация).")
    print("4. Ключи должны храниться в защищенном месте (HSM / TPM), а не в коде.")
    print("5. PBKDF2 с 100000 итераций защищает от перебора паролей.")
    print("6. В GCM НИКОГДА не используйте один nonce дважды с одним ключом!")
    
    # ---- 6. Дополнительно: демонстрация уязвимости ECB ----
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ УЯЗВИМОСТИ ECB (из текста про паттерны)")
    print("=" * 70)
    
    # Создаём данные с повторяющимся паттерном (например, 16 нулевых байт)
    pattern_data = b"\x00" * 64  # 64 нулевых байта = 4 блока
    key_fixed = generate_key(128)
    
    ecb_pattern_ct = encrypt_aes_ecb(key_fixed, pattern_data)
    cbc_pattern_ct, iv_cbc_pat = encrypt_aes_cbc(key_fixed, pattern_data)
    
    print(f"Данные с паттерном: {pattern_data.hex()}")
    print(f"ECB шифротекст (видно повторение блоков): {ecb_pattern_ct.hex()}")
    print(f"CBC шифротекст (блоки разные, паттерн скрыт): {cbc_pattern_ct.hex()[:64]}...")
    print("В ECB одинаковые блоки -> одинаковый шифротекст! Это позволяет анализировать данные.")

if __name__ == "__main__":
    # Проверка наличия библиотеки cryptography
    try:
        import cryptography
    except ImportError:
        print("ОШИБКА: Установите библиотеку cryptography:")
        print("  pip install cryptography")
        exit(1)
    
    demo()