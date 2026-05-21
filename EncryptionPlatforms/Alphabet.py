# 1. Алфавит
"""
Программа, реализующая понятия:
- алфавит (набор допустимых символов)
- текст как последовательность знаков
- выделение k-граф (диграфов, триграфов и т.д.)
- дополнение последнего k-графа до нужной длины
- разбиение текста на блоки фиксированной длины (в единицах текста)
"""

from typing import List, Tuple, Union

class Alphabet:
    """Класс, представляющий алфавит."""
    
    def __init__(self, symbols: str):
        """
        Инициализация алфавита.
        
        Args:
            symbols: строка, содержащая все допустимые символы алфавита.
        """
        self.symbols = symbols
        self._set = set(symbols)
    
    def contains(self, symbol: str) -> bool:
        """Проверяет, принадлежит ли символ алфавиту."""
        return symbol in self._set
    
    def __len__(self):
        return len(self.symbols)
    
    def __repr__(self):
        return f"Alphabet({self.symbols[:50]}...)" if len(self.symbols) > 50 else f"Alphabet({self.symbols})"


class Text:
    """Класс, представляющий текст как последовательность знаков."""
    
    def __init__(self, content: str, alphabet: Alphabet = None):
        """
        Инициализация текста.
        
        Args:
            content: строка с содержимым текста.
            alphabet: алфавит (если не задан, будет создан автоматически из символов текста).
        """
        self.content = content
        
        if alphabet is None:
            # Создаём алфавит из уникальных символов текста
            unique_symbols = ''.join(sorted(set(content)))
            self.alphabet = Alphabet(unique_symbols)
        else:
            self.alphabet = alphabet
            # Проверяем, что все символы текста принадлежат алфавиту
            for ch in content:
                if not self.alphabet.contains(ch):
                    raise ValueError(f"Символ '{ch}' не принадлежит алфавиту")
    
    def __len__(self):
        return len(self.content)
    
    def __getitem__(self, index):
        return self.content[index]
    
    def __repr__(self):
        preview = self.content[:50]
        if len(self.content) > 50:
            preview += "..."
        return f"Text('{preview}')"
    
    def get_kgrams(self, k: int, pad_symbol: str = None) -> List[str]:
        """
        Получение списка k-графов (последовательных k знаков).
        
        Args:
            k: длина k-графа (k >= 1)
            pad_symbol: символ для дополнения последнего неполного k-графа. Если None, то неполный k-граф отбрасывается.
        
        Returns:
            Список строк, каждая из которых является k-графом.
        """
        if k < 1:
            raise ValueError("k должно быть >= 1")
        
        n = len(self.content)
        kgrams = []
        
        for i in range(n - k + 1):
            kgrams.append(self.content[i:i + k])
        
        # Обработка последнего неполного k-графа
        remainder = n % k
        if remainder != 0 and pad_symbol is not None:
            last_start = n - remainder
            last_kgram = self.content[last_start:]
            # Дополняем до длины k
            last_kgram += pad_symbol * (k - remainder)
            kgrams.append(last_kgram)
        
        return kgrams
    
    def split_into_blocks(self, block_length: int, unit: str = "char") -> List[Union[str, List[str]]]:
        """
        Разбиение текста на блоки фиксированной длины.
        
        Args:
            block_length: длина блока в единицах текста.
            unit: тип единицы - 'char' (отдельные знаки) или 'kgram' (k-графы, но для этого используйте get_kgrams сначала)
        
        Returns:
            Список блоков.
        """
        if block_length <= 0:
            raise ValueError("Длина блока должна быть положительной")
        
        if unit == "char":
            # Разбиение по символам
            chars = list(self.content)
            blocks = []
            for i in range(0, len(chars), block_length):
                block = chars[i:i + block_length]
                blocks.append(''.join(block))
            return blocks
        else:
            raise ValueError("Поддерживается только unit='char'. Для k-графов сначала вызовите get_kgrams().")
    
    def get_ngrams_as_units(self, k: int, block_size: int = None, pad_symbol: str = None) -> Tuple[List[str], List[List[str]]]:
        """
        Комбинированный метод: сначала получаем k-графы, затем разбиваем их на блоки.
        
        Args:
            k: размер k-графа.
            block_size: количество k-графов в блоке (если None, то блоки не формируются).
            pad_symbol: символ для дополнения последнего k-графа.
        
        Returns:
            (список k-графов, список блоков из k-графов)
        """
        kgrams = self.get_kgrams(k, pad_symbol)
        
        if block_size is None:
            return kgrams, []
        
        blocks = []
        for i in range(0, len(kgrams), block_size):
            blocks.append(kgrams[i:i+block_size])
        
        return kgrams, blocks


# Пример использования и демонстрация
def demo():
    # 1. Русский алфавит (33 буквы + пробел)
    russian_alphabet_str = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "
    russian_alphabet = Alphabet(russian_alphabet_str)  # Создаём объект Alphabet
    
    # 2. Создаём текст
    text_content = "ПРИВЕТ МИР"
    text = Text(text_content, russian_alphabet)
    
    print("=" * 60)
    print("Демонстрация работы программы")
    print("=" * 60)
    print(f"Текст: '{text.content}'")
    print(f"Длина текста: {len(text)} знаков")
    print(f"Алфавит (первые 10 символов): {russian_alphabet.symbols[:10]}...")
    
    # 3. Диграфы (k=2)
    print("\n--- Диграфы (k=2, без дополнения) ---")
    digraphs = text.get_kgrams(2)
    print(digraphs)
    
    # 4. Триграфы (k=3) с дополнением
    print("\n--- Триграфы (k=3, дополнение символом '#') ---")
    trigrams = text.get_kgrams(3, pad_symbol = '#')
    print(trigrams)
    
    # 5. Триграфы без дополнения
    print("\n--- Триграфы (k=3, без дополнения) ---")
    trigrams_no_pad = text.get_kgrams(3, pad_symbol = None)
    print(trigrams_no_pad)
    
    # 6. Разбиение на блоки по 4 символа
    print("\n--- Разбиение на блоки по 4 символа ---")
    blocks = text.split_into_blocks(4, unit = "char")
    for i, block in enumerate(blocks):
        print(f"Блок {i + 1}: '{block}'")
    
    # 7. Комбинированный пример: k-графы как единицы, затем блоки из k-графов
    print("\n--- Биграммы как единицы текста, блоки по 2 биграммы ---")
    kgrams, blocks_of_kgrams = text.get_ngrams_as_units(k = 2, block_size = 2, pad_symbol = '_')
    print(f"Все биграммы: {kgrams}")
    print("Блоки биграмм:")
    for i, block in enumerate(blocks_of_kgrams):
        print(f"  Блок {i + 1}: {block}")
    
    # 8. Дополнительный пример: английский текст
    print("\n" + "=" * 60)
    print("Пример с английским текстом")
    print("=" * 60)
    english_alphabet_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    english_alphabet = Alphabet(english_alphabet_str)  # Создаём объект Alphabet
    eng_text = Text("HELLO WORLD", english_alphabet)
    print(f"Текст: '{eng_text.content}'")
    
    # Триграфы с дополнением
    eng_trigrams = eng_text.get_kgrams(3, pad_symbol = '_')
    print(f"Триграфы (k=3, дополнение '_'): {eng_trigrams}")
    
    # Блоки по 5 символов
    eng_blocks = eng_text.split_into_blocks(5)
    print(f"Блоки по 5 символов: {eng_blocks}")
    
    # 9. Пример с автоматическим созданием алфавита
    print("\n" + "=" * 60)
    print("Пример с автоматическим созданием алфавита")
    print("=" * 60)
    auto_text = Text("Hello, World! 123")
    print(f"Текст: '{auto_text.content}'")
    print(f"Автоматически созданный алфавит: '{auto_text.alphabet.symbols}'")


if __name__ == "__main__":
    demo()
