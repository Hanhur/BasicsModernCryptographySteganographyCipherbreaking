# 2. Оцифровка 
# -*- coding: utf-8 -*-

# ========== СЛОВАРИ ДЛЯ ОЦИФРОВКИ БУКВ ==========

# Русский алфавит (33 буквы, включая ё)
RUS_ALPH = {chr(ord('а') + i): i for i in range(32)}  # а-я без ё
RUS_ALPH['ё'] = 6  # ё на своём месте
# Добавим ё в правильном порядке (после е)
RUS_ALPH = {k: v for k, v in sorted(RUS_ALPH.items(), key = lambda x: x[1])}
RUS_TO_NUM = RUS_ALPH
RUS_NUM_TO_LETTER = {v: k for k, v in RUS_TO_NUM.items()}

# Английский алфавит (26 букв)
ENG_ALPH = {chr(ord('a') + i): i for i in range(26)}
ENG_TO_NUM = ENG_ALPH
ENG_NUM_TO_LETTER = {v: k for k, v in ENG_TO_NUM.items()}

# Искусственный алфавит Ы (8 символов: a, &, a, ?, 1, 2, 7, пробел)
# Внимание: два разных 'a'? В исходнике написано: "а & а ? 1 2 7 _"
# Первый а — возможно, латинская 'a'? Сохраним как есть.
ART_ALPH_SYMBOLS = ['a', '&', 'а', '?', '1', '2', '7', '_']
ART_TO_NUM = {ch: i for i, ch in enumerate(ART_ALPH_SYMBOLS)}
ART_NUM_TO_SYMBOL = {i: ch for i, ch in enumerate(ART_ALPH_SYMBOLS)}

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========

def digitize_text(text, alphabet_map):
    """
    Оцифровка текста: каждый символ -> число.
    Возвращает список чисел.
    """
    return [alphabet_map[ch] for ch in text]

def text_from_digits(digits, num_to_symbol_map):
    """
    Восстановление текста из списка чисел.
    """
    return ''.join(num_to_symbol_map[d] for d in digits)

def digitize_kgram(kgram, base):
    """
    Оцифровка k-графа (последовательности цифр) как числа в системе счисления base.
    kgram: список чисел [a_{k-1}, a_{k-2}, ..., a_0]
    Формула: a0 + a1*base + a2*base^2 + ... + a_{k-1}*base^{k-1}
    """
    result = 0
    for power, digit in enumerate(kgram):
        result += digit * (base ** power)
    return result

def kgram_from_number(number, k, base):
    """
    Восстановление k-графа из числа.
    Возвращает список цифр [a_{k-1}, ..., a_0] (младший разряд слева? нет — в порядке исходной записи)
    Здесь вернём в порядке от старшего к младшему для удобства.
    """
    digits = []
    temp = number
    for _ in range(k):
        digits.append(temp % base)
        temp //= base
    return digits[::-1]  # возвращаем [a_{k-1}, ..., a_0]

def to_binary_sequence(digits, bits_per_symbol):
    """
    Преобразует список чисел (каждое < 2^bits_per_symbol) в бинарную строку.
    """
    binary_str = ''
    for num in digits:
        binary_str += format(num, f'0{bits_per_symbol}b')
    return binary_str

def from_binary_sequence(binary_str, bits_per_symbol):
    """
    Восстанавливает список чисел из бинарной строки.
    """
    digits = []
    for i in range(0, len(binary_str), bits_per_symbol):
        chunk = binary_str[i:i + bits_per_symbol]
        if len(chunk) == bits_per_symbol:
            digits.append(int(chunk, 2))
    return digits

# ========== ПРИМЕРЫ ИЗ ТЕКСТА ==========

if __name__ == '__main__':
    print("=== ОЦИФРОВКА ПО ТЕКСТУ ЛЕКЦИИ ===\n")
    
    # 1. Русский текст "ястудентуниверситета"
    text_rus = "ястудентуниверситета"
    digits_rus = digitize_text(text_rus, RUS_TO_NUM)
    print(f"Текст: {text_rus}")
    print(f"Оцифровка: {digits_rus}")
    restored_rus = text_from_digits(digits_rus, RUS_NUM_TO_LETTER)
    print(f"Восстановлено: {restored_rus}\n")
    
    # 2. Английский текст "iamastudent"
    text_eng = "iamastudent"
    digits_eng = digitize_text(text_eng, ENG_TO_NUM)
    print(f"Текст: {text_eng}")
    print(f"Оцифровка: {digits_eng}")
    restored_eng = text_from_digits(digits_eng, ENG_NUM_TO_LETTER)
    print(f"Восстановлено: {restored_eng}\n")
    
    # 3. Восстановление по числам [15, 13, 18, 11] → "омск"
    test_omsk = [15, 13, 18, 11]
    word_omsk = text_from_digits(test_omsk, RUS_NUM_TO_LETTER)
    print(f"Числа {test_omsk} → слово: {word_omsk}\n")
    
    # 4. Искусственный алфавит Ы: текст "а&21_7"
    text_art = "а&21_7"  # символы: a, &, 2, 1, _, 7
    # Заметим: в исходнике пример "а&21_7" оцифровывается как 0,1,5,4,7,3
    # Проверим:
    digits_art = digitize_text(text_art, ART_TO_NUM)
    print(f"Алфавит Ы, текст: {text_art}")
    print(f"Оцифровка: {digits_art}")
    restored_art = text_from_digits(digits_art, ART_NUM_TO_SYMBOL)
    print(f"Восстановлено: {restored_art}\n")
    
    # 5. Оцифровка k-графа: пример с русским 3-графом "год"
    kgram_rus = "год"
    digits_kgram = digitize_text(kgram_rus, RUS_TO_NUM)
    print(f"3-граф '{kgram_rus}' → цифры: {digits_kgram}")
    num_kgram = digitize_kgram(digits_kgram, base = 33)
    print(f"Число в 33-ричной системе: {num_kgram}")
    restored_kgram = kgram_from_number(num_kgram, k = 3, base = 33)
    print(f"Из числа {num_kgram} обратно цифры: {restored_kgram}")
    print(f"Восстановленный текст: {text_from_digits(restored_kgram, RUS_NUM_TO_LETTER)}\n")
    
    # 6. Бинарные последовательности для алфавита Ы (8 = 2^3 символов)
    bits_per_symbol = 3
    binary_repr = to_binary_sequence(digits_art, bits_per_symbol)
    print(f"Текст '{text_art}' в бинарном виде: {binary_repr}")
    restored_digits = from_binary_sequence(binary_repr, bits_per_symbol)
    restored_text_bin = text_from_digits(restored_digits, ART_NUM_TO_SYMBOL)
    print(f"Из бинарной строки восстановлено: {restored_text_bin}\n")
    
    # 7. Проверка примера из текста: (2,5)_8 = 21
    digits_example = [2, 5]  # пара (2,5) в 8-ричной
    num_example = digitize_kgram(digits_example, base = 8)
    print(f"Пара (2,5) в 8-ричной = {num_example} (ожидается 21)")