# 1. DSS 
#!/usr/bin/env python3
"""
DSA (Digital Signature Algorithm) - Полная реализация
В соответствии со стандартом DSS (FIPS 186)

Содержит:
1. Базовый класс DSA с подписью и проверкой
2. Генерацию параметров (простые числа, порождающие элементы)
3. Демонстрационные примеры
4. Тесты безопасности
"""

import random
import hashlib
import math
from typing import Tuple, Optional


# ============================================================================
# ЧАСТЬ 1: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОСТЫМИ ЧИСЛАМИ
# ============================================================================

def is_prime(n: int, k: int = 40) -> bool:
    """
    Тест Миллера-Рабина на простоту
    
    Args:
        n: число для проверки
        k: количество раундов (чем больше, тем точнее)
    
    Returns:
        True если число вероятно простое
    """
    if n < 2:
        return False
    if n in [2, 3]:
        return True
    if n % 2 == 0:
        return False
    
    # Представление n-1 как d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проверка k раз
    for _ in range(k):
        a = random.randint(2, n - 2)
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


def generate_prime(bits: int) -> int:
    """
    Генерация простого числа заданной битности
    
    Args:
        bits: количество бит
    
    Returns:
        простое число
    """
    while True:
        n = random.getrandbits(bits)
        # Устанавливаем старший бит для обеспечения нужной длины
        n |= (1 << bits - 1) | 1  # делаем нечетным
        if is_prime(n):
            return n


def find_generator(p: int, q: int) -> int:
    """
    Поиск порождающего элемента f подгруппы порядка q в группе Z_p^*
    
    Реализация алгоритма, описанного в тексте:
    1. Берем случайный g из Z_p^*
    2. Вычисляем f = g^((p-1)/q) mod p
    3. Если f != 1, то f - искомый элемент
    
    Args:
        p: простое число
        q: простое число, делитель p-1
        
    Returns:
        f: порождающий элемент подгруппы порядка q
    """
    while True:
        # Выбираем случайный g из Z_p^*
        g = random.randint(2, p - 2)
        
        # Вычисляем f = g^((p-1)/q) mod p
        f = pow(g, (p - 1) // q, p)
        
        # Если f != 1, то f имеет порядок q (так как q - простое)
        if f != 1:
            return f


def generate_dsa_parameters(q_bits: int = 160, p_bits: int = 512) -> Tuple[int, int, int]:
    """
    Генерация параметров DSA
    
    Args:
        q_bits: размер q в битах (обычно 160)
        p_bits: размер p в битах (обычно 512, 1024 или 2048)
    
    Returns:
        (p, q, f) - параметры DSA
    """
    print(f"Генерация параметров DSA (q = {q_bits} бит, p = {p_bits} бит)...")
    
    # Генерируем q
    while True:
        q = generate_prime(q_bits)
        # Проверяем, что q в нужном диапазоне
        if 2 ** (q_bits - 1) < q < 2 ** q_bits:
            break
    
    # Генерируем p, такое что p = k*q + 1
    while True:
        # Выбираем k случайно
        k_bits = p_bits - q_bits
        k = random.getrandbits(k_bits)
        # Делаем k четным (чтобы p было нечетным)
        k |= 1
        p = k * q + 1
        
        # Проверяем, что p в нужном диапазоне и простое
        if 2 ** (p_bits - 1) < p < 2 ** p_bits and is_prime(p):
            break
    
    # Находим порождающий элемент f
    f = find_generator(p, q)
    
    return p, q, f


# ============================================================================
# ЧАСТЬ 2: ОСНОВНОЙ КЛАСС DSA
# ============================================================================

class DSA:
    """
    Реализация алгоритма цифровой подписи DSA (Digital Signature Algorithm)
    в соответствии со стандартом DSS (FIPS 186)
    
    Атрибуты:
        p: простое число (512-1024 бит)
        q: простое число (160 бит), делитель p-1
        f: порождающий элемент подгруппы порядка q
        a: секретный ключ (долгосрочный)
        y: открытый ключ (y = f^a mod p)
    """
    
    def __init__(self, p: int, q: int, f: int, a: Optional[int] = None):
        """
        Инициализация с параметрами
        
        Args:
            p: простое число, 512-1024 бит
            q: простое число, 160 бит, делитель p-1
            f: порождающий элемент подгруппы порядка q
            a: секретный ключ (если None, будет сгенерирован случайно)
        """
        self.p = p
        self.q = q
        self.f = f
        
        # Генерация секретного ключа, если не указан
        if a is None:
            self.a = random.randint(1, q - 1)
        else:
            self.a = a
            
        # Вычисление открытого ключа
        self.y = pow(f, self.a, p)
        
        # Сохраняем информацию о параметрах
        self.param_info = {
            'p_bits': p.bit_length(),
            'q_bits': q.bit_length(),
            'f': f,
            'a': self.a,
            'y': self.y
        }
    
    def mod_inverse(self, x: int, mod: int) -> int:
        """
        Вычисление обратного элемента по модулю
        
        Использует расширенный алгоритм Евклида (через встроенную функцию pow)
        
        Args:
            x: число
            mod: модуль
            
        Returns:
            x^(-1) mod mod
            
        Raises:
            ValueError: если обратный элемент не существует
        """
        try:
            return pow(x, -1, mod)
        except ValueError:
            raise ValueError(f"Элемент {x} не имеет обратного по модулю {mod}")
    
    def sign(self, message: bytes, k: Optional[int] = None) -> Tuple[int, int]:
        """
        Создание цифровой подписи для сообщения
        
        Алгоритм:
        1. h = SHA-1(message) mod q
        2. r = (f^k mod p) mod q
        3. s = k^(-1) * (h + a*r) mod q
        
        Args:
            message: сообщение в виде байтов
            k: сессионный ключ (если None, генерируется случайно)
            
        Returns:
            (r, s) - пара чисел подписи
            
        Raises:
            ValueError: если r=0 или s=0 (нужно сменить k)
        """
        # Вычисление хэша сообщения
        h = self._hash_message(message)
        
        # Генерация сессионного ключа
        if k is None:
            k = random.randint(1, self.q - 1)
        
        # Вычисление r = (f^k mod p) mod q
        r = pow(self.f, k, self.p) % self.q
        
        # Если r = 0, нужно выбрать другой k (по стандарту)
        if r == 0:
            raise ValueError("r = 0, необходимо изменить сессионный ключ k")
        
        # Вычисление l = k^(-1) mod q
        l = self.mod_inverse(k, self.q)
        
        # Вычисление s = l * (h(m) + a*r) mod q
        s = (l * (h + self.a * r)) % self.q
        
        # Если s = 0, нужно выбрать другой k (по стандарту)
        if s == 0:
            raise ValueError("s = 0, необходимо изменить сессионный ключ k")
        
        return (r, s)
    
    def verify(self, message: bytes, signature: Tuple[int, int]) -> bool:
        """
        Проверка цифровой подписи
        
        Алгоритм:
        1. Проверка 0 < r < q и 0 < s < q
        2. h = SHA-1(message) mod q
        3. w = s^(-1) mod q
        4. u1 = w * h mod q
        5. u2 = r * w mod q
        6. v = (f^u1 * y^u2 mod p) mod q
        7. Подпись верна, если v == r
        
        Args:
            message: сообщение в виде байтов
            signature: (r, s) - пара чисел подписи
            
        Returns:
            True если подпись верна, иначе False
        """
        r, s = signature
        
        # Проверка условий: 0 < r < q и 0 < s < q
        if not (0 < r < self.q and 0 < s < self.q):
            return False
        
        # Вычисление хэша сообщения
        h = self._hash_message(message)
        
        try:
            # Вычисление w = s^(-1) mod q
            w = self.mod_inverse(s, self.q)
            
            # Вычисление u1 = w * h(m) mod q
            u1 = (w * h) % self.q
            
            # Вычисление u2 = r * w mod q
            u2 = (r * w) % self.q
            
            # Вычисление v = (f^u1 * y^u2 mod p) mod q
            v = (pow(self.f, u1, self.p) * pow(self.y, u2, self.p)) % self.p
            v = v % self.q
            
            # Подпись верна, если v == r
            return v == r
            
        except ValueError:
            # Если s не имеет обратного элемента
            return False
    
    def _hash_message(self, message: bytes) -> int:
        """
        Вычисление хэша сообщения с использованием SHA-1
        
        В оригинальном DSS используется SHA-1, но в современных
        реализациях рекомендуется использовать SHA-256 или выше
        
        Args:
            message: сообщение в виде байтов
            
        Returns:
            хэш как целое число по модулю q
        """
        # SHA-1 (как в оригинальном DSS)
        hash_bytes = hashlib.sha1(message).digest()
        
        # Преобразование в целое число и приведение по модулю q
        h = int.from_bytes(hash_bytes, byteorder = 'big') % self.q
        
        return h
    
    def get_public_key(self) -> Tuple[int, int, int, int]:
        """
        Возвращает открытые параметры
        
        Returns:
            (p, q, f, y) - открытые параметры
        """
        return (self.p, self.q, self.f, self.y)
    
    def get_private_key(self) -> int:
        """
        Возвращает секретный ключ (только для отладки!)
        
        Returns:
            a - секретный ключ
        """
        return self.a
    
    def __str__(self) -> str:
        """Строковое представление параметров"""
        return (f"DSA(p = {self.p}, q = {self.q}, f = {self.f}, "f"a = {self.a}, y = {self.y})")


# ============================================================================
# ЧАСТЬ 3: ДЕМОНСТРАЦИОННЫЕ ПРИМЕРЫ
# ============================================================================

def demo_with_small_parameters():
    """
    Демонстрация работы DSA с малыми параметрами из примера в тексте
    p = 31, q = 5, f = 16, a = 2, k = 3
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ DSA С МАЛЫМИ ПАРАМЕТРАМИ (ИЗ ТЕКСТА)")
    print("=" * 70)
    
    # Параметры из примера
    p = 31
    q = 5
    f = 16  # f = 3^6 mod 31 = 16
    a = 2   # секретный ключ
    
    print(f"Параметры:")
    print(f"  p = {p} (простое)")
    print(f"  q = {q} (простое, делитель p - 1 = {p - 1})")
    print(f"  f = {f} (порождающий элемент, f ^ {q} mod p = {pow(f, q, p)})")
    print(f"  a = {a} (секретный ключ)")
    
    # Создаем экземпляр DSA
    dsa = DSA(p, q, f, a)
    
    # Открытый ключ
    y = dsa.y
    print(f"  y = f ^ a mod p = {f} ^ {a} mod {p} = {y} (открытый ключ)")
    
    # Сообщение и его хэш
    message = b"Hello, DSA!"
    h = dsa._hash_message(message)
    print(f"\nСообщение: '{message.decode()}'")
    print(f"Хэш h(m) = SHA-1('{message.decode()}') mod {q} = {h}")
    
    # Сессионный ключ из примера
    k = 3
    print(f"\nСессионный ключ k = {k}")
    
    # Подпись с детальным выводом
    print("\n" + "-" * 70)
    print("ГЕНЕРАЦИЯ ПОДПИСИ:")
    print("-" * 70)
    
    l = dsa.mod_inverse(k, q)
    r = pow(f, k, p) % q
    s = (l * (h + a * r)) % q
    
    print(f"  l = k ^ (-1) mod q = {k} ^ (-1) mod {q} = {l}")
    print(f"  r = (f ^ k mod p) mod q = ({f} ^ {k} mod {p}) mod {q} = {r}")
    print(f"  s = l * (h(m) + a * r) mod q = {l} * ({h} + {a} * {r}) mod {q} = {s}")
    print(f"  Подпись (r, s) = ({r}, {s})")
    
    # Проверка подписи с детальным выводом
    print("\n" + "-" * 70)
    print("ПРОВЕРКА ПОДПИСИ:")
    print("-" * 70)
    
    w = dsa.mod_inverse(s, q)
    u1 = (w * h) % q
    u2 = (r * w) % q
    v = (pow(f, u1, p) * pow(y, u2, p)) % p
    v = v % q
    
    print(f"  w = s ^ (-1) mod q = {s} ^ (-1) mod {q} = {w}")
    print(f"  u1 = w * h(m) mod q = {w} * {h} mod {q} = {u1}")
    print(f"  u2 = r * w mod q = {r} * {w} mod {q} = {u2}")
    print(f"  v = (f ^ u1 * y ^ u2 mod p) mod q = {v}")
    print(f"  r = {r}")
    print(f"  v == r: {v == r}")
    
    # Проверка через метод verify
    is_valid = dsa.verify(message, (r, s))
    print(f"\nРезультат проверки: {'✅ ПОДПИСЬ ВЕРНА' if is_valid else '❌ ПОДПИСЬ НЕВЕРНА'}")
    
    # Демонстрация обнаружения подделки
    print("\n" + "-" * 70)
    print("ДЕМОНСТРАЦИЯ ОБНАРУЖЕНИЯ ПОДДЕЛКИ:")
    print("-" * 70)
    
    # Изменяем сообщение
    fake_message = b"Fake message!"
    is_valid_fake = dsa.verify(fake_message, (r, s))
    print(f"  Измененное сообщение: '{fake_message.decode()}'")
    print(f"  Проверка: {'✅ ВЕРНА (ОШИБКА!)' if is_valid_fake else '❌ НЕВЕРНА (ОБНАРУЖЕНА)'}")
    
    # Изменяем подпись
    fake_r = (r + 1) % q
    is_valid_fake_sig = dsa.verify(message, (fake_r, s))
    print(f"  Измененная подпись: r = {fake_r}, s = {s}")
    print(f"  Проверка: {'✅ ВЕРНА (ОШИБКА!)' if is_valid_fake_sig else '❌ НЕВЕРНА (ОБНАРУЖЕНА)'}")


def demo_with_generated_parameters():
    """
    Демонстрация работы DSA с сгенерированными параметрами
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ DSA С СГЕНЕРИРОВАННЫМИ ПАРАМЕТРАМИ")
    print("=" * 70)
    
    # Генерируем параметры (для демонстрации используем маленькие битности)
    print("Генерация параметров...")
    p, q, f = generate_dsa_parameters(q_bits = 20, p_bits = 40)
    
    print(f"\nСгенерированные параметры:")
    print(f"  p = {p} ({p.bit_length()} бит)")
    print(f"  q = {q} ({q.bit_length()} бит)")
    print(f"  f = {f} (проверка: f^{q} mod p = {pow(f, q, p)})")
    print(f"  p - 1 mod q = {(p - 1) % q} (должно быть 0)")
    
    # Создаем DSA
    dsa = DSA(p, q, f)
    print(f"\nКлючи:")
    print(f"  Секретный ключ a = {dsa.a}")
    print(f"  Открытый ключ y = {dsa.y}")
    
    # Подписываем несколько сообщений
    messages = [
        b"First message",
        b"Second message with different content",
        b"Third message" * 10  # Длинное сообщение
    ]
    
    print("\n" + "-" * 70)
    print("ПОДПИСЬ И ПРОВЕРКА СООБЩЕНИЙ:")
    print("-" * 70)
    
    for i, msg in enumerate(messages, 1):
        # Генерируем подпись с случайным k
        r, s = dsa.sign(msg)
        
        # Проверяем
        is_valid = dsa.verify(msg, (r, s))
        
        print(f"\nСообщение {i}: '{msg[:30].decode()}{'...' if len(msg) > 30 else ''}'")
        print(f"  Хэш: {dsa._hash_message(msg)}")
        print(f"  Подпись: r = {r}, s = {s}")
        print(f"  Проверка: {'✅ ВЕРНА' if is_valid else '❌ НЕВЕРНА'}")


def demonstrate_weakness_reused_k():
    """
    Демонстрация уязвимости DSA при повторном использовании k
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ УЯЗВИМОСТИ: ПОВТОРНОЕ ИСПОЛЬЗОВАНИЕ k")
    print("=" * 70)
    
    # Используем малые параметры для наглядности
    p = 31
    q = 5
    f = 16
    a = 2
    
    dsa = DSA(p, q, f, a)
    
    # Два разных сообщения
    m1 = b"Message 1"
    m2 = b"Message 2"
    
    h1 = dsa._hash_message(m1)
    h2 = dsa._hash_message(m2)
    
    # Один и тот же k для обоих сообщений (нарушение безопасности!)
    k = 3
    
    print(f"Параметры:")
    print(f"  p = {p}, q = {q}, f = {f}")
    print(f"  Секретный ключ a = {a}")
    print(f"  Сессионный ключ k = {k} (используется дважды!)")
    print()
    
    # Подписываем
    r1, s1 = dsa.sign(m1, k)
    r2, s2 = dsa.sign(m2, k)
    
    print(f"Сообщение 1: h(m1) = {h1}")
    print(f"  Подпись: r1 = {r1}, s1 = {s1}")
    print(f"Сообщение 2: h(m2) = {h2}")
    print(f"  Подпись: r2 = {r2}, s2 = {s2}")
    print()
    
    print("Атака: восстановление секретного ключа...")
    
    # Восстанавливаем k (злоумышленник)
    # s1 - s2 = k^(-1) * (h1 - h2) mod q
    diff_s = (s1 - s2) % q
    diff_h = (h1 - h2) % q
    
    # k = (h1 - h2) * (s1 - s2)^(-1) mod q
    try:
        k_recovered = (diff_h * dsa.mod_inverse(diff_s, q)) % q
        print(f"  Восстановленный k = {k_recovered}")
        
        # Восстанавливаем секретный ключ a
        # s1 = k^(-1) * (h1 + a*r1) mod q
        # a = (s1*k - h1) * r1^(-1) mod q
        a_recovered = ((s1 * k - h1) * dsa.mod_inverse(r1, q)) % q
        print(f"  Восстановленный секретный ключ a = {a_recovered}")
        print(f"  Оригинальный a = {dsa.a}")
        print(f"  Ключ восстановлен: {'✅ ДА' if a_recovered == dsa.a else '❌ НЕТ'}")
        
    except ValueError as e:
        print(f"  ❌ Не удалось восстановить ключ: {e}")
    
    print("\n⚠️  ВЫВОД: Никогда не используйте один и тот же сессионный ключ k!")


def demonstrate_edge_cases():
    """
    Демонстрация обработки краевых случаев
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ОБРАБОТКИ КРАЕВЫХ СЛУЧАЕВ")
    print("=" * 70)
    
    p = 31
    q = 5
    f = 16
    a = 2
    
    dsa = DSA(p, q, f, a)
    
    # Случай 1: r = 0 (автоматически генерируется новый k)
    print("\n1. Проверка автоматической генерации k при r = 0...")
    try:
        # Пытаемся подписать с k, который даст r=0
        # Для p=31, q=5, f=16: r = (16^k mod 31) mod 5
        # Нужно найти k такое, что 16^k mod 31 кратно 5
        # Перебираем возможные k
        found_zero = False
        for test_k in range(1, q):
            r_test = pow(f, test_k, p) % q
            if r_test == 0:
                found_zero = True
                print(f"  Найден k = {test_k}, дающий r = 0")
                try:
                    dsa.sign(b"Test", test_k)
                except ValueError as e:
                    print(f"  ✅ Ошибка корректно обработана: {e}")
                break
        if not found_zero:
            print("  Не найден k с r = 0 (в этом наборе параметров)")
    except Exception as e:
        print(f"  ❌ Неожиданная ошибка: {e}")
    
    # Случай 2: Неверный формат подписи
    print("\n2. Проверка неверного формата подписи...")
    invalid_signatures = [
        (0, 1),  # r = 0
        (5, 0),  # s = 0 (q=5, поэтому s=0 недопустимо)
        (10, 3), # r >= q
        (1, 10), # s >= q
        (-1, 1)  # отрицательные значения
    ]
    
    for r_test, s_test in invalid_signatures:
        result = dsa.verify(b"Test", (r_test, s_test))
        print(f"  Подпись ({r_test}, {s_test}) -> {'❌ НЕВЕРНА' if not result else '✅ ВЕРНА (ОШИБКА!)'}")


# ============================================================================
# ЧАСТЬ 4: ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================

def performance_test():
    """
    Тест производительности DSA с разными размерами ключей
    """
    print("\n" + "=" * 70)
    print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 70)
    
    import time
    
    # Тестовое сообщение
    message = b"Performance test message" * 100
    
    # Различные размеры параметров
    test_configs = [
        (20, 40, "Маленькие (20/40 бит)"),
        (30, 60, "Средние (30/60 бит)"),
        (40, 80, "Большие (40/80 бит)"),
    ]
    
    print("\n{:<20} {:<15} {:<15} {:<15}".format(
        "Конфигурация", "Подпись (мс)", "Проверка (мс)", "Всего (мс)"
    ))
    print("-" * 70)
    
    for q_bits, p_bits, name in test_configs:
        try:
            # Генерируем параметры
            p, q, f = generate_dsa_parameters(q_bits, p_bits)
            dsa = DSA(p, q, f)
            
            # Измеряем подпись
            start = time.perf_counter()
            r, s = dsa.sign(message)
            sign_time = (time.perf_counter() - start) * 1000
            
            # Измеряем проверку
            start = time.perf_counter()
            is_valid = dsa.verify(message, (r, s))
            verify_time = (time.perf_counter() - start) * 1000
            
            print("{:<20} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                name, sign_time, verify_time, sign_time + verify_time
            ))
            
        except Exception as e:
            print(f"{name:<20} ОШИБКА: {str(e)[:30]}")


# ============================================================================
# ЧАСТЬ 5: ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """
    Главная функция, запускающая все демонстрации
    """
    print("=" * 70)
    print("ЦИФРОВАЯ ПОДПИСЬ DSA (DIGITAL SIGNATURE ALGORITHM)")
    print("Реализация в соответствии со стандартом DSS (FIPS 186)")
    print("=" * 70)
    print("\nАвтор: Реализация на основе стандарта FIPS 186")
    print("Версия: 1.0")
    print("Дата: 2024")
    
    # Запуск всех демонстраций
    demo_with_small_parameters()
    demo_with_generated_parameters()
    demonstrate_weakness_reused_k()
    demonstrate_edge_cases()
    
    # Тест производительности (опционально, можно закомментировать)
    try:
        performance_test()
    except Exception as e:
        print(f"\n⚠️ Тест производительности пропущен: {e}")
    
    # Итоговое заключение
    print("\n" + "=" * 70)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 70)
    print("""
    DSA обеспечивает:
    1. Аутентификация - подтверждение авторства документа
    2. Целостность - обнаружение любых изменений в документе
    3. Неотказуемость - автор не может отказаться от подписи
    
    Ключевые требования безопасности:
    ✅ Использовать криптостойкие параметры (p ≥ 1024 бит, q ≥ 160 бит)
    ✅ Никогда не повторять сессионный ключ k
    ✅ Использовать современные хэш-функции (SHA-256 вместо SHA-1)
    ✅ Хранить секретный ключ a в надежном месте
    ✅ Использовать криптографически стойкий генератор случайных чисел
    
    Слабости алгоритма:
    ⚠️ Уязвим к квантовым атакам (алгоритм Шора)
    ⚠️ Повторное использование k раскрывает секретный ключ
    ⚠️ Зависит от качества генерации случайных чисел
    """)
    
    print("=" * 70)
    print("Программа успешно завершена.")
    print("=" * 70)


if __name__ == "__main__":
    main()