# Замечания по протоколу слепой подписи
import random
import hashlib
import math

# ============================================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ RSA
# ============================================================================

def gcd_extended(a, b):
    """Расширенный алгоритм Евклида для обратного элемента по модулю."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd_extended(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inv(a, m):
    """Обратное число по модулю m."""
    g, x, _ = gcd_extended(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента не существует: gcd({a}, {m}) = {g}")
    return x % m

def is_prime(n, k = 5):
    """Простая проверка на простоту (Миллер-Рабин) для малых чисел."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_rsa_keys(bits = 8):
    """Генерация ключей RSA (маленькие простые числа для наглядности)."""
    while True:
        p = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(p):
            break
    while True:
        q = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(q) and q != p:
            break
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e = 65537 или маленькое, если не подходит
    e = 65537
    if math.gcd(e, phi) != 1:
        e = 17
        while math.gcd(e, phi) != 1:
            e += 2
    
    d = mod_inv(e, phi)
    return (e, n), (d, n)

# ============================================================================
# 2. ПРОТОКОЛ СЛЕПОЙ ПОДПИСИ (БАЗОВЫЙ)
# ============================================================================

class BlindSignatureProtocol:
    """
    Реализует протокол слепой подписи RSA.
    Алиса (подписывающая) имеет ключи (e, n) и (d, n).
    Боб (пользователь) хочет получить подпись на сообщение M, не раскрывая его.
    """
    
    def __init__(self, public_key, private_key):
        self.e, self.n = public_key
        self.d, self.n = private_key  # n совпадает
    
    def alice_sign_blind(self, blinded_message):
        """
        Алиса подписывает ослеплённое сообщение.
        Она НЕ ЗНАЕТ, что внутри.
        """
        signature = pow(blinded_message, self.d, self.n)
        return signature
    
    @staticmethod
    def bob_prepare_message(message, e, n):
        """
        Боб готовит сообщение к слепой подписи.
        Возвращает: (blinded_message, k, original_message)
        """
        # Проверка: M не должно быть 0 (иначе тривиальная атака)
        if message == 0:
            raise ValueError("Сообщение M=0 запрещено (тривиальная подпись)")
        
        # Генерируем случайное k, взаимно простое с n
        while True:
            k = random.randint(2, n - 1)
            if math.gcd(k, n) == 1:
                break
        
        # Ослепление: t = M * k^e mod n
        k_e = pow(k, e, n)
        blinded = (message * k_e) % n
        
        return blinded, k, message
    
    @staticmethod
    def bob_unblind_signature(blinded_signature, k, n):
        """
        Боб снимает ослепление с подписи: V = S / k mod n
        """
        k_inv = mod_inv(k, n)
        signature = (blinded_signature * k_inv) % n
        return signature
    
    @staticmethod
    def verify_signature(message, signature, e, n):
        """Проверка подписи: signature ^ e == message (mod n)"""
        return pow(signature, e, n) == message

# ============================================================================
# 3. ДЕМОНСТРАЦИЯ АТАК, ОПИСАННЫХ В ТЕКСТЕ
# ============================================================================

def demo_trivial_attack_m0():
    """Атака: M = 0 → подпись всегда 0, Алиса видит ослеплённое сообщение."""
    print("\n" + "=" * 70)
    print("3.1. АТАКА: M = 0 (тривиальная подпись)")
    print("=" * 70)
    
    pub, priv = generate_rsa_keys(bits = 8)
    protocol = BlindSignatureProtocol(pub, priv)
    
    message = 0
    try:
        blinded, k, _ = protocol.bob_prepare_message(message, pub[0], pub[1])
        print(f"  Ослеплённое сообщение t = {blinded} (при M = 0)")
        print(f"  Алиса видит t = 0 и сразу понимает, что M = 0")
        print("  [ЗАЩИТА] Протокол должен запрещать M = 0")
    except ValueError as e:
        print(f"  [ЗАЩИТА СРАБОТАЛА] {e}")

def demo_small_k_attack():
    """
    Атака малого k ^ e.
    Если k ^ e < n / M, то t = M * k ^ e без оборачивания по модулю.
    Атакующий восстанавливает M простым делением.
    """
    print("\n" + "=" * 70)
    print("3.2. АТАКА МАЛОГО k ^ e (восстановление сообщения)")
    print("=" * 70)
    
    # Используем маленький модуль для наглядности
    pub, priv = generate_rsa_keys(bits = 8)
    e, n = pub
    print(f"  Параметры RSA: e = {e}, n = {n}")
    
    # Боб готовит сообщение
    message = 42
    print(f"  Исходное сообщение M = {message}")
    
    # Принудительно ищем малое k^e
    print("  Ищем k такое, что k ^ e mod n < n // message ...")
    found_small = False
    for attempt in range(1, 500):
        k = attempt
        if math.gcd(k, n) != 1:
            continue
        k_e = pow(k, e, n)
        if k_e < n // message and k_e > 1:
            found_small = True
            print(f"  Найдено! k = {k}, k ^ e mod n = {k_e} (малое число)")
            
            # Моделируем атаку (злоумышленник видит только t и знает n, e)
            t = (message * k_e) % n
            
            # Так как t = M * k_e (без оборачивания), делим
            if t % k_e == 0:
                recovered = t // k_e
                print(f"  АТАКА УСПЕШНА: восстановлено M = {recovered}")
                print(f"  t = {t}, делим на {k_e} -> {recovered}")
            else:
                print("  Оборачивание всё же произошло, атака не удалась")
            break
    
    if not found_small:
        print("  Не удалось найти малое k ^ e для этого модуля (попробуйте перезапустить)")

def demo_factorization_misconception():
    """
    ДЕМОНСТРАЦИЯ ОШИБКИ из текста:
    "t — это произведение [X ⋅ Y]: X = M1 ← задача факторизации; Y = k ^ e"
    
    Показываем, что факторизация t как целого числа НЕ даёт M1.
    """
    print("\n" + "=" * 70)
    print("3.3. ОПРОВЕРЖЕНИЕ: факторизация t НЕ раскрывает M")
    print("=" * 70)
    
    # Боб готовит сообщение
    pub, priv = generate_rsa_keys(bits = 12)
    e, n = pub
    protocol = BlindSignatureProtocol(pub, priv)
    
    message = 12345
    blinded, k, _ = protocol.bob_prepare_message(message, e, n)
    
    k_e = pow(k, e, n)
    product_mod = (message * k_e) % n
    
    print(f"  M = {message}")
    print(f"  k ^ e mod n = {k_e}")
    print(f"  t = (M * k ^ e) mod n = {blinded}")
    print()
    print(f"  Если разложить t = {blinded} на множители (как целое число):")
    
    # Простая факторизация (для малых чисел)
    def factor_small(x):
        factors = []
        d = 2
        while d * d <= x:
            while x % d == 0:
                factors.append(d)
                x //= d
            d += 1 if d == 2 else 2
        if x > 1:
            factors.append(x)
        return factors
    
    factors = factor_small(blinded)
    print(f"  Множители t: {factors}")
    print()
    print("  ❗ Среди множителей НЕТ ни M = {message}, ни k ^ e = {k_e}!")
    print("  Потому что t — это остаток по модулю, а не произведение в целых числах.")
    print("  Формула t = M * k ^ e (без mod) — математически неверна.")

def demo_verification_check():
    """Демонстрация корректной проверки подписи."""
    print("\n" + "=" * 70)
    print("3.4. КОРРЕКТНАЯ ПРОВЕРКА ПОДПИСИ (V = S/k)")
    print("=" * 70)
    
    pub, priv = generate_rsa_keys(bits = 8)
    protocol = BlindSignatureProtocol(pub, priv)
    
    message = 42
    print(f"  Сообщение M = {message}")
    
    # Боб готовит и подписывает
    blinded, k, _ = protocol.bob_prepare_message(message, pub[0], pub[1])
    blind_sig = protocol.alice_sign_blind(blinded)
    
    # Боб снимает ослепление
    signature = protocol.bob_unblind_signature(blind_sig, k, pub[1])
    
    # Проверка
    is_valid = protocol.verify_signature(message, signature, pub[0], pub[1])
    print(f"  Подпись: S = {signature}")
    print(f"  Проверка: S ^ e mod n = {pow(signature, pub[0], pub[1])} == M? {is_valid}")
    print(f"  ✅ Подпись корректна, Алиса не узнала M (она видела только {blinded})")

def demo_zero_knowledge_analogy():
    """Аналогия с доказательствами с нулевым разглашением."""
    print("\n" + "=" * 70)
    print("3.5. АНАЛОГИЯ С ZKP (доказательства с нулевым разглашением)")
    print("=" * 70)
    
    print("""
    Элемент протокола              Аналог в ZKP
    ──────────────────────────────────────────────────────────────
    Случайное k                    Слепящий фактор (commitment)
    Ослепление t = M * k ^ e         Маскировка секрета
    Подпись Алисы S = t ^ d          Ответ на вызов (challenge response)
    Снятие маски V = S / k         Раскрытие (reveal) без потери секрета
    Проверка V ^ e == M              Верификация без знания исходного M
    """)

# ============================================================================
# 4. ЗАЩИЩЁННЫЙ ПРОТОКОЛ (с проверкой размера k^e)
# ============================================================================

class SecureBlindSignature(BlindSignatureProtocol):
    """
    Расширенный протокол с защитой от атаки малого k^e.
    """
    
    @staticmethod
    def bob_prepare_message_secure(message, e, n, min_k_e_size = None):
        """
        Боб готовит сообщение, но проверяет, что k^e достаточно большое.
        """
        if message == 0:
            raise ValueError("M = 0 запрещено")
        
        if min_k_e_size is None:
            min_k_e_size = n // (message * 10) if message > 0 else n // 100
        
        max_attempts = 1000
        for attempt in range(max_attempts):
            k = random.randint(2, n - 1)
            if math.gcd(k, n) != 1:
                continue
            
            k_e = pow(k, e, n)
            
            # Защита: k^e должно быть достаточно большим, чтобы исключить простое деление
            if k_e > min_k_e_size and k_e > 10:
                blinded = (message * k_e) % n
                return blinded, k, message
        
        raise RuntimeError(f"Не удалось найти безопасное k за {max_attempts} попыток")

# ============================================================================
# 5. ГЛАВНАЯ ДЕМОНСТРАЦИЯ
# ============================================================================

def main():
    print("=" * 70)
    print(" АНАЛИЗ ПРОТОКОЛА СЛЕПОЙ ПОДПИСИ RSA")
    print(" Демонстрация уязвимостей и защит")
    print("=" * 70)
    
    # Установим seed для воспроизводимости (но можно убрать)
    random.seed(42)
    
    demo_trivial_attack_m0()
    demo_small_k_attack()
    demo_factorization_misconception()
    demo_verification_check()
    demo_zero_knowledge_analogy()
    
    print("\n" + "=" * 70)
    print(" ЗАЩИЩЁННЫЙ ПРОТОКОЛ (SecureBlindSignature)")
    print("=" * 70)
    
    pub, priv = generate_rsa_keys(bits = 10)
    secure_protocol = SecureBlindSignature(pub, priv)
    
    message = 100
    print(f"  Сообщение: M = {message}")
    
    try:
        blinded, k, _ = secure_protocol.bob_prepare_message_secure(message, pub[0], pub[1])
        print(f"  Ослеплённое сообщение: t = {blinded}")
        print(f"  k = {k}, k ^ e mod n = {pow(k, pub[0], pub[1])}")
        
        blind_sig = secure_protocol.alice_sign_blind(blinded)
        sig = secure_protocol.bob_unblind_signature(blind_sig, k, pub[1])
        
        valid = secure_protocol.verify_signature(message, sig, pub[0], pub[1])
        print(f"  Подпись: S = {sig}")
        print(f"  Проверка: {'✅ УСПЕШНО' if valid else '❌ ОШИБКА'}")
        print("  Защита от малого k ^ e применена (k ^ e проверено на минимальный размер)")
        
    except Exception as e:
        print(f"  Ошибка: {e}")

if __name__ == "__main__":
    main()