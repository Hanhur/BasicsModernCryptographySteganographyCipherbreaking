# Слепая подпись в RSA
"""
Слепая подпись RSA
Реализация на чистом Python без использования numpy
"""

def egcd(a, b):
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    """Находит обратное число по модулю m"""
    gcd, x, _ = egcd(a, m)
    if gcd != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    return x % m

def mod_pow(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю
    (base^exponent) % modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # Если текущий бит равен 1
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Переход к следующему биту
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result

def print_separator(char = '=', length = 60):
    """Выводит разделительную линию"""
    print(char * length)

def main():
    print("=" * 70)
    print("СЛЕПАЯ ПОДПИСЬ RSA - ПРИМЕР РЕАЛИЗАЦИИ")
    print("=" * 70)
    
    # ========== ШАГ 1: Параметры Алисы ==========
    print("\n[ШАГ 1] Алиса генерирует ключи RSA")
    print_separator('-')
    
    pA = 67
    qA = 101
    e = 17
    
    NA = pA * qA
    phi = (pA - 1) * (qA - 1)
    
    print(f"pA = {pA}")
    print(f"qA = {qA}")
    print(f"NA = pA * qA = {NA}")
    print(f"φ(NA) = (pA-1) * (qA-1) = {phi}")
    print(f"e = {e}")
    
    # Вычисляем закрытый ключ dA
    dA = mod_inverse(e, phi)
    print(f"dA = e ^ (-1) mod φ(NA) = {dA}")
    print(f"Проверка: {e} * {dA} = {e * dA} ≡ 1 mod {phi}")
    
    # ========== ШАГ 2: Боб ослепляет сообщение ==========
    print("\n[ШАГ 2] Боб ослепляет сообщение")
    print_separator('-')
    
    M1 = 88  # Секрет Боба
    k = 29   # Случайное число
    
    print(f"M1 (секрет Боба) = {M1}")
    print(f"k (случайное число) = {k}")
    
    # Вычисляем t = M1 * k^e mod NA
    k_pow_e = mod_pow(k, e, NA)
    t = (M1 * k_pow_e) % NA
    
    print(f"k ^ e mod NA = {k_pow_e}")
    print(f"t = M1 * k ^ e mod NA = {t}")
    print(f"Боб отправляет Алисе t = {t}")
    
    # ========== ШАГ 3: Алиса создает слепую подпись ==========
    print("\n[ШАГ 3] Алиса создает слепую подпись")
    print_separator('-')
    
    S = mod_pow(t, dA, NA)
    print(f"S = t ^ dA mod NA = {S}")
    print(f"Алиса отправляет Бобу S = {S}")
    
    # ========== ШАГ 4: Боб снимает ослепление ==========
    print("\n[ШАГ 4] Боб снимает ослепление")
    print_separator('-')
    
    # Находим обратное к k по модулю NA
    k_inv = mod_inverse(k, NA)
    print(f"k ^ (-1) mod NA = {k_inv}")
    print(f"Проверка: {k} * {k_inv} = {k * k_inv} ≡ 1 mod {NA}")
    
    # Вычисляем V = S * k^(-1) mod NA
    V = (S * k_inv) % NA
    print(f"V = S * k ^ (-1) mod NA = {V}")
    
    # ========== ШАГ 5: Проверка подписи ==========
    print("\n[ШАГ 5] Проверка подписи")
    print_separator('-')
    
    V_pow_e = mod_pow(V, e, NA)
    print(f"V ^ e mod NA = {V_pow_e}")
    print(f"M1 = {M1}")
    
    print_separator('-')
    if V_pow_e == M1:
        print("✅ РЕЗУЛЬТАТ: ИСТИНА - Подпись верна!")
        print(f"✅ {V} ^ {e} ≡ {M1} (mod {NA})")
        print("\nБоб может быть уверен, что подпись поставлена Алисой.")
        print("Алиса подтверждает, что секрет (лекарство от рака) принадлежит Бобу.")
    else:
        print("❌ РЕЗУЛЬТАТ: ЛОЖЬ - Подпись неверна!")
    
    # ========== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ==========
    print("\n" + "=" * 70)
    print("ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ВСЕХ ВЫЧИСЛЕНИЙ")
    print("=" * 70)
    
    print(f"\nПроверка t = M1 * k ^ e mod NA:")
    print(f"  {M1} * {k_pow_e} = {M1 * k_pow_e}")
    print(f"  {M1 * k_pow_e} mod {NA} = {t}")
    
    print(f"\nПроверка S = t ^ dA mod NA:")
    print(f"  t ^ dA mod NA = {S}")
    
    print(f"\nПроверка V = S * k ^ (-1) mod NA:")
    print(f"  {S} * {k_inv} = {S * k_inv}")
    print(f"  {S * k_inv} mod {NA} = {V}")
    
    print(f"\nПроверка V ^ e ≡ M1 (mod NA):")
    print(f"  {V} ^ {e} mod {NA} = {V_pow_e}")
    print(f"  {V_pow_e} ≡ {M1} (mod {NA}) - {'✅' if V_pow_e == M1 else '❌'}")
    
    print("\n" + "=" * 70)
    print("ПРОТОКОЛ ЗАВЕРШЕН")
    print("=" * 70)

if __name__ == "__main__":
    main()