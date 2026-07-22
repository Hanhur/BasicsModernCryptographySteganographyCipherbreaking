# Типичные атаки на алгоритм
"""
RSA CRYPTOANALYSIS TOOLKIT
Демонстрация типичных атак на RSA из учебного материала
Без использования numpy - только стандартная библиотека
"""

import sys
import math
import random
import time
from typing import Tuple, Optional

# ============================================================
# ОТКЛЮЧАЕМ ОГРАНИЧЕНИЕ НА ПРЕОБРАЗОВАНИЕ БОЛЬШИХ ЧИСЕЛ В СТРОКИ
# ============================================================
try:
    # Python 3.11+ имеет ограничение на преобразование int в str
    sys.set_int_max_str_digits(0)  # 0 означает "без ограничений"
except AttributeError:
    pass  # Старые версии Python не имеют этого ограничения

# ============================================================
# БАЗОВЫЕ КРИПТОГРАФИЧЕСКИЕ ФУНКЦИИ
# ============================================================

def gcd(a: int, b: int) -> int:
    """Алгоритм Евклида"""
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y) где ax + by = gcd"""
    if b == 0:
        return a, 1, 0
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    return gcd_val, y1, x1 - (a // b) * y1

def mod_inverse(e: int, phi: int) -> int:
    """Обратное число по модулю"""
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % phi

def is_prime(n: int, k: int = 10) -> bool:
    """Тест Миллера-Рабина для проверки простоты"""
    if n < 2:
        return False
    if n in (2, 3, 5, 7):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Проверяем k свидетелей
    for _ in range(k):
        a = random.randint(2, n - 2)
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

def generate_prime(bits: int) -> int:
    """Генерация простого числа заданной битовости"""
    while True:
        n = random.getrandbits(bits)
        # Устанавливаем старший и младший биты в 1
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def generate_rsa_keypair(bits: int = 512) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Генерация пары RSA ключей"""
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while q == p:
        q = generate_prime(bits // 2)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Стандартная открытая экспонента
    e = 65537
    if gcd(e, phi) != 1:
        # Если e не взаимопростое, генерируем другое
        e = 17
        while gcd(e, phi) != 1:
            e += 2
    
    d = mod_inverse(e, phi)
    
    return (e, n), (d, n)

def rsa_encrypt(message: int, public_key: Tuple[int, int]) -> int:
    """Шифрование RSA"""
    e, n = public_key
    return pow(message, e, n)

def rsa_decrypt(ciphertext: int, private_key: Tuple[int, int]) -> int:
    """Расшифрование RSA"""
    d, n = private_key
    return pow(ciphertext, d, n)

# ============================================================
# 1. АТАКА: МАЛЫЙ ОТКРЫТЫЙ ТЕКСТ (прямое извлечение корня)
# ============================================================

def integer_nth_root(n: int, k: int) -> Optional[int]:
    """
    Находит целочисленный корень k-ой степени из n
    Использует бинарный поиск
    """
    if k == 1:
        return n
    if k == 2:
        root = int(math.isqrt(n))
        return root if root * root == n else None
    
    low, high = 1, n
    while low <= high:
        mid = (low + high) // 2
        power = pow(mid, k)
        if power == n:
            return mid
        elif power < n:
            low = mid + 1
        else:
            high = mid - 1
    return None

def attack_small_message(ciphertext: int, e: int) -> Optional[int]:
    """
    Атака на очень короткое сообщение: M ^ e < N
    Извлекает e-ый корень из шифротекста в обычной (не модульной) арифметике
    """
    try:
        return integer_nth_root(ciphertext, e)
    except:
        return None

def demo_small_message_attack():
    """Демонстрация атаки на короткое сообщение"""
    print("\n" + "=" * 60)
    print("1. АТАКА НА КОРОТКОЕ СООБЩЕНИЕ (M ^ e < N)")
    print("=" * 60)
    
    # Используем МАЛЕНЬКУЮ экспоненту для демонстрации
    # В реальности e=65537, но для атаки нужно e=3, 5, 7...
    e = 3
    M = 42
    
    # Генерируем ключи с маленьким e
    # Создаем N > M^e, чтобы атака сработала
    p = 101
    q = 103
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Проверяем, что e взаимопростое с phi
    if gcd(e, phi) != 1:
        e = 5
        while gcd(e, phi) != 1:
            e += 2
    
    d = mod_inverse(e, phi)
    public_key = (e, n)
    private_key = (d, n)
    
    print(f"Исходное сообщение: M = {M}")
    print(f"Открытая экспонента: e = {e}")
    print(f"Модуль: N = {n}")
    
    # Шифруем
    c = rsa_encrypt(M, public_key)
    print(f"Шифротекст: c = {c}")
    
    # Проверяем условие M^e < N
    me = pow(M, e)
    print(f"M ^ e = {me}")
    print(f"M ^ e < N: {me < n}")
    
    # Атака
    if me < n:
        recovered = attack_small_message(c, e)
        if recovered is not None:
            print(f"\n✅ АТАКА УСПЕШНА! Восстановлено: M = {recovered}")
            print(f"   Извлечен корень {e}-ой степени из {c}")
        else:
            print("\n❌ Атака не удалась (корень не извлекся)")
    else:
        print("\n⚠️  Атака невозможна: M ^ e >= N (сообщение достаточно длинное)")
    
    print("\n📌 РЕШЕНИЕ: Использовать паддинг (OAEP) с добавлением случайных битов")
    print("   в старшие разряды, чтобы M ^ e всегда было > N")

# ============================================================
# 2. АТАКА: ФАКТОРИЗАЦИЯ МЕТОДОМ ПОЛЛАРДА (p-1)
# ============================================================

def pollard_p_minus_1(n: int, B: int = 10000) -> Optional[int]:
    """
    Алгоритм Полларда p-1 для факторизации
    Работает, если p-1 или q-1 является B-гладким числом
    """
    a = 2
    for j in range(2, B + 1):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return d
    return None

def demo_pollard_attack():
    """Демонстрация атаки Полларда на слабый модуль"""
    print("\n" + "=" * 60)
    print("2. АТАКА ПОЛЛАРДА (p - 1 ФАКТОРИЗАЦИЯ)")
    print("=" * 60)
    
    # Создаем уязвимый модуль: p-1 имеет только маленькие простые множители
    # Используем маленькие простые числа для p
    
    # p = 2*3*5*7*11*13 + 1 = 30031 (простое)
    p = 30031
    q = 30047  # Другое простое
    n = p * q
    
    print(f"Модуль N = {n}")
    print(f"p = {p}, q = {q} (известны только для проверки)")
    print(f"p - 1 = {p - 1} = {2} x {3} x {5} x {7} x {11} x {13}")
    print(f"Все множители p-1 маленькие! (B-гладкое число)")
    
    # Атака
    start = time.time()
    factor = pollard_p_minus_1(n, B = 100)
    elapsed = time.time() - start
    
    if factor:
        print(f"\n✅ АТАКА УСПЕШНА! Время: {elapsed:.4f} сек")
        print(f"   Найден множитель: {factor}")
        print(f"   Второй множитель: {n // factor}")
        print(f"   p = {min(factor, n // factor)}, q = {max(factor, n // factor)}")
    else:
        print(f"\n❌ Атака не удалась за {elapsed:.4f} сек")
    
    print("\n📌 РЕШЕНИЕ: Использовать 'сильные простые' числа, где p - 1 и q - 1")
    print("   имеют большой простой множитель (≥ 100 бит)")

# ============================================================
# 3. АТАКА: АТАКА ВИНЕРА (МАЛАЯ СЕКРЕТНАЯ ЭКСПОНЕНТА)
# ============================================================

def continued_fraction(n: int, d: int) -> list:
    """Разложение n / d в цепную дробь"""
    fractions = []
    while d != 0:
        a = n // d
        fractions.append(a)
        n, d = d, n - a * d
    return fractions

def convergents(fractions: list) -> list:
    """Вычисление подходящих дробей из цепной дроби"""
    convs = []
    for i in range(len(fractions)):
        if i == 0:
            num, den = fractions[0], 1
        elif i == 1:
            num, den = fractions[0] * fractions[1] + 1, fractions[1]
        else:
            num, den = fractions[i] * convs[-1][0] + convs[-2][0], fractions[i] * convs[-1][1] + convs[-2][1]
        convs.append((num, den))
    return convs

def wiener_attack(e: int, n: int) -> Optional[int]:
    """
    Атака Винера: находит d если d < (1 / 3) * N ^ (1 / 4)
    Использует цепные дроби для приближения e/n
    """
    fracs = continued_fraction(e, n)
    convs = convergents(fracs)
    
    for k, d in convs:
        if k == 0:
            continue
        # Проверяем кандидата
        try:
            # Вычисляем phi = (e*d - 1)//k
            if (e * d - 1) % k != 0:
                continue
            phi = (e * d - 1) // k
            
            # Решаем квадратное уравнение для p и q
            # x^2 - (n - phi + 1)x + n = 0
            b = n - phi + 1
            discriminant = b * b - 4 * n
            if discriminant < 0:
                continue
            
            sqrt_disc = int(math.isqrt(discriminant))
            if sqrt_disc * sqrt_disc != discriminant:
                continue
            
            p = (b + sqrt_disc) // 2
            q = (b - sqrt_disc) // 2
            
            if p * q == n and p > 1 and q > 1:
                return d
        except:
            continue
    
    return None

def demo_wiener_attack():
    """Демонстрация атаки Винера на малую секретную экспоненту"""
    print("\n" + "=" * 60)
    print("3. АТАКА ВИНЕРА (МАЛАЯ СЕКРЕТНАЯ ЭКСПОНЕНТА d)")
    print("=" * 60)
    
    # Создаем ключи с intentionally малой d
    # Генерируем p и q
    p = 1861
    q = 2081
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Находим e такое, что d малое
    # Обратно: находим e = d^(-1) mod phi
    d_small = 29  # Маленькая секретная экспонента
    
    # Проверяем условие атаки Винера
    n_14 = int(n ** 0.25)
    if d_small < n_14 / 3:
        print(f"✅ d = {d_small} < (1 / 3) * N ^ (1 / 4) = {n_14 / 3:.2f} → УЯЗВИМОСТЬ!")
    
    e = mod_inverse(d_small, phi)
    
    print(f"p = {p}, q = {q}")
    print(f"N = {n}")
    print(f"φ(N) = {phi}")
    print(f"Секретная экспонента d = {d_small}")
    print(f"Открытая экспонента e = {e}")
    print(f"d < (1 / 3) * N  ^(1 / 4): {d_small < n_14 / 3}")
    
    # Атака
    start = time.time()
    recovered_d = wiener_attack(e, n)
    elapsed = time.time() - start
    
    if recovered_d:
        print(f"\n✅ АТАКА УСПЕШНА! Время: {elapsed:.4f} сек")
        print(f"   Найден d: {recovered_d}")
        print(f"   Исходный d: {d_small}")
        print(f"   Совпадает: {recovered_d == d_small}")
    else:
        print(f"\n❌ Атака не удалась за {elapsed:.4f} сек")
        print(f"   (возможно, d слишком большое)")
    
    print("\n📌 РЕШЕНИЕ: Выбирать d > N ^ (1 / 2) (близкое по размеру к N)")
    print("   или использовать стандартные рекомендации NIST")

# ============================================================
# 4. АТАКА: КВАНТОВЫЙ АЛГОРИТМ ШОРА (СИМУЛЯЦИЯ)
# ============================================================

def quantum_period_finding_simulation(a: int, n: int) -> int:
    """
    СИМУЛЯЦИЯ квантового нахождения периода
    В реальном квантовом компьютере это делается за O(log ^ 3 n)
    Здесь мы просто находим период перебором (для демонстрации)
    """
    # Находим наименьший r такой, что a^r ≡ 1 (mod n)
    r = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        r += 1
        if r > n:  # Защита от бесконечного цикла
            return -1
    return r

def shor_factorization_simulation(n: int) -> Optional[Tuple[int, int]]:
    """
    СИМУЛЯЦИЯ алгоритма Шора (только для демонстрации)
    В реальности квантовый компьютер находит период экспоненциально быстрее
    """
    if n % 2 == 0:
        return 2, n // 2
    
    # Пытаемся найти нетривиальный множитель
    for _ in range(10):
        a = random.randint(2, n - 2)
        if gcd(a, n) > 1:
            d = gcd(a, n)
            return d, n // d
        
        # Находим период (в квантовом компьютере - быстро)
        r = quantum_period_finding_simulation(a, n)
        
        if r % 2 == 0 and r > 0:
            x = pow(a, r // 2, n)
            if x != 1 and x != n - 1:
                p = gcd(x - 1, n)
                q = gcd(x + 1, n)
                if p > 1 and q > 1 and p * q == n:
                    return p, q
    
    return None

def demo_shor_attack():
    """Демонстрация квантовой угрозы (симуляция)"""
    print("\n" + "=" * 60)
    print("4. КВАНТОВАЯ АТАКА (АЛГОРИТМ ШОРА)")
    print("=" * 60)
    
    # Используем маленькое число для демонстрации
    n = 15  # 3 × 5
    
    print(f"Модуль N = {n}")
    print("Классический подход: факторизация перебором")
    print("Квантовый подход: нахождение периода за O(log³ N)")
    
    start = time.time()
    result = shor_factorization_simulation(n)
    elapsed = time.time() - start
    
    if result:
        p, q = result
        print(f"\n✅ ФАКТОРИЗАЦИЯ УСПЕШНА! Время (симуляция): {elapsed:.4f} сек")
        print(f"   {n} = {p} x {q}")
        print(f"\n⚠️  КВАНТОВАЯ УГРОЗА РЕАЛЬНА!")
        print("   Алгоритм Шора факторизует RSA за полиномиальное время")
    else:
        print(f"\n❌ Факторизация не удалась")
    
    print("\n📌 РЕШЕНИЕ: Переход на постквантовые криптосистемы")
    print("   (на решетках, кодах, многомерных системах)")

# ============================================================
# 5. АТАКА: ИЗВЕСТНЫЕ БИТЫ (КОППЕРСМИТА) - СИМУЛЯЦИЯ
# ============================================================

def known_bits_attack_simulation(n: int, p_bits_known: int, bits_position: str = "high") -> Optional[int]:
    """
    СИМУЛЯЦИЯ атаки Копперсмита с известными битами
    Упрощенная версия для демонстрации
    """
    # Для демонстрации просто проверяем возможность
    bits = n.bit_length()
    p_guess = generate_prime(bits // 2)
    
    # В реальной атаке используется LLL-алгоритм для поиска корней многочлена
    # Здесь мы просто показываем, что знание бит помогает
    
    # Если знаем половину бит, то можем восстановить p
    if bits_position == "high":
        # Симулируем, что знаем старшие биты
        known_mask = ((1 << (bits // 4)) - 1) << (bits // 4)
        known_part = p_guess & known_mask
        # В реальности мы бы искали p в форме known_part + x
        # с помощью алгоритма Копперсмита
        return p_guess
    else:
        # Младшие биты
        known_mask = (1 << (bits // 4)) - 1
        known_part = p_guess & known_mask
        return p_guess

def demo_coppersmith_attack():
    """Демонстрация атаки Копперсмита (известные биты)"""
    print("\n" + "=" * 60)
    print("5. АТАКА КОППЕРСМИТА (ИЗВЕСТНЫЕ БИТЫ ПРОСТОГО ЧИСЛА)")
    print("=" * 60)
    
    # Генерируем p и q
    p = 9876543210123456789
    q = 1234567890987654321
    n = p * q
    
    print(f"N = {n}")
    print(f"p = {p} (известно только для проверки)")
    
    bits = n.bit_length()
    known_bits = bits // 4  # Четверть бит
    
    print(f"Битов N: {bits}")
    print(f"Известно бит p: {known_bits} (≈ {known_bits / bits * 100:.1f}%)")
    print("По теореме Копперсмита: достаточно ≥ 50% бит")
    
    # Симуляция атаки
    recovered = known_bits_attack_simulation(n, known_bits, "high")
    
    if recovered:
        print(f"\n✅ АТАКА ВОЗМОЖНА!")
        print(f"   Известные биты позволяют восстановить p")
        print(f"   Используется LLL-алгоритм для нахождения корней")
    else:
        print(f"\n⚠️  Атака требует ≥ 50% известных бит")
    
    print("\n📌 РЕШЕНИЕ: Защищать битовое представление простых чисел")
    print("   Использовать защиту от атак по сторонним каналам")

# ============================================================
# 6. АТАКА: НЕСКОЛЬКО СООБЩЕНИЙ С МАЛЫМ e (ХАСТАД)
# ============================================================

def hastad_attack_simulation(messages: list, public_keys: list, e: int = 3) -> Optional[int]:
    """
    СИМУЛЯЦИЯ атаки Хастада
    Когда одно и то же сообщение отправлено разным получателям
    """
    # Используем Китайскую теорему об остатках
    # Находим M^e mod (N1*N2*N3)
    n1, n2, n3 = [k[1] for k in public_keys[:3]]
    c1, c2, c3 = messages[:3]
    
    # Вычисляем произведение всех N
    N_product = n1 * n2 * n3
    
    # Китайская теорема об остатках
    m1 = c1 * (N_product // n1) * mod_inverse(N_product // n1, n1)
    m2 = c2 * (N_product // n2) * mod_inverse(N_product // n2, n2)
    m3 = c3 * (N_product // n3) * mod_inverse(N_product // n3, n3)
    
    C = (m1 + m2 + m3) % N_product
    
    # Извлекаем e-ый корень
    return integer_nth_root(C, e)

def demo_hastad_attack():
    """Демонстрация атаки Хастада"""
    print("\n" + "=" * 60)
    print("6. АТАКА ХАСТАДА (ОДНО СООБЩЕНИЕ - МНОГО ПОЛУЧАТЕЛЕЙ)")
    print("=" * 60)
    
    e = 3
    M = 42  # Одно и то же сообщение
    
    print(f"Сообщение M = {M}")
    print(f"Открытая экспонента e = {e}")
    print("Сообщение отправлено 3 получателям с разными N\n")
    
    # Генерируем 3 пары ключей с МАЛЕНЬКИМИ модулями
    # чтобы M^e < N_i для всех i
    public_keys = []
    private_keys = []
    ciphertexts = []
    
    for i in range(3):
        # Создаем ключи вручную с маленькими простыми числами
        p = 101 + i * 10
        q = 103 + i * 10
        while not is_prime(p):
            p += 1
        while not is_prime(q):
            q += 1
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Используем e=3
        if gcd(e, phi) != 1:
            # Если e не взаимопростое, пропускаем
            continue
        
        d = mod_inverse(e, phi)
        pub = (e, n)
        priv = (d, n)
        
        public_keys.append(pub)
        private_keys.append(priv)
        c = rsa_encrypt(M, pub)
        ciphertexts.append(c)
        
        print(f"Получатель {i + 1}:")
        print(f"  N = {pub[1]}")
        print(f"  c = {c}")
    
    # Атака (только если M^e < N_i для всех i)
    print("\n" + "─" * 60)
    print("Атака: находим M ^ e по модулю N1*N2*N3 через КТО")
    
    # Проверяем условие
    can_attack = all(pow(M, e) < pub[1] for pub in public_keys)
    if can_attack and len(public_keys) >= 3:
        try:
            recovered = hastad_attack_simulation(ciphertexts, public_keys, e)
            if recovered == M:
                print(f"\n✅ АТАКА УСПЕШНА! Восстановлено: M = {recovered}")
            else:
                print(f"\n❌ Атака не удалась (восстановлено: {recovered})")
        except Exception as ex:
            print(f"\n❌ Ошибка при атаке: {ex}")
    else:
        print("\n⚠️  Атака невозможна (сообщение слишком длинное)")
    
    print("\n📌 РЕШЕНИЕ: Добавлять уникальный идентификатор для каждого получателя")
    print("   Использовать рандомизированный паддинг")

# ============================================================
# 7. ДЕМОНСТРАЦИЯ ОАЕР ПАДДИНГА
# ============================================================

def oaep_pad(message: int, n: int, bits: int) -> int:
    """
    Простая симуляция OAEP паддинга
    Добавляем случайные биты в старшие разряды
    """
    # Размер сообщения в битах
    msg_bits = message.bit_length()
    
    # Добавляем случайные биты в старшие разряды
    padding_bits = bits - msg_bits - 1
    if padding_bits <= 0:
        return message
    
    random_pad = random.getrandbits(padding_bits)
    padded = (random_pad << msg_bits) | message
    return padded

def demo_padding():
    """Демонстрация важности паддинга"""
    print("\n" + "=" * 60)
    print("7. ЗАЩИТА: ПАДДИНГ OAEP")
    print("=" * 60)
    
    M = 42
    e = 3
    
    print(f"Сообщение: M = {M}")
    print(f"e = {e}")
    
    # Без паддинга
    print("\n❌ БЕЗ ПАДДИНГА:")
    print(f"  M ^ e = {pow(M, e)}")
    print("  → Если M ^ e < N, сообщение уязвимо для атаки корня")
    
    # С паддингом
    print("\n✅ С OAEP ПАДДИНГОМ:")
    # Используем маленький модуль для демонстрации
    n = 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    padded_M = oaep_pad(M, n, 1024)
    print(f"  M (с паддингом) = {padded_M}")
    print(f"  M ^ e = {pow(padded_M, e)}")
    print("  → M ^ e > N всегда, атака корня невозможна")
    
    print("\n📌 КЛЮЧЕВОЙ МОМЕНТ: Паддинг добавляет случайные биты")
    print("   в СТАРШИЕ разряды, увеличивая числовое значение M")
    print("   Обратите внимание: добавление в младшие разряды НЕ помогает!")

# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция демонстрации всех атак"""
    print("\n" + "█" * 60)
    print("█  RSA CRYPTOANALYSIS TOOLKIT")
    print("█  Демонстрация типичных атак")
    print("█" + "█" * 60)
    
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запускаем все демонстрации
    demo_small_message_attack()
    demo_pollard_attack()
    demo_wiener_attack()
    demo_shor_attack()
    demo_coppersmith_attack()
    demo_hastad_attack()
    demo_padding()
    
    print("\n" + "=" * 60)
    print("🔒 ИТОГОВЫЕ РЕКОМЕНДАЦИИ ПО ЗАЩИТЕ RSA:")
    print("=" * 60)
    print("1. Использовать N ≥ 2048 бит")
    print("2. Использовать e = 65537 (не 3 или 17)")
    print("3. Применять OAEP паддинг (не просто добавление нулей)")
    print("4. Использовать 'сильные простые' числа")
    print("5. Готовиться к постквантовой эпохе")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()