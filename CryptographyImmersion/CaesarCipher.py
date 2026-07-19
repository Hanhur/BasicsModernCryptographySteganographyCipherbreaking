# Шифр Цезаря
# -*- coding: utf-8 -*-
"""
Криптографические алгоритмы из текста:
1. Шифр Цезаря (сдвиг на K позиций)
2. Многоалфавитный шифр с ключевой фразой (Виженера)
"""

import string


class CaesarCipher:
    """Шифр Цезаря - простой сдвиг на фиксированное число позиций"""
    
    def __init__(self, alphabet):
        """
        Инициализация с указанным алфавитом
        
        Args:
            alphabet: строка с алфавитом (например, 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
        """
        self.alphabet = alphabet
        self.alphabet_len = len(alphabet)
        
    def encrypt(self, text, shift):
        """
        Шифрование текста сдвигом вправо
        
        Args:
            text: исходный текст (открытый текст)
            shift: величина сдвига (положительное число)
            
        Returns:
            зашифрованный текст
        """
        result = []
        for char in text.upper():
            if char in self.alphabet:
                idx = self.alphabet.index(char)
                new_idx = (idx + shift) % self.alphabet_len
                result.append(self.alphabet[new_idx])
            else:
                result.append(char)  # символы вне алфавита (пробелы, знаки) оставляем
        return ''.join(result)
    
    def decrypt(self, text, shift):
        """
        Расшифрование текста сдвигом влево
        
        Args:
            text: зашифрованный текст
            shift: величина сдвига (положительное число)
            
        Returns:
            расшифрованный текст
        """
        return self.encrypt(text, -shift)


class VigenereCipher:
    """Многоалфавитный шифр с ключевой фразой"""
    
    def __init__(self, alphabet):
        """
        Инициализация с указанным алфавитом
        
        Args:
            alphabet: строка с алфавитом
        """
        self.alphabet = alphabet
        self.alphabet_len = len(alphabet)
        
    def _prepare_key(self, key_phrase, text_len):
        """
        Подготовка ключевой фразы: повторяем её до длины текста
        
        Args:
            key_phrase: ключевая фраза (например, 'ЮЛИЙЦЕЗАРЬ')
            text_len: длина текста для шифрования
            
        Returns:
            строка-ключ нужной длины
        """
        # Убираем пробелы и переводим в верхний регистр
        clean_key = ''.join(key_phrase.upper().split())
        # Повторяем ключевую фразу до нужной длины
        repeated_key = (clean_key * (text_len // len(clean_key) + 1))[:text_len]
        return repeated_key
    
    def encrypt(self, text, key_phrase):
        """
        Шифрование текста с помощью ключевой фразы
        
        Как на рис. 1.8: каждая буква текста заменяется на букву
        из ключевой фразы, стоящую под ней в алфавите.
        
        Args:
            text: исходный текст (открытый текст)
            key_phrase: ключевая фраза (например, 'ЮЛИЙЦЕЗАРЬ')
            
        Returns:
            зашифрованный текст
        """
        text = text.upper()
        text_len = len(text)
        key = self._prepare_key(key_phrase, text_len)
        
        result = []
        key_idx = 0
        
        for char in text:
            if char in self.alphabet:
                # Позиция буквы в алфавите
                text_pos = self.alphabet.index(char)
                # Позиция буквы ключа в алфавите
                key_pos = self.alphabet.index(key[key_idx])
                
                # Суммируем позиции (как на рис. 1.8)
                new_pos = (text_pos + key_pos) % self.alphabet_len
                result.append(self.alphabet[new_pos])
                
                key_idx += 1
            else:
                result.append(char)
                
        return ''.join(result)
    
    def decrypt(self, text, key_phrase):
        """
        Расшифрование текста с помощью ключевой фразы
        
        Args:
            text: зашифрованный текст
            key_phrase: ключевая фраза
            
        Returns:
            расшифрованный текст
        """
        text = text.upper()
        text_len = len(text)
        key = self._prepare_key(key_phrase, text_len)
        
        result = []
        key_idx = 0
        
        for char in text:
            if char in self.alphabet:
                # Позиция зашифрованной буквы
                enc_pos = self.alphabet.index(char)
                # Позиция буквы ключа
                key_pos = self.alphabet.index(key[key_idx])
                
                # Вычитаем позицию ключа (обратная операция)
                new_pos = (enc_pos - key_pos) % self.alphabet_len
                result.append(self.alphabet[new_pos])
                
                key_idx += 1
            else:
                result.append(char)
                
        return ''.join(result)


def create_russian_alphabet():
    """Создание русского алфавита (как в тексте - 33 буквы)"""
    # Полный русский алфавит с Ё (33 буквы)
    return 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'


def create_english_alphabet():
    """Создание английского алфавита (26 букв)"""
    return string.ascii_uppercase


def demonstrate_caesar():
    """Демонстрация шифра Цезаря"""
    print("=" * 60)
    print("ШИФР ЦЕЗАРЯ (сдвиг на K позиций)")
    print("=" * 60)
    
    alphabet = create_russian_alphabet()
    cipher = CaesarCipher(alphabet)
    
    # Пример из текста: ПРИВЕТ -> ТУЛЕЗХ (K=3)
    original_text = "ПРИВЕТ"
    shift = 3
    
    print(f"\nИсходное сообщение: {original_text}")
    print(f"Ключ (сдвиг): {shift}")
    
    encrypted = cipher.encrypt(original_text, shift)
    print(f"Зашифрованное:    {encrypted}")
    
    decrypted = cipher.decrypt(encrypted, shift)
    print(f"Расшифрованное:    {decrypted}")
    
    # Проверка всех 32 комбинаций (как в тексте)
    print(f"\n[!] Для взлома методом грубой силы нужно проверить {len(alphabet) - 1} комбинаций")
    print("Пример перебора (первые 5 вариантов):")
    for i in range(1, 6):
        test = cipher.decrypt(encrypted, i)
        print(f"  Сдвиг {i:2d}: {test}")


def demonstrate_vigenere():
    """Демонстрация многоалфавитного шифра с ключевой фразой"""
    print("\n" + "=" * 60)
    print("МНОГОАЛФАВИТНЫЙ ШИФР С КЛЮЧЕВОЙ ФРАЗОЙ (Виженера)")
    print("=" * 60)
    
    alphabet = create_russian_alphabet()
    cipher = VigenereCipher(alphabet)
    
    # Пример из текста: СЕАНС -> РЕЮЦР (ключ: ЮЛИЙЦЕЗАРЬ)
    original_text = "СЕАНС"
    key_phrase = "ЮЛИЙЦЕЗАРЬ"
    
    print(f"\nИсходное сообщение: {original_text}")
    print(f"Ключевая фраза:      {key_phrase}")
    
    encrypted = cipher.encrypt(original_text, key_phrase)
    print(f"Зашифрованное:       {encrypted}")
    
    decrypted = cipher.decrypt(encrypted, key_phrase)
    print(f"Расшифрованное:       {decrypted}")
    
    print("\n[!] Количество возможных комбинаций для взлома:")
    print(f"    {len(alphabet)}! = 33! = 8, 683, 317, 618, 811, 890, 000, 000, 000, 000, 000, 000, 000")
    print("    (это более 8.6 × 10³⁶ комбинаций)")
    
    # Демонстрация с длинным текстом
    print("\n--- Дополнительный пример ---")
    long_text = "СЕАНС СОСТОИТСЯ ЗАВТРА"
    print(f"Исходный текст:  {long_text}")
    
    encrypted_long = cipher.encrypt(long_text, key_phrase)
    print(f"Зашифрованный:   {encrypted_long}")
    
    decrypted_long = cipher.decrypt(encrypted_long, key_phrase)
    print(f"Расшифрованный:  {decrypted_long}")


def demonstrate_visual_mapping():
    """Визуальная демонстрация принципа подстановки (как на рис. 1.8)"""
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ ПРИНЦИПА ПОДСТАНОВКИ")
    print("=" * 60)
    
    alphabet = create_russian_alphabet()
    key_phrase = "ЮЛИЙЦЕЗАРЬ"
    
    # Показываем как работает подстановка для слова СЕАНС
    text = "СЕАНС"
    key = (key_phrase * (len(text) // len(key_phrase) + 1))[:len(text)]
    
    print(f"\nАлфавит:      {' '.join(alphabet[:10])}... (всего {len(alphabet)} букв)")
    print(f"\nОткрытый текст:  {'  '.join(text)}")
    print(f"Ключевая фраза:  {'  '.join(key)}")
    
    print("\nЗамена букв (как на рис. 1.8):")
    for i, (char, key_char) in enumerate(zip(text, key)):
        text_pos = alphabet.index(char)
        key_pos = alphabet.index(key_char)
        new_pos = (text_pos + key_pos) % len(alphabet)
        new_char = alphabet[new_pos]
        
        print(f"  {char} (позиция {text_pos:2d}) + {key_char} (поз. {key_pos:2d}) = {new_char} (поз. {new_pos:2d})")


def main():
    """Главная функция программы"""
    print("\n" + "█" * 60)
    print("█" + " " * 20 + "КРИПТОГРАФИЯ: ШИФРЫ ЦЕЗАРЯ И ВИЖЕНЕРА" + " " * 18 + "█")
    print("█" * 60)
    
    demonstrate_caesar()
    demonstrate_vigenere()
    demonstrate_visual_mapping()
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nКлючевые выводы из текста:")
    print("  1. Шифр Цезаря: легко взломать перебором (всего 32 варианта)")
    print("  2. Многоалфавитный шифр: 33! комбинаций → очень сложно взломать")
    print("  3. Главная проблема: симметричность (ключ нужно передавать)")
    print("  4. Современная криптография использует асимметричные ключи")


if __name__ == "__main__":
    main()