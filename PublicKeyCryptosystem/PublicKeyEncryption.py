# 1. Идея шифрования с открытым ключом
"""
RSA — учебная реализация (на основе текста об односторонней функции с секретом)
Иллюстрирует:
- Генерацию открытого (e, n) и секретного (d, n) ключей
- Шифрование открытым ключом
- Дешифрование секретным ключом
"""

import random
from math import gcd

# ---------- Вспомогательные функции ----------
def is_prime(n, k = 5):
    """Проверка простоты числа (тест Миллера–Рабина) — учебная версия"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = 2^s * d
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    def check(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        return False
    
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not check(a):
            return False
    return True

def generate_prime(bits = 8):
    """Генерация простого числа (бит — учебное, для маленьких чисел)"""
    while True:
        num = random.randrange(2 ** (bits - 1), 2 ** bits)
        if is_prime(num):
            return num

def modinv(a, m):
    """Обратное число по модулю (расширенный алгоритм Евклида)"""
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

# ---------- Основной класс RSA ----------
class RSA:
    def __init__(self, key_size = 16):
        """
        key_size — длина ключа в битах (в учебных целях 16-24 бита)
        Реальные системы используют 2048+ бит
        """
        self.key_size = key_size
        
        # Генерация двух разных простых чисел p и q
        p = generate_prime(key_size // 2)
        q = generate_prime(key_size // 2)
        while q == p:
            q = generate_prime(key_size // 2)
        
        self.p = p
        self.q = q
        self.n = p * q                 # модуль (часть открытого и секретного ключа)
        self.phi = (p - 1) * (q - 1)   # функция Эйлера
        
        # Выбираем открытую экспоненту e (обычно 65537, но для малых чисел используем 17)
        self.e = 17
        while gcd(self.e, self.phi) != 1:
            self.e += 2
        
        # Секретная экспонента d: e * d ≡ 1 (mod phi)
        self.d = modinv(self.e, self.phi)
        
        # Открытый ключ (e, n), секретный (d, n)
        print(f"=== Генерация ключей (длина {key_size} бит) ===")
        print(f"Простые числа: p = {self.p}, q = {self.q}")
        print(f"Модуль n = {self.n}")
        print(f"Открытая экспонента e = {self.e}")
        print(f"Секретная экспонента d = {self.d}")
        print("=" * 40)
    
    def encrypt(self, message_int, public_key = None):
        """
        Шифрование открытым ключом (e, n)
        Если public_key не передан, используется (self.e, self.n)
        """
        if public_key is None:
            e, n = self.e, self.n
        else:
            e, n = public_key
        
        # c = m^e mod n
        return pow(message_int, e, n)
    
    def decrypt(self, cipher_int):
        """Дешифрование секретным ключом (d, n)"""
        # m = c^d mod n
        return pow(cipher_int, self.d, self.n)
    
    def get_public_key(self):
        """Возвращает открытый ключ (e, n)"""
        return (self.e, self.n)
    
    def get_private_key(self):
        """Возвращает секретный ключ (d, n) — только для демонстрации"""
        return (self.d, self.n)


# ---------- Демонстрация работы ----------
def demo():
    print("Криптосистема RSA — иллюстрация односторонней функции с секретом\n")
    
    # 1. Генерация ключей (у получателя)
    print("1. Получатель генерирует пару ключей:")
    rsa = RSA(key_size = 16)  # 16 бит = ~65k максимум для шифрования числа
    
    # 2. Открытый ключ публикуется
    public_key = rsa.get_public_key()
    print(f"Открытый ключ (e, n) = {public_key}  →  публикуется в «телефонной книге»")
    print(f"Секретный ключ (d, n) = {rsa.get_private_key()} → известен только получателю\n")
    
    # 3. Отправитель шифрует сообщение (число) открытым ключом
    original_message = 42  # простое число для примера (сообщение должно быть < n)
    print(f"2. Отправитель хочет передать число: {original_message}")
    cipher = rsa.encrypt(original_message, public_key)
    print(f"   Шифротекст (c = m ^ e mod n): {cipher}")
    
    # 4. Получатель расшифровывает своим секретным ключом
    decrypted = rsa.decrypt(cipher)
    print(f"3. Получатель расшифровывает (c ^ d mod n): {decrypted}")
    
    # 5. Проверка
    if decrypted == original_message:
        print("\n✅ Успех! Расшифрованное сообщение совпадает с исходным.")
    else:
        print("\n❌ Ошибка!")
    
    # 6. Демонстрация невозможности расшифровки без секрета (иллюзия взлома)
    print("\n4. Что если злоумышленник знает только открытый ключ?")
    print(f"   Он видит: n = {rsa.n}, e = {rsa.e}, шифротекст = {cipher}")
    print("   Чтобы расшифровать, нужно найти d. Для этого надо знать φ(n) = (p - 1) * (q - 1).")
    print(f"   φ(n) = {rsa.phi}. Но чтобы его вычислить, надо разложить n = {rsa.n} на p и q.")
    print("   При больших n (например, 2048 бит) факторизация — трудная задача.")
    print("   Это и есть ОДНОСТОРОННЯЯ ФУНКЦИЯ С СЕКРЕТОМ (секрет — знание p и q).")


# ---------- Пример шифрования текста (не только чисел) ----------
def demo_text():
    print("\n" + "=" * 50)
    print("Пример шифрования короткого текста (кодировка чисел < n)")
    print("=" * 50)
    
    rsa = RSA(key_size = 20)  # чуть больше бит, чтобы влезло несколько символов
    
    # Сообщение в виде строки
    plaintext = "HELLO"
    print(f"\nИсходный текст: {plaintext}")
    
    # Преобразуем текст в число (конкатенация кодов ASCII)
    message_int = 0
    for ch in plaintext:
        message_int = message_int * 256 + ord(ch)
    
    print(f"Числовое представление: {message_int}")
    print(f"Проверка: оно должно быть меньше n = {rsa.n} → {'OK' if message_int < rsa.n else 'Слишком большое для учебного примера'}")
    
    if message_int >= rsa.n:
        print("(Для реального использования RSA так не делают — используют гибридное шифрование)")
        return
    
    # Шифрование
    cipher = rsa.encrypt(message_int)
    print(f"Шифротекст (число): {cipher}")
    
    # Дешифрование
    decrypted_int = rsa.decrypt(cipher)
    
    # Восстанавливаем текст
    decrypted_text = ""
    temp = decrypted_int
    while temp > 0:
        decrypted_text = chr(temp % 256) + decrypted_text
        temp //= 256
    
    print(f"Расшифрованный текст: {decrypted_text}")
    if decrypted_text == plaintext:
        print("✅ Текст восстановлен корректно!")


# ---------- Запуск ----------
if __name__ == "__main__":
    demo()
    demo_text()