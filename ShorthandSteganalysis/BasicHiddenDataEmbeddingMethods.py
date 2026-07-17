# Основные методы встраивания скрытых данных
"""
Стеганография: LSB Matching для 24-битных BMP изображений
Версия без NumPy - использует только стандартные библиотеки Python
"""

from PIL import Image
import random
import struct
import os
import math


class LSBMatcher:
    """
    Реализация LSB Matching для 24-битных BMP
    Использует сложение/вычитание с переносами как описано в тексте
    """
    
    def __init__(self, seed = None):
        """
        Инициализация с секретным ключом (seed для псевдослучайного генератора)
        """
        self.seed = seed
        self.random = random.Random(seed) if seed is not None else random.Random()
    
    def _embed_bit(self, pixel_value, bit, random_sign):
        """
        Встраивание одного бита с использованием LSB matching
        Согласно формуле из текста:
        x_i = x_i, если LSB(x_i) == m_i
        x_i + r_i, если LSB(x_i) != m_i и x_i != 0, x_i != 255
        x_i + 1, если LSB(x_i) != m_i и x_i == 0
        x_i - 1, если LSB(x_i) != m_i и x_i == 255
        """
        lsb = pixel_value & 1  # LSB(x_i)
        
        if lsb == bit:
            return pixel_value
        else:
            # Случайный выбор: +1 или -1
            r = random_sign if random_sign is not None else self.random.choice([-1, 1])
            
            if pixel_value == 0:
                return pixel_value + 1
            elif pixel_value == 255:
                return pixel_value - 1
            else:
                return pixel_value + r
    
    def embed_data(self, image_path, data, output_path):
        """
        Встраивание данных в изображение
        data: битовая строка (строка из '0' и '1') или список битов
        """
        # Загрузка изображения
        img = Image.open(image_path)
        # Преобразуем в режим RGB для работы с цветами
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = list(img.getdata())  # Получаем все пиксели как список RGB кортежей
        
        # Преобразуем данные в список битов
        if isinstance(data, str):
            bits = [int(b) for b in data]
        elif isinstance(data, list):
            bits = [int(b) for b in data]
        elif isinstance(data, bytes):
            bits = []
            for byte in data:
                for i in range(7, -1, -1):
                    bits.append((byte >> i) & 1)
        else:
            raise ValueError("Data must be string of bits, list, or bytes")
        
        # Общее количество компонентов (R, G, B для каждого пикселя)
        total_components = len(pixels) * 3
        if len(bits) > total_components:
            raise ValueError(f"Data too large! Max bits: {total_components}")
        
        # Создаем список позиций для встраивания
        positions = list(range(total_components))
        self.random.shuffle(positions)
        positions = positions[:len(bits)]
        
        # Преобразуем пиксели в плоский список компонентов (R, G, B последовательно)
        flat_pixels = []
        for pixel in pixels:
            flat_pixels.extend(pixel)
        
        # Встраиваем биты
        idx = 0
        for pos in positions:
            # Генерируем случайный знак для операции
            r = self.random.choice([-1, 1])
            # Встраиваем бит
            flat_pixels[pos] = self._embed_bit(flat_pixels[pos], bits[idx], r)
            idx += 1
        
        # Преобразуем обратно в список пикселей
        new_pixels = []
        for i in range(0, len(flat_pixels), 3):
            new_pixels.append(tuple(flat_pixels[i:i + 3]))
        
        # Сохраняем результат
        result_img = Image.new('RGB', (width, height))
        result_img.putdata(new_pixels)
        result_img.save(output_path)
        print(f"Data embedded successfully! Saved to {output_path}")
        return len(bits)
    
    def extract_data(self, image_path, num_bits):
        """
        Извлечение данных из изображения
        num_bits: количество бит для извлечения
        """
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = list(img.getdata())
        
        # Общее количество компонентов
        total_components = len(pixels) * 3
        
        # Получаем те же позиции, что и при встраивании
        positions = list(range(total_components))
        self.random.shuffle(positions)
        positions = positions[:num_bits]
        
        # Преобразуем пиксели в плоский список
        flat_pixels = []
        for pixel in pixels:
            flat_pixels.extend(pixel)
        
        # Извлекаем биты
        bits = []
        for pos in positions:
            bit = flat_pixels[pos] & 1
            bits.append(bit)
        
        return bits
    
    def embed_message(self, image_path, message, output_path):
        """
        Встраивание текстового сообщения
        """
        # Конвертируем сообщение в байты
        data_bytes = message.encode('utf-8')
        
        # Добавляем длину сообщения (4 байта) в начало
        length_bytes = struct.pack('>I', len(data_bytes))
        full_data = length_bytes + data_bytes
        
        # Конвертируем в биты
        bits = []
        for byte in full_data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        return self.embed_data(image_path, bits, output_path)
    
    def extract_message(self, image_path):
        """
        Извлечение текстового сообщения
        """
        # Сначала извлекаем длину сообщения (32 бита = 4 байта)
        length_bits = self.extract_data(image_path, 32)
        
        # Преобразуем в длину
        length_bytes = 0
        for i, bit in enumerate(length_bits):
            length_bytes = (length_bytes << 1) | bit
        
        # Извлекаем само сообщение
        message_bits = self.extract_data(image_path, 32 + length_bytes * 8)
        
        # Извлекаем только биты сообщения
        message_bits = message_bits[32:]
        
        # Преобразуем биты в байты
        message_bytes = bytearray()
        for i in range(0, len(message_bits), 8):
            if i + 8 <= len(message_bits):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | message_bits[i + j]
                message_bytes.append(byte_val)
        
        try:
            return message_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return message_bytes


class TextSteganography:
    """
    Метод встраивания в текстовые синонимы
    Как описано в тексте: "большой - крупный" и т.д.
    """
    
    # Словарь синонимов как в тексте
    SYNONYMS = {
        'большой': ('большой', 'крупный'),
        'умный': ('умный', 'способный'),
        'летчик': ('летчик', 'пилот'),
        'хороший': ('хороший', 'отличный'),
        'красивый': ('красивый', 'прекрасный'),
        'быстрый': ('быстрый', 'скорый'),
        'сильный': ('сильный', 'мощный'),
        'маленький': ('маленький', 'небольшой'),
        'говорить': ('говорить', 'сказать'),
        'видеть': ('видеть', 'замечать'),
        'работать': ('работать', 'трудиться'),
        'знать': ('знать', 'понимать'),
        'идти': ('идти', 'шагать'),
        'смотреть': ('смотреть', 'глядеть')
    }
    
    def __init__(self, synonyms_dict = None):
        if synonyms_dict:
            self.synonyms = synonyms_dict
        else:
            self.synonyms = self.SYNONYMS
    
    def encode_text(self, text, message_bits):
        """
        Встраивание битов в текст через выбор синонимов
        Возвращает закодированный текст и количество встроенных бит
        """
        words = text.split()
        result = words.copy()
        bit_idx = 0
        
        # Создаем обратный словарь для быстрого поиска
        reverse_dict = {}
        for key, (syn1, syn2) in self.synonyms.items():
            reverse_dict[syn1] = key
            reverse_dict[syn2] = key
        
        for i, word in enumerate(result):
            if bit_idx >= len(message_bits):
                break
                
            if word in reverse_dict:
                key = reverse_dict[word]
                syn_pair = self.synonyms[key]
                
                if message_bits[bit_idx] == 0:
                    result[i] = syn_pair[0]
                else:
                    result[i] = syn_pair[1]
                bit_idx += 1
        
        return ' '.join(result), bit_idx
    
    def decode_text(self, text):
        """
        Извлечение битов из текста по синонимам
        """
        words = text.split()
        bits = []
        
        # Создаем словари для кодирования
        encoding = {}
        for key, (syn0, syn1) in self.synonyms.items():
            encoding[syn0] = 0
            encoding[syn1] = 1
        
        for word in words:
            if word in encoding:
                bits.append(encoding[word])
        
        return bits
    
    def encode_message(self, text, message):
        """
        Встраивает текстовое сообщение в виде битов
        """
        # Преобразуем сообщение в биты
        bits = []
        for char in message:
            byte_val = ord(char)
            for i in range(7, -1, -1):
                bits.append((byte_val >> i) & 1)
        
        return self.encode_text(text, bits)
    
    def decode_message(self, text, num_chars):
        """
        Извлекает текстовое сообщение заданной длины
        """
        bits = self.decode_text(text)
        
        message = ""
        for i in range(0, min(len(bits), num_chars * 8), 8):
            if i + 8 <= len(bits):
                char_code = 0
                for j in range(8):
                    char_code = (char_code << 1) | bits[i + j]
                message += chr(char_code)
        
        return message


class BMPGenerator:
    """
    Вспомогательный класс для создания тестовых BMP изображений
    """
    
    @staticmethod
    def create_test_image(width, height, output_path):
        """
        Создает тестовое BMP изображение с градиентом
        """
        from PIL import Image, ImageDraw
        
        # Создаем новое изображение
        img = Image.new('RGB', (width, height))
        pixels = []
        
        # Создаем градиент
        for y in range(height):
            for x in range(width):
                r = (x + y) % 256
                g = (x * 2 + y) % 256
                b = (x + y * 2) % 256
                pixels.append((r, g, b))
        
        img.putdata(pixels)
        img.save(output_path)
        print(f"Test image created: {output_path} ({width} x {height})")
        return output_path


# ============ Примеры использования ============

def example_lsb_matching_formula():
    """
    Демонстрация формулы LSB matching из текста
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ФОРМУЛЫ LSB MATCHING")
    print("=" * 60)
    
    stego = LSBMatcher()
    
    # Тестовые значения
    test_values = [0, 1, 2, 127, 128, 254, 255]
    bit_to_embed = 0
    
    print(f"Встраиваем бит: {bit_to_embed}")
    print("-" * 60)
    print("Исходное | LSB | Результат | Изменение | Описание")
    print("-" * 60)
    
    for val in test_values:
        # Используем фиксированный знак для демонстрации
        new_val = stego._embed_bit(val, bit_to_embed, random_sign = 1)
        lsb = val & 1
        lsb_new = new_val & 1
        
        if val == 0:
            desc = "Спец. случай: min значение"
        elif val == 255:
            desc = "Спец. случай: max значение"
        else:
            desc = f"LSB {'совпадает' if lsb == bit_to_embed else 'не совпадает'}"
        
        print(f"{val:7} | {lsb:3} | {new_val:9} | {new_val - val:8} | {desc}")


def example_embed_message():
    """
    Пример встраивания сообщения в BMP
    """
    print("\n" + "=" * 60)
    print("ПРИМЕР: LSB MATCHING В BMP ИЗОБРАЖЕНИИ")
    print("=" * 60)
    
    # Создаем тестовое изображение
    test_image_path = 'test_image.bmp'
    
    if not os.path.exists(test_image_path):
        BMPGenerator.create_test_image(300, 200, test_image_path)
    
    # Инициализация с секретным ключом
    secret_key = 12345
    stego = LSBMatcher(seed = secret_key)
    
    # Сообщение для встраивания
    message = "Привет! Это секретное сообщение, встроенное методом LSB matching."
    print(f"\nОригинальное сообщение: {message}")
    print(f"Длина сообщения: {len(message)} символов")
    
    # Встраиваем сообщение
    output_path = 'output_with_secret.bmp'
    
    try:
        embedded_bits = stego.embed_message(test_image_path, message, output_path)
        print(f"Встроено бит: {embedded_bits}")
        
        # Извлекаем сообщение
        extracted = stego.extract_message(output_path)
        print(f"\nИзвлеченное сообщение: {extracted}")
        
        # Проверка соответствия
        print(f"\nУспешно извлечено: {'ДА' if message == extracted else 'НЕТ'}")
        print(f"Длина извлеченного сообщения: {len(extracted)} символов")
        
        # Сравнение размеров файлов
        original_size = os.path.getsize(test_image_path)
        hidden_size = os.path.getsize(output_path)
        print(f"\nРазмер оригинального файла: {original_size} байт")
        print(f"Размер файла со скрытым сообщением: {hidden_size} байт")
        print(f"Разница: {hidden_size - original_size} байт")
        
    except Exception as e:
        print(f"Ошибка: {e}")


def example_text_steganography():
    """
    Пример встраивания в текстовые синонимы
    """
    print("\n" + "=" * 60)
    print("ПРИМЕР: ТЕКСТОВАЯ СТЕГАНОГРАФИЯ (СИНОНИМЫ)")
    print("=" * 60)
    
    text_stego = TextSteganography()
    
    # Исходный текст
    original_text = "большой умный летчик хороший красивый быстрый сильный маленький говорить видеть"
    secret_bits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0]  # Бинарное сообщение
    
    print(f"\nОригинальный текст: {original_text}")
    print(f"Скрытые биты: {secret_bits}")
    
    # Встраиваем
    encoded_text, bits_embedded = text_stego.encode_text(original_text, secret_bits)
    print(f"\nТекст со встроенным сообщением:")
    print(encoded_text)
    print(f"Встроено бит: {bits_embedded}")
    
    # Извлекаем
    extracted_bits = text_stego.decode_text(encoded_text)
    print(f"Извлеченные биты: {extracted_bits}")
    
    # Проверка
    success = secret_bits == extracted_bits[:len(secret_bits)]
    print(f"Успешно извлечено: {'ДА' if success else 'НЕТ'}")


def example_encrypt_message():
    """
    Пример кодирования текстового сообщения через синонимы
    """
    print("\n" + "=" * 60)
    print("ПРИМЕР: КОДИРОВАНИЕ ТЕКСТОВОГО СООБЩЕНИЯ ЧЕРЕЗ СИНОНИМЫ")
    print("=" * 60)
    
    text_stego = TextSteganography()
    
    # Текст-контейнер
    container = "большой умный летчик хороший красивый быстрый сильный маленький говорить видеть работать знать идти смотреть"
    
    # Сообщение для встраивания
    secret_message = "Привет"
    
    print(f"Текст-контейнер:")
    print(container)
    print(f"\nСообщение для встраивания: {secret_message}")
    
    # Кодируем
    encoded, bits_embedded = text_stego.encode_message(container, secret_message)
    print(f"\nЗакодированный текст:")
    print(encoded)
    print(f"Встроено бит: {bits_embedded}")
    
    # Декодируем
    decoded = text_stego.decode_message(encoded, len(secret_message))
    print(f"\nИзвлеченное сообщение: {decoded}")
    print(f"Успешно: {'ДА' if decoded == secret_message else 'НЕТ'}")


def demo_original_lsb_concept():
    """
    Демонстрация оригинальной концепции LSB из текста
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ КОНЦЕПЦИИ LSB (ИСТОРИЧЕСКИЙ ПРИМЕР)")
    print("=" * 60)
    
    print("\nКак в таблицах логарифмов в Средние века:")
    print("-" * 60)
    
    # Пример из текста: 0.2284938 -> 0.2284939
    original = 0.2284938
    modified = 0.2284939
    print(f"Оригинальное значение: {original}")
    print(f"Измененное значение:  {modified}")
    print(f"Изменение: +{modified - original}")
    
    print("\nВ двоичном представлении (8 бит):")
    
    # Демонстрация LSB в двоичных числах
    numbers = [168, 169, 170, 171]
    print("Число | Двоичное представление | LSB")
    print("-" * 45)
    for n in numbers:
        binary = format(n, '08b')
        lsb = n & 1
        print(f"{n:5} | {binary} | {lsb}")
    
    print("\nВстраивание бита '0':")
    for n in numbers:
        new_n = n if (n & 1) == 0 else n - 1
        print(f"{n} -> {new_n} (LSB: {n & 1} -> {new_n & 1})")
    
    print("\nВстраивание бита '1':")
    for n in numbers:
        new_n = n if (n & 1) == 1 else n + 1
        print(f"{n} -> {new_n} (LSB: {n & 1} -> {new_n & 1})")


if __name__ == "__main__":
    print("=" * 60)
    print("LSB MATCHING - СТЕГАНОГРАФИЯ")
    print("На основе текста '10.2. Основные методы встраивания скрытых данных'")
    print("=" * 60)
    
    # Проверяем наличие PIL
    try:
        import PIL
        print("✓ PIL (Pillow) установлена")
    except ImportError:
        print("✗ Установите PIL: pip install Pillow")
        exit(1)
    
    # Запускаем демонстрации
    demo_original_lsb_concept()
    example_lsb_matching_formula()
    
    # Пример с изображением
    try:
        example_embed_message()
    except Exception as e:
        print(f"\nОшибка в примере с изображением: {e}")
    
    # Примеры с текстом
    example_text_steganography()
    example_encrypt_message()
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)