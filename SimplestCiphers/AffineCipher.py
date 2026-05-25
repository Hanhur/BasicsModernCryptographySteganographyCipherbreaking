# 1. Аффинный шифр
import math

class AffineCipher:
    def __init__(self, n):
        """
        Инициализация аффинного шифра.
        n: модуль (например, 26 для английского алфавита)
        """
        self.n = n

    def _mod_inverse(self, a):
        """
        Находит обратный элемент a modulo n.
        Использует расширенный алгоритм Евклида.
        """
        # Используем локальные переменные, не изменяя self.n
        n_local = self.n
        a_local = a % n_local
        
        # Расширенный алгоритм Евклида
        t, new_t = 0, 1
        r, new_r = n_local, a_local
        
        while new_r != 0:
            quotient = r // new_r
            t, new_t = new_t, t - quotient * new_t
            r, new_r = new_r, r - quotient * new_r
        
        if r > 1:
            return None  # Обратный элемент не существует
        
        if t < 0:
            t += n_local
            
        return t

    def encrypt_char(self, m, a, b):
        """
        Шифрует один символ (число m).
        c = a*m + b (mod n)
        """
        return (a * m + b) % self.n

    def decrypt_char(self, c, a, b):
        """
        Расшифровывает один символ (число c).
        m = a^(-1)*(c - b) (mod n)
        """
        a_inv = self._mod_inverse(a)
        if a_inv is None:
            raise ValueError(f"a = {a} не обратим по модулю {self.n}")
        return (a_inv * (c - b)) % self.n

    def encrypt_text(self, text, a, b):
        """
        Шифрует текст (строку или список чисел) с ключом (a, b).
        """
        # Проверяем обратимость a
        if self._mod_inverse(a) is None:
            raise ValueError(f"a = {a} не обратим по модулю {self.n}. НОД({a}, {self.n}) = {math.gcd(a, self.n)}")
        
        result = []
        for ch in text:
            if isinstance(ch, int):  # уже число
                m = ch
            else:
                m = ord(ch)  # для демонстрации, лучше использовать своё отображение
            result.append(self.encrypt_char(m, a, b))
        return result

    def decrypt_text(self, cipher, a, b):
        """
        Расшифровывает список чисел в список чисел.
        """
        # Проверяем обратимость a
        if self._mod_inverse(a) is None:
            raise ValueError(f"a = {a} не обратим по модулю {self.n}")
        
        result = []
        for c in cipher:
            result.append(self.decrypt_char(c, a, b))
        return result

    def recover_key_from_pairs(self, pairs):
        """
        Восстанавливает ключ (a, b) по двум или более парам (m, c).
        pairs: список кортежей (m1, c1), (m2, c2), ...
        Возвращает (a, b) или None, если восстановить не удалось.
        """
        if len(pairs) < 2:
            raise ValueError("Нужно минимум 2 пары")

        m1, c1 = pairs[0]
        m2, c2 = pairs[1]

        # Вычисляем m1 - m2 и c1 - c2
        delta_m = (m1 - m2) % self.n
        delta_c = (c1 - c2) % self.n

        gcd = math.gcd(delta_m, self.n)

        if gcd == 1:
            # Однозначное восстановление a
            delta_m_inv = self._mod_inverse(delta_m)
            if delta_m_inv is None:
                return None
            a = (delta_c * delta_m_inv) % self.n
            b = (c1 - a * m1) % self.n
            return (a, b)
        else:
            # Несколько возможных a, пробуем уточнить с помощью третьей пары
            if len(pairs) < 3:
                print(f"gcd(delta_m, n) = {gcd} > 1, нужно больше пар для однозначного восстановления")
                return None

            # Перебираем возможные a и проверяем по третьей паре
            candidates = []
            for a in range(0, self.n):
                if (a * delta_m) % self.n == delta_c:
                    b = (c1 - a * m1) % self.n
                    # Проверяем на всех дополнительных парах
                    valid = True
                    for m, c in pairs[2:]:
                        if (a * m + b) % self.n != c:
                            valid = False
                            break
                    if valid:
                        candidates.append((a, b))

            if len(candidates) == 1:
                return candidates[0]
            elif len(candidates) > 1:
                print(f"Найдено {len(candidates)} возможных ключей: {candidates}")
                return candidates[0]  # возвращаем первый, но с предупреждением
            else:
                return None

    def display_key_space_size(self):
        """Выводит количество возможных ключей для данного n."""
        phi_n = 0
        for i in range(1, self.n + 1):
            if math.gcd(i, self.n) == 1:
                phi_n += 1
        return phi_n * self.n

    def text_to_numbers(self, text, shift=ord('A')):
        """Преобразует строку в список чисел (A = 0, B = 1, ...)."""
        result = []
        for ch in text.upper():
            if 'A' <= ch <= 'Z':
                result.append(ord(ch) - shift)
        return result

    def numbers_to_text(self, numbers, shift = ord('A')):
        """Преобразует список чисел обратно в строку."""
        result = []
        for num in numbers:
            result.append(chr(num + shift))
        return ''.join(result)

def demo():
    """Демонстрация работы аффинного шифра."""
    n = 26  # для английского алфавита
    cipher = AffineCipher(n)

    print("=== АФФИННЫЙ ШИФР ===")
    print(f"Модуль n = {n}")
    print(f"Размер пространства ключей: {cipher.display_key_space_size()}")
    print()

    # Пример ключа
    a, b = 5, 8
    print(f"Ключ: a = {a}, b = {b}")
    print(f"Проверка обратимости a: НОД({a}, {n}) = {math.gcd(a, n)}")
    print()

    # Исходный текст
    plain_text = "HELLO"
    print(f"Открытый текст: {plain_text}")
    
    # Преобразуем в числа
    plain_numbers = cipher.text_to_numbers(plain_text)
    print(f"Открытый текст (числа): {plain_numbers}")

    # Шифрование
    cipher_numbers = cipher.encrypt_text(plain_numbers, a, b)
    print(f"Шифротекст (числа):   {cipher_numbers}")
    
    # Преобразуем обратно в буквы
    cipher_text = cipher.numbers_to_text(cipher_numbers)
    print(f"Шифротекст (буквы):   {cipher_text}")

    # Расшифрование
    decrypted_numbers = cipher.decrypt_text(cipher_numbers, a, b)
    print(f"Расшифрованный текст (числа): {decrypted_numbers}")
    
    decrypted_text = cipher.numbers_to_text(decrypted_numbers)
    print(f"Расшифрованный текст (буквы): {decrypted_text}")
    print()

    # Атака по двум парам
    print("=== АТАКА ПО ДВУМ ПАРАМ ===")
    # Знаем две пары (m, c)
    pairs = [(plain_numbers[0], cipher_numbers[0]), (plain_numbers[1], cipher_numbers[1])]
    print(f"Известные пары: {[(m, c) for m, c in pairs]}")

    recovered_key = cipher.recover_key_from_pairs(pairs)
    print(f"Восстановленный ключ: a = {recovered_key[0]}, b = {recovered_key[1]}")

    # Проверка: шифруем с восстановленным ключом
    test_cipher = cipher.encrypt_text(plain_numbers, recovered_key[0], recovered_key[1])
    print(f"Шифротекст восстановленным ключом: {test_cipher}")
    print(f"Совпадает с исходным? {test_cipher == cipher_numbers}")

    # Пример с необратимым a
    print("\n=== ПРИМЕР С НЕДОПУСТИМЫМ КЛЮЧОМ ===")
    a_bad, b_bad = 2, 3  # gcd(2,26)=2 ≠ 1
    try:
        cipher.encrypt_text(plain_numbers, a_bad, b_bad)
    except ValueError as e:
        print(f"Ошибка: {e}")

    # Частотный анализ и атака
    print("\n=== ЧАСТОТНЫЙ АНАЛИЗ И АТАКА ===")
    
    # Более длинный текст для демонстрации
    sample_text = "EEEEETTTTTOOOOOAAAAA"  # много повторяющихся букв
    sample_numbers = cipher.text_to_numbers(sample_text)
    sample_cipher = cipher.encrypt_text(sample_numbers, a, b)
    
    from collections import Counter
    
    print(f"Исходный текст: {sample_text}")
    print(f"Исходные частоты (буквы): {Counter(sample_text)}")
    print(f"Шифротекст (буквы): {cipher.numbers_to_text(sample_cipher)}")
    print(f"Частоты шифротекста (буквы): {Counter(cipher.numbers_to_text(sample_cipher))}")
    print("Частоты сохранились — уязвимость к частотному анализу")
    
    # Атака через частотный анализ
    print("\n=== АТАКА ЧЕРЕЗ ЧАСТОТНЫЙ АНАЛИЗ ===")
    
    # Типичные частоты для английского языка (упрощённо)
    # E (4) - самая частая, T (19) - вторая по частоте
    freq_plain = {4: 'E', 19: 'T', 0: 'A', 14: 'O', 13: 'N'}
    
    # Находим самые частые буквы в шифротексте
    cipher_text_str = cipher.numbers_to_text(sample_cipher)
    cipher_freq = Counter(cipher_text_str)
    most_common_cipher = cipher_freq.most_common(3)  # топ-3
    
    print(f"Самые частые буквы в шифротексте: {most_common_cipher}")
    
    # Пробуем предположить, что самая частая буква шифротекста = E
    if len(most_common_cipher) >= 2:
        most_freq_cipher_char = most_common_cipher[0][0]
        second_freq_cipher_char = most_common_cipher[1][0]
        
        most_freq_cipher_num = ord(most_freq_cipher_char) - ord('A')
        second_freq_cipher_num = ord(second_freq_cipher_char) - ord('A')
        
        print(f"\nПредполагаем, что '{most_freq_cipher_char}' ({most_freq_cipher_num}) = 'E' (4)")
        print(f"Предполагаем, что '{second_freq_cipher_char}' ({second_freq_cipher_num}) = 'T' (19)")
        
        # Решаем систему:
        # most_freq_cipher_num = a*4 + b mod 26
        # second_freq_cipher_num = a*19 + b mod 26
        
        delta_m = (4 - 19) % 26
        delta_c = (most_freq_cipher_num - second_freq_cipher_num) % 26
        
        gcd = math.gcd(delta_m, 26)
        
        if gcd == 1:
            delta_m_inv = cipher._mod_inverse(delta_m)
            if delta_m_inv:
                a_guess = (delta_c * delta_m_inv) % 26
                b_guess = (most_freq_cipher_num - a_guess * 4) % 26
                
                print(f"\nВычисленный ключ по частотному анализу: a = {a_guess}, b = {b_guess}")
                
                # Проверяем
                decrypted_guess = cipher.decrypt_text(sample_cipher, a_guess, b_guess)
                decrypted_text_guess = cipher.numbers_to_text(decrypted_guess)
                print(f"Расшифрованный текст: {decrypted_text_guess}")
                print(f"Совпадает с исходным? {decrypted_text_guess == sample_text}")
                
                if decrypted_text_guess == sample_text:
                    print("✅ Атака успешна! Ключ восстановлен.")
                else:
                    print("❌ Атака не удалась — возможно, другие частоты.")
        else:
            print(f"НОД = {gcd} > 1, нужно больше пар для однозначного восстановления")


if __name__ == "__main__":
    demo()