# Блоковые шифры 
"""
Реализация блоковых шифров на основе описания из текста:
1. ГОСТ 28147-89 (упрощённая версия с фиксированными S-боксами)
2. RC6-32/20/16 (полноценная реализация)
3. Rijndael/AES-128 (полноценная реализация)
"""

import struct
import math

# ========================================================================
# 1. ГОСТ 28147-89 (упрощённая реализация)
# ========================================================================

class GOST28147:
    """
    Упрощённая реализация ГОСТ 28147-89.
    В реальном ГОСТе S-боксы должны быть секретными и задаваться отдельно.
    Здесь используются фиксированные S-боксы для демонстрации.
    """
    
    # Фиксированные S-боксы (каждый содержит перестановку чисел 0..15)
    # В реальном ГОСТе они должны быть случайными и секретными
    S_BOXES = [
        [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3],
        [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
        [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
        [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
        [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2],
        [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14],
        [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
        [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12]
    ]
    
    def __init__(self, key):
        """
        Инициализация шифра ГОСТ 28147-89.
        key: 256-битный ключ (32 байта) в виде bytes
        """
        if len(key) != 32:
            raise ValueError("Ключ должен быть 32 байта (256 бит)")
        
        # Разбиваем ключ на 8 слов по 32 бита
        self.K = [self._bytes_to_word(key[i * 4:(i + 1) * 4]) for i in range(8)]
        
    def _bytes_to_word(self, b):
        """Преобразование 4 байт в 32-битное слово (little-endian)"""
        return struct.unpack('<I', b)[0]
    
    def _word_to_bytes(self, w):
        """Преобразование 32-битного слова в 4 байта"""
        return struct.pack('<I', w)
    
    def _rotl11(self, x):
        """Циклический сдвиг влево на 11 бит (32-битное слово)"""
        return ((x << 11) | (x >> (32 - 11))) & 0xFFFFFFFF
    
    def _sbox_transform(self, x):
        """Применение S-боксов к 32-битному слову (по 4 бита)"""
        result = 0
        for i in range(8):
            # Извлекаем 4 бита (i-й ниббл)
            nibble = (x >> (4 * i)) & 0xF
            # Применяем S-бокс
            transformed = self.S_BOXES[i][nibble]
            # Помещаем обратно
            result |= transformed << (4 * i)
        return result
    
    def _round(self, L, R, key):
        """Один раунд сети Фейстела"""
        # R + K (mod 2^32)
        s = (R + key) & 0xFFFFFFFF
        # S-боксы
        s = self._sbox_transform(s)
        # Циклический сдвиг влево на 11 бит
        s = self._rotl11(s)
        # L = L XOR результат
        new_L = L ^ s
        return new_L, R
    
    def _generate_round_keys(self, encrypt = True):
        """Генерация раундовых ключей согласно (8.6) и (8.7)"""
        if encrypt:
            # Прямой порядок: K0..K7, K0..K7, K0..K7, K7..K0
            order = [0, 1, 2, 3, 4, 5, 6, 7] * 3 + [7, 6, 5, 4, 3, 2, 1, 0]
        else:
            # Обратный порядок для дешифрования: K0..K7, K7..K0, K7..K0, K7..K0
            order = [0, 1, 2, 3, 4, 5, 6, 7] + [7, 6, 5, 4, 3, 2, 1, 0] * 3
        return [self.K[i] for i in order]
    
    def encrypt_block(self, block):
        """
        Шифрование 64-битного блока.
        block: 8 байт
        возвращает: 8 байт (зашифрованный блок)
        """
        if len(block) != 8:
            raise ValueError("Блок должен быть 8 байт")
        
        # Разбиваем на левую и правую половины
        L = self._bytes_to_word(block[:4])
        R = self._bytes_to_word(block[4:])
        
        # Генерируем раундовые ключи
        round_keys = self._generate_round_keys(encrypt = True)
        
        # 32 раунда
        for i in range(32):
            L, R = self._round(L, R, round_keys[i])
            # Меняем местами (кроме последнего раунда)
            if i < 31:
                L, R = R, L
        
        # Собираем результат
        return self._word_to_bytes(L) + self._word_to_bytes(R)
    
    def decrypt_block(self, block):
        """
        Дешифрование 64-битного блока.
        block: 8 байт
        возвращает: 8 байт (расшифрованный блок)
        """
        if len(block) != 8:
            raise ValueError("Блок должен быть 8 байт")
        
        L = self._bytes_to_word(block[:4])
        R = self._bytes_to_word(block[4:])
        
        round_keys = self._generate_round_keys(encrypt = False)
        
        for i in range(32):
            L, R = self._round(L, R, round_keys[i])
            if i < 31:
                L, R = R, L
        
        return self._word_to_bytes(L) + self._word_to_bytes(R)


# ========================================================================
# 2. RC6-32/20/16
# ========================================================================

class RC6:
    """
    Реализация шифра RC6-32/20/16.
    w = 32 бита, r = 20 раундов, ключ 16 байт (128 бит)
    """
    
    def __init__(self, key, w = 32, r = 20):
        """
        Инициализация RC6.
        key: ключ в виде bytes
        w: размер слова в битах (16, 32 или 64)
        r: количество раундов
        """
        self.w = w
        self.r = r
        self.log_w = int(math.log2(w))
        
        # Вычисляем магические константы
        if w == 16:
            self.P = 0xB7E1
            self.Q = 0x9E37
        elif w == 32:
            self.P = 0xB7E15163
            self.Q = 0x9E3779B9
        elif w == 64:
            self.P = 0xB7E151628AED2A6B
            self.Q = 0x9E3779B97F4A7C15
        else:
            raise ValueError("w должен быть 16, 32 или 64")
        
        self.mask = (1 << w) - 1
        
        # Разворачиваем ключ
        self.W = self._expand_key(key)
    
    def _bytes_to_words(self, data):
        """Преобразование байтов в слова"""
        words = []
        for i in range(0, len(data), self.w // 8):
            if self.w == 32:
                words.append(struct.unpack('<I', data[i:i + 4])[0])
            elif self.w == 64:
                words.append(struct.unpack('<Q', data[i:i + 8])[0])
            else:
                # 16 бит
                words.append(struct.unpack('<H', data[i:i + 2])[0])
        return words
    
    def _words_to_bytes(self, words):
        """Преобразование слов в байты"""
        data = b''
        for w in words:
            if self.w == 32:
                data += struct.pack('<I', w & self.mask)
            elif self.w == 64:
                data += struct.pack('<Q', w & self.mask)
            else:
                data += struct.pack('<H', w & self.mask)
        return data
    
    def _rotl(self, x, n):
        """Циклический сдвиг влево"""
        n = n % self.w
        return ((x << n) | (x >> (self.w - n))) & self.mask
    
    def _rotr(self, x, n):
        """Циклический сдвиг вправо"""
        n = n % self.w
        return ((x >> n) | (x << (self.w - n))) & self.mask
    
    def _f(self, x):
        """Функция f(x) = x * (2x + 1) mod 2^w"""
        return (x * ((2 * x + 1) & self.mask)) & self.mask
    
    def _expand_key(self, key):
        """
        Развёртка ключа (алгоритм 8.4)
        """
        c = max(1, len(key) // (self.w // 8))
        L = self._bytes_to_words(key)
        # Дополняем ключ нулями при необходимости
        while len(L) < c:
            L.append(0)
        
        # Инициализация W
        W = [self.P]
        for i in range(1, 2 * self.r + 4):
            W.append((W[-1] + self.Q) & self.mask)
        
        # Перемешивание
        a = b = 0
        i = j = 0
        k = 3 * max(c, 2 * self.r + 4)
        
        for _ in range(k):
            W[i] = self._rotl((W[i] + a + b) & self.mask, 3)
            a = W[i]
            L[j] = self._rotl((L[j] + a + b) & self.mask, (a + b) & self.mask)
            b = L[j]
            i = (i + 1) % (2 * self.r + 4)
            j = (j + 1) % c
        
        return W
    
    def encrypt_block(self, block):
        """
        Шифрование блока (алгоритм 8.2)
        block: 4 * (w/8) байт
        """
        words = self._bytes_to_words(block)
        if len(words) != 4:
            raise ValueError("Блок должен состоять из 4 слов")
        
        a, b, c, d = words
        
        # Предварительное сложение с ключом
        b = (b + self.W[0]) & self.mask
        d = (d + self.W[1]) & self.mask
        
        # Основные раунды
        for i in range(1, self.r + 1):
            t = self._rotl(self._f(b), self.log_w)
            u = self._rotl(self._f(d), self.log_w)
            a = self._rotl(a ^ t, u) + self.W[2 * i]
            a &= self.mask
            c = self._rotl(c ^ u, t) + self.W[2 * i + 1]
            c &= self.mask
            a, b, c, d = b, c, d, a
        
        # Финальное сложение с ключом
        a = (a + self.W[2 * self.r + 2]) & self.mask
        c = (c + self.W[2 * self.r + 3]) & self.mask
        
        return self._words_to_bytes([a, b, c, d])
    
    def decrypt_block(self, block):
        """
        Дешифрование блока (алгоритм 8.3)
        """
        words = self._bytes_to_words(block)
        if len(words) != 4:
            raise ValueError("Блок должен состоять из 4 слов")
        
        a, b, c, d = words
        
        # Финальное вычитание ключа
        c = (c - self.W[2 * self.r + 3]) & self.mask
        a = (a - self.W[2 * self.r + 2]) & self.mask
        
        # Основные раунды (в обратном порядке)
        for i in range(self.r, 0, -1):
            a, b, c, d = d, a, b, c
            t = self._rotl(self._f(b), self.log_w)
            u = self._rotl(self._f(d), self.log_w)
            a = self._rotr((a - self.W[2 * i]) & self.mask, u) ^ t
            c = self._rotr((c - self.W[2 * i + 1]) & self.mask, t) ^ u
        
        # Начальное вычитание ключа
        d = (d - self.W[1]) & self.mask
        b = (b - self.W[0]) & self.mask
        
        return self._words_to_bytes([a, b, c, d])


# ========================================================================
# 3. Rijndael (AES-128)
# ========================================================================

class AES:
    """
    Реализация AES-128 (Rijndael).
    Размер блока: 128 бит, ключ: 128 бит, 10 раундов.
    """
    
    # S-box (из таблицы в спецификации AES)
    S_BOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    # Обратный S-box
    INV_S_BOX = [
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
    ]
    
    # Таблицы для умножения в поле GF(2^8)
    # Используются для MixColumns
    def __init__(self, key):
        """
        Инициализация AES-128.
        key: 16 байт (128 бит)
        """
        if len(key) != 16:
            raise ValueError("Ключ должен быть 16 байт")
        
        self.key = key
        self.Nb = 4  # число столбцов в блоке (4 для AES)
        self.Nk = 4  # число слов в ключе (4 для AES-128)
        self.Nr = 10  # число раундов
        
        # Разворачиваем ключ
        self.round_keys = self._key_expansion()
    
    def _sub_word(self, word):
        """Применение S-box к слову (4 байта)"""
        return [self.S_BOX[b] for b in word]
    
    def _rot_word(self, word):
        """Циклический сдвиг слова влево на 1 байт"""
        return word[1:] + word[:1]
    
    def _key_expansion(self):
        """
        Развёртка ключа (алгоритм 8.9)
        """
        # Rcon для AES
        Rcon = [
            0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
        ]
        
        # Преобразуем ключ в слова
        key_words = [list(self.key[i:i + 4]) for i in range(0, 16, 4)]
        
        # Расширяем до (Nb * (Nr + 1)) = 44 слов
        expanded = key_words.copy()
        
        for i in range(self.Nk, self.Nb * (self.Nr + 1)):
            temp = expanded[i - 1].copy()
            
            if i % self.Nk == 0:
                temp = self._sub_word(self._rot_word(temp))
                temp[0] ^= Rcon[(i // self.Nk) - 1]
            elif self.Nk > 6 and i % self.Nk == 4:
                temp = self._sub_word(temp)
            
            # XOR с предыдущим словом на расстоянии Nk
            word = [expanded[i - self.Nk][j] ^ temp[j] for j in range(4)]
            expanded.append(word)
        
        # Преобразуем в плоский список байт
        return [byte for word in expanded for byte in word]
    
    def _add_round_key(self, state, round_num):
        """XOR с раундовым ключом"""
        start = round_num * 16
        for i in range(4):
            for j in range(4):
                state[i][j] ^= self.round_keys[start + i + 4 * j]
        return state
    
    def _sub_bytes(self, state):
        """Замена байтов (SubBytes)"""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.S_BOX[state[i][j]]
        return state
    
    def _inv_sub_bytes(self, state):
        """Обратная замена байтов"""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.INV_S_BOX[state[i][j]]
        return state
    
    def _shift_rows(self, state):
        """Сдвиг строк (ShiftRows)"""
        # Строка 0: без сдвига
        # Строка 1: сдвиг влево на 1
        state[1] = state[1][1:] + state[1][:1]
        # Строка 2: сдвиг влево на 2
        state[2] = state[2][2:] + state[2][:2]
        # Строка 3: сдвиг влево на 3
        state[3] = state[3][3:] + state[3][:3]
        return state
    
    def _inv_shift_rows(self, state):
        """Обратный сдвиг строк"""
        state[1] = state[1][3:] + state[1][:3]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][1:] + state[3][:1]
        return state
    
    def _gf_mul(self, a, b):
        """Умножение в поле GF(2 ^ 8) с полиномом m(x) = x ^ 8 + x ^ 4 + x ^ 3 + x + 1"""
        result = 0
        for _ in range(8):
            if b & 1:
                result ^= a
            carry = a & 0x80
            a = (a << 1) & 0xFF
            if carry:
                a ^= 0x1B  # m(x) без старшего члена
            b >>= 1
        return result
    
    def _mix_columns(self, state):
        """Перемешивание столбцов (MixColumns) - матрица (8.10)"""
        new_state = [[0] * 4 for _ in range(4)]
        for c in range(4):
            new_state[0][c] = self._gf_mul(2, state[0][c]) ^ self._gf_mul(3, state[1][c]) ^ state[2][c] ^ state[3][c]
            new_state[1][c] = state[0][c] ^ self._gf_mul(2, state[1][c]) ^ self._gf_mul(3, state[2][c]) ^ state[3][c]
            new_state[2][c] = state[0][c] ^ state[1][c] ^ self._gf_mul(2, state[2][c]) ^ self._gf_mul(3, state[3][c])
            new_state[3][c] = self._gf_mul(3, state[0][c]) ^ state[1][c] ^ state[2][c] ^ self._gf_mul(2, state[3][c])
        return new_state
    
    def _inv_mix_columns(self, state):
        """Обратное перемешивание столбцов - матрица (8.11)"""
        new_state = [[0] * 4 for _ in range(4)]
        for c in range(4):
            new_state[0][c] = (self._gf_mul(14, state[0][c]) ^ self._gf_mul(11, state[1][c]) ^ self._gf_mul(13, state[2][c]) ^ self._gf_mul(9, state[3][c]))
            new_state[1][c] = (self._gf_mul(9, state[0][c]) ^ self._gf_mul(14, state[1][c]) ^ self._gf_mul(11, state[2][c]) ^ self._gf_mul(13, state[3][c]))
            new_state[2][c] = (self._gf_mul(13, state[0][c]) ^ self._gf_mul(9, state[1][c]) ^ self._gf_mul(14, state[2][c]) ^ self._gf_mul(11, state[3][c]))
            new_state[3][c] = (self._gf_mul(11, state[0][c]) ^ self._gf_mul(13, state[1][c]) ^ self._gf_mul(9, state[2][c]) ^ self._gf_mul(14, state[3][c]))
        return new_state
    
    def _state_to_bytes(self, state):
        """Преобразование матрицы состояния в байты (по столбцам)"""
        result = bytearray(16)
        for i in range(4):
            for j in range(4):
                result[i + 4 * j] = state[i][j]
        return bytes(result)
    
    def _bytes_to_state(self, data):
        """Преобразование байт в матрицу состояния (по столбцам)"""
        state = [[0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[i][j] = data[i + 4 * j]
        return state
    
    def encrypt_block(self, block):
        """
        Шифрование блока (алгоритм 8.5)
        block: 16 байт
        """
        if len(block) != 16:
            raise ValueError("Блок должен быть 16 байт")
        
        state = self._bytes_to_state(block)
        
        # Начальное сложение с ключом
        state = self._add_round_key(state, 0)
        
        # Основные раунды
        for round_num in range(1, self.Nr):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, round_num)
        
        # Последний раунд (без MixColumns)
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self.Nr)
        
        return self._state_to_bytes(state)
    
    def decrypt_block(self, block):
        """
        Дешифрование блока (алгоритм 8.6)
        block: 16 байт
        """
        if len(block) != 16:
            raise ValueError("Блок должен быть 16 байт")
        
        state = self._bytes_to_state(block)
        
        # Начальное сложение с ключом (последний раунд)
        state = self._add_round_key(state, self.Nr)
        
        # Основные раунды (в обратном порядке)
        for round_num in range(self.Nr - 1, 0, -1):
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
            state = self._add_round_key(state, round_num)
            state = self._inv_mix_columns(state)
        
        # Последний раунд (без MixColumns)
        state = self._inv_shift_rows(state)
        state = self._inv_sub_bytes(state)
        state = self._add_round_key(state, 0)
        
        return self._state_to_bytes(state)


# ========================================================================
# 4. Тестирование
# ========================================================================

def test_gost():
    """Тестирование ГОСТ 28147-89"""
    print("=" * 50)
    print("Тест ГОСТ 28147-89")
    print("=" * 50)
    
    # Ключ 256 бит (32 байта)
    key = b"01234567890123456789012345678901"
    # Блок 64 бита (8 байт)
    plaintext = b"12345678"
    
    gost = GOST28147(key)
    
    print(f"Исходный блок: {plaintext}")
    
    encrypted = gost.encrypt_block(plaintext)
    print(f"Зашифрованный блок: {encrypted.hex()}")
    
    decrypted = gost.decrypt_block(encrypted)
    print(f"Расшифрованный блок: {decrypted}")
    
    print(f"Тест пройден: {plaintext == decrypted}")
    print()

def test_rc6():
    """Тестирование RC6"""
    print("=" * 50)
    print("Тест RC6-32/20/16")
    print("=" * 50)
    
    # Ключ 128 бит (16 байт)
    key = b"0123456789012345"
    # Блок 128 бит (16 байт)
    plaintext = b"0123456789ABCDEF"
    
    rc6 = RC6(key, w = 32, r = 20)
    
    print(f"Исходный блок: {plaintext}")
    
    encrypted = rc6.encrypt_block(plaintext)
    print(f"Зашифрованный блок: {encrypted.hex()}")
    
    decrypted = rc6.decrypt_block(encrypted)
    print(f"Расшифрованный блок: {decrypted}")
    
    print(f"Тест пройден: {plaintext == decrypted}")
    print()

def test_aes():
    """Тестирование AES-128"""
    print("=" * 50)
    print("Тест AES-128 (Rijndael)")
    print("=" * 50)
    
    # Ключ 128 бит (16 байт)
    key = b"0123456789012345"
    # Блок 128 бит (16 байт)
    plaintext = b"0123456789ABCDEF"
    
    aes = AES(key)
    
    print(f"Исходный блок: {plaintext}")
    
    encrypted = aes.encrypt_block(plaintext)
    print(f"Зашифрованный блок: {encrypted.hex()}")
    
    decrypted = aes.decrypt_block(encrypted)
    print(f"Расшифрованный блок: {decrypted}")
    
    print(f"Тест пройден: {plaintext == decrypted}")
    print()


def test_compatibility():
    """Тестирование совместимости с известными векторами"""
    print("=" * 50)
    print("Тест совместимости AES")
    print("=" * 50)
    
    # Известный тестовый вектор из спецификации AES
    key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
    plaintext = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    expected = bytes.fromhex("69C4E0D86A7B0430D8CDB78070B4C55A")
    
    aes = AES(key)
    result = aes.encrypt_block(plaintext)
    
    print(f"Ожидаемый результат: {expected.hex().upper()}")
    print(f"Полученный результат: {result.hex().upper()}")
    print(f"Тест пройден: {result == expected}")
    print()

if __name__ == "__main__":
    print("РЕАЛИЗАЦИЯ БЛОКОВЫХ ШИФРОВ\n")
    
    # Запускаем тесты всех шифров
    test_gost()
    test_rc6()
    test_aes()
    test_compatibility()