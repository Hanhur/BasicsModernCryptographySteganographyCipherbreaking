# 5. Роторные машины
import random
import string
from collections import Counter, defaultdict
from itertools import cycle

# -------------------------------
# 1. Вспомогательные функции
# -------------------------------

def generate_random_substitution(alphabet):
    """Генерирует случайную подстановку на алфавите."""
    shuffled = list(alphabet)
    random.shuffle(shuffled)
    return dict(zip(alphabet, shuffled))

def inverse_substitution(subst):
    """Обратная подстановка для расшифрования."""
    return {v: k for k, v in subst.items()}

def apply_substitution(text, subst):
    """Применяет подстановку к тексту."""
    return ''.join(subst.get(ch, ch) for ch in text)

# -------------------------------
# 2. Шифрование и дешифрование
# -------------------------------

class RotorCipher:
    def __init__(self, substitutions):
        """
        substitutions: список словарей {символ: символ}
        для каждого потока (ключа).
        """
        self.substitutions = substitutions
        self.inverse_subs = [inverse_substitution(s) for s in substitutions]
        self.t = len(substitutions)

    def encrypt(self, plaintext):
        result = []
        for i, ch in enumerate(plaintext):
            rotor_idx = i % self.t
            result.append(self.substitutions[rotor_idx].get(ch, ch))
        return ''.join(result)

    def decrypt(self, ciphertext):
        result = []
        for i, ch in enumerate(ciphertext):
            rotor_idx = i % self.t
            result.append(self.inverse_subs[rotor_idx].get(ch, ch))
        return ''.join(result)

# -------------------------------
# 3. Криптоанализ (взлом)
# -------------------------------

def kasiski_test(ciphertext, max_key_len = 20, min_repeat = 3):
    """
    Определяет вероятную длину ключа t по тесту Казисского.
    Возвращает список вероятных длин (от самой вероятной).
    """
    repeats = defaultdict(list)

    # Поиск повторяющихся подстрок длины 3-5
    for length in range(3, 6):
        for i in range(len(ciphertext) - length):
            sub = ciphertext[i:i + length]
            if len(sub) < length:
                continue
            repeats[sub].append(i)

    distances = []
    for positions in repeats.values():
        if len(positions) >= min_repeat:
            for k in range(len(positions) - 1):
                dist = positions[k + 1] - positions[k]
                distances.append(dist)

    # Подсчёт множителей расстояний
    factor_counts = defaultdict(int)
    for d in distances:
        for factor in range(2, max_key_len + 1):
            if d % factor == 0:
                factor_counts[factor] += 1

    # Сортируем по убыванию частоты
    sorted_factors = sorted(factor_counts.items(), key = lambda x: -x[1])
    return [f for f, _ in sorted_factors]

def frequency_attack_for_single_stream(chunk, alphabet, top_n = 5):
    """
    Для одного потока (зашифрованного одной подстановкой)
    пытается найти наиболее вероятное соответствие букв.
    Возвращает словарь подстановки (cipher -> plain).
    """
    # Английские частоты букв (в порядке убывания)
    english_freq_order = 'etaoin shrdlu'.replace(' ', '')  # 'etaoinshrdlu'

    # Частотный анализ шифротекста
    counter = Counter(chunk)
    # Убираем символы не из алфавита
    counter = {ch: cnt for ch, cnt in counter.items() if ch in alphabet}
    sorted_cipher_chars = sorted(counter.items(), key = lambda x: -x[1])
    cipher_order = [ch for ch, _ in sorted_cipher_chars]

    # Предполагаем отображение: самая частая буква шифротекста -> 'e', вторая -> 't', и т.д.
    substitution = {}
    for i, c_ch in enumerate(cipher_order):
        if i < len(english_freq_order):
            substitution[c_ch] = english_freq_order[i]
        else:
            # Остальные сопоставляем случайно (или просто оставляем неизвестными)
            # Лучше: оставить как есть или не использовать.
            pass

    # Дополняем отображение для букв, не попавших в top
    for ch in alphabet:
        if ch not in substitution:
            # Неизвестное отображение -> оставляем как было? Нет, подстановка должна быть биекцией.
            # Для простоты сопоставим себе (но это неверно криптоаналитически).
            # В реальном анализе мы бы строили полную замену вручную.
            substitution[ch] = ch

    return substitution

def cryptanalyze_rotor(ciphertext, alphabet, max_key_len = 20):
    """
    Взламывает роторный шифр:
    1. Определяет длину ключа (тест Казисского)
    2. Для каждого потока делает частотный анализ
    3. Расшифровывает текст
    """
    possible_lengths = kasiski_test(ciphertext, max_key_len)

    best_length = None
    best_plaintext = ""

    for t in possible_lengths[:3]:  # пробуем топ-3 длины
        # Разбиваем на t потоков
        streams = [[] for _ in range(t)]
        for idx, ch in enumerate(ciphertext):
            streams[idx % t].append(ch)

        # Восстанавливаем подстановки для каждого потока
        substitutions = []
        for stream in streams:
            stream_str = ''.join(stream)
            sub = frequency_attack_for_single_stream(stream_str, alphabet)
            substitutions.append(sub)

        # Расшифровываем по найденным подстановкам
        decrypted = []
        for idx, ch in enumerate(ciphertext):
            rotor_idx = idx % t
            # Применяем ОБРАТНУЮ подстановку, чтобы получить открытый текст
            inv_sub = {v: k for k, v in substitutions[rotor_idx].items()}
            decrypted.append(inv_sub.get(ch, ch))

        plain_candidate = ''.join(decrypted)

        # Проверка качества (например, количество слов в словаре)
        # Упрощённо: берём первую найденную длину
        if not best_plaintext or len(set(plain_candidate)) > len(set(best_plaintext)):
            best_length = t
            best_plaintext = plain_candidate

    return best_length, best_plaintext

# -------------------------------
# 4. Демонстрация работы
# -------------------------------

if __name__ == "__main__":
    alphabet = string.ascii_lowercase
    # Генерируем случайные подстановки для ротора (длина ключа t=5)
    t = 5
    substitutions = [generate_random_substitution(alphabet) for _ in range(t)]

    cipher = RotorCipher(substitutions)

    # Исходный текст (длинный для качественного анализа)
    plaintext = """
        it was the best of times it was the worst of times it was the age of wisdom
        it was the age of foolishness it was the epoch of belief it was the epoch
        of incredulity it was the season of light it was the season of darkness
        it was the spring of hope it was the winter of despair we had everything
        before us we had nothing before us we were all going direct to heaven
        we were all going direct the other way
    """.replace('\n', ' ').replace(' ', '').lower()

    # Очистка от не-букв
    plaintext = ''.join(ch for ch in plaintext if ch in alphabet)

    print("Исходный текст (первые 100 символов):")
    print(plaintext[:100], "...\n")

    ciphertext = cipher.encrypt(plaintext)
    print("Зашифрованный текст (первые 100 символов):")
    print(ciphertext[:100], "...\n")

    # Криптоанализ
    guessed_len, recovered_plain = cryptanalyze_rotor(ciphertext, alphabet, max_key_len = 15)

    print(f"Предполагаемая длина ключа: {guessed_len}")
    print("Восстановленный открытый текст (первые 200 символов):")
    print(recovered_plain[:200])
    print("\nОригинал (первые 200 символов):")
    print(plaintext[:200])

    # Проверка совпадения (упрощённо)
    match = sum(1 for a, b in zip(plaintext, recovered_plain) if a == b) / len(plaintext)
    print(f"\nТочность восстановления: {match * 100:.2f}%")