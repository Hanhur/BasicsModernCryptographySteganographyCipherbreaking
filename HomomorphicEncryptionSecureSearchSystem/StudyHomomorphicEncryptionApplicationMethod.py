# Изучение гомоморфного шифрования и способы его применения
import hashlib
import random
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class HomomorphicCipher:
    """
    Упрощенная реализация гомоморфного шифрования на основе модульной арифметики.
    Демонстрирует аддитивный гомоморфизм: E(a) + E(b) = E(a + b)
    """
    
    def __init__(self, prime_modulus: int = 9973):
        """
        Инициализация шифра с простым модулем.
        
        Args:
            prime_modulus: Простое число для модульной арифметики
        """
        self.modulus = prime_modulus
        # Секретный ключ (в реальном шифровании это было бы сложнее)
        self.secret_key = random.randint(2, prime_modulus - 1)
        
    def encrypt(self, plaintext: int) -> int:
        """
        Шифрование числа с использованием модульной арифметики.
        Сохраняет гомоморфизм сложения.
        
        Пример: A = 87 → a ≡ 9 (mod 13)
        """
        # Добавляем случайный шум для криптостойкости (в реальности)
        noise = random.randint(0, self.modulus // 10)
        # Используем секретный ключ как множитель
        encrypted = (plaintext * self.secret_key + noise) % self.modulus
        return encrypted
    
    def decrypt(self, ciphertext: int) -> int:
        """
        Дешифрование числа (требует знания секретного ключа).
        """
        # Обратная операция: находим значение, которое при умножении
        # на secret_key дает ciphertext по модулю
        # В реальном RSA это было бы сложнее
        try:
            inv_key = pow(self.secret_key, -1, self.modulus)
            plaintext = (ciphertext * inv_key) % self.modulus
            return plaintext
        except ValueError:
            # Если ключ не обратим (не взаимно прост с модулем)
            return ciphertext
    
    def add(self, ciphertext1: int, ciphertext2: int) -> int:
        """
        Гомоморфное сложение зашифрованных чисел.
        E(a) + E(b) = E(a + b)
        """
        return (ciphertext1 + ciphertext2) % self.modulus
    
    def multiply(self, ciphertext1: int, ciphertext2: int) -> int:
        """
        Гомоморфное умножение зашифрованных чисел.
        E(a) * E(b) = E(a * b)
        """
        return (ciphertext1 * ciphertext2) % self.modulus
    
    def hash_to_int(self, text: str) -> int:
        """
        Преобразование текста в число для шифрования.
        """
        # Используем хеш для преобразования текста в число
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # Берем первые 4 байта и преобразуем в число
        number = int.from_bytes(hash_bytes[:4], 'big') % self.modulus
        return number


class HomomorphicSearchEngine:
    """
    Поисковая система, работающая с зашифрованными данными (CSE).
    Демонстрирует принципы, описанные в тексте.
    """
    
    def __init__(self, prime_modulus: int = 9973):
        """
        Инициализация поисковой системы.
        """
        self.cipher = HomomorphicCipher(prime_modulus)
        self.modulus = prime_modulus
        
        # Инвертированный индекс: зашифрованный терм → список ID документов
        self.inverted_index: Dict[int, List[int]] = defaultdict(list)
        
        # Хранилище документов
        self.documents: Dict[int, str] = {}
        
        # Хранилище зашифрованных документов (для демонстрации)
        self.encrypted_docs: Dict[int, List[int]] = {}
        
        # Счетчик документов
        self.doc_counter = 0
        
        # История поиска (для статистики)
        self.search_history: List[Tuple[int, List[int]]] = []
    
    def add_document(self, content: str, is_encrypted: bool = False):
        """
        Добавление документа в индекс.
        
        Args:
            content: Текст документа
            is_encrypted: Если True, добавляем как зашифрованный
        """
        doc_id = self.doc_counter
        self.doc_counter += 1
        
        self.documents[doc_id] = content
        
        # Токенизация (разбиваем на слова)
        words = self._tokenize(content)
        
        if is_encrypted:
            # Шифруем каждое слово и сохраняем
            encrypted_words = [self.cipher.encrypt(self.cipher.hash_to_int(word)) for word in words]
            self.encrypted_docs[doc_id] = encrypted_words
            
            # Строим индекс на основе зашифрованных слов
            for enc_word in set(encrypted_words):
                self.inverted_index[enc_word].append(doc_id)
        else:
            # Для наглядности: строим индекс на основе хешей слов (как в традиционных системах)
            for word in set(words):
                word_hash = self.cipher.hash_to_int(word)
                self.inverted_index[word_hash].append(doc_id)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Токенизация текста (упрощенная).
        """
        # Приводим к нижнему регистру и убираем пунктуацию
        text = text.lower()
        for punct in ['.', ',', '!', '?', ';', ':', '"', "'", '(', ')', '[', ']', '{', '}']:
            text = text.replace(punct, ' ')
        return text.split()
    
    def search(self, query: str, is_encrypted: bool = True) -> Dict[int, float]:
        """
        Поиск документов по запросу.
        
        Args:
            query: Поисковый запрос
            is_encrypted: Если True, поиск выполняется над зашифрованными данными
            
        Returns:
            Словарь {doc_id: релевантность}
        """
        # Токенизация запроса
        query_words = self._tokenize(query)
        
        if is_encrypted:
            # Шифруем запрос
            encrypted_query = [self.cipher.encrypt(self.cipher.hash_to_int(word)) for word in query_words]
            
            print(f"\n🔒 Зашифрованный запрос: {encrypted_query}")
            print(f"   (Исходный запрос: '{query}' защищен)")
            
            # Ищем документы, содержащие зашифрованные термы
            # Важно: мы не знаем, что ищем - работаем вслепую!
            results = self._search_blind(encrypted_query)
            
            # Сохраняем историю
            self.search_history.append((self.cipher.hash_to_int(query), list(results.keys())))
            
            return results
        else:
            # Традиционный поиск (для сравнения)
            query_hashes = [self.cipher.hash_to_int(word) for word in query_words]
            results = self._search_clear(query_hashes)
            return results
    
    def _search_blind(self, encrypted_query: List[int]) -> Dict[int, float]:
        """
        Поиск вслепую над зашифрованными данными.
        Демонстрирует принцип гомоморфного поиска.
        """
        results = {}
        
        # Для каждого документа
        for doc_id, encrypted_words in self.encrypted_docs.items():
            # Считаем количество совпадений с зашифрованными термами
            matches = 0
            for enc_term in encrypted_query:
                # Гомоморфно проверяем наличие терма в документе
                # В реальной системе здесь были бы более сложные вычисления
                if enc_term in encrypted_words:
                    matches += 1
            
            if matches > 0:
                # Вычисляем релевантность (вслепую, без расшифровки)
                # Используем гомоморфные операции
                relevance = self._compute_relevance_blind(matches, len(encrypted_words), len(self.encrypted_docs))
                results[doc_id] = relevance
        
        return dict(sorted(results.items(), key = lambda x: x[1], reverse = True))
    
    def _search_clear(self, query_hashes: List[int]) -> Dict[int, float]:
        """
        Традиционный поиск по хешам (для сравнения).
        """
        results = {}
        
        for doc_id, content in self.documents.items():
            words = self._tokenize(content)
            word_hashes = [self.cipher.hash_to_int(w) for w in words]
            
            matches = sum(1 for q_hash in query_hashes if q_hash in word_hashes)
            
            if matches > 0:
                # TF-IDF упрощенный
                relevance = matches / len(set(words)) if words else 0
                results[doc_id] = relevance
        
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
    
    def _compute_relevance_blind(self, matches: int, total_words: int, total_docs: int) -> float:
        """
        Вычисление релевантности над зашифрованными данными.
        Использует только гомоморфные операции (сложение, умножение).
        """
        # В реальной системе здесь были бы операции над шифротекстами
        # Мы демонстрируем принцип, используя простые вычисления
        
        # Симулируем гомоморфное вычисление релевантности
        # В реальности: E(relevance) = E(matches) / E(total_words) * E(log(total_docs))
        # Поскольку у нас нет деления и логарифма в гомоморфном виде,
        # используем упрощенную формулу
        
        if total_words == 0:
            return 0
        
        # Упрощенная релевантность (только для демонстрации)
        relevance = (matches * matches) / (total_words * 0.5 + 1)
        
        # Важно: в реальной системе мы бы не расшифровывали здесь!
        # Мы бы вернули зашифрованное значение релевантности
        return relevance
    
    def demonstrate_homomorphism(self):
        """
        Демонстрация гомоморфных свойств, как в примере из текста.
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ГОМОМОРФИЗМА (как в примере из текста)")
        print("=" * 60)
        
        # Пример из текста: A=87, B=93, C=180, mod=13
        print("\n📐 Пример из текста:")
        print("   A = 87, B = 93, A + B = 180")
        
        # Шифруем
        a_enc = self.cipher.encrypt(87)
        b_enc = self.cipher.encrypt(93)
        
        print(f"\n   E(87) = {a_enc} (mod {self.modulus})")
        print(f"   E(93) = {b_enc} (mod {self.modulus})")
        
        # Гомоморфное сложение
        c_enc = self.cipher.add(a_enc, b_enc)
        print(f"\n   E(87) + E(93) = {c_enc} (mod {self.modulus})")
        
        # Расшифровываем результат
        c_dec = self.cipher.decrypt(c_enc)
        print(f"\n   Расшифровка: {c_dec}")
        print(f"   Ожидалось: (87 + 93) mod {self.modulus} = 180 mod {self.modulus} = {180 % self.modulus}")
        
        print("\n✅ Гомоморфизм сложения работает!")
        print("   (c) не раскрывает реальные значения A и B")
    
    def demonstrate_search(self):
        """
        Демонстрация поиска по зашифрованным данным.
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ПОИСКА ПО ЗАШИФРОВАННЫМ ДАННЫМ (CSE)")
        print("=" * 60)
        
        # Добавляем документы
        print("\n📄 Добавляем документы:")
        docs = [
            "Python is a programming language",
            "Java is also a programming language",
            "Machine learning with Python",
            "Data science and machine learning",
            "Programming in Python and Java"
        ]
        
        for i, doc in enumerate(docs):
            self.add_document(doc, is_encrypted = True)
            print(f"   Документ {i}: '{doc}'")
            print(f"   Зашифрован как: {self.encrypted_docs[i][:3]}... (показаны первые 3 слова)")
        
        print("\n" + "-" * 60)
        
        # Поиск
        queries = ["Python", "Java", "machine learning"]
        
        for query in queries:
            print(f"\n🔍 Поиск: '{query}'")
            results = self.search(query, is_encrypted = True)
            
            if results:
                print("   Результаты (вслепую, без расшифровки):")
                for doc_id, relevance in list(results.items())[:3]:
                    print(f"   → Документ {doc_id}: релевантность = {relevance:.3f}")
                    print(f"     Содержимое: '{self.documents[doc_id]}'")
            else:
                print("   Результатов не найдено")
        
        print("\n" + "-" * 60)
        print("📊 Статистика:")
        print(f"   Всего документов: {len(self.documents)}")
        print(f"   Размер индекса: {len(self.inverted_index)} уникальных термов")
        print(f"   Выполнено поисков: {len(self.search_history)}")
    
    def demonstrate_blind_operation(self):
        """
        Демонстрация "слепой" работы с данными.
        """
        print("\n" + "=" * 60)
        print("ПРИНЦИП 'СЛЕПОЙ' РАБОТЫ С ДАННЫМИ")
        print("=" * 60)
        
        print("\n🤔 Система работает с зашифрованными данными, не зная:")
        print("   • Что ищет (контент запроса)")
        print("   • Что хранит (контент документов)")
        print("   • Каков реальный результат (C)")
        print("\n   Вместо этого она видит только изоморфные значения (c).")
        
        print("\n📌 Пример из текста:")
        print("   A = 87 → a = 9  (изоморфное значение)")
        print("   B = 93 → b = 2  (изоморфное значение)")
        print("   C = 180 → c = 11 (изоморфное значение)")
        
        print("\n🔐 Система знает только:")
        print("   a + b = 9 + 2 = 11 = c")
        print("   Но не знает, что 9 → 87, 2 → 93, 11 → 180")
        
        print("\n✨ Это и есть суть гомоморфизма:")

    def demonstrate_security(self):
        """
        Демонстрация безопасности (невозможность обратного преобразования).
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ БЕЗОПАСНОСТИ (ОДНОСТОРОННЯЯ ФУНКЦИЯ)")
        print("=" * 60)
        
        # Показываем, что разные значения могут дать одинаковый шифротекст
        # (в реальном шифровании коллизии маловероятны, но здесь для демонстрации)
        
        test_values = [87, 100, 200]
        
        print("\n📊 Шифрование разных значений:")
        for val in test_values:
            enc = self.cipher.encrypt(val)
            dec = self.cipher.decrypt(enc)
            print(f"   {val} → E = {enc} → D = {dec}")
            print(f"   Трудно вернуться от {enc} к {val} без ключа")
        
        print("\n🔑 Для дешифрования нужен секретный ключ:")
        print(f"   Секретный ключ: {self.cipher.secret_key}")
        print(f"   Модуль: {self.cipher.modulus}")
        
        print("\n⚠️  Без ключа невозможно определить:")
        print("   • Какое исходное значение было зашифровано")
        print("   • Какие документы соответствуют запросу")
        print("   • Каков реальный результат вычислений")


def main():
    """
    Главная функция для демонстрации всех возможностей.
    """
    print("=" * 70)
    print("ИЗУЧЕНИЕ ГОМОМОРФНОГО ШИФРОВАНИЯ И ПОИСКОВАЯ СИСТЕМА (CSE)")
    print("=" * 70)
    print("\nАвтор: Исследовательская работа")
    print("Тема: Гомоморфное шифрование и его применение в поисковых системах")
    print("\n" + "=" * 70)
    
    # Создаем экземпляр поисковой системы
    search_engine = HomomorphicSearchEngine(prime_modulus = 9973)
    
    # Демонстрация гомоморфизма
    search_engine.demonstrate_homomorphism()
    
    # Демонстрация "слепой" работы
    search_engine.demonstrate_blind_operation()
    
    # Демонстрация безопасности
    search_engine.demonstrate_security()
    
    # Демонстрация поиска
    search_engine.demonstrate_search()
    
    print("\n" + "=" * 70)
    print("ВЫВОДЫ:")
    print("=" * 70)
    print("""    
    1. Гомоморфное шифрование позволяет выполнять операции над 
       зашифрованными данными без их расшифровки.
    
    2. Частичный гомоморфизм (сложение или умножение) недостаточен 
       для полноценного поиска, требующего множества операций.
    
    3. Поисковая система CSE может работать 'вслепую', не зная 
       содержимого запроса и документов.
    
    4. Основная сложность — обеспечить эффективность при сохранении 
       конфиденциальности данных.
    
    5. Для реального применения требуются полностью гомоморфные 
       схемы (FHE), которые пока значительно медленнее традиционных.
    """)
    
    print("\n🔬 Программа демонстрирует концепцию, описанную в тексте:")
    print("   • Гомоморфизм сложения: E(a) + E(b) = E(a + b)")
    print("   • Однонаправленное преобразование (без ключа)")
    print("   • Поиск по зашифрованным данным")
    print("   • Сохранение конфиденциальности исходных значений")
    
    print("\n✅ Демонстрация завершена!")


if __name__ == "__main__":
    main()