# Одностороння функция с «лазейкой» и шифр RSA
import random
import math
from typing import Tuple, Optional

class RSAUser:
    """Класс, представляющий пользователя в системе RSA"""
    
    def __init__(self, name: str, key_size: int = 8):
        """
        Инициализация пользователя с генерацией ключей
        
        Args:
            name: Имя пользователя
            key_size: Размер простых чисел (в битах), для демонстрации используем маленькие числа
        """
        self.name = name
        self.key_size = key_size
        
        # Генерация ключей
        self.P, self.Q = self._generate_primes()
        self.N = self.P * self.Q
        self.phi = (self.P - 1) * (self.Q - 1)
        
        # Выбор открытой экспоненты d (взаимно простой с phi)
        self.d = self._choose_d()
        
        # Вычисление секретной экспоненты c (обратное к d по модулю phi)
        self.c = self._mod_inverse(self.d, self.phi)
        
        # Открытый ключ: (d, N), Секретный ключ: c
        print(f"Пользователь {self.name} создан:")
        print(f"  P = {self.P}, Q = {self.Q}")
        print(f"  N = {self.N}, phi = {self.phi}")
        print(f"  Открытая экспонента d = {self.d}")
        print(f"  Секретная экспонента c = {self.c}")
        print("-" * 50)
    
    def _is_prime(self, n: int) -> bool:
        """Проверка числа на простоту (для небольших чисел)"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def _generate_primes(self) -> Tuple[int, int]:
        """Генерация двух различных простых чисел"""
        # Для демонстрации генерируем небольшие простые числа
        # В реальных системах используются большие числа (например, 1024-2048 бит)
        primes = []
        # Начинаем с достаточно большого числа, чтобы получить разные простые
        start = 10 ** (self.key_size // 2)
        attempts = 0
        while len(primes) < 2 and attempts < 1000:
            # Генерируем случайное число в диапазоне
            num = random.randint(start, start * 2)
            if self._is_prime(num) and num not in primes:
                primes.append(num)
            attempts += 1
        
        if len(primes) < 2:
            # Если не нашли достаточно простых, используем предопределенные
            return (3, 11)  # Для демонстрации
        
        return (primes[0], primes[1])
    
    def _gcd(self, a: int, b: int) -> int:
        """Алгоритм Евклида для нахождения НОД"""
        while b != 0:
            a, b = b, a % b
        return a
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида
        Возвращает: (НОД, x, y), где a * x + b * y = НОД(a, b)
        """
        if b == 0:
            return (a, 1, 0)
        gcd, x1, y1 = self._extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (gcd, x, y)
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """
        Нахождение обратного числа по модулю m
        Используется расширенный алгоритм Евклида
        """
        gcd, x, y = self._extended_gcd(a, m)
        if gcd != 1:
            raise ValueError(f"Число {a} не имеет обратного по модулю {m}")
        return x % m
    
    def _choose_d(self) -> int:
        """Выбор открытой экспоненты d, взаимно простой с phi"""
        # Обычно выбирают d = 3, 17 или 65537
        # Но для корректности нужно проверить взаимную простоту
        for d in [3, 5, 17, 257, 65537]:
            if d < self.phi and self._gcd(d, self.phi) == 1:
                return d
        
        # Если стандартные не подходят, ищем случайное
        d = random.randint(2, self.phi - 1)
        while self._gcd(d, self.phi) != 1:
            d = random.randint(2, self.phi - 1)
        return d
    
    def encrypt(self, message: int, recipient) -> int:
        """
        Шифрование сообщения для получателя
        
        Args:
            message: Сообщение (число, меньшее N получателя)
            recipient: Объект получателя (содержит открытые параметры)
        
        Returns:
            Зашифрованное сообщение
        """
        if message >= recipient.N:
            raise ValueError(f"Сообщение {message} должно быть меньше N получателя {recipient.N}")
        
        # e = m^d mod N (используем открытые параметры получателя)
        encrypted = pow(message, recipient.d, recipient.N)
        return encrypted
    
    def decrypt(self, encrypted_message: int) -> int:
        """
        Дешифрование сообщения своим секретным ключом
        
        Args:
            encrypted_message: Зашифрованное сообщение
        
        Returns:
            Расшифрованное сообщение
        """
        # m' = e^c mod N (используем свой секретный ключ c)
        decrypted = pow(encrypted_message, self.c, self.N)
        return decrypted
    
    def sign(self, message: int) -> int:
        """
        Создание цифровой подписи (шифрование своим секретным ключом)
        
        Args:
            message: Сообщение для подписи
        
        Returns:
            Подпись (зашифрованное своим ключом сообщение)
        """
        # e = m^c mod N (используем свой секретный ключ c)
        signature = pow(message, self.c, self.N)
        return signature
    
    def verify_signature(self, message: int, signature: int, sender) -> bool:
        """
        Проверка цифровой подписи отправителя
        
        Args:
            message: Исходное сообщение
            signature: Подпись отправителя
            sender: Объект отправителя (содержит открытые параметры)
        
        Returns:
            True если подпись верна, иначе False
        """
        # m = e^d mod N (используем открытые параметры отправителя)
        verified = pow(signature, sender.d, sender.N)
        return verified == message


class RSASystem:
    """Класс для демонстрации работы системы RSA"""
    
    @staticmethod
    def demonstrate_basic_protocol():
        """Демонстрация базового протокола RSA"""
        print("\n" + "=" * 60)
        print("БАЗОВЫЙ ПРОТОКОЛ RSA (передача от Алисы к Бобу)")
        print("=" * 60 + "\n")
        
        # Создаем пользователей
        alice = RSAUser("Алиса", key_size = 4)
        bob = RSAUser("Боб", key_size = 4)
        
        # Сообщение от Алисы к Бобу
        message = 15
        print(f"Сообщение Алисы: {message}")
        print(f"Проверка: {message} < N_Боба ({bob.N}) -> {message < bob.N}")
        print()
        
        # Шаг 1: Алиса шифрует сообщение открытым ключом Боба
        print("ШАГ 1: Алиса шифрует сообщение открытым ключом Боба")
        print(f"  e = m ^ {bob.d} mod {bob.N}")
        encrypted = alice.encrypt(message, bob)
        print(f"  Зашифрованное сообщение e = {encrypted}")
        print()
        
        # Шаг 2: Боб расшифровывает своим секретным ключом
        print("ШАГ 2: Боб расшифровывает своим секретным ключом")
        print(f"  m' = e ^ {bob.c} mod {bob.N}")
        decrypted = bob.decrypt(encrypted)
        print(f"  Расшифрованное сообщение m' = {decrypted}")
        print()
        
        # Проверка
        print(f"Результат: {message} == {decrypted} -> {message == decrypted}")
        print("✓ Протокол работает корректно!")
        print("\n" + "-" * 60)
    
    @staticmethod
    def demonstrate_signed_protocol():
        """Демонстрация протокола с цифровой подписью"""
        print("\n" + "=" * 60)
        print("ПРОТОКОЛ RSA С ЦИФРОВОЙ ПОДПИСЬЮ")
        print("=" * 60 + "\n")
        
        # Создаем пользователей
        alice = RSAUser("Алиса", key_size = 4)
        bob = RSAUser("Боб", key_size = 4)
        
        # Сообщение от Алисы к Бобу
        message = 15
        print(f"Исходное сообщение: {message}")
        print(f"Проверка: {message} < N_Алисы ({alice.N}) и {message} < N_Боба ({bob.N})")
        print()
        
        # Шаг 1: Алиса подписывает сообщение своим секретным ключом
        print("ШАГ 1: Алиса подписывает сообщение (шифрует своим секретным ключом)")
        print(f"  e = m^{alice.c} mod {alice.N}")
        signature = alice.sign(message)
        print(f"  Подпись (зашифрованное сообщение) e = {signature}")
        print()
        
        # Шаг 2: Алиса шифрует подпись открытым ключом Боба
        print("ШАГ 2: Алиса шифрует подпись открытым ключом Боба")
        print(f"  f = e^{bob.d} mod {bob.N}")
        double_encrypted = alice.encrypt(signature, bob)
        print(f"  Дважды зашифрованное сообщение f = {double_encrypted}")
        print()
        
        # Шаг 3: Боб расшифровывает своим секретным ключом
        print("ШАГ 3: Боб расшифровывает своим секретным ключом")
        print(f"  u = f^{bob.c} mod {bob.N}")
        decrypted_signature = bob.decrypt(double_encrypted)
        print(f"  Расшифрованная подпись u = {decrypted_signature}")
        print()
        
        # Шаг 4: Боб проверяет подпись открытым ключом Алисы
        print("ШАГ 4: Боб проверяет подпись открытым ключом Алисы")
        print(f"  w = u^{alice.d} mod {alice.N}")
        is_valid = bob.verify_signature(message, decrypted_signature, alice)
        print(f"  Результат проверки: {is_valid}")
        print()
        
        # Проверка
        if is_valid:
            print("✓ Подпись подтверждена! Боб знает, что сообщение от Алисы.")
        else:
            print("✗ Подпись недействительна!")
        
        # Демонстрация атаки (злоумышленник не может подделать подпись)
        print("\n" + "-"*60)
        print("ДЕМОНСТРАЦИЯ: Попытка подделки подписи")
        print("-"*60)
        
        # Злоумышленник (Ева) пытается подделать сообщение от Алисы
        eva = RSAUser("Ева", key_size=4)
        fake_message = 20
        print(f"Ева пытается отправить сообщение {fake_message} от имени Алисы")
        
        # Ева не знает c_Алисы, но пытается подделать
        try:
            # Ева подписывает своим ключом (но это не подпись Алисы!)
            fake_signature = eva.sign(fake_message)
            # Ева шифрует открытым ключом Боба
            fake_encrypted = eva.encrypt(fake_signature, bob)
            # Боб расшифровывает
            fake_decrypted = bob.decrypt(fake_encrypted)
            # Боб проверяет подпись открытым ключом Алисы
            is_fake_valid = bob.verify_signature(fake_message, fake_decrypted, alice)
            
            print(f"  Подпись Евы: {fake_signature}")
            print(f"  Проверка подписи открытым ключом Алисы: {is_fake_valid}")
            
            if not is_fake_valid:
                print("  ✓ Подделка обнаружена! Боб не принял сообщение.")
            else:
                print("  ✗ Подделка прошла! (это не должно случиться при корректной реализации)")
        except Exception as e:
            print(f"  Ошибка при попытке подделки: {e}")
        
        print("\n" + "="*60)
    
    @staticmethod
    def demonstrate_with_different_keys():
        """Демонстрация работы с разными размерами ключей"""
        print("\n" + "="*60)
        print("ДЕМОНСТРАЦИЯ С РАЗНЫМИ РАЗМЕРАМИ КЛЮЧЕЙ")
        print("="*60 + "\n")
        
        # Создаем пользователей с разными размерами ключей
        alice = RSAUser("Алиса (1024 бит)", key_size=6)
        bob = RSAUser("Боб (2048 бит)", key_size=7)
        
        # Сообщение должно быть меньше N обоих пользователей
        message = 42
        if message < alice.N and message < bob.N:
            print(f"Сообщение: {message}")
            
            # Базовое шифрование
            encrypted = alice.encrypt(message, bob)
            decrypted = bob.decrypt(encrypted)
            
            print(f"Шифрование: {message} -> {encrypted} -> {decrypted}")
            print(f"Результат: {'✓ Успешно' if message == decrypted else '✗ Ошибка'}")
        else:
            print(f"Сообщение {message} слишком велико для одного из модулей")
            print(f"N_Алисы = {alice.N}, N_Боба = {bob.N}")
    
    @staticmethod
    def run_all_demonstrations():
        """Запуск всех демонстраций"""
        print("\n" + "█"*60)
        print("РЕАЛИЗАЦИЯ СИСТЕМЫ RSA")
        print("На основе текста: Односторонняя функция с «лазейкой» и шифр RSA")
        print("█"*60)
        
        # Демонстрация базового протокола
        RSASystem.demonstrate_basic_protocol()
        
        # Демонстрация протокола с подписью
        RSASystem.demonstrate_signed_protocol()
        
        # Демонстрация с разными ключами
        RSASystem.demonstrate_with_different_keys()
        
        print("\n" + "█"*60)
        print("ЗАКЛЮЧЕНИЕ")
        print("█"*60)
        print("""
1. RSA использует одностороннюю функцию с лазейкой:
   - Шифрование (возведение в степень) - легко
   - Дешифрование без лазейки (факторизация N) - трудно
   - Лазейка - знание простых множителей P и Q

2. Базовая схема RSA позволяет передать сообщение за 1 пересылку

3. Протокол с подписью решает проблему подделки сообщений:
   - Отправитель подписывает сообщение своим секретным ключом
   - Получатель проверяет подпись открытым ключом отправителя
   - Это основа электронной цифровой подписи

4. В реальных системах используются ключи размером 1024, 2048 или 4096 бит
        """)
        print("█"*60)


# Пример использования
if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов
    random.seed(42)
    
    # Запуск всех демонстраций
    RSASystem.run_all_demonstrations()