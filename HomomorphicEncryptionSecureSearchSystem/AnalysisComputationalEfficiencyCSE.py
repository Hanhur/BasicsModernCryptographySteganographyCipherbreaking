# Анализ вычислительной эффективности CSE
"""
Анализ вычислительной эффективности CSE (Cryptographic Search Engine)
На основе текста: секрет слепого поиска, AES-256, аутентификация, эффективность E = S/T
Без использования NumPy
"""

import time
import hashlib
import os
import random
import math
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from typing import Dict, List, Tuple, Optional

class CSEAnalyzer:
    """
    Класс для анализа эффективности CSE системы
    Соответствует описанию из текста:
    - Шифрование файлов (AES-256)
    - Аутентификация (человек-ВМ, ВМ-ВМ)
    - Слепой поиск по зашифрованным данным
    - Расчет эффективности E = S / T
    """
    
    def __init__(self):
        self.security_level = 0.0
        self.search_time = 0.0
        self.efficiency = 0.0
        self.encrypted_files = {}
        self.file_sizes = {}
        self.keywords_index = {}
        self.backend = default_backend()
        
    def generate_aes_key(self) -> bytes:
        """Генерация ключа AES-256 (32 байта)"""
        return os.urandom(32)
    
    def generate_hmac_key(self) -> bytes:
        """Генерация ключа для HMAC-аутентификации"""
        return os.urandom(32)
    
    def encrypt_file_aes256(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """
        Шифрование данных алгоритмом AES-256 в режиме GCM
        Возвращает: (зашифрованные_данные, тег_аутентификации)
        """
        # Генерация случайного 12-байтового nonce (рекомендовано для GCM)
        nonce = os.urandom(12)
        
        # Создание шифра AES-256 в режиме GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend = self.backend)
        encryptor = cipher.encryptor()
        
        # Шифрование данных
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        # Возвращаем зашифрованные данные, nonce и тег
        return encrypted_data, nonce, encryptor.tag
    
    def decrypt_file_aes256(self, encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
        """
        Дешифрование данных AES-256 в режиме GCM
        """
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend = self.backend)
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data
    
    def calculate_security_level(self, algorithm: str = "AES-256", key_size: int = 256) -> float:
        """
        Расчет уровня безопасности S на основе алгоритма и размера ключа
        S = 0 - нет шифрования, S = 1 - квантовое шифрование (100% безопасность)
        """
        if algorithm == "AES-256":
            # AES-256 с 256-битным ключом
            # Учитываем: устойчивость к перебору, квантовые атаки (Гровер)
            # Теоретическая сложность: 2^256, квантовая: 2^128
            classical_security = 1.0 - (1.0 / (2 ** 128))  # Практически 1
            quantum_factor = 0.999999  # Учет квантовых атак
            self.security_level = classical_security * quantum_factor
            
        elif algorithm == "Twofish":
            # Twofish-256 как альтернатива (упоминается в тексте)
            self.security_level = 0.999998
            
        elif algorithm == "None":
            # Без шифрования (S = 0)
            self.security_level = 0.0
            
        elif algorithm == "Quantum":
            # Квантовое шифрование (теоретически 100%)
            self.security_level = 1.0
            
        else:
            self.security_level = 0.5
            
        return self.security_level
    
    def measure_encryption_time(self, data_size_bytes: int, key: bytes) -> float:
        """
        Измерение времени шифрования данных заданного размера
        """
        # Генерация тестовых данных
        test_data = os.urandom(data_size_bytes)
        
        start_time = time.perf_counter()
        encrypted, nonce, tag = self.encrypt_file_aes256(test_data, key)
        end_time = time.perf_counter()
        
        return end_time - start_time
    
    def measure_search_time(self, query_keyword: str, total_files: int, encrypted_files: Dict, keywords_index: Dict) -> float:
        """
        Измерение времени выполнения слепого поиска
        """
        start_time = time.perf_counter()
        
        # Симуляция слепого поиска по зашифрованным данным
        # Без расшифровки - поиск по индексу ключевых слов
        results = []
        
        if query_keyword in keywords_index:
            # Слепой поиск по зашифрованным токенам
            encrypted_token = hashlib.sha256(query_keyword.encode()).digest()
            
            # Поиск в индексе
            for file_id in keywords_index[query_keyword]:
                # Аутентификация доступа к файлу (проверка HMAC)
                if self.authenticate_access(file_id):
                    results.append(file_id)
        
        end_time = time.perf_counter()
        self.search_time = end_time - start_time
        
        return self.search_time
    
    def authenticate_access(self, file_id: str) -> bool:
        """
        Аутентификация доступа к файлу
        Имитация проверки между человеком и ВМ, а также между ВМ
        """
        # Симуляция времени аутентификации (0.0001 - 0.001 сек)
        auth_time = random.uniform(0.0001, 0.001)
        time.sleep(auth_time)  # Имитация задержки аутентификации
        
        # Случайный успех аутентификации (для демонстрации)
        return random.random() > 0.05  # 95% успешных аутентификаций
    
    def calculate_efficiency(self) -> float:
        """
        Расчет эффективности системы E = S / T
        Где S - уровень безопасности (0 - 1), T - время обработки запроса
        """
        if self.search_time > 0:
            self.efficiency = self.security_level / self.search_time
        else:
            self.efficiency = 0.0
            
        return self.efficiency
    
    def build_encrypted_dataset(self, num_files: int, avg_file_size_kb: int) -> Dict:
        """
        Создание зашифрованного набора данных
        """
        key = self.generate_aes_key()
        encrypted_files = {}
        file_sizes = {}
        
        total_size_bytes = 0
        keywords = ["security", "encryption", "search", "database", "crypto", "authentication", "privacy"]
        
        for i in range(num_files):
            # Генерация файла с текстовыми данными
            file_content = self.generate_file_content(avg_file_size_kb, keywords)
            file_size_bytes = len(file_content)
            total_size_bytes += file_size_bytes
            
            # Шифрование файла
            encrypted, nonce, tag = self.encrypt_file_aes256(file_content.encode(), key)
            
            file_id = f"file_{i + 1}"
            encrypted_files[file_id] = {
                'encrypted_data': encrypted,
                'nonce': nonce,
                'tag': tag,
                'key': key
            }
            file_sizes[file_id] = file_size_bytes
            
            # Индексация ключевых слов для поиска
            for keyword in keywords:
                if keyword in file_content.lower():
                    if keyword not in self.keywords_index:
                        self.keywords_index[keyword] = []
                    self.keywords_index[keyword].append(file_id)
        
        self.encrypted_files = encrypted_files
        self.file_sizes = file_sizes
        
        return encrypted_files
    
    def generate_file_content(self, size_kb: int, keywords: List[str]) -> str:
        """
        Генерация содержимого файла с ключевыми словами
        """
        base_text = "This is a sample document about cryptography and security. "
        base_text += "The system uses advanced encryption for data protection. "
        base_text += "Search functionality enables efficient retrieval of encrypted information. "
        base_text += "Authentication ensures secure access to files. "
        
        # Добавляем ключевые слова в текст
        for keyword in keywords[:3]:
            base_text += f"Keyword: {keyword}. "
            
        # Дополняем до нужного размера
        multiplier = max(1, int((size_kb * 1024) / len(base_text)))
        full_text = base_text * multiplier
        
        # Усекаем до точного размера
        return full_text[:size_kb * 1024]
    
    def run_simulation(self, num_files: int = 100, avg_file_size_kb: int = 10):
        """
        Запуск полной симуляции CSE системы
        """
        print("=" * 80)
        print("АНАЛИЗ ВЫЧИСЛИТЕЛЬНОЙ ЭФФЕКТИВНОСТИ CSE")
        print("=" * 80)
        
        # 1. Инициализация системы
        print("\n[1] Инициализация системы шифрования...")
        master_key = self.generate_aes_key()
        
        # 2. Расчет уровня безопасности
        print("\n[2] Расчет уровня безопасности (S)...")
        algorithms = ["AES-256", "Twofish", "None", "Quantum"]
        for alg in algorithms:
            sec_level = self.calculate_security_level(alg)
            print(f"  - {alg}: S = {sec_level:.8f}")
        
        # Устанавливаем AES-256 как основной
        self.calculate_security_level("AES-256")
        print(f"\n  Выбран алгоритм: AES-256 с S = {self.security_level:.8f}")
        
        # 3. Создание зашифрованных данных
        print(f"\n[3] Создание зашифрованного набора данных...")
        print(f"  - Количество файлов: {num_files}")
        print(f"  - Средний размер файла: {avg_file_size_kb} KB")
        
        total_data_size_kb = num_files * avg_file_size_kb
        total_data_size_mb = total_data_size_kb / 1024
        total_data_size_gb = total_data_size_mb / 1024
        print(f"  - Общий объем данных: {total_data_size_kb:.2f} KB "
              f"({total_data_size_mb:.2f} MB, {total_data_size_gb:.6f} GB)")
        
        # Измеряем время шифрования
        start_encryption = time.perf_counter()
        self.build_encrypted_dataset(num_files, avg_file_size_kb)
        end_encryption = time.perf_counter()
        encryption_time = end_encryption - start_encryption
        
        print(f"  - Время шифрования: {encryption_time:.4f} секунд")
        print(f"  - Количество ключевых слов в индексе: {len(self.keywords_index)}")
        
        # 4. Тестирование поиска
        print("\n[4] Тестирование слепого поиска...")
        test_keywords = ["security", "encryption", "database", "privacy"]
        
        for keyword in test_keywords:
            # Измеряем время поиска
            search_time = self.measure_search_time(
                keyword, 
                num_files, 
                self.encrypted_files, 
                self.keywords_index
            )
            
            # Рассчитываем эффективность
            efficiency = self.calculate_efficiency()
            
            print(f"\n  Запрос: '{keyword}'")
            print(f"    - Время обработки (T): {search_time:.6f} секунд")
            print(f"    - Уровень безопасности (S): {self.security_level:.8f}")
            print(f"    - Эффективность (E = S/T): {efficiency:.2f}")
            
            if keyword in self.keywords_index:
                result_count = len(self.keywords_index[keyword])
                print(f"    - Найдено файлов: {result_count}")
            else:
                print(f"    - Найдено файлов: 0")
        
        # 5. Вычисление средней эффективности
        print("\n[5] Статистика системы...")
        avg_search_time = 0
        for keyword in test_keywords:
            t = self.measure_search_time(keyword, num_files, self.encrypted_files, self.keywords_index)
            avg_search_time += t
        avg_search_time /= len(test_keywords)
        
        self.search_time = avg_search_time
        avg_efficiency = self.calculate_efficiency()
        
        print(f"  - Среднее время поиска: {avg_search_time:.6f} секунд")
        print(f"  - Средняя эффективность: {avg_efficiency:.2f}")
        print(f"  - Общее количество обработанных ключевых слов: {sum(len(v) for v in self.keywords_index.values())}")
        
        # 6. Анализ масштабирования
        print("\n[6] Анализ масштабирования...")
        scales = [100, 500, 1000]
        for scale_num_files in scales:
            scale_encryption_time = self.measure_encryption_time(
                scale_num_files * avg_file_size_kb * 1024, 
                master_key
            )
            print(f"  - {scale_num_files} файлов: время шифрования = {scale_encryption_time:.4f} сек, " f"объем = {scale_num_files * avg_file_size_kb / 1024:.2f} MB")
        
        # 7. Расчет теоретической эффективности по формуле из текста
        print("\n[7] Итоговый расчет эффективности по формуле E = S/T:")
        print(f"  S (безопасность AES-256) = {self.security_level:.10f}")
        print(f"  T (среднее время поиска) = {avg_search_time:.6f} сек")
        print(f"  E = {self.security_level:.10f} / {avg_search_time:.6f} = {avg_efficiency:.2f}")
        
        # Проверка условия T <= 2 секунды (из текста)
        if avg_search_time <= 2.0:
            print(f"  ✓ Время поиска ({avg_search_time:.4f} сек) соответствует требованию <= 2 сек")
        else:
            print(f"  ✗ Время поиска ({avg_search_time:.4f} сек) превышает требование <= 2 сек")
        
        print("\n" + "=" * 80)
        print("СИМУЛЯЦИЯ ЗАВЕРШЕНА")
        print("=" * 80)
        
        return {
            'security_level': self.security_level,
            'search_time': avg_search_time,
            'efficiency': avg_efficiency,
            'encryption_time': encryption_time,
            'num_files': num_files,
            'total_data_gb': total_data_size_gb
        }

def demo_authentication():
    """
    Демонстрация аутентификации между человеком и ВМ, и между ВМ
    """
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ АУТЕНТИФИКАЦИИ")
    print("=" * 80)
    
    # Генерация ключей аутентификации
    hmac_key = os.urandom(32)
    backend = default_backend()
    
    def authenticate_human_vm(username: str, password: str) -> bool:
        """Аутентификация между человеком и виртуальной машиной"""
        # Создание HMAC для верификации
        h = hmac.HMAC(hmac_key, hashes.SHA256(), backend = backend)
        auth_data = f"{username}:{password}".encode()
        h.update(auth_data)
        signature = h.finalize()
        
        # Симуляция верификации (сравнение с ожидаемым)
        expected_username = "admin"
        expected_password = "secure_pass"
        expected_data = f"{expected_username}:{expected_password}".encode()
        h_expected = hmac.HMAC(hmac_key, hashes.SHA256(), backend = backend)
        h_expected.update(expected_data)
        expected_signature = h_expected.finalize()
        
        return signature == expected_signature
    
    def authenticate_vm_vm(vm_id_1: str, vm_id_2: str, token: str) -> bool:
        """Аутентификация между виртуальными машинами"""
        h = hmac.HMAC(hmac_key, hashes.SHA256(), backend = backend)
        auth_data = f"{vm_id_1}:{vm_id_2}:{token}".encode()
        h.update(auth_data)
        signature = h.finalize()
        
        # Для демонстрации - проверяем длину подписи
        return len(signature) == 32
    
    # Тестирование аутентификации
    print("\n[1] Аутентификация: Человек -> Виртуальная машина")
    result = authenticate_human_vm("admin", "secure_pass")
    print(f"  Результат: {'УСПЕШНО' if result else 'ОШИБКА'}")
    
    print("\n[2] Аутентификация: Виртуальная машина <-> Виртуальная машина")
    result = authenticate_vm_vm("VM-001", "VM-002", "session_token_123")
    print(f"  Результат: {'УСПЕШНО' if result else 'ОШИБКА'}")
    
    # Измерение времени аутентификации
    print("\n[3] Измерение времени аутентификации...")
    times = []
    for _ in range(100):
        start = time.perf_counter()
        authenticate_human_vm("admin", "secure_pass")
        end = time.perf_counter()
        times.append(end - start)
    
    avg_auth_time = sum(times) / len(times)
    print(f"  Среднее время аутентификации (человек-ВМ): {avg_auth_time:.8f} сек")
    print("=" * 80)

def main():
    """
    Главная функция запуска программы
    """
    # Создание экземпляра анализатора
    analyzer = CSEAnalyzer()
    
    # Запуск симуляции с параметрами из текста
    print("ЗАПУСК АНАЛИЗА ВЫЧИСЛИТЕЛЬНОЙ ЭФФЕКТИВНОСТИ CSE")
    print("На основе: AES-256, слепой поиск, аутентификация\n")
    
    # Параметры по умолчанию (как в тексте)
    num_files = 100
    avg_file_size_kb = 50  # 50 KB на файл
    
    results = analyzer.run_simulation(num_files, avg_file_size_kb)
    
    # Демонстрация аутентификации
    demo_authentication()
    
    # Итоговые результаты
    print("\n" + "=" * 80)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("=" * 80)
    print(f"Всего проанализировано файлов: {results['num_files']}")
    print(f"Общий объем данных: {results['total_data_gb']:.6f} GB")
    print(f"Уровень безопасности (S): {results['security_level']:.10f}")
    print(f"Среднее время поиска (T): {results['search_time']:.6f} сек")
    print(f"Эффективность системы (E): {results['efficiency']:.2f}")
    print(f"Время шифрования всех файлов: {results['encryption_time']:.4f} сек")
    print("=" * 80)
    
    # Вывод рекомендаций из текста
    print("\nРЕКОМЕНДАЦИИ ПО ПОВЫШЕНИЮ ЭФФЕКТИВНОСТИ:")
    print("1. Использовать AES-256 с аппаратным ускорением (AES-NI)")
    print("2. Применять индексирование ключевых слов для уменьшения T")
    print("3. Внедрить кеширование частых запросов")
    print("4. Оптимизировать аутентификацию через HMAC-SHA256")
    print("5. Рассмотреть альтернативу Twofish для дополнительной безопасности")
    
    if results['search_time'] > 2.0:
        print("\n⚠ ВНИМАНИЕ: Время поиска превышает 2 секунды!")
        print("  Рекомендуется оптимизировать индекс или использовать параллельную обработку")

if __name__ == "__main__":
    main()