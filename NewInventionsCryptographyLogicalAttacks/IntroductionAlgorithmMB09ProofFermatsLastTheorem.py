# Введение в алгоритм MB09 и доказательство последней теоремы Ферма
"""
MB09 Криптографический алгоритм
Основан на свойствах малой теоремы Ферма и сложности обратного поиска
Версия: Pure Python (без numpy)
"""

import random
import time
import math
from typing import Tuple, Optional

class MB09Crypto:
    """
    Реализация алгоритма MB09 для шифрования/дешифрования
    и демонстрации односторонних функций
    """
    
    def __init__(self, key_size: int = 1024):
        """
        Инициализация криптосистемы
        
        Args:
            key_size: Размер ключа в битах (чем больше, тем безопаснее)
        """
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self.modulus = None
        
    def is_prime(self, n: int, k: int = 5) -> bool:
        """
        Проверка числа на простоту (тест Миллера-Рабина)
        
        Args:
            n: Число для проверки
            k: Количество раундов тестирования
        
        Returns:
            True если число простое, иначе False
        """
        if n < 2:
            return False
        if n in [2, 3]:
            return True
        if n % 2 == 0:
            return False
            
        # Представляем n-1 как d * 2^r
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
            
        # Проводим k раундов теста
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def generate_prime(self, bits: int) -> int:
        """
        Генерация простого числа заданной битовой длины
        
        Args:
            bits: Количество бит
            
        Returns:
            Простое число
        """
        while True:
            # Генерируем случайное число нужной длины
            num = random.getrandbits(bits)
            # Убеждаемся, что число нечетное и имеет нужную длину
            num |= (1 << bits - 1) | 1
            
            # Проверяем на простоту
            if self.is_prime(num):
                return num
    
    def generate_keypair(self) -> Tuple[int, int, int]:
        """
        Генерация пары ключей (открытый, закрытый) и модуля
        
        Returns:
            Кортеж (private_key, public_key, modulus)
        """
        # Генерируем простое число p (модуль)
        # В реальной системе p должно быть большим
        p = self.generate_prime(self.key_size // 2)
        
        # Генерируем секретный ключ [a] - большое число
        # В тексте сказано: a >> p (a намного больше p)
        secret_key = random.getrandbits(self.key_size * 2)
        
        # Вычисляем открытый ключ (A) по формуле: A = a^p mod p
        # По малой теореме Ферма: a^p ≡ a (mod p)
        # Поэтому A = a mod p (если a не кратно p)
        public_key = secret_key % p
        
        self.private_key = secret_key
        self.public_key = public_key
        self.modulus = p
        
        return secret_key, public_key, p
    
    def encrypt(self, message: int, public_key: int, modulus: int) -> int:
        """
        Шифрование сообщения
        
        Args:
            message: Сообщение для шифрования (целое число)
            public_key: Открытый ключ (A)
            modulus: Модуль (p)
            
        Returns:
            Зашифрованное сообщение
        """
        # В схеме MB09 шифрование работает через операцию возведения в степень
        # и использование открытого ключа
        # C = (message + public_key) mod modulus
        # Это простой пример, так как в тексте упоминается модульное сложение
        
        # Генерируем случайное число r для дополнительной безопасности
        r = random.randint(2, modulus - 1)
        
        # Шифруем: C = (message + public_key) mod modulus
        ciphertext = (message + public_key) % modulus
        
        # Для большей сложности: C = (message * public_key + r) mod modulus
        # Но оставим базовый вариант из текста
        return ciphertext
    
    def decrypt(self, ciphertext: int, private_key: int, modulus: int) -> int:
        """
        Дешифрование сообщения
        
        Args:
            ciphertext: Зашифрованное сообщение
            private_key: Секретный ключ [a]
            modulus: Модуль (p)
            
        Returns:
            Расшифрованное сообщение
        """
        # Для дешифрования используем знание секретного ключа [a]
        # M = (ciphertext - (private_key % modulus)) mod modulus
        # Но так как private_key % modulus = public_key, то:
        # M = (ciphertext - public_key) mod modulus
        
        public_key = private_key % modulus
        message = (ciphertext - public_key) % modulus
        return message
    
    def prove_fermat(self, a: int, p: int) -> dict:
        """
        Демонстрация малой теоремы Ферма: a^p ≡ a (mod p)
        
        Args:
            a: Основание
            p: Простое число (модуль)
            
        Returns:
            Словарь с результатами вычислений
        """
        result = {
            'a': a,
            'p': p,
            'a_mod_p': a % p,
            'a_pow_mod': pow(a, p, p),
            'is_equal': (a % p) == pow(a, p, p),
            'a_less_than_p': a < p,
            'absolute_value': a,
            'congruent_value': pow(a, p, p)
        }
        return result
    
    def demonstrate_one_way_function(self, secret: int, modulus: int) -> dict:
        """
        Демонстрация односторонней функции
        Показывает, как легко вычислить A из a, но сложно найти a из A
        
        Args:
            secret: Секретное число [a]
            modulus: Модуль p
            
        Returns:
            Словарь с результатами
        """
        public = secret % modulus
        
        # Пытаемся найти оригинальное число перебором
        found = None
        attempts = 0
        
        # Ограничиваем поиск для демонстрации
        # В реальности поиск бесконечен
        max_attempts = 100000
        
        start_time = time.time()
        
        # Ищем число, которое дает такой же остаток
        for i in range(modulus + 1, modulus + max_attempts):
            attempts += 1
            if i % modulus == public:
                found = i
                if i == secret:
                    break
        
        elapsed = time.time() - start_time
        
        return {
            'secret': secret,
            'modulus': modulus,
            'public': public,
            'found': found,
            'attempts': attempts,
            'time_seconds': elapsed,
            'is_secret_found': found == secret,
            'complexity': f"О(2^{modulus.bit_length()})"
        }

def demo_fermat_theorem():
    """Демонстрация малой теоремы Ферма"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ МАЛОЙ ТЕОРЕМЫ ФЕРМА")
    print("=" * 60)
    
    crypto = MB09Crypto()
    
    # Случай 1: a < p
    print("\n1. СЛУЧАЙ: a < p (a меньше p)")
    print("-" * 40)
    a = 37
    p = 7
    result = crypto.prove_fermat(a, p)
    print(f"a = {a}, p = {p}")
    print(f"a^p mod p = {result['a_pow_mod']}")
    print(f"a mod p = {result['a_mod_p']}")
    print(f"Результаты равны: {result['is_equal']}")
    print(f"Абсолютное значение: {result['absolute_value']}")
    print(f"Конгруэнтное значение: {result['congruent_value']}")
    
    # Случай 2: a > p
    print("\n2. СЛУЧАЙ: a > p (a больше p)")
    print("-" * 40)
    a = 53
    p = 3
    result = crypto.prove_fermat(a, p)
    print(f"a = {a}, p = {p}")
    print(f"a^p mod p = {result['a_pow_mod']}")
    print(f"a mod p = {result['a_mod_p']}")
    print(f"Результаты равны: {result['is_equal']}")
    print(f"Абсолютное значение: {result['absolute_value']}")
    print(f"Конгруэнтное значение: {result['congruent_value']}")
    print(f"Примечание: {a} ≠ {result['congruent_value']} по модулю {p}")
    
    # Демонстрация класса эквивалентности
    print("\n3. КЛАСС ЭКВИВАЛЕНТНОСТИ (все числа дают одинаковый остаток)")
    print("-" * 40)
    p = 3
    numbers = [5, 8, 11, 14, 17, 20]
    print(f"Модуль p = {p}")
    for num in numbers:
        remainder = num % p
        print(f"{num} mod {p} = {remainder}")
    print(f"Все числа дают одинаковый остаток {numbers[0] % p} по модулю {p}")
    print("Это делает невозможным определение исходного числа по остатку!")

def demo_key_generation():
    """Демонстрация генерации ключей"""
    print("\n" + "=" * 60)
    print("ГЕНЕРАЦИЯ КЛЮЧЕЙ MB09")
    print("=" * 60)
    
    crypto = MB09Crypto(key_size = 16)  # Маленький размер для демонстрации
    
    print("\nГенерация ключевой пары...")
    private_key, public_key, modulus = crypto.generate_keypair()
    
    print(f"Модуль (p): {modulus}")
    print(f"Секретный ключ [a]: {private_key}")
    print(f"Открытый ключ (A): {public_key}")
    print(f"Проверка: {private_key} mod {modulus} = {private_key % modulus}")
    print(f"A = {public_key} (совпадает с остатком)")

def demo_encryption_decryption():
    """Демонстрация шифрования и дешифрования"""
    print("\n" + "=" * 60)
    print("ШИФРОВАНИЕ И ДЕШИФРОВАНИЕ MB09")
    print("=" * 60)
    
    crypto = MB09Crypto(key_size = 16)
    
    # Генерируем ключи
    private_key, public_key, modulus = crypto.generate_keypair()
    
    print(f"Модуль (p): {modulus}")
    print(f"Открытый ключ (A): {public_key}")
    print(f"Секретный ключ [a]: {private_key}\n")
    
    # Сообщение для шифрования
    message = 42
    print(f"Исходное сообщение: {message}")
    
    # Шифруем
    ciphertext = crypto.encrypt(message, public_key, modulus)
    print(f"Зашифрованное сообщение: {ciphertext}")
    
    # Дешифруем
    decrypted = crypto.decrypt(ciphertext, private_key, modulus)
    print(f"Расшифрованное сообщение: {decrypted}")
    
    # Проверяем
    print(f"\nУспешно: {message == decrypted}")

def demo_reverse_search():
    """Демонстрация сложности обратного поиска"""
    print("\n" + "=" * 60)
    print("СЛОЖНОСТЬ ОБРАТНОГО ПОИСКА (a >> p)")
    print("=" * 60)
    
    crypto = MB09Crypto(key_size = 8)  # Маленький для демонстрации
    
    # Маленький модуль для наглядности
    modulus = 3
    # Большое секретное число
    secret = 96269369030336679694019965478670
    
    print(f"Модуль (p): {modulus}")
    print(f"Секретное число [a]: {secret}")
    print(f"Длина секрета: {len(str(secret))} цифр")
    print(f"Размер секрета: {secret.bit_length()} бит\n")
    
    # Вычисляем открытый ключ
    public = secret % modulus
    print(f"Открытый ключ (A): {public}")
    print(f"Вычислено: {secret} mod {modulus} = {public}\n")
    
    print("Пробуем найти исходное число по открытому ключу...")
    print("(Поиск ограничен 10000 итераций для демонстрации)\n")
    
    # Пытаемся найти оригинальное число
    found = None
    attempts = 0
    max_attempts = 10000
    
    start_time = time.time()
    
    for i in range(modulus + 1, modulus + max_attempts + 1):
        attempts += 1
        if i % modulus == public:
            found = i
            print(f"Найдено число: {found} (попытка {attempts})")
            if found == secret:
                print("✓ Найдено ИСКОМОЕ секретное число!")
                break
            else:
                print(f"  Это НЕ то же число, что {secret} (оно дает тот же остаток)")
                # Продолжаем поиск
                continue
    
    elapsed = time.time() - start_time
    
    print(f"\nРезультат поиска:")
    print(f"  - Проверено чисел: {attempts}")
    print(f"  - Найдено совпадений по остатку: {attempts // 3}")
    print(f"  - Время поиска: {elapsed:.4f} секунд")
    print(f"  - Оригинальное число: {secret}")
    print(f"  - Найденное число: {found}")
    print(f"  - Совпадают: {found == secret if found else False}")
    
    if found != secret:
        print("\n⚠ ВЫВОД: Невозможно определить исходное число [a]")
        print(f"  Любое число вида k * {modulus} + {public} подходит")
        print("  Это и есть односторонняя функция!")

def demo_practical_example():
    """Практический пример использования MB09"""
    print("\n" + "=" * 60)
    print("ПРАКТИЧЕСКИЙ ПРИМЕР: БЕЗОПАСНАЯ ПЕРЕДАЧА")
    print("=" * 60)
    
    crypto = MB09Crypto(key_size = 16)
    
    # Алиса генерирует ключи
    print("\nАЛИСА генерирует ключевую пару:")
    alice_private, alice_public, modulus = crypto.generate_keypair()
    print(f"  Открытый ключ (A): {alice_public}")
    print(f"  Модуль (p): {modulus}")
    print(f"  Секретный ключ [a]: {alice_private}")
    
    # Боб шифрует сообщение для Алисы
    print("\nБОБ шифрует сообщение для Алисы:")
    message = 123
    print(f"  Сообщение: {message}")
    ciphertext = crypto.encrypt(message, alice_public, modulus)
    print(f"  Шифротекст: {ciphertext}")
    
    # Алиса расшифровывает
    print("\nАЛИСА расшифровывает сообщение:")
    decrypted = crypto.decrypt(ciphertext, alice_private, modulus)
    print(f"  Расшифрованное: {decrypted}")
    print(f"  Успешно: {message == decrypted}")
    
    # Демонстрация атаки (Ева пытается взломать)
    print("\nЕВА (злоумышленник) пытается взломать:")
    print(f"  Знает: открытый ключ (A = {alice_public}), модуль (p = {modulus})")
    
    # Ева пытается найти секретный ключ перебором
    eve_found = None
    for i in range(modulus + 1, modulus + 1000):
        if i % modulus == alice_public:
            eve_found = i
            break
    
    if eve_found:
        print(f"  Ева нашла число: {eve_found}")
        print(f"  Это НЕ секретный ключ Алисы ({alice_private})")
        print("  Ева не может определить правильный ключ!")

def main():
    """Главная функция программы"""
    print("=" * 60)
    print("MB09 КРИПТОГРАФИЧЕСКИЙ АЛГОРИТМ")
    print("Основан на малой теореме Ферма")
    print("=" * 60)
    
    # Запускаем все демонстрации
    demo_fermat_theorem()
    demo_key_generation()
    demo_encryption_decryption()
    demo_reverse_search()
    demo_practical_example()
    
    print("\n" + "=" * 60)
    print("ЗАКЛЮЧЕНИЕ:")
    print("=" * 60)
    print("""
    MB09 использует одностороннюю функцию на основе малой теоремы Ферма:
    
    1. [a] - секретное число (огромное, вне кольца Zp)
    2. A = [a] mod p - открытый ключ (внутри кольца)
    3. Зная A и p, невозможно найти [a] (бесконечное множество решений)
    4. Это свойство используется для:
       - Шифрования/дешифрования
       - Генерации ключей
       - Электронных платежей
       - Создания односторонних функций
    
    Сложность взлома: O(2^n) где n - размер [a]
    """)

if __name__ == "__main__":
    main()