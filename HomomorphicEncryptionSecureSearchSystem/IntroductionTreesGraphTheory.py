# Введение в деревья — теория графов
"""
Программа для работы с древовидными графами и префиксными кодами
на основе текста из главы о теории графов и коде Хаффмана.
Не использует numpy - только стандартные библиотеки Python.
"""

from collections import Counter, defaultdict
import heapq
import sys


class Node:
    """
    Класс, представляющий вершину (узел) дерева.
    """
    def __init__(self, value = None, frequency = 0):
        self.value = value          # Символ (буква) или None для внутренних узлов
        self.frequency = frequency  # Частота встречаемости
        self.left = None            # Левое поддерево (код 0)
        self.right = None           # Правое поддерево (код 1)
        self.parent = None          # Ссылка на родителя (для обратного хода)
    
    def is_leaf(self):
        """Проверка, является ли узел листом (конечной точкой)."""
        return self.left is None and self.right is None
    
    def __lt__(self, other):
        """Метод для сравнения узлов в куче (по частоте)."""
        return self.frequency < other.frequency
    
    def __eq__(self, other):
        """Метод для сравнения узлов на равенство."""
        if other is None:
            return False
        return self.frequency == other.frequency and self.value == other.value


class HuffmanTree:
    """
    Класс для построения и работы с деревом Хаффмана.
    """
    def __init__(self, text = None):
        self.root = None
        self.codes = {}          # Словарь: символ -> бинарный код
        self.reverse_codes = {}  # Словарь: бинарный код -> символ
        self.text = text
        self.encoded_text = ""
        
        if text:
            self.build_tree(text)
    
    def build_tree(self, text):
        """
        Построение дерева Хаффмана на основе частот символов.
        """
        # 1. Подсчет частот
        frequency = Counter(text)
        print(f"\n[1] Подсчет частот символов:")
        for char, freq in sorted(frequency.items()):
            print(f"    '{char}': {freq}")
        
        # 2. Создание начальной кучи из узлов
        heap = [Node(char, freq) for char, freq in frequency.items()]
        heapq.heapify(heap)
        
        # 3. Построение дерева (объединение двух самых редких узлов)
        print(f"\n[2] Построение дерева Хаффмана:")
        step = 1
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Создаем родительский узел с суммой частот
            parent = Node(frequency = left.frequency + right.frequency)
            parent.left = left
            parent.right = right
            left.parent = parent
            right.parent = parent
            
            heapq.heappush(heap, parent)
            
            print(f"    Шаг {step}: объединение '{left.value or 'внутр'}' (частота {left.frequency}) "
                  f"и '{right.value or 'внутр'}' (частота {right.frequency}) "
                  f"-> частота {parent.frequency}")
            step += 1
        
        self.root = heap[0]
        print(f"\n    Корень дерева создан (частота = {self.root.frequency})")
        
        # 4. Генерация префиксных кодов
        self.codes = {}
        self._generate_codes(self.root, "")
        self.reverse_codes = {code: char for char, code in self.codes.items()}
        
        print(f"\n[3] Сгенерированные префиксные коды:")
        for char, code in sorted(self.codes.items()):
            print(f"    '{char}': {code}")
        
        # 5. Кодирование текста
        self.encoded_text = self.encode(text)
        print(f"\n[4] Кодирование текста:")
        print(f"    Исходный текст: '{text}'")
        print(f"    Закодированная строка: {self.encoded_text}")
        
        # 6. Декодирование для проверки
        decoded = self.decode(self.encoded_text)
        print(f"    Декодированная строка: '{decoded}'")
        print(f"    Совпадение с исходной: {'ДА' if decoded == text else 'НЕТ'}")
    
    def _generate_codes(self, node, current_code):
        """
        Рекурсивный обход дерева для генерации префиксных кодов.
        Левый потомок = 0, правый потомок = 1.
        """
        if node is None:
            return
        
        if node.is_leaf():
            self.codes[node.value] = current_code
        else:
            self._generate_codes(node.left, current_code + "0")
            self._generate_codes(node.right, current_code + "1")
    
    def encode(self, text):
        """
        Кодирование текста в бинарную строку.
        """
        result = ""
        for char in text:
            if char in self.codes:
                result += self.codes[char]
            else:
                raise ValueError(f"Символ '{char}' не найден в дереве Хаффмана")
        return result
    
    def decode(self, encoded_text):
        """
        Декодирование бинарной строки обратно в текст.
        """
        result = ""
        current = self.root
        
        for bit in encoded_text:
            if bit == '0':
                current = current.left
            elif bit == '1':
                current = current.right
            else:
                raise ValueError(f"Некорректный бит: '{bit}'")
            
            # Если достигли листа, добавляем символ и возвращаемся к корню
            if current.is_leaf():
                result += current.value
                current = self.root
        
        return result
    
    def print_tree(self):
        """
        Визуализация дерева в консоли.
        """
        print("\n" + "=" * 60)
        print("ВИЗУАЛИЗАЦИЯ ДЕРЕВА")
        print("=" * 60)
        self._print_tree_recursive(self.root, "", True)
    
    def _print_tree_recursive(self, node, prefix, is_left):
        """
        Рекурсивный вывод дерева с ASCII-графикой.
        """
        if node is None:
            return
        
        # Определяем метку узла
        if node.is_leaf():
            label = f"'{node.value}' (частота: {node.frequency})"
        else:
            label = f"внутр (частота: {node.frequency})"
        
        # Вывод текущего узла
        if node == self.root:
            print(f"┌─ Корень: {label}")
        else:
            connector = "┌── " if is_left else "└── "
            print(prefix + connector + label)
        
        # Рекурсивный обход детей
        if node.left or node.right:
            # Для левого потомка
            if node.left:
                self._print_tree_recursive(
                    node.left, 
                    prefix + ("│   " if not is_left else "    "), 
                    True
                )
            # Для правого потомка
            if node.right:
                self._print_tree_recursive(
                    node.right, 
                    prefix + ("    " if is_left else "│   "), 
                    False
                )
    
    def show_prefix_example(self):
        """
        Демонстрация префиксного кодирования, как в таблице 8.1.
        """
        print("\n" + "=" * 60)
        print("ПРИМЕР ПРЕФИКСНОГО КОДИРОВАНИЯ")
        print("=" * 60)
        
        # Используем пример из книги: a, b, c, d, e, f
        example_chars = ['a', 'b', 'c', 'd', 'e', 'f']
        example_codes = {
            'a': '0', 
            'b': '101', 
            'c': '100', 
            'd': '111', 
            'e': '1101', 
            'f': '1100'
        }
        
        print("\nТаблица префиксных кодов из книги (табл. 8.1):")
        print("-" * 40)
        print("Буква | Код")
        print("-" * 40)
        for char in example_chars:
            print(f"  {char}   | {example_codes[char]}")
        
        # Кодирование строки "abc"
        test_str = "abc"
        encoded = ""
        for char in test_str:
            encoded += example_codes[char] + "·"
        encoded = encoded.rstrip('·')
        
        print("-" * 40)
        print(f"\nКодирование строки '{test_str}':")
        print(f"  {test_str} -> {encoded}")
        
        # Проверка уникальности
        print("\nПроверка префиксности:")
        print("-" * 40)
        codes_list = list(example_codes.values())
        is_prefix_free = True
        for i, code1 in enumerate(codes_list):
            for j, code2 in enumerate(codes_list):
                if i != j and code1.startswith(code2):
                    print(f"  ВНИМАНИЕ: '{code1}' начинается с '{code2}'")
                    is_prefix_free = False
        if is_prefix_free:
            print("  ✓ Все коды префиксно-свободны (ни один код не является префиксом другого)")
        
        print("\nПрефиксные коды обеспечивают:")
        print("  • Однозначное декодирование")
        print("  • Эффективный поиск по префиксу")
        print("  • Аналогия с телефонными индексами (001 - Америка, 002 - Африка и т.д.)")


class TrieNode:
    """
    Узел для префиксного дерева (Trie) - используется для поиска.
    """
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.value = None


class PrefixTree:
    """
    Реализация префиксного дерева (Trie) для эффективного поиска.
    Как в примере с телефонными индексами.
    """
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, value = None):
        """
        Вставка слова в префиксное дерево.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.value = value if value is not None else word
    
    def search(self, word):
        """
        Поиск точного слова в префиксном дереве.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.value if node.is_end_of_word else None
    
    def starts_with(self, prefix):
        """
        Поиск всех слов с заданным префиксом.
        Как поиск по коду страны/региона.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Сбор всех слов из поддерева
        results = []
        self._collect_words(node, prefix, results)
        return results
    
    def _collect_words(self, node, current_prefix, results):
        """
        Рекурсивный сбор всех слов из поддерева.
        """
        if node.is_end_of_word:
            results.append(current_prefix)
        
        for char, child in node.children.items():
            self._collect_words(child, current_prefix + char, results)
    
    def print_tree(self):
        """
        Визуализация префиксного дерева.
        """
        print("\nПрефиксное дерево (Trie):")
        self._print_trie(self.root, "")
    
    def _print_trie(self, node, indent):
        """
        Рекурсивный вывод префиксного дерева.
        """
        for char, child in node.children.items():
            marker = "*" if child.is_end_of_word else ""
            print(f"{indent}└── {char}{marker}")
            self._print_trie(child, indent + "    ")


def demonstrate_phone_index():
    """
    Демонстрация аналогии с телефонными индексами.
    """
    print("\n" + "=" * 60)
    print("ТЕЛЕФОННЫЕ ИНДЕКСЫ И ПРЕФИКСНЫЕ КОДЫ")
    print("=" * 60)
    
    trie = PrefixTree()
    
    # Добавляем индексы регионов (как в примере)
    trie.insert("001", "Северная Америка")
    trie.insert("001-415", "Сан-Франциско, Калифорния")
    trie.insert("001-415-555", "Конкретный район Сан-Франциско")
    trie.insert("002", "Африка")
    trie.insert("003", "Европа")
    trie.insert("003-44", "Великобритания")
    trie.insert("003-44-20", "Лондон")
    trie.insert("004", "Азия")
    
    print("\nСтруктура телефонных индексов:")
    print("-" * 40)
    trie.print_tree()
    
    print("\nПоиск по префиксам:")
    print("-" * 40)
    
    test_prefixes = ["001", "001-415", "003", "003-44"]
    for prefix in test_prefixes:
        results = trie.starts_with(prefix)
        if results:
            print(f"\nПрефикс '{prefix}':")
            for result in results:
                info = trie.search(result)
                print(f"  • {result} -> {info}")
    
    print("\nКак это работает:")
    print("  • 001 -> сужает поиск до Северной Америки")
    print("  • 001-415 -> сужает до Сан-Франциско")
    print("  • Аналогично работают префиксные коды Хаффмана")


def main():
    """
    Главная функция для демонстрации работы программы.
    """
    print("\n" + "=" * 60)
    print("ПРОГРАММА ДЛЯ РАБОТЫ С ДРЕВОВИДНЫМИ ГРАФАМИ")
    print("НА ОСНОВЕ ТЕОРИИ ПРЕФИКСНЫХ КОДОВ")
    print("=" * 60)
    print("\nАвтор: Реализация на основе текста из книги")
    print("Тема: Древовидные графы, кодирование Хаффмана, префиксные коды")
    
    # ========== ЧАСТЬ 1: КОД ХАФФМАНА ==========
    print("\n" + "=" * 60)
    print("ЧАСТЬ 1: КОДИРОВАНИЕ ХАФФМАНА")
    print("=" * 60)
    
    # Пример из текста: "aabbc" или более осмысленный текст
    test_text = "aabbc"
    print(f"\nИсходный текст для кодирования: '{test_text}'")
    
    huffman = HuffmanTree(test_text)
    huffman.print_tree()
    
    # ========== ЧАСТЬ 2: ПРИМЕР ИЗ КНИГИ ==========
    print("\n" + "=" * 60)
    print("ЧАСТЬ 2: ПРИМЕР ИЗ ТЕКСТА КНИГИ")
    print("=" * 60)
    huffman.show_prefix_example()
    
    # ========== ЧАСТЬ 3: ТЕЛЕФОННЫЕ ИНДЕКСЫ ==========
    demonstrate_phone_index()
    
    # ========== ЧАСТЬ 4: ПОЛНЫЙ ПРИМЕР ==========
    print("\n" + "=" * 60)
    print("ЧАСТЬ 4: ПОЛНЫЙ ПРИМЕР РАБОТЫ")
    print("=" * 60)
    
    # Более сложный пример
    full_text = "это пример текста для кодирования по хаффману"
    print(f"\nИсходный текст: '{full_text}'")
    print(f"Длина: {len(full_text)} символов")
    
    huffman_full = HuffmanTree(full_text)
    
    # Сравнение с фиксированным кодированием (ASCII)
    ascii_bits = len(full_text) * 8  # 8 бит на символ
    huffman_bits = len(huffman_full.encoded_text)
    compression_ratio = (1 - huffman_bits / ascii_bits) * 100
    
    print("\nСравнение эффективности:")
    print("-" * 40)
    print(f"  Кодирование ASCII: {ascii_bits} бит")
    print(f"  Кодирование Хаффмана: {huffman_bits} бит")
    print(f"  Сжатие: {compression_ratio:.1f}%")
    
    # Декодирование
    decoded_full = huffman_full.decode(huffman_full.encoded_text)
    print(f"\nДекодирование: '{decoded_full}'")
    print(f"  Успешно: {'ДА' if decoded_full == full_text else 'НЕТ'}")
    
    # ========== ЗАКЛЮЧЕНИЕ ==========
    print("\n" + "=" * 60)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 60)
    print("\nДревовидные графы и префиксные коды применяются для:")
    print("  • Сжатия данных без потерь (код Хаффмана)")
    print("  • Поиска и индексации данных (поисковые системы)")
    print("  • Телефонных индексов и маршрутизации")
    print("  • Эффективного хранения зашифрованных данных")
    print("\nКлючевые свойства префиксных кодов:")
    print("  • Однозначное декодирование")
    print("  • Оптимальность (минимальная средняя длина кода)")
    print("  • Быстрый поиск по префиксу за O(длина_префикса)")
    
    print("\n" + "=" * 60)
    print("Программа завершена.")
    print("=" * 60)


if __name__ == "__main__":
    main()