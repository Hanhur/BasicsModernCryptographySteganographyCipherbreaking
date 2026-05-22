# 1. Основные понятия
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Криптографическая программа на основе лекционного материала.

Реализует:
1. Представление текста в числовой системе (вычеты по модулю)
2. Шифрование и расшифрование шифром Цезаря
3. Демонстрацию принципа Керкгоффса (секрет только в ключе)
"""

# ================================================================
# 1. НАСТРОЙКА АЛФАВИТОВ И ПЛАТФОРМ
# ================================================================

# Русский алфавит (33 буквы) для числового представления как в лекции
RUSSIAN_ALPHABET_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUSSIAN_ALPHABET_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Английский алфавит (26 букв) как в примере с "cake"
ENGLISH_ALPHABET_LOWER = "abcdefghijklmnopqrstuvwxyz"
ENGLISH_ALPHABET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Создаем словари для быстрого преобразования буква -> число
def create_mapping(alphabet):
    """Создает словарь {буква: индекс} для данного алфавита"""
    return {letter: idx for idx, letter in enumerate(alphabet)}

# Русские словари
RUS_TO_NUM_LOWER = create_mapping(RUSSIAN_ALPHABET_LOWER)
RUS_TO_NUM_UPPER = create_mapping(RUSSIAN_ALPHABET_UPPER)

# Английские словари
ENG_TO_NUM_LOWER = create_mapping(ENGLISH_ALPHABET_LOWER)
ENG_TO_NUM_UPPER = create_mapping(ENGLISH_ALPHABET_UPPER)

# Обратные словари для преобразования число -> буква
NUM_TO_RUS_LOWER = {v: k for k, v in RUS_TO_NUM_LOWER.items()}
NUM_TO_RUS_UPPER = {v: k for k, v in RUS_TO_NUM_UPPER.items()}
NUM_TO_ENG_LOWER = {v: k for k, v in ENG_TO_NUM_LOWER.items()}
NUM_TO_ENG_UPPER = {v: k for k, v in ENG_TO_NUM_UPPER.items()}

# Параметры модулей (размеры алфавитов)
MOD_RUSSIAN = len(RUSSIAN_ALPHABET_LOWER)  # = 33
MOD_ENGLISH = len(ENGLISH_ALPHABET_LOWER)  # = 26


# ================================================================
# 2. ПРЕОБРАЗОВАНИЕ ТЕКСТА В ЧИСЛА И ОБРАТНО (как в лекции)
# ================================================================

def text_to_numbers(text, language = 'russian'):
    """
    Преобразует текст в последовательность чисел (вычеты по модулю).
    
    Пример из лекции: "поэт" -> [16, 15, 30, 19]
    Пример из лекции: "cake" -> [2, 0, 10, 4]
    
    Args:
        text: входная строка
        language: 'russian' или 'english'
    
    Returns:
        список чисел
    """
    numbers = []
    
    if language == 'russian':
        to_num_lower = RUS_TO_NUM_LOWER
        to_num_upper = RUS_TO_NUM_UPPER
    else:
        to_num_lower = ENG_TO_NUM_LOWER
        to_num_upper = ENG_TO_NUM_UPPER
    
    for char in text:
        if char in to_num_lower:
            numbers.append(to_num_lower[char])
        elif char in to_num_upper:
            numbers.append(to_num_upper[char])
        else:
            # Для символов не из алфавита: пробелы, знаки препинания
            # Оставляем как есть или можно пропустить
            numbers.append(char)
    
    return numbers


def numbers_to_text(numbers, language = 'russian'):
    """
    Преобразует последовательность чисел обратно в текст.
    
    Args:
        numbers: список чисел (индексы букв)
        language: 'russian' или 'english'
    
    Returns:
        строка текста
    """
    if language == 'russian':
        num_to_lower = NUM_TO_RUS_LOWER
        num_to_upper = NUM_TO_RUS_UPPER
    else:
        num_to_lower = NUM_TO_ENG_LOWER
        num_to_upper = NUM_TO_ENG_UPPER
    
    result_chars = []
    for num in numbers:
        if isinstance(num, int):
            # По умолчанию возвращаем строчную букву
            result_chars.append(num_to_lower.get(num, '?'))
        else:
            # Символ не из алфавита (пробел и т.д.)
            result_chars.append(num)
    
    return ''.join(result_chars)


# ================================================================
# 3. ФУНКЦИЯ ШИФРОВАНИЯ (шифр Цезаря)
# ================================================================

def caesar_encrypt(plaintext, key, language = 'russian'):
    """
    Шифрование текста шифром Цезаря.
    
    Функция шифрования E_k(P) = (P + k) mod m
    
    Где:
        P - число, соответствующее букве открытого текста
        k - ключ (секретное число)
        m - размер алфавита (модуль)
    
    Args:
        plaintext: открытый текст
        key: ключ (целое число, сдвиг)
        language: 'russian' или 'english'
    
    Returns:
        зашифрованный текст
    """
    if language == 'russian':
        modulus = MOD_RUSSIAN
        to_num_lower = RUS_TO_NUM_LOWER
        to_num_upper = RUS_TO_NUM_UPPER
        num_to_lower = NUM_TO_RUS_LOWER
        num_to_upper = NUM_TO_RUS_UPPER
    else:
        modulus = MOD_ENGLISH
        to_num_lower = ENG_TO_NUM_LOWER
        to_num_upper = ENG_TO_NUM_UPPER
        num_to_lower = NUM_TO_ENG_LOWER
        num_to_upper = NUM_TO_ENG_UPPER
    
    result = []
    
    for char in plaintext:
        if char in to_num_lower:
            # Строчная буква
            p = to_num_lower[char]
            c = (p + key) % modulus
            result.append(num_to_lower[c])
        elif char in to_num_upper:
            # Заглавная буква
            p = to_num_upper[char]
            c = (p + key) % modulus
            result.append(num_to_upper[c])
        else:
            # Не буквенный символ оставляем без изменений
            result.append(char)
    
    return ''.join(result)


def caesar_decrypt(ciphertext, key, language = 'russian'):
    """
    Расшифрование текста шифром Цезаря.
    
    Функция расшифрования D_k(C) = (C - k) mod m
    
    Args:
        ciphertext: зашифрованный текст
        key: ключ (тот же, что использовался для шифрования)
        language: 'russian' или 'english'
    
    Returns:
        расшифрованный текст
    """
    return caesar_encrypt(ciphertext, -key, language)


# ================================================================
# 4. КРИПТОАНАЛИЗ (взлом шифра Цезаря перебором)
# ================================================================

def brute_force_caesar(ciphertext, language = 'russian'):
    """
    Криптоанализ шифра Цезаря: перебор всех возможных ключей.
    
    Демонстрирует, почему шифр Цезаря не является криптостойким.
    
    Args:
        ciphertext: зашифрованный текст
        language: 'russian' или 'english'
    
    Returns:
        словарь {ключ: расшифрованный_текст}
    """
    if language == 'russian':
        modulus = MOD_RUSSIAN
    else:
        modulus = MOD_ENGLISH
    
    results = {}
    for key in range(modulus):
        decrypted = caesar_decrypt(ciphertext, key, language)
        results[key] = decrypted
    
    return results


# ================================================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ
# ================================================================

def demonstrate_encryption_examples():
    """Демонстрирует примеры из лекции"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРИМЕРОВ ИЗ ЛЕКЦИИ")
    print("=" * 60)
    
    # Пример 1: "cake" на английском
    print("\n1. Английский пример 'cake':")
    text_eng = "cake"
    numbers_eng = text_to_numbers(text_eng, 'english')
    print(f"   Текст: {text_eng}")
    print(f"   Числа: {numbers_eng} (как в лекции: [2, 0, 10, 4])")
    
    # Пример 2: "поэт" на русском
    print("\n2. Русский пример 'поэт':")
    text_rus = "поэт"
    numbers_rus = text_to_numbers(text_rus, 'russian')
    print(f"   Текст: {text_rus}")
    print(f"   Числа: {numbers_rus} (как в лекции: [16, 15, 30, 19])")
    print(f"   Проверка: п=16, о=15, э=30, т=19")
    
    # Проверка обратного преобразования
    text_restored = numbers_to_text(numbers_rus, 'russian')
    print(f"   Обратное преобразование: {text_restored}")


def demonstrate_caesar():
    """Демонстрирует шифрование и расшифрование шифром Цезаря"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ШИФРА ЦЕЗАРЯ")
    print("=" * 60)
    
    # Русский пример
    print("\n1. Русский текст:")
    plain_rus = "привет мир"
    key = 5
    print(f"   Открытый текст: {plain_rus}")
    print(f"   Ключ: {key}")
    
    cipher_rus = caesar_encrypt(plain_rus, key, 'russian')
    print(f"   Зашифрованный текст: {cipher_rus}")
    
    decrypted_rus = caesar_decrypt(cipher_rus, key, 'russian')
    print(f"   Расшифрованный текст: {decrypted_rus}")
    
    # Английский пример (как в лекции с cake)
    print("\n2. Английский текст (как в лекции о Цезаре):")
    plain_eng = "cake"
    key_eng = 3
    print(f"   Открытый текст: {plain_eng}")
    print(f"   Ключ: {key_eng}")
    
    cipher_eng = caesar_encrypt(plain_eng, key_eng, 'english')
    print(f"   E_3(cake) = (2,0,10,4) + 3 = (5,3,13,7) -> {cipher_eng}")
    
    decrypted_eng = caesar_decrypt(cipher_eng, key_eng, 'english')
    print(f"   Расшифрование: {decrypted_eng}")


def demonstrate_brute_force():
    """Демонстрирует криптоанализ перебором"""
    print("\n" + "=" * 60)
    print("КРИПТОАНАЛИЗ: ПЕРЕБОР ВСЕХ КЛЮЧЕЙ")
    print("=" * 60)
    print("Демонстрация того, почему шифр Цезаря нестойкий\n")
    
    # Небольшой зашифрованный текст
    cipher = "хитсз"
    print(f"Перехваченный шифртекст: '{cipher}'")
    print("Перебор всех возможных ключей (0-32):\n")
    
    results = brute_force_caesar(cipher, 'russian')
    
    print("Ключ | Расшифрованный текст")
    print("-" * 35)
    for key in range(10):  # Покажем только первые 10 для краткости
        print(f" {key:2}   | {results[key]}")
    print(" ...")
    
    # Находим осмысленный результат (обычно ключ 11 дает "привет" для "хитсз")
    print("\nПри ключе 11 получается: " + results[11])


def demonstrate_kerckhoffs():
    """Демонстрирует принцип Керкгоффса"""
    print("\n" + "=" * 60)
    print("ПРИНЦИП КЕРКГОФФСА")
    print("=" * 60)
    print("Секрет должен заключаться ТОЛЬКО в ключе, алгоритм шифрования открыт.")
    print("В нашей программе алгоритм (функция caesar_encrypt) известен всем.")
    print("Без знания ключа (3, 5, 11...) невозможно прочитать сообщение,")
    print("но перебором ключей (как показано выше) можно найти правильный.")
    print("Поэтому современные шифры используют огромные пространства ключей.")


# ================================================================
# 6. ДОПОЛНИТЕЛЬНЫЙ КЛАСС ДЛЯ КРИПТОСИСТЕМЫ
# ================================================================

class Cryptosystem:
    """
    Класс, представляющий полную криптосистему согласно определению из лекции.
    
    Криптосистема = (P, C, K, E, D)
    где:
    P - пространство открытых текстов
    C - пространство шифртекстов
    K - пространство ключей
    E - функция шифрования
    D - функция расшифрования
    """
    
    def __init__(self, language = 'russian'):
        self.language = language
        if language == 'russian':
            self.modulus = MOD_RUSSIAN
            self.alphabet = RUSSIAN_ALPHABET_LOWER
        else:
            self.modulus = MOD_ENGLISH
            self.alphabet = ENGLISH_ALPHABET_LOWER
        
        self.plaintext_space = self.alphabet  # P
        self.ciphertext_space = self.alphabet  # C
        self.key_space = list(range(self.modulus))  # K
    
    def encrypt(self, plaintext, key):
        """Функция шифрования E_k(P)"""
        return caesar_encrypt(plaintext, key, self.language)
    
    def decrypt(self, ciphertext, key):
        """Функция расшифрования D_k(C)"""
        return caesar_decrypt(ciphertext, key, self.language)
    
    def is_valid_key(self, key):
        """Проверяет, принадлежит ли ключ пространству ключей"""
        return 0 <= key < self.modulus
    
    def get_key_space_size(self):
        """Возвращает размер пространства ключей"""
        return len(self.key_space)
    
    def __repr__(self):
        return f"Cryptosystem(language = {self.language}, modulus = {self.modulus}, |K| = {self.get_key_space_size()})"


# ================================================================
# 7. ГЛАВНАЯ ФУНКЦИЯ
# ================================================================

def main():
    """Главная функция программы"""
    print("\n" + "=" * 60)
    print("    КРИПТОГРАФИЧЕСКАЯ ПРОГРАММА")
    print("    На основе лекционного материала")
    print("=" * 60)
    
    # Демонстрация всех примеров
    demonstrate_encryption_examples()
    demonstrate_caesar()
    demonstrate_brute_force()
    demonstrate_kerckhoffs()
    
    # Работа с классом криптосистемы
    print("\n" + "=" * 60)
    print("КЛАСС КРИПТОСИСТЕМЫ")
    print("=" * 60)
    
    cs_rus = Cryptosystem('russian')
    print(f"Создана криптосистема: {cs_rus}")
    
    test_text = "криптография"
    test_key = 7
    encrypted = cs_rus.encrypt(test_text, test_key)
    decrypted = cs_rus.decrypt(encrypted, test_key)
    
    print(f"Тест: '{test_text}' -> зашифровано -> '{encrypted}' -> расшифровано -> '{decrypted}'")
    print(f"Пространство ключей |K| = {cs_rus.get_key_space_size()} (всего {cs_rus.modulus} возможных сдвигов)")
    
    print("\n" + "=" * 60)
    print("Программа завершила работу.")
    print("=" * 60)


# Точка входа
if __name__ == "__main__":
    main()