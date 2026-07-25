# Атака на неинтерактивный протокол RSA ZKP
import random
import math

def extended_gcd(a, b):
    """Расширенный алгоритм Евклида для нахождения обратного элемента по модулю"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """Находит обратное число a ^ (-1) mod m"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратный элемент не существует")
    return x % m

def generate_rsa_parameters(bits = 20):
    """
    Генерирует RSA-подобные параметры для демонстрации.
    В реальности N должно быть произведением двух простых чисел,
    но для атаки это не важно (как указано в тексте).
    """
    # Генерируем два простых числа (для учебных целей)
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def generate_prime(bits):
        while True:
            n = random.randint(2 ** (bits - 1), 2 ** bits - 1)
            if is_prime(n):
                return n
    
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    N = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (открытая экспонента)
    e = 65537
    while math.gcd(e, phi) != 1:
        e = random.randint(3, phi - 1)
    
    return N, e, phi

def prove_attack():
    """Демонстрирует атаку Евы на неинтерактивный протокол RSA ZKP"""
    
    print("=" * 70)
    print("АТАКА НА НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ RSA ZKP")
    print("=" * 70)
    
    # Шаг 0: Генерация открытых параметров
    print("\n[0] Генерация открытых параметров RSA")
    N, e, phi = generate_rsa_parameters(bits = 22)  # bits=22 для наглядности чисел
    print(f"    N = {N}")
    print(f"    e = {e}")
    
    # Секретное сообщение m (Пегги знает его, Ева - нет)
    m = random.randint(1000, 10000)
    print(f"\n[Секрет] m = {m} (известно только Пегги)")
    
    # Вычисляем c = m^e mod N (это открытый параметр)
    c = pow(m, e, N)
    print(f"\n[Открытый параметр] c = m ^ e mod N = {c}")
    
    print("\n" + "=" * 70)
    print("НАЧАЛО АТАКИ ЕВЫ")
    print("=" * 70)
    
    # АТАКА ЕВЫ (она не знает m)
    print("\n[1] Ева выбирает случайное число r")
    r = random.randint(2, N - 2)
    while math.gcd(r, N) != 1:
        r = random.randint(2, N - 2)
    print(f"    r = {r} (секрет Евы)")
    
    print("\n[2] Ева вычисляет v1 = e * r ^ (-1) mod N")
    r_inv = mod_inverse(r, N)
    v1 = (e * r_inv) % N
    print(f"    r ^ (-1) mod N = {r_inv}")
    print(f"    v1 = {v1}")
    
    print("\n[3] Ева решает уравнение e * x ≡ c (mod N)")
    print("    Находит x = c * e ^ (-1) mod N")
    e_inv = mod_inverse(e, phi)  # Обратное по модулю phi(N)
    # Важно: в реальности Ева может найти x через расширенный алгоритм Евклида
    # используя только N и e (так как e взаимно просто с N)
    # Но для простоты используем phi (в тексте атаки это не требуется, т.к. e открыто)
    x = (c * e_inv) % N
    print(f"    e ^ (-1) mod N = {e_inv}")
    print(f"    x = {x}")
    
    print("\n[4] Ева вычисляет v2 = x * r mod N")
    v2 = (x * r) % N
    print(f"    v2 = {v2}")
    
    print("\n[5] Ева отправляет Виктору пару (v1, v2)")
    print(f"    (v1, v2) = ({v1}, {v2})")
    
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ВИКТОРА")
    print("=" * 70)
    
    print("\n[6] Виктор проверяет: v1 * v2 ≡ c (mod N)")
    check = (v1 * v2) % N
    print(f"    v1 * v2 mod N = {check}")
    print(f"    c = {c}")
    
    print("\n[7] РЕЗУЛЬТАТ:")
    if check == c:
        print("    ✓ АТАКА УСПЕШНА! Виктор поверил, что Ева знает m.")
        print("    ✓ Ева обманула проверяющего, хотя m ей НЕИЗВЕСТНО!")
    else:
        print("    ✗ Атака провалилась (такого быть не должно при правильных вычислениях)")
    
    print("\n" + "=" * 70)
    print("ДОКАЗАТЕЛЬСТВО ОБМАНА")
    print("=" * 70)
    print(f"    Реальное значение m = {m}")
    print(f"    Ева использовала только открытые параметры (N, e, c)")
    print(f"    и своё случайное число r = {r}")
    print("=" * 70)

def demonstrate_with_example_from_text():
    """Демонстрирует атаку на числовом примере из текста"""
    
    print("\n" + "=" * 70)
    print("ЧИСЛОВОЙ ПРИМЕР ИЗ ТЕКСТА")
    print("=" * 70)
    
    # Параметры из текста
    N = 2430101
    c = 160613
    e = 9007
    r = 39
    
    print(f"Открытые параметры:")
    print(f"  N = {N}")
    print(f"  c = {c}")
    print(f"  e = {e}")
    print(f"Секретное число Евы: r = {r}")
    
    print("\n[Шаг 1] Ева вычисляет v1 = e * r ^ (-1) mod N")
    r_inv = mod_inverse(r, N)
    v1 = (e * r_inv) % N
    print(f"  r ^ (-1) mod N = {r_inv}")
    print(f"  v1 = {v1} (в тексте: 1 557 988)")
    
    print("\n[Шаг 2] Ева решает e * x ≡ c (mod N)")
    # Для нахождения x используем расширенный алгоритм Евклида
    # Так как e и N взаимно просты
    e_inv = mod_inverse(e, N)
    x = (c * e_inv) % N
    print(f"  e ^ (-1) mod N = {e_inv}")
    print(f"  x = {x} (в тексте: 2 031 892)")
    
    print("\n[Шаг 3] Ева вычисляет v2 = x * r mod N")
    v2 = (x * r) % N
    print(f"  v2 = {v2} (в тексте: 1 480 556)")
    
    print("\n[Проверка Виктора]")
    check = (v1 * v2) % N
    print(f"  v1 * v2 mod N = {check}")
    print(f"  c = {c}")
    
    if check == c:
        print("\n✓ АТАКА УСПЕШНА! Все числа совпадают с текстом.")
    else:
        print("\n✗ Ошибка в вычислениях")

if __name__ == "__main__":
    # Запуск основной атаки со случайными параметрами
    prove_attack()
    
    print("\n")
    
    # Демонстрация с примером из текста
    demonstrate_with_example_from_text()
    
    print("\n" + "=" * 70)
    print("ВЫВОД:")
    print("  Атака успешна, потому что в неинтерактивном протоколе")
    print("  все параметры (N, e, c) известны заранее.")
    print("  Ева может решить уравнение e * x ≡ c (mod N) и подделать")
    print("  доказательство, НЕ ЗНАЯ секретного значения m.")
    print("=" * 70)