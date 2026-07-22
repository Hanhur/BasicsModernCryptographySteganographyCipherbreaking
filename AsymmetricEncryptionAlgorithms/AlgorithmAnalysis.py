# Анализ алгоритма
"""
АЛГОРИТМ ДИФФИ-ХЕЛЛМАНА (БЕЗ NUMPY)
Демонстрация:
1. Легальный обмен ключами
2. Атака "Человек посередине" (Man-in-the-Middle)
3. Проверка на малые подгруппы (атака с B = 1)
4. Визуализация вычислений по модулю
"""

import random
import math
import time

# ======================== БЛОК 1: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================

def is_prime(n, k = 5):
    """
    Тест Миллера-Рабина для проверки простоты числа
    (используется для генерации безопасного p)
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Представляем n-1 как d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Проверяем k раундов
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

def generate_prime(bits = 8):
    """
    Генерирует простое число заданной битности
    (для демонстрации используем 8-битные числа)
    """
    while True:
        # Генерируем нечетное число в диапазоне [2^(bits-1), 2^bits - 1]
        num = random.getrandbits(bits)
        # Убеждаемся, что число нечетное и достаточно большое
        num |= (1 << (bits - 1)) | 1
        if is_prime(num):
            return num

def find_primitive_root(p):
    """
    Находит первообразный корень по модулю p
    (порождающий элемент группы)
    """
    if p == 2:
        return 1
    
    # Разложение p-1 на простые множители
    phi = p - 1
    factors = []
    n = phi
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    
    # Ищем g
    for g in range(2, p):
        ok = True
        for factor in factors:
            if pow(g, phi // factor, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None

def mod_exp(base, exp, mod):
    """
    Быстрое возведение в степень по модулю (бинарный метод)
    Встроенная pow() делает это быстрее, но здесь показан алгоритм
    """
    result = 1
    base = base % mod
    while exp > 0:
        if exp & 1:  # если бит установлен
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result

# ======================== БЛОК 2: КЛАСС УЧАСТНИКА ========================

class DiffieHellmanParticipant:
    """Класс, представляющий участника обмена ключами"""
    
    def __init__(self, name, p, g):
        self.name = name
        self.p = p
        self.g = g
        # Генерируем секретный ключ (случайное число от 2 до p-2)
        self.private_key = random.randint(2, p - 2)
        # Вычисляем открытый ключ: A = g^a mod p
        self.public_key = pow(g, self.private_key, p)
        self.shared_secret = None
    
    def compute_shared_secret(self, other_public_key):
        """Вычисляет общий секрет: K = (B) ^ a mod p"""
        self.shared_secret = pow(other_public_key, self.private_key, self.p)
        return self.shared_secret
    
    def __str__(self):
        return f"{self.name}: приватный = {self.private_key}, публичный = {self.public_key}"

# ======================== БЛОК 3: КЛАСС ЗЛОУМЫШЛЕННИКА ========================

class Eve:
    """Класс злоумышленника, реализующий атаку Man-in-the-Middle"""
    
    def __init__(self, p, g):
        self.p = p
        self.g = g
        # Ева генерирует свои пары ключей
        self.private_key_alice = random.randint(2, p - 2)
        self.private_key_bob = random.randint(2, p - 2)
        self.public_key_alice = pow(g, self.private_key_alice, p)
        self.public_key_bob = pow(g, self.private_key_bob, p)
        self.secret_with_alice = None
        self.secret_with_bob = None
    
    def intercept_alice(self, alice_public):
        """Ева перехватывает ключ Алисы и подменяет его"""
        print(f"  🕵️  Ева перехватила публичный ключ Алисы: {alice_public}")
        print(f"  🕵️  Ева подменяет его своим: {self.public_key_alice}")
        self.secret_with_alice = pow(alice_public, self.private_key_alice, self.p)
        return self.public_key_alice
    
    def intercept_bob(self, bob_public):
        """Ева перехватывает ключ Боба и подменяет его"""
        print(f"  🕵️  Ева перехватила публичный ключ Боба: {bob_public}")
        print(f"  🕵️  Ева подменяет его своим: {self.public_key_bob}")
        self.secret_with_bob = pow(bob_public, self.private_key_bob, self.p)
        return self.public_key_bob
    
    def show_secrets(self):
        print(f"  🕵️  Ева знает секрет с Алисой: {self.secret_with_alice}")
        print(f"  🕵️  Ева знает секрет с Бобом: {self.secret_with_bob}")

# ======================== БЛОК 4: ОСНОВНЫЕ ДЕМОНСТРАЦИИ ========================

def demo_legitimate_exchange():
    """Демонстрация 1: Легальный обмен ключами"""
    print("\n" + "=" * 70)
    print("📌 ДЕМОНСТРАЦИЯ 1: ЛЕГАЛЬНЫЙ ОБМЕН КЛЮЧАМИ")
    print("=" * 70)
    
    # 1. Генерация параметров
    print("\n🔧 Шаг 1: Генерация параметров...")
    p = generate_prime(8)  # 8-битное простое число для наглядности
    g = find_primitive_root(p)
    print(f"   p = {p} (простое)")
    print(f"   g = {g} (первообразный корень по модулю {p})")
    
    # 2. Создание участников
    print("\n🔑 Шаг 2: Участники генерируют ключи...")
    alice = DiffieHellmanParticipant("Алиса", p, g)
    bob = DiffieHellmanParticipant("Боб", p, g)
    print(f"   {alice}")
    print(f"   {bob}")
    
    # 3. Обмен открытыми ключами
    print("\n📤 Шаг 3: Обмен открытыми ключами...")
    print(f"   Алиса отправляет Бобу: A = {alice.public_key}")
    print(f"   Боб отправляет Алисе: B = {bob.public_key}")
    
    # 4. Вычисление общего секрета
    print("\n🔐 Шаг 4: Вычисление общего секрета...")
    secret_alice = alice.compute_shared_secret(bob.public_key)
    secret_bob = bob.compute_shared_secret(alice.public_key)
    print(f"   Алиса вычислила: K = B ^ a mod p = {bob.public_key} ^ {alice.private_key} mod {p} = {secret_alice}")
    print(f"   Боб вычислил: K = A ^ b mod p = {alice.public_key} ^ {bob.private_key} mod {p} = {secret_bob}")
    
    # 5. Проверка
    print("\n✅ Шаг 5: Проверка...")
    if secret_alice == secret_bob:
        print(f"   ✅ СЕКРЕТ СОШЕЛСЯ! Общий ключ: {secret_alice}")
        print(f"   Математика: g ^ (a * b) = {pow(g, alice.private_key * bob.private_key, p)}")
    else:
        print("   ❌ ОШИБКА: секреты не совпали!")
    
    return alice, bob

def demo_mitm_attack():
    """Демонстрация 2: Атака Man-in-the-Middle"""
    print("\n" + "=" * 70)
    print("📌 ДЕМОНСТРАЦИЯ 2: АТАКА «ЧЕЛОВЕК ПОСЕРЕДИНЕ»")
    print("=" * 70)
    
    # 1. Генерация параметров
    p = generate_prime(8)
    g = find_primitive_root(p)
    print(f"\nПараметры: p = {p}, g = {g}")
    
    # 2. Создание участников
    alice = DiffieHellmanParticipant("Алиса", p, g)
    bob = DiffieHellmanParticipant("Боб", p, g)
    eve = Eve(p, g)
    
    print(f"\n🔑 Исходные ключи:")
    print(f"   {alice}")
    print(f"   {bob}")
    print(f"   🕵️  Ева: публичный для Алисы = {eve.public_key_alice}, публичный для Боба = {eve.public_key_bob}")
    
    # 3. Атака
    print("\n🎯 Шаг 1: Алиса отправляет A Бобу, но Ева перехватывает...")
    alice_to_bob = eve.intercept_alice(alice.public_key)
    print(f"   Боб получает от Евы: A' = {alice_to_bob}")
    
    print("\n🎯 Шаг 2: Боб отправляет B Алисе, но Ева перехватывает...")
    bob_to_alice = eve.intercept_bob(bob.public_key)
    print(f"   Алиса получает от Евы: B' = {bob_to_alice}")
    
    # 4. Вычисление секретов
    print("\n🔐 Шаг 3: Вычисление секретов...")
    secret_alice = alice.compute_shared_secret(bob_to_alice)  # Алиса думает, что это ключ Боба
    secret_bob = bob.compute_shared_secret(alice_to_bob)      # Боб думает, что это ключ Алисы
    eve.show_secrets()
    
    print(f"\n   Алиса вычислила секрет: {secret_alice}")
    print(f"   Боб вычислил секрет: {secret_bob}")
    print(f"   🕵️  Ева знает оба секрета!")
    
    # 5. Итог
    print("\n⚠️  ИТОГ: Алиса и Боб думают, что общаются напрямую,")
    print(f"   но на самом деле Ева читает весь трафик!")
    print(f"   Алиса↔Ева: {secret_alice}, Боб↔Ева: {secret_bob}")
    
    return alice, bob, eve

def demo_small_subgroup_attack():
    """Демонстрация 3: Атака с использованием элемента малой подгруппы"""
    print("\n" + "=" * 70)
    print("📌 ДЕМОНСТРАЦИЯ 3: АТАКА НА МАЛУЮ ПОДГРУППУ (B = 1)")
    print("=" * 70)
    
    # Используем фиксированный p для демонстрации
    p = 23
    g = 5  # Первообразный корень по модулю 23
    print(f"\nПараметры: p = {p}, g = {g}")
    
    # Алиса честно генерирует ключ
    alice = DiffieHellmanParticipant("Алиса", p, g)
    print(f"\n{alice}")
    
    # Злоумышленник отправляет B = 1 (всегда в подгруппе)
    print(f"\n🎯 Атака: Ева отправляет Алисе B = 1 (вместо честного ключа)")
    malicious_B = 1
    
    # Алиса вычисляет секрет
    secret = alice.compute_shared_secret(malicious_B)
    print(f"   Алиса вычислила: K = 1 ^ {alice.private_key} mod {p} = {secret}")
    
    if secret == 1:
        print(f"\n⚠️  СЕКРЕТ СТАЛ РАВЕН 1! Ева знает его без вычислений.")
        print(f"   Это делает шифрование бесполезным.")
    
    # Демонстрация проверки
    print(f"\n✅ Защита: всегда проверяйте, что B ^ ((p - 1) / 2) ≠ 1")
    print(f"   Проверка B = {malicious_B}: {malicious_B} ^ { (p - 1) // 2 } mod {p} = {pow(malicious_B, (p - 1) // 2, p)}")
    if pow(malicious_B, (p - 1) // 2, p) == 1:
        print("   ⚠️  Элемент находится в малой подгруппе! Нужно отклонить.")
    
    return alice

def demo_visual_computation():
    """Демонстрация 4: Визуализация вычислений"""
    print("\n" + "=" * 70)
    print("📌 ДЕМОНСТРАЦИЯ 4: ПОШАГОВАЯ ВИЗУАЛИЗАЦИЯ ВЫЧИСЛЕНИЙ")
    print("=" * 70)
    
    # Используем маленькие числа для наглядности
    p = 11
    g = 7  # 7 - первообразный корень по модулю 11 (как в вашем примере)
    a = 3
    b = 6
    
    print(f"\nПараметры: p = {p}, g = {g}")
    print(f"Секретные ключи: a = {a}, b = {b}")
    
    # Шаг 1: Вычисление открытых ключей
    print("\n🔧 Шаг 1: Вычисление открытых ключей:")
    A = pow(g, a, p)
    B = pow(g, b, p)
    print(f"   A = g ^ a mod p = {g} ^ {a} mod {p} = {A}")
    print(f"   B = g ^ b mod p = {g} ^ {b} mod {p} = {B}")
    
    # Шаг 2: Обмен
    print("\n📤 Шаг 2: Обмен открытыми ключами:")
    print(f"   Алиса отправляет A = {A}")
    print(f"   Боб отправляет B = {B}")
    
    # Шаг 3: Вычисление секрета
    print("\n🔐 Шаг 3: Вычисление общего секрета:")
    
    # Алиса: K = B^a mod p
    K_alice = pow(B, a, p)
    print(f"   Алиса: K = B ^ a mod p = {B} ^ {a} mod {p} = {K_alice}")
    print(f"   Раскрываем: ({g} ^ {b}) ^ {a} = g ^ ({b} * {a}) = g ^ {a * b}")
    
    # Боб: K = A^b mod p
    K_bob = pow(A, b, p)
    print(f"   Боб: K = A ^ b mod p = {A} ^ {b} mod {p} = {K_bob}")
    print(f"   Раскрываем: ({g} ^ {a}) ^ {b} = g ^ ({a} * {b}) = g ^ {a * b}")
    
    # Проверка
    print(f"\n✅ Итог: g ^ ({a} * {b}) = {g} ^ {a * b} mod {p} = {pow(g, a * b, p)}")
    print(f"   Общий секрет: {K_alice}")
    
    # Демонстрация вашего примера из текста
    print(f"\n📖 Сверяем с вашим примером из текста:")
    print(f"   (7 ^ 6) ^ 3 = 7 ^ (6 * 3) = 7 ^ 18 mod 11 = {pow(7, 18, 11)}")
    print(f"   (7 ^ 3) ^ 6 = 7 ^ (3 * 6) = 7 ^ 18 mod 11 = {pow(7, 18, 11)}")
    print(f"   ✅ Совпадает: 9 (как в тексте)")

# ======================== БЛОК 5: ЗАПУСК ========================

def main():
    """Главная функция для запуска всех демонстраций"""
    print("=" * 70)
    print("🔐 АЛГОРИТМ ДИФФИ-ХЕЛЛМАНА: ПОЛНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 70)
    print("(Без использования numpy - чистый Python)")
    
    # Демонстрация 4: Визуализация (самая простая, показываем первой)
    demo_visual_computation()
    
    # Демонстрация 1: Легальный обмен
    demo_legitimate_exchange()
    
    # Демонстрация 2: Атака MitM
    demo_mitm_attack()
    
    # Демонстрация 3: Атака на малую подгруппу
    demo_small_subgroup_attack()
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("📚 ИТОГОВЫЕ ВЫВОДЫ:")
    print("=" * 70)
    print("1. ✅ Базовый DH работает на свойстве: (g ^ a) ^ b ≡ (g ^ b) ^ a (mod p)")
    print("2. ⚠️  Без аутентификации уязвим к MitM (Ева читает всё)")
    print("3. ⚠️  Необходимо проверять ключи на принадлежность к большой подгруппе")
    print("4. 🔒 Для защиты используйте ECDHE + цифровые подписи (как в TLS)")
    print("5. 🚀 В реальных системах p должно быть ≥ 2048 бит")
    print("=" * 70)

if __name__ == "__main__":
    # Фиксируем seed для воспроизводимости результатов
    random.seed(42)
    main()