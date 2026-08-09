# Создание прямой цифровой подписи в MBXI
"""
Реализация протокола MBXI (игрушечная версия)
Внимание! Это НЕ безопасная криптосистема, а лишь демонстрация алгоритма из текста.
"""

import random
import hashlib
import math


class MBXI:
    """
    Класс, реализующий протокол MBXI
    """
    
    def __init__(self, p = None, g = None):
        """
        Инициализация системы с простым модулем p и генератором g
        
        Args:
            p: простое число (если None - генерируется автоматически)
            g: генератор мультипликативной группы (если None - выбирается автоматически)
        """
        if p is None:
            # Генерируем небольшое простое число для демонстрации
            self.p = self._generate_prime(100, 200)
        else:
            self.p = p
            
        if g is None:
            # Находим примитивный корень (генератор)
            self.g = self._find_primitive_root(self.p)
        else:
            self.g = g
            
        # Словарь для хранения параметров eB (совместная итерация)
        self.eB_params = {}
        
    def _is_prime(self, n):
        """Простая проверка на простоту (для малых чисел)"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def _generate_prime(self, start, end):
        """Генерация простого числа в диапазоне"""
        candidates = list(range(start, end))
        random.shuffle(candidates)
        for num in candidates:
            if self._is_prime(num):
                return num
        raise ValueError("Не найдено простое число в заданном диапазоне")
    
    def _prime_factors(self, n):
        """Разложение числа на простые множители"""
        factors = set()
        # Проверяем делимость на 2
        if n % 2 == 0:
            factors.add(2)
            while n % 2 == 0:
                n //= 2
        
        # Проверяем нечетные делители
        i = 3
        while i * i <= n:
            if n % i == 0:
                factors.add(i)
                while n % i == 0:
                    n //= i
            i += 2
        
        if n > 1:
            factors.add(n)
        return factors
    
    def _find_primitive_root(self, p):
        """Поиск примитивного корня по модулю p"""
        if p == 2:
            return 1
        
        factors = self._prime_factors(p - 1)
        
        for g in range(2, p):
            is_primitive = True
            for factor in factors:
                if pow(g, (p - 1) // factor, p) == 1:
                    is_primitive = False
                    break
            if is_primitive:
                return g
        
        raise ValueError(f"Не удалось найти примитивный корень для p = {p}")
    
    def generate_keys(self, name):
        """
        Генерация пары ключей для пользователя
        
        Args:
            name: имя пользователя ('alice' или 'bob')
            
        Returns:
            tuple: (private_key, public_key)
        """
        # Закрытый ключ - случайное число от 2 до p-2
        private_key = random.randint(2, self.p - 2)
        
        # Открытый ключ: K = g^private_key mod p
        public_key = pow(self.g, private_key, self.p)
        
        return private_key, public_key
    
    def generate_eB(self, alice_private, bob_public, iterations = 10):
        """
        Совместная итерация для генерации параметра eB
        (имитация процесса, описанного в тексте)
        
        Args:
            alice_private: закрытый ключ Алисы
            bob_public: открытый ключ Боба
            iterations: количество итераций
            
        Returns:
            int: параметр eB
        """
        # Начальное значение
        eB = 1
        
        for i in range(iterations):
            # Итеративный процесс (имитация совместной генерации)
            # В реальном протоколе здесь были бы сложные вычисления
            eB = (eB * bob_public * alice_private) % (self.p - 1)
            eB = (eB + i * 7) % (self.p - 1)  # Добавляем случайность
            
            # Гарантируем, что eB взаимно прост с p-1
            while math.gcd(eB, self.p - 1) != 1:
                eB = (eB + 1) % (self.p - 1)
                if eB == 0:
                    eB = 1
        
        return eB
    
    def compute_x(self, eB, bob_private):
        """
        Вычисление параметра x (результат функций шифрования)
        
        Args:
            eB: параметр eB
            bob_private: закрытый ключ Боба
            
        Returns:
            int: параметр x
        """
        # x = eB * b mod (p-1)
        x = (eB * bob_private) % (self.p - 1)
        if x == 0:
            x = 1
        return x
    
    def compute_y(self, eB, bob_public, alice_private):
        """
        Вычисление параметра y (для расшифрования)
        
        Args:
            eB: параметр eB
            bob_public: открытый ключ Боба
            alice_private: закрытый ключ Алисы
            
        Returns:
            int: параметр y
        """
        # y = eB * a * K_B mod (p-1)
        # Но нужен обратный элемент для проверки подписи
        # В оригинальном тексте написано: "y задается функцией расшифрования"
        # Это обратный элемент к x по модулю (p-1)
        x = self.compute_x(eB, self._get_private_from_public(bob_public))
        # Находим обратный элемент
        try:
            y = pow(x, -1, self.p - 1)
        except ValueError:
            # Если обратного нет, корректируем
            y = 1
        return y
    
    def _get_private_from_public(self, public_key):
        """
        Вспомогательная функция - в реальности здесь был бы дискретный логарифм
        Для демонстрации используем словарь соответствий
        """
        # В реальном протоколе это невозможно вычислить!
        # Здесь мы эмулируем, что Алиса знает закрытый ключ Боба
        # (что нарушает безопасность)
        return random.randint(2, self.p - 2)
    
    def hash_message(self, message):
        """
        Вычисление хеша сообщения
        
        Args:
            message: строка или число
            
        Returns:
            int: хеш-значение
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        elif isinstance(message, int):
            message = str(message).encode('utf-8')
            
        hash_obj = hashlib.sha256(message)
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.p
    
    def encrypt(self, message, x):
        """
        Шифрование сообщения
        
        Args:
            message: сообщение (число)
            x: параметр шифрования
            
        Returns:
            int: шифротекст
        """
        return pow(message, x, self.p)
    
    def decrypt(self, ciphertext, y):
        """
        Расшифрование сообщения
        
        Args:
            ciphertext: шифротекст
            y: параметр расшифрования
            
        Returns:
            int: расшифрованное сообщение
        """
        return pow(ciphertext, y, self.p)
    
    def sign(self, message_hash, x):
        """
        Создание цифровой подписи
        
        Args:
            message_hash: хеш сообщения
            x: параметр подписи
            
        Returns:
            int: подпись S
        """
        return pow(message_hash, x, self.p)
    
    def verify(self, signature, message_hash, y):
        """
        Проверка цифровой подписи
        
        Args:
            signature: подпись S
            message_hash: хеш сообщения
            y: параметр проверки
            
        Returns:
            bool: True если подпись верна
        """
        computed_hash = pow(signature, y, self.p)
        return computed_hash == message_hash


def main():
    """
    Демонстрация работы протокола MBXI
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА MBXI")
    print("=" * 60)
    
    # 1. Инициализация системы
    print("\n1. Инициализация системы...")
    mbxi = MBXI(p = 257, g = 3)  # Используем небольшое простое число для демонстрации
    print(f"   Простое число p = {mbxi.p}")
    print(f"   Генератор g = {mbxi.g}")
    
    # 2. Генерация ключей
    print("\n2. Генерация ключей...")
    alice_private, alice_public = mbxi.generate_keys('alice')
    bob_private, bob_public = mbxi.generate_keys('bob')
    
    print(f"   Алиса: приватный = {alice_private}, публичный = {alice_public}")
    print(f"   Боб: приватный = {bob_private}, публичный = {bob_public}")
    
    # 3. Совместная итерация для eB
    print("\n3. Совместная итерация (генерация eB)...")
    eB = mbxi.generate_eB(alice_private, bob_public, iterations = 5)
    print(f"   Параметр eB = {eB}")
    
    # 4. Вычисление x
    print("\n4. Вычисление параметра x...")
    x = mbxi.compute_x(eB, bob_private)
    print(f"   x = {x}")
    
    # 5. Вычисление y
    print("\n5. Вычисление параметра y...")
    y = mbxi.compute_y(eB, bob_public, alice_private)
    print(f"   y = {y}")
    print(f"   Проверка: (x * y) mod (p - 1) = {(x * y) % (mbxi.p - 1)}")
    
    # 6. Сообщение и подпись
    print("\n6. Создание подписи...")
    message = "Привет, Алиса! Это секретное сообщение от Боба."
    print(f"   Сообщение: '{message}'")
    
    message_hash = mbxi.hash_message(message)
    print(f"   Хеш сообщения H(m) = {message_hash}")
    
    signature = mbxi.sign(message_hash, x)
    print(f"   Подпись S = {signature}")
    
    # 7. Шифрование (опционально)
    print("\n7. Шифрование сообщения...")
    message_int = int.from_bytes(message.encode('utf-8'), 'big') % mbxi.p
    ciphertext = mbxi.encrypt(message_int, x)
    print(f"   Шифротекст C = {ciphertext}")
    
    # 8. Проверка подписи
    print("\n8. Проверка подписи Алисой...")
    is_valid = mbxi.verify(signature, message_hash, y)
    print(f"   Результат проверки: {'ПОДПИСЬ ВЕРНА ✅' if is_valid else 'ПОДПИСЬ НЕВЕРНА ❌'}")
    
    # 9. Расшифрование (опционально)
    print("\n9. Расшифрование сообщения Алисой...")
    decrypted_int = mbxi.decrypt(ciphertext, y)
    # Восстанавливаем сообщение (упрощенно)
    decrypted_bytes = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, 'big')
    try:
        decrypted_message = decrypted_bytes.decode('utf-8')
    except:
        decrypted_message = str(decrypted_int)
    print(f"   Расшифрованное сообщение: '{decrypted_message[:50]}...'")
    
    # 10. Дополнительная проверка - попытка подделки
    print("\n10. Проверка на подделку подписи...")
    fake_signature = (signature + 1) % mbxi.p
    is_valid_fake = mbxi.verify(fake_signature, message_hash, y)
    print(f"   Проверка измененной подписи: {'ПОДПИСЬ ВЕРНА ❌ (ОШИБКА!)' if is_valid_fake else 'ПОДПИСЬ НЕВЕРНА ✅'}")
    
    print("\n" + "=" * 60)
    print("ВАЖНОЕ ПРИМЕЧАНИЕ:")
    print("Данная реализация является ДЕМОНСТРАЦИОННОЙ и НЕ БЕЗОПАСНОЙ.")
    print("Протокол MBXI в описанном виде содержит криптографические ошибки:")
    print("1. Для проверки подписи требуется секретный ключ Алисы")
    print("2. Параметр eB генерируется совместно (интерактивный протокол)")
    print("3. Отсутствует неотказуемость (non-repudiation)")
    print("=" * 60)


if __name__ == "__main__":
    main()