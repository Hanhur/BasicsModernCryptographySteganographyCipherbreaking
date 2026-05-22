# 3. Шифр замены
import random
import string

# ------------------------------------------------------------
# 1. Общий шифр простой замены (на основе подстановки)
# ------------------------------------------------------------
class SimpleSubstitutionCipher:
    def __init__(self, alphabet: str):
        """
        :param alphabet: строка из всех допустимых символов (например, 'abcdefghijklmnopqrstuvwxyz')
        """
        self.alphabet = alphabet
        self.n = len(alphabet)
        # Словари для отображения символ -> индекс и индекс -> символ
        self.char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        self.idx_to_char = {i: ch for i, ch in enumerate(alphabet)}
        # Подстановка sigma: индекс -> индекс (по умолчанию тождественная)
        self.sigma = list(range(self.n))
        self.inv_sigma = list(range(self.n))
    
    def set_substitution(self, sigma: list):
        """
        Установить подстановку sigma (список длины n, перестановка чисел 0..n-1)
        """
        if sorted(sigma) != list(range(self.n)):
            raise ValueError("sigma должна быть перестановкой индексов 0..n-1")
        self.sigma = sigma[:]
        # Вычисляем обратную подстановку
        self.inv_sigma = [0] * self.n
        for i, s in enumerate(sigma):
            self.inv_sigma[s] = i
    
    def set_random_substitution(self, seed = None):
        """
        Сгенерировать случайную подстановку
        """
        if seed is not None:
            random.seed(seed)
        perm = list(range(self.n))
        random.shuffle(perm)
        self.set_substitution(perm)
    
    def encrypt(self, plaintext: str) -> str:
        """Шифрование: c = sigma(i)"""
        result = []
        for ch in plaintext:
            if ch in self.char_to_idx:
                i = self.char_to_idx[ch]
                c_idx = self.sigma[i]
                result.append(self.idx_to_char[c_idx])
            else:
                # Символ не из алфавита — оставляем как есть
                result.append(ch)
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Дешифрование: i = sigma^{-1}(c)"""
        result = []
        for ch in ciphertext:
            if ch in self.char_to_idx:
                c_idx = self.char_to_idx[ch]
                i = self.inv_sigma[c_idx]
                result.append(self.idx_to_char[i])
            else:
                result.append(ch)
        return ''.join(result)
    
    def print_mapping(self):
        """Вывести отображение букв"""
        print("Подстановка (исходная -> заменяющая):")
        for ch in self.alphabet:
            enc = self.encrypt(ch)
            print(f"  {ch} -> {enc}")


# ------------------------------------------------------------
# 2. Шифр сдвига (Цезаря) как частный случай
# ------------------------------------------------------------
class CaesarCipher:
    def __init__(self, alphabet: str, shift: int):
        self.alphabet = alphabet
        self.n = len(alphabet)
        self.shift = shift % self.n
        self.char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        self.idx_to_char = {i: ch for i, ch in enumerate(alphabet)}
    
    def encrypt(self, plaintext: str) -> str:
        result = []
        for ch in plaintext:
            if ch in self.char_to_idx:
                i = self.char_to_idx[ch]
                new_i = (i + self.shift) % self.n
                result.append(self.idx_to_char[new_i])
            else:
                result.append(ch)
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        result = []
        for ch in ciphertext:
            if ch in self.char_to_idx:
                i = self.char_to_idx[ch]
                new_i = (i - self.shift) % self.n
                result.append(self.idx_to_char[new_i])
            else:
                result.append(ch)
        return ''.join(result)


# ------------------------------------------------------------
# 3. Демонстрация
# ------------------------------------------------------------
if __name__ == "__main__":
    # Используем стандартный английский алфавит (строчные буквы)
    ALPHABET = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    
    print("=" * 60)
    print("1. ШИФР ПРОСТОЙ ЗАМЕНЫ (случайная подстановка)")
    print("=" * 60)
    
    cipher = SimpleSubstitutionCipher(ALPHABET)
    cipher.set_random_substitution(seed = 42)  # фиксируем seed для повторяемости результата
    cipher.print_mapping()
    
    plain = "algorithm"
    encrypted = cipher.encrypt(plain)
    decrypted = cipher.decrypt(encrypted)
    
    print(f"\nИсходный текст : {plain}")
    print(f"Зашифрованный : {encrypted}")
    print(f"Расшифрованный : {decrypted}")
    print(f"Успех: {plain == decrypted}")
    
    print("\n" + "=" * 60)
    print("2. ШИФР СДВИГА (Цезаря) с ключом e = 13")
    print("=" * 60)
    
    caesar = CaesarCipher(ALPHABET, shift = 13)
    
    plain2 = "algorithm"
    encrypted2 = caesar.encrypt(plain2)
    decrypted2 = caesar.decrypt(encrypted2)
    
    print(f"Исходный текст : {plain2}")
    print(f"Зашифрованный : {encrypted2}")
    print(f"Расшифрованный : {decrypted2}")
    print(f"Успех: {plain2 == decrypted2}")
    
    # Проверка соответствия примеру из текста (сдвиг 13)
    # 'algorithm' -> 'nytbvguz' ?
    expected_caesar = "nytbvguz"
    print(f"\nПроверка по тексту лекции: {plain2} -> {encrypted2}")
    print(f"Совпадает с ожидаемым 'nytbvguz': {encrypted2 == expected_caesar}")
    
    print("\n" + "=" * 60)
    print("3. РУЧНАЯ ЗАДАНИЕ ПОДСТАНОВКИ (по индексам из текста)")
    print("=" * 60)
    # Пример подстановки из вашего текста: σ(i) = i+13 mod 26, но она же сдвиг
    # Сделаем для демонстрации другую: например, reverse mapping
    custom_sigma = [(i * 7) % 26 for i in range(26)]  # просто пример не-сдвига
    cipher_custom = SimpleSubstitutionCipher(ALPHABET)
    cipher_custom.set_substitution(custom_sigma)
    
    plain3 = "python"
    encrypted3 = cipher_custom.encrypt(plain3)
    decrypted3 = cipher_custom.decrypt(encrypted3)
    print(f"Текст: {plain3} -> {encrypted3} -> {decrypted3}")