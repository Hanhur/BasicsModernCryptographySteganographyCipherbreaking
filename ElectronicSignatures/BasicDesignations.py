# 2. Основные обозначения
import hashlib
import pickle
import math
import random
from typing import Dict, Any
from dataclasses import dataclass

# ============================================================
# 1. Пространства
# ============================================================
# M            - пространство документов (любые байты)
# M_s          - пространство дайджестов (32-байтовые строки)
# S            - пространство подписей (словари/кортежи)

# ============================================================
# 2. Функция R: M -> M_s (инъективная)
# ============================================================
def R(document: bytes) -> bytes:
    """
    Инъективная функция, сопоставляющая документу его дайджест.
    Возвращает сериализованный объект (длина + документ).
    Это инъективно, но не сжимает.
    """
    data = pickle.dumps(("R_digest", len(document), document))
    return data


def R_inverse(digest: bytes) -> bytes:
    """
    Обратная функция R^{-1} : Im R -> M
    """
    try:
        marker, length, doc = pickle.loads(digest)
        if marker == "R_digest" and len(doc) == length:
            return doc
        else:
            raise ValueError("Invalid digest format")
    except Exception:
        raise ValueError("Cannot invert R: digest not in Im R")


# ============================================================
# 3. Односторонняя функция h: M -> M_s (хэш-функция)
# ============================================================
def h(document: bytes) -> bytes:
    """
    Криптографическая хэш-функция SHA-256.
    Свойства:
    - Легко вычислить
    - Необратима
    - Стойка к коллизиям
    """
    return hashlib.sha256(document).digest()


# ============================================================
# 4. Система электронной подписи (RSA-подобная для демонстрации)
# ============================================================
@dataclass
class KeyPair:
    private_key: Dict[str, Any]
    public_key: Dict[str, Any]


def generate_keys() -> KeyPair:
    """
    Генерирует пару ключей для подписи.
    """
    # Маленькие простые числа для демонстрации (небезопасно!)
    primes = [61, 53, 47, 43, 41, 37, 31, 29, 23, 19, 17, 13]
    p = random.choice(primes)
    q = random.choice(primes)
    while q == p:
        q = random.choice(primes)

    n = p * q
    phi = (p - 1) * (q - 1)

    # e = 65537 (стандарт)
    e = 65537
    # d = e ^ {-1} mod phi
    d = pow(e, -1, phi)

    return KeyPair(
        private_key = {"d": d, "n": n},
        public_key = {"e": e, "n": n}
    )


def sign(private_key: Dict[str, Any], digest: bytes) -> bytes:
    """
    Подпись дайджеста: σ = (digest) ^ d mod n
    digest преобразуется в число.
    """
    d = private_key["d"]
    n = private_key["n"]

    # Преобразуем digest в целое число
    m_int = int.from_bytes(digest, "big") % n

    # Подпись
    sig_int = pow(m_int, d, n)

    # Возвращаем подпись как байты
    return sig_int.to_bytes((n.bit_length() + 7) // 8, "big")


def verify(public_key: Dict[str, Any], digest: bytes, signature: bytes) -> bool:
    """
    Проверка подписи: вычисляется digest' = signature^e mod n,
    сравнивается с исходным digest.
    """
    e = public_key["e"]
    n = public_key["n"]

    sig_int = int.from_bytes(signature, "big")
    decrypted_int = pow(sig_int, e, n)

    # Дополняем до нужной длины
    expected_digest = decrypted_int.to_bytes((n.bit_length() + 7) // 8, "big")
    # Обрезаем до длины digest (хэш 32 байта)
    expected_digest = expected_digest[-len(digest):]

    return expected_digest == digest


# ============================================================
# 5. Полный процесс подписи документа (по вашей модели)
# ============================================================
def sign_document(keypair: KeyPair, document: bytes) -> bytes:
    """
    Подпись документа:
    - Вычисляем R(m) (инъективный дайджест)
    - Вычисляем h(R(m)) (односторонняя хэш-функция)
    - Подписываем результат: Sign(sk, h(R(m)))
    """
    # Шаг 1: R(m)
    r_digest = R(document)            # ∈ M_s

    # Шаг 2: h(R(m))
    hash_of_r = h(r_digest)           # ∈ M_s (фиксированной длины)

    # Шаг 3: подпись
    signature = sign(keypair.private_key, hash_of_r)

    return signature


def verify_document(keypair: KeyPair, document: bytes, signature: bytes) -> bool:
    """
    Проверка подписи документа:
    - Вычисляем R(m) из документа
    - Вычисляем h(R(m))
    - Проверяем подпись от этого значения
    """
    r_digest = R(document)
    hash_of_r = h(r_digest)

    return verify(keypair.public_key, hash_of_r, signature)


# ============================================================
# 6. Вспомогательная функция для кодирования строк с русскими буквами
# ============================================================
def encode_text(text: str) -> bytes:
    """Преобразует строку (в т.ч. с русскими буквами) в байты UTF-8"""
    return text.encode('utf-8')


def decode_bytes(data: bytes) -> str:
    """Преобразует байты обратно в строку UTF-8"""
    return data.decode('utf-8')


# ============================================================
# 7. Демонстрация работы
# ============================================================
if __name__ == "__main__":
    print("=== Демонстрация системы электронной подписи ===\n")

    # 1. Генерация ключей
    keys = generate_keys()
    print("Keys generated successfully.")

    # 2. Исходный документ (теперь с правильной кодировкой)
    original_text = "Important document: contract for 1000$"
    original_doc = original_text.encode('utf-8')
    print(f"Document: {original_text}")

    # 3. Подпись документа
    sig = sign_document(keys, original_doc)
    print(f"Signature (first 32 bytes): {sig[:32].hex()}...")

    # 4. Проверка подписи
    is_valid = verify_document(keys, original_doc, sig)
    print(f"Verification result: {'✅ Signature valid' if is_valid else '❌ Signature invalid'}")

    # 5. Попытка подделки: изменяем документ
    tampered_text = "Important document: contract for 9999$"
    tampered_doc = tampered_text.encode('utf-8')
    is_valid_tampered = verify_document(keys, tampered_doc, sig)
    print(f"Verification of tampered document: {'✅ Signature valid' if is_valid_tampered else '❌ Signature invalid'}")

    # 6. Дополнительно: демонстрация с русским текстом
    print("\n=== Testing with Russian text (UTF-8) ===")
    russian_text = "Важный документ: контракт на сумму 1000$"
    russian_doc = russian_text.encode('utf-8')
    print(f"Russian document: {russian_text}")

    sig_russian = sign_document(keys, russian_doc)
    is_valid_russian = verify_document(keys, russian_doc, sig_russian)
    print(f"Russian signature valid: {is_valid_russian}")

    # 7. Демонстрация свойств R и R ^ {-1}
    print("\n=== Testing R and R ^ {-1} properties ===")
    doc1 = b"Hello"
    doc2 = b"World"
    r1 = R(doc1)
    r2 = R(doc2)
    print(f"R(doc1) != R(doc2): {r1 != r2}")

    recovered_doc1 = R_inverse(r1)
    print(f"Recovered doc1: {recovered_doc1} (matches? {recovered_doc1 == doc1})")

    # 8. Демонстрация односторонности h
    print("\n=== Testing one-way property of h ===")
    hash_val = h(b"secret")
    print(f"Hash of 'secret': {hash_val.hex()}")
    print("(Reverse computation is impossible by SHA-256 definition)")

    print("\nDone.")