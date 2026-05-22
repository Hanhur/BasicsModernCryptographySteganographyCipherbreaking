# 1. Основные понятия
"""
Криптоанализ учебного шифра Цезаря
Демонстрация трех типов атак из конспекта:
1. Анализ с полной информацией (известна пара (m, c))
2. Пассивная атака (только шифртекст)
3. Активная атака (возможность посылать тексты и получать ответы)
"""

import string
from typing import Optional, Dict, Tuple

# ------------------------------------------------------------
# Учебный шифр (Цезарь) - нарочно слабый
# ------------------------------------------------------------
class CaesarCipher:
    """Шифр Цезаря для демонстрации криптоанализа"""
    
    def __init__(self, key: int):
        """
        key: сдвиг от 0 до 25
        """
        self.key = key % 26
        self.alphabet_lower = string.ascii_lowercase
        self.alphabet_upper = string.ascii_uppercase
    
    def encrypt(self, plaintext: str) -> str:
        """Шифрование"""
        result = []
        for ch in plaintext:
            if ch.islower():
                idx = (self.alphabet_lower.index(ch) + self.key) % 26
                result.append(self.alphabet_lower[idx])
            elif ch.isupper():
                idx = (self.alphabet_upper.index(ch) + self.key) % 26
                result.append(self.alphabet_upper[idx])
            else:
                result.append(ch)  # не буквы не меняем
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Дешифрование (обратный сдвиг)"""
        result = []
        for ch in ciphertext:
            if ch.islower():
                idx = (self.alphabet_lower.index(ch) - self.key) % 26
                result.append(self.alphabet_lower[idx])
            elif ch.isupper():
                idx = (self.alphabet_upper.index(ch) - self.key) % 26
                result.append(self.alphabet_upper[idx])
            else:
                result.append(ch)
        return ''.join(result)


# ------------------------------------------------------------
# 1. Атака с полной информацией
# ------------------------------------------------------------
def attack_known_pair(cipher: CaesarCipher, plaintext: str, ciphertext: str) -> Optional[int]:
    """
    Анализ с полной информацией.
    Известно: m (исходный текст) и c = E(m)
    Находим ключ.
    """
    # Берем первую букву в открытом тексте (не пробел и не знак)
    for i in range(len(plaintext)):
        if plaintext[i].isalpha():
            m_char = plaintext[i]
            c_char = ciphertext[i]
            break
    else:
        return None
    
    # Вычисляем сдвиг
    if m_char.islower():
        m_idx = string.ascii_lowercase.index(m_char.lower())
        c_idx = string.ascii_lowercase.index(c_char.lower())
    else:
        m_idx = string.ascii_uppercase.index(m_char.upper())
        c_idx = string.ascii_uppercase.index(c_char.upper())
    
    key = (c_idx - m_idx) % 26
    return key


# ------------------------------------------------------------
# 2. Пассивная атака (только шифртекст)
# ------------------------------------------------------------
def passive_attack_only_ciphertext(ciphertext: str) -> Dict[int, str]:
    """
    Пассивная атака: известен только шифрованный текст.
    Требуется прочитать исходный текст.
    Используем полный перебор (универсальный метод).
    """
    candidates = {}
    for possible_key in range(26):
        test_cipher = CaesarCipher(possible_key)
        # Дешифрование с предполагаемым ключом (обратный сдвиг)
        # Внимание: для дешифрования нужен ключ сдвига, но наш decrypt делает
        # обратный сдвиг от текущего key. Если мы предполагаем key=k, то:
        # Чтобы расшифровать, нужно создать шифр с ключом -k mod 26
        # Проще: пробуем все ключи для дешифрования напрямую
        decrypted = []
        for ch in ciphertext:
            if ch.islower():
                idx = (string.ascii_lowercase.index(ch) - possible_key) % 26
                decrypted.append(string.ascii_lowercase[idx])
            elif ch.isupper():
                idx = (string.ascii_uppercase.index(ch) - possible_key) % 26
                decrypted.append(string.ascii_uppercase[idx])
            else:
                decrypted.append(ch)
        candidates[possible_key] = ''.join(decrypted)
    return candidates


def score_english(text: str) -> float:
    """Очень простая оценка, насколько текст похож на английский"""
    common_letters = set('etaoinshrdlu')
    text_lower = text.lower()
    if not text_lower:
        return 0
    score = sum(1 for ch in text_lower if ch in common_letters) / len(text_lower)
    return score


def best_guess_from_ciphertext(ciphertext: str) -> Tuple[int, str]:
    """Выбирает наиболее вероятный ключ на основе частотного анализа"""
    candidates = passive_attack_only_ciphertext(ciphertext)
    best_key = None
    best_text = ""
    best_score = -1
    for key, text in candidates.items():
        scr = score_english(text)
        if scr > best_score:
            best_score = scr
            best_key = key
            best_text = text
    return best_key, best_text


# ------------------------------------------------------------
# 3. Активная атака
# ------------------------------------------------------------
class Oracle:
    """
    Оракул шифрования: взломщик может посылать любые открытые тексты
    и получать шифртексты.
    """
    def __init__(self, secret_key: int):
        self.cipher = CaesarCipher(secret_key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext)


def active_attack(oracle: Oracle) -> int:
    """
    Активная атака: взломщик специально посылает текст 'a' (или 'A')
    и по полученному шифртексту мгновенно вычисляет ключ.
    """
    # Посылаем специально выбранный открытый текст
    chosen_plain = 'a'   # строчная буква
    cipher_response = oracle.encrypt(chosen_plain)
    
    # Вычисляем ключ
    p_idx = string.ascii_lowercase.index(chosen_plain)
    c_idx = string.ascii_lowercase.index(cipher_response)
    key = (c_idx - p_idx) % 26
    return key


# ------------------------------------------------------------
# Демонстрация работы всех трех атак
# ------------------------------------------------------------
def main():
    print("=" * 60)
    print("КРИПТОАНАЛИЗ УЧЕБНОГО ШИФРА ЦЕЗАРЯ")
    print("Демонстрация атак из конспекта\n")
    
    # Секретный ключ (неизвестен взломщику)
    SECRET_KEY = 7
    cipher = CaesarCipher(SECRET_KEY)
    
    # Исходное сообщение
    plaintext = "attack at dawn"
    ciphertext = cipher.encrypt(plaintext)
    
    print(f"[Секретный ключ]    : {SECRET_KEY}")
    print(f"[Исходный текст]    : {plaintext}")
    print(f"[Шифрованный текст] : {ciphertext}\n")
    
    # --------------------------------------------------------
    # Атака 1: полная информация
    # --------------------------------------------------------
    print("1. АТАКА С ПОЛНОЙ ИНФОРМАЦИЕЙ")
    print("   Известна пара (открытый текст, шифртекст)")
    found_key = attack_known_pair(cipher, plaintext, ciphertext)
    if found_key is not None:
        print(f"   Найден ключ: {found_key}")
        print(f"   Расшифровка: {CaesarCipher(found_key).decrypt(ciphertext)}")
    print()
    
    # --------------------------------------------------------
    # Атака 2: пассивная (только шифртекст)
    # --------------------------------------------------------
    print("2. ПАССИВНАЯ АТАКА")
    print("   Известен только шифртекст")
    best_key, best_text = best_guess_from_ciphertext(ciphertext)
    print(f"   Наиболее вероятный ключ: {best_key}")
    print(f"   Расшифровка: {best_text}")
    print(f"   Успех: {'Да' if best_key == SECRET_KEY else 'Нет'}")
    print()
    
    # --------------------------------------------------------
    # Атака 3: активная (возможность посылать тексты)
    # --------------------------------------------------------
    print("3. АКТИВНАЯ АТАКА")
    print("   Взломщик может посылать свои тексты в оракул")
    oracle = Oracle(SECRET_KEY)
    recovered_key = active_attack(oracle)
    print(f"   Посылаем 'a' -> получаем '{oracle.encrypt('a')}'")
    print(f"   Вычисленный ключ: {recovered_key}")
    print(f"   Точное восстановление: {'Да' if recovered_key == SECRET_KEY else 'Нет'}")
    print()
    
    # --------------------------------------------------------
    # Дополнительно: универсальный метод (полный перебор)
    # --------------------------------------------------------
    print("4. УНИВЕРСАЛЬНЫЙ МЕТОД (полный перебор, как в тексте)")
    print("   Для шифра Цезаря работает мгновенно (26 вариантов)")
    for k in range(26):
        test_cipher = CaesarCipher(k)
        decrypted = test_cipher.decrypt(ciphertext)
        if decrypted == plaintext:
            print(f"   Найден ключ {k}: '{decrypted}'")
            break
    
    print("\n" + "=" * 60)
    print("ВЫВОД (из конспекта):")
    print("- Активная атака — самая мощная для слабых шифров.")
    print("- Универсальный перебор работает, но для хороших шифров")
    print("  (AES, ChaCha20) невозможен за реальное время.")
    print("=" * 60)


if __name__ == "__main__":
    main()