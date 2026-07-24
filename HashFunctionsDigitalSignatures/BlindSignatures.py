# Слепые подписи 
import random
import hashlib

def gcd(a, b):
    """Алгоритм Евклида для НОД"""
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """Расширенный алгоритм Евклида (возвращает x, y для ax + by = gcd(a,b))"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """Обратное число по модулю m"""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    return x % m

def is_prime(n, k = 10):
    """Тест Миллера-Рабина для проверки простоты"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # n-1 = d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
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

def generate_prime(bits = 512):
    """Генерация простого числа заданной битности"""
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1  # Ставим старший и младший бит в 1
        if is_prime(p):
            return p

def generate_rsa_keys(bits = 512):
    """Генерация ключей RSA"""
    # Генерируем два простых числа
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    while p == q:
        q = generate_prime(bits // 2)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем открытую экспоненту (обычно 65537)
    e = 65537
    while gcd(e, phi) != 1:
        e = random.randint(3, phi - 1)
        if e % 2 == 0:
            e += 1
    
    # Вычисляем закрытую экспоненту
    d = mod_inverse(e, phi)
    
    return {
        'public': (e, n),
        'private': d,
        'n': n,
        'phi': phi
    }

def hash_message(message):
    """Хеширование сообщения (для подписи хеша)"""
    return int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)

class BlindSignatureRSA:
    """Реализация протокола слепой подписи RSA Чаума"""
    
    def __init__(self):
        self.keys = None
        self.blinding_factor = None
    
    def setup_keys(self, bits = 512):
        """Генерация ключей для подписывающего"""
        self.keys = generate_rsa_keys(bits)
        print(f"Сгенерированы ключи RSA (битность: {bits})")
        print(f"  n = {self.keys['n']}")
        print(f"  e = {self.keys['public'][0]}")
        print(f"  d = {self.keys['private']}")
        return self.keys
    
    def blind_message(self, message):
        """Шаг 1: Ослепление сообщения"""
        if self.keys is None:
            raise ValueError("Ключи не сгенерированы!")
        
        e, n = self.keys['public']
        
        # Хешируем сообщение
        m = hash_message(message)
        m = m % n
        if m == 0:
            m = 1
        
        # Выбираем случайный слепящий множитель r
        while True:
            r = random.randint(2, n - 1)
            if gcd(r, n) == 1:
                break
        
        self.blinding_factor = r
        
        # Ослепляем сообщение: m' = m * r^e mod n
        m_blinded = (m * pow(r, e, n)) % n
        
        print(f"\n--- Ослепление ---")
        print(f"  Исходное сообщение: {message}")
        print(f"  Хеш сообщения m = {m}")
        print(f"  Слепящий множитель r = {r}")
        print(f"  Ослепленное сообщение m' = {m_blinded}")
        
        return m_blinded
    
    def sign_blinded(self, m_blinded):
        """Шаг 2: Подписание ослепленного сообщения"""
        if self.keys is None:
            raise ValueError("Ключи не сгенерированы!")
        
        d = self.keys['private']
        n = self.keys['n']
        
        # s' = (m')^d mod n
        signature_blinded = pow(m_blinded, d, n)
        
        print(f"\n--- Подписание ослепленного сообщения ---")
        print(f"  Подпись ослепленного сообщения s' = {signature_blinded}")
        
        return signature_blinded
    
    def unblind_signature(self, signature_blinded):
        """Шаг 3: Снятие ослепления с подписи"""
        if self.keys is None or self.blinding_factor is None:
            raise ValueError("Нет данных для снятия ослепления!")
        
        n = self.keys['n']
        r = self.blinding_factor
        
        # Находим r^{-1} mod n
        r_inv = mod_inverse(r, n)
        
        # s = s' * r^{-1} mod n
        signature = (signature_blinded * r_inv) % n
        
        print(f"\n--- Снятие ослепления ---")
        print(f"  r ^ {-1} mod n = {r_inv}")
        print(f"  Итоговая подпись s = {signature}")
        
        return signature
    
    def verify_signature(self, message, signature):
        """Проверка подписи"""
        if self.keys is None:
            raise ValueError("Ключи не сгенерированы!")
        
        e, n = self.keys['public']
        
        # Хешируем сообщение
        m = hash_message(message) % n
        if m == 0:
            m = 1
        
        # Вычисляем s^e mod n
        m_verified = pow(signature, e, n)
        
        print(f"\n--- Проверка подписи ---")
        print(f"  Хеш сообщения: {m}")
        print(f"  s ^ e mod n = {m_verified}")
        print(f"  Подпись {'✅ ВЕРНА' if m == m_verified else '❌ НЕВЕРНА'}")
        
        return m == m_verified

def demo_blind_signature():
    """Демонстрация работы протокола"""
    print("=" * 60)
    print("ПРОТОКОЛ СЛЕПОЙ ПОДПИСИ RSA (ЧАУМ, 1982)")
    print("=" * 60)
    
    # 1. Создаем экземпляр протокола
    protocol = BlindSignatureRSA()
    
    # 2. Генерируем ключи для подписывающего (Боб)
    print("\n1️⃣  ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA")
    print("-" * 40)
    keys = protocol.setup_keys(bits = 256)  # Для демонстрации берем 256 бит
    
    # 3. Сообщение, которое хочет подписать Алиса
    message = "Голос: Кандидат №42"
    
    print(f"\n2️⃣  АЛИСА ГОТОВИТ СООБЩЕНИЕ К ПОДПИСИ")
    print("-" * 40)
    print(f"  Сообщение: '{message}'")
    
    # 4. Ослепление
    m_blinded = protocol.blind_message(message)
    
    # 5. Боб подписывает ослепленное сообщение
    signature_blinded = protocol.sign_blinded(m_blinded)
    
    # 6. Алиса снимает ослепление
    signature = protocol.unblind_signature(signature_blinded)
    
    # 7. Проверка подписи
    print(f"\n3️⃣  ПРОВЕРКА ПОДПИСИ")
    print("-" * 40)
    is_valid = protocol.verify_signature(message, signature)
    
    # 8. Дополнительная проверка: попытка подделать
    print(f"\n4️⃣  ПРОВЕРКА НА ПОДДЕЛКУ")
    print("-" * 40)
    fake_message = "Голос: Кандидат №13"
    print(f"  Попытка использовать подпись для другого сообщения: '{fake_message}'")
    protocol.verify_signature(fake_message, signature)
    
    # 9. Итоговый вывод
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ")
    print("=" * 60)
    if is_valid:
        print("✅ Слепая подпись успешно создана и проверена!")
        print("   Боб подписал сообщение, не зная его содержимого.")
        print("   Анонимность гарантирована!")
    else:
        print("❌ Ошибка в протоколе!")
    
    print("\n" + "=" * 60)

def demo_ecash_scenario():
    """Демонстрация сценария электронной наличности"""
    print("\n" + "=" * 60)
    print("СЦЕНАРИЙ: ЭЛЕКТРОННАЯ НАЛИЧНОСТЬ (eCash)")
    print("=" * 60)
    
    # Банк
    bank = BlindSignatureRSA()
    bank.setup_keys(bits = 256)
    
    # Покупатель (Алиса)
    print("\n🏦 АЛИСА ПОКУПАЕТ ЦИФРОВУЮ КУПЮРУ В БАНКЕ")
    print("-" * 40)
    
    # Серийный номер купюры
    serial = "SN-2026-0420"
    print(f"  Серийный номер купюры: {serial}")
    
    # Ослепление
    m_blinded = bank.blind_message(serial)
    
    # Банк подписывает (выпускает купюру)
    print("\n🏦 БАНК ПОДПИСЫВАЕТ КУПЮРУ")
    print("  (Банк не видит серийный номер!)")
    signature_blinded = bank.sign_blinded(m_blinded)
    
    # Алиса снимает ослепление
    signature = bank.unblind_signature(signature_blinded)
    
    # Теперь у Алисы есть подписанная банком купюра
    print("\n💰 АЛИСА ПОЛУЧИЛА ПОДПИСАННУЮ КУПЮРУ")
    print(f"  Серийный номер: {serial}")
    print(f"  Подпись банка: {signature}")
    
    # Алиса тратит купюру в магазине
    print("\n🛒 АЛИСА ТРАТИТ КУПЮРУ В МАГАЗИНЕ")
    print("-" * 40)
    
    # Магазин проверяет подпись банка
    print("  Магазин проверяет подпись банка...")
    is_valid = bank.verify_signature(serial, signature)
    
    if is_valid:
        print("  ✅ Купюра подлинная! Товар выдан.")
        print("\n  🔒 АНОНИМНОСТЬ: Банк не знает, что купюра с номером")
        print(f"     {serial} принадлежит Алисе, т.к. он подписал ослепленную версию.")
    else:
        print("  ❌ Подпись недействительна!")

if __name__ == "__main__":
    # Запускаем демонстрацию
    demo_blind_signature()
    demo_ecash_scenario()