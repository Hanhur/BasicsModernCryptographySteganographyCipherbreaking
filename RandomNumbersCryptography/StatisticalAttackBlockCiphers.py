# Статистическая атака на блоковые шифры 
"""
Градиентная статистическая атака на блочный шифр
Реализация на основе описания из текста
БЕЗ ВНЕШНИХ ЗАВИСИМОСТЕЙ (только random, math, collections)
"""

import random
import math
from collections import Counter
from typing import List, Tuple, Optional

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def int_to_bits(n: int, length: int) -> List[int]:
    """Преобразование целого числа в битовый список фиксированной длины"""
    if n < 0:
        n = 0
    if n >= 2 ** length:
        n = n % (2 ** length)
    return [int(x) for x in format(n, f'0{length}b')]

def bits_to_int(bits: List[int]) -> int:
    """Преобразование битового списка в целое число"""
    return int(''.join(map(str, bits)), 2)

def xor_lists(a: List[int], b: List[int]) -> List[int]:
    """Побитовое XOR двух списков"""
    return [x ^ y for x, y in zip(a, b)]

def rotate_left(bits: List[int], shift: int) -> List[int]:
    """Циклический сдвиг влево"""
    if len(bits) == 0:
        return bits
    shift = shift % len(bits)
    return bits[shift:] + bits[:shift]

def rotate_right(bits: List[int], shift: int) -> List[int]:
    """Циклический сдвиг вправо"""
    if len(bits) == 0:
        return bits
    shift = shift % len(bits)
    return bits[-shift:] + bits[:-shift]

def add_mod(bits_a: List[int], bits_b: List[int]) -> List[int]:
    """Сложение по модулю 2^n"""
    n = len(bits_a)
    a = bits_to_int(bits_a)
    b = bits_to_int(bits_b)
    result = (a + b) % (2 ** n)
    return int_to_bits(result, n)

def sub_mod(bits_a: List[int], bits_b: List[int]) -> List[int]:
    """Вычитание по модулю 2^n"""
    n = len(bits_a)
    a = bits_to_int(bits_a)
    b = bits_to_int(bits_b)
    result = (a - b) % (2 ** n)
    return int_to_bits(result, n)

# ============================================================
# 2. ШИФР RC5 (УПРОЩЁННАЯ ВЕРСИЯ)
# ============================================================

class RC5Simplified:
    """
    Упрощённая реализация RC5 для демонстрации градиентной атаки
    Размер блока: 2 слова по w бит
    """
    
    def __init__(self, w: int = 8, rounds: int = 4, fixed_key: Optional[List[int]] = None):
        """
        w: размер слова в битах (8, 16, 32)
        rounds: число раундов
        fixed_key: фиксированный ключ для воспроизводимости
        """
        self.w = w
        self.rounds = rounds
        self.word_size = w
        self.block_size = 2 * w
        self.fixed_key = fixed_key
        
    def _generate_round_keys(self, seed_key: Optional[List[int]] = None) -> List[List[int]]:
        """
        Генерация раундовых ключей
        """
        if seed_key is None:
            if self.fixed_key is not None:
                seed_key = self.fixed_key
            else:
                seed_key = [random.randint(0, 1) for _ in range(self.w)]
        
        keys = []
        # Добавляем два начальных ключа (как в RC5)
        keys.append([random.randint(0, 1) for _ in range(self.w)])
        keys.append([random.randint(0, 1) for _ in range(self.w)])
        
        # Генерируем по 2 ключа на раунд
        for i in range(self.rounds):
            k1 = []
            k2 = []
            for j in range(self.w):
                val = seed_key[j] ^ ((i * 7 + j * 3) % 2)
                k1.append(val)
                val = seed_key[(j + i) % self.w] ^ ((i * 11 + j * 5) % 2)
                k2.append(val)
            keys.append(k1)
            keys.append(k2)
            
        return keys
    
    def _round_encrypt(self, a: List[int], b: List[int], k1: List[int], k2: List[int]) -> Tuple[List[int], List[int]]:
        """Один раунд шифрования (как в RC5)"""
        # a = ((a XOR b) <<< b) + k1
        xor_ab = xor_lists(a, b)
        shift = bits_to_int(b) % self.w
        rotated = rotate_left(xor_ab, shift)
        a_new = add_mod(rotated, k1)
        
        # b = ((b XOR a) <<< a) + k2
        xor_ba = xor_lists(b, a)
        shift = bits_to_int(a) % self.w
        rotated = rotate_left(xor_ba, shift)
        b_new = add_mod(rotated, k2)
        
        return a_new, b_new
    
    def _round_decrypt(self, a: List[int], b: List[int], k1: List[int], k2: List[int]) -> Tuple[List[int], List[int]]:
        """Один раунд дешифрования (обратный к _round_encrypt)"""
        # b = ((b - k2) >>> a) XOR a
        b_sub = sub_mod(b, k2)
        shift = bits_to_int(a) % self.w
        b_rot = rotate_right(b_sub, shift)
        b_new = xor_lists(b_rot, a)
        
        # a = ((a - k1) >>> b) XOR b
        a_sub = sub_mod(a, k1)
        shift = bits_to_int(b_new) % self.w
        a_rot = rotate_right(a_sub, shift)
        a_new = xor_lists(a_rot, b_new)
        
        return a_new, b_new
    
    def encrypt_block(self, plaintext: List[int], key: Optional[List[int]] = None) -> List[int]:
        """Шифрование одного блока"""
        if len(plaintext) != self.block_size:
            raise ValueError(f"Block size must be {self.block_size} bits")
        
        # Разбиваем на два слова
        a = plaintext[:self.w]
        b = plaintext[self.w:]
        
        # Генерируем ключи
        keys = self._generate_round_keys(key)
        
        # Предварительное сложение с ключами
        a = add_mod(a, keys[0])
        b = add_mod(b, keys[1])
        
        # Раунды
        for i in range(self.rounds):
            k1 = keys[2 * i + 2]
            k2 = keys[2 * i + 3]
            a, b = self._round_encrypt(a, b, k1, k2)
        
        return a + b
    
    def decrypt_block(self, ciphertext: List[int], key: Optional[List[int]] = None) -> List[int]:
        """Дешифрование одного блока"""
        if len(ciphertext) != self.block_size:
            raise ValueError(f"Block size must be {self.block_size} bits")
        
        a = ciphertext[:self.w]
        b = ciphertext[self.w:]
        
        keys = self._generate_round_keys(key)
        
        # Обратные раунды
        for i in range(self.rounds - 1, -1, -1):
            k1 = keys[2 * i + 2]
            k2 = keys[2 * i + 3]
            a, b = self._round_decrypt(a, b, k1, k2)
        
        # Вычитание начальных ключей
        a = sub_mod(a, keys[0])
        b = sub_mod(b, keys[1])
        
        return a + b
    
    def decrypt_one_round(self, ciphertext: List[int], round_key: List[int], round_idx: int) -> List[int]:
        """
        Дешифрование ОДНОГО раунда (для атаки)
        round_idx: номер раунда (0-based от начала)
        """
        if len(ciphertext) != self.block_size:
            raise ValueError(f"Block size must be {self.block_size} bits")
        
        a = ciphertext[:self.w]
        b = ciphertext[self.w:]
        
        # Генерируем "правильную" цепочку ключей
        # Но для атаки мы не знаем остальные ключи, поэтому используем
        # фиктивные (в реальной атаке они неизвестны)
        keys = self._generate_round_keys(None)
        
        # Заменяем ключ указанного раунда на переданный
        # В RC5 на раунд идут 2 ключа
        if round_idx >= 0 and round_idx < self.rounds:
            # Используем переданный ключ как k1 для этого раунда
            keys[2 * round_idx + 2] = round_key
            # k2 генерируем случайно (в реальной атаке он неизвестен)
            keys[2 * round_idx + 3] = [random.randint(0, 1) for _ in range(self.w)]
        
        # Дешифруем только указанный раунд
        # Для этого дешифруем все раунды до нужного, затем один раунд,
        # затем снова шифруем остальные (упрощённо)
        
        # Дешифруем с конца до round_idx + 1
        for i in range(self.rounds - 1, round_idx, -1):
            k1 = keys[2 * i + 2]
            k2 = keys[2 * i + 3]
            a, b = self._round_decrypt(a, b, k1, k2)
        
        # Дешифруем target раунд с переданным ключом
        k1 = keys[2 * round_idx + 2]
        k2 = keys[2 * round_idx + 3]
        a, b = self._round_decrypt(a, b, k1, k2)
        
        # Шифруем обратно оставшиеся раунды (для сохранения структуры)
        for i in range(round_idx + 1, self.rounds):
            k1 = keys[2 * i + 2]
            k2 = keys[2 * i + 3]
            a, b = self._round_encrypt(a, b, k1, k2)
        
        return a + b

# ============================================================
# 3. СТАТИСТИЧЕСКИЕ ТЕСТЫ (БЕЗ ВНЕШНИХ БИБЛИОТЕК)
# ============================================================

def chi_square_test(bits: List[int]) -> Tuple[float, bool]:
    """
    Критерий хи-квадрат для проверки случайности битовой последовательности
    Возвращает: (статистика, rejected)
    """
    n = len(bits)
    if n == 0:
        return 0.0, False
    
    # Считаем количество нулей и единиц
    counts = [bits.count(0), bits.count(1)]
    
    # Ожидаемое количество при равномерном распределении
    expected = n / 2
    
    # Вычисляем статистику хи-квадрат
    if expected == 0:
        return 0.0, False
    
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    
    # Критическое значение для 1 степени свободы при уровне 0.001
    critical_value = 10.83
    
    rejected = chi2 > critical_value
    
    return chi2, rejected

def adaptive_chi_square(bits: List[int], max_parts: int = 128) -> Tuple[float, bool]:
    """
    Адаптивный критерий хи-квадрат из текста
    Разбивает последовательность на части и проверяет каждую
    """
    n = len(bits)
    if n < 64:
        chi2, rej = chi_square_test(bits)
        return chi2, rej
    
    # Пробуем разные размеры блоков
    best_chi2 = 0.0
    best_rejected = False
    
    for block_size in [8, 16, 32, 64, 128]:
        if block_size > n:
            break
        
        num_blocks = n // block_size
        if num_blocks < 2:
            break
        
        # Собираем статистику по блокам
        chi2_total = 0.0
        rejected_count = 0
        
        for i in range(num_blocks):
            block = bits[i * block_size:(i + 1) * block_size]
            chi2, rej = chi_square_test(block)
            chi2_total += chi2
            if rej:
                rejected_count += 1
        
        # Нормируем
        chi2_avg = chi2_total / num_blocks
        
        # Если хотя бы 30% блоков отклонены - считаем неслучайным
        is_rejected = (rejected_count / num_blocks) > 0.3
        
        if chi2_avg > best_chi2:
            best_chi2 = chi2_avg
            best_rejected = is_rejected
    
    return best_chi2, best_rejected

def randomness_measure(bits: List[int]) -> float:
    """
    Мера случайности: чем больше значение, тем более случайна последовательность
    Используем хи-квадрат статистику
    """
    chi2, _ = chi_square_test(bits)
    return chi2

def sequence_randomness(sequences: List[List[int]]) -> List[float]:
    """Вычисляет меру случайности для каждой последовательности"""
    return [randomness_measure(seq) for seq in sequences]

# ============================================================
# 4. ГРАДИЕНТНАЯ СТАТИСТИЧЕСКАЯ АТАКА
# ============================================================

class GradientAttack:
    """
    Реализация градиентной статистической атаки
    """
    
    def __init__(self, cipher: RC5Simplified):
        self.cipher = cipher
        self.w = cipher.w
        
    def generate_nonrandom_sequence(self, count: int) -> List[List[int]]:
        """
        Генерирует последовательность α₀, α₁, ... (двоичные записи чисел)
        как в тексте
        """
        sequence = []
        for i in range(count):
            bits = int_to_bits(i, self.cipher.block_size)
            sequence.append(bits)
        return sequence
    
    def measure_randomness(self, sequence: List[List[int]]) -> float:
        """Измеряет случайность последовательности блоков"""
        # Объединяем все блоки в один битовый поток
        all_bits = []
        for block in sequence:
            all_bits.extend(block)
        
        chi2, _ = adaptive_chi_square(all_bits)
        return chi2
    
    def find_round_key(self, ciphertexts: List[List[int]], round_idx: int, key_space_size: int = None) -> Tuple[Optional[List[int]], float]:
        """
        Находит ключ для указанного раунда методом градиентной атаки
        round_idx: номер раунда (с начала, 0 - первый)
        """
        if key_space_size is None:
            key_space_size = min(2 ** self.w, 256)  # Ограничиваем для скорости
        
        best_key = None
        best_randomness = float('inf')  # Ищем минимум (наименее случайный)
        
        print(f"    Перебор {key_space_size} ключей...")
        
        # Перебираем возможные ключи
        for key_idx in range(key_space_size):
            # Генерируем ключ-кандидат
            candidate_key = int_to_bits(key_idx, self.w)
            
            # Дешифруем целевой раунд с этим ключом
            decrypted = []
            for ct in ciphertexts[:10]:  # Используем подвыборку для скорости
                try:
                    block = self.cipher.decrypt_one_round(ct, candidate_key, round_idx)
                    decrypted.append(block)
                except Exception as e:
                    continue
            
            if not decrypted:
                continue
            
            # Оцениваем случайность
            randomness = self.measure_randomness(decrypted)
            
            # Запоминаем ключ с наименьшей случайностью
            if randomness < best_randomness:
                best_randomness = randomness
                best_key = candidate_key
        
        return best_key, best_randomness
    
    def attack(self, num_blocks: int = 50, rounds_to_attack: int = 2) -> Tuple[List[Optional[List[int]]], List[float]]:
        """
        Выполняет полную атаку
        Возвращает: (найденные ключи, меры случайности)
        """
        print(f"\nЗапуск градиентной атаки на шифр с {self.cipher.rounds} раундами")
        print(f"Размер слова: {self.w} бит, блок: {self.cipher.block_size} бит")
        
        # 1. Генерируем неслучайную последовательность
        print(f"Генерация {num_blocks} неслучайных блоков...")
        plaintexts = self.generate_nonrandom_sequence(num_blocks)
        
        # 2. Шифруем (используем фиксированный ключ)
        print("Шифрование...")
        ciphertexts = []
        for pt in plaintexts:
            ct = self.cipher.encrypt_block(pt)
            ciphertexts.append(ct)
        
        # Проверяем случайность зашифрованной последовательности
        random_val = self.measure_randomness(ciphertexts)
        print(f"  Случайность шифротекста: {random_val:.4f}")
        
        # 3. Атакуем раунды с конца
        found_keys = []
        random_measures = []
        
        # Атакуем последние rounds_to_attack раундов
        for i in range(rounds_to_attack):
            round_idx = self.cipher.rounds - 1 - i
            print(f"\nПоиск ключа для раунда {round_idx} (считая с 0)...")
            
            key, randomness = self.find_round_key(ciphertexts, round_idx)
            found_keys.append(key)
            random_measures.append(randomness)
            
            if key is not None:
                key_str = ''.join(map(str, key[:8])) + '...' if len(key) > 8 else ''.join(map(str, key))
                print(f"  Найден ключ: {key_str}")
            else:
                print(f"  Ключ не найден")
            print(f"  Мера случайности: {randomness:.4f}")
            
            # Обновляем ciphertexts для следующего раунда
            # (дешифруем найденным ключом)
            if key is not None:
                new_ciphertexts = []
                for ct in ciphertexts:
                    try:
                        dec = self.cipher.decrypt_one_round(ct, key, round_idx)
                        new_ciphertexts.append(dec)
                    except:
                        new_ciphertexts.append(ct)
                ciphertexts = new_ciphertexts
        
        return found_keys, random_measures

# ============================================================
# 5. ТЕСТИРОВАНИЕ И ДЕМОНСТРАЦИЯ
# ============================================================

def run_demo():
    """Демонстрация работы атаки"""
    print("=" * 70)
    print("ГРАДИЕНТНАЯ СТАТИСТИЧЕСКАЯ АТАКА НА БЛОЧНЫЙ ШИФР")
    print("=" * 70)
    
    # Создаём шифр с фиксированным ключом для воспроизводимости
    fixed_key = [1, 0, 1, 0, 1, 0, 1, 0]  # 8-битный ключ
    cipher = RC5Simplified(w = 8, rounds = 4, fixed_key = fixed_key)
    
    print(f"\nПараметры шифра:")
    print(f"  Размер слова: {cipher.w} бит")
    print(f"  Число раундов: {cipher.rounds}")
    print(f"  Размер блока: {cipher.block_size} бит")
    print(f"  Фиксированный ключ: {fixed_key}")
    
    # Создаём атаку
    attack = GradientAttack(cipher)
    
    # Выполняем атаку
    print("\n" + "-" * 70)
    found_keys, measures = attack.attack(num_blocks = 30, rounds_to_attack = 2)
    
    print("\n" + "-" * 70)
    print("РЕЗУЛЬТАТЫ АТАКИ:")
    print("-" * 70)
    for i, (key, measure) in enumerate(zip(found_keys, measures)):
        round_num = cipher.rounds - 1 - i
        if key is not None:
            key_str = ''.join(map(str, key))
            print(f"  Раунд {round_num}: ключ = {key_str}, мера = {measure:.4f}")
        else:
            print(f"  Раунд {round_num}: ключ не найден, мера = {measure:.4f}")
    
    # Сравнение с полным перебором
    print("\n" + "-" * 70)
    print("СРАВНЕНИЕ ТРУДОЁМКОСТИ:")
    print("-" * 70)
    key_bits = cipher.w
    total_key_bits = key_bits * (2 * cipher.rounds + 2)  # Приблизительно
    print(f"  Длина одного раундового ключа: {key_bits} бит")
    print(f"  Общая длина ключа: ~{total_key_bits} бит")
    print(f"  Полный перебор: 2 ^ {total_key_bits} операций (огромное число)")
    print(f"  Градиентная атака (2 раунда): ~2 * m * 2 ^ {key_bits} операций")
    print(f"  где m - длина анализируемой последовательности")
    print(f"\n  Экономия: фактор ~2 ^ {total_key_bits - key_bits - 1}")

def test_randomness():
    """Тестирование мер случайности"""
    print("\n" + "=" * 70)
    print("ТЕСТ МЕР СЛУЧАЙНОСТИ")
    print("=" * 70)
    
    # Случайная последовательность
    random_bits = [random.randint(0, 1) for _ in range(1000)]
    chi2, rej = chi_square_test(random_bits)
    print(f"\nСлучайная последовательность (1000 бит):")
    print(f"  Хи-квадрат: {chi2:.4f}")
    print(f"  Отвергнута гипотеза о случайности: {'ДА' if rej else 'НЕТ'}")
    
    # Неслучайная последовательность (все нули)
    nonrandom_bits = [0] * 1000
    chi2, rej = chi_square_test(nonrandom_bits)
    print(f"\nНеслучайная последовательность (все нули):")
    print(f"  Хи-квадрат: {chi2:.4f}")
    print(f"  Отвергнута гипотеза о случайности: {'ДА' if rej else 'НЕТ'}")
    
    # Последовательность с сильной периодичностью
    periodic_bits = [i % 2 for i in range(1000)]
    chi2, rej = chi_square_test(periodic_bits)
    print(f"\nПериодическая последовательность (010101...):")
    print(f"  Хи-квадрат: {chi2:.4f}")
    print(f"  Отвергнута гипотеза о случайности: {'ДА' if rej else 'НЕТ'}")
    
    # Адаптивный тест
    print(f"\nАдаптивный тест для периодической последовательности:")
    chi2, rej = adaptive_chi_square(periodic_bits)
    print(f"  Хи-квадрат: {chi2:.4f}")
    print(f"  Отвергнута гипотеза о случайности: {'ДА' if rej else 'НЕТ'}")

def test_rc5_basic():
    """Базовое тестирование шифра"""
    print("\n" + "=" * 70)
    print("ТЕСТ ШИФРА RC5 (УПРОЩЁННЫЙ)")
    print("=" * 70)
    
    cipher = RC5Simplified(w = 8, rounds = 3)
    
    # Тестовый блок
    plaintext = [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]
    print(f"\nИсходный блок (16 бит): {plaintext}")
    
    # Шифрование
    ciphertext = cipher.encrypt_block(plaintext)
    print(f"Зашифрованный блок: {ciphertext}")
    
    # Дешифрование
    decrypted = cipher.decrypt_block(ciphertext)
    print(f"Расшифрованный блок: {decrypted}")
    
    # Проверка
    success = decrypted == plaintext
    print(f"Корректность шифрования/дешифрования: {'✓ ДА' if success else '✗ НЕТ'}")
    
    # Проверка случайности шифротекста
    chi2, rej = chi_square_test(ciphertext)
    print(f"\nСтатистика шифротекста:")
    print(f"  Хи-квадрат: {chi2:.4f}")
    print(f"  Отличается от случайного: {'ДА' if rej else 'НЕТ'}")

def test_gradient_property():
    """
    Проверка основного свойства градиентной атаки:
    правильный ключ уменьшает случайность, неправильный - увеличивает
    """
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ОСНОВНОГО СВОЙСТВА ГРАДИЕНТНОЙ АТАКИ")
    print("=" * 70)
    
    cipher = RC5Simplified(w = 8, rounds = 4)
    attack = GradientAttack(cipher)
    
    # Генерируем тестовые данные
    plaintexts = attack.generate_nonrandom_sequence(20)
    ciphertexts = [cipher.encrypt_block(pt) for pt in plaintexts]
    
    # Измеряем случайность шифротекста
    random_original = attack.measure_randomness(ciphertexts)
    print(f"\nСлучайность шифротекста (исходная): {random_original:.4f}")
    
    # Для последнего раунда пробуем правильный и неправильные ключи
    # Получаем правильные ключи
    keys = cipher._generate_round_keys()
    correct_key = keys[-2]  # Последний ключ
    
    print(f"\nПравильный ключ последнего раунда: {correct_key[:8]}...")
    
    # Дешифруем с правильным ключом
    decrypted_correct = []
    for ct in ciphertexts[:10]:
        block = cipher.decrypt_one_round(ct, correct_key, cipher.rounds - 1)
        decrypted_correct.append(block)
    random_correct = attack.measure_randomness(decrypted_correct)
    print(f"  Случайность после правильного ключа: {random_correct:.4f} (должна УМЕНЬШИТЬСЯ)")
    
    # Дешифруем с неправильными ключами
    random_wrong_list = []
    for i in range(5):
        wrong_key = [random.randint(0, 1) for _ in range(cipher.w)]
        decrypted_wrong = []
        for ct in ciphertexts[:10]:
            block = cipher.decrypt_one_round(ct, wrong_key, cipher.rounds - 1)
            decrypted_wrong.append(block)
        random_wrong = attack.measure_randomness(decrypted_wrong)
        random_wrong_list.append(random_wrong)
        print(f"  Случайность после неправильного ключа {i + 1}: {random_wrong:.4f} (должна УВЕЛИЧИТЬСЯ)")
    
    # Проверка
    avg_wrong = sum(random_wrong_list) / len(random_wrong_list)
    print(f"\nСредняя случайность для неправильных ключей: {avg_wrong:.4f}")
    
    if random_correct < random_original and avg_wrong > random_original:
        print("\n✓ СВОЙСТВО ПОДТВЕРЖДЕНО: правильный ключ УМЕНЬШАЕТ случайность")
        print("  неправильные ключи УВЕЛИЧИВАЮТ случайность")
    else:
        print("\n✗ Свойство не подтверждено (возможно, нужно больше данных)")

# ============================================================
# 6. ОСНОВНАЯ ПРОГРАММА
# ============================================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    print("\n" + "=" * 70)
    print(" ГРАДИЕНТНАЯ СТАТИСТИЧЕСКАЯ АТАКА")
    print(" Демонстрация на упрощённом RC5")
    print(" (БЕЗ ВНЕШНИХ ЗАВИСИМОСТЕЙ)")
    print("=" * 70)
    
    # Запускаем тесты
    test_rc5_basic()
    test_randomness()
    test_gradient_property()
    run_demo()
    
    print("\n" + "=" * 70)
    print("ЗАВЕРШЕНО")
    print("=" * 70)