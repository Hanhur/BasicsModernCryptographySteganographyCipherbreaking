# Введение
"""
Реализация шифров, описанных в главе 8.1
Демонстрация: шифр Цезаря, многоалфавитный шифр, блочный шифр с перемешиванием
"""

import string
from typing import Tuple, List, Optional
from collections import Counter

# Русский алфавит (32 буквы без Ё)
RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ALPHABET_SIZE = len(RUSSIAN_ALPHABET)

def char_to_index(char: str) -> int:
    """Преобразует букву в индекс (0 - 31)"""
    return RUSSIAN_ALPHABET.index(char.upper())

def index_to_char(index: int) -> str:
    """Преобразует индекс в букву"""
    return RUSSIAN_ALPHABET[index % ALPHABET_SIZE]

def text_to_indices(text: str) -> List[int]:
    """Преобразует текст в список индексов"""
    return [char_to_index(c) for c in text.upper() if c.upper() in RUSSIAN_ALPHABET]

def indices_to_text(indices: List[int]) -> str:
    """Преобразует список индексов в текст"""
    return ''.join(index_to_char(i) for i in indices)

def text_prepare(text: str) -> str:
    """Подготавливает текст: удаляет пробелы и знаки препинания"""
    return ''.join(c.upper() for c in text if c.upper() in RUSSIAN_ALPHABET)

# ============ ШИФР ЦЕЗАРЯ (для сравнения) ============

def caesar_encrypt(text: str, key: int) -> str:
    """Шифрование шифром Цезаря"""
    text = text_prepare(text)
    indices = text_to_indices(text)
    encrypted = [(i + key) % ALPHABET_SIZE for i in indices]
    return indices_to_text(encrypted)

def caesar_decrypt(text: str, key: int) -> str:
    """Дешифрование шифром Цезаря"""
    text = text_prepare(text)
    indices = text_to_indices(text)
    decrypted = [(i - key) % ALPHABET_SIZE for i in indices]
    return indices_to_text(decrypted)

def caesar_cryptanalysis(ciphertext: str, known_word: Optional[str] = None) -> None:
    """Криптоанализ шифра Цезаря (перебор всех ключей)"""
    ciphertext = text_prepare(ciphertext)
    print(f"\nКриптоанализ шифра Цезаря для текста: {ciphertext}")
    print("Перебор всех 32 ключей:")
    
    for key in range(ALPHABET_SIZE):
        decrypted = caesar_decrypt(ciphertext, key)
        # Если задано известное слово, проверяем его наличие
        if known_word:
            if known_word.upper() in decrypted:
                print(f"  Ключ {key:2d}: {decrypted} <-- ВОЗМОЖНО РЕШЕНИЕ!")
        else:
            print(f"  Ключ {key:2d}: {decrypted}")

# ============ МНОГОАЛФАВИТНЫЙ ШИФР (8.1) ============

class MultiCaesar:
    """
    Шифр с разными ключами для четных и нечетных позиций
    k = (k1, k2) - ключ для нечетных и четных позиций соответственно
    """
    
    def __init__(self, key1: int, key2: int):
        self.k1 = key1 % ALPHABET_SIZE
        self.k2 = key2 % ALPHABET_SIZE
    
    def encrypt(self, text: str) -> str:
        """Шифрование (8.1)"""
        text = text_prepare(text)
        result = []
        for i, char in enumerate(text):
            idx = char_to_index(char)
            if i % 2 == 0:  # нечетная позиция (0, 2, 4...)
                new_idx = (idx + self.k1) % ALPHABET_SIZE
            else:           # четная позиция (1, 3, 5...)
                new_idx = (idx + self.k2) % ALPHABET_SIZE
            result.append(index_to_char(new_idx))
        return ''.join(result)
    
    def decrypt(self, text: str) -> str:
        """Дешифрование"""
        text = text_prepare(text)
        result = []
        for i, char in enumerate(text):
            idx = char_to_index(char)
            if i % 2 == 0:
                new_idx = (idx - self.k1) % ALPHABET_SIZE
            else:
                new_idx = (idx - self.k2) % ALPHABET_SIZE
            result.append(index_to_char(new_idx))
        return ''.join(result)
    
    def get_key(self) -> Tuple[int, int]:
        return (self.k1, self.k2)


# ============ БЛОЧНЫЙ ШИФР С ПЕРЕМЕШИВАНИЕМ (8.2) ============

class BlockCipher:
    """
    Блочный шифр с перемешиванием (раунд)
    Шифрует блоки по 2 символа: 
    m~i = mi + mi+1
    m~i+1 = mi+1 + m~i
    ci = m~i + k1
    ci+1 = m~i+1 + k2
    """
    
    def __init__(self, key1: int, key2: int):
        self.k1 = key1 % ALPHABET_SIZE
        self.k2 = key2 % ALPHABET_SIZE
    
    def _mix_block(self, a: int, b: int) -> Tuple[int, int]:
        """Перемешивание двух символов (первые две операции из 8.2)"""
        a_tilde = (a + b) % ALPHABET_SIZE
        b_tilde = (b + a_tilde) % ALPHABET_SIZE
        return a_tilde, b_tilde
    
    def _unmix_block(self, a_tilde: int, b_tilde: int) -> Tuple[int, int]:
        """Обратное перемешивание (из 8.3)"""
        b = (b_tilde - a_tilde) % ALPHABET_SIZE
        a = (a_tilde - b) % ALPHABET_SIZE
        return a, b
    
    def encrypt(self, text: str, show_intermediate: bool = False) -> str:
        """Шифрование (8.2)"""
        text = text_prepare(text)
        indices = text_to_indices(text)
        
        # Добавляем фиктивный символ, если длина нечетная
        if len(indices) % 2 != 0:
            indices.append(0)  # Добавляем 'А'
        
        result = []
        intermediate = []
        
        for i in range(0, len(indices), 2):
            a, b = indices[i], indices[i + 1]
            a_tilde, b_tilde = self._mix_block(a, b)
            
            if show_intermediate:
                intermediate.extend([a_tilde, b_tilde])
            
            # Добавляем ключи
            c1 = (a_tilde + self.k1) % ALPHABET_SIZE
            c2 = (b_tilde + self.k2) % ALPHABET_SIZE
            result.extend([c1, c2])
        
        if show_intermediate:
            print(f"  Промежуточный результат (после перемешивания): {indices_to_text(intermediate)}")
        
        return indices_to_text(result)
    
    def decrypt(self, text: str) -> str:
        """Дешифрование (8.3)"""
        text = text_prepare(text)
        indices = text_to_indices(text)
        
        result = []
        for i in range(0, len(indices), 2):
            if i + 1 >= len(indices):
                break
            c1, c2 = indices[i], indices[i + 1]
            
            # Вычитаем ключи
            a_tilde = (c1 - self.k1) % ALPHABET_SIZE
            b_tilde = (c2 - self.k2) % ALPHABET_SIZE
            
            # Обратное перемешивание
            a, b = self._unmix_block(a_tilde, b_tilde)
            result.extend([a, b])
        
        return indices_to_text(result)
    
    def get_key(self) -> Tuple[int, int]:
        return (self.k1, self.k2)


# ============ ДВУХРАУНДОВЫЙ ШИФР (8.5) ============

class DoubleBlockCipher:
    """
    Двухраундовый шифр: применяет BlockCipher дважды
    """
    
    def __init__(self, key1_1: int, key1_2: int, key2_1: int, key2_2: int):
        self.round1 = BlockCipher(key1_1, key1_2)
        self.round2 = BlockCipher(key2_1, key2_2)
    
    def encrypt(self, text: str, show_intermediate: bool = False) -> str:
        """Двухраундовое шифрование (8.5)"""
        text = text_prepare(text)
        
        if show_intermediate:
            print(f"  Исходный текст: {text}")
            print(f"  Ключ раунда 1: {self.round1.get_key()}")
        
        after_round1 = self.round1.encrypt(text, show_intermediate)
        
        if show_intermediate:
            print(f"  После раунда 1: {after_round1}")
            print(f"  Ключ раунда 2: {self.round2.get_key()}")
        
        after_round2 = self.round2.encrypt(after_round1, False)
        
        if show_intermediate:
            print(f"  После раунда 2: {after_round2}")
        
        return after_round2
    
    def decrypt(self, text: str) -> str:
        """Дешифрование"""
        text = text_prepare(text)
        after_round1 = self.round2.decrypt(text)
        original = self.round1.decrypt(after_round1)
        return original


# ============ КРИПТОАНАЛИЗ ============

def frequency_analysis(text: str) -> None:
    """Частотный анализ текста"""
    text = text_prepare(text)
    counter = Counter(text)
    total = len(text)
    
    print("\nЧастотный анализ:")
    print(f"  Длина текста: {total}")
    for char, count in counter.most_common():
        percentage = (count / total) * 100
        print(f"  {char}: {count} ({percentage:.1f}%)")

def cryptanalysis_multi_caesar(ciphertext: str, known_plaintext_word: Optional[str] = None) -> None:
    """
    Криптоанализ многоалфавитного шифра (частотный анализ)
    """
    ciphertext = text_prepare(ciphertext)
    print(f"\nКриптоанализ многоалфавитного шифра для: {ciphertext}")
    
    # Анализируем четные и нечетные позиции отдельно
    even_positions = [ciphertext[i] for i in range(1, len(ciphertext), 2)]
    odd_positions = [ciphertext[i] for i in range(0, len(ciphertext), 2)]
    
    if not even_positions:
        print("  Текст слишком короткий для анализа")
        return
    
    # Находим наиболее частые буквы на четных позициях
    even_counter = Counter(even_positions)
    most_common_even = even_counter.most_common(3)
    print(f"\n  Наиболее частые на четных позициях: {most_common_even}")
    
    # Для примера: предполагаем, что самая частая буква - это 'О' или 'Е'
    # (в реальном криптоанализе используется таблица частот языка)
    common_letters = ['О', 'Е', 'А']
    
    found_keys = []
    for target_char in common_letters[:2]:  # Проверяем О и Е
        if most_common_even:
            most_freq_even = most_common_even[0][0]
            k2 = (char_to_index(most_freq_even) - char_to_index(target_char)) % ALPHABET_SIZE
            print(f"\n  Гипотеза: {most_freq_even} = {target_char} => k2 = {k2}")
            
            # Перебираем k1
            for k1 in range(ALPHABET_SIZE):
                cipher = MultiCaesar(k1, k2)
                decrypted = cipher.decrypt(ciphertext)
                # Если задано известное слово, проверяем
                if known_plaintext_word:
                    if known_plaintext_word.upper() in decrypted:
                        print(f"    Ключ ({k1}, {k2}): {decrypted} <-- НАЙДЕНО!")
                        found_keys.append((k1, k2))
                else:
                    # Показываем только осмысленные результаты (все буквы русского алфавита)
                    if all(c in RUSSIAN_ALPHABET for c in decrypted):
                        print(f"    Ключ ({k1}, {k2}): {decrypted}")
    
    return found_keys


# ============ ДЕМОНСТРАЦИЯ ============

def demonstrate_all_ciphers():
    """Демонстрация всех шифров на примере из текста"""
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ШИФРОВ ИЗ ГЛАВЫ 8.1")
    print("=" * 60)
    
    # Исходное сообщение из текста
    plaintext = "ПЕРЕМЕНА"
    print(f"\nИсходное сообщение: {plaintext}")
    
    # 1. Шифр Цезаря (для сравнения)
    print("\n" + "-" * 40)
    print("1. ШИФР ЦЕЗАРЯ (ключ 3)")
    print("-" * 40)
    caesar_key = 3
    ciphertext_caesar = caesar_encrypt(plaintext, caesar_key)
    print(f"  Зашифровано: {ciphertext_caesar}")
    decrypted_caesar = caesar_decrypt(ciphertext_caesar, caesar_key)
    print(f"  Расшифровано: {decrypted_caesar}")
    
    # 2. Многоалфавитный шифр (8.1)
    print("\n" + "-" * 40)
    print("2. МНОГОАЛФАВИТНЫЙ ШИФР (8.1) с ключом (3, 5)")
    print("-" * 40)
    multi = MultiCaesar(3, 5)
    ciphertext_multi = multi.encrypt(plaintext)
    print(f"  Зашифровано: {ciphertext_multi}")
    decrypted_multi = multi.decrypt(ciphertext_multi)
    print(f"  Расшифровано: {decrypted_multi}")
    
    # 3. Блочный шифр с перемешиванием (8.2)
    print("\n" + "-" * 40)
    print("3. БЛОЧНЫЙ ШИФР С ПЕРЕМЕШИВАНИЕМ (8.2) с ключом (3, 5)")
    print("-" * 40)
    block = BlockCipher(3, 5)
    ciphertext_block = block.encrypt(plaintext, show_intermediate = True)
    print(f"  Зашифровано: {ciphertext_block}")
    decrypted_block = block.decrypt(ciphertext_block)
    print(f"  Расшифровано: {decrypted_block}")
    
    # 4. Двухраундовый шифр (8.5)
    print("\n" + "-" * 40)
    print("4. ДВУХРАУНДОВЫЙ ШИФР (8.5) с ключами (3,5) и (3,5)")
    print("-" * 40)
    double = DoubleBlockCipher(3, 5, 3, 5)
    ciphertext_double = double.encrypt(plaintext, show_intermediate = True)
    print(f"  Зашифровано: {ciphertext_double}")
    decrypted_double = double.decrypt(ciphertext_double)
    print(f"  Расшифровано: {decrypted_double}")
    
    # 5. Сравнение размеров ключей
    print("\n" + "-" * 40)
    print("5. СРАВНЕНИЕ РАЗМЕРОВ КЛЮЧЕЙ")
    print("-" * 40)
    print(f"  Шифр Цезаря: 1 ключ (32 варианта)")
    print(f"  Многоалфавитный (8.1): 2 ключа (32 ^ 2 = {32 ** 2} вариантов)")
    print(f"  Блочный (8.2): 2 ключа (32 ^ 2 = {32 ** 2} вариантов)")
    print(f"  Двухраундовый (8.5): 4 ключа (32 ^ 4 = {32 ** 4} вариантов)")


def demonstrate_cryptanalysis():
    """Демонстрация криптоанализа"""
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ КРИПТОАНАЛИЗА")
    print("=" * 60)
    
    # 1. Частотный анализ
    text = "ВЛОЖЕНИЕСРЕДСТВВБАНКИРАССМАТРИВАЕТСЯКАКНАДЕЖНЫЙСПОСОБСОХРАНЕНИЯ"
    print(f"\nТекст для частотного анализа: {text[:40]}...")
    frequency_analysis(text)
    
    # 2. Криптоанализ многоалфавитного шифра
    print("\n" + "-" * 40)
    print("КРИПТОАНАЛИЗ МНОГОАЛФАВИТНОГО ШИФРА")
    print("-" * 40)
    
    # Шифруем текст
    plaintext = "ПЕРЕМЕНА"
    multi = MultiCaesar(3, 5)
    ciphertext = multi.encrypt(plaintext)
    print(f"  Исходный текст: {plaintext}")
    print(f"  Зашифровано: {ciphertext}")
    
    # Атака с известным открытым текстом (частично)
    print(f"\n  Атака с известным открытым текстом:")
    print(f"  Известно: {plaintext} -> {ciphertext}")
    print(f"  Вычисляем ключи:")
    k1 = (char_to_index(ciphertext[0]) - char_to_index(plaintext[0])) % ALPHABET_SIZE
    k2 = (char_to_index(ciphertext[1]) - char_to_index(plaintext[1])) % ALPHABET_SIZE
    print(f"    k1 = {ciphertext[0]} - {plaintext[0]} = {k1}")
    print(f"    k2 = {ciphertext[1]} - {plaintext[1]} = {k2}")
    
    # 3. Проблема с блочным шифром
    print("\n" + "-" * 40)
    print("ПРОБЛЕМА: БЛОЧНЫЙ ШИФР (8.2) И АТАКА С ИЗВЕСТНЫМ ТЕКСТОМ")
    print("-" * 40)
    
    block = BlockCipher(3, 5)
    ciphertext_block = block.encrypt(plaintext)
    print(f"  {plaintext} -> {ciphertext_block}")
    print(f"  Прямое вычисление ключей невозможно!")
    print(f"  Нужно сначала получить промежуточный результат...")
    
    # Но Ева может получить промежуточный результат, зная алгоритм
    print(f"  Ева знает алгоритм и может применить перемешивание к открытому тексту:")
    mixed = []
    indices = text_to_indices(plaintext)
    for i in range(0, len(indices), 2):
        a, b = indices[i], indices[i + 1]
        a_tilde = (a + b) % ALPHABET_SIZE
        b_tilde = (b + a_tilde) % ALPHABET_SIZE
        mixed.extend([a_tilde, b_tilde])
    mixed_text = indices_to_text(mixed)
    print(f"    Промежуточный: {plaintext} -> {mixed_text}")
    print(f"  Теперь можно вычислить ключи:")
    k1 = (char_to_index(ciphertext_block[0]) - char_to_index(mixed_text[0])) % ALPHABET_SIZE
    k2 = (char_to_index(ciphertext_block[1]) - char_to_index(mixed_text[1])) % ALPHABET_SIZE
    print(f"    k1 = {ciphertext_block[0]} - {mixed_text[0]} = {k1}")
    print(f"    k2 = {ciphertext_block[1]} - {mixed_text[1]} = {k2}")


def interactive_test():
    """Интерактивный тест для пользователя"""
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ ТЕСТ")
    print("=" * 60)
    
    while True:
        print("\nВыберите действие:")
        print("  1. Зашифровать текст (многоалфавитный шифр)")
        print("  2. Зашифровать текст (блочный шифр)")
        print("  3. Дешифровать текст")
        print("  4. Частотный анализ текста")
        print("  5. Выйти")
        
        choice = input("Ваш выбор: ").strip()
        
        if choice == '5':
            break
        
        if choice == '1':
            text = input("Введите текст: ")
            k1 = int(input("Введите k1: "))
            k2 = int(input("Введите k2: "))
            cipher = MultiCaesar(k1, k2)
            result = cipher.encrypt(text)
            print(f"Зашифровано: {result}")
        
        elif choice == '2':
            text = input("Введите текст: ")
            k1 = int(input("Введите k1: "))
            k2 = int(input("Введите k2: "))
            cipher = BlockCipher(k1, k2)
            show = input("Показывать промежуточный результат? (y/n): ").lower() == 'y'
            result = cipher.encrypt(text, show)
            print(f"Зашифровано: {result}")
        
        elif choice == '3':
            text = input("Введите зашифрованный текст: ")
            print("Выберите шифр:")
            print("  1. Многоалфавитный")
            print("  2. Блочный")
            cipher_type = input("Ваш выбор: ").strip()
            
            if cipher_type == '1':
                k1 = int(input("Введите k1: "))
                k2 = int(input("Введите k2: "))
                cipher = MultiCaesar(k1, k2)
            else:
                k1 = int(input("Введите k1: "))
                k2 = int(input("Введите k2: "))
                cipher = BlockCipher(k1, k2)
            
            result = cipher.decrypt(text)
            print(f"Расшифровано: {result}")
        
        elif choice == '4':
            text = input("Введите текст: ")
            frequency_analysis(text)
        
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    # Запуск демонстрации
    demonstrate_all_ciphers()
    demonstrate_cryptanalysis()
    
    # Интерактивный режим (закомментирован, чтобы не мешать демонстрации)
    # interactive_test()