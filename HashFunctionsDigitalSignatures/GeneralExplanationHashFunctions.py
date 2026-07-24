# Общее объяснение хеш-функций
"""
Демонстрация принципов работы хеш-функций
Основано на тексте о криптографических хеш-функциях
Без использования numpy - только стандартная библиотека Python
"""

import hashlib
import time
import random
import string
from collections import defaultdict
from typing import Tuple, Optional

# ============================================================================
# БЛОК 1: БАЗОВЫЕ ХЕШ-ФУНКЦИИ (Демонстрация основных свойств)
# ============================================================================

class HashDemonstration:
    """Класс для демонстрации свойств хеш-функций"""
    
    @staticmethod
    def get_hash(message: str, algorithm: str = 'sha256') -> str:
        """
        Вычисляет хеш сообщения (дайджест)
        
        Args:
            message: Входное сообщение произвольной длины
            algorithm: Алгоритм хеширования (sha256, sha1, md5)
        
        Returns:
            Hex-представление хеша фиксированной длины
        """
        if algorithm == 'sha256':
            hash_obj = hashlib.sha256()
        elif algorithm == 'sha1':
            hash_obj = hashlib.sha1()
        elif algorithm == 'md5':
            hash_obj = hashlib.md5()
        else:
            raise ValueError(f"Неподдерживаемый алгоритм: {algorithm}")
        
        # Кодируем сообщение в байты и вычисляем хеш
        hash_obj.update(message.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def demonstrate_fixed_length():
        """Демонстрация свойства фиксированной длины выхода"""
        print("\n" + "=" * 70)
        print("СВОЙСТВО 1: ФИКСИРОВАННАЯ ДЛИНА ВЫХОДНЫХ ДАННЫХ")
        print("=" * 70)
        
        test_messages = [
            "A",  # 1 символ
            "Hello, World!",  # 13 символов
            "Это очень длинное сообщение, которое содержит много текста" * 10,  # ~500 символов
            ""  # Пустое сообщение
        ]
        
        for msg in test_messages:
            hash_val = HashDemonstration.get_hash(msg)
            display_msg = msg[:50] + "..." if len(msg) > 50 else msg or "(empty)"
            print(f"Вход: {display_msg}")
            print(f"Длина входа: {len(msg)} байт -> Длина хеша: {len(hash_val)} символов (256 бит)")
            print(f"Хеш: {hash_val[:16]}...{hash_val[-16:]}\n")
    
    @staticmethod
    def demonstrate_avalanche_effect():
        """
        Демонстрация лавинного эффекта:
        Изменение 1 бита полностью меняет хеш
        """
        print("\n" + "=" * 70)
        print("СВОЙСТВО 2: ЛАВИННЫЙ ЭФФЕКТ (Avalanche Effect)")
        print("=" * 70)
        
        # Исходное сообщение
        original = "Hello, World!"
        # Изменяем всего 1 символ
        modified = "Hello, World?"  # '!' -> '?' (меняем 1 байт)
        
        hash1 = HashDemonstration.get_hash(original)
        hash2 = HashDemonstration.get_hash(modified)
        
        print(f"Исходное сообщение: {original}")
        print(f"Хеш 1: {hash1}\n")
        print(f"Измененное сообщение: {modified}")
        print(f"Хеш 2: {hash2}\n")
        
        # Сравниваем хеши
        different_bits = sum(1 for a, b in zip(hash1, hash2) if a != b)
        print(f"Количество различающихся hex-символов: {different_bits} из {len(hash1)}")
        print(f"Процент изменений: {different_bits / len(hash1) * 100:.1f}%")
        
        # Проверяем, что хеши разные
        if hash1 != hash2:
            print("✅ Хеши отличаются - изменение 1 бита полностью меняет дайджест!")
    
    @staticmethod
    def demonstrate_one_way():
        """
        Демонстрация однонаправленности:
        По хешу невозможно восстановить исходное сообщение
        """
        print("\n" + "=" * 70)
        print("СВОЙСТВО 3: ОДНОНАПРАВЛЕННОСТЬ (One-way Function)")
        print("=" * 70)
        
        # Предположим, у нас есть только хеш
        secret_message = "Секретное сообщение для подписи"
        hash_value = HashDemonstration.get_hash(secret_message)
        
        print(f"Исходное сообщение: {secret_message}")
        print(f"Хеш сообщения: {hash_value[:16]}...{hash_value[-16:]}\n")
        print("❌ По этому хешу невозможно восстановить исходное сообщение")
        print("   (единственный способ - перебор, который практически невозможен)")

# ============================================================================
# БЛОК 2: ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ
# ============================================================================

class IntegrityChecker:
    """Класс для демонстрации проверки целостности"""
    
    @staticmethod
    def verify_integrity(original_message: str, received_message: str) -> bool:
        """
        Проверяет целостность сообщения путем сравнения хешей
        
        Args:
            original_message: Оригинальное сообщение
            received_message: Полученное сообщение для проверки
        
        Returns:
            True если хеши совпадают (целостность не нарушена)
        """
        original_hash = HashDemonstration.get_hash(original_message)
        received_hash = HashDemonstration.get_hash(received_message)
        
        return original_hash == received_hash
    
    @staticmethod
    def demonstrate_integrity():
        """Демонстрация проверки целостности"""
        print("\n" + "=" * 70)
        print("ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ")
        print("=" * 70)
        
        # Оригинальное сообщение
        original = "Важное сообщение: перевести 1000 монет на кошелек 0xABCD"
        print(f"Оригинал: {original}\n")
        
        # Получатель получает сообщение без изменений
        received_ok = "Важное сообщение: перевести 1000 монет на кошелек 0xABCD"
        is_valid = IntegrityChecker.verify_integrity(original, received_ok)
        print(f"Сообщение получено без изменений: {is_valid}")
        if is_valid:
            print("✅ Целостность подтверждена - можно доверять данным")
        
        # Получатель получает измененное сообщение (изменен 1 символ)
        received_bad = "Важное сообщение: перевести 9999 монет на кошелек 0xABCD"
        is_valid = IntegrityChecker.verify_integrity(original, received_bad)
        print(f"\nСообщение с изменением: {received_bad}")
        print(f"Целостность подтверждена: {is_valid}")
        if not is_valid:
            print("❌ Целостность нарушена - данные были изменены!")
        
        # Показываем хеши для наглядности
        print(f"\nХеш оригинала: {HashDemonstration.get_hash(original)[:20]}...")
        print(f"Хеш измененного: {HashDemonstration.get_hash(received_bad)[:20]}...")

# ============================================================================
# БЛОК 3: ПОИСК КОЛЛИЗИЙ (Демонстрация устойчивости)
# ============================================================================

class CollisionSearch:
    """Демонстрация поиска коллизий (для MD5 - учебный пример)"""
    
    @staticmethod
    def find_collision_md5():
        """
        Поиск коллизий в MD5 (учебная демонстрация)
        ВНИМАНИЕ: Для реальных хешей (SHA-256) это практически невозможно!
        """
        print("\n" + "=" * 70)
        print("УСТОЙЧИВОСТЬ К КОЛЛИЗИЯМ (Collision Resistance)")
        print("=" * 70)
        
        # MD5 сломан, поэтому коллизии можно найти перебором
        # Для демонстрации ищем два разных сообщения с одинаковым хешем
        print("Демонстрация поиска коллизий для MD5 (учебный пример):\n")
        
        hash_table = {}
        messages_found = 0
        max_attempts = 100000
        
        print(f"Перебираем случайные сообщения (максимум {max_attempts} попыток)...")
        
        for i in range(max_attempts):
            # Генерируем случайное сообщение
            length = random.randint(3, 10)
            message = ''.join(random.choice(string.ascii_letters) for _ in range(length))
            
            # Вычисляем хеш MD5
            hash_val = HashDemonstration.get_hash(message, algorithm = 'md5')
            
            # Проверяем, есть ли уже такое хеш-значение
            if hash_val in hash_table:
                if hash_table[hash_val] != message:
                    print(f"\n✅ Найдена коллизия!")
                    print(f"Сообщение 1: {hash_table[hash_val]}")
                    print(f"Сообщение 2: {message}")
                    print(f"Хеш MD5: {hash_val}")
                    return
            else:
                hash_table[hash_val] = message
                messages_found += 1
                if messages_found % 10000 == 0:
                    print(f"Проверено {messages_found} уникальных сообщений...")
        
        print(f"\n❌ Коллизия не найдена за {max_attempts} попыток")
        print("  (Это хорошо - для SHA-256 это практически невозможно!)")
        
        print("\nДля SHA-256 поиск коллизий потребует более 2 ^ 128 операций,")
        print("что невозможно при современном уровне технологий.")
    
    @staticmethod
    def birthday_paradox_demo():
        """Демонстрация парадокса дней рождения (атака на хеш-функции)"""
        print("\n" + "=" * 70)
        print("ПАРАДОКС ДНЕЙ РОЖДЕНИЯ (Birthday Attack)")
        print("=" * 70)
        
        # Для 64-битного хеша количество попыток до коллизии ~2^32
        print("Теоретическая оценка:")
        print("- Для 64-битного хеша нужно ~2 ^ 32 попыток для коллизии")
        print("- Для 128-битного хеша нужно ~2 ^ 64 попыток")
        print("- Для 256-битного хеша нужно ~2 ^ 128 попыток (практически невозможно)")
        
        # Простая симуляция для малого пространства
        print("\nСимуляция для малого пространства (8 бит, 256 значений):")
        
        hash_bits = 8
        max_value = 2 ** hash_bits
        seen = set()
        attempts = 0
        
        while True:
            # Генерируем "хеш" как случайное число
            hash_val = random.randint(0, max_value - 1)
            attempts += 1
            
            if hash_val in seen:
                print(f"Найдена коллизия за {attempts} попыток (пространство {max_value} значений)")
                print(f"Теоретическое ожидание: ~{int(max_value ** 0.5)} попыток")
                break
            
            seen.add(hash_val)
            if attempts > max_value * 2:
                print("Остановка - слишком много попыток")
                break

# ============================================================================
# БЛОК 4: ИНДЕКСИРОВАНИЕ БАЗ ДАННЫХ (Поиск)
# ============================================================================

class HashIndexing:
    """Демонстрация использования хешей для индексирования"""
    
    @staticmethod
    def demonstrate_indexing():
        """Демонстрация хеш-индекса для быстрого поиска"""
        print("\n" + "=" * 70)
        print("ИНДЕКСИРОВАНИЕ БАЗ ДАННЫХ С ПОМОЩЬЮ ХЕШЕЙ")
        print("=" * 70)
        
        # Создаем хеш-таблицу для быстрого поиска
        hash_index = {}
        
        # Данные для индексации
        records = [
            ("Alice", "alice@email.com", "123-456-7890"),
            ("Bob", "bob@email.com", "234-567-8901"),
            ("Charlie", "charlie@email.com", "345-678-9012"),
            ("Diana", "diana@email.com", "456-789-0123")
        ]
        
        print("Создание хеш-индекса для записей:")
        for name, email, phone in records:
            # Ключ - это хеш от имени
            key = HashDemonstration.get_hash(name)[:8]  # Берем первые 8 символов для компактности
            hash_index[key] = (name, email, phone)
            print(f"  {name} -> хеш: {key}")
        
        print("\nБыстрый поиск по хешу:")
        search_name = "Bob"
        search_hash = HashDemonstration.get_hash(search_name)[:8]
        
        if search_hash in hash_index:
            record = hash_index[search_hash]
            print(f"  Найдена запись: {record}")
            print(f"  Время поиска: O(1) - константное время!")
        else:
            print(f"  Запись не найдена")
        
        print("\n✅ Хеши позволяют искать данные за постоянное время")
        print("  (независимо от размера базы данных)")

# ============================================================================
# БЛОК 5: СИМУЛЯЦИЯ ЦИФРОВОЙ ПОДПИСИ
# ============================================================================

class DigitalSignatureSimulation:
    """
    Симуляция использования хешей в цифровых подписях
    (упрощенная версия без реальной асимметричной криптографии)
    """
    
    def __init__(self):
        # В реальной системе здесь были бы публичный и приватный ключи
        self.private_key = "секретный_ключ_отправителя"
        self.public_key = "публичный_ключ_отправителя"
    
    def sign(self, message: str) -> Tuple[str, str]:
        """
        Создает цифровую подпись для сообщения
        
        Args:
            message: Исходное сообщение
        
        Returns:
            (подпись, хеш_сообщения)
        """
        # Шаг 1: Вычисляем хеш сообщения
        message_hash = HashDemonstration.get_hash(message)
        
        # Шаг 2: Подписываем хеш (в реальности - шифруем приватным ключом)
        # Здесь мы просто создаем подпись как комбинацию хеша и ключа
        signature = HashDemonstration.get_hash(message_hash + self.private_key)
        
        return signature, message_hash
    
    def verify(self, message: str, signature: str, expected_hash: str) -> bool:
        """
        Проверяет цифровую подпись
        
        Args:
            message: Полученное сообщение
            signature: Подпись отправителя
            expected_hash: Ожидаемый хеш сообщения
        
        Returns:
            True если подпись валидна
        """
        # Шаг 1: Вычисляем хеш полученного сообщения
        current_hash = HashDemonstration.get_hash(message)
        
        # Шаг 2: Проверяем, что хеш совпадает с ожидаемым
        if current_hash != expected_hash:
            return False
        
        # Шаг 3: Проверяем подпись (в реальности - расшифровываем публичным ключом)
        expected_signature = HashDemonstration.get_hash(current_hash + self.private_key)
        
        return signature == expected_signature
    
    @staticmethod
    def demonstrate():
        """Демонстрация процесса подписания"""
        print("\n" + "=" * 70)
        print("ЦИФРОВАЯ ПОДПИСЬ С ИСПОЛЬЗОВАНИЕМ ХЕШЕЙ")
        print("=" * 70)
        
        sim = DigitalSignatureSimulation()
        
        # Оригинальное сообщение
        message = "Важное сообщение: перевод 1000 BTC на кошелек 0x123"
        print(f"Исходное сообщение: {message}\n")
        
        # Создание подписи
        signature, message_hash = sim.sign(message)
        print(f"Хеш сообщения: {message_hash[:16]}...{message_hash[-16:]}")
        print(f"Цифровая подпись: {signature[:16]}...{signature[-16:]}\n")
        
        # Проверка подписи (сообщение не изменено)
        print("Проверка подписи (сообщение не изменено):")
        is_valid = sim.verify(message, signature, message_hash)
        print(f"Результат: {is_valid}")
        if is_valid:
            print("✅ Подпись подтверждена - отправитель идентифицирован")
        
        # Проверка подписи (сообщение изменено)
        print("\nПроверка подписи (сообщение изменено):")
        tampered_message = "Важное сообщение: перевод 9999 BTC на кошелек 0x123"
        is_valid = sim.verify(tampered_message, signature, message_hash)
        print(f"Результат: {is_valid}")
        if not is_valid:
            print("❌ Подпись недействительна - сообщение было изменено!")
        
        print("\n✅ Хеш позволяет подписывать дайджест вместо всего сообщения,")
        print("   что экономит время и сохраняет конфиденциальность!")

# ============================================================================
# БЛОК 6: СРАВНЕНИЕ АЛГОРИТМОВ ПО СКОРОСТИ
# ============================================================================

class PerformanceComparison:
    """Сравнение производительности различных хеш-алгоритмов"""
    
    @staticmethod
    def benchmark():
        """Бенчмарк различных хеш-алгоритмов"""
        print("\n" + "=" * 70)
        print("СРАВНЕНИЕ СКОРОСТИ ХЕШ-АЛГОРИТМОВ")
        print("=" * 70)
        
        # Создаем тестовое сообщение
        test_message = "Тестовое сообщение " * 1000
        algorithms = ['md5', 'sha1', 'sha256']
        iterations = 1000
        
        print(f"Тестовое сообщение: {len(test_message)} символов")
        print(f"Количество итераций: {iterations}\n")
        
        for algo in algorithms:
            start_time = time.time()
            
            for _ in range(iterations):
                HashDemonstration.get_hash(test_message, algorithm = algo)
            
            elapsed = time.time() - start_time
            print(f"{algo.upper()}: {elapsed:.3f} секунд")
        
        print("\n📊 MD5 и SHA-1 быстрее, но SHA-256 безопаснее")
        print("   Для большинства приложений выбирают SHA-256")

# ============================================================================
# БЛОК 7: ХЕШИРОВАНИЕ БОЛЬШИХ ФАЙЛОВ (по кускам)
# ============================================================================

class FileHashDemo:
    """Демонстрация хеширования больших данных по частям"""
    
    @staticmethod
    def hash_large_data(data_parts):
        """
        Хеширует данные по частям (как при работе с большими файлами)
        
        Args:
            data_parts: Список частей данных
        """
        print("\n" + "=" * 70)
        print("ХЕШИРОВАНИЕ БОЛЬШИХ ДАННЫХ ПО ЧАСТЯМ")
        print("=" * 70)
        
        # Инициализируем хеш-объект
        hash_obj = hashlib.sha256()
        
        print("Обработка данных по частям:")
        total_size = 0
        
        for i, part in enumerate(data_parts, 1):
            encoded = part.encode('utf-8')
            hash_obj.update(encoded)
            total_size += len(encoded)
            print(f"  Часть {i}: {len(part)} символов")
        
        final_hash = hash_obj.hexdigest()
        print(f"\nОбщий размер: {total_size} байт")
        print(f"Итоговый хеш: {final_hash}")
        
        # Сравниваем с хешированием всех данных сразу
        full_data = ''.join(data_parts)
        direct_hash = HashDemonstration.get_hash(full_data)
        
        print(f"\nХеш прямым методом: {direct_hash}")
        
        if final_hash == direct_hash:
            print("✅ Результаты совпадают - по частям работает корректно")
        
        print("\n💡 Это позволяет хешировать файлы любого размера")
        print("   без загрузки всего файла в память!")

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ (Запуск всех демонстраций)
# ============================================================================

def main():
    """Запуск всех демонстраций"""
    print("\n" + "=" * 70)
    print("КРИПТОГРАФИЧЕСКИЕ ХЕШ-ФУНКЦИИ: ПРАКТИЧЕСКАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 70)
    print("Основано на тексте о свойствах и применении хеш-функций")
    print("Библиотеки: только стандартный Python (hashlib, time, random, string)")
    
    # Создаем объекты для демонстраций
    demo = HashDemonstration()
    integrity = IntegrityChecker()
    collision = CollisionSearch()
    indexing = HashIndexing()
    signature = DigitalSignatureSimulation()
    perf = PerformanceComparison()
    file_demo = FileHashDemo()
    
    # Запускаем демонстрации
    demo.demonstrate_fixed_length()
    demo.demonstrate_avalanche_effect()
    demo.demonstrate_one_way()
    
    integrity.demonstrate_integrity()
    
    # Комментируем поиск коллизий MD5, чтобы не тратить время
    print("\n" + "=" * 70)
    print("ПОИСК КОЛЛИЗИЙ (ПРОПУСК ДЛЯ ЭКОНОМИИ ВРЕМЕНИ)")
    print("=" * 70)
    print("Для демонстрации поиска коллизий раскомментируйте вызов")
    print("collision.find_collision_md5() в функции main()")
    # collision.find_collision_md5()  # Раскомментируйте для поиска коллизий MD5
    
    collision.birthday_paradox_demo()
    indexing.demonstrate_indexing()
    signature.demonstrate()
    perf.benchmark()
    
    # Демонстрация хеширования по частям
    data_parts = [
        "Первая часть данных ",
        "Вторая часть данных ",
        "Третья часть данных ",
        "Четвертая часть данных"
    ]
    file_demo.hash_large_data(data_parts)
    
    # Итоговое резюме
    print("\n" + "=" * 70)
    print("ИТОГОВОЕ РЕЗЮМЕ")
    print("=" * 70)
    print("✅ Хеш-функции преобразуют данные произвольной длины в фиксированный дайджест")
    print("✅ Являются однонаправленными (невозможно восстановить оригинал)")
    print("✅ Обладают лавинным эффектом (1 бит меняет весь хеш)")
    print("✅ Устойчивы к коллизиям (невозможно найти два одинаковых хеша)")
    print("✅ Используются для цифровых подписей, проверки целостности, индексирования")
    print("✅ SHA-256 - современный стандарт безопасности")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()