# 2. Генерация псевдослучайных последовательностей
import random
import math

def is_prime(n, k = 10):
    """Простая проверка на простоту (для демонстрации)"""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
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

def generate_prime(bits, congruent_to_3_mod_4 = False):
    """Генерация простого числа заданной битовой длины"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # Старший и младший биты = 1
        if congruent_to_3_mod_4 and n % 4 != 3:
            n = (n & ~3) | 3
        if is_prime(n):
            return n


# 1. Линейный конгруэнтный генератор (ЛКГ)
class LCG:
    """X_{i + 1} = (a * X_i + b) mod n"""
    
    def __init__(self, n, a, b, seed):
        self.n = n
        self.a = a
        self.b = b
        self.current = seed % n
    
    def next(self):
        self.current = (self.a * self.current + self.b) % self.n
        return self.current
    
    def generate_bits(self, count):
        """Генерация последовательности битов"""
        bits = []
        for _ in range(count):
            bits.append(self.next() & 1)
        return bits
    
    def generate_numbers(self, count):
        """Генерация последовательности чисел"""
        return [self.next() for _ in range(count)]


# 2. Генератор на основе RSA
class RSAGenerator:
    """X_i = X_{i - 1} ^ e mod n, выход — младшие биты"""
    
    def __init__(self, n, e, seed):
        self.n = n
        self.e = e
        self.current = seed % n
    
    def next(self):
        self.current = pow(self.current, self.e, self.n)
        return self.current
    
    def generate_bits(self, count, bits_per_output = 1):
        """
        Генерация битовой последовательности
        bits_per_output — сколько младших битов брать от каждого X_i
        """
        bits = []
        for _ in range(count):
            val = self.next()
            for _ in range(bits_per_output):
                bits.append(val & 1)
                val >>= 1
        return bits


# 3. Генератор Микали–Шнорра (Micali–Schnorr)
class MicaliSchnorr:
    """
    Установка: RSA с параметрами (n, e)
    Требование: 80e >= N, где N = битовая длина n
    r = N - k, k = floor(N * (1 - 2 / e))
    """
    
    def __init__(self, n, e, seed = None):
        self.n = n
        self.e = e
        self.N = n.bit_length()  # длина n в битах
        
        # Проверка условия
        if 80 * e < self.N:
            print(f"Предупреждение: 80e = {80 * e} < N = {self.N}, условие не выполнено")
        
        self.k = int(self.N * (1 - 2 / e))  # количество выходных битов на шаг
        self.r = self.N - self.k            # количество битов состояния
        
        # Инициализация seed (r битов)
        if seed is None:
            self.state = random.getrandbits(self.r)
        else:
            self.state = seed & ((1 << self.r) - 1)
        
        print(f"Micali-Schnorr: N = {self.N}, k = {self.k}, r = {self.r}")
    
    def next_block(self):
        """Генерация одного блока: (y = state ^ e mod n) -> (state, output)"""
        y = pow(self.state, self.e, self.n)
        
        # r старших битов y — новое состояние
        # k младших битов y — выход
        self.state = y >> self.k
        output_bits = y & ((1 << self.k) - 1)
        
        return output_bits
    
    def generate_bits(self, total_bits):
        """Генерация total_bits битов"""
        bits = []
        bits_needed = total_bits
        
        while bits_needed > 0:
            block = self.next_block()
            # Добавляем биты блока (k битов)
            block_bits = []
            for _ in range(self.k):
                block_bits.append(block & 1)
                block >>= 1
            block_bits.reverse()  # Старшие биты блока идут первыми
            bits.extend(block_bits[:bits_needed])
            bits_needed -= self.k
        
        return bits[:total_bits]
    
    def generate_bytes(self, num_bytes):
        """Генерация байтовой последовательности"""
        bits = self.generate_bits(num_bytes * 8)
        bytes_data = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
        return bytes(bytes_data)


# 4. Генератор BBS (Blum–Blum–Shub)
class BBS:
    """
    X_i = X_{i - 1} ^ 2 mod n, выход — младший бит
    p, q — простые, p ≡ q ≡ 3 mod 4
    """
    
    def __init__(self, bit_length, seed = None):
        """bit_length — битовая длина модуля n = p * q"""
        # Генерация p и q, сравнимых с 3 mod 4
        p_bits = bit_length // 2
        q_bits = bit_length - p_bits
        
        self.p = generate_prime(p_bits, congruent_to_3_mod_4 = True)
        self.q = generate_prime(q_bits, congruent_to_3_mod_4 = True)
        self.n = self.p * self.q
        
        print(f"BBS: p = {self.p} (mod4 = {self.p % 4}), q = {self.q} (mod4 = {self.q % 4}), n = {self.n}")
        
        # Выбор seed: взаимно простой с n
        if seed is None:
            while True:
                self.seed = random.randrange(1, self.n)
                if math.gcd(self.seed, self.n) == 1:
                    break
        else:
            self.seed = seed % self.n
            if math.gcd(self.seed, self.n) != 1:
                raise ValueError("seed должен быть взаимно прост с n")
        
        self.current = pow(self.seed, 2, self.n)
    
    def next_bit(self):
        self.current = pow(self.current, 2, self.n)
        return self.current & 1
    
    def generate_bits(self, count):
        return [self.next_bit() for _ in range(count)]
    
    def generate_bytes(self, num_bytes):
        bits = self.generate_bits(num_bytes * 8)
        bytes_data = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
        return bytes(bytes_data)


# Демонстрация работы
def demo():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ГЕНЕРАТОРОВ ПСЕВДОСЛУЧАЙНЫХ ПОСЛЕДОВАТЕЛЬНОСТЕЙ")
    print("=" * 60)
    
    # 1. LCG
    print("\n1. ЛИНЕЙНЫЙ КОНГРУЭНТНЫЙ ГЕНЕРАТОР (LCG)")
    print("-" * 50)
    lcg = LCG(n = 2 ** 31 - 1, a = 1103515245, b = 12345, seed = 42)
    numbers = lcg.generate_numbers(5)
    bits = lcg.generate_bits(20)
    print(f"  Числа: {numbers}")
    print(f"  Биты: {bits}")
    
    # 2. RSA-генератор
    print("\n2. RSA-ГЕНЕРАТОР")
    print("-" * 50)
    # Для демонстрации используем небольшой модуль
    rsa_gen = RSAGenerator(n = 3233, e = 17, seed = 42)
    bits = rsa_gen.generate_bits(20, bits_per_output = 1)
    print(f"  Биты (младшие биты X_i): {bits}")
    
    # 3. Micali-Schnorr
    print("\n3. ГЕНЕРАТОР МИКАЛИ–ШНОРРА")
    print("-" * 50)
    # n должно быть достаточно большим. Для демо используем 256 бит
    p = generate_prime(128)
    q = generate_prime(128)
    n_ms = p * q
    e = 3
    
    ms = MicaliSchnorr(n = n_ms, e = e, seed = random.getrandbits(64))
    bits = ms.generate_bits(40)
    print(f"  Первые 40 бит: {bits}")
    print(f"  В виде байтов (первые 8 байт): {ms.generate_bytes(8)[:8]}")
    
    # 4. BBS
    print("\n4. ГЕНЕРАТОР BBS (Blum–Blum–Shub)")
    print("-" * 50)
    bbs = BBS(bit_length = 128)
    bits = bbs.generate_bits(30)
    print(f"  Биты: {bits}")
    
    # Статистическая проверка (баланс нулей и единиц)
    print("\n" + "=" * 60)
    print("СТАТИСТИЧЕСКАЯ ПРОВЕРКА (баланс нулей и единиц)")
    print("=" * 60)
    
    for name, gen_func in [
        ("LCG", lambda: LCG(n = 2 ** 31 - 1, a = 1664525, b = 1013904223, seed = 123).generate_bits(1000)),
        ("RSA", lambda: RSAGenerator(n = 3233, e = 17, seed = 123).generate_bits(1000)),
        ("BBS", lambda: BBS(bit_length = 128).generate_bits(1000))
    ]:
        bits = gen_func()
        zeros = bits.count(0)
        ones = bits.count(1)
        print(f"{name}: нулей = {zeros}, единиц = {ones}, отношение = {ones / len(bits):.3f}")


# Пример использования каждого генератора отдельно
def example_usage():
    print("\n" + "=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 60)
    
    # LCG
    print("\n--- LCG ---")
    lcg = LCG(n = 100, a = 7, b = 3, seed = 1)
    print("Первые 10 чисел:", [lcg.next() for _ in range(10)])
    
    # RSA
    print("\n--- RSA Generator ---")
    rsa = RSAGenerator(n = 3233, e = 17, seed = 42)
    print("Первые 5 чисел X_i:", [rsa.next() for _ in range(5)])
    print("Первые 20 битов:", rsa.generate_bits(20))
    
    # Micali-Schnorr (требует больших чисел)
    print("\n--- Micali-Schnorr (256-битный модуль) ---")
    p = generate_prime(128)
    q = generate_prime(128)
    ms = MicaliSchnorr(n = p * q, e = 3, seed = 12345)
    print("Первые 64 бита:", ms.generate_bits(64))
    
    # BBS
    print("\n--- BBS Generator ---")
    bbs = BBS(bit_length = 64)
    print("Первые 20 битов:", bbs.generate_bits(20))


if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости результатов
    
    demo()
    example_usage()