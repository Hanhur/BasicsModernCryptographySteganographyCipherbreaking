# Заметки и пример по SHA-1
"""
SHA-1 Implementation (Pure Python, no numpy)
Based on the algorithm description:
1. Padding (append 1, zeros, and 64-bit length)
2. Initialize 5 registers (H0-H4)
3. Process 512-bit blocks with 80 rounds
4. Produce 160-bit digest
"""

def sha1(message_bytes):
    """
    Вычисляет SHA-1 хеш от входных данных (байтовый объект).
    Возвращает 40-символьную шестнадцатеричную строку.
    """
    
    # ========== ШАГ 1: ДОПОЛНЕНИЕ (PADDING) ==========
    # Исходная длина в битах
    original_bit_len = len(message_bytes) * 8
    
    # Добавляем бит '1' (0x80 в байтах)
    padded = bytearray(message_bytes)
    padded.append(0x80)
    
    # Добавляем нулевые байты, пока длина не станет ≡ 56 (mod 64)
    # 56 байт = 448 бит (оставляем 8 байт под длину)
    while len(padded) % 64 != 56:
        padded.append(0x00)
    
    # Добавляем 64-битную длину исходного сообщения (big-endian)
    padded.extend((original_bit_len).to_bytes(8, byteorder = 'big'))
    
    # ========== ШАГ 2: ИНИЦИАЛИЗАЦИЯ РЕГИСТРОВ ==========
    H0 = 0x67452301
    H1 = 0xEFCDAB89
    H2 = 0x98BADCFE
    H3 = 0x10325476
    H4 = 0xC3D2E1F0
    
    # Константы для раундов
    K = [
        0x5A827999,  # 0..19
        0x6ED9EBA1,  # 20..39
        0x8F1BBCDC,  # 40..59
        0xCA62C1D6   # 60..79
    ]
    
    # ========== ШАГ 3: ОБРАБОТКА БЛОКОВ ПО 512 БИТ ==========
    for chunk_start in range(0, len(padded), 64):
        chunk = padded[chunk_start:chunk_start + 64]
        
        # Создаём массив W из 80 слов (каждое по 32 бита)
        W = [0] * 80
        
        # Первые 16 слов - это байты чанка (big-endian)
        for i in range(16):
            W[i] = int.from_bytes(chunk[i * 4:(i + 1) * 4], byteorder = 'big')
        
        # Расширяем до 80 слов (операции XOR и циклический сдвиг)
        for i in range(16, 80):
            W[i] = left_rotate(W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16], 1)
        
        # Копируем регистры
        a, b, c, d, e = H0, H1, H2, H3, H4
        
        # 80 раундов
        for i in range(80):
            if 0 <= i <= 19:
                f = (b & c) | ((~b) & d)
                k = K[0]
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = K[1]
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = K[2]
            else:  # 60..79
                f = b ^ c ^ d
                k = K[3]
            
            # Основная операция раунда
            temp = (left_rotate(a, 5) + f + e + k + W[i]) & 0xFFFFFFFF
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
        
        # Добавляем к итоговым регистрам
        H0 = (H0 + a) & 0xFFFFFFFF
        H1 = (H1 + b) & 0xFFFFFFFF
        H2 = (H2 + c) & 0xFFFFFFFF
        H3 = (H3 + d) & 0xFFFFFFFF
        H4 = (H4 + e) & 0xFFFFFFFF
    
    # ========== ШАГ 4: ФОРМИРОВАНИЕ ДАЙДЖЕСТА ==========
    digest = (H0.to_bytes(4, 'big') +
              H1.to_bytes(4, 'big') +
              H2.to_bytes(4, 'big') +
              H3.to_bytes(4, 'big') +
              H4.to_bytes(4, 'big'))
    
    return digest.hex()


def left_rotate(value, shift):
    """
    Циклический сдвиг 32-битного числа влево на shift бит.
    """
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


# ========== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ==========
if __name__ == "__main__":
    # Тест 1: Пустое сообщение
    empty_hash = sha1(b"")
    print(f"SHA-1('') = {empty_hash}")
    print(f"Ожидается:  da39a3ee5e6b4b0d3255bfef95601890afd80709")
    print(f"Совпадает: {empty_hash == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'}")
    print()
    
    # Тест 2: Сообщение "abc"
    abc_hash = sha1(b"abc")
    print(f"SHA-1('abc') = {abc_hash}")
    print(f"Ожидается:  a9993e364706816aba3e25717850c26c9cd0d89d")
    print(f"Совпадает: {abc_hash == 'a9993e364706816aba3e25717850c26c9cd0d89d'}")
    print()
    
    # Тест 3: Ваш пример с длиной 2800 бит (350 байт)
    # Создаём сообщение длиной ровно 350 байт = 2800 бит
    test_msg = b"A" * 350
    print(f"Сообщение из 350 байт (2800 бит)")
    print(f"Дополнение согласно вашему описанию: 2800 + 1 + 207 = 3008 бит")
    print(f"Затем +64 бита длины = 3072 бит = 6 блоков по 512 бит")
    print(f"SHA-1 = {sha1(test_msg)}")
    print()
    
    # Тест 4: Сообщение "The quick brown fox jumps over the lazy dog"
    fox_hash = sha1(b"The quick brown fox jumps over the lazy dog")
    print(f"SHA-1(fox) = {fox_hash}")
    print(f"Ожидается:  2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
    print(f"Совпадает: {fox_hash == '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12'}")