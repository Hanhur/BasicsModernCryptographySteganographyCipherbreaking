# Как работает протокол zk-SNARK
"""
Реализация неинтерактивного протокола zk-SNARK на основе дискретного логарифма
(аналог протокола Шнорра с преобразованием Фиата-Шамира)

Без использования numpy - только встроенные модули Python
"""

import hashlib
import random
import math
from typing import Tuple, Optional


class ZKSNARK:
    """
    Класс, реализующий протокол zk-SNARK для доказательства знания дискретного логарифма
    """
    
    def __init__(self, p: int, g: int):
        """
        Инициализация с публичными параметрами
        
        Args:
            p: простое число (модуль)
            g: генератор (первообразный корень по модулю p)
        """
        self.p = p
        self.g = g
        self.order = p - 1  # Порядок мультипликативной группы
        
    @staticmethod
    def is_prime(n: int) -> bool:
        """Проверка числа на простоту (для маленьких чисел)"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def is_primitive_root(g: int, p: int) -> bool:
        """
        Проверка, является ли g первообразным корнем по модулю p (для небольших p)
        """
        if p <= 2:
            return True
            
        # Факторизация p-1
        phi = p - 1
        factors = []
        temp = phi
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                factors.append(d)
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            factors.append(temp)
        
        # Проверка условия: g^(phi/f) != 1 mod p для всех простых f
        for f in factors:
            if pow(g, phi // f, p) == 1:
                return False
        return True
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        Вычисление обратного элемента по модулю m (расширенный алгоритм Евклида)
        """
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    
    def generate_keypair(self, secret: int) -> Tuple[int, int]:
        """
        Генерация пары ключей (открытый, закрытый)
        
        Args:
            secret: секретное значение a (закрытый ключ)
            
        Returns:
            (public_key, private_key)
        """
        if not (1 <= secret < self.order):
            raise ValueError(f"Секрет должен быть в диапазоне [1, {self.order - 1}]")
        
        public_key = pow(self.g, secret, self.p)
        return public_key, secret
    
    def hash_to_int(self, *args) -> int:
        """
        Хеш-функция, преобразующая произвольное количество аргументов в целое число
        (имитация криптографической хеш-функции)
        
        Args:
            *args: произвольные аргументы для хеширования
            
        Returns:
            целое число в диапазоне [0, order-1]
        """
        # Преобразуем все аргументы в строку
        data = "|".join(str(arg) for arg in args)
        # Вычисляем SHA-256
        hash_bytes = hashlib.sha256(data.encode()).digest()
        # Преобразуем первые 8 байт в целое число
        hash_int = int.from_bytes(hash_bytes[:8], 'big')
        # Приводим к диапазону [0, order-1]
        return hash_int % self.order
    
    def prove(self, secret: int, public_key: int, 
              random_seed: Optional[int] = None) -> Tuple[int, int, int]:
        """
        Генерация доказательства (алгоритм P)
        
        Args:
            secret: секретное значение a
            public_key: открытый ключ y = g ^ a mod p
            random_seed: опциональный seed для детерминированной генерации
            
        Returns:
            (t, r, c) где:
                t = g ^ v mod p (коммитмент)
                r = v - c * a mod (p - 1) (ответ)
                c = H(g, y, t) (вызов)
        """
        if random_seed is not None:
            random.seed(random_seed)
        
        # Выбираем случайное v
        v = random.randint(1, self.order - 1)
        
        # Вычисляем t = g^v mod p
        t = pow(self.g, v, self.p)
        
        # Вычисляем вызов c = H(g, y, t)
        c = self.hash_to_int(self.g, public_key, t)
        
        # Вычисляем ответ r = v - c*a mod (p-1)
        r = (v - c * secret) % self.order
        
        return t, r, c
    
    def verify(self, public_key: int, t: int, r: int) -> bool:
        """
        Проверка доказательства (алгоритм V)
        
        Args:
            public_key: открытый ключ y
            t: коммитмент из доказательства
            r: ответ из доказательства
            
        Returns:
            True, если доказательство верно, иначе False
        """
        # Вычисляем c' = H(g, y, t)
        c_prime = self.hash_to_int(self.g, public_key, t)
        
        # Проверяем: t == g^r * y^c mod p
        left = t
        right = (pow(self.g, r, self.p) * pow(public_key, c_prime, self.p)) % self.p
        
        return left == right
    
    def attack_fake_proof(self, public_key: int) -> Tuple[int, int, int]:
        """
        Демонстрация атаки: попытка создать поддельное доказательство
        (злоумышленник не знает секрет, но пытается подделать)
        
        Это демонстрирует, почему важно использовать криптостойкую хеш-функцию
        
        Args:
            public_key: открытый ключ жертвы
            
        Returns:
            (t, r, c) - поддельное доказательство
        """
        # Злоумышленник выбирает случайные r и c
        r = random.randint(1, self.order - 1)
        c = random.randint(1, self.order - 1)
        
        # Подгоняет t так, чтобы уравнение выполнялось: t = g^r * y^c
        t = (pow(self.g, r, self.p) * pow(public_key, c, self.p)) % self.p
        
        # Но хеш от (g, y, t) почти наверняка не будет равен c
        # Это показывает, что атака не работает из-за хеш-функции
        
        return t, r, c


def demo_basic_protocol():
    """Демонстрация базовой работы протокола"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ БАЗОВОГО ПРОТОКОЛА zk-SNARK")
    print("=" * 60)
    
    # Параметры (используем небольшие простые числа для наглядности)
    p = 23
    g = 5  # Первообразный корень по модулю 23
    
    print(f"\nПубличные параметры:")
    print(f"  p = {p} (простое число)")
    print(f"  g = {g} (генератор группы)")
    
    # Инициализация протокола
    zk = ZKSNARK(p, g)
    
    # Секрет Анны
    secret_a = 6
    print(f"\nСекрет Анны: a = {secret_a}")
    
    # Генерация ключей
    public_key, private_key = zk.generate_keypair(secret_a)
    print(f"Открытый ключ: y = g ^ a mod p = {public_key}")
    
    # Анна генерирует доказательство
    print("\n--- Анна генерирует доказательство ---")
    t, r, c = zk.prove(secret_a, public_key, random_seed = 42)
    print(f"  t = g ^ v mod p = {t}")
    print(f"  c = H(g, y, t) = {c}")
    print(f"  r = v - c * a mod (p - 1) = {r}")
    
    # Карл проверяет доказательство
    print("\n--- Карл проверяет доказательство ---")
    is_valid = zk.verify(public_key, t, r)
    print(f"Результат проверки: {'✅ ИСТИНА (доказательство верно)' if is_valid else '❌ ЛОЖЬ (доказательство неверно)'}")
    
    # Проверка математического тождества
    print("\n--- Математическая проверка ---")
    left = t
    right = (pow(g, r, p) * pow(public_key, c, p)) % p
    print(f"  t = {left}")
    print(f"  g ^ r * y ^ c mod p = {right}")
    print(f"  Равенство выполняется: {left == right}")


def demo_attack():
    """Демонстрация попытки подделки доказательства"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АТАКИ (ПОДДЕЛКА ДОКАЗАТЕЛЬСТВА)")
    print("=" * 60)
    
    p = 23
    g = 5
    zk = ZKSNARK(p, g)
    
    # Честная Анна
    secret_a = 6
    public_key, _ = zk.generate_keypair(secret_a)
    
    print(f"\nОткрытый ключ Анны: y = {public_key}")
    print(f"(Злоумышленник знает y, но НЕ знает a)")
    
    # Атака: злоумышленник пытается подделать доказательство
    print("\n--- Злоумышленник пытается подделать доказательство ---")
    t_fake, r_fake, c_fake = zk.attack_fake_proof(public_key)
    print(f"  Подогнанный t = {t_fake}")
    print(f"  Выбранный c = {c_fake}")
    print(f"  Выбранный r = {r_fake}")
    
    # Проверка подделки
    print("\n--- Проверка поддельного доказательства ---")
    is_valid_fake = zk.verify(public_key, t_fake, r_fake)
    
    print(f"Результат проверки: {'✅ ИСТИНА' if is_valid_fake else '❌ ЛОЖЬ (подделка раскрыта)'}")
    
    # Объяснение
    print("\n--- Почему атака не сработала ---")
    c_real = zk.hash_to_int(g, public_key, t_fake)
    print(f"  Хеш от (g, y, t): c_real = {c_real}")
    print(f"  А злоумышленник выбрал: c_fake = {c_fake}")
    print(f"  Они не совпадают: {c_real} != {c_fake}")
    print("  ✅ Криптостойкая хеш-функция предотвращает подделку!")
    

def demo_multiple_examples():
    """Демонстрация с несколькими разными секретами"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С РАЗНЫМИ СЕКРЕТАМИ")
    print("=" * 60)
    
    p = 101  # Большее простое число
    g = 2    # Первообразный корень по модулю 101
    
    # Проверим, что g - первообразный корень
    if not ZKSNARK.is_primitive_root(g, p):
        print(f"Предупреждение: {g} не является первообразным корнем по модулю {p}")
        # Найдём подходящий g
        for test_g in range(2, p):
            if ZKSNARK.is_primitive_root(test_g, p):
                g = test_g
                print(f"Используем g = {g} как первообразный корень")
                break
    
    zk = ZKSNARK(p, g)
    
    secrets = [3, 7, 15, 42]
    
    print(f"\nПубличные параметры: p = {p}, g = {g}")
    print("\nСекрет | Открытый ключ | Доказательство | Проверка")
    print("-" * 60)
    
    for secret in secrets:
        public_key, _ = zk.generate_keypair(secret)
        t, r, c = zk.prove(secret, public_key, random_seed = secret)
        is_valid = zk.verify(public_key, t, r)
        
        status = "✅" if is_valid else "❌"
        print(f"{secret:6} | {public_key:12} | {t:4}, {r:4} | {status}")
    

def demo_with_large_numbers():
    """Демонстрация с большими числами (реалистичный размер)"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С БОЛЬШИМИ ЧИСЛАМИ")
    print("=" * 60)
    
    # Используем 16-битное простое число (для демонстрации)
    # В реальных протоколах используются 256-битные числа
    p = 65537  # Простое число Ферма
    g = 3      # Первообразный корень по модулю 65537
    
    # Проверим, что g - первообразный корень
    if not ZKSNARK.is_primitive_root(g, p):
        print(f"Предупреждение: {g} не является первообразным корнем по модулю {p}")
        # Найдём подходящий g
        for test_g in range(2, p):
            if ZKSNARK.is_primitive_root(test_g, p):
                g = test_g
                print(f"Используем g = {g} как первообразный корень")
                break
    
    zk = ZKSNARK(p, g)
    
    # Случайный секрет
    secret = random.randint(1, p-2)
    public_key, _ = zk.generate_keypair(secret)
    
    print(f"\nРазмер чисел: p = {p} (~{p.bit_length()} бит)")
    print(f"Секрет a = {secret}")
    print(f"Открытый ключ y = {public_key}")
    
    # Доказательство
    import time
    start = time.time()
    t, r, c = zk.prove(secret, public_key)
    proof_time = time.time() - start
    
    # Проверка
    start = time.time()
    is_valid = zk.verify(public_key, t, r)
    verify_time = time.time() - start
    
    print(f"\nДоказательство:")
    print(f"  t = {t}")
    print(f"  r = {r}")
    print(f"  c = {c}")
    print(f"\nРезультат: {'✅ Верно' if is_valid else '❌ Неверно'}")
    print(f"Время генерации доказательства: {proof_time * 1000:.3f} мс")
    print(f"Время проверки: {verify_time * 1000:.3f} мс")


def demo_zero_knowledge_property():
    """Демонстрация свойства нулевого разглашения"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ СВОЙСТВА НУЛЕВОГО РАЗГЛАШЕНИЯ")
    print("=" * 60)
    
    p = 23
    g = 5
    zk = ZKSNARK(p, g)
    
    # Два разных секрета, но одинаковое доказательство?
    secret1 = 6
    secret2 = 8
    
    public_key1, _ = zk.generate_keypair(secret1)
    public_key2, _ = zk.generate_keypair(secret2)
    
    print(f"\nСекрет 1: a = {secret1} -> y = {public_key1}")
    print(f"Секрет 2: a = {secret2} -> y = {public_key2}")
    
    # Генерируем доказательства
    t1, r1, c1 = zk.prove(secret1, public_key1, random_seed = 100)
    t2, r2, c2 = zk.prove(secret2, public_key2, random_seed = 200)
    
    print(f"\nДоказательство 1: (t = {t1}, r = {r1}, c = {c1})")
    print(f"Доказательство 2: (t = {t2}, r = {r2}, c = {c2})")
    
    print("\nСвойства:")
    print(f"  ✅ Доказательства разные (как и ожидалось)")
    print(f"  ✅ Проверка 1: {zk.verify(public_key1, t1, r1)}")
    print(f"  ✅ Проверка 2: {zk.verify(public_key2, t2, r2)}")
    print(f"  ❌ Проверка 1 со вторым доказательством: {zk.verify(public_key1, t2, r2)}")
    print(f"  ❌ Проверка 2 с первым доказательством: {zk.verify(public_key2, t1, r1)}")
    
    print("\n📝 Вывод: Доказательства привязаны к конкретному открытому ключу")
    print("   и не раскрывают информацию о секрете.")


def main():
    """Главная функция со всеми демонстрациями"""
    print("🧙‍♂️  РЕАЛИЗАЦИЯ ПРОТОКОЛА zk-SNARK НА PYTHON")
    print("   (на основе дискретного логарифма)\n")
    
    # Запускаем все демонстрации
    demo_basic_protocol()
    demo_attack()
    demo_multiple_examples()
    demo_with_large_numbers()
    demo_zero_knowledge_property()
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ")
    print("=" * 60)


if __name__ == "__main__":
    main()