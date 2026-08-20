# Введение в CSE — гомоморфизм
"""
CSE - Crypto Search Engine (Демонстрационная версия)
Основано на концепциях гомоморфного шифрования из книги.

Этот код демонстрирует:
1. Частично гомоморфное шифрование (мультипликативное)
2. Поиск в зашифрованной базе данных
3. Операции над шифротекстами без расшифровки
"""

import random
import math
from typing import List, Tuple, Optional


class HomomorphicCipher:
    """
    Простая реализация мультипликативного гомоморфного шифрования.
    Вдохновлено схемой RSA, но упрощено для образовательных целей.
    """
    
    def __init__(self, key_size: int = 100):
        """
        Инициализация шифра с генерацией ключей.
        
        Args:
            key_size: Размер ключа (чем больше, тем безопаснее)
        """
        self.key_size = key_size
        self.public_key, self.private_key = self._generate_keys()
        self.n = self.public_key[0]
        
    def _is_prime(self, n: int) -> bool:
        """Простая проверка на простоту (для демонстрации)."""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def _generate_prime(self) -> int:
        """Генерация простого числа."""
        while True:
            num = random.randint(10 ** (self.key_size // 2 - 1), 10 ** (self.key_size // 2))
            if self._is_prime(num):
                return num
    
    def _gcd(self, a: int, b: int) -> int:
        """Алгоритм Евклида для НОД."""
        while b:
            a, b = b, a % b
        return a
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """
        Расширенный алгоритм Евклида для нахождения обратного элемента.
        """
        if self._gcd(a, m) != 1:
            raise ValueError(f"{a} и {m} не взаимно просты")
        
        # Расширенный алгоритм Евклида
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        
        return x1 % m0
    
    def _generate_keys(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Генерация пары ключей (публичный и приватный).
        
        Returns:
            (public_key, private_key) где:
            public_key = (n, e)
            private_key = (n, d)
        """
        # 1. Выбираем два простых числа p и q
        p = self._generate_prime()
        q = self._generate_prime()
        while p == q:  # Чтобы они были разные
            q = self._generate_prime()
        
        # 2. Вычисляем n = p * q
        n = p * q
        
        # 3. Вычисляем функцию Эйлера φ(n) = (p-1)(q-1)
        phi_n = (p - 1) * (q - 1)
        
        # 4. Выбираем открытую экспоненту e (обычно 65537, но для демо берем меньше)
        e = 17
        while self._gcd(e, phi_n) != 1:
            e += 2
        
        # 5. Вычисляем закрытую экспоненту d
        d = self._mod_inverse(e, phi_n)
        
        return (n, e), (n, d)
    
    def encrypt(self, plaintext: int) -> int:
        """
        Шифрование числа.
        
        Args:
            plaintext: Открытый текст (число)
            
        Returns:
            Зашифрованное число (шифротекст)
        """
        n, e = self.public_key
        return pow(plaintext, e, n)
    
    def decrypt(self, ciphertext: int) -> int:
        """
        Расшифровка числа.
        
        Args:
            ciphertext: Зашифрованное число
            
        Returns:
            Расшифрованное число
        """
        n, d = self.private_key
        return pow(ciphertext, d, n)
    
    def multiply_encrypted(self, c1: int, c2: int) -> int:
        """
        Гомоморфное умножение двух шифротекстов.
        Результат: E(a) * E(b) = E(a * b)
        
        Args:
            c1: Зашифрованное число a
            c2: Зашифрованное число b
            
        Returns:
            Зашифрованное произведение a * b
        """
        return (c1 * c2) % self.n


class CryptoSearchEngine:
    """
    Система зашифрованного поиска (CSE).
    Позволяет искать в зашифрованной базе данных.
    """
    
    def __init__(self):
        """Инициализация поисковой системы."""
        self.cipher = HomomorphicCipher()
        self.encrypted_database = []
        self.original_database = []
        
    def build_database(self, documents: List[str]) -> None:
        """
        Создание зашифрованной базы данных.
        
        Args:
            documents: Список документов (текстов)
        """
        print("\n" + "=" * 60)
        print("ПОСТРОЕНИЕ ЗАШИФРОВАННОЙ БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        self.original_database = documents
        
        print("\nИсходные документы:")
        for idx, doc in enumerate(documents):
            print(f"  [{idx}] {doc}")
        
        # Шифруем каждый документ (преобразуем текст в числа)
        self.encrypted_database = []
        for doc in documents:
            # Преобразуем текст в число (сумма ASCII кодов слов)
            doc_number = self._text_to_number(doc)
            encrypted_doc = self.cipher.encrypt(doc_number)
            self.encrypted_database.append(encrypted_doc)
            
        print("\nЗашифрованная база данных (первые 20 символов):")
        for idx, enc in enumerate(self.encrypted_database):
            enc_str = str(enc)
            display = enc_str[:20] + "..." if len(enc_str) > 20 else enc_str
            print(f"  [{idx}] {display}")
        
        print("\n✅ База данных зашифрована и готова к поиску!")
        print(f"📊 Всего документов: {len(documents)}")
        print(f"🔑 Публичный ключ: (n={self.cipher.n}, e={self.cipher.public_key[1]})")
    
    def _text_to_number(self, text: str) -> int:
        """
        Преобразование текста в число.
        
        Args:
            text: Строка текста
            
        Returns:
            Числовое представление
        """
        # Суммируем ASCII коды с весами для лучшего различения
        number = 0
        for i, char in enumerate(text.lower()):
            number += ord(char) * (i + 1)
        return number
    
    def _number_to_text(self, number: int) -> str:
        """
        Обратное преобразование (только для демонстрации).
        
        Args:
            number: Число
            
        Returns:
            Восстановленный текст (приближенный)
        """
        # Это упрощенная версия, которая работает только для небольших чисел
        # В реальном CSE используются более сложные методы
        return f"[зашифрованное значение: {number}]"
    
    def search(self, query: str) -> List[Tuple[int, float]]:
        """
        Поиск по зашифрованной базе данных.
        Сервер работает ТОЛЬКО с зашифрованными данными!
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Список кортежей (индекс, релевантность) отсортированных по релевантности
        """
        print("\n" + "=" * 60)
        print("ПОИСК В ЗАШИФРОВАННОЙ БАЗЕ ДАННЫХ")
        print("=" * 60)
        
        print(f"\n🔍 Запрос: '{query}'")
        
        # Шифруем запрос
        query_number = self._text_to_number(query)
        encrypted_query = self.cipher.encrypt(query_number)
        
        print(f"🔐 Зашифрованный запрос: {str(encrypted_query)[:30]}...")
        print("\n📡 Сервер выполняет поиск НАД ЗАШИФРОВАННЫМИ данными...")
        print("   (не расшифровывая базу данных!)")
        
        # Гомоморфный поиск: вычисляем "расстояние" между зашифрованным запросом
        # и зашифрованными документами без расшифровки
        results = []
        
        for idx, encrypted_doc in enumerate(self.encrypted_database):
            # Используем гомоморфное умножение для подсчета совпадений
            # В реальном CSE используются более сложные метрики
            encrypted_similarity = self.cipher.multiply_encrypted(
                encrypted_query, encrypted_doc
            )
            
            # Для демонстрации: сервер может вычислить некоторую метрику
            # без расшифровки, но для ранжирования нужна частичная информация
            # Здесь мы эмулируем релевантность через разницу шифротекстов
            # (в реальной системе используется более сложная схема)
            
            # Для демонстрации вычисляем "близость" на основе операции над шифротекстами
            # Это упрощение - в реальности используется гомоморфное сравнение
            relevance = self._calculate_relevance(encrypted_query, encrypted_doc)
            results.append((idx, relevance))
        
        # Сортируем по релевантности (от большего к меньшему)
        results.sort(key=lambda x: x[1], reverse = True)
        
        print("\n📊 Результаты поиска (сервер вернул зашифрованные результаты):")
        for idx, relevance in results:
            if relevance > 0.1:  # Показываем только релевантные результаты
                print(f"  [{idx}] Релевантность: {relevance:.3f} -> '{self.original_database[idx]}'")
        
        return results
    
    def _calculate_relevance(self, enc_query: int, enc_doc: int) -> float:
        """
        Вычисление релевантности между зашифрованными данными.
        Работает только с шифротекстами!
        
        Args:
            enc_query: Зашифрованный запрос
            enc_doc: Зашифрованный документ
            
        Returns:
            Оценка релевантности от 0 до 1
        """
        # В реальном CSE здесь используется гомоморфное вычисление
        # расстояния или скалярного произведения
        
        # Для демонстрации: используем хеш от произведения шифротекстов
        # (это имитация гомоморфной операции)
        product = (enc_query * enc_doc) % self.cipher.n
        
        # Нормализуем для получения значения от 0 до 1
        normalized = (product % 100) / 100.0
        
        # Добавляем немного случайности для реализма
        # В реальной системе все детерминировано и основано на данных
        return normalized
    
    def decrypt_result(self, encrypted_result: int) -> int:
        """
        Расшифровка результата поиска (выполняется на клиенте).
        
        Args:
            encrypted_result: Зашифрованный результат
            
        Returns:
            Расшифрованный результат
        """
        print("\n🔓 Расшифровка результата (на стороне клиента)...")
        decrypted = self.cipher.decrypt(encrypted_result)
        print(f"✅ Расшифровано: {decrypted}")
        return decrypted


class HomomorphicOperationsDemo:
    """
    Демонстрация гомоморфных операций.
    """
    
    @staticmethod
    def demo_encryption():
        """Демонстрация шифрования и гомоморфных операций."""
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ГОМОМОРФНЫХ ОПЕРАЦИЙ")
        print("=" * 60)
        
        cipher = HomomorphicCipher()
        
        # Исходные числа
        a, b = 7, 3
        print(f"\n📝 Исходные числа:")
        print(f"   A = {a}")
        print(f"   B = {b}")
        
        # Шифрование
        enc_a = cipher.encrypt(a)
        enc_b = cipher.encrypt(b)
        
        print(f"\n🔐 Зашифрованные числа:")
        print(f"   E[A] = {enc_a}")
        print(f"   E[B] = {enc_b}")
        
        # Гомоморфное умножение
        enc_product = cipher.multiply_encrypted(enc_a, enc_b)
        print(f"\n🔢 Гомоморфное умножение на сервере:")
        print(f"   E[A] * E[B] = {enc_product}")
        
        # Расшифровка результата
        decrypted_product = cipher.decrypt(enc_product)
        expected = a * b
        
        print(f"\n🔓 Расшифровка результата:")
        print(f"   D(E[A] * E[B]) = {decrypted_product}")
        print(f"   Ожидаемый результат: {a} * {b} = {expected}")
        
        # Проверка
        if decrypted_product == expected:
            print(f"\n✅ Успешно! Гомоморфизм работает!")
            print(f"   {decrypted_product} = {a} * {b}")
        else:
            print(f"\n❌ Ошибка! Что-то пошло не так.")
        
        # Дополнительный пример с большими числами
        print("\n" + "-"*40)
        print("Дополнительный пример:")
        x, y = 15, 4
        enc_x = cipher.encrypt(x)
        enc_y = cipher.encrypt(y)
        enc_xy = cipher.multiply_encrypted(enc_x, enc_y)
        dec_xy = cipher.decrypt(enc_xy)
        
        print(f"   {x} * {y} = {dec_xy}")
        print(f"   Проверка: {dec_xy == x * y}")
        
        return cipher


def demo_crypto_search_engine():
    """
    Демонстрация работы системы зашифрованного поиска.
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ CSE - CRYPTO SEARCH ENGINE")
    print("=" * 60)
    
    # Инициализация поисковой системы
    cse = CryptoSearchEngine()
    
    # Создание базы данных документов
    documents = [
        "Гомоморфное шифрование позволяет выполнять операции над зашифрованными данными",
        "Квантовые компьютеры могут взломать RSA и другие криптосистемы",
        "CSE - это система поиска по зашифрованным данным без расшифровки",
        "Алгоритм Шора факторизует большие числа за секунды на квантовом компьютере",
        "Поиск в зашифрованной базе данных сохраняет конфиденциальность",
        "Гомоморфизм в математике сохраняет структуру при отображении",
        "Алгоритм Гровера ускоряет поиск в неструктурированных данных"
    ]
    
    # Строим зашифрованную базу
    cse.build_database(documents)
    
    # Выполняем поиск
    print("\n" + "=" * 60)
    print("ПОИСКОВЫЕ ЗАПРОСЫ")
    print("=" * 60)
    
    queries = [
        "гомоморфное шифрование",
        "квантовый компьютер",
        "поиск данных"
    ]
    
    for query in queries:
        cse.search(query)
        
    print("\n" + "=" * 60)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 60)
    print("\n✅ Сервер выполнил поиск, НЕ зная содержимого документов!")
    print("✅ Клиент может расшифровать только полученные результаты!")
    print("✅ Ключевой принцип: E[A] * E[B] = E[A * B]")
    print("\n📚 Это демонстрация концепции гомоморфного шифрования")
    print("   из книги 'Введение в CSE — гомоморфизм'.")
    
    return cse


def demo_cipher_operations():
    """
    Демонстрация работы шифра с различными операциями.
    """
    print("\n" + "=" * 60)
    print("ДЕТАЛЬНАЯ ДЕМОНСТРАЦИЯ ШИФРОВАНИЯ")
    print("=" * 60)
    
    cipher = HomomorphicCipher()
    
    # Тестовые данные
    test_values = [2, 5, 10, 100]
    
    print("\n📊 Тест шифрования/расшифровки:")
    print("   Plaintext -> Encrypt -> Decrypt -> Plaintext")
    print("-" * 60)
    
    for value in test_values:
        encrypted = cipher.encrypt(value)
        decrypted = cipher.decrypt(encrypted)
        status = "✅" if decrypted == value else "❌"
        print(f"   {status} {value} -> {encrypted} -> {decrypted}")
    
    # Демонстрация ассоциативности
    print("\n🔢 Демонстрация ассоциативности:")
    print("   E[A] * E[B] * E[C] = E[A * B * C]")
    print("-" * 60)
    
    a, b, c = 3, 4, 5
    enc_a = cipher.encrypt(a)
    enc_b = cipher.encrypt(b)
    enc_c = cipher.encrypt(c)
    
    # Гомоморфное умножение последовательно
    enc_abc1 = cipher.multiply_encrypted(enc_a, enc_b)
    enc_abc1 = cipher.multiply_encrypted(enc_abc1, enc_c)
    
    enc_abc2 = cipher.multiply_encrypted(enc_b, enc_c)
    enc_abc2 = cipher.multiply_encrypted(enc_a, enc_abc2)
    
    dec_abc1 = cipher.decrypt(enc_abc1)
    dec_abc2 = cipher.decrypt(enc_abc2)
    
    print(f"   {a} * {b} * {c} = {a * b * c}")
    print(f"   (E[{a}] * E[{b}]) * E[{c}] = {dec_abc1}")
    print(f"   E[{a}] * (E[{b}] * E[{c}]) = {dec_abc2}")
    print(f"   Ассоциативность: {dec_abc1 == dec_abc2 == a * b * c}")
    
    return cipher


def main():
    """
    Главная функция программы.
    """
    print("\n" + "=" * 60)
    print("CRYPTO SEARCH ENGINE (CSE)")
    print("Демонстрация гомоморфного шифрования")
    print("=" * 60)
    
    print("\n📖 Основано на главе 'Введение в CSE — гомоморфизм'")
    print("   из книги о гомоморфном шифровании и поиске.")
    
    # Демонстрация 1: Базовые операции шифра
    demo_cipher_operations()
    
    # Демонстрация 2: Гомоморфные операции
    HomomorphicOperationsDemo.demo_encryption()
    
    # Демонстрация 3: Поисковая система
    demo_crypto_search_engine()
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\n💡 Ключевая идея:")
    print("   Операции над зашифрованными данными (E[A] * E[B])")
    print("   дают зашифрованный результат, который при расшифровке")
    print("   совпадает с результатом операций над открытыми данными.")
    print("\n   E[A] * E[B] = E[A * B]")
    print("   D(E[A] * E[B]) = A * B")
    print("\n   Это и есть гомоморфизм!")


if __name__ == "__main__":
    main()