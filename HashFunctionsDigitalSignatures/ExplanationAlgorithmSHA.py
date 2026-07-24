# Объяснение алгоритма SHA-1
def sha1(message: bytes) -> str:
    """
    Реализация алгоритма SHA-1.
    Вход: сообщение в виде байтов
    Выход: 160-битное хеш-значение в шестнадцатеричном формате
    """
    
    # Шаг 1: Инициализация регистров (константы)
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    # Вспомогательные функции для циклического сдвига влево
    def left_rotate(n: int, b: int) -> int:
        """Циклический сдвиг 32-битного числа n влево на b бит"""
        return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF
    
    # Шаг 2: Подготовка сообщения (дополнение и разбиение)
    # 2.1: Добавляем бит '1' (0x80 = 10000000)
    msg = bytearray(message)
    msg.append(0x80)
    
    # 2.2: Добавляем нулевые биты до 448 бит (56 байт) от начала
    # Оставляем 8 байт (64 бита) для длины
    while len(msg) % 64 != 56:
        msg.append(0x00)
    
    # 2.3: Добавляем исходную длину сообщения в битах (64 бита, big-endian)
    msg += (len(message) * 8).to_bytes(8, byteorder = 'big')
    
    # Шаг 3: Обработка блоков по 512 бит (64 байта)
    for i in range(0, len(msg), 64):
        # 3.1: Разбиваем блок на 16 слов по 32 бита
        w = [0] * 80
        for j in range(16):
            # Берем 4 байта из блока и преобразуем в 32-битное число (big-endian)
            w[j] = int.from_bytes(msg[i + j * 4 : i + j * 4 + 4], byteorder = 'big')
        
        # 3.2: Расширение сообщения до 80 слов
        for j in range(16, 80):
            w[j] = left_rotate(w[j - 3] ^ w[j - 8] ^ w[j - 14] ^ w[j - 16], 1)
        
        # 3.3: Инициализация рабочих переменных
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        
        # 3.4: Главный цикл (80 раундов)
        for j in range(80):
            # Определяем логическую функцию f и константу K в зависимости от раунда
            if 0 <= j <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:  # 60 <= j <= 79
                f = b ^ c ^ d
                k = 0xCA62C1D6
            
            # Вычисляем временную переменную T
            temp = (left_rotate(a, 5) + f + e + k + w[j]) & 0xFFFFFFFF
            
            # Обновляем регистры (сдвиг вправо)
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
        
        # 3.5: Добавляем результат к текущему хешу
        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF
        h4 = (h4 + e) & 0xFFFFFFFF
    
    # Шаг 4: Формирование финального хеша (конкатенация)
    hash_result = (h0 << 128) | (h1 << 96) | (h2 << 64) | (h3 << 32) | h4
    
    # Возвращаем в шестнадцатеричном формате с ведущими нулями
    return f"{hash_result:040x}"


# Функция для хеширования строки (удобный интерфейс)
def sha1_string(text: str) -> str:
    """
    Хеширует строку с кодировкой UTF-8
    """
    return sha1(text.encode('utf-8'))


# Функция для хеширования файла
def sha1_file(filepath: str) -> str:
    """
    Хеширует содержимое файла
    """
    with open(filepath, 'rb') as f:
        return sha1(f.read())


# Примеры использования
if __name__ == "__main__":
    # Тест 1: Пустая строка (известный хеш: da39a3ee5e6b4b0d3255bfef95601890afd80709)
    print("Пустая строка:")
    print(sha1_string(""))
    print("Ожидается: da39a3ee5e6b4b0d3255bfef95601890afd80709")
    print()
    
    # Тест 2: Строка "hello"
    print("Строка 'hello':")
    print(sha1_string("hello"))
    print("Ожидается: aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")
    print()
    
    # Тест 3: Строка "The quick brown fox jumps over the lazy dog"
    print("Строка 'The quick brown fox jumps over the lazy dog':")
    print(sha1_string("The quick brown fox jumps over the lazy dog"))
    print("Ожидается: 2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
    print()
    
    # Тест 4: Строка "abc"
    print("Строка 'abc':")
    print(sha1_string("abc"))
    print("Ожидается: a9993e364706816aba3e25717850c26c9cd0d89d")
    print()
    
    # Тест 5: Строка с русским текстом
    print("Строка 'Привет мир!':")
    print(sha1_string("Привет мир!"))
    
    # Демонстрация хеширования файла (закомментировано, чтобы не было ошибки)
    print("\nХеш файла 'example.txt':")
    try:
        print(sha1_file("example.txt"))
    except FileNotFoundError:
        print("Файл не найден")