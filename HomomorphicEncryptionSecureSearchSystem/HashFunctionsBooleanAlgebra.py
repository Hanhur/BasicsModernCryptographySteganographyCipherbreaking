# Хеш-функции и булева алгебра 
import hashlib
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
from typing import List, Set, Dict, Tuple


class SimpleCSE:
    """
    Простая реализация Cryptographic Search Engine (CSE)
    на основе принципов из статьи Cryptolab
    """
    
    def __init__(self, password: str = "master_key_123"):
        """
        Инициализация поисковой системы
        
        Args:
            password: Пароль для генерации ключей шифрования
        """
        self.password = password
        self.documents = {}  # {doc_id: encrypted_content}
        self.index = {}      # {хеш_слова: {doc_id: set(позиции)}}
        self.doc_metadata = {}  # {doc_id: {original_name, ...}}
        self.fernet_key = None
        self._generate_key()
        
    def _generate_key(self):
        """Генерация ключа шифрования на основе пароля"""
        salt = b'cse_salt_2026'  # В реальной системе соль должна быть случайной и храниться отдельно
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = 100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        self.fernet_key = key
        self.cipher = Fernet(key)
        
    def _hash_word(self, word: str) -> str:
        """
        Хеширование слова для индексации
        
        Args:
            word: Слово для хеширования
            
        Returns:
            Хеш слова в виде шестнадцатеричной строки
        """
        # Нормализация: приводим к нижнему регистру и удаляем пробелы
        normalized = word.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Разбиение текста на токены (слова)
        
        Args:
            text: Текст для токенизации
            
        Returns:
            Список слов
        """
        # Удаляем знаки препинания и разбиваем по пробелам
        words = re.findall(r'\b[а-яa-z]+\b', text.lower())
        return words
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """
        Добавление документа в систему с индексацией
        
        Args:
            doc_id: Уникальный идентификатор документа
            content: Содержимое документа
            metadata: Дополнительная информация о документе
        """
        if metadata is None:
            metadata = {}
        
        # Шифруем содержимое
        encrypted_content = self.cipher.encrypt(content.encode())
        self.documents[doc_id] = encrypted_content
        self.doc_metadata[doc_id] = metadata
        
        # Индексируем все слова в документе
        words = self._tokenize(content)
        word_positions = {}
        
        for idx, word in enumerate(words):
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append(idx)
        
        # Для каждого уникального слова добавляем в индекс
        for word, positions in word_positions.items():
            word_hash = self._hash_word(word)
            
            if word_hash not in self.index:
                self.index[word_hash] = {}
            
            if doc_id not in self.index[word_hash]:
                self.index[word_hash][doc_id] = set()
            
            self.index[word_hash][doc_id].update(positions)
    
    def _search_word(self, word: str) -> Set[str]:
        """
        Поиск документов, содержащих конкретное слово
        
        Args:
            word: Слово для поиска
            
        Returns:
            Множество ID документов
        """
        word_hash = self._hash_word(word)
        if word_hash in self.index:
            return set(self.index[word_hash].keys())
        return set()
    
    def search(self, query: str) -> List[Tuple[str, bytes, Dict]]:
        """
        Выполнение булевого запроса с поддержкой операторов И, ИЛИ, НЕ
        
        Args:
            query: Запрос в формате "слово1 И слово2 НЕ слово3"
            
        Returns:
            Список кортежей (doc_id, encrypted_content, metadata)
        """
        # Разбираем запрос на части
        query = query.lower()
        
        # Заменяем логические операторы на их символьные представления
        # для упрощения разбора
        query = query.replace(' и ', ' AND ')
        query = query.replace(' or ', ' OR ')
        query = query.replace(' не ', ' NOT ')
        query = query.replace(' nor ', ' NOT ')
        query = query.replace(' and ', ' AND ')
        query = query.replace(' or ', ' OR ')
        query = query.replace(' not ', ' NOT ')
        
        # Разбиваем на токены, сохраняя операторы
        tokens = []
        current = []
        i = 0
        while i < len(query):
            if query[i:i + 5] == ' AND ':
                if current:
                    tokens.append(' '.join(current).strip())
                    current = []
                tokens.append('AND')
                i += 5
            elif query[i:i + 4] == ' OR ':
                if current:
                    tokens.append(' '.join(current).strip())
                    current = []
                tokens.append('OR')
                i += 4
            elif query[i:i + 5] == ' NOT ':
                if current:
                    tokens.append(' '.join(current).strip())
                    current = []
                tokens.append('NOT')
                i += 5
            else:
                current.append(query[i])
                i += 1
        if current:
            tokens.append(' '.join(current).strip())
        
        # Упрощаем: если нет операторов, считаем это AND
        if not any(op in tokens for op in ['AND', 'OR', 'NOT']):
            words = self._tokenize(query)
            result_set = None
            for word in words:
                docs = self._search_word(word)
                if result_set is None:
                    result_set = docs
                else:
                    result_set = result_set & docs  # AND
            if result_set is None:
                result_set = set()
        else:
            # Парсим и выполняем булево выражение
            result_set = self._evaluate_boolean_expression(tokens)
        
        # Возвращаем результаты
        results = []
        for doc_id in sorted(result_set):
            if doc_id in self.documents:
                results.append((
                    doc_id,
                    self.documents[doc_id],
                    self.doc_metadata.get(doc_id, {})
                ))
        
        return results
    
    def _evaluate_boolean_expression(self, tokens: List[str]) -> Set[str]:
        """
        Вычисление булевого выражения из списка токенов
        
        Args:
            tokens: Список токенов (слова и операторы)
            
        Returns:
            Множество ID документов
        """
        # Приводим к постфиксной записи (обратная польская нотация) для простоты
        # Но для демонстрации реализуем простой парсинг слева направо
        
        # Шаг 1: Инициализация
        i = 0
        result = None
        current_op = None
        current_not = False
        
        while i < len(tokens):
            token = tokens[i]
            
            if token in ['AND', 'OR', 'NOT']:
                # Сохраняем оператор
                current_op = token
                i += 1
                
                # Если оператор NOT, применяем его к следующему операнду
                if token == 'NOT':
                    if i < len(tokens):
                        next_token = tokens[i]
                        # Ищем документы с этим словом
                        docs = self._search_word(next_token)
                        # Инвертируем относительно всех документов
                        all_docs = set(self.documents.keys())
                        docs = all_docs - docs
                        result = self._apply_operator(result, docs, 'AND')  # NOT работает как AND с отрицанием
                        i += 1
                    continue
                
                # Для AND и OR ждем следующий операнд
                if i < len(tokens):
                    next_token = tokens[i]
                    # Проверяем, не является ли следующий токен оператором
                    if next_token in ['AND', 'OR', 'NOT']:
                        # Если да, то это ошибка в запросе, пропускаем
                        i += 1
                        continue
                    
                    # Получаем документы для следующего слова
                    docs = self._search_word(next_token)
                    
                    # Применяем оператор
                    result = self._apply_operator(result, docs, current_op)
                    i += 1
            else:
                # Это слово без оператора - начинаем с него
                docs = self._search_word(token)
                if result is None:
                    result = docs
                i += 1
        
        if result is None:
            result = set()
        
        return result
    
    def _apply_operator(self, left: Set[str], right: Set[str], operator: str) -> Set[str]:
        """
        Применение бинарного оператора к двум множествам
        
        Args:
            left: Левое множество
            right: Правое множество
            operator: Оператор (AND, OR, NOT)
            
        Returns:
            Результат операции
        """
        if left is None:
            return right
        
        if operator == 'AND':
            return left & right
        elif operator == 'OR':
            return left | right
        elif operator == 'NOT':
            return left - right
        else:
            return left
    
    def decrypt_document(self, doc_id: str) -> str:
        """
        Расшифровка документа
        
        Args:
            doc_id: ID документа
            
        Returns:
            Расшифрованное содержимое
        """
        if doc_id in self.documents:
            decrypted = self.cipher.decrypt(self.documents[doc_id])
            return decrypted.decode()
        return None
    
    def print_index_stats(self):
        """Вывод статистики по индексу"""
        print(f"Всего документов: {len(self.documents)}")
        print(f"Уникальных хешей слов: {len(self.index)}")
        
        total_entries = sum(len(docs) for docs in self.index.values())
        print(f"Всего записей в индексе: {total_entries}")


def demo_cse():
    """
    Демонстрация работы CSE с примерами из текста
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ CSE (Cryptographic Search Engine)")
    print("=" * 60)
    
    # Создаем экземпляр поисковой системы
    cse = SimpleCSE("cryptolab_key_2026")
    
    # Подготавливаем тестовые документы (главы книги)
    documents = {
        "chapter1": """
        Введение в криптографию. Основные понятия и определения.
        Хеш-функции используются для создания цифровых подписей.
        Булева алгебра применяется в криптографических алгоритмах.
        """,
        
        "chapter2": """
        Булева алгебра и логические операторы. Операции И, ИЛИ, НЕ.
        В этой главе рассматриваются основные понятия булевой алгебры.
        Здесь нет хеш-функций, только булева логика.
        """,
        
        "chapter3": """
        Хеш-функции и их применение. Хеш-функции в криптографии.
        Алгоритмы хеширования SHA-256 и MD5.
        Булева алгебра не упоминается в этой главе.
        """,
        
        "chapter4": """
        Продвинутые хеш-функции. Хеш-функции и булева алгебра.
        В этом разделе рассматривается интеграция хеш-функций с булевыми операциями.
        Комбинированное использование хешей и булевой алгебры.
        """
    }
    
    # Добавляем документы в систему
    print("\n📚 Добавление документов в CSE...")
    for doc_id, content in documents.items():
        cse.add_document(
            doc_id, 
            content, 
            {"title": f"Глава {doc_id[-1]}", "author": "Cryptolab"}
        )
    print(f"✅ Добавлено {len(documents)} документов")
    
    # Показываем статистику индекса
    print("\n📊 Статистика индекса:")
    cse.print_index_stats()
    
    # Функция для выполнения поиска и вывода результатов
    def perform_search(query: str, description: str):
        print(f"\n{'=' * 60}")
        print(f"🔍 ПОИСК: {description}")
        print(f"   Запрос: [{query}]")
        print(f"{'=' * 60}")
        
        results = cse.search(query)
        
        if not results:
            print("❌ Результатов не найдено")
            return
        
        print(f"✅ Найдено документов: {len(results)}")
        for doc_id, encrypted, metadata in results:
            print(f"\n📄 Документ: {doc_id}")
            print(f"   Метаданные: {metadata}")
            
            # Расшифровываем и показываем первые 150 символов
            decrypted = cse.decrypt_document(doc_id)
            if decrypted:
                preview = decrypted[:150].replace('\n', ' ')
                if len(decrypted) > 150:
                    preview += "..."
                print(f"   Содержимое: {preview}")
    
    # Выполняем поисковые запросы из текста
    perform_search(
        "хеш-функции И булева И алгебра",
        "Поиск всех трех терминов вместе (AND)"
    )
    
    perform_search(
        "булева И алгебра НЕ хеш-функции",
        "Булева алгебра без хеш-функций (AND + NOT)"
    )
    
    perform_search(
        "хеш-функции ИЛИ булева",
        "Поиск любого из двух терминов (OR)"
    )
    
    # Дополнительные тесты
    perform_search(
        "криптография",
        "Одиночное ключевое слово"
    )
    
    perform_search(
        "хеш-функции И булева",
        "Два термина через AND"
    )
    
    print("\n" + "=" * 60)
    print("✅ Демонстрация завершена")
    print("=" * 60)


if __name__ == "__main__":
    # Устанавливаем зависимости (если не установлены)
    try:
        import cryptography
    except ImportError:
        print("Установка необходимых зависимостей...")
        os.system("pip install cryptography")
        print("Зависимости установлены. Перезапустите программу.")
        exit()
    
    demo_cse()