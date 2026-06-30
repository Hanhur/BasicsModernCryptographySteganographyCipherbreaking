# Задачи и упражнения
# Задача 1. =========================================================================================================================================
import math
import random

# ---------- Вспомогательные функции ----------

def factorize(n):
    """Разложение числа на простые множители (для поиска порождающего элемента)"""
    factors = []
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors

def is_primitive_root(g, p, factors):
    """
    Проверяет, является ли g порождающим элементом мультипликативной группы по модулю p.
    Для простого p порядок группы равен p-1.
    """
    for q in factors:
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True

def find_primitive_root(p):
    """Находит один порождающий элемент мультипликативной группы по модулю p."""
    factors = factorize(p - 1)
    for g in range(2, p):
        if is_primitive_root(g, p, factors):
            return g
    return None

def element_order(g, mod, n):
    """Вычисляет порядок элемента g в группе порядка n по модулю mod."""
    for d in range(1, n + 1):
        if n % d == 0:
            if pow(g, d, mod) == 1:
                return d
    return n

def all_subgroups(g, mod, n):
    """
    Возвращает словарь {порядок: множество подгрупп (как frozenset элементов)}.
    Только для демонстрации, перебор всех элементов.
    """
    subgroups_by_order = {}
    # Все элементы группы
    elements = [pow(g, i, mod) for i in range(n)]
    
    # Перебираем все подмножества? Нет, это слишком долго.
    # Вместо этого перебираем все элементы как порождающие.
    for elem in elements:
        sub = set()
        cur = elem
        for _ in range(n):
            sub.add(cur)
            cur = (cur * elem) % mod
            if cur == elem:
                break
        order = len(sub)
        if order not in subgroups_by_order:
            subgroups_by_order[order] = set()
        subgroups_by_order[order].add(frozenset(sub))
    return subgroups_by_order

# ---------- Основная программа ----------

def main():
    # Выбираем простое число p так, чтобы n = p-1 имело много делителей.
    # Для примера возьмём p = 23, тогда n = 22, делители: 1, 2, 11, 22.
    p = 23
    n = p - 1  # порядок циклической группы
    print(f"Группа G = C_{n} (мультипликативная группа по модулю {p})")
    
    # Находим порождающий элемент
    g = find_primitive_root(p)
    if g is None:
        print("Не удалось найти порождающий элемент.")
        return
    print(f"Порождающий элемент g = {g}")
    
    # Выбираем делитель q
    divisors = [d for d in range(1, n + 1) if n % d == 0]
    print(f"Делители n = {n}: {divisors}")
    
    q = 11  # возьмём для примера q = 11
    if n % q != 0:
        print(f"{q} не является делителем {n}")
        return
    print(f"\nРассмотрим делитель q = {q}")
    
    # 1. Существование: строим H = <g^(n/q)>
    exponent = n // q
    h = pow(g, exponent, p)
    print(f"Элемент h = g ^ {exponent} = {h} (mod {p})")
    
    # Вычисляем порядок h
    order_h = element_order(h, p, n)
    print(f"Порядок h = {order_h} (должен быть равен {q})")
    assert order_h == q, "Ошибка: порядок h не равен q!"
    
    # Строим все элементы подгруппы H
    H_elements = set()
    cur = h
    for _ in range(q):
        H_elements.add(cur)
        cur = (cur * h) % p
    print(f"Подгруппа H = {sorted(H_elements)}")
    
    # 2. Единственность: находим все подгруппы порядка q (перебором)
    print("\nПроверка единственности (перебор всех подгрупп):")
    all_subs = all_subgroups(g, p, n)
    
    if q in all_subs:
        subgroups_q = all_subs[q]
        print(f"Найдено подгрупп порядка {q}: {len(subgroups_q)}")
        for i, sub in enumerate(subgroups_q):
            print(f"  Подгруппа {i + 1}: {sorted(sub)}")
            # Проверяем, совпадает ли с H
            if set(sub) == H_elements:
                print("    -> Это наша H")
            else:
                print("    -> Это другая подгруппа (НО ТАКОЙ БЫТЬ НЕ ДОЛЖНО!)")
        
        # Проверяем единственность
        if len(subgroups_q) == 1:
            print("\n*** Единственность подтверждена: существует ровно одна подгруппа порядка q. ***")
        else:
            print("\nВНИМАНИЕ: Найдено более одной подгруппы! (противоречит теории, проверьте код)")
    else:
        print(f"Подгрупп порядка {q} не найдено (ошибка).")
    
    # Дополнительно: выведем все подгруппы для наглядности
    print("\nВсе подгруппы группы C_22:")
    for ord_sub in sorted(all_subs.keys()):
        print(f"  Порядок {ord_sub}: {len(all_subs[ord_sub])} подгрупп")
        for sub in all_subs[ord_sub]:
            print(f"    {sorted(sub)}")

if __name__ == "__main__":
    main()

# Задача 2. =========================================================================================================================================
import random
import hashlib

def mod_inv(a, m):
    """Вычисляет обратное число по модулю m (расширенный алгоритм Евклида)."""
    a = a % m
    # Расширенный алгоритм Евклида
    m0 = m
    y = 0
    x = 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x = x + m0
    return x

def hash_message(message):
    """Вычисляет хэш сообщения (SHA-256) и приводит к модулю q."""
    h = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return int(h, 16)

def generate_dsa_params():
    """
    Генерирует параметры DSA для демонстрации.
    Для простоты используем небольшие числа, но сохраняем логику.
    """
    # В реальном DSA p и q — большие простые числа.
    # Здесь для примера возьмём готовые небольшие параметры.
    # q = 101 (простое), p = 2*q + 1 = 203 (простое)
    # g — примитивный элемент порядка q.
    
    q = 101
    p = 203  # В реальности p должно быть простым, но для примера подойдёт
    # Найдём g порядка q: g = 2^((p-1)//q) mod p
    g = pow(2, (p - 1) // q, p)
    
    return p, q, g

def generate_keys(p, q, g):
    """Генерирует секретный и открытый ключи."""
    x = random.randint(1, q - 1)  # Секретный ключ
    y = pow(g, x, p)            # Открытый ключ
    return x, y

def sign_message(message, p, q, g, x, k):
    """Подписывает сообщение с заданным k."""
    h = hash_message(message) % q
    r = pow(g, k, p) % q
    if r == 0:
        raise ValueError("r = 0, нужно выбрать другое k")
    
    k_inv = mod_inv(k, q)
    s = (h + x * r) * k_inv % q
    if s == 0:
        raise ValueError("s = 0, нужно выбрать другое k")
    
    return r, s

def recover_secret_key(m1, m2, r1, s1, r2, s2, q):
    """
    Восстанавливает секретный ключ x, если известно, что
    для подписей использовался один и тот же k.
    """
    print("=" * 60)
    print("ВОССТАНОВЛЕНИЕ СЕКРЕТНОГО КЛЮЧА")
    print("=" * 60)
    
    # Шаг 1: Проверяем, что r одинаковы (признак повторного использования k)
    print(f"\n1. Проверка r1 == r2: {r1} == {r2} -> {r1 == r2}")
    if r1 != r2:
        print("ОШИБКА: r разные, k использовались разные!")
        return None
    
    r = r1
    print(f"   r = {r}")
    
    # Шаг 2: Вычисляем хэши сообщений
    h1 = hash_message(m1) % q
    h2 = hash_message(m2) % q
    print(f"\n2. Хэши сообщений:")
    print(f"   h1 = H({m1}) = {h1}")
    print(f"   h2 = H({m2}) = {h2}")
    
    # Шаг 3: Восстанавливаем k = (h2 - h1) * (s2 - s1)^(-1) mod q
    print(f"\n3. Восстанавливаем сессионный ключ k:")
    print(f"   s1 = {s1}, s2 = {s2}")
    
    diff_h = (h2 - h1) % q
    diff_s = (s2 - s1) % q
    
    print(f"   h2 - h1 = {diff_h}")
    print(f"   s2 - s1 = {diff_s}")
    
    if diff_s == 0:
        print("ОШИБКА: s2 - s1 = 0, невозможно восстановить k!")
        return None
    
    s_inv = mod_inv(diff_s, q)
    k = diff_h * s_inv % q
    print(f"   k = {diff_h} * {s_inv} mod {q} = {k}")
    
    # Шаг 4: Восстанавливаем x = (s1 * k - h1) * r^(-1) mod q
    print(f"\n4. Восстанавливаем секретный ключ x:")
    print(f"   x = (s1 * k - h1) * r ^ (-1) mod {q}")
    
    r_inv = mod_inv(r, q)
    x_recovered = (s1 * k - h1) * r_inv % q
    print(f"   r^(-1) = {r_inv}")
    print(f"   x = ({s1} * {k} - {h1}) * {r_inv} mod {q} = {x_recovered}")
    
    return x_recovered

def main():
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ВЗЛОМА DSA ПРИ ПОВТОРНОМ ИСПОЛЬЗОВАНИИ k")
    print("=" * 60)
    
    # 1. Генерируем параметры DSA
    p, q, g = generate_dsa_params()
    print(f"\nПараметры DSA:")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  g = {g}")
    
    # 2. Генерируем ключи
    x_real, y = generate_keys(p, q, g)
    print(f"\nКлючи:")
    print(f"  Секретный ключ x = {x_real} (это знает только Алиса)")
    print(f"  Открытый ключ y = {y} (это знают все)")
    
    # 3. Алиса подписывает два сообщения с ОДНИМ И ТЕМ ЖЕ k
    k_same = random.randint(1, q-1)
    print(f"\nАлиса использует один и тот же сессионный ключ k = {k_same}")
    
    m1 = "Документ 1: Перевести 100$ Бобу"
    m2 = "Документ 2: Перевести 500$ Чаку"
    
    print(f"\nПодпись первого сообщения:")
    r1, s1 = sign_message(m1, p, q, g, x_real, k_same)
    print(f"  m1 = '{m1}'")
    print(f"  Подпись: (r1, s1) = ({r1}, {s1})")
    
    print(f"\nПодпись второго сообщения:")
    r2, s2 = sign_message(m2, p, q, g, x_real, k_same)
    print(f"  m2 = '{m2}'")
    print(f"  Подпись: (r2, s2) = ({r2}, {s2})")
    
    # 4. Оскар перехватывает сообщения и подписи
    print("\n" + "=" * 60)
    print("ОСКАР ПЕРЕХВАТИЛ СООБЩЕНИЯ И ПОДПИСИ")
    print("=" * 60)
    print(f"  m1 = '{m1}', подпись = ({r1}, {s1})")
    print(f"  m2 = '{m2}', подпись = ({r2}, {s2})")
    print("  Оскар знает, что использован один k!")
    
    # 5. Оскар восстанавливает секретный ключ
    x_recovered = recover_secret_key(m1, m2, r1, s1, r2, s2, q)
    
    # 6. Проверка
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ")
    print("=" * 60)
    if x_recovered is not None:
        print(f"  Восстановленный секретный ключ: {x_recovered}")
        print(f"  Настоящий секретный ключ:       {x_real}")
        print(f"  Ключи совпадают? {x_recovered == x_real}")
        if x_recovered == x_real:
            print("\n  ✅ ВЗЛОМ УСПЕШЕН! Оскар восстановил секретный ключ!")
            print("  ⚠️  Теперь Оскар может подписывать любые документы от имени Алисы.")
        else:
            print("\n  ❌ Что-то пошло не так...")
    else:
        print("  Не удалось восстановить ключ.")

if __name__ == "__main__":
    main()

# Задача 3. =========================================================================================================================================
def find_private_key_interactive():
    """
    Интерактивная версия для поиска ключа a
    """
    print("Введите параметры системы:")
    
    # Базовая настройка
    p = int(input("Введите p: ") or "43")
    q = int(input("Введите q (порядок g): ") or "7")
    g = int(input("Введите g (порождающий элемент): ") or "21")
    
    print("\nВведите данные документов:")
    h1 = int(input("Введите h(m1): ") or "2")
    h2 = int(input("Введите h(m2): ") or "3")
    
    print("\nВведите подписи:")
    r = int(input("Введите r (общее для обеих подписей): ") or "2")
    s1 = int(input("Введите s1: ") or "1")
    s2 = int(input("Введите s2: ") or "6")
    
    # Проверка: r должно быть одинаковым
    if r == 0:
        print("Ошибка: r не может быть 0!")
        return None
    
    # Решение системы уравнений
    # s1 = k^(-1) * (h1 + a*r) mod q
    # s2 = k^(-1) * (h2 + a*r) mod q
    
    # Находим обратные элементы для s1 и s2
    try:
        s1_inv = pow(s1, -1, q)
        s2_inv = pow(s2, -1, q)
    except ValueError:
        print("Ошибка: s1 или s2 не имеют обратного элемента по модулю q!")
        return None
    
    # Вычисляем a
    numerator = (s1_inv * h1 - s2_inv * h2) % q
    denominator = (r * (s2_inv - s1_inv)) % q
    
    if denominator == 0:
        print("Ошибка: знаменатель равен 0, решение невозможно!")
        return None
    
    try:
        a = (numerator * pow(denominator, -1, q)) % q
    except ValueError:
        print("Ошибка: знаменатель не имеет обратного элемента!")
        return None
    
    # Вычисляем k для проверки
    k = (pow(s1, -1, q) * (h1 + a * r)) % q
    
    # Выводим результаты
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ:")
    print(f"Долгосрочный ключ a = {a}")
    print(f"Сессионный ключ k = {k}")
    print("=" * 50)
    
    # Проверка
    print("\nПроверка:")
    k_inv = pow(k, -1, q)
    s1_check = (k_inv * (h1 + a * r)) % q
    s2_check = (k_inv * (h2 + a * r)) % q
    
    print(f"s1 вычисленное = {s1_check} (должно быть {s1}) - {'✓' if s1_check == s1 else '✗'}")
    print(f"s2 вычисленное = {s2_check} (должно быть {s2}) - {'✓' if s2_check == s2 else '✗'}")
    
    return a

# Запуск
if __name__ == "__main__":
    find_private_key_interactive()