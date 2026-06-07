# 5. Схема базовой электронной подписи Эль Гамаля
import random
import math

def egcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y), где a * x + b * y = g = gcd(a, b)"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, x1, y1 = egcd(b % a, a)
        return (g, y1 - (b // a) * x1, x1)

def modinv(a, m):
    """Обратное число по модулю m, если существует"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception(f"Обратного элемента для {a} mod {m} не существует")
    return x % m

def generate_keys(p, g, a = None):
    """
    Генерация ключей для схемы Эль-Гамаля.
    p - простое число
    g - порождающий элемент мультипликативной группы Zp*
    a - секретный ключ (если None, выбирается случайно)
    Возвращает: (public_key, private_key)
    public_key = (p, g, y)
    private_key = a
    """
    if a is None:
        a = random.randint(1, p - 2)
    y = pow(g, a, p)
    return (p, g, y), a

def hash_message(message, p):
    """
    Хеш-функция h: {0, 1} * -> Zp
    В реальных системах используется криптостойкая хэш-функция.
    Здесь для демонстрации: интерпретируем бинарную строку как число в двоичной системе.
    """
    if isinstance(message, str):
        # Если сообщение — строка из '0' и '1'
        if all(c in '01' for c in message):
            return int(message, 2) % p
        else:
            # Преобразуем строку в битовую последовательность (ASCII)
            bits = ''.join(format(ord(c), '08b') for c in message)
            return int(bits, 2) % p
    else:
        # Если уже число
        return message % p

def sign(message, private_key, public_key, k = None):
    """
    Создание подписи Эль-Гамаля.
    public_key = (p, g, y)
    private_key = a
    message - бинарная последовательность или строка/число
    k - сессионный ключ (если None, выбирается случайно)
    Возвращает: (r, s)
    """
    p, g, y = public_key
    a = private_key
    
    # 1. Вычисляем h(m)
    hm = hash_message(message, p)
    
    # 2. Выбираем k: 1 <= k <= p - 2, gcd(k, p - 1) = 1
    if k is None:
        while True:
            k = random.randint(1, p - 2)
            if math.gcd(k, p - 1) == 1:
                break
    else:
        if not (1 <= k <= p - 2 and math.gcd(k, p - 1) == 1):
            raise ValueError(f"k = {k} не удовлетворяет условиям: 1 <= k <= {p - 2} и gcd(k, p - 1) = 1")
    
    # 3. Вычисляем l = k ^ {-1} mod (p - 1)
    l = modinv(k, p - 1)
    
    # 4. Первый элемент подписи r = g ^ k mod p
    r = pow(g, k, p)
    
    # 5. Второй элемент подписи s = l * (h(m) - a * r) mod (p - 1)
    # Приводим к стандартному имени 0 <= s <= p - 2
    s = (l * (hm - a * r)) % (p - 1)
    
    return (r, s)

def verify(message, signature, public_key):
    """
    Проверка подписи Эль-Гамаля.
    public_key = (p, g, y)
    signature = (r, s)
    Возвращает: True, если подпись верна, иначе False
    """
    p, g, y = public_key
    r, s = signature
    
    # Проверка диапазонов
    if not (1 <= r <= p-1):
        print(f"Ошибка: r = {r} не в диапазоне [1, {p - 1}]")
        return False
    if not (0 <= s <= p-2):
        print(f"Ошибка: s = {s} не в диапазоне [0, {p - 2}]")
        return False
    
    # Вычисляем v1 = y ^ r * r ^ s mod p
    v1 = (pow(y, r, p) * pow(r, s, p)) % p
    
    # Вычисляем h(m) и v2 = g ^ {h(m)} mod p
    hm = hash_message(message, p)
    v2 = pow(g, hm, p)
    
    return v1 == v2

def recover_private_key_from_k(r, s, message, k, public_key):
    """
    Восстановление долгосрочного ключа a из k (демонстрация слабости).
    """
    p, g, y = public_key
    hm = hash_message(message, p)
    # ks = k * s ≡ h(m) - a * r (mod p - 1)
    # a * r ≡ h(m) - k * s (mod p - 1)
    # a ≡ (h(m) - k * s) * r ^ {-1} (mod p - 1)
    ks = (k * s) % (p - 1)
    rhs = (hm - ks) % (p - 1)
    r_inv = modinv(r % (p - 1), p - 1)
    a_recovered = (rhs * r_inv) % (p - 1)
    return a_recovered

# ==================== ДЕМОНСТРАЦИЯ ====================

def demo_from_text():
    """Пример 62 из текста: p = 31, g = 3, a = 5, m = 1011 (11), k = 7"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРИМЕРА ИЗ ТЕКСТА")
    print("=" * 60)
    
    p = 31
    g = 3
    a = 5
    y = pow(g, a, p)  # 3 ^ 5 mod 31 = 26
    
    public_key = (p, g, y)
    private_key = a
    
    print(f"p = {p}, g = {g}, a = {a}")
    print(f"Открытый ключ: y = {y}")
    
    # Сообщение: бинарная последовательность "1011"
    message_bin = "1011"
    hm = hash_message(message_bin, p)
    print(f"Сообщение m = '{message_bin}' -> h(m) = {hm}")
    
    k = 7
    print(f"Сессионный ключ k = {k}")
    
    # Подпись
    r, s = sign(message_bin, private_key, public_key, k = k)
    print(f"Подпись: r = {r}, s = {s}")
    
    # Проверка
    valid = verify(message_bin, (r, s), public_key)
    print(f"Результат проверки: {'ВЕРНА' if valid else 'НЕВЕРНА'}")
    
    # Проверка с неправильным сообщением
    print("\nПроверка с изменённым сообщением '1010':")
    valid2 = verify("1010", (r, s), public_key)
    print(f"Результат: {'ВЕРНА' if valid2 else 'НЕВЕРНА'} (ожидалось НЕВЕРНА)")
    print()

def demo_weak_k_attack():
    """Демонстрация: если k маленькое, злоумышленник восстанавливает a"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ СЛАБОСТИ: ВОССТАНОВЛЕНИЕ КЛЮЧА a ПРИ МАЛОМ k")
    print("=" * 60)
    
    # Используем небольшие числа для наглядности
    p = 31
    g = 3
    a = 5  # секретный ключ
    public_key, _ = generate_keys(p, g, a)
    p, g, y = public_key
    
    # Злоумышленник знает открытые данные
    print(f"Открытые данные: p = {p}, g = {g}, y = {y}")
    print(f"Секретный ключ a = {a} (неизвестен злоумышленнику)")
    
    message = "1011"
    # Слабое k: маленькое значение, легко перебрать
    k_weak = 2
    while math.gcd(k_weak, p - 1) != 1:
        k_weak += 1
    
    r, s = sign(message, a, public_key, k = k_weak)
    print(f"\nПерехвачены: сообщение='{message}', подпись r = {r}, s = {s}")
    print(f"Сессионный ключ k = {k_weak} (подобран перебором, т.к. r = g ^ k мал)")
    
    # Восстанавливаем a
    a_recovered = recover_private_key_from_k(r, s, message, k_weak, public_key)
    print(f"\nВосстановленный долгосрочный ключ a' = {a_recovered}")
    print(f"Исходный ключ a = {a}")
    
    if a_recovered == a:
        print("УСПЕХ: злоумышленник восстановил секретный ключ!")
        # Теперь можно подделать любую подпись
        fake_message = "11111"
        r_fake, s_fake = sign(fake_message, a_recovered, public_key)
        print(f"Поддельная подпись для '{fake_message}': ({r_fake}, {s_fake})")
        print(f"Проверка поддельной подписи: {verify(fake_message, (r_fake, s_fake), public_key)}")
    else:
        print("Не удалось восстановить (такое возможно только при малых p)")

def demo_correct_usage():
    """Демонстрация корректной работы на больших параметрах"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НА БОЛЬШИХ ПАРАМЕТРАХ")
    print("=" * 60)
    
    # Безопасные параметры (для демонстрации используем умеренно большое p)
    # В реальности p должно быть ~2048 бит
    p = 257  # простое число
    # Находим порождающий элемент (упрощённо: проверяем, что порядок = p - 1)
    g = 5  # 5 — порождающий для p = 257 (проверено)
    
    # Генерируем ключи
    a = random.randint(2, p - 2)
    public_key, private_key = generate_keys(p, g, a)
    p, g, y = public_key
    
    print(f"p = {p} (простое)")
    print(f"g = {g} (порождающий элемент)")
    print(f"Секретный ключ a = {private_key}")
    print(f"Открытый ключ y = {y}")
    
    # Сообщение (строка, преобразуется в биты)
    message = "Hello, ElGamal!"
    
    # Подпись
    r, s = sign(message, private_key, public_key)
    print(f"\nСообщение: '{message}'")
    print(f"Подпись: r = {r}, s = {s}")
    
    # Проверка
    valid = verify(message, (r, s), public_key)
    print(f"Проверка подписи: {'УСПЕШНО' if valid else 'ОШИБКА'}")
    
    # Попытка подделки
    fake_message = "Fake message"
    valid_fake = verify(fake_message, (r, s), public_key)
    print(f"Проверка подписи для другого сообщения: {'ПОДДЕЛКА ОБНАРУЖЕНА' if not valid_fake else 'ОШИБКА: подпись подошла к другому сообщению'}")
    
    # Попытка изменить подпись
    r_bad = (r + 1) % p
    if r_bad == 0:
        r_bad = 1
    valid_bad = verify(message, (r_bad, s), public_key)
    print(f"Проверка с изменённым r: {'ПОДДЕЛКА ОБНАРУЖЕНА' if not valid_bad else 'ОШИБКА: подпись с изменённым r прошла'}")

if __name__ == "__main__":
    # Запуск демонстраций
    demo_from_text()
    demo_weak_k_attack()
    demo_correct_usage()