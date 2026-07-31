# Детали однораундового протокола
"""
Однораундовый протокол доказательства знания x
(Аналог обмена ключами Диффи-Хеллмана)

Реализованы две версии:
1. Классический интерактивный (2 шага): Пегги <-> Виктор
2. Неинтерактивный (1 шаг) с использованием хеш-функции (Фиат-Шамир)
"""

import random
import hashlib


def modinv(a, p):
    """Обратное число по модулю p (расширенный алгоритм Евклида)"""
    return pow(a, -1, p)


class ProtocolParams:
    """Публичные параметры системы"""
    def __init__(self, p, g):
        self.p = p
        self.g = g


class Peggy:
    """Пегги - доказывающая сторона (знает секрет x)"""
    
    def __init__(self, params, x):
        self.params = params
        self.x = x
        # Открытый ключ: b = g^x mod p
        self.b = pow(params.g, x, params.p)
        print(f"[Peggy] Секрет x = {x}")
        print(f"[Peggy] Открытый ключ b = {self.b}")
    
    # ==================== ИНТЕРАКТИВНЫЙ ПРОТОКОЛ (2 ШАГА) ====================
    
    def receive_challenge(self, c):
        """
        Шаг 2: Пегги получает вызов c = g ^ y mod p и вычисляет ответ r = c ^ x mod p
        """
        r = pow(c, self.x, self.params.p)
        print(f"[Peggy] Получен вызов c = {c}")
        print(f"[Peggy] Вычислен ответ r = {r}")
        return r
    
    # ==================== НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ (1 ШАГ) ====================
    
    def generate_proof_noninteractive(self):
        """
        Генерирует одно сообщение (c, r) без взаимодействия с Виктором.
        Использует хеш-функцию для создания вызова y = H(c).
        """
        # Шаг 1: Пегги выбирает случайное k
        k = random.randint(2, self.params.p - 2)
        
        # Шаг 2: Вычисляет c = g^k mod p
        c = pow(self.params.g, k, self.params.p)
        
        # Шаг 3: Генерирует вызов с помощью хеша (заменяет Виктора)
        y_bytes = hashlib.sha256(str(c).encode()).digest()
        y = int.from_bytes(y_bytes, 'big') % (self.params.p - 1)
        
        # Шаг 4: Вычисляет ответ r = k + x*y mod (p-1)
        r = (k + self.x * y) % (self.params.p - 1)
        
        print(f"[Peggy] Неинтерактивный протокол:")
        print(f"  k = {k}, c = {c}, y = H(c) = {y}")
        print(f"  r = k + x * y mod (p - 1) = {r}")
        
        return c, r


class Victor:
    """Виктор - проверяющая сторона (не знает x)"""
    
    def __init__(self, params, b):
        self.params = params
        self.b = b  # Открытый ключ Пегги
        print(f"[Victor] Открытый ключ Пегги b = {b}")
    
    # ==================== ИНТЕРАКТИВНЫЙ ПРОТОКОЛ (2 ШАГА) ====================
    
    def generate_challenge(self):
        """
        Шаг 1: Виктор генерирует случайное y и вычисляет c = g ^ y mod p
        """
        self.y = random.randint(2, self.params.p - 2)
        c = pow(self.params.g, self.y, self.params.p)
        print(f"[Victor] Сгенерирован вызов:")
        print(f"  y = {self.y}, c = g ^ y mod p = {c}")
        return c
    
    def verify_response(self, r):
        """
        Шаг 4: Виктор проверяет: r == b ^ y mod p
        """
        expected = pow(self.b, self.y, self.params.p)
        is_valid = (r == expected)
        print(f"[Victor] Проверка: r = {r}, b ^ y mod p = {expected}")
        print(f"[Victor] Результат: {'✅ ДОКАЗАНО' if is_valid else '❌ ОТВЕРГНУТО'}")
        return is_valid
    
    # ==================== НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ (1 ШАГ) ====================
    
    def verify_proof_noninteractive(self, c, r):
        """
        Проверяет доказательство (c, r) за один шаг.
        Вычисляет y = H(c) и проверяет: g ^ r == c * b ^ y mod p
        """
        # Шаг 1: Виктор вычисляет y = H(c) (так же, как Пегги)
        y_bytes = hashlib.sha256(str(c).encode()).digest()
        y = int.from_bytes(y_bytes, 'big') % (self.params.p - 1)
        
        # Шаг 2: Проверка g^r == c * b^y mod p
        left = pow(self.params.g, r, self.params.p)
        right = (c * pow(self.b, y, self.params.p)) % self.params.p
        
        is_valid = (left == right)
        print(f"[Victor] Неинтерактивная проверка:")
        print(f"  c = {c}, y = H(c) = {y}, r = {r}")
        print(f"  g ^ r mod p = {left}")
        print(f"  c * b ^ y mod p = {right}")
        print(f"[Victor] Результат: {'✅ ДОКАЗАНО' if is_valid else '❌ ОТВЕРГНУТО'}")
        return is_valid


def main():
    """Демонстрация работы обоих протоколов"""
    
    print("=" * 70)
    print("ОДНОРАУНДОВЫЙ ПРОТОКОЛ ДОКАЗАТЕЛЬСТВА ЗНАНИЯ x")
    print("=" * 70)
    
    # ---------- Публичные параметры (как в DH) ----------
    # Простое число p и первообразный корень g
    p = 23  # Маленькое простое для наглядности
    g = 5   # Первообразный корень по модулю 23
    params = ProtocolParams(p, g)
    print(f"\nПубличные параметры:")
    print(f"  p = {p}, g = {g}")
    
    # ---------- Секрет Пегги ----------
    x = random.randint(2, p - 2)
    peggy = Peggy(params, x)
    victor = Victor(params, peggy.b)
    
    print("\n" + "=" * 70)
    print("ЧАСТЬ 1: ИНТЕРАКТИВНЫЙ ПРОТОКОЛ (2 ШАГА)")
    print("=" * 70)
    
    # Шаг 1: Виктор -> Пегги (вызов)
    c = victor.generate_challenge()
    
    # Шаг 2: Пегги -> Виктор (ответ)
    r = peggy.receive_challenge(c)
    
    # Шаг 3: Виктор проверяет
    victor.verify_response(r)
    
    print("\n" + "=" * 70)
    print("ЧАСТЬ 2: НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ (1 ШАГ)")
    print("=" * 70)
    print("(Используется хеш-функция для генерации вызова)")
    
    # Пегги генерирует доказательство за один шаг
    c_nonce, r_nonce = peggy.generate_proof_noninteractive()
    
    # Виктор проверяет за один шаг
    victor.verify_proof_noninteractive(c_nonce, r_nonce)
    
    print("\n" + "=" * 70)
    print("ЧАСТЬ 3: АТАКА - ПЕГГИ НЕ ЗНАЕТ x")
    print("=" * 70)
    print("Попытка сгенерировать доказательство без знания x...")
    
    # Злоумышленник пытается подделать доказательство
    fake_x = random.randint(2, p - 2)
    while fake_x == x:
        fake_x = random.randint(2, p - 2)
    
    fake_peggy = Peggy(params, fake_x)
    fake_b = fake_peggy.b
    
    # Виктор использует правильный открытый ключ b, а не fake_b
    fake_victor = Victor(params, peggy.b)  # Используем правильный b!
    
    # Генерируем доказательство с fake_x
    c_fake, r_fake = fake_peggy.generate_proof_noninteractive()
    
    # Проверяем с правильным b
    fake_victor.verify_proof_noninteractive(c_fake, r_fake)
    
    print("\n" + "=" * 70)
    print("ВЫВОДЫ:")
    print("  1. Интерактивный протокол требует 2 шага (вызов-ответ)")
    print("  2. Неинтерактивный протокол работает за 1 шаг (одно сообщение)")
    print("  3. Без знания x невозможно подделать доказательство")
    print("=" * 70)


if __name__ == "__main__":
    main()