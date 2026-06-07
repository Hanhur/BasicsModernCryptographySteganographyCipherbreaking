# 3. Доказательства с нулевым разглашением
import random
import math

# ---------- 1. Вспомогательные функции ----------
def is_prime(n, k = 10):
    """Простая проверка на простоту (тест Миллера–Рабина)"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    # записываем n - 1 = d * 2 ^ s
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

def generate_prime(bits = 8):
    """Генерирует простое число заданной длины (для демонстрации)"""
    while True:
        p = random.randrange(2 ** (bits - 1), 2 ** bits)
        if p % 2 == 0:
            p += 1
        if is_prime(p):
            return p

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def modinv(a, m):
    """Обратное по модулю (расширенный алгоритм Евклида)"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

# ---------- 2. Центр T (генерирует n = p * q) ----------
class TrustedCenter:
    def __init__(self, bits = 8):
        self.p = generate_prime(bits)
        self.q = generate_prime(bits)
        while self.p == self.q:
            self.q = generate_prime(bits)
        self.n = self.p * self.q
        print(f"[Центр] Сгенерировано n = {self.n} (p = {self.p}, q = {self.q})")

    def get_n(self):
        return self.n

# ---------- 3. Пользователь A (доказывающий) ----------
class ProverA:
    def __init__(self, center):
        self.n = center.get_n()
        # Выбираем секрет s: 1 < s < n, gcd(s, n) = 1
        while True:
            self.s = random.randrange(2, self.n)
            if gcd(self.s, self.n) == 1:
                break
        self.v = (self.s * self.s) % self.n  # открытое значение
        print(f"[A] Секрет s = {self.s}, открытое v = {self.v}")

    def get_public_v(self):
        return self.v

    def step1_send_x(self):
        """Раунд 1: выбираем случайное r, вычисляем x = r ^ 2 mod n"""
        self.r = random.randrange(1, self.n)
        while gcd(self.r, self.n) != 1:
            self.r = random.randrange(1, self.n)
        self.x = (self.r * self.r) % self.n
        print(f"  [A] -> B: x = {self.x}")
        return self.x

    def step3_send_y(self, e):
        """Раунд 3: вычисляем y = r * s ^ e mod n"""
        if e == 0:
            y = self.r % self.n
        else:  # e == 1
            y = (self.r * self.s) % self.n
        print(f"  [A] -> B: y = {y}")
        return y

# ---------- 4. Пользователь B (проверяющий) ----------
class VerifierB:
    def __init__(self, center, public_v):
        self.n = center.get_n()
        self.v = public_v

    def step2_send_e(self):
        """Раунд 2: случайный бит e ∈ {0, 1}"""
        self.e = random.choice([0, 1])
        print(f"  [B] -> A: e = {self.e}")
        return self.e

    def verify(self, x, y, e):
        """Проверка: y ^ 2 ≡ x * v ^ e (mod n)"""
        if y == 0:
            print("  [B] Ошибка: y = 0, отвергаем")
            return False
        left = (y * y) % self.n
        right = (x * pow(self.v, e, self.n)) % self.n
        ok = (left == right)
        print(f"  [B] Проверка: {left} == {right} -> {'✓' if ok else '✗'}")
        return ok

# ---------- 5. Злоумышленник C (пытается выдать себя за A) ----------
class AttackerC:
    def __init__(self, center, public_v):
        self.n = center.get_n()
        self.v = public_v
        # Не знает s

    def step1_send_x_attack(self, guessed_e):
        """Готовит x в зависимости от угаданного e"""
        self.guessed_e = guessed_e
        self.r_attack = random.randrange(1, self.n)
        while gcd(self.r_attack, self.n) != 1:
            self.r_attack = random.randrange(1, self.n)

        if guessed_e == 0:
            # e = 0: x = r ^ 2
            self.x = (self.r_attack * self.r_attack) % self.n
        else:
            # e = 1: x = r ^ 2 * v ^ {-1}
            v_inv = modinv(self.v, self.n)
            self.x = (self.r_attack * self.r_attack * v_inv) % self.n
        print(f"  [C] -> B: x = {self.x} (угадал e = {guessed_e})")
        return self.x

    def step3_send_y_attack(self, actual_e):
        """Отправляет y в зависимости от того, угадали ли e"""
        if actual_e == self.guessed_e:
            # Угадали: отправляем r
            y = self.r_attack % self.n
            print(f"  [C] -> B: y = {y} (успешно, угадал)")
            return y
        else:
            # Не угадали: честно ответить не можем
            print(f"  [C] -> B: не может ответить правильно (не угадал e = {actual_e})")
            # Возвращаем случайное число, но проверка провалится
            return random.randrange(1, self.n)

# ---------- 6. Симулятор для доказательства нулевого разглашения ----------
class SimulatorZK:
    """Симулятор, не знающий s, но создающий неотличимый диалог"""
    def __init__(self, center, public_v):
        self.n = center.get_n()
        self.v = public_v

    def simulate_one_round(self):
        """Создаёт тройку (x, e, y), не зная s"""
        # Угадываем e заранее
        e_sim = random.choice([0, 1])
        y_sim = random.randrange(1, self.n)
        while gcd(y_sim, self.n) != 1:
            y_sim = random.randrange(1, self.n)

        if e_sim == 0:
            x_sim = (y_sim * y_sim) % self.n
        else:
            v_inv = modinv(self.v, self.n)
            x_sim = (y_sim * y_sim * v_inv) % self.n

        return x_sim, e_sim, y_sim

# ---------- 7. Демонстрация ----------
def run_honest_protocol(rounds = 3):
    print("\n" + "=" * 50)
    print("ЧЕСТНЫЙ ПРОТОКОЛ (A знает s)")
    center = TrustedCenter(bits = 6)   # маленькие числа для наглядности
    prover = ProverA(center)
    verifier = VerifierB(center, prover.get_public_v())

    for rnd in range(1, rounds + 1):
        print(f"\n--- Раунд {rnd} ---")
        x = prover.step1_send_x()
        e = verifier.step2_send_e()
        y = prover.step3_send_y(e)
        ok = verifier.verify(x, y, e)
        if not ok:
            print("Идентификация НЕ удалась (не должно случиться для честного A)")
            return False
    print(f"\n✓ Идентификация успешна за {rounds} раундов")
    return True

def run_attack(rounds = 3):
    print("\n" + "=" * 50)
    print("ПОПЫТКА ОБМАНА (C не знает s)")
    center = TrustedCenter(bits = 6)
    # C узнаёт открытое v пользователя A (например, из реестра центра)
    # Создадим реального A только чтобы получить v
    real_A = ProverA(center)
    public_v = real_A.get_public_v()
    attacker = AttackerC(center, public_v)
    verifier = VerifierB(center, public_v)

    success_count = 0
    for rnd in range(1, rounds + 1):
        print(f"\n--- Раунд {rnd} ---")
        guessed_e = random.choice([0, 1])
        x = attacker.step1_send_x_attack(guessed_e)
        e = verifier.step2_send_e()
        y = attacker.step3_send_y_attack(e)
        ok = verifier.verify(x, y, e)
        if ok:
            success_count += 1
            print(f"  Раунд {rnd}: УСПЕХ обмана")
        else:
            print(f"  Раунд {rnd}: ПРОВАЛ обмана")
    print(f"\nРезультат: {success_count}/{rounds} успешных обманов (вероятность ~1/2^?)")
    return success_count

def run_simulation_zk():
    print("\n" + "=" * 50)
    print("СИМУЛЯЦИЯ ДЛЯ НУЛЕВОГО РАЗГЛАШЕНИЯ (без секрета s)")
    center = TrustedCenter(bits = 6)
    real_A = ProverA(center)
    public_v = real_A.get_public_v()
    simulator = SimulatorZK(center, public_v)

    print("Симулятор генерирует диалоги, не зная s:")
    for i in range(3):
        x, e, y = simulator.simulate_one_round()
        print(f"  Диалог {i + 1}: (x = {x}, e = {e}, y = {y})")
        # Проверим, что такой диалог прошёл бы проверку
        verifier = VerifierB(center, public_v)
        ok = verifier.verify(x, y, e)
        print(f"    Проверка: {'✓' if ok else '✗'}")

if __name__ == "__main__":
    random.seed(42)  # для воспроизводимости, можно убрать
    run_honest_protocol(rounds = 3)
    run_attack(rounds = 5)
    run_simulation_zk()