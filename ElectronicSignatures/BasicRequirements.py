# 1. Основные требования
import hashlib
import rsa
import os

def generate_keys():
    """Генерация пары ключей (уникальность)"""
    (pub_key, priv_key) = rsa.newkeys(2048)
    return pub_key, priv_key

def sign_document(document_path, priv_key):
    """Подпись документа: обеспечивает неотделимость от документа и целостность"""
    with open(document_path, "rb") as f:  # Читаем в бинарном режиме - проблем с кодировкой нет
        document_data = f.read()

    # Хэш документа (защита целостности + неотделимость)
    doc_hash = hashlib.sha256(document_data).digest()

    # Создание подписи
    signature = rsa.sign(doc_hash, priv_key, 'SHA-256')
    return signature

def verify_signature(document_path, signature, pub_key):
    """Проверка подписи (проверяемость + неотклонимость)"""
    with open(document_path, "rb") as f:  # Читаем в бинарном режиме
        document_data = f.read()

    doc_hash = hashlib.sha256(document_data).digest()

    try:
        rsa.verify(doc_hash, signature, pub_key)
        return True
    except rsa.VerificationError:
        return False

# Пример использования
if __name__ == "__main__":
    # 1. Уникальность: каждый получает свою пару ключей
    pub_key, priv_key = generate_keys()

    # Создаём тестовый документ (явно указываем UTF-8)
    with open("document.txt", "w", encoding = "utf-8") as f:
        f.write("Важный контракт")

    # 2. Подписываем документ (защита целостности + неотделимость)
    signature = sign_document("document.txt", priv_key)

    # Сохраняем подпись в файл
    with open("document.txt.sig", "wb") as f:
        f.write(signature)

    # 3. Проверяем подпись (проверяемость)
    is_valid = verify_signature("document.txt", signature, pub_key)
    print(f"Подпись верна: {is_valid}")

    # 4. Показываем неотделимость: изменяем документ на 1 байт
    with open("document.txt", "a", encoding = "utf-8") as f:
        f.write(".")  # Изменение

    is_valid_after_modify = verify_signature("document.txt", signature, pub_key)
    print(f"После изменения документа: {is_valid_after_modify}")

    # 5. Попытка перенести подпись на другой документ
    with open("document2.txt", "w", encoding = "utf-8") as f:
        f.write("Другой документ")

    is_valid_other = verify_signature("document2.txt", signature, pub_key)
    print(f"С другим документом: {is_valid_other}")