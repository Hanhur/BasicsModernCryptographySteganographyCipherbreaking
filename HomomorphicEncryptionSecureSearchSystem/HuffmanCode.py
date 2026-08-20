# Код Хаффмана
from collections import Counter
import heapq

class HuffmanNode:
    """Узел дерева Хаффмана"""
    def __init__(self, char, freq):
        self.char = char          # Символ (буква)
        self.freq = freq          # Частота
        self.left = None          # Левый потомок (0)
        self.right = None         # Правый потомок (1)
    
    def __lt__(self, other):
        # Для корректной работы heapq при сравнении узлов
        if self.freq == other.freq:
            # Если частоты равны, сравниваем по символу (для детерминизма)
            return self.char < other.char if self.char and other.char else False
        return self.freq < other.freq
    
    def __repr__(self):
        return f"Node({self.char}, {self.freq})"

def build_huffman_tree(char_freq):
    """
    Построение дерева Хаффмана по словарю {символ: частота}
    Возвращает корень дерева
    """
    # Создаём приоритетную очередь (кучу) из узлов
    heap = []
    for char, freq in char_freq.items():
        heapq.heappush(heap, HuffmanNode(char, freq))
    
    # Объединяем узлы, пока не останется один (корень)
    while len(heap) > 1:
        # Извлекаем два узла с наименьшей частотой
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Создаём родительский узел (без символа, только частота = сумма)
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        
        # Добавляем обратно в кучу
        heapq.heappush(heap, parent)
    
    # Возвращаем корень дерева
    return heap[0] if heap else None

def generate_codes(node, prefix = "", codebook = None):
    """
    Рекурсивный обход дерева для генерации кодов
    Возвращает словарь {символ: двоичный_код}
    """
    if codebook is None:
        codebook = {}
    
    # Если узел листовой (содержит символ)
    if node.char is not None:
        codebook[node.char] = prefix
    else:
        # Идём влево (добавляем 0)
        if node.left:
            generate_codes(node.left, prefix + "0", codebook)
        # Идём вправо (добавляем 1)
        if node.right:
            generate_codes(node.right, prefix + "1", codebook)
    
    return codebook

def encode_text(text, codebook):
    """
    Кодирование текста в битовую строку
    """
    return ''.join(codebook[char] for char in text)

def decode_text(encoded, root):
    """
    Декодирование битовой строки в текст
    """
    decoded = []
    current = root
    
    for bit in encoded:
        if bit == '0':
            current = current.left
        else:  # bit == '1'
            current = current.right
        
        # Если достигли листа, сохраняем символ и возвращаемся к корню
        if current.char is not None:
            decoded.append(current.char)
            current = root
    
    return ''.join(decoded)

def huffman_compress(text):
    """
    Основная функция сжатия текста методом Хаффмана
    Возвращает: (закодированная_строка, словарь_кодов, корень_дерева)
    """
    if not text:
        return "", {}, None
    
    # 1. Подсчёт частот символов
    freq = Counter(text)
    print(f"Частоты символов: {dict(freq)}")
    
    # 2. Построение дерева
    root = build_huffman_tree(freq)
    
    # 3. Генерация кодов
    codes = generate_codes(root)
    print(f"Коды Хаффмана: {codes}")
    
    # 4. Кодирование текста
    encoded = encode_text(text, codes)
    
    # 5. Проверка (опционально)
    decoded = decode_text(encoded, root)
    print(f"Декодировано: {decoded}")
    
    return encoded, codes, root

def calculate_compression_stats(text, codes):
    """
    Расчёт статистики сжатия
    """
    original_bits = len(text) * 8  # ASCII (8 бит на символ)
    
    # Подсчёт бит по формуле: сумма (частота * длина_кода)
    freq = Counter(text)
    compressed_bits = sum(freq[char] * len(codes[char]) for char in freq)
    
    # Средняя длина кода
    total_chars = len(text)
    avg_length = compressed_bits / total_chars
    
    return {
        'original_bits': original_bits,
        'compressed_bits': compressed_bits,
        'savings': original_bits - compressed_bits,
        'compression_ratio': original_bits / compressed_bits if compressed_bits > 0 else 0,
        'avg_code_length': avg_length
    }

# ==================== ОСНОВНАЯ ПРОГРАММА ====================

if __name__ == "__main__":
    # Текст из вашего примера (буквы с их частотами)
    # Создаём текст, в котором буквы встречаются с заданными частотами
    text = "a" * 20 + "o" * 28 + "q" * 4 + "u" * 17 + "y" * 12 + "z" * 7
    print(f"Исходный текст (длина {len(text)} символов):")
    print(f"{text[:50]}... (показано первых 50 символов)\n")
    
    # Сжатие
    encoded, codes, root = huffman_compress(text)
    
    print(f"\nЗакодированная строка (первые 100 бит):")
    print(f"{encoded[:100]}...")
    print(f"Общая длина: {len(encoded)} бит\n")
    
    # Статистика
    stats = calculate_compression_stats(text, codes)
    print("=== СТАТИСТИКА СЖАТИЯ ===")
    print(f"Исходный размер (ASCII): {stats['original_bits']} бит")
    print(f"Сжатый размер:          {stats['compressed_bits']} бит")
    print(f"Экономия:               {stats['savings']} бит")
    print(f"Коэффициент сжатия:     {stats['compression_ratio']:.2f}x")
    print(f"Средняя длина кода:     {stats['avg_code_length']:.2f} бит/символ")
    
    # Демонстрация декодирования
    print("\n=== ПРОВЕРКА ДЕКОДИРОВАНИЯ ===")
    decoded = decode_text(encoded, root)
    print(f"Декодированный текст (первые 50 символов): {decoded[:50]}...")
    print(f"Декодирование {'✓ успешно' if decoded == text else '✗ ошибка'}")
    
    # Отображение дерева (для наглядности)
    print("\n=== СТРУКТУРА ДЕРЕВА ===")
    print("(числа в скобках - частоты, None - внутренний узел)")
    
    def print_tree(node, level=0):
        if node:
            indent = "  " * level
            if node.char is not None:
                print(f"{indent}├── {node.char} ({node.freq})")
            else:
                print(f"{indent}├── (internal, {node.freq})")
                if node.left:
                    print_tree(node.left, level + 1)
                if node.right:
                    print_tree(node.right, level + 1)
    
    print_tree(root)
    
    # Дополнительно: кодирование произвольного текста
    print("\n=== КОДИРОВАНИЕ ПРОИЗВОЛЬНОГО ТЕКСТА ===")
    test_text = "you"
    print(f"Текст: '{test_text}'")
    
    # Для нового текста нужно перестроить дерево (или использовать существующее)
    if set(test_text).issubset(set(codes.keys())):
        test_encoded = encode_text(test_text, codes)
        print(f"Закодировано: {test_encoded}")
        test_decoded = decode_text(test_encoded, root)
        print(f"Декодировано: '{test_decoded}'")
    else:
        print(f"Текст содержит символы не из исходного алфавита: {set(test_text) - set(codes.keys())}")
        print("Для произвольного текста нужно перестроить дерево")