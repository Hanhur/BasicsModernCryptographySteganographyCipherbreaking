# Однораундовый ZKP
import random
import hashlib

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def mod_pow(base, exp, mod):
    """Быстрое возведение в степень по модулю (аналог pow() встроенный)"""
    return pow(base, exp, mod)

def is_primitive_root(g, p):
    """Проверяет, является ли g первообразным корнем по модулю p"""
    if g % p == 0:
        return False
    factors = []
    phi = p - 1
    n = phi
    # Находим простые делители phi
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
        i += 1
    if n > 1:
        factors.append(n)
    
    # Проверяем условие: g^(phi/q) != 1 для всех простых q | phi
    for q in factors:
        if pow(g, phi // q, p) == 1:
            return False
    return True

def find_primitive_root(p):
    """Находит наименьший первообразный корень по модулю p"""
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    return None

# ---------- ОСНОВНЫЕ ФУНКЦИИ ПРОТОКОЛА ----------

def generate_parameters(bits = 8):
    """
    Генерирует простое число p и первообразный корень g.
    Для демонстрации используем маленькие числа (8 бит).
    """
    # Для простоты используем заранее известное простое число 23
    # В реальных системах нужно генерировать большое простое число
    primes = [23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    for p in primes:
        g = find_primitive_root(p)
        if g is not None:
            print(f"Параметры: p = {p}, g = {g}")
            return p, g
    
    raise RuntimeError("Не удалось найти подходящие параметры")

def setup_prover(p, g):
    """
    Этап инициализации доказывающей стороны (Пегги).
    Генерирует секретный ключ x и публичный ключ b.
    """
    # Секретный ключ (1 < x < p-1)
    x = random.randint(2, p - 2)
    # Публичный ключ: b = g^x mod p
    b = mod_pow(g, x, p)
    
    print(f"Пегги: секрет x = {x}")
    print(f"Пегги: публичный ключ b = {b}")
    return x, b

def prover_generate_proof(p, g, x, message = ""):
    """
    Пегги генерирует доказательство (один раунд, неинтерактивный).
    Возвращает (t, r) - доказательство.
    """
    # 1. Выбираем случайное k (1 < k < p-1)
    k = random.randint(2, p - 2)
    
    # 2. Вычисляем t = g^k mod p
    t = mod_pow(g, k, p)
    
    # 3. Вычисляем вызов c = H(t || message) через хеш-функцию
    # Для неинтерактивности используем хеш
    data = str(t).encode() + b":" + message.encode('utf-8')
    c_bytes = hashlib.sha256(data).digest()
    # Преобразуем хеш в число по модулю (p-1)
    c = int.from_bytes(c_bytes, 'big') % (p - 1)
    # Если c = 0, берём 1 (чтобы избежать проблем)
    if c == 0:
        c = 1
    
    # 4. Вычисляем r = k + c*x mod (p-1)
    r = (k + c * x) % (p - 1)
    
    print(f"\n--- Генерация доказательства ---")
    print(f"Пегги: k = {k}")
    print(f"Пегги: t = {t}")
    print(f"Пегги: c = H(t||message) = {c}")
    print(f"Пегги: r = k + c * x = {r}")
    
    return t, r, c  # c возвращаем только для отладки

def verifier_verify(p, g, b, t, r, message = ""):
    """
    Виктор проверяет доказательство (t, r).
    Возвращает True, если доказательство верно.
    """
    # 1. Вычисляем c = H(t || message)
    data = str(t).encode() + b":" + message.encode('utf-8')
    c_bytes = hashlib.sha256(data).digest()
    c = int.from_bytes(c_bytes, 'big') % (p - 1)
    if c == 0:
        c = 1
    
    # 2. Проверяем: g^r ≡ t * b^c (mod p)
    left = mod_pow(g, r, p)
    right = (t * mod_pow(b, c, p)) % p
    
    print(f"\n--- Проверка доказательства ---")
    print(f"Виктор: c = H(t||message) = {c}")
    print(f"Виктор: g ^ r mod p = {left}")
    print(f"Виктор: t * b ^ c mod p = {right}")
    
    return left == right

# ---------- АТАКА: ПОПЫТКА ПОДДЕЛКИ БЕЗ ЗНАНИЯ СЕКРЕТА ----------

def attacker_forge_proof(p, g, b, message = ""):
    """
    Злоумышленник пытается подделать доказательство, не зная x.
    В корректном протоколе это должно быть невозможно.
    """
    print("\n*** Попытка атаки (подделка доказательства) ***")
    
    # Атакующий выбирает случайные t и r, надеясь, что проверка пройдёт
    # Шанс успеха - 1/(p-1), что крайне мало для больших p
    t = random.randint(2, p - 2)
    r = random.randint(2, p - 2)
    
    print(f"Атакующий: выбрал случайные t = {t}, r = {r}")
    
    # Проверяем, пройдёт ли проверка
    data = str(t).encode() + b":" + message.encode('utf-8')
    c_bytes = hashlib.sha256(data).digest()
    c = int.from_bytes(c_bytes, 'big') % (p - 1)
    if c == 0:
        c = 1
    
    left = mod_pow(g, r, p)
    right = (t * mod_pow(b, c, p)) % p
    
    print(f"g ^ r mod p = {left}")
    print(f"t * b ^ c mod p = {right}")
    print(f"Результат: {'УСПЕШНО' if left == right else 'НЕ УДАЛОСЬ'}")
    
    return left == right

# ---------- ГЛАВНАЯ ФУНКЦИЯ ДЛЯ ДЕМОНСТРАЦИИ ----------

def main():
    print("=" * 60)
    print("ОДНОРАУНДОВЫЙ ZKP (схема с хеш-функцией)")
    print("=" * 60)
    
    # 1. Генерация параметров
    print("\n[1] Генерация параметров системы")
    p, g = generate_parameters(bits = 8)
    
    # 2. Инициализация Пегги
    print("\n[2] Инициализация Пегги")
    x, b = setup_prover(p, g)
    
    # 3. Сообщение (опционально) - теперь строка
    message = "Привет, это доказательство!"
    print(f"\nСообщение: {message}")
    
    # 4. Пегги генерирует доказательство
    print("\n[3] Пегги генерирует доказательство")
    t, r, c = prover_generate_proof(p, g, x, message)
    print(f"Доказательство: (t = {t}, r = {r})")
    
    # 5. Виктор проверяет доказательство
    print("\n[4] Виктор проверяет доказательство")
    is_valid = verifier_verify(p, g, b, t, r, message)
    print(f"\nРЕЗУЛЬТАТ: {'✅ ДОКАЗАТЕЛЬСТВО ПРИНЯТО' if is_valid else '❌ ДОКАЗАТЕЛЬСТВО ОТКЛОНЕНО'}")
    
    # 6. Проверка подделки (демонстрация безопасности)
    print("\n[5] Демонстрация безопасности (попытка подделки)")
    attack_success = attacker_forge_proof(p, g, b, message)
    print(f"\nАтака {'✅ УСПЕШНА' if attack_success else '❌ НЕ УДАЛАСЬ'}")
    
    # 7. Дополнительная демонстрация: разные случайные значения дают разные доказательства
    print("\n[6] Демонстрация: новое доказательство с другим k")
    t2, r2, c2 = prover_generate_proof(p, g, x, message)
    is_valid2 = verifier_verify(p, g, b, t2, r2, message)
    print(f"\nВторое доказательство: (t = {t2}, r = {r2})")
    print(f"Результат: {'✅ ПРИНЯТО' if is_valid2 else '❌ ОТКЛОНЕНО'}")
    
    print("\n" + "=" * 60)
    print("Программа завершена.")

if __name__ == "__main__":
    main()