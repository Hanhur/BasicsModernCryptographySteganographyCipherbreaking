# Пример кодирования одного блока с помощью SHA-1
def sha1(message_bytes):
    """
    Реализация SHA-1 на чистом Python
    Вход: байтовые данные (message_bytes)
    Выход: hex-строка дайджеста (160 бит)
    """
    
    # Шаг 2: Инициализация хеш-значений (как в примере)
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    # Шаг 1: Дополнение сообщения
    # Переводим байты в биты (для наглядности)
    original_bit_length = len(message_bytes) * 8
    
    # Добавляем байт 0x80 (единичный бит + нули)
    padded = bytearray(message_bytes)
    padded.append(0x80)
    
    # Добавляем нулевые байты, пока длина не станет 56 байт (448 бит) по модулю 64
    while len(padded) % 64 != 56:
        padded.append(0x00)
    
    # Добавляем 64-битную длину исходного сообщения (в битах, big-endian)
    padded.extend(original_bit_length.to_bytes(8, byteorder = 'big'))
    
    # Вспомогательные функции
    def left_rotate(n, b):
        """Циклический сдвиг влево на b бит (32-битные числа)"""
        return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF
    
    # Обработка каждого блока по 512 бит (64 байта)
    for chunk_start in range(0, len(padded), 64):
        chunk = padded[chunk_start:chunk_start + 64]
        
        # Шаг 3: Создание расписания сообщения W[0..79]
        w = [0] * 80
        
        # Первые 16 слов (W[0]..W[15]) - копируем из блока
        for i in range(16):
            w[i] = int.from_bytes(chunk[i * 4:i * 4 + 4], byteorder = 'big')
        
        # Расширяем до 80 слов (W[16]..W[79])
        for i in range(16, 80):
            w[i] = left_rotate(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)
        
        # Инициализация рабочих переменных
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        
        # Основной цикл: 4 раунда по 20 шагов
        for i in range(80):
            if 0 <= i <= 19:
                # Раунд 1
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= i <= 39:
                # Раунд 2
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                # Раунд 3
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:  # 60 <= i <= 79
                # Раунд 4
                f = b ^ c ^ d
                k = 0xCA62C1D6
            
            # Основная операция SHA-1
            temp = (left_rotate(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
        
        # Шаг: Сложение с предыдущими значениями (как в вашем примере)
        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF
        h4 = (h4 + e) & 0xFFFFFFFF
    
    # Шаг 4: Формирование дайджеста (160 бит = 40 hex символов)
    digest = f"{h0:08x}{h1:08x}{h2:08x}{h3:08x}{h4:08x}"
    return digest


def demonstrate_example():
    """Демонстрация работы на примере из вашего текста"""
    
    print("=" * 60)
    print("ПРИМЕР: Вычисление SHA-1 для строки 'abc'")
    print("=" * 60)
    
    # Шаг 1: Подготовка данных
    message = "abc"
    message_bytes = message.encode('ascii')
    
    print(f"\n1. Исходное сообщение: '{message}'")
    print(f"   В hex: {message_bytes.hex()}")
    print(f"   Длина: {len(message_bytes) * 8} бит")
    
    # Показываем дополнение (как в вашем тексте)
    padded = bytearray(message_bytes)
    padded.append(0x80)
    while len(padded) % 64 != 56:
        padded.append(0x00)
    padded.extend((len(message_bytes) * 8).to_bytes(8, byteorder = 'big'))
    
    print("\n2. Дополненный блок (первые 64 байта):")
    print(f"   W[0] = {padded[0:4].hex()}  (61626380 - бит 1 и нули)")
    print(f"   W[14] = {padded[56:60].hex()}  (нули)")
    print(f"   W[15] = {padded[60:64].hex()}  (длина = 24 = 0x18)")
    
    # Вычисляем хеш
    digest = sha1(message_bytes)
    
    print("\n3. Результат (как в вашем примере):")
    print(f"   A9993E36 4706816A BA3E2571 7850C26C 9CD0D89D")
    print(f"\n4. Наш результат:")
    # Форматируем для сравнения
    formatted = ' '.join([digest[i:i + 8] for i in range(0, 40, 8)])
    print(f"   {formatted}")
    
    print("\n5. Проверка совпадения:")
    expected = "a9993e364706816aba3e25717850c26c9cd0d89d"
    if digest == expected:
        print("   ✓ СОВПАДАЕТ с официальным SHA-1 для 'abc'!")
    else:
        print("   ✗ НЕ СОВПАДАЕТ (ошибка в реализации)")
    
    print("\n" + "=" * 60)


def test_additional():
    """Тест с другими известными примерами"""
    
    print("\nДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ:")
    print("-" * 40)
    
    # Тест 1: Пустая строка
    empty_hash = sha1(b"")
    print(f"Пустая строка: {empty_hash}")
    print(f"Ожидается:      da39a3ee5e6b4b0d3255bfef95601890afd80709")
    
    # Тест 2: Строка "The quick brown fox jumps over the lazy dog"
    fox = b"The quick brown fox jumps over the lazy dog"
    fox_hash = sha1(fox)
    print(f"\n'fox' хеш: {fox_hash}")
    print(f"Ожидается: 2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
    
    print("-" * 40)


if __name__ == "__main__":
    # Запускаем демонстрацию на примере из текста
    demonstrate_example()
    
    # Дополнительные тесты
    test_additional()
    
    # Интерактивный режим
    print("\nИНТЕРАКТИВНЫЙ РЕЖИМ:")
    print("-" * 40)
    user_input = input("Введите строку для хеширования (или нажмите Enter для выхода): ")
    if user_input:
        result = sha1(user_input.encode('utf-8'))
        print(f"SHA-1 хеш: {result}")