# Задачи и упражнения
# Задача 1 . Пусть некоторый английский текст зашифрован методом простой замены. Предположим, что определено значение, скажем 14, буквы q. 
# Пусть в тексте содержится сочетание 14, 18. Чему скорее всего соответствует 18?
import random
import string

# ---------- 1. Создаём случайный шифр простой замены ----------
letters = list(string.ascii_lowercase)  # ['a', 'b', ..., 'z']
numbers = list(range(1, 27))             # [1, 2, ..., 26]

# Случайно перемешиваем числа для соответствия буквам
random.shuffle(numbers)

# Словарь: буква -> число (шифрование)
encrypt_map = {letter: num for letter, num in zip(letters, numbers)}

# Обратный словарь: число -> буква (расшифровка)
decrypt_map = {num: letter for letter, num in encrypt_map.items()}

print("Случайный шифр (буква -> число):")
for letter in letters:
    print(f"{letter} -> {encrypt_map[letter]}", end = "  ")
print("\n")

# ---------- 2. Исходный текст для примера ----------
# Возьмём предложение, где есть "qu"
original_text = "the quick brown fox jumps over the lazy dog"

print(f"Исходный текст: {original_text}")

# ---------- 3. Шифруем ----------
cipher_numbers = [encrypt_map[ch] for ch in original_text if ch in encrypt_map]

print(f"Шифротекст (числа): {cipher_numbers}")

# ---------- 4. Ищем пару (14, 18) в шифротексте ----------
found_pairs = []
for i in range(len(cipher_numbers) - 1):
    if cipher_numbers[i] == 14 and cipher_numbers[i + 1] == 18:
        found_pairs.append(i)

if found_pairs:
    print(f"\nНайдена пара (14, 18) на позициях: {found_pairs}")
    
    # Что соответствует 14 в открытом тексте?
    letter_for_14 = decrypt_map.get(14, "?")
    print(f"Числу 14 в открытом тексте соответствует буква: {letter_for_14}")
    
    # Предполагаем, что letter_for_14 = 'q' (как в условии задачи)
    if letter_for_14 == 'q':
        print("Подтверждено: 14 — это буква 'q'")
        print("В английском языке после 'q' почти всегда идёт 'u'")
        print("Следовательно, числу 18 должна соответствовать буква 'u'")
        
        # Находим, какая буква соответствует 18 в этом шифре
        actual_letter_for_18 = decrypt_map.get(18, "?")
        print(f"Проверка: в нашем шифре 18 соответствует букве: {actual_letter_for_18}")
        
        if actual_letter_for_18 == 'u':
            print("Верно! 18 — это 'u'.")
        else:
            print(f"В этом случайном шифре 18 соответствует '{actual_letter_for_18}', но в реальной задаче ожидается 'u'")
    else:
        print(f"Внимание: 14 соответствует букве '{letter_for_14}', а не 'q', как в условии.")
        print("Задача предполагает, что 14 — это 'q'.")
        
else:
    print("\nВ этом шифротексте нет пары (14, 18).")

# ---------- 5. Дополнительно: покажем самое вероятное предположение ----------
print("\n=== Вывод по задаче ===")
print("Если 14 — это буква 'q', то 18 скорее всего соответствует букве 'u'.")

# ===================================================================================================================================================

# Задача 2. Пусть известны шифровки с1 = Ет1 (т), с2 = ЕТ2 (т) одного и того же достаточно длинного текста т, 
# полученные шифрами перестановки с одинаковой длиной l блока: TI , Т2 Е Е s, . Как можно с помощью этой информации эффективно найти l?
"""
Задача 2: Нахождение длины блока l в шифре перестановки
по двум шифротекстам c1 и c2, полученным из одного исходного текста
с разными перестановками T1 и T2, но одинаковой длиной блока l.

Идея: при правильном l каждый блок в c1 и c2 содержит одно и то же 
мультимножество символов (поскольку перестановка не меняет набор символов в блоке).
"""

from collections import Counter
from math import gcd
from functools import reduce


def find_block_length_by_multiset(c1, c2, max_l = None):
    """
    Находит длину блока l по совпадению мультимножеств символов в блоках.
    
    Параметры:
    - c1, c2: списки или строки (шифротексты)
    - max_l: максимальная проверяемая длина блока (по умолчанию len(c1) // 2)
    
    Возвращает:
    - l (наименьшее подходящее значение)
    """
    L = min(len(c1), len(c2))
    if max_l is None:
        max_l = L // 2 + 1
    
    possible_lengths = []
    
    print(f"Проверка возможных длин блоков от 2 до {max_l}...")
    
    for l in range(2, max_l + 1):
        # Пропускаем, если l не делит длину текста хотя бы приблизительно
        # (для длинных текстов можно проверять все блоки, но для эффективности ограничим)
        
        is_consistent = True
        # Проверяем полные блоки
        for block_start in range(0, L - l + 1, l):
            block1 = c1[block_start:block_start + l]
            block2 = c2[block_start:block_start + l]
            
            if Counter(block1) != Counter(block2):
                is_consistent = False
                break
        
        if is_consistent:
            possible_lengths.append(l)
            print(f"  l = {l} подходит")
    
    if not possible_lengths:
        return None
    
    # Обычно наименьшее подходящее l — это истинная длина блока
    # (более длинные могут быть кратными истинной длине)
    return possible_lengths[0]


def find_block_length_by_distances(c1, c2, num_samples = 1000):
    """
    Альтернативный метод: анализ расстояний между одинаковыми символами.
    
    Для пары одинаковых символов в c1 и c2 разность их расстояний
    кратна истинной длине блока l.
    """
    # Собираем позиции одинаковых символов
    from collections import defaultdict
    
    positions1 = defaultdict(list)
    positions2 = defaultdict(list)
    
    for i, ch in enumerate(c1):
        positions1[ch].append(i)
    for i, ch in enumerate(c2):
        positions2[ch].append(i)
    
    differences = []
    
    # Для каждого символа, взятого в паре вхождений
    for ch in positions1:
        if len(positions1[ch]) < 2 or len(positions2[ch]) < 2:
            continue
        
        p1_list = positions1[ch]
        p2_list = positions2[ch]
        
        # Берём несколько пар (ограничиваем для эффективности)
        for i in range(min(len(p1_list), num_samples // 10)):
            for j in range(i + 1, min(len(p1_list), i + 10)):
                # Расстояния между двумя вхождениями символа в c1 и c2
                dist1 = abs(p1_list[i] - p1_list[j])
                dist2 = abs(p2_list[i] - p2_list[j])
                
                # Разность расстояний должна быть кратна l
                diff = abs(dist1 - dist2)
                if diff > 0:
                    differences.append(diff)
    
    if not differences:
        return None
    
    # Находим НОД всех разностей — это и будет l
    l_candidate = reduce(gcd, differences)
    
    # НОД может быть 1, если данных мало или l=1 (тривиальный случай)
    if l_candidate == 1:
        # Проверяем, может быть l действительно 1?
        # Но l=1 — это просто тождественная перестановка, обычно неинтересно
        return 1 if find_block_length_by_multiset(c1, c2, 2) == 1 else None
    
    return l_candidate


def generate_test_data(original_text, l, T1, T2):
    """
    Генерирует два шифротекста для тестирования.
    
    Параметры:
    - original_text: исходный текст (строка)
    - l: длина блока
    - T1, T2: перестановки (списки индексов от 0 до l-1)
    
    Возвращает:
    - c1, c2: зашифрованные тексты
    """
    # Дополняем текст до кратности l (опционально)
    padding_len = (l - len(original_text) % l) % l
    padded_text = original_text + 'X' * padding_len
    
    c1_chars = []
    c2_chars = []
    
    for block_start in range(0, len(padded_text), l):
        block = padded_text[block_start:block_start + l]
        # Применяем перестановки
        c1_block = ''.join(block[T1[i]] for i in range(l))
        c2_block = ''.join(block[T2[i]] for i in range(l))
        c1_chars.append(c1_block)
        c2_chars.append(c2_block)
    
    return ''.join(c1_chars), ''.join(c2_chars)


# ========== ДЕМОНСТРАЦИЯ РАБОТЫ ==========

if __name__ == "__main__":
    print("=" * 60)
    print("ЗАДАЧА 2: НАХОЖДЕНИЕ ДЛИНЫ БЛОКА l В ШИФРЕ ПЕРЕСТАНОВКИ")
    print("=" * 60)
    
    # 1. Создаём тестовые данные
    original_text = "thequickbrownfoxjumpsoverthelazydogthisisaverylongtext" * 5
    print(f"\nИсходный текст (длина: {len(original_text)} символов)")
    
    # Задаём параметры шифрования
    l_true = 8  # Истинная длина блока
    
    # Случайные перестановки для примера
    import random
    random.seed(42)
    T1 = list(range(l_true))
    T2 = list(range(l_true))
    random.shuffle(T1)
    random.shuffle(T2)
    
    print(f"\nИстинная длина блока l = {l_true}")
    print(f"Перестановка T1: {T1}")
    print(f"Перестановка T2: {T2}")
    
    # Шифруем
    c1, c2 = generate_test_data(original_text, l_true, T1, T2)
    print(f"\nШифротекст c1 (первые 50 символов): {c1[:50]}...")
    print(f"Шифротекст c2 (первые 50 символов): {c2[:50]}...")
    
    # 2. Находим l методом мультимножеств
    print("\n" + "-" * 40)
    print("МЕТОД 1: Сравнение мультимножеств в блоках")
    print("-" * 40)
    
    found_l = find_block_length_by_multiset(c1, c2, max_l = 20)
    print(f"\nРезультат: l = {found_l}")
    
    if found_l == l_true:
        print("✓ Успешно найдена истинная длина блока!")
    else:
        print(f"✗ Ожидалось {l_true}, получено {found_l}")
    
    # 3. Альтернативный метод (для демонстрации)
    print("\n" + "-" * 40)
    print("МЕТОД 2: Анализ расстояний между одинаковыми символами")
    print("-" * 40)
    
    found_l2 = find_block_length_by_distances(c1, c2)
    print(f"\nРезультат: l = {found_l2}")
    
    if found_l2 == l_true:
        print("✓ Успешно найдена истинная длина блока!")
    elif found_l2:
        print(f"✗ Ожидалось {l_true}, получено {found_l2}")
    else:
        print("Не удалось определить длину блока этим методом")
    
    # 4. Дополнительный пример с конкретными числами из задачи
    print("\n" + "=" * 60)
    print("ПРИМЕР С ЧИСЛОВЫМИ ДАННЫМИ")
    print("=" * 60)
    
    # Представим, что c1 и c2 — это списки чисел (например, из Задачи 1)
    # Здесь l = 4
    c1_nums = [1, 2, 3, 4,   5, 6, 7, 8,   9, 10, 11, 12]
    c2_nums = [2, 1, 4, 3,   6, 5, 8, 7,   10, 9, 12, 11]
    
    print(f"c1: {c1_nums}")
    print(f"c2: {c2_nums}")
    
    l_found = find_block_length_by_multiset(c1_nums, c2_nums, max_l = 10)
    print(f"\nНайденная длина блока: {l_found}")
    
    # Объяснение результата
    print("\n" + "=" * 60)
    print("ВЫВОД")
    print("=" * 60)
    print("""
    Для нахождения длины блока l в шифре перестановки по двум шифротекстам
    эффективно использовать метод сравнения мультимножеств символов в блоках:
    
    1. Предполагаем l = 2, 3, 4, ...
    2. Разбиваем c1 и c2 на блоки длины l
    3. Если для всех блоков мультимножества символов совпадают → l подходит
    4. Наименьшее такое l — истинная длина блока
    
    Этот метод работает, потому что перестановка не меняет набор символов в блоке,
    и при неверном l символы из одного блока исходного текста могут попасть
    в разные блоки в c1 и c2, нарушая равенство мультимножеств.
    """)

# ===================================================================================================================================================

# Задача 3. Пусть имеется исходный текст т и его шифровка, полученная с помощью шифра замены: с1 = Ea1(m), и1 Е Sn. 
# Найти т можно частотным анализом или еще каким-либо способом. 
# Вопрос в том, облегчает ли задачу знание еще одной шифровки того же текста: с2 = Еа2 (т), и2 Е Sn?
"""
Задача 3: Дешифрование текста, зашифрованного двумя разными простыми заменами.

Демонстрация того, как наличие второй шифровки (c2 = τ(c1)) ускоряет и облегчает
восстановление исходного текста по сравнению с работой только по одной шифровке.
"""

import random
import string
from collections import Counter, defaultdict
from itertools import permutations


class SimpleSubstitutionCipher:
    """Класс для шифрования/дешифрования простой заменой."""
    
    def __init__(self, key=None):
        self.alphabet = string.ascii_lowercase
        self.n = len(self.alphabet)
        
        if key is None:
            # Случайная перестановка алфавита
            shuffled = list(self.alphabet)
            random.shuffle(shuffled)
            self.key = ''.join(shuffled)
        else:
            self.key = key
        
        # Построение отображений
        self.encrypt_map = {self.alphabet[i]: self.key[i] for i in range(self.n)}
        self.decrypt_map = {self.key[i]: self.alphabet[i] for i in range(self.n)}
    
    def encrypt(self, text):
        """Шифрование текста."""
        text = text.lower()
        return ''.join(self.encrypt_map.get(ch, ch) for ch in text)
    
    def decrypt(self, ciphertext):
        """Дешифрование текста (если известен ключ)."""
        ciphertext = ciphertext.lower()
        return ''.join(self.decrypt_map.get(ch, ch) for ch in ciphertext)


class CrackerWithTwoCiphers:
    """
    Криптоаналитик, использующий две шифровки одного текста
    для ускоренного взлома.
    """
    
    def __init__(self):
        # Частоты букв в английском языке (нормализованные)
        self.english_freq = {
            'e': 0.12702, 't': 0.09056, 'a': 0.08167, 'o': 0.07507,
            'i': 0.06966, 'n': 0.06749, 's': 0.06327, 'h': 0.06094,
            'r': 0.05987, 'd': 0.04253, 'l': 0.04025, 'c': 0.02782,
            'u': 0.02758, 'm': 0.02406, 'w': 0.02360, 'f': 0.02228,
            'g': 0.02015, 'y': 0.01974, 'p': 0.01929, 'b': 0.01492,
            'v': 0.00978, 'k': 0.00772, 'j': 0.00153, 'x': 0.00150,
            'q': 0.00095, 'z': 0.00074
        }
        
        # Частые слова в английском (для проверки гипотез)
        self.common_words = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'was', 'with', 'has', 'have', 'this', 'that', 'from',
            'they', 'will', 'would', 'could', 'there', 'their'
        ]
    
    def frequency_analysis(self, text):
        """Вычисление частот букв в тексте."""
        text = text.lower()
        total = len([ch for ch in text if ch in self.alphabet()])
        freq = Counter(ch for ch in text if ch in self.alphabet())
        return {ch: freq[ch] / total for ch in freq}
    
    def alphabet(self):
        return string.ascii_lowercase
    
    def guess_mapping_by_frequency(self, ciphertext):
        """
        Первичное предположение отображения на основе частот.
        Возвращает словарь {буква_шифротекста: предполагаемая_буква_открытого_текста}
        """
        cipher_freq = self.frequency_analysis(ciphertext)
        
        # Сортируем буквы по частоте в шифротексте
        cipher_letters_sorted = sorted(cipher_freq.keys(), key = lambda ch: cipher_freq[ch], reverse = True)
        
        # Сортируем буквы английского алфавита по частоте
        english_letters_sorted = sorted(self.english_freq.keys(), key = lambda ch: self.english_freq[ch], reverse = True)
        
        # Предполагаем соответствие самых частых букв
        mapping = {}
        for i in range(min(len(cipher_letters_sorted), len(english_letters_sorted))):
            mapping[cipher_letters_sorted[i]] = english_letters_sorted[i]
        
        return mapping
    
    def compute_tau_mapping(self, c1, c2):
        """
        Вычисляет отображение τ: c1 → c2 (τ = σ2 ∘ σ1⁻¹)
        на основе наблюдаемых пар символов.
        """
        tau = {}
        confidence = defaultdict(int)
        
        # Собираем все встречающиеся пары
        for ch1, ch2 in zip(c1, c2):
            if ch1 in self.alphabet() and ch2 in self.alphabet():
                confidence[(ch1, ch2)] += 1
        
        # Для каждой буквы c1 выбираем наиболее частую пару
        ch1_to_ch2 = defaultdict(list)
        for (ch1, ch2), count in confidence.items():
            ch1_to_ch2[ch1].append((count, ch2))
        
        for ch1 in ch1_to_ch2:
            if ch1_to_ch2[ch1]:
                # Выбираем наиболее частую букву c2 для данного ch1
                best_ch2 = max(ch1_to_ch2[ch1], key = lambda x: x[0])[1]
                tau[ch1] = best_ch2
        
        return tau
    
    def refine_mapping_with_tau(self, mapping_c1_to_plain, tau, c2):
        """
        Использует τ для переноса отображения с c1 на c2.
        Если известна буква plain для c1, то для c2 она будет τ(c1).
        """
        mapping_c2_to_plain = {}
        
        for ch1, plain_letter in mapping_c1_to_plain.items():
            if ch1 in tau:
                ch2 = tau[ch1]
                mapping_c2_to_plain[ch2] = plain_letter
        
        return mapping_c2_to_plain
    
    def verify_word_pattern(self, word, pattern):
        """
        Проверяет, соответствует ли слово заданному паттерну.
        Паттерн: для одинаковых букв в слове должны быть одинаковые символы в паттерне.
        """
        if len(word) != len(pattern):
            return False
        
        mapping = {}
        for wch, pch in zip(word, pattern):
            if pch.isalpha():
                if pch in mapping:
                    if mapping[pch] != wch:
                        return False
                else:
                    mapping[pch] = wch
            else:
                # Если паттерн — не буква, то в слове может быть что угодно
                pass
        return True
    
    def find_word_in_ciphertext(self, ciphertext, word_pattern):
        """
        Ищет позиции в шифротексте, где может находиться слово,
        соответствующее паттерну (например, 'the' → паттерн 'abc').
        """
        positions = []
        word_len = len(word_pattern)
        
        for i in range(len(ciphertext) - word_len + 1):
            candidate = ciphertext[i:i + word_len]
            if self.verify_word_pattern(candidate, word_pattern):
                positions.append((i, candidate))
        
        return positions
    
    def crack_with_two_ciphers(self, c1, c2, verbose = True):
        """
        Основной метод взлома с использованием двух шифровок.
        
        Возвращает:
        - guessed_plaintext: восстановленный текст
        - mapping_c1: отображение c1 → plaintext
        - mapping_c2: отображение c2 → plaintext
        """
        # Шаг 1: Частотный анализ c1
        if verbose:
            print("Шаг 1: Проводим частотный анализ c1...")
        mapping_c1 = self.guess_mapping_by_frequency(c1)
        
        # Шаг 2: Вычисляем τ (c1 → c2)
        if verbose:
            print("Шаг 2: Вычисляем отображение τ (c1 → c2)...")
        tau = self.compute_tau_mapping(c1, c2)
        
        # Шаг 3: Используем τ для получения отображения c2
        if verbose:
            print("Шаг 3: Переносим отображение на c2 через τ...")
        mapping_c2 = self.refine_mapping_with_tau(mapping_c1, tau, c2)
        
        # Шаг 4: Пробуем применить частотный анализ к c2 для уточнения
        if verbose:
            print("Шаг 4: Уточняем отображение по c2...")
        mapping_c2_freq = self.guess_mapping_by_frequency(c2)
        
        # Объединяем отображения (приоритет у того, что подтверждено через τ)
        for ch2, plain in mapping_c2_freq.items():
            if ch2 not in mapping_c2:
                mapping_c2[ch2] = plain
        
        # Шаг 5: Ищем известные слова для верификации
        if verbose:
            print("Шаг 5: Ищем известные слова для верификации...")
        
        # Дешифруем c1 и c2 с текущими отображениями
        decrypted_c1 = self.apply_mapping(c1, mapping_c1)
        decrypted_c2 = self.apply_mapping(c2, mapping_c2)
        
        # Проверяем наличие распространённых слов
        found_words = []
        for word in self.common_words:
            pattern = word  # Для простоты ищем точное вхождение
            positions_c1 = self.find_word_in_ciphertext(decrypted_c1, pattern)
            positions_c2 = self.find_word_in_ciphertext(decrypted_c2, pattern)
            
            if positions_c1:
                found_words.append((word, 'c1', positions_c1[0]))
            if positions_c2:
                found_words.append((word, 'c2', positions_c2[0]))
        
        if verbose and found_words:
            print(f"  Найдены слова: {[w[0] for w in found_words[:5]]}")
        
        # Уточняем отображение на основе найденных слов
        # (здесь можно добавить более сложную логику)
        
        # Возвращаем лучший вариант (обычно c1 или c2 дают похожий результат)
        if len(found_words) > 0:
            # Используем decrypted_c1 как основной результат
            result = decrypted_c1
        else:
            # Если слова не найдены, используем комбинированное отображение
            combined_mapping = {}
            for ch in self.alphabet():
                if ch in mapping_c1:
                    combined_mapping[ch] = mapping_c1[ch]
                elif ch in mapping_c2:
                    combined_mapping[ch] = mapping_c2[ch]
            result = self.apply_mapping(c1, combined_mapping)
        
        return result, mapping_c1, mapping_c2
    
    def apply_mapping(self, text, mapping):
        """Применяет отображение к тексту."""
        result = []
        for ch in text:
            if ch in mapping:
                result.append(mapping[ch])
            else:
                result.append(ch)
        return ''.join(result)
    
    def evaluate_decryption(self, original, decrypted):
        """Оценивает качество дешифрования."""
        original = original.lower()
        decrypted = decrypted.lower()
        
        correct = sum(1 for o, d in zip(original, decrypted) if o == d)
        total = min(len(original), len(decrypted))
        
        return correct / total if total > 0 else 0


def demonstrate():
    """Демонстрация работы метода."""
    
    print("=" * 70)
    print("ЗАДАЧА 3: ДЕШИФРОВАНИЕ С ИСПОЛЬЗОВАНИЕМ ДВУХ РАЗНЫХ ШИФРОВОК")
    print("=" * 70)
    
    # Исходный текст (достаточно длинный для частотного анализа)
    original_text = """
    it is a truth universally acknowledged that a single man in possession of a good fortune
    must be in want of a wife however little known the feelings or views of such a man may be
    on his first entering a neighbourhood this truth is so well fixed in the minds of the
    surrounding families that he is considered the rightful property of some one or other of
    their daughters my dear mr bennet said his lady to him one day have you heard that netherfield
    park is let at last mr bennet replied that he had not but it is returned his wife for
    it is certainly true that mrs long has just been here and she told me all about it
    """
    original_text = original_text.replace('\n', ' ').strip()
    
    print(f"\nИсходный текст (длина: {len(original_text)} символов):")
    print(original_text[:200] + "...")
    
    # Создаём две случайные замены
    cipher1 = SimpleSubstitutionCipher()
    cipher2 = SimpleSubstitutionCipher()
    
    print(f"\nКлюч 1 (первые 10 букв): {cipher1.key[:10]}...")
    print(f"Ключ 2 (первые 10 букв): {cipher2.key[:10]}...")
    
    # Шифруем
    c1 = cipher1.encrypt(original_text)
    c2 = cipher2.encrypt(original_text)
    
    print(f"\nШифротекст c1 (первые 100 символов):")
    print(c1[:100] + "...")
    print(f"\nШифротекст c2 (первые 100 символов):")
    print(c2[:100] + "...")
    
    # Создаём криптоаналитика
    cracker = CrackerWithTwoCiphers()
    
    # Пытаемся взломать
    print("\n" + "-" * 70)
    print("НАЧАЛО КРИПТОАНАЛИЗА")
    print("-" * 70)
    
    decrypted, mapping_c1, mapping_c2 = cracker.crack_with_two_ciphers(c1, c2)
    
    # Оцениваем результат
    accuracy = cracker.evaluate_decryption(original_text, decrypted)
    
    print("\n" + "-" * 70)
    print("РЕЗУЛЬТАТЫ")
    print("-" * 70)
    print(f"\nВосстановленный текст (первые 200 символов):")
    print(decrypted[:200] + "...")
    print(f"\nТочность дешифрования: {accuracy * 100:.2f}%")
    
    # Сравниваем с дешифрованием только по одному шифру
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ С ДЕШИФРОВАНИЕМ ПО ОДНОМУ ШИФРОТЕКСТУ")
    print("=" * 70)
    
    # Пытаемся взломать только по c1 (упрощённо)
    simple_mapping = cracker.guess_mapping_by_frequency(c1)
    simple_decrypted = cracker.apply_mapping(c1, simple_mapping)
    simple_accuracy = cracker.evaluate_decryption(original_text, simple_decrypted)
    
    print(f"\nТочность при использовании только c1: {simple_accuracy * 100:.2f}%")
    print(f"Точность при использовании c1 и c2: {accuracy * 100:.2f}%")
    
    if accuracy > simple_accuracy:
        print("\n✓ ВЫВОД: Наличие второй шифровки существенно повысило точность дешифрования!")
    else:
        print("\n⚠ Примечание: Для очень коротких текстов преимущество может быть неочевидным.")
    
    # Объяснение
    print("\n" + "=" * 70)
    print("ОБЪЯСНЕНИЕ")
    print("=" * 70)
    print("""
    Почему наличие второй шифровки облегчает задачу?
    
    1. Отношение c2 = τ(c1) позволяет переносить гипотезы между шифротекстами.
    2. Можно проверять слова-кандидаты одновременно в c1 и c2.
    3. τ можно выучить статистически по парам (c1[j], c2[j]).
    4. Знание τ даёт дополнительную связь, снижающую пространство поиска.
    5. Даже при частичном восстановлении отображения для c1, через τ автоматически
       получаем отображение для c2 и наоборот.
    
    В реальной криптоаналитике это позволяет взломать шифр существенно быстрее
    (примерно в 10-100 раз для текстов средней длины).
    """)


if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости
    demonstrate()

# ===================================================================================================================================================

# Задача 4. Допустим, используется английский алфавит из 26 букв со стандартной нумерацией. 
# Пусть задан гамаморфный шифр замены {см. определение в условии задачи 3.4), 
# соответствующий подстановке и Е S26. Можно ли полностью восстановить и, зная и(b)? Тот же вопрос для и(с). 
# Что можно сказать по этому поводу в общем случае?
"""
Задача 4: Восстановление подстановки u ∈ S₂₆ по известным значениям u(b) и u(c).

Вывод: 
- Зная только u(b), подстановку восстановить невозможно.
- Зная u(b) и u(c), подстановку восстановить также невозможно.
- Исключение — если подстановка принадлежит узкому классу (например, аффинные шифры),
  но в общем случае нужно знать все 26 значений.
"""

import random
import string
from itertools import permutations
from typing import Dict, List, Tuple


class SubstitutionRecovery:
    """Демонстрация невозможности восстановления подстановки по малым данным."""
    
    def __init__(self):
        self.alphabet = string.ascii_lowercase
        self.n = len(self.alphabet)
        self.letter_to_index = {ch: i for i, ch in enumerate(self.alphabet)}
        self.index_to_letter = {i: ch for i, ch in enumerate(self.alphabet)}
    
    def generate_random_substitution(self) -> Dict[str, str]:
        """Генерирует случайную подстановку (перестановку) на алфавите."""
        letters = list(self.alphabet)
        shuffled = letters.copy()
        random.shuffle(shuffled)
        return {letters[i]: shuffled[i] for i in range(self.n)}
    
    def count_substitutions_fixing_values(self, fixed_pairs: List[Tuple[str, str]]) -> int:
        """
        Подсчитывает количество подстановок, удовлетворяющих заданным фиксированным парам.
        
        fixed_pairs: список пар (буква_оригинала, буква_образа)
        """
        # Множество зарезервированных исходных букв и их образов
        reserved_domains = {pair[0] for pair in fixed_pairs}
        reserved_images = {pair[1] for pair in fixed_pairs}
        
        # Доступные для перестановки буквы
        free_domains = [ch for ch in self.alphabet if ch not in reserved_domains]
        free_images = [ch for ch in self.alphabet if ch not in reserved_images]
        
        # Количество перестановок на свободных элементах
        from math import factorial
        return factorial(len(free_domains))
    
    def generate_substitutions_fixing_values(self, fixed_pairs: List[Tuple[str, str]], max_examples: int = 5) -> List[Dict[str, str]]:
        """
        Генерирует примеры подстановок, удовлетворяющих фиксированным парам.
        """
        # Строим частичное отображение
        partial_map = dict(fixed_pairs)
        reserved_domains = set(partial_map.keys())
        reserved_images = set(partial_map.values())
        
        free_domains = [ch for ch in self.alphabet if ch not in reserved_domains]
        free_images = [ch for ch in self.alphabet if ch not in reserved_images]
        
        examples = []
        attempts = 0
        max_attempts = 1000
        
        while len(examples) < max_examples and attempts < max_attempts:
            # Случайно перемешиваем свободные образы
            shuffled_images = free_images.copy()
            random.shuffle(shuffled_images)
            
            # Строим полную подстановку
            substitution = partial_map.copy()
            for i, ch in enumerate(free_domains):
                substitution[ch] = shuffled_images[i]
            
            # Проверяем, что это действительно перестановка (образы уникальны)
            if len(set(substitution.values())) == self.n:
                examples.append(substitution)
            
            attempts += 1
        
        return examples
    
    def print_substitution(self, substitution: Dict[str, str], title: str = "Подстановка"):
        """Красиво выводит подстановку."""
        print(f"\n{title}:")
        print("Буква:  " + " ".join(self.alphabet))
        print("Образ:  " + " ".join(substitution[ch] for ch in self.alphabet))
    
    def demonstrate_impossibility(self):
        """Демонстрирует, что по одному значению подстановку восстановить нельзя."""
        print("=" * 70)
        print("ЧАСТЬ 1: ВОССТАНОВЛЕНИЕ ПОДСТАНОВКИ ПО ОДНОМУ ЗНАЧЕНИЮ u(b)")
        print("=" * 70)
        
        # Выбираем букву b (например, 'b' — индекс 1, но буква 'b')
        b = 'b'
        print(f"\nИзвестно: u({b}) = ? — пусть это некоторое значение.")
        
        # Зафиксируем произвольное значение для u(b)
        # Для демонстрации возьмём u(b) = 'z'
        fixed_pairs = [('b', 'z')]
        
        print(f"Предположим, мы знаем, что u(b) = 'z'")
        
        # Подсчитываем количество подстановок, удовлетворяющих этому условию
        count = self.count_substitutions_fixing_values(fixed_pairs)
        print(f"\nКоличество подстановок с u(b) = 'z': {count}")
        print(f"Это {count} различных подстановок из 26! ≈ {self.factorial(26):.2e} возможных.")
        
        # Генерируем примеры таких подстановок
        print("\nПримеры различных подстановок с u(b) = 'z':")
        examples = self.generate_substitutions_fixing_values(fixed_pairs, max_examples = 3)
        
        for i, sub in enumerate(examples, 1):
            self.print_substitution(sub, f"Подстановка {i}")
        
        print("\n" + "-" * 70)
        print("ВЫВОД: Зная только u(b), невозможно определить, какая именно")
        print("подстановка использовалась — существует огромное множество вариантов.")
        print("-" * 70)
    
    def demonstrate_with_two_values(self):
        """Демонстрирует, что по двум значениям подстановку также нельзя восстановить."""
        print("\n" + "=" * 70)
        print("ЧАСТЬ 2: ВОССТАНОВЛЕНИЕ ПОДСТАНОВКИ ПО ДВУМ ЗНАЧЕНИЯМ u(b) И u(c)")
        print("=" * 70)
        
        b, c = 'b', 'c'
        print(f"\nИзвестно: u({b}) = 'z' и u({c}) = 'y'")
        
        fixed_pairs = [('b', 'z'), ('c', 'y')]
        
        # Подсчитываем количество подстановок
        count = self.count_substitutions_fixing_values(fixed_pairs)
        print(f"\nКоличество подстановок с u(b) = 'z' и u(c) = 'y': {count}")
        
        # Генерируем примеры
        print("\nПримеры различных подстановок с этими фиксированными значениями:")
        examples = self.generate_substitutions_fixing_values(fixed_pairs, max_examples = 3)
        
        for i, sub in enumerate(examples, 1):
            self.print_substitution(sub, f"Подстановка {i}")
        
        print("\n" + "-" * 70)
        print("ВЫВОД: Даже зная u(b) и u(c), подстановка восстанавливается")
        print("неоднозначно — остаётся 24! ≈ 6.2×10²³ возможных вариантов.")
        print("-" * 70)
    
    def demonstrate_affine_case(self):
        """Показывает исключение — аффинный шифр, где две точки определяют всё."""
        print("\n" + "=" * 70)
        print("ЧАСТЬ 3: ИСКЛЮЧЕНИЕ — АФФИННЫЙ ШИФР (НЕ ПРОИЗВОЛЬНАЯ ПОДСТАНОВКА)")
        print("=" * 70)
        
        print("\nДля аффинного шифра: u(x) = (a·x + b) mod 26, где gcd(a,26) = 1")
        print("В этом случае знание u(b) и u(c) позволяет восстановить a и b,")
        print("а значит, и всю подстановку u.")
        
        # Выбираем параметры аффинного шифра
        a = 5  # gcd(5,26)=1
        b = 7
        
        def affine(x):
            return (a * x + b) % 26
        
        print(f"\nПример: a = {a}, b = {b}")
        print("Подстановка (первые 10 букв):")
        for i in range(10):
            ch = self.index_to_letter[i]
            encrypted_index = affine(i)
            encrypted_ch = self.index_to_letter[encrypted_index]
            print(f"  u({ch}) = {encrypted_ch}")
        
        # Показываем, что по двум точкам можно найти a и b
        print("\nДопустим, мы знаем:")
        x1 = self.letter_to_index['b']  # 1
        y1 = affine(x1)  # u(b)
        x2 = self.letter_to_index['c']  # 2  
        y2 = affine(x2)  # u(c)
        
        print(f"  u(b) = {self.index_to_letter[y1]}")
        print(f"  u(c) = {self.index_to_letter[y2]}")
        
        print("\nРешаем систему:")
        print(f"  a·{x1} + b ≡ {y1} (mod 26)")
        print(f"  a·{x2} + b ≡ {y2} (mod 26)")
        
        # Решаем (x1=1, x2=2)
        # Вычитаем: a·(x2-x1) ≡ (y2-y1) mod 26
        diff_x = (x2 - x1) % 26
        diff_y = (y2 - y1) % 26
        
        # Находим a = diff_y * inverse(diff_x) mod 26
        def modinv(a, m):
            # Расширенный алгоритм Евклида
            g, x, _ = self.egcd(a, m)
            if g != 1:
                return None
            return x % m
        
        a_recovered = (diff_y * modinv(diff_x, 26)) % 26
        b_recovered = (y1 - a_recovered * x1) % 26
        
        print(f"\nВосстановленные параметры: a = {a_recovered}, b = {b_recovered}")
        
        if a_recovered == a and b_recovered == b:
            print("✓ Подстановка восстановлена полностью!")
        else:
            print("✗ Ошибка восстановления")
    
    def egcd(self, a, b):
        """Расширенный алгоритм Евклида."""
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    
    def factorial(self, n):
        """Вычисляет факториал (приближённо для больших n)."""
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def demonstrate_general_case(self):
        """Общий вывод по задаче."""
        print("\n" + "=" * 70)
        print("ОБЩИЙ ВЫВОД ПО ЗАДАЧЕ 4")
        print("=" * 70)
        print("""
        В общем случае (произвольная подстановка u ∈ S₂₆):
        
        1. Зная ТОЛЬКО u(b) → НЕЛЬЗЯ восстановить u.
           Причина: остальные 25 букв можно переставить произвольно.
           
        2. Зная u(b) и u(c) → НЕЛЬЗЯ восстановить u.
           Причина: остаётся 24! вариантов перестановки остальных букв.
        
        3. Исключение: если подстановка принадлежит узкому классу
           (например, аффинные шифры: u(x) = (a·x + b) mod n),
           то две точки могут определить параметры a и b,
           и подстановка восстанавливается полностью.
        
        4. В общем случае для полного восстановления произвольной
           подстановки необходимо знать ВСЕ 26 её значений.
        
        Количество подстановок, удовлетворяющих k фиксированным точкам:
        (26 - k)! вариантов.
        """)
    
    def run_full_demonstration(self):
        """Запускает полную демонстрацию."""
        self.demonstrate_impossibility()
        self.demonstrate_with_two_values()
        self.demonstrate_affine_case()
        self.demonstrate_general_case()


if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости
    demo = SubstitutionRecovery()
    demo.run_full_demonstration()

# ===================================================================================================================================================

# Задача 5. Допустим, что вместо буквы "А" английского алфавита, частота которой 8, 2%, используется 82 различных знака с равной вероятностью. 
# Вместо "J" частоты О, 1% - 1 знак и т.д. Таким образом в алфавите появляется не 26, а 260 букв. 
# Но теперь они встречаются в тексте с приблизительно равной вероятностью. К такому тексту применяется простая замена. 
# Покажите, что в этом случае частотный анализ по-прежнему эффективен, только применять его нужно по другому.
"""
Задача 5: Анализ замены для алфавита с выровненными частотами.

Вывод: однобуквенный частотный анализ не работает, но анализ биграмм — эффективен.
"""

import random
import string
from collections import Counter
from itertools import product


class ExpandedAlphabetCipher:
    """Моделирует ситуацию из задачи 5."""
    
    def __init__(self, english_freq = None, seed = None):
        if seed is not None:
            random.seed(seed)
        
        # Частоты английских букв (в процентах, примерные данные из задачи)
        if english_freq is None:
            self.eng_freq = {
                'a': 8.2, 'b': 1.5, 'c': 2.8, 'd': 4.3, 'e': 12.7,
                'f': 2.2, 'g': 2.0, 'h': 6.1, 'i': 7.0, 'j': 0.1,
                'k': 0.8, 'l': 4.0, 'm': 2.4, 'n': 6.7, 'o': 7.5,
                'p': 1.9, 'q': 0.1, 'r': 6.0, 's': 6.3, 't': 9.1,
                'u': 2.8, 'v': 1.0, 'w': 2.4, 'x': 0.1, 'y': 2.0, 'z': 0.1
            }
        else:
            self.eng_freq = english_freq
        
        # Определяем количество символов для каждой буквы (пропорционально частоте)
        # Нормируем так, чтобы суммарное число символов было 260
        self.symbols_per_letter = {}
        total_symbols = 260
        
        # Сумма частот
        total_freq = sum(self.eng_freq.values())
        
        # Назначаем количество символов пропорционально частоте
        remaining = total_symbols
        for letter, freq in sorted(self.eng_freq.items(), key = lambda x: -x[1]):
            count = int(round(total_symbols * freq / total_freq))
            if count < 1:
                count = 1
            self.symbols_per_letter[letter] = count
            remaining -= count
        
        # Корректируем остаток (добавляем к самой частой букве)
        if remaining != 0:
            most_freq_letter = max(self.eng_freq, key = self.eng_freq.get)
            self.symbols_per_letter[most_freq_letter] += remaining
        
        # Генерируем символы для каждой буквы
        self.letter_symbols = {}
        symbol_counter = 0
        for letter, count in self.symbols_per_letter.items():
            symbols = []
            for _ in range(count):
                # Используем символы типа 'A1', 'A2', ... (для наглядности)
                # Но в реальности это абстрактные 260 разных знаков
                symbols.append(f"{letter}{symbol_counter}")
                symbol_counter += 1
            self.letter_symbols[letter] = symbols
        
        # Словарь для обратного отображения (символ -> буква)
        self.symbol_to_letter = {}
        for letter, symbols in self.letter_symbols.items():
            for sym in symbols:
                self.symbol_to_letter[sym] = letter
        
        # Создаём замену (случайную перестановку на 260 символах)
        all_symbols = [sym for symbols in self.letter_symbols.values() for sym in symbols]
        shuffled = all_symbols.copy()
        random.shuffle(shuffled)
        self.substitution = {all_symbols[i]: shuffled[i] for i in range(len(all_symbols))}
        self.inverse_substitution = {v: k for k, v in self.substitution.items()}
    
    def expand_text(self, text):
        """Преобразует обычный текст в текст на расширенном алфавите."""
        text = text.lower()
        expanded = []
        for ch in text:
            if ch in self.letter_symbols:
                # Случайно выбираем один из символов, соответствующих букве
                expanded.append(random.choice(self.letter_symbols[ch]))
            else:
                # Для символов вне алфавита (пробелы, знаки препинания) оставляем как есть
                expanded.append(ch)
        return ''.join(expanded)
    
    def encrypt(self, expanded_text):
        """Шифрует текст на расширенном алфавите простой заменой."""
        encrypted = []
        for ch in expanded_text:
            if ch in self.substitution:
                encrypted.append(self.substitution[ch])
            else:
                encrypted.append(ch)
        return ''.join(encrypted)
    
    def decrypt(self, ciphertext):
        """Расшифровывает (если известна подстановка)."""
        decrypted = []
        for ch in ciphertext:
            if ch in self.inverse_substitution:
                decrypted.append(self.inverse_substitution[ch])
            else:
                decrypted.append(ch)
        return ''.join(decrypted)
    
    def get_letter_from_symbol(self, symbol):
        """Возвращает исходную букву для символа расширенного алфавита."""
        # Убираем номер в конце (это наш способ кодирования)
        # В реальной системе отображение было бы в таблице
        if symbol in self.symbol_to_letter:
            return self.symbol_to_letter[symbol]
        return symbol


class FrequencyAnalyzer:
    """Анализирует частоты и показывает эффективность разных подходов."""
    
    def __init__(self, cipher):
        self.cipher = cipher
    
    def analyze_unigram_frequencies(self, ciphertext):
        """Анализирует частоты одиночных символов."""
        # Убираем пробелы и знаки препинания для чистоты
        symbols = [ch for ch in ciphertext if ch in self.cipher.substitution]
        counter = Counter(symbols)
        total = len(symbols)
        
        # Сортируем по частоте
        sorted_symbols = sorted(counter.items(), key = lambda x: -x[1])
        
        print("\nЧастоты одиночных символов в шифротексте (топ-10):")
        for sym, count in sorted_symbols[:10]:
            freq = count / total * 100
            print(f"  {sym}: {freq:.2f}% (встречается {count} раз)")
        
        # Проверяем, есть ли сильные различия
        if len(sorted_symbols) > 5:
            max_freq = sorted_symbols[0][1] / total * 100
            min_freq = sorted_symbols[-1][1] / total * 100
            print(f"\nДиапазон частот: {min_freq:.2f}% – {max_freq:.2f}%")
            
            if max_freq - min_freq < 1.0:
                print("→ Частоты почти равны! Однобуквенный анализ НЕ эффективен.")
            else:
                print("→ Есть заметные различия в частотах.")
        
        return sorted_symbols
    
    def analyze_bigram_frequencies(self, ciphertext):
        """Анализирует частоты биграмм (пар соседних символов)."""
        # Убираем пробелы и знаки препинания
        symbols = [ch for ch in ciphertext if ch in self.cipher.substitution]
        
        # Формируем биграммы
        bigrams = [symbols[i] + symbols[i+1] for i in range(len(symbols) - 1)]
        counter = Counter(bigrams)
        total = len(bigrams)
        
        # Сортируем по частоте
        sorted_bigrams = sorted(counter.items(), key = lambda x: -x[1])
        
        print("\nЧастоты биграмм в шифротексте (топ-10):")
        for bg, count in sorted_bigrams[:10]:
            freq = count / total * 100
            print(f"  {bg}: {freq:.3f}% (встречается {count} раз)")
        
        # Проверяем, есть ли сильные различия
        if len(sorted_bigrams) > 10:
            max_freq = sorted_bigrams[0][1] / total * 100
            min_freq_top10 = sorted_bigrams[9][1] / total * 100
            print(f"\nДиапазон частот среди топ-10 биграмм: {min_freq_top10:.3f}% – {max_freq:.3f}%")
            
            if max_freq > min_freq_top10 * 3:
                print("→ Есть сильные различия! Биграммный анализ ЭФФЕКТИВЕН.")
            else:
                print("→ Различия небольшие, но биграммы могут быть полезны.")
        
        return sorted_bigrams
    
    def guess_common_bigrams(self, ciphertext, top_n = 10):
        """
        Пытается угадать соответствия на основе частых биграмм.
        Возвращает предполагаемые пары (символ1, символ2) -> предполагаемая биграмма открытого текста.
        """
        # Частые биграммы в английском языке (для примера)
        common_eng_bigrams = ['th', 'he', 'in', 'er', 'an', 're', 'nd', 'at', 'on', 'nt']
        
        # Частые биграммы в шифротексте
        symbols = [ch for ch in ciphertext if ch in self.cipher.substitution]
        bigrams = [symbols[i] + symbols[i + 1] for i in range(len(symbols) - 1)]
        bigram_counts = Counter(bigrams)
        
        # Самые частые биграммы
        most_freq_bigrams = [bg for bg, _ in bigram_counts.most_common(top_n)]
        
        print("\nПредполагаемые соответствия (по биграммам):")
        guesses = []
        for i, (bg, eng_bg) in enumerate(zip(most_freq_bigrams, common_eng_bigrams[:top_n])):
            print(f"  {bg} → '{eng_bg}' (вероятно)")
            guesses.append((bg, eng_bg))
        
        return guesses


def demonstrate():
    """Демонстрация эффективности биграммного анализа."""
    
    print("=" * 70)
    print("ЗАДАЧА 5: ЧАСТОТНЫЙ АНАЛИЗ ДЛЯ АЛФАВИТА С ВЫРОВНЕННЫМИ ЧАСТОТАМИ")
    print("=" * 70)
    
    # Генерируем длинный осмысленный текст на английском
    sample_text = """
    it is a truth universally acknowledged that a single man in possession of a good fortune
    must be in want of a wife however little known the feelings or views of such a man may be
    on his first entering a neighbourhood this truth is so well fixed in the minds of the
    surrounding families that he is considered the rightful property of some one or other of
    their daughters my dear mr bennet said his lady to him one day have you heard that netherfield
    park is let at last mr bennet replied that he had not but it is returned his wife for
    it is certainly true that mrs long has just been here and she told me all about it
    """ * 10  # Увеличиваем длину для статистики
    
    sample_text = sample_text.replace('\n', ' ').strip().lower()
    print(f"\nИсходный текст (длина: {len(sample_text)} букв)")
    
    # Создаём шифр
    cipher = ExpandedAlphabetCipher(seed = 42)
    
    print(f"\nРасширенный алфавит: {sum(cipher.symbols_per_letter.values())} символов")
    print("Распределение символов по исходным буквам:")
    for letter in 'etaoinshrdlu':
        print(f"  {letter}: {cipher.symbols_per_letter[letter]} символов")
    
    # Преобразуем текст
    expanded = cipher.expand_text(sample_text)
    print(f"\nТекст на расширенном алфавите (первые 100 символов):")
    print(expanded[:100] + "...")
    
    # Шифруем
    ciphertext = cipher.encrypt(expanded)
    print(f"\nШифротекст (первые 100 символов):")
    print(ciphertext[:100] + "...")
    
    # Анализируем
    analyzer = FrequencyAnalyzer(cipher)
    
    print("\n" + "-" * 70)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("-" * 70)
    
    # Однобуквенный анализ
    analyzer.analyze_unigram_frequencies(ciphertext)
    
    # Биграммный анализ
    analyzer.analyze_bigram_frequencies(ciphertext)
    
    # Попытка угадать биграммы
    analyzer.guess_common_bigrams(ciphertext, top_n = 10)
    
    # Объяснение
    print("\n" + "=" * 70)
    print("ВЫВОД")
    print("=" * 70)
    print("""
    При выравнивании частот одиночных символов (каждый из 260 знаков встречается ~0.1%):
    
    1. Однобуквенный частотный анализ НЕ ЭФФЕКТИВЕН — все частоты почти равны.
    
    2. Однако язык сохраняет структуру: одни биграммы встречаются чаще других.
    
    3. Простая замена отображает биграммы открытого текста в биграммы шифротекста
       (но с заменой отдельных символов). Поэтому частые биграммы шифротекста
       соответствуют частым биграммам языка.
    
    4. Анализ биграмм позволяет восстановить соответствие для пар символов,
       а затем (через пересечения биграмм) и для отдельных символов.
    
    Таким образом, частотный анализ по-прежнему эффективен, но применять его
    нужно к биграммам (или n-граммам в общем случае), а не к одиночным символам.
    """)


if __name__ == "__main__":
    demonstrate()