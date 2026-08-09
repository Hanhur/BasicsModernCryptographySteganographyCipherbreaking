# Шифрование в Cybpher 
import random

class Cybpher:
    def __init__(self, seed = None):
        """
        Инициализация шифра Cybpher
        :param seed: зерно для генератора случайных чисел (для воспроизводимости)
        """
        if seed is not None:
            random.seed(seed)
        
        # Создаем буфер ключей (256 чисел от 0 до 255, перемешанных случайно)
        self.key_buffer = list(range(256))
        random.shuffle(self.key_buffer)
        
        # Создаем буфер смещения (256 чисел от 0 до 255, перемешанных случайно)
        self.offset_buffer = list(range(256))
        random.shuffle(self.offset_buffer)
        
        # Последнее число в буфере ключей (для SWAP операций)
        self.last_key = self.key_buffer[-1]
        
        # Переменная для хранения последнего шифротекста
        self.last_cipher = None
    
    def generate_first_key(self):
        """
        Генерация первого ключа (x, x1, K1) как в описании
        Возвращает K1
        """
        # Шаг 2: Случайно выбираем x из буфера ключей
        x = random.choice(self.key_buffer)
        # Берем x-й элемент из буфера ключей
        x1 = self.key_buffer[x]
        
        # Шаг 3: Вычисляем y = (x + x1) mod 256
        y = (x + x1) % 256
        # Берем y-й элемент из буфера смещения
        K1 = self.offset_buffer[y]
        
        return K1
    
    def encrypt_char(self, char_ascii, key):
        """
        Шифрование одного символа
        :param char_ascii: ASCII код символа
        :param key: текущий ключ
        :return: зашифрованный символ (ASCII код)
        """
        # Шаг 4: XOR ключа и открытого текста
        c = key ^ char_ascii
        
        # Находим число в позиции c в буфере ключей
        cipher_value = self.key_buffer[c]
        
        # Заменяем значение в позиции c на c (по сути, сохраняем результат)
        # В оригинале: "заменяем 110 на 149" - это означает,
        # что мы берем значение по индексу c и используем его как шифротекст
        self.key_buffer[c] = cipher_value  # Сохраняем, хотя это уже то же значение
        
        return cipher_value
    
    def generate_next_key(self, current_cipher):
        """
        Генерация следующего сеансового ключа
        :param current_cipher: текущий шифротекст
        :return: следующий ключ
        """
        # Берем последнее число из буфера ключей
        z = self.key_buffer[-1]
        
        # SWAP: меняем местами значения
        # Находим индекс, где находится current_cipher
        try:
            idx = self.key_buffer.index(current_cipher)
            # Меняем местами
            self.key_buffer[idx], self.key_buffer[-1] = self.key_buffer[-1], self.key_buffer[idx]
        except ValueError:
            # Если current_cipher не найден (что маловероятно), просто записываем в конец
            self.key_buffer[-1] = current_cipher
        
        # Новый ключ - это current_cipher (как в описании: "K2 = 149")
        next_key = current_cipher
        
        # Обновляем last_key
        self.last_key = self.key_buffer[-1]
        
        return next_key
    
    def encrypt(self, plaintext):
        """
        Шифрование строки
        :param plaintext: текст для шифрования
        :return: список шифротекстов
        """
        ciphertext = []
        
        # Генерируем первый ключ
        current_key = self.generate_first_key()
        
        for i, char in enumerate(plaintext):
            # Получаем ASCII код символа
            char_ascii = ord(char)
            
            # Шифруем символ
            cipher_val = self.encrypt_char(char_ascii, current_key)
            ciphertext.append(cipher_val)
            
            # Для следующего символа генерируем новый ключ
            if i < len(plaintext) - 1:
                current_key = self.generate_next_key(cipher_val)
        
        return ciphertext
    
    def decrypt_char(self, cipher_val, key):
        """
        Дешифрование одного символа
        :param cipher_val: зашифрованный символ
        :param key: текущий ключ
        :return: расшифрованный символ (ASCII код)
        """
        # Находим исходное значение в буфере ключей
        # В обратном порядке: ищем индекс, где хранится cipher_val
        try:
            idx = self.key_buffer.index(cipher_val)
            # Получаем исходное значение c
            c = idx
            # Вычисляем открытый текст: key XOR c
            char_ascii = key ^ c
            return char_ascii
        except ValueError:
            # Если значение не найдено (что маловероятно)
            return None
    
    def decrypt(self, ciphertext):
        """
        Дешифрование списка шифротекстов
        :param ciphertext: список зашифрованных значений
        :return: расшифрованная строка
        """
        plaintext = []
        
        # Генерируем первый ключ (должен быть тот же, что и при шифровании)
        current_key = self.generate_first_key()
        
        for i, cipher_val in enumerate(ciphertext):
            # Дешифруем символ
            char_ascii = self.decrypt_char(cipher_val, current_key)
            if char_ascii is not None:
                plaintext.append(chr(char_ascii))
            
            # Генерируем следующий ключ (как при шифровании)
            if i < len(ciphertext) - 1:
                current_key = self.generate_next_key(cipher_val)
        
        return ''.join(plaintext)


def main():
    # Создаем экземпляр шифра с фиксированным зерном для воспроизводимости
    # (для реального использования можно не указывать seed)
    cipher = Cybpher(seed = 42)
    
    # Исходное слово
    plaintext = "hello"
    print(f"Исходный текст: {plaintext}")
    
    # Шифрование
    ciphertext = cipher.encrypt(plaintext)
    print(f"Зашифрованный текст (ASCII): {ciphertext}")
    print(f"Зашифрованный текст (символы): {''.join(chr(c) for c in ciphertext)}")
    
    # Дешифрование (создаем новый экземпляр с тем же seed)
    cipher2 = Cybpher(seed = 42)
    decrypted = cipher2.decrypt(ciphertext)
    print(f"Расшифрованный текст: {decrypted}")
    
    # Проверка
    print(f"Успешно: {plaintext == decrypted}")


if __name__ == "__main__":
    main()