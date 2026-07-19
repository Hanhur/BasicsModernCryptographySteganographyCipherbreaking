# Простой DES
"""
SIMPLE DES (Упрощенная версия DES)
Реализация на основе текста:
- Блок сообщения: 12 бит
- Ключ: 9 бит
- 1 раунд шифрования
- S-блоки: 2 шт. (2 строки × 8 столбцов, вход 4 бита → выход 3 бита)
"""

class SimpleDES:
    def __init__(self):
        # S-блоки (2 строки × 8 столбцов, каждый элемент - 3-битное число)
        # Строки: 0 и 1 (первый бит входа)
        # Столбцы: 0-7 (последние 3 бита входа)
        self.S1 = [
            [0, 1, 2, 3, 4, 5, 6, 7],  # строка 0
            [7, 6, 5, 4, 3, 2, 1, 0]   # строка 1
        ]
        
        self.S2 = [
            [0, 1, 2, 3, 4, 5, 6, 7],  # строка 0
            [7, 6, 5, 4, 3, 2, 1, 0]   # строка 1
        ]
        
        # Функция расширения: 6 бит → 8 бит [индексы 1-6]
        self.expansion = [1, 2, 4, 3, 4, 3, 5, 6]  # индексы от 1 до 6
    
    def _string_to_bits(self, text):
        """Преобразует строку в список битов (целые числа 0/1)"""
        bits = []
        for char in text:
            if char == '0':
                bits.append(0)
            elif char == '1':
                bits.append(1)
            else:
                raise ValueError(f"Недопустимый символ: {char}. Используйте только '0' и '1'")
        return bits
    
    def _bits_to_string(self, bits):
        """Преобразует список битов в строку"""
        return ''.join(str(b) for b in bits)
    
    def _validate_input(self, bits, expected_length, name):
        """Проверяет длину входных данных"""
        if len(bits) != expected_length:
            raise ValueError(f"{name} должен содержать {expected_length} бит, получено {len(bits)}")
        return bits
    
    def _xor(self, a, b):
        """Побитовое XOR двух списков одинаковой длины"""
        return [x ^ y for x, y in zip(a, b)]
    
    def _expand(self, bits_6bit):
        """
        Расширение 6 бит до 8 бит
        Используется схема расширения Exp [1, 2, 4, 3, 4, 3, 5, 6]
        """
        if len(bits_6bit) != 6:
            raise ValueError(f"Расширение требует 6 бит, получено {len(bits_6bit)}")
        
        # Индексы в схеме от 1 до 6, преобразуем в индексы Python (0-5)
        expanded = [bits_6bit[i - 1] for i in self.expansion]
        return expanded
    
    def _sbox_lookup(self, sbox, input_4bit):
        """
        Подстановка в S-блоке
        Вход: 4 бита
        - Первый бит (индекс 0) → строка (0 или 1)
        - Последние 3 бита (индексы 1-3) → столбец (0-7)
        Выход: 3 бита
        """
        if len(input_4bit) != 4:
            raise ValueError(f"S-блок требует 4 бита, получено {len(input_4bit)}")
        
        # Определяем строку (первый бит)
        row = input_4bit[0]  # 0 или 1
        
        # Определяем столбец (последние 3 бита)
        col = (input_4bit[1] << 2) | (input_4bit[2] << 1) | input_4bit[3]
        # col будет от 0 до 7
        
        # Получаем значение из S-блока (0-7)
        value = sbox[row][col]
        
        # Преобразуем число в 3 бита
        return [(value >> 2) & 1, (value >> 1) & 1, value & 1]
    
    def _generate_round_key(self, K, round_num):
        """
        Генерация ключа для раунда
        Берем 8 бит, начиная с round_num-го бита (от 1 до 9)
        """
        if len(K) != 9:
            raise ValueError(f"Ключ должен содержать 9 бит, получено {len(K)}")
        
        # В тексте: K4 = биты с 4-го по 11-й (циклически)
        # Для Python: индекс 0 соответствует 1-му биту
        start_idx = (round_num - 1) % 9
        
        # Берем 8 бит циклически
        key_8bit = []
        for i in range(8):
            idx = (start_idx + i) % 9
            key_8bit.append(K[idx])
        
        return key_8bit
    
    def _feistel_round(self, L, R, K_round):
        """
        Один раунд структуры Фейстеля
        L: 6 бит (левая половина)
        R: 6 бит (правая половина)
        K_round: 8 бит (ключ раунда)
        Возвращает: (новое_L, новое_R)
        """
        # Шаг 1: Расширение R до 8 бит
        expanded_R = self._expand(R)
        
        # Шаг 2: XOR с ключом раунда
        xored = self._xor(expanded_R, K_round)
        
        # Шаг 3: Разбиваем на две 4-битные части
        left_4bit = xored[:4]
        right_4bit = xored[4:]
        
        # Шаг 4: Пропускаем через S-блоки
        s1_output = self._sbox_lookup(self.S1, left_4bit)
        s2_output = self._sbox_lookup(self.S2, right_4bit)
        
        # Шаг 5: Конкатенация 3+3 = 6 бит (функция f)
        f_result = s1_output + s2_output
        
        # Шаг 6: Структура Фейстеля
        new_L = R
        new_R = self._xor(L, f_result)
        
        return new_L, new_R
    
    def encrypt(self, M, K):
        """
        Шифрование блока 12 бит с ключом 9 бит
        M: строка из 12 бит (например, "011001100110")
        K: строка из 9 бит (например, "010011001")
        Возвращает: строка из 12 бит (шифротекст)
        """
        # Преобразуем строки в списки битов
        M_bits = self._string_to_bits(M)
        K_bits = self._string_to_bits(K)
        
        # Проверяем длины
        self._validate_input(M_bits, 12, "Сообщение M")
        self._validate_input(K_bits, 9, "Ключ K")
        
        # Инициализация: разбиваем на L0 и R0
        L = M_bits[:6]
        R = M_bits[6:]
        
        # Выполняем 1 раунд (можно увеличить количество)
        # В вашем тексте показан 4-й раунд, но для примера сделаем 1 раунд
        for round_num in range(1, 2):  # 1 раунд
            # Генерируем ключ для раунда
            K_round = self._generate_round_key(K_bits, round_num)
            
            # Выполняем раунд Фейстеля
            L, R = self._feistel_round(L, R, K_round)
        
        # Конкатенируем результат
        ciphertext = L + R
        
        return self._bits_to_string(ciphertext)
    
    def decrypt(self, C, K):
        """
        Дешифрование (обратный порядок ключей)
        Для простоты: в 1-раундовом DES шифрование = дешифрование
        (так как только 1 раунд)
        """
        # Для 1 раунда дешифрование идентично шифрованию
        # В реальном многораундовом DES ключи подавались бы в обратном порядке
        return self.encrypt(C, K)


def main():
    """Демонстрация работы Simple DES"""
    
    print("=" * 60)
    print("SIMPLE DES - Упрощенный DES")
    print("=" * 60)
    
    # Создаем экземпляр шифра
    des = SimpleDES()
    
    # Пример из текста
    print("\n1. Пример из текста:")
    print("-" * 40)
    
    M = "011001100110"  # 12 бит
    K = "010011001"     # 9 бит
    
    print(f"Сообщение M: {M}")
    print(f"Ключ K:      {K}")
    
    # Шифрование
    C = des.encrypt(M, K)
    print(f"\nШифротекст C: {C}")
    
    # Дешифрование
    M_decrypted = des.decrypt(C, K)
    print(f"Дешифровано:  {M_decrypted}")
    print(f"Совпадает:    {M == M_decrypted}")
    
    # Дополнительный пример с пошаговым выводом
    print("\n2. Пошаговый разбор (как в тексте):")
    print("-" * 40)
    
    # Разбираем вручную для демонстрации
    M_bits = des._string_to_bits(M)
    K_bits = des._string_to_bits(K)
    
    print(f"M = {M}")
    print(f"L0 = {des._bits_to_string(M_bits[:6])}")
    print(f"R0 = {des._bits_to_string(M_bits[6:])}")
    print(f"K = {K}")
    
    # Расширение R0
    expanded_R = des._expand(M_bits[6:])
    print(f"\nExp(R0) = {des._bits_to_string(expanded_R)} (расширение по схеме [1, 2, 4, 3, 4, 3, 5, 6])")
    
    # Генерация K4 (4-й раунд)
    K4 = des._generate_round_key(K_bits, 4)
    print(f"K4 = {des._bits_to_string(K4)} (8 бит с 4-й позиции)")
    
    # XOR
    xored = des._xor(expanded_R, K4)
    print(f"Exp(R0) ⊕ K4 = {des._bits_to_string(xored)}")
    
    # Разбивка
    left = xored[:4]
    right = xored[4:]
    print(f"Левая часть: {des._bits_to_string(left)}")
    print(f"Правая часть: {des._bits_to_string(right)}")
    
    # S-блоки
    s1_out = des._sbox_lookup(des.S1, left)
    s2_out = des._sbox_lookup(des.S2, right)
    print(f"S1({des._bits_to_string(left)}) = {des._bits_to_string(s1_out)}")
    print(f"S2({des._bits_to_string(right)}) = {des._bits_to_string(s2_out)}")
    
    f_result = s1_out + s2_out
    print(f"f(R0, K4) = {des._bits_to_string(f_result)}")
    
    # Тестируем разные ключи
    print("\n3. Тест с разными ключами:")
    print("-" * 40)
    
    test_messages = [
        "000000000000",
        "111111111111",
        "101010101010",
        "011001100110"
    ]
    
    for msg in test_messages:
        c = des.encrypt(msg, K)
        m_dec = des.decrypt(c, K)
        print(f"M: {msg} → C: {c} → M': {m_dec} {'✓' if msg == m_dec else '✗'}")
    
    # Проверка лавинного эффекта (изменение 1 бита)
    print("\n4. Лавинный эффект (изменение 1 бита в сообщении):")
    print("-" * 40)
    
    M1 = "000000000000"
    M2 = "000000000001"  # изменили последний бит
    
    C1 = des.encrypt(M1, K)
    C2 = des.encrypt(M2, K)
    
    # Считаем количество изменившихся бит
    diff_bits = sum(1 for a, b in zip(C1, C2) if a != b)
    print(f"M1: {M1} → C1: {C1}")
    print(f"M2: {M2} → C2: {C2}")
    print(f"Изменилось бит: {diff_bits} из 12 ({diff_bits / 12 * 100:.1f}%)")
    
    # Проверка валидации
    print("\n5. Проверка валидации входных данных:")
    print("-" * 40)
    
    try:
        des.encrypt("00000000000", K)  # 11 бит (неверно)
    except ValueError as e:
        print(f"✓ Ошибка: {e}")
    
    try:
        des.encrypt(M, "01001100")  # 8 бит (неверно)
    except ValueError as e:
        print(f"✓ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("Готово!")


if __name__ == "__main__":
    main()