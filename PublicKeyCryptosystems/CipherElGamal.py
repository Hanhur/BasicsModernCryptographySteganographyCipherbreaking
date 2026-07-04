# Шифр Эль-Гамаля
"""
Шифр Эль-Гамаля
Реализация на основе теоретического описания из текста.
"""

import random
import math


def mod_pow(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю.
    Вычисляет (base^exponent) % modulus эффективно.
    """
    return pow(base, exponent, modulus)


def is_primitive_root(g, p):
    """
    Проверяет, является ли g первообразным корнем по модулю p.
    Для простоты проверяем, что все степени g от 1 до p - 1 дают различные значения.
    Для больших p это неэффективно, но для демонстрации подходит.
    """
    if g <= 1 or g >= p:
        return False
    
    seen = set()
    for i in range(1, p):
        val = mod_pow(g, i, p)
        if val in seen:
            return False
        seen.add(val)
    
    # Должно быть p-1 различных значений (все ненулевые)
    return len(seen) == p - 1


def generate_parameters(p = None, g = None):
    """
    Генерирует или принимает параметры для системы Эль-Гамаля.
    Возвращает (p, g).
    """
    if p is None:
        # Для примера используем небольшое простое число
        # В реальных системах p должно быть очень большим (например, 2048 бит)
        primes = [23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        p = random.choice(primes)
    
    if g is None:
        # Находим первообразный корень
        for g_candidate in range(2, p):
            if is_primitive_root(g_candidate, p):
                g = g_candidate
                break
        else:
            raise ValueError(f"Не найден первообразный корень для p = {p}")
    
    return p, g


class ElGamalUser:
    """
    Класс, представляющий абонента в системе Эль-Гамаля.
    """
    
    def __init__(self, name, p, g):
        """
        Инициализация пользователя.
        
        Аргументы:
            name: имя пользователя (A, B, C, ...)
            p: простое число (публичный параметр)
            g: первообразный корень (публичный параметр)
        """
        self.name = name
        self.p = p
        self.g = g
        
        # Генерация секретного ключа (1 < c < p-1)
        self.private_key = random.randint(2, p - 2)
        
        # Вычисление открытого ключа: d = g^c mod p
        self.public_key = mod_pow(g, self.private_key, p)
        
        print(f"Абонент {name}:")
        print(f"  Секретный ключ c_{name} = {self.private_key}")
        print(f"  Открытый ключ d_{name} = {self.public_key}")
        print()
    
    def encrypt(self, message, recipient_public_key, k = None):
        """
        Шифрование сообщения для получателя.
        
        Аргументы:
            message: сообщение (число m < p)
            recipient_public_key: открытый ключ получателя (d_B)
            k: случайное число (если None, генерируется автоматически)
        
        Возвращает:
            (r, e): зашифрованное сообщение в виде пары чисел
        """
        if message >= self.p:
            raise ValueError(f"Сообщение должно быть меньше p = {self.p}")
        
        # Шаг 1: выбор случайного k (1 <= k <= p-2)
        if k is None:
            k = random.randint(1, self.p - 2)
        
        print(f"\n{self.name} отправляет сообщение:")
        print(f"  Исходное сообщение m = {message}")
        print(f"  Выбранное случайное k = {k}")
        
        # Вычисление r = g^k mod p
        r = mod_pow(self.g, k, self.p)
        
        # Вычисление e = m * (d_B)^k mod p
        e = (message * mod_pow(recipient_public_key, k, self.p)) % self.p
        
        print(f"  r = g ^ k mod p = {r}")
        print(f"  e = m * d_B ^ k mod p = {e}")
        print(f"  Отправляется пара (r, e) = ({r}, {e})")
        
        return (r, e)
    
    def decrypt(self, encrypted_message):
        """
        Расшифрование полученного сообщения.
        
        Аргументы:
            encrypted_message: пара (r, e)
        
        Возвращает:
            расшифрованное сообщение m
        """
        r, e = encrypted_message
        
        print(f"\n{self.name} получил пару (r, e) = ({r}, {e})")
        print(f"  Используется секретный ключ c_{self.name} = {self.private_key}")
        
        # Вычисление m' = e * r^(p-1-c) mod p
        exponent = self.p - 1 - self.private_key
        r_power = mod_pow(r, exponent, self.p)
        decrypted = (e * r_power) % self.p
        
        print(f"  r ^ (p - 1 - c) = {r} ^ {exponent} mod {self.p} = {r_power}")
        print(f"  m' = e * r ^ (p - 1 -c) mod p = {decrypted}")
        
        return decrypted


def print_table(users):
    """
    Вывод таблицы ключей всех пользователей.
    """
    print("\n" + "=" * 50)
    print("Таблица ключей пользователей в системе Эль-Гамаля")
    print("=" * 50)
    print(f"{'Абонент':<10} {'Секретный ключ':<20} {'Открытый ключ':<20}")
    print("-" * 50)
    for user in users:
        print(f"{user.name:<10} {user.private_key:<20} {user.public_key:<20}")
    print("=" * 50 + "\n")


def main():
    """
    Демонстрация работы шифра Эль-Гамаля.
    """
    print("=" * 60)
    print("ШИФР ЭЛЬ-ГАМАЛЯ")
    print("=" * 60)
    
    # Шаг 1: Выбор публичных параметров
    print("\n1. Выбор публичных параметров:")
    p = 23  # Простое число
    g = 5   # Первообразный корень
    
    # Проверка, что g - первообразный корень
    if not is_primitive_root(g, p):
        print(f"Ошибка: {g} не является первообразным корнем по модулю {p}")
        return
    
    print(f"   Выбрано простое число p = {p}")
    print(f"   Выбран первообразный корень g = {g}")
    print(f"   Параметры (p, g) = ({p}, {g}) являются открытыми\n")
    
    # Шаг 2: Создание пользователей
    print("2. Генерация ключей для абонентов:")
    print("-" * 40)
    
    # Создаём абонентов A, B, C
    users = {
        'A': ElGamalUser('A', p, g),
        'B': ElGamalUser('B', p, g),
        'C': ElGamalUser('C', p, g)
    }
    
    # Вывод таблицы ключей
    print_table(list(users.values()))
    
    # Шаг 3: Передача сообщения от A к B
    print("\n3. Передача сообщения от A к B:")
    print("-" * 40)
    
    A = users['A']
    B = users['B']
    
    # Сообщение для передачи
    m = 15
    print(f"   A хочет передать сообщение m = {m} абоненту B")
    
    # A шифрует сообщение
    r, e = A.encrypt(m, B.public_key, k = 7)  # k=7 для совпадения с примером из текста
    
    # B расшифровывает
    decrypted = B.decrypt((r, e))
    
    # Проверка
    print(f"\n{'=' * 40}")
    print(f"Результат: {decrypted == m}")
    print(f"Расшифрованное сообщение m' = {decrypted}")
    print(f"Исходное сообщение m = {m}")
    print('=' * 40)
    
    # Шаг 4: Передача сообщения от C к A (с другим случайным k)
    print("\n\n4. Передача сообщения от C к A:")
    print("-" * 40)
    
    C = users['C']
    A = users['A']
    
    m2 = 42 % p  # Сообщение должно быть меньше p
    print(f"   C хочет передать сообщение m = {m2} абоненту A")
    
    # C шифрует (с новым случайным k)
    r2, e2 = C.encrypt(m2, A.public_key)  # k генерируется автоматически
    
    # A расшифровывает
    decrypted2 = A.decrypt((r2, e2))
    
    print(f"\n{'=' * 40}")
    print(f"Результат: {decrypted2 == m2}")
    print(f"Расшифрованное сообщение m' = {decrypted2}")
    print(f"Исходное сообщение m = {m2}")
    print('=' * 40)
    
    # Шаг 5: Демонстрация стойкости (противник не может расшифровать)
    print("\n\n5. Демонстрация стойкости:")
    print("-" * 40)
    print("Противник знает:")
    print(f"  p = {p}, g = {g}")
    print(f"  Открытый ключ B: d_B = {B.public_key}")
    print(f"  Перехваченные (r, e) = ({r}, {e})")
    print("\n  Чтобы расшифровать, противнику нужно:")
    print(f"  1) Найти k из r = g ^ k mod p (задача дискретного логарифмирования)")
    print(f"  2) Найти c_B из d_B = g ^ c_B mod p (задача дискретного логарифмирования)")
    print(f"  3) Или вычислить m из e = m * d_B ^ k mod p без знания k или c_B")
    print("\n  Это вычислительно сложно для больших p!")


if __name__ == "__main__":
    main()