# Криптограммы Бейла
import re
import string
from typing import List, Tuple, Optional


class BealeCipher:
    """
    Реализация книжного шифра Бейла.
    Каждое число в шифре соответствует номеру слова в тексте-ключе,
    а буква извлекается как первая буква этого слова.
    """
    
    def __init__(self, key_text: str):
        """
        Инициализация шифра с текстом-ключом.
        
        Args:
            key_text: Текст-ключ (например, Декларация независимости)
        """
        self.key_text = key_text
        self.words = self._tokenize(key_text)
        self.word_count = len(self.words)
        
        # Словарь для быстрого поиска: номер слова -> первая буква
        self.word_map = {}
        for idx, word in enumerate(self.words, start = 1):
            self.word_map[idx] = word[0] if word else ''
        
        print(f"[Инициализация] Загружено {self.word_count} слов в тексте-ключе")
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Разбивает текст на слова, удаляя знаки препинания.
        Словами считаются последовательности букв и апострофов.
        """
        # Удаляем всё, кроме букв, пробелов и апострофов
        text = re.sub(r'[^a-zA-Z\'\s]', ' ', text)
        # Разбиваем по пробелам и убираем пустые строки
        words = [word for word in text.split() if word]
        return words
    
    def encrypt(self, plaintext: str) -> List[int]:
        """
        Шифрует открытый текст в последовательность чисел.
        
        Args:
            plaintext: Текст для шифрования (только буквы, пробелы игнорируются)
            
        Returns:
            Список чисел (номеров слов в тексте-ключе)
        """
        # Убираем всё, кроме букв и пробелов
        clean_text = re.sub(r'[^a-zA-Z\s]', '', plaintext)
        # Извлекаем первые буквы каждого слова
        target_letters = [word[0].upper() for word in clean_text.split() if word]
        
        encrypted = []
        not_found = []
        
        for letter in target_letters:
            # Ищем слово, начинающееся с нужной буквы
            found = False
            # Начинаем поиск с 1 (первое слово в тексте-ключе)
            for word_num, first_letter in self.word_map.items():
                if first_letter.upper() == letter:
                    encrypted.append(word_num)
                    found = True
                    break
            
            if not found:
                # Если буква не найдена, используем заглушку -1
                encrypted.append(-1)
                not_found.append(letter)
        
        if not_found:
            print(f"[Предупреждение] Буквы не найдены в тексте-ключе: {set(not_found)}")
        
        return encrypted
    
    def decrypt(self, numbers: List[int]) -> str:
        """
        Расшифровывает последовательность чисел в открытый текст.
        
        Args:
            numbers: Список чисел (номеров слов в тексте-ключе)
            
        Returns:
            Расшифрованный текст
        """
        result = []
        errors = []
        
        for num in numbers:
            if num in self.word_map:
                result.append(self.word_map[num])
            else:
                # Если номер выходит за пределы текста-ключа
                if num > 0:
                    errors.append(num)
                    result.append('?')  # Заглушка для неизвестного номера
                else:
                    result.append('?')
        
        if errors:
            print(f"[Предупреждение] Номера вне диапазона (1 - {self.word_count}): {errors[:10]}...")
        
        return ''.join(result)
    
    def decrypt_with_context(self, numbers: List[int], show_first: int = 10) -> str:
        """
        Расшифровывает и показывает процесс для первых N чисел.
        """
        result = []
        print("\n=== Пошаговая расшифровка ===")
        print(f"{'№':<6} {'Слово в ключе':<25} {'Первая буква':<12} {'Результат'}")
        print("-" * 60)
        
        for i, num in enumerate(numbers[:show_first], 1):
            if num in self.word_map:
                word = self.words[num - 1] if num <= len(self.words) else "???"
                letter = self.word_map[num]
                result.append(letter)
                print(f"{num:<6} {word[:24]:<25} {letter:<12} {''.join(result)}")
            else:
                print(f"{num:<6} {'[НЕ НАЙДЕНО]':<25} {'?':<12} {''.join(result)}?")
                result.append('?')
        
        if len(numbers) > show_first:
            print(f"... и ещё {len(numbers) - show_first} чисел")
        
        print("-" * 60)
        print(f"Результат: {''.join(result)}")
        return ''.join(result)


def load_declaration() -> str:
    """
    Загружает Декларацию независимости США.
    Если файл не найден, использует встроенный текст (первые 115 слов).
    """
    try:
        with open('declaration.txt', 'r', encoding = 'utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("[Информация] Файл declaration.txt не найден. Использую встроенный текст.")
        return DECLARATION_TEXT


# Первые 115 слов Декларации независимости США (как в вашем примере)
DECLARATION_TEXT = """
When in the Course of human events it becomes necessary for one people to dissolve 
the political bands which have connected them with another and to assume among 
the powers of the earth the separate and equal station to which the laws of nature 
and of nature's God entitle them a decent respect to the opinions of mankind 
requires that they should declare the causes which impel them to the separation 
We hold these truths to be self-evident that all men are created equal that they 
are endowed by their Creator with certain unalienable rights that among these 
are life liberty and the pursuit of happiness that to secure these rights 
governments are instituted
"""


def main():
    """
    Демонстрация работы шифра Бейла.
    """
    print("=" * 60)
    print("КРИПТОГРАММЫ БЕЙЛА — реализация книжного шифра")
    print("=" * 60)
    
    # 1. Загружаем текст-ключ
    print("\n[1] Загрузка текста-ключа (Декларация независимости США)...")
    key_text = load_declaration()
    
    # 2. Создаём шифр
    cipher = BealeCipher(key_text)
    
    # 3. Пример шифрования
    print("\n[2] Шифрование сообщения...")
    plaintext = "I have deposited in the county"
    print(f"Исходный текст: {plaintext}")
    
    encrypted = cipher.encrypt(plaintext)
    print(f"Зашифрованный текст (числа): {encrypted[:20]}...")
    
    # 4. Пример расшифровки (с пошаговым выводом)
    print("\n[3] Расшифровка с пошаговым показом...")
    decrypted = cipher.decrypt_with_context(encrypted, show_first = 10)
    
    # 5. Полная расшифровка
    print(f"\n[4] Полный расшифрованный текст: {decrypted}")
    
    # 6. Демонстрация на реальных числах из второй криптограммы
    print("\n" + "=" * 60)
    print("[5] Демонстрация на реальных числах из второй криптограммы Бейла")
    print("=" * 60)
    
    beale_numbers = [
        115, 73, 24, 807, 37, 52, 49, 17, 31, 62, 647, 22, 7, 15, 140,
        47, 29, 107, 79, 84, 56, 239, 10, 26, 811, 5, 196, 308, 85, 52,
        160, 136, 59, 211, 36, 9, 46, 316, 554, 122
    ]
    
    print(f"Числа: {beale_numbers[:10]}...")
    
    # Используем полный текст Декларации (а не только 115 слов)
    # Расшифруем первые несколько чисел
    print("\nРасшифровка первых 10 чисел:")
    result_parts = []
    for i, num in enumerate(beale_numbers[:10], 1):
        if num in cipher.word_map:
            letter = cipher.word_map[num]
            word = cipher.words[num - 1] if num <= len(cipher.words) else "???"
            result_parts.append(letter)
            print(f"  {num} -> слово #{num} = '{word[:30]}' -> первая буква '{letter}'")
        else:
            print(f"  {num} -> [НЕ НАЙДЕНО в тексте-ключе]")
    
    print(f"\nРезультат: {''.join(result_parts)}")
    print("(ожидается: 'I have depo...' — I, H, A, V, E, D, E, P, O, S)")
    
    # 7. Сохранение результата в файл
    print("\n[6] Сохранение результатов...")
    with open('beale_decrypted.txt', 'w', encoding = 'utf-8') as f:
        f.write("=== Расшифровка криптограмм Бейла ===\n\n")
        f.write(f"Текст-ключ: Декларация независимости США\n")
        f.write(f"Количество слов в ключе: {cipher.word_count}\n\n")
        f.write(f"Пример шифрования: {plaintext}\n")
        f.write(f"Числа: {encrypted[:30]}...\n")
        f.write(f"Расшифровка: {decrypted}\n")
    
    print("Результаты сохранены в файл 'beale_decrypted.txt'")


if __name__ == "__main__":
    main()