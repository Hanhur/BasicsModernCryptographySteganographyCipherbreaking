# 3. Шифр Виженера
"""
Шифр Виженера и криптоанализ (тест Казиского + частотный анализ)
"""

from collections import Counter
from math import gcd
from itertools import product

# ------------------------------------------------------------
# 1. Базовые функции шифра Виженера
# ------------------------------------------------------------

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
N = 26

def vigenere_encrypt(plaintext: str, key: str) -> str:
    """Шифрование Виженера (текст и ключ — строки A-Z)"""
    plaintext = plaintext.upper().replace(' ', '')
    key = key.upper().replace(' ', '')
    ciphertext = []
    key_len = len(key)
    
    for i, ch in enumerate(plaintext):
        if ch not in ALPHABET:
            ciphertext.append(ch)
            continue
        p = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')
        c = (p + k) % N
        ciphertext.append(chr(c + ord('A')))
    
    return ''.join(ciphertext)

def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Дешифрование Виженера"""
    ciphertext = ciphertext.upper().replace(' ', '')
    key = key.upper().replace(' ', '')
    plaintext = []
    key_len = len(key)
    
    for i, ch in enumerate(ciphertext):
        if ch not in ALPHABET:
            plaintext.append(ch)
            continue
        c = ord(ch) - ord('A')
        k = ord(key[i % key_len]) - ord('A')
        p = (c - k) % N
        plaintext.append(chr(p + ord('A')))
    
    return ''.join(plaintext)

# ------------------------------------------------------------
# 2. Тест Казиского для определения длины ключа
# ------------------------------------------------------------

def kasiski_test(ciphertext: str, min_len = 3, max_len = 20, top_n = 5) -> list:
    """
    Возвращает список возможных длин ключа, отсортированных по вероятности.
    
    ciphertext: шифротекст (только буквы A-Z)
    min_len: минимальная длина повторяющейся подстроки
    max_len: максимальная длина ключа для проверки
    top_n: сколько наиболее вероятных длин вернуть
    """
    ciphertext = ciphertext.upper().replace(' ', '')
    
    # Поиск повторяющихся подстрок
    distances = []
    for length in range(min_len, min(10, len(ciphertext) // 2)):
        seen = {}
        for i in range(len(ciphertext) - length + 1):
            substr = ciphertext[i:i + length]
            if substr in seen:
                dist = i - seen[substr]
                if dist > 0:
                    distances.append(dist)
            else:
                seen[substr] = i
    
    if not distances:
        return list(range(2, min(max_len + 1, 20)))  # нет повторов — пробуем всё
    
    # Подсчёт НОД расстояний
    gcd_counts = Counter()
    for d in distances:
        for candidate_len in range(2, max_len + 1):
            if d % candidate_len == 0:
                gcd_counts[candidate_len] += 1
    
    # Сортировка по частоте
    most_likely = [l for l, _ in gcd_counts.most_common(top_n)]
    return most_likely if most_likely else list(range(2, max_len + 1))

# ------------------------------------------------------------
# 3. Восстановление ключа (частотный анализ)
# ------------------------------------------------------------

# Частоты букв в английском языке (в порядке убывания)
ENGLISH_FREQ = [
    'E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 
    'L', 'C', 'U', 'M', 'W', 'F', 'G', 'Y', 'P', 'B', 
    'V', 'K', 'J', 'X', 'Q', 'Z'
]

def shift_letter(letter: str, shift: int) -> str:
    """Сдвиг буквы на shift (0-25)"""
    idx = (ord(letter) - ord('A') + shift) % N
    return chr(idx + ord('A'))

def find_shift_for_column(text_col: str) -> int:
    """
    Находит наиболее вероятный сдвиг для столбца (буквы, зашифрованные одним
    символом ключа) с помощью частотного анализа.
    """
    col = [ch for ch in text_col if ch in ALPHABET]
    if not col:
        return 0
    
    # Считаем частоты букв в столбце
    freq = Counter(col)
    
    best_shift = 0
    best_score = -1
    
    # Для каждого возможного сдвига (0..25)
    for shift in range(N):
        score = 0
        # Расшифровываем столбец этим сдвигом и сравниваем с частотностью английского
        for ch, count in freq.items():
            # Буква в открытом тексте (если сдвиг = shift)
            pt_idx = (ord(ch) - ord('A') - shift) % N
            pt_letter = chr(pt_idx + ord('A'))
            # Даём очки, если эта буква частая в английском
            # (вес = 1/позиция в частотном списке, упрощённо)
            try:
                pos = ENGLISH_FREQ.index(pt_letter)
                score += count * (len(ENGLISH_FREQ) - pos)
            except ValueError:
                pass
        if score > best_score:
            best_score = score
            best_shift = shift
    
    return best_shift

def recover_key(ciphertext: str, key_length: int) -> str:
    """Восстанавливает ключ заданной длины методом частотного анализа"""
    ciphertext = ciphertext.upper().replace(' ', '')
    key = []
    
    for col_idx in range(key_length):
        # Собираем все буквы из этого столбца
        column = [ciphertext[i] for i in range(col_idx, len(ciphertext), key_length) if ciphertext[i] in ALPHABET]
        shift = find_shift_for_column(column)
        key.append(chr(shift + ord('A')))
    
    return ''.join(key)

# ------------------------------------------------------------
# 4. Демонстрация работы
# ------------------------------------------------------------

if __name__ == '__main__':
    # Пример из вашего текста (Тютчев + ключ 17,9,3,8)
    plaintext = "ASMOKEOFMOTHERLANDISSWEETFORUSANDPLEASANT"
    key = "RJDK"  # R=17, J=9, D=3, K=8
    
    print("=" * 50)
    print("ШИФР ВИЖЕНЕРА — ДЕМОНСТРАЦИЯ")
    print("=" * 50)
    print(f"Открытый текст: {plaintext}")
    print(f"Ключ: {key} (R=17, J=9, D=3, K=8)")
    
    cipher = vigenere_encrypt(plaintext, key)
    print(f"Шифротекст: {cipher}")
    
    # Проверка дешифрования
    decrypted = vigenere_decrypt(cipher, key)
    print(f"Расшифровано: {decrypted}")
    print(f"Успех: {decrypted == plaintext}")
    
    print("\n" + "=" * 50)
    print("КРИПТОАНАЛИЗ (только шифротекст)")
    print("=" * 50)
    
    # Тест Казиского
    print("1. Тест Казиского (поиск длины ключа):")
    possible_lengths = kasiski_test(cipher, min_len = 3, max_len = 10)
    print(f"   Наиболее вероятные длины ключа: {possible_lengths}")
    
    # Восстановление ключа для предполагаемой длины
    print("\n2. Восстановление ключа частотным анализом:")
    for L in possible_lengths[:3]:  # пробуем топ-3 длины
        recovered = recover_key(cipher, L)
        print(f"   Длина {L}: восстановленный ключ = {recovered}")
        # Если восстановили исходный ключ — покажем
        if recovered == key:
            print(f"   >>> ТОЧНОЕ СОВПАДЕНИЕ с исходным ключом! <<<")
            break
        else:
            # Попробуем расшифровать этим ключом
            dec = vigenere_decrypt(cipher, recovered)
            # Покажем первые 50 символов для оценки
            print(f"      Расшифровка (начало): {dec[:60]}...")
    
    # Дополнительно: если ключ известен, можно его проверить
    print("\n3. Проверка с исходным ключом:")
    decrypted_full = vigenere_decrypt(cipher, key)
    print(f"   Расшифровка исходным ключом: {decrypted_full}")