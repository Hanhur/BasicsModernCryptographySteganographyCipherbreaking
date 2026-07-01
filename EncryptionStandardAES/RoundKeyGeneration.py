# 4. Генерация раундовых ключей
class AESKeySchedule:
    def __init__(self, key_bytes, Nk):
        """
        key_bytes: исходный ключ в виде байтов (длина должна быть 4*Nk)
        Nk: количество 32-битных слов в ключе (4, 6 или 8)
        """
        self.Nk = Nk
        self.Nb = 4  # Стандартный размер блока для AES (можно менять)
        self.Nr = self.get_rounds()
        
        # S-Box (таблица замен) - стандартный для AES
        self.sbox = [
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
        
        # Преобразуем байты в слова
        self.W = self._bytes_to_words(key_bytes)
        
    def get_rounds(self):
        """Определяет количество раундов в зависимости от Nk"""
        if self.Nk == 4:
            return 10
        elif self.Nk == 6:
            return 12
        elif self.Nk == 8:
            return 14
        else:
            raise ValueError("Nk должен быть 4, 6 или 8")
    
    def _bytes_to_words(self, key_bytes):
        """Преобразует массив байтов в список 32-битных слов"""
        if len(key_bytes) != 4 * self.Nk:
            raise ValueError(f"Длина ключа должна быть {4 * self.Nk} байт")
        
        words = []
        for i in range(0, len(key_bytes), 4):
            word = (key_bytes[i] << 24) | (key_bytes[i + 1] << 16) | (key_bytes[i + 2] << 8) | key_bytes[i + 3]
            words.append(word)
        return words
    
    def _word_to_bytes(self, word):
        """Преобразует 32-битное слово в 4 байта"""
        return [
            (word >> 24) & 0xFF,
            (word >> 16) & 0xFF,
            (word >> 8) & 0xFF,
            word & 0xFF
        ]
    
    def _rot_word(self, word):
        """Циклический сдвиг байтов в слове на 1 байт влево (T-функция)"""
        bytes_word = self._word_to_bytes(word)
        rotated = bytes_word[1:] + [bytes_word[0]]
        return (rotated[0] << 24) | (rotated[1] << 16) | (rotated[2] << 8) | rotated[3]
    
    def _sub_word(self, word):
        """Замена каждого байта через S-Box (F-функция)"""
        bytes_word = self._word_to_bytes(word)
        substituted = [self.sbox[b] for b in bytes_word]
        return (substituted[0] << 24) | (substituted[1] << 16) | (substituted[2] << 8) | substituted[3]
    
    def _rc(self, t):
        """Вычисление раундовой константы RC[t] по формуле RC[t] = t · RC[t - 1] в GF(2⁸)"""
        # RC[0] = 1 в стандарте, но в вашем тексте RC[0] = 1
        if t == 0:
            return 1
        
        # Умножение на 2 в поле GF(2⁸) с полиномом x⁸ + x⁴ + x³ + x + 1
        def xtime(x):
            result = x << 1
            if result & 0x100:
                result ^= 0x1B
            return result & 0xFF
        
        # Вычисляем RC[t] = RC[t-1] * 2
        rc = 1
        for _ in range(t):
            rc = xtime(rc)
        return rc
    
    def generate_key_schedule(self):
        """Генерирует расширенный ключ согласно вашему описанию"""
        # Вычисляем общее количество слов в расширенном ключе
        total_words = self.Nb * (self.Nr + 1)
        
        # Первые Nk слов - это исходный ключ
        expanded = self.W[:]
        
        # Генерируем остальные слова
        for i in range(self.Nk, total_words):
            temp = expanded[i - 1]
            
            if i % self.Nk == 0:
                # Для i, кратных Nk (i = l*Nk)
                # W[i] = F(T(W[i-1])) ⊕ W[i-Nk] ⊕ C(i/Nk)
                temp = self._rot_word(temp)      # T
                temp = self._sub_word(temp)      # F
                
                # Раундовая константа C(t) = (RC[t], 0, 0, 0)
                t = i // self.Nk
                rc_value = self._rc(t)
                round_const = (rc_value << 24) & 0xFF000000
                
                temp = temp ^ round_const
                
            elif self.Nk > 6 and (i - 4) % self.Nk == 0:
                # Дополнительное правило для Nk > 6 (в вашем тексте Nk ≥ 6, но это ошибка)
                # W[i] = F(W[i-1]) ⊕ W[i-Nk]
                temp = self._sub_word(temp)
            
            # Общая формула для всех случаев
            expanded.append(temp ^ expanded[i - self.Nk])
        
        return expanded
    
    def print_key_schedule(self, expanded_key):
        """Выводит расширенный ключ в удобочитаемом виде"""
        print(f"Расширенный ключ (Nk = {self.Nk}, раундов = {self.Nr}):")
        print("=" * 60)
        
        for i, word in enumerate(expanded_key):
            hex_word = f"{word:08X}"
            round_num = i // self.Nb
            print(f"W[{i:2d}] = {hex_word}  (раунд {round_num})")
            
            # Разделитель между раундами
            if (i + 1) % self.Nb == 0 and i < len(expanded_key) - 1:
                print("-" * 60)


# ===================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ =====================

def test_aes128():
    """Тест для AES-128 (Nk = 4)"""
    print("\n" + "=" * 60)
    print("ТЕСТ AES-128 (Nk = 4)")
    print("=" * 60)
    
    # Ключ из стандарта FIPS-197
    key_hex = "2b7e151628aed2a6abf7158809cf4f3c"
    key_bytes = bytes.fromhex(key_hex)
    
    print(f"Исходный ключ: {key_hex}")
    print()
    
    aes = AESKeySchedule(key_bytes, Nk = 4)
    expanded = aes.generate_key_schedule()
    aes.print_key_schedule(expanded)
    
    # Проверка первого раундового ключа (должен быть a0fafe17 88542cb1 23a33939 2a6c7605)
    expected_first_round = ["A0FAFE17", "88542CB1", "23A33939", "2A6C7605"]
    print("\nПроверка первого раундового ключа:")
    for i in range(4, 8):
        hex_word = f"{expanded[i]:08X}"
        status = "✓" if hex_word == expected_first_round[i - 4] else "✗"
        print(f"W[{i}] = {hex_word}  (ожидается {expected_first_round[i - 4]}) {status}")


def test_aes192():
    """Тест для AES-192 (Nk = 6)"""
    print("\n" + "=" * 60)
    print("ТЕСТ AES-192 (Nk = 6)")
    print("=" * 60)
    
    key_hex = "8e73b0f7da0e6452c810f32b809079e562f8ead2522c6b7b"
    key_bytes = bytes.fromhex(key_hex)
    
    print(f"Исходный ключ: {key_hex}")
    print()
    
    aes = AESKeySchedule(key_bytes, Nk = 6)
    expanded = aes.generate_key_schedule()
    aes.print_key_schedule(expanded)


def test_aes256():
    """Тест для AES-256 (Nk = 8)"""
    print("\n" + "=" * 60)
    print("ТЕСТ AES-256 (Nk = 8)")
    print("=" * 60)
    
    key_hex = "603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4"
    key_bytes = bytes.fromhex(key_hex)
    
    print(f"Исходный ключ: {key_hex}")
    print()
    
    aes = AESKeySchedule(key_bytes, Nk = 8)
    expanded = aes.generate_key_schedule()
    aes.print_key_schedule(expanded)


if __name__ == "__main__":
    # Запускаем все тесты
    test_aes128()
    test_aes192()
    test_aes256()
    
    # Дополнительный пример с произвольным ключом
    print("\n" + "=" * 60)
    print("ПРОИЗВОЛЬНЫЙ КЛЮЧ (Nk = 4)")
    print("=" * 60)
    
    # Создаем случайный ключ (16 байт)
    import os
    random_key = os.urandom(16)
    print(f"Случайный ключ (hex): {random_key.hex()}")
    print()
    
    aes = AESKeySchedule(random_key, Nk = 4)
    expanded = aes.generate_key_schedule()
    
    # Покажем только первые 8 слов для примера
    print("Первые 8 слов расширенного ключа:")
    for i in range(8):
        print(f"W[{i}] = {expanded[i]:08X}")