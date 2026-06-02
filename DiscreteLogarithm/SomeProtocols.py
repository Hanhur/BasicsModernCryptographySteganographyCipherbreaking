# 2. Некоторые протоколы, основанные на трудности нахождения дискретного логарифма
"""
Реализация протоколов, основанных на трудности нахождения дискретного логарифма:
1. Протокол Диффи-Хеллмана (разделение секретного ключа)
2. Протокол Масси-Омуры (шифрование сообщения)
3. Протокол Эль-Гамаля (асимметричное шифрование)

Внимание: Данная реализация предназначена для образовательных целей.
Для реального использования необходимы простые числа гораздо большего размера (например, 2048 бит)
и криптостойкие генераторы случайных чисел.
"""

import random
import math
from typing import Tuple, Optional


def gcd(a: int, b: int) -> int:
    """Наибольший общий делитель."""
    return math.gcd(a, b)


def mod_inverse(a: int, m: int) -> int:
    """
    Обратное число по модулю m.
    Используется расширенный алгоритм Евклида.
    """
    # Обратное существует только если a и m взаимно просты
    if gcd(a, m) != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    
    # Расширенный алгоритм Евклида
    original_m = m
    x0, x1 = 1, 0
    
    while m > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1, x0 - q * x1
    
    return x0 % original_m


def is_prime(n: int, k: int = 10) -> bool:
    """
    Проверка числа на простоту (тест Миллера-Рабина).
    Для учебных целей используем простую проверку.
    В реальности нужно использовать библиотечные функции или большие простые числа.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Для малых чисел используем простой перебор (учебный вариант)
    if n < 1000000:
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    # Для больших чисел используем вероятностный тест (упрощённо)
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
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


def find_primitive_root(p: int) -> int:
    """
    Находит первообразный корень по модулю простого числа p.
    Для составных полей эта функция должна быть более сложной.
    """
    if not is_prime(p):
        raise ValueError("p должно быть простым числом")
    
    # Разложение p-1 на простые множители (упрощённо)
    factors = []
    phi = p - 1
    n = phi
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
        i += 1
    if n > 1:
        factors.append(n)
    
    # Поиск первообразного корня
    for g in range(2, p):
        ok = True
        for q in factors:
            if pow(g, phi // q, p) == 1:
                ok = False
                break
        if ok:
            return g
    
    raise ValueError("Не удалось найти первообразный корень")


class FiniteField:
    """
    Простейшее представление конечного поля F_p (простого поля).
    Для F_{p ^ r} потребовалась бы более сложная реализация.
    """
    
    def __init__(self, p: int):
        if not is_prime(p):
            raise ValueError(f"{p} не является простым числом")
        self.p = p
        self.primitive_root = find_primitive_root(p)
    
    def multiply(self, a: int, b: int) -> int:
        """Умножение в поле (по модулю p)."""
        return (a * b) % self.p
    
    def power(self, base: int, exp: int) -> int:
        """Возведение в степень в поле (по модулю p)."""
        return pow(base, exp, self.p)
    
    def add(self, a: int, b: int) -> int:
        """Сложение в поле (по модулю p)."""
        return (a + b) % self.p
    
    def subtract(self, a: int, b: int) -> int:
        """Вычитание в поле (по модулю p)."""
        return (a - b) % self.p
    
    def divide(self, a: int, b: int) -> int:
        """Деление в поле: a * b^{-1} mod p."""
        return (a * mod_inverse(b, self.p)) % self.p


class DiffieHellman:
    """
    Протокол Диффи-Хеллмана для разделения секретного ключа.
    """
    
    def __init__(self, field: FiniteField, g: int):
        self.field = field
        self.g = g  # образующий элемент
        self.secret: Optional[int] = None  # секретное число (x или z)
        self.public: Optional[int] = None  # публичное значение (g^x или g^z)
        self.shared_secret: Optional[int] = None  # разделённый секрет
    
    def generate_secret(self) -> None:
        """Генерация секретного числа (случайное натуральное число)."""
        # Выбираем случайное число от 1 до p-2
        self.secret = random.randint(1, self.field.p - 2)
    
    def compute_public(self) -> int:
        """Вычисление публичного значения y = g^x."""
        if self.secret is None:
            raise ValueError("Сначала сгенерируйте секретное число")
        self.public = self.field.power(self.g, self.secret)
        return self.public
    
    def compute_shared_secret(self, other_public: int) -> int:
        """
        Вычисление разделённого секрета на основе публичного значения собеседника.
        shared = other_public^secret
        """
        if self.secret is None:
            raise ValueError("Сначала сгенерируйте секретное число")
        self.shared_secret = self.field.power(other_public, self.secret)
        return self.shared_secret
    
    @staticmethod
    def demo():
        """Демонстрация работы протокола Диффи-Хеллмана."""
        print("\n" + "=" * 60)
        print("ПРОТОКОЛ ДИФФИ-ХЕЛЛМАНА (разделение секретного ключа)")
        print("=" * 60)
        
        # Установка: выбираем простое поле и образующий элемент
        # В реальности p должно быть очень большим
        p = 997  # Простое число для демонстрации
        field = FiniteField(p)
        g = field.primitive_root
        print(f"Открытые параметры: поле F_{p}, образующий элемент g = {g}")
        
        # Алиса
        alice = DiffieHellman(field, g)
        alice.generate_secret()
        alice_public = alice.compute_public()
        print(f"Алиса: секрет = {alice.secret}, публичное = {alice_public}")
        
        # Боб
        bob = DiffieHellman(field, g)
        bob.generate_secret()
        bob_public = bob.compute_public()
        print(f"Боб: секрет = {bob.secret}, публичное = {bob_public}")
        
        # Обмен публичными значениями (по открытому каналу)
        print("\nПередача публичных значений по открытому каналу...")
        
        # Вычисление общего секрета
        alice_shared = alice.compute_shared_secret(bob_public)
        bob_shared = bob.compute_shared_secret(alice_public)
        
        print(f"\nАлиса вычислила общий секрет: {alice_shared}")
        print(f"Боб вычислил общий секрет: {bob_shared}")
        
        if alice_shared == bob_shared:
            print(f"\n✓ Успех! Общий секретный ключ: {alice_shared}")
        else:
            print("\n✗ Ошибка: секреты не совпадают")


class MasseyOmura:
    """
    Протокол Масси-Омуры (шифрование с тройным обменом).
    Сообщение m передаётся от Алисы к Бобу.
    """
    
    def __init__(self, field: FiniteField):
        self.field = field
        self.order = field.p - 1  # порядок мультипликативной группы F_p*
    
    def generate_key(self) -> Tuple[int, int]:
        """
        Генерация пары ключей (x, x ^ {-1} mod (p-1)).
        x взаимно просто с p-1.
        """
        while True:
            x = random.randint(2, self.order - 1)
            if gcd(x, self.order) == 1:
                x_inv = mod_inverse(x, self.order)
                return x, x_inv
    
    def encrypt(self, message: int, exponent: int) -> int:
        """Шифрование: m^exponent mod p."""
        return self.field.power(message, exponent)
    
    @staticmethod
    def demo():
        """Демонстрация работы протокола Масси-Омуры."""
        print("\n" + "=" * 60)
        print("ПРОТОКОЛ МАССИ-ОМУРЫ (шифрование с тройным обменом)")
        print("=" * 60)
        
        # Установка
        p = 101  # Простое число (в реальности нужно большее)
        field = FiniteField(p)
        print(f"Открытые параметры: поле F_{p}")
        
        # Секретное сообщение Алисы
        message = 42
        print(f"\nАлиса хочет передать сообщение: {message}")
        
        # Создаем экземпляр протокола
        protocol = MasseyOmura(field)
        
        # Алиса
        alice_x, alice_x_inv = protocol.generate_key()
        print(f"Алиса: x = {alice_x}, x ^ {-1} = {alice_x_inv}")
        
        # Боб
        bob_z, bob_z_inv = protocol.generate_key()
        print(f"Боб: z = {bob_z}, z ^ {-1} = {bob_z_inv}")
        
        # Протокол
        print("\n--- Выполнение протокола ---")
        
        # Шаг 1: Алиса отправляет m ^ x
        step1 = protocol.encrypt(message, alice_x)
        print(f"1. Алиса → Боб: m ^ {alice_x} = {step1}")
        
        # Шаг 2: Боб возводит в степень z, отправляет m ^ {xz}
        step2 = protocol.encrypt(step1, bob_z)
        print(f"2. Боб → Алиса: (m ^ {alice_x}) ^ {bob_z} = m ^ {alice_x * bob_z} = {step2}")
        
        # Шаг 3: Алиса возводит в степень x ^ {-1}, получает m ^ z
        step3 = protocol.encrypt(step2, alice_x_inv)
        print(f"3. Алиса → Боб: (m ^ {alice_x * bob_z}) ^ {alice_x_inv} = m ^ {bob_z} = {step3}")
        
        # Шаг 4: Боб возводит в степень z ^ {-1}, получает m
        decrypted = protocol.encrypt(step3, bob_z_inv)
        print(f"4. Боб расшифровывает: (m ^ {bob_z}) ^ {bob_z_inv} = m ^ {1} = {decrypted}")
        
        if decrypted == message:
            print(f"\n✓ Успех! Сообщение успешно расшифровано: {decrypted}")
        else:
            print(f"\n✗ Ошибка: получено {decrypted}, ожидалось {message}")


class ElGamal:
    """
    Протокол Эль-Гамаля (асимметричное шифрование).
    """
    
    def __init__(self, field: FiniteField, g: int):
        self.field = field
        self.g = g
        self.private_key: Optional[int] = None
        self.public_key: Optional[int] = None
    
    def generate_keypair(self) -> Tuple[int, int]:
        """
        Генерация пары ключей:
        - private_key: b (секретное число)
        - public_key: g ^ b
        """
        self.private_key = random.randint(1, self.field.p - 2)
        self.public_key = self.field.power(self.g, self.private_key)
        return self.private_key, self.public_key
    
    def encrypt(self, message: int, recipient_public_key: int) -> Tuple[int, int]:
        """
        Шифрование сообщения для получателя.
        Возвращает (c1, c2) = (g ^ k, m * (g ^ b) ^ k)
        """
        # Выбираем случайное k
        k = random.randint(1, self.field.p - 2)
        
        # c1 = g ^ k
        c1 = self.field.power(self.g, k)
        
        # s = (g ^ b) ^ k = g ^ {bk}
        s = self.field.power(recipient_public_key, k)
        
        # c2 = m * s mod p
        c2 = self.field.multiply(message, s)
        
        return (c1, c2)
    
    def decrypt(self, ciphertext: Tuple[int, int]) -> int:
        """
        Расшифрование сообщения с использованием закрытого ключа.
        """
        c1, c2 = ciphertext
        
        if self.private_key is None:
            raise ValueError("Закрытый ключ не установлен")
        
        # s = c1 ^ b = g ^ {kb}
        s = self.field.power(c1, self.private_key)
        
        # m = c2 * s ^ {-1}
        s_inv = mod_inverse(s, self.field.p)
        message = self.field.multiply(c2, s_inv)
        
        return message
    
    @staticmethod
    def demo():
        """Демонстрация работы протокола Эль-Гамаля."""
        print("\n" + "=" * 60)
        print("ПРОТОКОЛ ЭЛЬ-ГАМАЛЯ (асимметричное шифрование)")
        print("=" * 60)
        
        # Установка: поле и образующий элемент
        p = 257  # Простое число (в реальности нужно большее)
        field = FiniteField(p)
        g = field.primitive_root
        print(f"Открытые параметры: поле F_{p}, образующий элемент g = {g}")
        
        # Генерация ключей для Боба (получателя)
        bob = ElGamal(field, g)
        bob_private, bob_public = bob.generate_keypair()
        print(f"\nБоб (получатель):")
        print(f"  Секретный ключ: {bob_private}")
        print(f"  Открытый ключ: {bob_public}")
        
        # Алиса хочет передать сообщение
        message = 123
        print(f"\nАлиса хочет передать сообщение: {message}")
        
        # Алиса шифрует сообщение, используя открытый ключ Боба
        alice = ElGamal(field, g)
        ciphertext = alice.encrypt(message, bob_public)
        print(f"Алиса отправляет шифротекст: {ciphertext}")
        
        # Боб расшифровывает
        decrypted = bob.decrypt(ciphertext)
        print(f"Боб расшифровал сообщение: {decrypted}")
        
        if decrypted == message:
            print(f"\n✓ Успех! Сообщение успешно расшифровано")
        else:
            print(f"\n✗ Ошибка: получено {decrypted}, ожидалось {message}")


def demonstrate_man_in_the_middle():
    """
    Демонстрация атаки "человек посередине" на протокол Диффи-Хеллмана.
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АТАКИ \"ЧЕЛОВЕК ПОСЕРЕДИНЕ\"")
    print("=" * 60)
    
    p = 997
    field = FiniteField(p)
    g = field.primitive_root
    print(f"Открытые параметры: поле F_{p}, g = {g}")
    
    # Алиса
    alice = DiffieHellman(field, g)
    alice.generate_secret()
    alice_public = alice.compute_public()
    print(f"\nАлиса: секрет = {alice.secret}, публичный = {alice_public}")
    
    # Боб
    bob = DiffieHellman(field, g)
    bob.generate_secret()
    bob_public = bob.compute_public()
    print(f"Боб: секрет = {bob.secret}, публичный = {bob_public}")
    
    # Злоумышленник Ева (перехватывает и подменяет сообщения)
    eve = DiffieHellman(field, g)
    eve.generate_secret()
    eve_public = eve.compute_public()
    print(f"Ева: секрет = {eve.secret}, публичный = {eve_public}")
    
    print("\n--- Атака \"человек посередине\" ---")
    print("Ева перехватывает сообщения и подменяет их:")
    
    # Ева выдаёт себя за Алису перед Бобом
    # и за Боба перед Алисой
    
    # Алиса думает, что общается с Бобом, но общается с Евой
    alice_shared_with_eve = alice.compute_shared_secret(eve_public)
    
    # Боб думает, что общается с Алисой, но общается с Евой
    bob_shared_with_eve = bob.compute_shared_secret(eve_public)
    
    # Ева вычисляет оба общих секрета
    eve_shared_with_alice = eve.compute_shared_secret(alice_public)
    eve_shared_with_bob = eve.compute_shared_secret(bob_public)
    
    print(f"\nРезультаты:")
    print(f"  Алиса думает, что её общий секрет с Бобом: {alice_shared_with_eve}")
    print(f"  Боб думает, что его общий секрет с Алисой: {bob_shared_with_eve}")
    print(f"  Ева имеет секрет с Алисой: {eve_shared_with_alice}")
    print(f"  Ева имеет секрет с Бобом: {eve_shared_with_bob}")
    
    # Проверяем, что Ева успешно установила ключи
    if eve_shared_with_alice == alice_shared_with_eve and eve_shared_with_bob == bob_shared_with_eve:
        print("\n✓ Ева успешно установила два независимых секретных ключа!")
        print("  Теперь она может расшифровывать, читать и модифицировать")
        print("  все сообщения между Алисой и Бобом, оставаясь незамеченной.")
    else:
        print("\n✗ Что-то пошло не так")
    
    print("\n  ВЫВОД: протоколы без аутентификации уязвимы для MitM-атак.")


def main():
    """Главная функция для демонстрации всех протоколов."""
    print("=" * 60)
    print("ПРОТОКОЛЫ, ОСНОВАННЫЕ НА ДИСКРЕТНОМ ЛОГАРИФМЕ")
    print("=" * 60)
    print("Внимание: Для образовательных целей используются малые простые числа.")
    print("В реальных системах нужны простые числа размером 2048+ бит.\n")
    
    # Демонстрация всех протоколов
    DiffieHellman.demo()
    MasseyOmura.demo()
    ElGamal.demo()
    demonstrate_man_in_the_middle()
    
    print("\n" + "=" * 60)
    print("ЗАВЕРШЕНИЕ ДЕМОНСТРАЦИИ")
    print("=" * 60)


if __name__ == "__main__":
    main()