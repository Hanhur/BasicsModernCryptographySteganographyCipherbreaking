# Создание подписи с дополнением в MBXI
import random
import hashlib
import math

# =============================================
# 1. Вспомогательные криптографические функции
# =============================================

def is_prime(n, k = 40):
    """Тест Миллера-Рабина для проверки простоты чисел"""
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
        a = random.randrange(2, n - 1)
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

def generate_prime(bits = 16):
    """Генерация простого числа заданной битности"""
    while True:
        # Генерируем нечетное число
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1  # Ставим старший и младший бит в 1
        if is_prime(num):
            return num

def primitive_root(p):
    """Поиск первообразного корня по модулю p"""
    if p == 2:
        return 1
    
    # Факторизуем p-1
    factors = []
    n = p - 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    
    # Проверяем кандидатов
    g = 2
    while True:
        ok = True
        for factor in factors:
            if pow(g, (p - 1) // factor, p) == 1:
                ok = False
                break
        if ok:
            return g
        g += 1

def mod_inverse(a, m):
    """Нахождение обратного элемента по модулю m (расширенный алгоритм Евклида)"""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("Обратного элемента не существует")

# =============================================
# 2. Класс подписи MBXI
# =============================================

class MBXISignature:
    def __init__(self, bits = 16):
        """
        Инициализация системы MBXI
        bits - битность простого числа p (для демонстрации)
        """
        self.bits = bits
        self.p = None
        self.g = None
        self.private_key = None
        self.public_key = None
    
    def generate_keys(self):
        """Шаг 1: Генерация ключей (G)"""
        print(f"Генерация ключей с битностью {self.bits}...")
        
        # Генерируем простое число p
        self.p = generate_prime(self.bits)
        print(f"p = {self.p}")
        
        # Находим первообразный корень g
        self.g = primitive_root(self.p)
        print(f"g = {self.g}")
        
        # Выбираем закрытый ключ b (1 < b < p-1)
        self.private_key = random.randrange(2, self.p - 1)
        print(f"b (закрытый ключ) = {self.private_key}")
        
        # Вычисляем открытый ключ K_B = g^b mod p
        self.public_key = pow(self.g, self.private_key, self.p)
        print(f"K_B (открытый ключ) = {self.public_key}")
        print("-" * 50)
        
        return {
            'p': self.p,
            'g': self.g,
            'public_key': self.public_key,
            'private_key': self.private_key
        }
    
    def hash_message(self, message):
        """Вычисление хеша сообщения H(m)"""
        # Используем SHA-256, затем берем число по модулю (p-1)
        hash_bytes = hashlib.sha256(message.encode()).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        return hash_int % (self.p - 1)
    
    def sign(self, message):
        """
        Шаг 2: Создание цифровой подписи (s)
        Используем исправленную формулу:
        s = H(m) * (k + b) mod (p - 1)
        """
        if self.p is None or self.private_key is None:
            raise ValueError("Сначала сгенерируйте ключи методом generate_keys()")
        
        # Вычисляем хеш сообщения
        H_m = self.hash_message(message)
        print(f"H(m) = {H_m}")
        
        # Шаг 1: Выбираем случайное k (1 < k < p-1, взаимно простое с p-1)
        while True:
            k = random.randrange(2, self.p - 1)
            if math.gcd(k, self.p - 1) == 1:
                break
        print(f"k (случайный сеансовый ключ) = {k}")
        
        # Вычисляем r = g^k mod p
        r = pow(self.g, k, self.p)
        print(f"r = {r}")
        
        # Вычисляем s = H(m) * (k + b) mod (p-1)
        # ВНИМАНИЕ: это исправленная формула!
        s = (H_m * (k + self.private_key)) % (self.p - 1)
        print(f"s (подпись) = {s}")
        
        return {
            'H_m': H_m,
            'r': r,
            's': s,
            'k': k  # Сохраняем для демонстрации (в реальности не передается)
        }
    
    def verify(self, message, signature):
        """
        Шаг 3: Проверка подписи (V)
        Проверяем: g ^ s ≡ (r * K_B) ^ H(m) (mod p)
        """
        if self.p is None or self.public_key is None:
            raise ValueError("Сначала сгенерируйте ключи методом generate_keys()")
        
        H_m = signature['H_m']
        r = signature['r']
        s = signature['s']
        
        print("\n--- Проверка подписи ---")
        print(f"Получено: H(m) = {H_m}, r = {r}, s = {s}")
        
        # Вычисляем левую часть: g^s mod p
        left = pow(self.g, s, self.p)
        print(f"Левая часть (g ^ s mod p) = {left}")
        
        # Вычисляем правую часть: (r * K_B)^H(m) mod p
        right = pow((r * self.public_key) % self.p, H_m, self.p)
        print(f"Правая часть ((r * K_B) ^ H(m) mod p) = {right}")
        
        # Сравниваем
        if left == right:
            print("✅ ПОДПИСЬ ВЕРНА! V = V1")
            return True
        else:
            print("❌ ПОДПИСЬ НЕВЕРНА!")
            return False

# =============================================
# 3. Демонстрация работы программы
# =============================================

def main():
    print("=" * 60)
    print("ПРОГРАММА ПОДПИСИ MBXI (С ДОПОЛНЕНИЕМ)")
    print("=" * 60)
    print()
    
    # 1. Создаем экземпляр подписи
    mbxi = MBXISignature(bits = 16)  # bits=16 для быстрой работы (можно увеличить до 32, 64)
    
    # 2. Генерируем ключи
    keys = mbxi.generate_keys()
    
    # 3. Сообщение для подписи
    message = "Привет, Алиса! Это секретное сообщение от Боба."
    print(f"\nСообщение: {message}")
    print("-" * 50)
    
    # 4. Создаем подпись
    print("\n--- Процесс подписания ---")
    signature = mbxi.sign(message)
    
    # 5. Проверяем подпись
    result = mbxi.verify(message, signature)
    
    # 6. Дополнительно: проверяем, что подпись не пройдет с измененным сообщением
    print("\n" + "=" * 60)
    print("ПРОВЕРКА АТАКИ: Изменяем сообщение")
    print("=" * 60)
    
    fake_message = "Привет, Алиса! Это фальшивое сообщение от Евы."
    print(f"Поддельное сообщение: {fake_message}")
    
    # Пытаемся проверить ту же подпись с другим сообщением
    # Вычисляем новый хеш для поддельного сообщения
    fake_H = mbxi.hash_message(fake_message)
    fake_signature = {
        'H_m': fake_H,  # Подменяем хеш
        'r': signature['r'],
        's': signature['s']
    }
    
    result_fake = mbxi.verify(fake_message, fake_signature)
    
    # 7. Демонстрация безопасности при повторном использовании k
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ УЯЗВИМОСТИ ПРИ ПОВТОРНОМ ИСПОЛЬЗОВАНИИ k")
    print("=" * 60)
    
    # Создаем второе сообщение
    message2 = "Второе секретное сообщение"
    print(f"Сообщение 2: {message2}")
    
    # Используем ТОТ ЖЕ k (в реальности это критическая ошибка!)
    same_k = signature['k']
    print(f"Злоумышленник заметил, что использован тот же k = {same_k}")
    
    # Создаем подпись для второго сообщения с тем же k
    H_m2 = mbxi.hash_message(message2)
    s2 = (H_m2 * (same_k + mbxi.private_key)) % (mbxi.p - 1)
    r2 = pow(mbxi.g, same_k, mbxi.p)
    
    print(f"H(m2) = {H_m2}")
    print(f"r2 = {r2}")
    print(f"s2 = {s2}")
    
    # Теперь злоумышленник может восстановить закрытый ключ
    # s1 = H1*(k+b), s2 = H2*(k+b)
    # s1 - s2 = (H1 - H2)*(k+b) -> Это не дает напрямую b, но если известно k...
    # В классической атаке: s1/H1 = k+b, s2/H2 = k+b
    # Нужно найти обратный элемент к H
    try:
        H1 = signature['H_m']
        H2 = H_m2
        s1 = signature['s']
        
        # Вычисляем k + b из первого уравнения
        inv_H1 = mod_inverse(H1, mbxi.p - 1)
        k_plus_b = (s1 * inv_H1) % (mbxi.p - 1)
        
        # Восстанавливаем b
        recovered_b = (k_plus_b - same_k) % (mbxi.p - 1)
        print(f"\n⚠️ ВОССТАНОВЛЕННЫЙ ЗАКРЫТЫЙ КЛЮЧ b = {recovered_b}")
        print(f"Оригинальный b = {mbxi.private_key}")
        
        if recovered_b == mbxi.private_key:
            print("❌ КЛЮЧ УСПЕШНО СКОМПРОМЕТИРОВАН! Никогда не используйте одинаковые k!")
    except Exception as e:
        print(f"Ошибка при атаке: {e}")

if __name__ == "__main__":
    main()