# Демонстрация работы неинтерактивного протокола ZKP
import random
import math

# ============================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# ============================================

def gcd(a, b):
    """Алгоритм Евклида для НОД"""
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """
    Расширенный алгоритм Евклида для нахождения
    мультипликативной инверсии a ^ (-1) mod m
    """
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def is_prime(n, k = 5):
    """Простая проверка на простоту (метод Ферма)"""
    if n < 2:
        return False
    for _ in range(k):
        a = random.randint(2, n - 2)
        if pow(a, n - 1, n) != 1:
            return False
    return True

def generate_rsa_keys(bits = 8):
    """
    Генерация RSA ключей (маленькие числа для демонстрации)
    bits = количество бит для простых чисел
    """
    # Генерируем два простых числа p и q
    while True:
        p = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(p):
            break
    
    while True:
        q = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(q) and q != p:
            break
    
    N = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (обычно 65537, но для демонстрации возьмём небольшое)
    e = 17
    while gcd(e, phi) != 1:
        e += 2
    
    # Вычисляем d
    d = mod_inverse(e, phi)
    
    return {
        'public': (e, N),
        'private': d,
        'p': p,
        'q': q,
        'phi': phi
    }

# ============================================
# 2. ОСНОВНОЙ ПРОТОКОЛ ZKP (ЧЕСТНАЯ ПЕГГИ)
# ============================================

class HonestProver:
    """Честный доказывающий, который знает секрет m"""
    
    def __init__(self, rsa_keys):
        self.e, self.N = rsa_keys['public']
        self.d = rsa_keys['private']
        self.keys = rsa_keys
    
    def encrypt(self, m):
        """Шифрование сообщения: c = m ^ e mod N"""
        return pow(m, self.e, self.N)
    
    def generate_proof(self, m):
        """
        Генерация доказательства (x1, x2) для неинтерактивного ZKP
        x1 * x2 ≡ c (mod N), где c = m ^ e mod N
        """
        # 1. Выбираем случайное r1 (взаимно простое с N)
        while True:
            r1 = random.randint(2, self.N - 1)
            if gcd(r1, self.N) == 1:
                break
        
        # 2. Вычисляем x1 = r1^e mod N
        x1 = pow(r1, self.e, self.N)
        
        # 3. Вычисляем x2 = (m * r1^(-1))^e mod N
        #    Сначала находим инверсию r1 по модулю N
        r1_inv = mod_inverse(r1, self.N)
        if r1_inv is None:
            raise ValueError("Не удалось найти инверсию для r1")
        
        #    Затем вычисляем x2
        x2 = pow((m * r1_inv) % self.N, self.e, self.N)
        
        # 4. Вычисляем c (шифротекст) для проверки
        c = self.encrypt(m)
        
        return {
            'x1': x1,
            'x2': x2,
            'c': c,
            'r1': r1  # Сохраняем только для демонстрации (в реальном протоколе не передаётся)
        }

class Verifier:
    """Проверяющий (Виктор)"""
    
    def __init__(self, rsa_keys):
        self.e, self.N = rsa_keys['public']
    
    def verify(self, proof):
        """
        Проверка доказательства:
        x1 * x2 ≡ c (mod N)
        """
        x1 = proof['x1']
        x2 = proof['x2']
        c = proof['c']
        
        left_side = (x1 * x2) % self.N
        right_side = c % self.N
        
        is_valid = (left_side == right_side)
        
        return {
            'valid': is_valid,
            'left_side': left_side,
            'right_side': right_side
        }

# ============================================
# 3. АТАКА (НЕЧЕСТНАЯ ЕВА)
# ============================================

class Attacker:
    """
    Злоумышленник, который НЕ знает m,
    но может подделать доказательство
    """
    
    def __init__(self, rsa_keys):
        self.e, self.N = rsa_keys['public']
    
    def forge_proof(self, c):
        """
        Создание фальшивого доказательства,
        которое проходит проверку, но не требует знания m
        """
        # 1. Выбираем произвольное t
        while True:
            t = random.randint(2, self.N - 1)
            if gcd(t, self.N) == 1:
                break
        
        # 2. Устанавливаем x1 = t
        x1 = t
        
        # 3. Вычисляем x2 = c * t^(-1) mod N
        t_inv = mod_inverse(t, self.N)
        if t_inv is None:
            raise ValueError("Не удалось найти инверсию для t")
        
        x2 = (c * t_inv) % self.N
        
        return {
            'x1': x1,
            'x2': x2,
            'c': c,
            't': t  # Сохраняем только для демонстрации
        }

# ============================================
# 4. ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================

def main():
    print("=" * 60)
    print("НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ ZKP НА ОСНОВЕ RSA")
    print("=" * 60)
    
    # 1. Генерация ключей
    print("\n[1] Генерация RSA ключей...")
    keys = generate_rsa_keys(bits = 6)  # Маленькие биты для наглядности
    e, N = keys['public']
    print(f"    Публичный ключ: e = {e}, N = {N}")
    print(f"    Приватный ключ: d = {keys['private']}")
    print(f"    p = {keys['p']}, q = {keys['q']}, phi = {keys['phi']}")
    
    # 2. Честный протокол
    print("\n" + "=" * 60)
    print("[2] ЧЕСТНАЯ ПЕГГИ (знает секрет)")
    print("=" * 60)
    
    m = 42  # Секретное сообщение
    print(f"    Секретное сообщение m = {m}")
    
    prover = HonestProver(keys)
    verifier = Verifier(keys)
    
    # Генерируем доказательство
    proof = prover.generate_proof(m)
    print(f"\n    Доказательство:")
    print(f"      x1 = {proof['x1']}")
    print(f"      x2 = {proof['x2']}")
    print(f"      c  = {proof['c']} (шифротекст)")
    print(f"      r1 = {proof['r1']} (секретная соль, не передаётся)")
    
    # Проверяем
    result = verifier.verify(proof)
    print(f"\n    Проверка Виктора:")
    print(f"      x1 * x2 mod N = {result['left_side']}")
    print(f"      c mod N       = {result['right_side']}")
    print(f"      РЕЗУЛЬТАТ: {'✓ ПРИНЯТО' if result['valid'] else '✗ ОТКЛОНЕНО'}")
    
    # Демонстрация умножения
    print(f"\n    Проверка умножения:")
    print(f"      {proof['x1']} * {proof['x2']} ≡ {proof['c']} (mod {N})")
    print(f"      {(proof['x1'] * proof['x2']) % N} ≡ {proof['c'] % N} (mod {N})")
    
    # 3. Атака
    print("\n" + "=" * 60)
    print("[3] АТАКА (НЕЧЕСТНАЯ ЕВА НЕ ЗНАЕТ m)")
    print("=" * 60)
    
    attacker = Attacker(keys)
    
    # Ева перехватывает шифротекст c
    c = proof['c']
    print(f"    Ева перехватила шифротекст c = {c}")
    print(f"    Ева НЕ знает m ({m})")
    
    # Создаёт фальшивое доказательство
    fake_proof = attacker.forge_proof(c)
    print(f"\n    Фальшивое доказательство Евы:")
    print(f"      x1' = {fake_proof['x1']}")
    print(f"      x2' = {fake_proof['x2']}")
    print(f"      c'  = {fake_proof['c']}")
    print(f"      t   = {fake_proof['t']} (секретный параметр Евы)")
    
    # Проверяем фальшивку
    fake_result = verifier.verify(fake_proof)
    print(f"\n    Проверка Виктором фальшивки:")
    print(f"      x1' * x2' mod N = {fake_result['left_side']}")
    print(f"      c' mod N        = {fake_result['right_side']}")
    print(f"      РЕЗУЛЬТАТ: {'✓ ПРИНЯТО' if fake_result['valid'] else '✗ ОТКЛОНЕНО'}")
    
    # 4. Объяснение атаки
    print("\n" + "=" * 60)
    print("[4] ОБЪЯСНЕНИЕ АТАКИ")
    print("=" * 60)
    print(f"""
    Ева выбрала случайное t = {fake_proof['t']}
    Затем она вычислила:
      x1' = t = {fake_proof['x1']}
      x2' = c * t ^ (-1) mod N = {fake_proof['x2']}
    
    При проверке:
      x1' * x2' = t * (c * t ^ (-1)) = c (mod N)
    
    Таким образом, Ева успешно обманула Виктора,
    НЕ ЗНАЯ секретного сообщения m = {m}!
    
    ВЫВОД: Протокол проверяет только соотношение x1 * x2 ≡ c,
    но НЕ ДОКАЗЫВАЕТ, что доказывающий знает m.
    """)
    
    # 5. Корректное умножение для честного протокола
    print("\n" + "=" * 60)
    print("[5] ПОЧЕМУ ЧЕСТНАЯ ПЕГГИ ПРОХОДИТ ПРОВЕРКУ")
    print("=" * 60)
    print(f"""
    Пегги выбрала r1 = {proof['r1']}
    Она вычислила:
      x1 = r1 ^ e mod N = {proof['x1']}
      x2 = (m * r1 ^ (-1)) ^ e mod N = {proof['x2']}
    
    При перемножении:
      x1 * x2 = r1 ^ e * (m * r1 ^ (-1)) ^ e = r1 ^ e * m ^ e * (r1 ^ (-1)) ^ e = m ^ e * (r1 * r1 ^ (-1)) ^ e = m ^ e * 1 ^ e = m ^ e ≡ c (mod N)
    
    Это математически верно, но не защищает от подделки!
    """)
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)

if __name__ == "__main__":
    main()