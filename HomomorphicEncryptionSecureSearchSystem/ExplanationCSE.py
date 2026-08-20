# Объяснение CSE
"""
CSE (Client-Side Encryption with Search) Demo
Без использования NumPy.
Реализует:
- Шифрование данных на клиенте перед отправкой на сервер.
- Построение зашифрованного поискового индекса.
- Слепой поиск (сервер не видит открытые данные).
- Расшифровка только на клиенте.
"""

import os
import json
import hashlib
import base64
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Используем библиотеку cryptography для надёжного шифрования
# pip install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# ===================== КЛИЕНТСКАЯ ЧАСТЬ =====================

class Client:
    """
    Клиент, который владеет ключами шифрования.
    Шифрует данные, строит индекс, расшифровывает результаты.
    """
    def __init__(self, master_password: str):
        # Соль для генерации ключей (можно хранить на клиенте)
        self.salt = b'cse_salt_2026'
        self.master_password = master_password.encode('utf-8')
        
        # Генерируем два ключа из мастер-пароля:
        # 1) Ключ для шифрования данных (AES-256)
        # 2) Ключ для построения поискового индекса (HMAC)
        self.data_key = self._derive_key(b'data_key')
        self.index_key = self._derive_key(b'index_key')
    
    def _derive_key(self, purpose: bytes) -> bytes:
        """Получение ключа из мастер-пароля с использованием PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,  # 256 бит для AES
            salt = self.salt + purpose,
            iterations = 100000,
            backend = default_backend()
        )
        return kdf.derive(self.master_password)
    
    def _pad(self, data: bytes) -> bytes:
        """Дополнение для AES (PKCS7)."""
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)
    
    def _unpad(self, data: bytes) -> bytes:
        """Удаление дополнения."""
        pad_len = data[-1]
        return data[:-pad_len]
    
    def encrypt_data(self, plaintext: str) -> Dict[str, str]:
        """
        Шифрует текстовые данные на клиенте.
        Возвращает словарь: {'ciphertext': base64, 'iv': base64}
        """
        iv = os.urandom(16)  # случайный вектор инициализации
        cipher = Cipher(algorithms.AES(self.data_key), modes.CBC(iv), backend = default_backend())
        encryptor = cipher.encryptor()
        padded = self._pad(plaintext.encode('utf-8'))
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8')
        }
    
    def decrypt_data(self, encrypted: Dict[str, str]) -> str:
        """Расшифровывает данные на клиенте."""
        ciphertext = base64.b64decode(encrypted['ciphertext'])
        iv = base64.b64decode(encrypted['iv'])
        cipher = Cipher(algorithms.AES(self.data_key), modes.CBC(iv), backend = default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = self._unpad(padded)
        return plaintext.decode('utf-8')
    
    def build_search_index(self, keywords: List[str]) -> List[str]:
        """
        Строит зашифрованный индекс для ключевых слов.
        Использует HMAC-SHA256 (детерминированное шифрование).
        """
        index = []
        for kw in keywords:
            # Нормализуем слово
            normalized = kw.strip().lower()
            # Используем HMAC с индексным ключом
            h = hashlib.pbkdf2_hmac('sha256', normalized.encode('utf-8'), self.index_key, 10000)
            index.append(base64.b64encode(h).decode('utf-8'))
        return index
    
    def encrypt_search_query(self, keyword: str) -> str:
        """Шифрует поисковый запрос (так же, как и индекс)."""
        normalized = keyword.strip().lower()
        h = hashlib.pbkdf2_hmac('sha256', normalized.encode('utf-8'), self.index_key, 10000)
        return base64.b64encode(h).decode('utf-8')


# ===================== СЕРВЕРНАЯ ЧАСТЬ =====================

@dataclass
class StoredRecord:
    """
    Запись, хранящаяся на сервере.
    Содержит зашифрованные данные и зашифрованный индекс.
    """
    record_id: int
    encrypted_data: Dict[str, str]  # {'ciphertext': ..., 'iv': ...}
    encrypted_index: List[str]      # список зашифрованных ключевых слов
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Server:
    """
    Удалённый сервер, который хранит только зашифрованные данные и индексы.
    Не имеет ключей, не может расшифровать данные.
    """
    def __init__(self):
        self.storage: Dict[int, StoredRecord] = {}
        self.next_id = 1
    
    def store_record(self, encrypted_data: Dict[str, str], encrypted_index: List[str]) -> int:
        """Сохраняет зашифрованную запись на сервере."""
        record = StoredRecord(
            record_id = self.next_id,
            encrypted_data = encrypted_data,
            encrypted_index = encrypted_index
        )
        self.storage[self.next_id] = record
        self.next_id += 1
        return record.record_id
    
    def search(self, encrypted_query: str) -> List[int]:
        """
        Слепой поиск: сервер ищет совпадение индекса с запросом.
        Не видит открытых данных.
        Возвращает список ID записей, подходящих под запрос.
        """
        results = []
        for rec_id, record in self.storage.items():
            if encrypted_query in record.encrypted_index:
                results.append(rec_id)
        return results
    
    def get_encrypted_record(self, record_id: int) -> Optional[Dict[str, str]]:
        """Возвращает зашифрованные данные по ID."""
        if record_id in self.storage:
            return self.storage[record_id].encrypted_data
        return None


# ===================== ДЕМОНСТРАЦИЯ РАБОТЫ =====================

def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ CSE (Client-Side Encryption with Search)")
    print("=" * 60)
    
    # 1. Инициализация клиента (пользователь вводит мастер-пароль)
    master_pw = "my_secure_password_123"
    client = Client(master_pw)
    print(f"[Клиент] Инициализирован с мастер-паролем (скрыто).")
    print(f"[Клиент] Ключи сгенерированы на клиенте и не передаются на сервер.\n")
    
    # 2. Создание данных на клиенте
    print("--- Шаг 1: Клиент создаёт и шифрует записи ---")
    
    records_data = [
        ("Иванов Иван", "Диагноз: гипертония, лечение: амлодипин"),
        ("Петрова Мария", "Диагноз: сахарный диабет 2 типа, лечение: метформин"),
        ("Сидоров Алексей", "Диагноз: бронхиальная астма, лечение: сальбутамол"),
    ]
    
    # Сервер пока пуст
    server = Server()
    
    # Клиент шифрует каждую запись и отправляет на сервер
    for i, (patient, diagnosis) in enumerate(records_data, 1):
        # Формируем текст для шифрования
        plaintext = f"Пациент: {patient}\nДиагноз: {diagnosis}"
        
        # Шифруем данные
        encrypted_data = client.encrypt_data(plaintext)
        
        # Строим индекс по ключевым словам (из диагноза)
        keywords = diagnosis.lower().split()  # простой разбор
        encrypted_index = client.build_search_index(keywords)
        
        # Отправляем на сервер
        record_id = server.store_record(encrypted_data, encrypted_index)
        print(f"  Запись #{record_id} зашифрована и отправлена на сервер.")
    
    print("\n[Сервер] Все записи сохранены в зашифрованном виде.")
    print(f"[Сервер] Всего записей: {len(server.storage)}\n")
    
    # 3. Поиск на сервере (слепой поиск)
    print("--- Шаг 2: Выполнение слепого поиска ---")
    
    search_queries = ["гипертония", "диабет", "астма", "грипп"]
    
    for query in search_queries:
        # Клиент шифрует запрос
        encrypted_query = client.encrypt_search_query(query)
        
        # Сервер выполняет поиск (не видя открытого запроса)
        result_ids = server.search(encrypted_query)
        
        print(f"\nПоиск по ключевому слову '{query}':")
        print(f"  Зашифрованный запрос: {encrypted_query[:20]}...")
        print(f"  Найдено записей: {len(result_ids)}")
        
        # Клиент получает зашифрованные данные и расшифровывает их
        for rid in result_ids:
            enc_data = server.get_encrypted_record(rid)
            if enc_data:
                decrypted = client.decrypt_data(enc_data)
                print(f"    ID {rid}: {decrypted.split(chr(10))[0]}")  # показываем первую строку
    
    # 4. Демонстрация безопасности
    print("\n--- Шаг 3: Проверка безопасности ---")
    print("[Сервер] Содержимое хранилища (зашифровано):")
    for rid, record in server.storage.items():
        print(f"  ID {rid}: данные = {record.encrypted_data['ciphertext'][:30]}...")
        print(f"         индексы = {[idx[:15]+'...' for idx in record.encrypted_index[:3]]}")
    
    print("\n[Клиент] Расшифрованная последняя запись:")
    last_id = len(server.storage)
    last_enc = server.get_encrypted_record(last_id)
    if last_enc:
        decrypted = client.decrypt_data(last_enc)
        print(decrypted)
    
    print("\n" + "=" * 60)
    print("Вывод: Сервер не видит открытые данные, но может выполнять поиск.")
    print("Ключи никогда не покидают клиент. Расшифровка только на клиенте.")
    print("=" * 60)


if __name__ == "__main__":
    main()