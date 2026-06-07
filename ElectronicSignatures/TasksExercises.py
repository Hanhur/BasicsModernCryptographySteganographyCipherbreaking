# Задачи и упражнения
import random
import hashlib
import math

def generate_prime(bits = 20):
    """Генерация простого числа (для демонстрации — маленького)."""
    while True:
        n = random.getrandbits(bits)
        n |= 1  # делаем нечётным
        if n > 1 and all(n % i != 0 for i in range(2, int(n ** 0.5) + 1)):
            return n

def find_primitive_root(p):
    """Находит порождающий элемент мультипликативной группы Z_p ^ *."""
    if p == 2:
        return 1
    # Факторизуем p - 1
    phi = p - 1
    factors = []
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

    for g in range(2, p):
        ok = True
        for q in factors:
            if pow(g, phi // q, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None

def hash_to_zp(message, p):
    """Хэширует сообщение в число по модулю p."""
    h = hashlib.sha256(message.encode()).hexdigest()
    h_int = int(h, 16) % p
    # Обеспечиваем gcd(h, p - 1) = 1
    while math.gcd(h_int, p - 1) != 1:
        # Добавляем небольшое смещение (в реальности — более умная коррекция)
        h_int = (h_int + 1) % p
        if h_int == 0:
            h_int = 1
    return h_int

# ------------------------------------------------------------
# 1. Генерация параметров схемы
p = generate_prime(12)  # небольшое простое для наглядности
while p < 100:
    p = generate_prime(12)

g = find_primitive_root(p)
if g is None:
    raise ValueError("Не удалось найти порождающий элемент")

print("=== Параметры схемы ===")
print(f"p = {p}")
print(f"g = {g}")

# Секретный ключ пользователя
a = random.randint(2, p - 2)
y = pow(g, a, p)

print(f"Открытый ключ y = {y}")
print(f"Секретный ключ a = {a}")

# ------------------------------------------------------------
# 2. Сообщение
message = "Важное сообщение"
h = hash_to_zp(message, p)
print(f"\n=== Сообщение: {message} ===")
print(f"Хеш h = {h}, gcd(h, p - 1) = {math.gcd(h, p - 1)}")

# ------------------------------------------------------------
# 3. Честная подпись (используя секрет a)
h_inv = pow(h, -1, p - 1)  # обратное по модулю p - 1
z = (h_inv * a) % (p - 1)
signature_honest = pow(g, z, p)

print(f"\n=== Честная подпись ===")
print(f"z = {z}")
print(f"Подпись s = g ^ z mod p = {signature_honest}")

# Проверка честной подписи: s ^ h == y ?
if pow(signature_honest, h, p) == y:
    print("Проверка честной подписи: УСПЕШНО")
else:
    print("Проверка честной подписи: ОШИБКА")

# ------------------------------------------------------------
# 4. Атака: злоумышленник создаёт подпись без знания a
h_inv_attacker = pow(h, -1, p - 1)  # то же самое, что и выше — знает только h
signature_forged = pow(y, h_inv_attacker, p)

print(f"\n=== Поддельная подпись (злоумышленник) ===")
print(f"Вычислено: подпись = y ^ {h_inv} mod p = {signature_forged}")

# Проверка поддельной подписи
if pow(signature_forged, h, p) == y:
    print("Проверка поддельной подписи: УСПЕШНО (подделка прошла!)")
else:
    print("Проверка поддельной подписи: НЕ УСПЕШНО")

# ------------------------------------------------------------
# 5. Демонстрация, что подписи совпадают
print(f"\n=== Сравнение ===")
print(f"Честная подпись: {signature_honest}")
print(f"Поддельная подпись: {signature_forged}")
if signature_honest == signature_forged:
    print("Подписи одинаковы — злоумышленник создал точную копию без знания секрета.")
else:
    print("Подписи различаются — такого не должно было случиться в теории (проверьте реализацию).")