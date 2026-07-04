# Стандарты на электронную (цифровую) подпись
import random
import hashlib
from typing import Tuple, Dict, Optional

class DSA:
    """
    Реализация алгоритма цифровой подписи DSA
    Поддерживает российский стандарт ГОСТ Р34.10-94 и американский FIPS 186
    """
    
    def __init__(self, standard: str = 'russian', q_bits: int = 256, p_bits: int = 1024):
        """
        Инициализация DSA
        
        Args:
            standard: 'russian' или 'american'
            q_bits: длина q в битах (256 для РФ, 160 для США)
            p_bits: длина p в битах (1024 для РФ)
        """
        self.standard = standard
        self.q_bits = q_bits
        self.p_bits = p_bits
        
        # Общие параметры (будут установлены при генерации)
        self.p = None
        self.q = None
        self.a = None
        
        # Ключи пользователя
        self.x = None  # секретный ключ
        self.y = None  # открытый ключ
        
    # ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
    
    @staticmethod
    def is_prime(n: int, k: int = 40) -> bool:
        """
        Проверка числа на простоту методом Миллера-Рабина
        
        Args:
            n: проверяемое число
            k: количество раундов теста
            
        Returns:
            True если число простое, иначе False
        """
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
            
        # Представляем n-1 как d * 2^s
        s = 0
        d = n - 1
        while d % 2 == 0:
            d //= 2
            s += 1
            
        # Проводим k раундов теста
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
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида
        
        Returns:
            (gcd, x, y): gcd = a * x + b * y
        """
        if b == 0:
            return a, 1, 0
        gcd, x1, y1 = DSA.extended_gcd(b, a % b)
        return gcd, y1, x1 - (a // b) * y1
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        Нахождение обратного числа по модулю
        
        Args:
            a: число
            m: модуль
            
        Returns:
            a ^ (-1) mod m
        """
        gcd, x, _ = DSA.extended_gcd(a, m)
        if gcd != 1:
            raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
        return x % m
    
    @staticmethod
    def hash_message(message: str, q: int) -> int:
        """
        Вычисление хеша сообщения с приведением к диапазону [1, q - 1]
        
        Args:
            message: сообщение
            q: модуль для приведения
            
        Returns:
            хеш-значение в диапазоне (0, q)
        """
        # Используем SHA-256 для хеширования
        hash_bytes = hashlib.sha256(message.encode('utf-8')).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        # Приводим к диапазону (0, q)
        return (hash_int % (q - 1)) + 1
    
    # ==================== ГЕНЕРАЦИЯ ПАРАМЕТРОВ ====================
    
    def generate_parameters(self) -> Tuple[int, int, int]:
        """
        Генерация общих параметров p, q, a
        
        Returns:
            (p, q, a) - общие параметры
        """
        print(f"Генерация параметров для {self.standard} стандарта...")
        print(f"Размер q: {self.q_bits} бит, p: {self.p_bits} бит")
        
        # 1. Генерируем простое число q заданной длины
        while True:
            # Генерируем случайное число с установленным старшим битом
            q_candidate = random.getrandbits(self.q_bits)
            # Устанавливаем старший бит в 1
            q_candidate |= (1 << (self.q_bits - 1))
            # Делаем число нечетным
            q_candidate |= 1
            
            if self.is_prime(q_candidate):
                self.q = q_candidate
                break
        
        # 2. Генерируем p = b*q + 1, где p - простое
        while True:
            # Генерируем b случайно
            b_bits = self.p_bits - self.q_bits
            b = random.getrandbits(b_bits)
            # Убеждаемся, что b > 0 и p будет иметь нужную длину
            b |= (1 << (b_bits - 1))
            
            p_candidate = b * self.q + 1
            
            # Проверяем, что p имеет нужную длину и простое
            if p_candidate.bit_length() == self.p_bits and self.is_prime(p_candidate):
                self.p = p_candidate
                break
        
        # 3. Находим a: элемент порядка q в группе по модулю p
        while True:
            # Берем случайное g
            g = random.randrange(2, self.p - 1)
            # Вычисляем a = g^((p-1)/q) mod p
            a_candidate = pow(g, (self.p - 1) // self.q, self.p)
            
            # Проверяем, что a > 1 (условие a^q mod p = 1 будет выполнено автоматически)
            if a_candidate > 1:
                self.a = a_candidate
                break
        
        print(f"Параметры сгенерированы:")
        print(f"p = {self.p}")
        print(f"q = {self.q}")
        print(f"a = {self.a}")
        
        return self.p, self.q, self.a
    
    def generate_keys(self) -> Tuple[int, int]:
        """
        Генерация ключей пользователя
        
        Returns:
            (x, y) - секретный и открытый ключи
        """
        if self.p is None or self.q is None or self.a is None:
            raise ValueError("Сначала необходимо сгенерировать общие параметры")
        
        # 1. Выбираем x случайно из (0, q)
        self.x = random.randrange(1, self.q)
        
        # 2. Вычисляем y = a^x mod p
        self.y = pow(self.a, self.x, self.p)
        
        print(f"Ключи сгенерированы:")
        print(f"Секретный ключ x = {self.x}")
        print(f"Открытый ключ y = {self.y}")
        
        return self.x, self.y
    
    # ==================== ПОДПИСЬ ====================
    
    def sign(self, message: str) -> Tuple[int, int, int]:
        """
        Подписание сообщения
        
        Args:
            message: сообщение для подписи
            
        Returns:
            (h, r, s) - хеш сообщения, r и s компоненты подписи
        """
        if self.x is None:
            raise ValueError("Сначала необходимо сгенерировать ключи")
        
        # 1. Вычисляем хеш сообщения
        h = self.hash_message(message, self.q)
        print(f"Хеш сообщения: h = {h}")
        
        # 2. Генерируем случайное k и вычисляем подпись
        max_attempts = 1000
        for attempt in range(max_attempts):
            # Выбираем случайное k из (0, q)
            k = random.randrange(1, self.q)
            
            # 3. Вычисляем r = (a^k mod p) mod q
            r = pow(self.a, k, self.p) % self.q
            
            if r == 0:
                continue  # r не должен быть равен 0
            
            # 4. Вычисляем s в зависимости от стандарта
            if self.standard == 'russian':
                # Российский стандарт: s = (k*h + x*r) mod q
                s = (k * h + self.x * r) % self.q
            else:  # american
                # Американский стандарт: s = k^(-1) * (h + x*r) mod q
                k_inv = self.mod_inverse(k, self.q)
                s = (k_inv * (h + self.x * r)) % self.q
            
            if s != 0:
                print(f"Подпись создана (попытка {attempt + 1})")
                print(f"r = {r}, s = {s}")
                return h, r, s
        
        raise RuntimeError(f"Не удалось создать подпись после {max_attempts} попыток")
    
    # ==================== ПРОВЕРКА ====================
    
    def verify(self, message: str, h: int, r: int, s: int) -> bool:
        """
        Проверка подписи
        
        Args:
            message: сообщение
            h: хеш сообщения (из подписи)
            r: компонент r подписи
            s: компонент s подписи
            
        Returns:
            True если подпись верна, иначе False
        """
        if self.y is None:
            raise ValueError("Открытый ключ не установлен")
        
        print("\n--- Проверка подписи ---")
        
        # 1. Проверяем, что хеш сообщения совпадает
        h_new = self.hash_message(message, self.q)
        print(f"Вычисленный хеш: {h_new}, хеш из подписи: {h}")
        
        if h != h_new:
            print("ОШИБКА: Хеш сообщения не совпадает!")
            return False
        
        # 2. Проверяем диапазоны r и s
        if not (0 < r < self.q):
            print(f"ОШИБКА: r вне диапазона (0 < {r} < {self.q})")
            return False
        
        if not (0 < s < self.q):
            print(f"ОШИБКА: s вне диапазона (0 < {s} < {self.q})")
            return False
        
        print("Проверка диапазонов пройдена")
        
        # 3. Вычисляем u1 и u2 в зависимости от стандарта
        if self.standard == 'russian':
            # Российский стандарт
            h_inv = self.mod_inverse(h, self.q)
            u1 = (s * h_inv) % self.q
            u2 = (-r * h_inv) % self.q
            print(f"Российский стандарт: u1 = {u1}, u2 = {u2}")
        else:
            # Американский стандарт
            s_inv = self.mod_inverse(s, self.q)
            u1 = (h * s_inv) % self.q
            u2 = (r * s_inv) % self.q
            print(f"Американский стандарт: u1 = {u1}, u2 = {u2}")
        
        # 4. Вычисляем v = (a^u1 * y^u2 mod p) mod q
        part1 = pow(self.a, u1, self.p)
        part2 = pow(self.y, u2, self.p)
        v = (part1 * part2) % self.p
        v = v % self.q
        
        print(f"v = {v}")
        print(f"r = {r}")
        
        # 5. Проверяем v == r
        if v == r:
            print("✓ ПОДПИСЬ ВЕРНА!")
            return True
        else:
            print("✗ ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА!")
            return False


# ==================== ДЕМОНСТРАЦИОННЫЙ ПРИМЕР ====================

def demo_russian_standard():
    """Демонстрация российского стандарта"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ РОССИЙСКОГО СТАНДАРТА ГОСТ Р34.10-94")
    print("=" * 60)
    
    # Создаем экземпляр DSA для российского стандарта
    dsa = DSA(standard = 'russian', q_bits = 256, p_bits = 1024)
    
    # Генерируем общие параметры
    p, q, a = dsa.generate_parameters()
    
    # Генерируем ключи пользователя
    x, y = dsa.generate_keys()
    
    # Сообщение для подписи
    message = "Пример сообщения для подписи"
    print(f"\nСообщение: {message}")
    
    # Подписываем
    h, r, s = dsa.sign(message)
    print(f"Подпись: (r = {r}, s = {s})")
    
    # Проверяем оригинальное сообщение
    print("\n--- Проверка оригинального сообщения ---")
    dsa.verify(message, h, r, s)
    
    # Проверяем измененное сообщение
    print("\n--- Проверка измененного сообщения ---")
    modified_message = "Пример сообщения для подписи (изменено)"
    dsa.verify(modified_message, h, r, s)


def demo_american_standard():
    """Демонстрация американского стандарта"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АМЕРИКАНСКОГО СТАНДАРТА FIPS 186 (DSA)")
    print("=" * 60)
    
    # Создаем экземпляр DSA для американского стандарта
    dsa = DSA(standard = 'american', q_bits = 160, p_bits = 1024)
    
    # Генерируем общие параметры
    p, q, a = dsa.generate_parameters()
    
    # Генерируем ключи пользователя
    x, y = dsa.generate_keys()
    
    # Сообщение для подписи
    message = "Hello, World!"
    print(f"\nСообщение: {message}")
    
    # Подписываем
    h, r, s = dsa.sign(message)
    print(f"Подпись: (r = {r}, s = {s})")
    
    # Проверяем
    print("\n--- Проверка подписи ---")
    dsa.verify(message, h, r, s)


def demo_with_fixed_parameters():
    """
    Демонстрация с фиксированными параметрами из примера в тексте
    (Пример 4.3 из документа)
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НА ПРИМЕРЕ ИЗ ТЕКСТА (Пример 4.3)")
    print("=" * 60)
    
    # Создаем экземпляр DSA
    dsa = DSA(standard = 'russian')
    
    # Устанавливаем параметры из примера
    dsa.q = 11
    dsa.p = 67
    dsa.a = 25
    
    # Устанавливаем ключи
    dsa.x = 6
    dsa.y = 62
    
    print(f"Параметры: p = {dsa.p}, q = {dsa.q}, a = {dsa.a}")
    print(f"Ключи: x = {dsa.x}, y = {dsa.y}")
    
    # Сообщение из примера
    message = "baaaab"
    h = 3  # хеш из примера
    
    print(f"\nСообщение: {message}, хеш: {h}")
    
    # Симулируем подпись из примера
    r = 2
    s = 3
    print(f"Подпись из примера: (r = {r}, s = {s})")
    
    # Проверяем
    print("\n--- Проверка подписи ---")
    dsa.verify(message, h, r, s)


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов
    random.seed(42)
    
    # Демонстрация работы
    demo_russian_standard()
    
    print("\n" + "=" * 60)
    print("ПРИМЕЧАНИЕ: Американский стандарт требует больше времени")
    print("для генерации параметров из-за меньшего размера q (160 бит)")
    print("=" * 60)
    
    # Раскомментируйте для демонстрации американского стандарта
    # demo_american_standard()
    
    # Демонстрация с фиксированными параметрами из примера
    demo_with_fixed_parameters()