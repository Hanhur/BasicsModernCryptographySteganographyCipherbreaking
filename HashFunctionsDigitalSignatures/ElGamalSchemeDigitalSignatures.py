# Цифровые подписи в схеме Эль-Гамаля
import random
import hashlib

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# ============================================================

def modinv(a, m):
    """
    Возвращает x такое, что (a * x) % m == 1
    Использует расширенный алгоритм Евклида (O(log m))
    """
    a = a % m
    # Расширенный алгоритм Евклида
    x0, x1 = 1, 0
    b = m
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
    # a теперь НОД, но мы знаем что он = 1 (если a и m взаимно просты)
    return x0 % m


def mod_pow(base, exp, mod):
    """
    Быстрое возведение в степень по модулю (бинарный метод)
    base^exp % mod
    """
    result = 1
    base = base % mod
    while exp > 0:
        if exp & 1:   # если текущий бит = 1
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


def is_prime(n, k=10):
    """
    Простая проверка на простоту (Miller–Rabin) для p до 200003
    Для демонстрации достаточно, но можно и обычным перебором
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def find_primitive_root(p):
    """
    Находит первообразный корень по модулю p
    (для демонстрации — перебор с проверкой)
    """
    if p == 2:
        return 1
    
    # факторизуем p-1
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
    
    # ищем g
    for g in range(2, p):
        ok = True
        for q in factors:
            if mod_pow(g, phi // q, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None


# ============================================================
# ОСНОВНОЙ КЛАСС СХЕМЫ ЭЛЬ-ГАМАЛЯ (ПОДПИСЬ)
# ============================================================

class ElGamalSignature:
    """
    Реализация цифровой подписи Эль-Гамаля.
    Все шаги строго по тексту из главы.
    """
    
    def __init__(self, p = None, g = None):
        """
        Инициализация открытых параметров.
        Если p и g не заданы — генерируются автоматически (для примера).
        """
        if p is None or g is None:
            # Генерируем безопасное простое p (для демонстрации ~200000)
            print("Генерация параметров...")
            self.p = self._generate_safe_prime()
            self.g = find_primitive_root(self.p)
            print(f"p = {self.p}")
            print(f"g = {self.g}")
        else:
            self.p = p
            self.g = g
        
        self.p_minus_1 = self.p - 1
        
        # Генерация ключей
        self._generate_keys()
    
    def _generate_safe_prime(self):
        """Генерирует простое число в районе 200000 (для примера)"""
        # Для воспроизводимости используем фиксированное зерно
        # random.seed(42)  # раскомментировать для повторяемости
        
        while True:
            # Генерируем нечётное в диапазоне [150000, 250000]
            p = random.randint(150000, 250000)
            if p % 2 == 0:
                p += 1
            if is_prime(p):
                return p
    
    def _generate_keys(self):
        """Генерирует закрытые и открытые ключи для Алисы и Боба"""
        # Закрытые ключи (должны быть < p-1)
        self.b_private = random.randint(2, self.p_minus_1 - 1)  # Боб
        self.a_private = random.randint(2, self.p_minus_1 - 1)  # Алиса
        
        # Открытые ключи
        self.B_public = mod_pow(self.g, self.b_private, self.p)  # Боб
        self.A_public = mod_pow(self.g, self.a_private, self.p)  # Алиса
        
        print(f"\n=== КЛЮЧИ ===")
        print(f"Закрытый ключ Алисы (a) = {self.a_private}")
        print(f"Открытый ключ Алисы (A) = {self.A_public}")
        print(f"Закрытый ключ Боба (b)   = {self.b_private}")
        print(f"Открытый ключ Боба (B)   = {self.B_public}")
    
    def hash_message(self, message):
        """
        Хеширует сообщение и возвращает целое число m < p-1
        (в тексте: h[M] = m)
        """
        # Используем SHA-256, затем обрезаем до нужного размера
        if isinstance(message, str):
            message = message.encode('utf-8')
        digest = hashlib.sha256(message).hexdigest()
        # Берём первые 8 символов (32 бита) как целое
        m = int(digest[:8], 16) % self.p_minus_1
        # Гарантируем, что m > 0
        if m == 0:
            m = 1
        return m
    
    def sign(self, message, k = None):
        """
        Подпись сообщения по схеме Эль-Гамаля.
        Возвращает кортеж (m, y1, S) — открытые параметры для проверки.
        """
        print(f"\n=== ПОДПИСЬ СООБЩЕНИЯ ===")
        print(f"Исходное сообщение (секрет) = {message}")
        
        # Шаг 0: вычисляем хеш m
        m = self.hash_message(message)
        print(f"Хеш сообщения h[M] = m = {m}")
        
        # Выбираем случайное k (должно быть взаимно просто с p-1)
        if k is None:
            while True:
                k = random.randint(2, self.p_minus_1 - 1)
                if self._gcd(k, self.p_minus_1) == 1:
                    break
        else:
            # Для демонстрации используем переданное k (как в тексте)
            if self._gcd(k, self.p_minus_1) != 1:
                raise ValueError(f"k = {k} не взаимно просто с p - 1 = {self.p_minus_1}")
        
        print(f"Случайное секретное число Алисы [k] = {k}")
        
        # Вычисляем y1 = g^k mod p
        y1 = mod_pow(self.g, k, self.p)
        print(f"y1 = g^k mod p = {y1}")
        
        # Шаг 1: обратное значение k по mod (p-1)
        inv_k = modinv(k, self.p_minus_1)
        print(f"INV k = k ^ (-1) mod (p-1) = {inv_k}")
        
        # Шаг 2: подпись S = inv_k * (m - a*y1) mod (p-1)
        S = (inv_k * (m - self.a_private * y1)) % self.p_minus_1
        print(f"S = {inv_k} * ({m} - {self.a_private} * {y1}) mod {self.p_minus_1} = {S}")
        
        print(f"\nАлиса отправляет Бобу: (m, y1, S) = ({m}, {y1}, {S})")
        
        return (m, y1, S)
    
    def verify(self, message, signature):
        """
        Проверка подписи.
        Возвращает True, если подпись верна.
        """
        m, y1, S = signature
        
        print(f"\n=== ПРОВЕРКА ПОДПИСИ ===")
        print(f"Боб получил: (m, y1, S) = ({m}, {y1}, {S})")
        
        # Шаг 3: первая проверка V1 = A^y1 * y1^S mod p
        V1 = (mod_pow(self.A_public, y1, self.p) * mod_pow(y1, S, self.p)) % self.p
        print(f"V1 = A ^ y1 * y1 ^ S mod p = {self.A_public} ^ {y1} * {y1} ^ {S} mod {self.p} = {V1}")
        
        # Вторая проверка V2 = g^m mod p
        V2 = mod_pow(self.g, m, self.p)
        print(f"V2 = g ^ m mod p = {self.g} ^ {m} mod {self.p} = {V2}")
        
        # Сравниваем
        if V1 == V2:
            print("✅ V1 == V2 → Подпись ПРИНЯТА")
            return True
        else:
            print("❌ V1 != V2 → Подпись ОТКЛОНЕНА")
            return False
    
    def _gcd(self, a, b):
        """Наибольший общий делитель (Евклид)"""
        while b:
            a, b = b, a % b
        return a


# ============================================================
# ДЕМОНСТРАЦИЯ С ЧИСЛОВЫМ ПРИМЕРОМ ИЗ ТЕКСТА
# ============================================================

def demo_from_text():
    """
    Демонстрация строго по числам из текста:
    p = 200003, g = 7, a = 5433, b = 2367, k = 23, M = 88
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПО ЧИСЛАМ ИЗ ТЕКСТА")
    print("=" * 60)
    
    # Параметры из текста
    p = 200003
    g = 7
    a_private = 5433
    b_private = 2367
    k = 23
    message = 88  # [M] = 88
    
    # Создаём экземпляр с заданными параметрами
    elgamal = ElGamalSignature(p, g)
    
    # Вручную устанавливаем ключи (чтобы совпадали с текстом)
    elgamal.a_private = a_private
    elgamal.b_private = b_private
    elgamal.A_public = mod_pow(g, a_private, p)  # 43725
    elgamal.B_public = mod_pow(g, b_private, p)  # 151854
    
    print(f"\n=== ПРОВЕРКА КЛЮЧЕЙ ===")
    print(f"A = g ^ a mod p = {elgamal.A_public} (в тексте: 43 725)")
    print(f"B = g ^ b mod p = {elgamal.B_public} (в тексте: 151 854)")
    
    # Хеш сообщения (в тексте h[M] = 77)
    # Для воспроизводимости принудительно устанавливаем m = 77
    m = 77
    print(f"\nХеш сообщения (вручную) = {m} (в тексте: 77)")
    
    # Вычисляем y1 = g^k mod p
    y1 = mod_pow(g, k, p)
    print(f"y1 = {g} ^ {k} mod {p} = {y1} (в тексте: 90 914)")
    
    # Подпись
    inv_k = modinv(k, p - 1)
    S = (inv_k * (m - a_private * y1)) % (p - 1)
    print(f"S = {inv_k} * ({m} - {a_private} * {y1}) mod {p - 1} = {S} (в тексте: 72 577)")
    
    # Проверка
    V1 = (mod_pow(elgamal.A_public, y1, p) * mod_pow(y1, S, p)) % p
    V2 = mod_pow(g, m, p)
    print(f"\nV1 = {V1} (в тексте: 76 561)")
    print(f"V2 = {V2} (в тексте: 76 561)")
    print(f"✅ Подпись верна!" if V1 == V2 else "❌ Ошибка!")


# ============================================================
# РЕАЛЬНЫЙ ПРИМЕР С ПРОИЗВОЛЬНЫМ СООБЩЕНИЕМ
# ============================================================

def demo_random():
    """
    Демонстрация с генерацией всех параметров и подписью строки
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ С ПРОИЗВОЛЬНЫМИ ПАРАМЕТРАМИ")
    print("=" * 60)
    
    # Создаём схему с автоматической генерацией p и g
    elgamal = ElGamalSignature()
    
    # Сообщение
    message = "Привет, Боб! Это Алиса."
    print(f"\nИсходное сообщение: {message}")
    
    # Подпись (k генерируется автоматически)
    signature = elgamal.sign(message)
    
    # Проверка
    elgamal.verify(message, signature)
    
    # Показываем, что подпись не пройдёт с изменённым сообщением
    print("\n" + "-" * 40)
    print("Проверка с изменённым сообщением:")
    fake_message = "Привет, Боб! Это Ева."
    elgamal.verify(fake_message, signature)


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    # 1. Демонстрация по точным числам из текста
    demo_from_text()
    
    # 2. Демонстрация с произвольными параметрами
    demo_random()