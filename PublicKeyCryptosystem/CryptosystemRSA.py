# 2. Криптасистема RSA
import random
import math

def gcd(a, b):
    """Наибольший общий делитель"""
    while b:
        a, b = b, a % b
    return a

def egcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y), где a * x + b * y = g = gcd(a, b)"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратный элемент a по модулю m (требует gcd(a, m) = 1)"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception("Обратного элемента не существует")
    else:
        return x % m

def is_prime(n, k = 5):
    """Простая проверка на простоту (Миллер-Рабин)"""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    d = n-1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits = 8):
    """Генерация простого числа заданной битовой длины"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def text_to_number(text):
    """
    Преобразует 3-граф (ровно 3 буквы A-Z) в число по 26-ричной системе.
    A<->0, B<->1, ..., Z<->25.
    """
    if len(text) != 3:
        raise ValueError("Длина текста должна быть ровно 3 символа")
    num = 0
    for ch in text.upper():
        if ch < 'A' or ch > 'Z':
            raise ValueError(f"Недопустимый символ: {ch}. Разрешены только A-Z")
        num = num * 26 + (ord(ch) - ord('A'))
    return num

def number_to_text(num):
    """Обратное преобразование: число -> 3-граф"""
    if num < 0 or num >= 26 ** 3:
        raise ValueError(f"Число {num} вне диапазона 0..{26 ** 3 - 1} для 3-графа")
    res = []
    for _ in range(3):
        num, rem = divmod(num, 26)
        res.append(chr(rem + ord('A')))
    return ''.join(reversed(res))

def string_to_blocks(text, block_size=3):
    """
    Преобразует строку произвольной длины в список блоков по block_size символов.
    Последний блок дополняется буквой 'X' при необходимости.
    """
    text = text.upper()
    # Удаляем все символы, не являющиеся буквами
    text = ''.join([ch for ch in text if ch >= 'A' and ch <= 'Z'])
    
    blocks = []
    for i in range(0, len(text), block_size):
        block = text[i:i + block_size]
        if len(block) < block_size:
            block = block + 'X' * (block_size - len(block))
        blocks.append(block)
    return blocks

# ========== Класс RSA ==========
class RSA:
    def __init__(self, p, q, e = None):
        """
        Инициализация RSA с заданными p и q.
        Если e не задан — выбирается случайное, взаимно простое с φ(n).
        """
        self.p = p
        self.q = q
        self.n = p * q
        self.phi = (p - 1) * (q - 1)

        if e is None:
            e = random.randrange(2, self.phi)
            while gcd(e, self.phi) != 1:
                e = random.randrange(2, self.phi)
        else:
            if gcd(e, self.phi) != 1:
                raise ValueError(f"e = {e} не взаимно просто с φ(n) = {self.phi}")

        self.e = e
        self.d = modinv(e, self.phi)

    def encrypt(self, m):
        """Шифрование числа m (0 ≤ m < n)"""
        if m < 0 or m >= self.n:
            raise ValueError(f"Число {m} вне диапазона 0..{self.n - 1}")
        return pow(m, self.e, self.n)

    def decrypt(self, c):
        """Дешифрование числа c"""
        return pow(c, self.d, self.n)

    def encrypt_text(self, text):
        """
        Шифрует текст произвольной длины.
        Разбивает на 3-графы, преобразует в числа, шифрует каждое число.
        Возвращает список шифротекстов (чисел).
        """
        blocks = string_to_blocks(text, 3)
        cipher_numbers = []
        for block in blocks:
            m = text_to_number(block)
            c = self.encrypt(m)
            cipher_numbers.append(c)
        return cipher_numbers

    def decrypt_text(self, cipher_numbers):
        """
        Дешифрует список чисел в текст.
        """
        decrypted_blocks = []
        for c in cipher_numbers:
            m = self.decrypt(c)
            block = number_to_text(m)
            decrypted_blocks.append(block)
        return ''.join(decrypted_blocks)

# ========== Демонстрация на примере из текста ==========
def demo_from_text():
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НА ПРИМЕРЕ ИЗ ТЕКСТА (YES)")
    print("=" * 60)
    
    # Параметры из текста
    p = 281
    q = 167
    e = 46377
    
    rsa = RSA(p, q, e)
    print(f"p = {p}, q = {q}")
    print(f"n = {rsa.n} (открытый модуль)")
    print(f"e = {rsa.e} (открытый ключ)")
    print(f"d = {rsa.d} (секретный ключ)")
    print(f"φ(n) = {rsa.phi} (секретно)")
    
    # Слово YES -> число
    word = "YES"
    m = text_to_number(word)
    print(f"\nИсходное слово: {word}")
    print(f"Числовое представление (26-ричное): {m}")
    
    # Шифрование
    c = rsa.encrypt(m)
    print(f"Шифротекст (число): {c}")
    
    # Дешифрование
    decrypted_m = rsa.decrypt(c)
    decrypted_word = number_to_text(decrypted_m)
    print(f"Расшифрованное число: {decrypted_m}")
    print(f"Расшифрованное слово: {decrypted_word}")
    
    assert decrypted_word == word, "Ошибка: расшифровка не совпала!"
    print("\n✓ Тест из текста пройден успешно!")

# ========== Демонстрация работы для разных типов сообщений ==========
def demo_edge_cases():
    """
    Демонстрация того, что RSA работает для любых m (в том числе не взаимно простых с n)
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ ДЛЯ ЛЮБЫХ m (включая кратные p или q)")
    print("=" * 60)
    
    p = 281
    q = 167
    rsa = RSA(p, q, e = 46377)
    
    # Случай 1: m взаимно просто с n
    m1 = 12345
    c1 = rsa.encrypt(m1)
    m1_dec = rsa.decrypt(c1)
    print(f"\n1. m = {m1} (взаимно просто с {rsa.n}): расшифровано -> {m1_dec}")
    assert m1_dec == m1
    
    # Случай 2: m кратно p (но не n)
    m2 = p * 2  # 562
    print(f"2. m = {m2} (кратно p = {p})")
    c2 = rsa.encrypt(m2)
    m2_dec = rsa.decrypt(c2)
    print(f"   Шифротекст: {c2}, расшифровано: {m2_dec} (должно быть {m2})")
    assert m2_dec == m2
    
    # Случай 3: m кратно q
    m3 = q * 3  # 501
    print(f"3. m = {m3} (кратно q = {q})")
    c3 = rsa.encrypt(m3)
    m3_dec = rsa.decrypt(c3)
    print(f"   Шифротекст: {c3}, расшифровано: {m3_dec} (должно быть {m3})")
    assert m3_dec == m3
    
    # Случай 4: m = 0
    m4 = 0
    c4 = rsa.encrypt(m4)
    m4_dec = rsa.decrypt(c4)
    print(f"4. m = 0: шифр {c4}, расшифровано {m4_dec}")
    assert m4_dec == 0
    
    print("\n✓ Все граничные случаи успешно пройдены!")

# ========== Демонстрация с λ(n) = lcm(p-1,q-1) ==========
def demo_lambda_vs_phi():
    """
    Демонстрация использования λ(n) = lcm(p - 1, q - 1) вместо φ(n)
    для получения меньшего d
    """
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ φ(n) И λ(n) ДЛЯ ВЫЧИСЛЕНИЯ СЕКРЕТНОЙ ЭКСПОНЕНТЫ")
    print("=" * 60)
    
    p = 281
    q = 167
    n = p * q
    phi = (p - 1) * (q - 1)
    lambda_n = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)
    
    print(f"p = {p}, q = {q}")
    print(f"n = {n}")
    print(f"φ(n) = {phi}")
    print(f"λ(n) = {lambda_n}")
    print(f"λ(n) в {phi // lambda_n} раз меньше, чем φ(n)")
    
    e = 46377
    d_phi = modinv(e, phi)
    d_lambda = modinv(e, lambda_n)
    
    print(f"\nd (из φ(n)) = {d_phi}")
    print(f"d (из λ(n)) = {d_lambda}")
    
    # Проверка, что оба d работают
    m = text_to_number("YES")
    c = pow(m, e, n)
    m1 = pow(c, d_phi, n)
    m2 = pow(c, d_lambda, n)
    
    print(f"\nДля сообщения YES:")
    print(f"  Расшифровка через d_phi -> {number_to_text(m1)}")
    print(f"  Расшифровка через d_lambda -> {number_to_text(m2)}")
    
    assert m1 == m2 == m
    print("\n✓ Оба ключа дешифруют корректно!")

# ========== Демонстрация с разными словами ==========
def demo_different_words():
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НА РАЗНЫХ 3-ГРАФАХ")
    print("=" * 60)
    
    p = 281
    q = 167
    rsa = RSA(p, q, e = 46377)
    
    # Только 3-символьные слова
    test_words = ["YES", "NOX", "ABC", "XYZ", "RSA", "TOP", "CAT", "DOG", "SUN", "CAR"]
    
    for word in test_words:
        m = text_to_number(word)
        c = rsa.encrypt(m)
        m2 = rsa.decrypt(c)
        word2 = number_to_text(m2)
        print(f"\n{word:3} -> число {m:5} -> шифр {c:8} -> число {m2:5} -> {word2}")
        assert word == word2
    
    print("\n✓ Все слова успешно зашифрованы и расшифрованы!")

# ========== Демонстрация с произвольным текстом ==========
def demo_arbitrary_text():
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С ПРОИЗВОЛЬНЫМ ТЕКСТОМ")
    print("=" * 60)
    
    p = 281
    q = 167
    rsa = RSA(p, q, e = 46377)
    
    # Исходный текст произвольной длины
    original_text = "HELLO WORLD"
    print(f"Исходный текст: {original_text}")
    
    # Разбиваем на блоки и шифруем
    blocks = string_to_blocks(original_text, 3)
    print(f"Блоки (3-графы): {blocks}")
    
    # Шифрование
    cipher_numbers = []
    for block in blocks:
        m = text_to_number(block)
        c = rsa.encrypt(m)
        cipher_numbers.append(c)
    print(f"Шифротексты (числа): {cipher_numbers}")
    
    # Дешифрование
    decrypted_blocks = []
    for c in cipher_numbers:
        m = rsa.decrypt(c)
        block = number_to_text(m)
        decrypted_blocks.append(block)
    decrypted_text = ''.join(decrypted_blocks)
    print(f"Расшифрованный текст: {decrypted_text}")
    
    # Обратите внимание: "HELLO WORLD" → без пробелов + дополнение до 3-граф
    expected_text = "HEL LOW ORL DXX".replace(" ", "")
    print(f"Ожидаемый текст (после обработки): {expected_text}")
    assert decrypted_text == expected_text
    
    print("\n✓ Произвольный текст успешно зашифрован и расшифрован!")

# ========== Запуск всех демонстраций ==========
if __name__ == "__main__":
    demo_from_text()
    demo_edge_cases()
    demo_lambda_vs_phi()
    demo_different_words()
    demo_arbitrary_text()
    
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
    print("=" * 60)