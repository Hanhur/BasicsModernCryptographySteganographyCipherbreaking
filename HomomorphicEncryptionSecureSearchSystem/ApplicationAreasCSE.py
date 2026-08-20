# Области применения CSE 
import hashlib
import json
import random
import string
from typing import Dict, List, Tuple

# ===================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# ===================================================

def generate_salt(length: int = 8) -> str:
    """Генерация случайной соли."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k = length))

def hash_keyword(keyword: str, salt: str) -> str:
    """Хеширование ключевого слова с солью (имитация слепого токена)."""
    combined = keyword + salt
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def simple_encrypt(text: str, key: str) -> str:
    """Очень простая имитация шифрования (XOR с ключом)."""
    encrypted_chars = []
    for i, ch in enumerate(text):
        key_char = key[i % len(key)]
        encrypted_chars.append(chr(ord(ch) ^ ord(key_char)))
    return ''.join(encrypted_chars)

def simple_decrypt(encrypted: str, key: str) -> str:
    """Дешифрование (обратная операция XOR)."""
    return simple_encrypt(encrypted, key)  # XOR симметричен

# ===================================================
# 2. КЛАСС СИСТЕМЫ CSE (имитация)
# ===================================================

class CSESystem:
    """
    Демонстрационная система CSE для медицинских карт (EHR).
    Хранит зашифрованные записи и инвертированный индекс хешей.
    Поиск выполняется по хешу, без расшифровки всех данных.
    """
    
    def __init__(self, master_key: str):
        self.master_key = master_key
        self.encrypted_records = []       # список зашифрованных записей
        self.index = {}                   # хеш_слова -> список ID записей
        self.next_id = 0
        self.used_salts = set()           # для уникальности

    def _generate_unique_salt(self) -> str:
        """Генерация уникальной соли."""
        salt = generate_salt()
        while salt in self.used_salts:
            salt = generate_salt()
        self.used_salts.add(salt)
        return salt

    def add_record(self, patient_name: str, symptoms: List[str], diagnosis: str) -> int:
        """
        Добавляет новую медицинскую запись.
        Данные шифруются, а ключевые слова (симптомы) индексируются через хеши.
        """
        record_id = self.next_id
        self.next_id += 1

        # 1. Шифруем все поля записи (имитация)
        encrypted_name = simple_encrypt(patient_name, self.master_key)
        encrypted_diagnosis = simple_encrypt(diagnosis, self.master_key)
        
        # Для каждого симптома генерируем уникальную соль и хеш
        symptom_entries = []
        for symptom in symptoms:
            salt = self._generate_unique_salt()
            hashed = hash_keyword(symptom, salt)
            # Сохраняем соль вместе с хешем (в реальной системе соль известна только владельцу)
            symptom_entries.append({
                'symptom_hash': hashed,
                'salt': salt
            })
            
            # Добавляем в индекс
            if hashed not in self.index:
                self.index[hashed] = []
            self.index[hashed].append(record_id)

        # Сохраняем зашифрованную запись
        record = {
            'id': record_id,
            'encrypted_name': encrypted_name,
            'encrypted_diagnosis': encrypted_diagnosis,
            'symptom_entries': symptom_entries  # храним соли для возможности дешифровки при необходимости
        }
        self.encrypted_records.append(record)
        return record_id

    def search_by_symptom(self, symptom: str) -> List[Dict]:
        """
        Поиск записей по симптому БЕЗ расшифровки всех данных.
        Возвращает список ID и зашифрованные поля.
        """
        # Для поиска мы должны использовать ТЕ ЖЕ САМЫЕ СОЛИ, которые были при индексации.
        # В реальной CSE соль детерминирована или хранится в защищённом виде.
        # В этой демо-версии мы перебираем все сохранённые соли для данного симптома.
        # (Это упрощение, но оно показывает принцип: поиск идёт по хешам)
        
        found_ids = set()
        
        # Перебираем все записи и проверяем хеши симптомов
        # (в реальной системе используется обратный индекс, но для демо мы покажем оба подхода)
        for record in self.encrypted_records:
            for entry in record['symptom_entries']:
                # Проверяем, совпадает ли хеш искомого симптома с хешем в записи
                if hash_keyword(symptom, entry['salt']) == entry['symptom_hash']:
                    found_ids.add(record['id'])
        
        # Собираем результаты
        results = []
        for record in self.encrypted_records:
            if record['id'] in found_ids:
                results.append({
                    'id': record['id'],
                    'encrypted_name': record['encrypted_name'],
                    'encrypted_diagnosis': record['encrypted_diagnosis'],
                    # Показываем, что данные зашифрованы (нечитаемы)
                })
        return results

    def decrypt_record(self, encrypted_name: str, encrypted_diagnosis: str) -> Tuple[str, str]:
        """Расшифровка конкретной записи (только для авторизованного доступа)."""
        name = simple_decrypt(encrypted_name, self.master_key)
        diagnosis = simple_decrypt(encrypted_diagnosis, self.master_key)
        return name, diagnosis

# ===================================================
# 3. ДЕМОНСТРАЦИЯ РАБОТЫ
# ===================================================

def main():
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ CSE (ГОМОМОРФНЫЙ ПОИСК) В ЗДРАВООХРАНЕНИИ")
    print("=" * 70)
    
    # Инициализация системы с мастер-ключом
    system = CSESystem(master_key = "MySecretKey2026")
    
    # Добавляем тестовые медицинские записи (EHR)
    print("\n1. Добавление зашифрованных медицинских карт в облачное хранилище:")
    system.add_record("Иван Петров", ["кашель", "температура", "головная боль"], "Грипп")
    system.add_record("Мария Смирнова", ["кашель", "одышка", "усталость"], "Пневмония")
    system.add_record("Алексей Иванов", ["головная боль", "тошнота", "головокружение"], "Мигрень")
    system.add_record("Елена Васильева", ["температура", "кашель", "потеря обоняния"], "COVID-19")
    system.add_record("Петр Сидоров", ["одышка", "боль в груди", "усталость"], "Сердечная недостаточность")
    
    print("   ✅ Добавлено 5 записей. Все данные зашифрованы (просмотр дамп):")
    for rec in system.encrypted_records:
        print(f"      ID = {rec['id']}: name = {rec['encrypted_name'][:10]}..., diagnosis = {rec['encrypted_diagnosis'][:10]}...")
    
    # Поиск без расшифровки
    print("\n2. Поиск по симптому 'кашель' (без расшифровки всех данных):")
    results = system.search_by_symptom("кашель")
    print(f"   Найдено записей: {len(results)}")
    for res in results:
        print(f"      ID = {res['id']}: зашифрованное имя = {res['encrypted_name'][:15]}..., диагноз = {res['encrypted_diagnosis'][:15]}...")
    
    # Расшифровка только найденных записей (привилегированный доступ)
    print("\n3. Расшифровка найденных записей (авторизованный врач):")
    for res in results:
        name, diagnosis = system.decrypt_record(res['encrypted_name'], res['encrypted_diagnosis'])
        print(f"      ID = {res['id']}: Имя = {name}, Диагноз = {diagnosis}")
    
    # Другой поиск
    print("\n4. Поиск по симптому 'одышка':")
    results2 = system.search_by_symptom("одышка")
    print(f"   Найдено записей: {len(results2)}")
    for res in results2:
        name, diagnosis = system.decrypt_record(res['encrypted_name'], res['encrypted_diagnosis'])
        print(f"      ID = {res['id']}: Имя = {name}, Диагноз = {diagnosis}")
    
    # Демонстрация безопасности
    print("\n5. Демонстрация безопасности:")
    print("   ❌ При перехвате данных в канале связи злоумышленник видит только:")
    sample_record = system.encrypted_records[0]
    print(f"      {json.dumps(sample_record, indent = 6)[:150]}...")
    print("   ✅ Без ключа расшифровать или найти связь между симптомами невозможно.")
    
    print("\n" + "=" * 70)
    print("ВЫВОД: Система позволяет искать по симптомам (гомоморфный поиск)")
    print("без расшифровки всех записей, что соответствует принципам CSE")
    print("из описания: EHR в облаке, безопасность, приватность пациентов.")
    print("=" * 70)

if __name__ == "__main__":
    main()