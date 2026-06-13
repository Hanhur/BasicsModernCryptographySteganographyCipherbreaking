# 4. Master Card
import random
import hashlib
import math

# ---------- Вспомогательные функции ----------
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def gcd(a, b):
    return math.gcd(a, b)

# ---------- 1. Банк создаёт RSA-ключи ----------
def bank_keygen(bits = 512):
    # Для демонстрации используем маленькие простые числа (в реальности bits >= 1024)
    # Здесь для наглядности возьмём небольшие p, q (в учебных целях)
    p = 61
    q = 53
    # При желании можно сгенерировать случайные:
    # p = random.getrandbits(bits//2) | 1
    # q = random.getrandbits(bits//2) | 1
    # ... но для простоты оставим фиксированные
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537  # стандартная открытая экспонента
    if gcd(e, phi) != 1:
        e = 17  # запасной вариант
    d = modinv(e, phi)
    return (n, e, d)

# Односторонняя функция f: Zn -> Zn (хеш + приведение к числу)
def f_hash(x, n):
    h = hashlib.sha256(str(x).encode()).hexdigest()
    # переводим хеш в целое число и берём по модулю n
    return int(h, 16) % n

# ---------- 2. Клиент создаёт "полуфабрикат" карточки ----------
def client_blind_request(x, n, e):
    # x - номер купюры (случайное число из Zn)
    fx = f_hash(x, n)

    # Выбираем r взаимно простое с n
    while True:
        r = random.randint(2, n - 1)
        if gcd(r, n) == 1:
            break

    # Затемняющий множитель r^e mod n
    blinding_factor = pow(r, e, n)
    y = (fx * blinding_factor) % n
    return y, r, fx

# ---------- 3. Банк подписывает слепое сообщение ----------
def bank_sign(y, d, n):
    # z = y^d mod n
    z = pow(y, d, n)
    return z

# ---------- 4. Клиент снимает затемнение ----------
def client_unblind(z, r, n):
    r_inv = modinv(r, n)
    signature = (z * r_inv) % n   # это f(x)^d mod n
    return signature

# ---------- 5. Продавец проверяет подпись (автономно) ----------
def verify_card(x, signature, n, e):
    fx = f_hash(x, n)
    # Проверяем (signature)^e ≡ f(x) (mod n)
    return pow(signature, e, n) == fx

# ---------- 6. Банк проверяет, не тратилась ли карточка (база данных) ----------
spent_db = set()

def bank_check_and_spend(x, signature, n, e, amount, balance_limit):
    # Сначала проверяем подпись (повторно, для надёжности)
    if not verify_card(x, signature, n, e):
        return False, "Неверная подпись карточки"

    if x in spent_db:
        return False, "Карточка уже была использована (двойная трата)"

    # В реальности здесь был бы учёт остатка средств.
    # В простейшей модели - карточка на фиксированный номинал.
    if amount > balance_limit:
        return False, "Недостаточно средств"

    spent_db.add(x)
    return True, "Платёж одобрен"

# ---------- Демонстрация работы протокола ----------
if __name__ == "__main__":
    print("=== Банк генерирует RSA-ключи ===")
    n, e, d = bank_keygen()
    print(f"Публичный ключ: n = {n}, e = {e}")
    print(f"Секретный ключ d = {d}\n")

    print("=== Клиент A выбирает номер купюры ===")
    x = random.randint(2, n - 1)
    print(f"x (номер купюры) = {x}")

    print("\n=== Клиент создаёт слепое сообщение ===")
    y, r, fx = client_blind_request(x, n, e)
    print(f"f(x) = {fx}")
    print(f"r = {r}")
    print(f"Слепое сообщение y = {y}")

    print("\n=== Банк подписывает слепое сообщение ===")
    z = bank_sign(y, d, n)
    print(f"Подпись банка на слепом сообщении: z = {z}")

    print("\n=== Клиент снимает затемнение ===")
    signature = client_unblind(z, r, n)
    print(f"Итоговая подпись f(x) ^ d = {signature}")

    print("\n=== Продавец проверяет карточку (без банка) ===")
    if verify_card(x, signature, n, e):
        print("✅ Автономная проверка подписи: УСПЕШНО")
    else:
        print("❌ Автономная проверка подписи: НЕУДАЧА")

    print("\n=== Банк проверяет достаточность средств и отсутствие двойной траты ===")
    # Предположим, номинал карточки = 100
    success, msg = bank_check_and_spend(x, signature, n, e, amount = 50, balance_limit = 100)
    print(msg)

    print("\n=== Пытаемся потратить ту же карточку снова ===")
    success2, msg2 = bank_check_and_spend(x, signature, n, e, amount = 30, balance_limit = 100)
    print(msg2)

    print("\n=== База потраченных номеров ===")
    print(f"Потраченные x: {spent_db}")