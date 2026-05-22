# 4. Разностный крипта анализ
"""
Учебная демонстрация принципа разностного криптоанализа.
Шифр: 4-битный блок, 1 раунд.
- S-блок: нелинейное преобразование (взят из упрощённого DES-подобного)
- XOR с ключом до и после S-блока (упрощённая сеть Фейстеля для 4 бит)
- Атака восстанавливает ключ после S-блока.
"""

from collections import Counter
import random

# ----------------------------------------------
# Упрощённый S-блок (4x4) с нелинейностью
# Используется для демонстрации дифференциальной неоднородности
# ----------------------------------------------
S_BOX = {
    0b0000: 0b1110,
    0b0001: 0b0100,
    0b0010: 0b1101,
    0b0011: 0b0001,
    0b0100: 0b0010,
    0b0101: 0b1111,
    0b0110: 0b1011,
    0b0111: 0b1000,
    0b1000: 0b0011,
    0b1001: 0b1010,
    0b1010: 0b0110,
    0b1011: 0b1100,
    0b1100: 0b0101,
    0b1101: 0b1001,
    0b1110: 0b0000,
    0b1111: 0b0111,
}

# Обратный S-блок (для вычислений при атаке)
INV_S_BOX = {v: k for k, v in S_BOX.items()}

# ----------------------------------------------
# Функции шифрования (упрощённый 1-раундовый шифр)
# ----------------------------------------------
def apply_sbox(x):
    """Применение S-блока к 4-битному входу."""
    return S_BOX[x & 0b1111]

def encrypt(plaintext, key_before, key_after):
    """
    plaintext: 4 бита
    key_before, key_after: 4 бита
    Шифр: plaintext XOR key_before -> S-Box -> XOR key_after
    """
    x = plaintext ^ key_before
    y = apply_sbox(x)
    ciphertext = y ^ key_after
    return ciphertext

# ----------------------------------------------
# Сбор дифференциальных характеристик S-блока
# ----------------------------------------------
def compute_differential_distribution():
    """
    Для каждого входного XOR (разности) считаем, какие выходные XOR возможны
    и сколько раз встречаются.
    """
    dd = {}
    for dx in range(16):
        dd[dx] = Counter()
        for x1 in range(16):
            x2 = x1 ^ dx
            y1 = apply_sbox(x1)
            y2 = apply_sbox(x2)
            dy = y1 ^ y2
            dd[dx][dy] += 1
    return dd

# ----------------------------------------------
# Разностная атака на последний ключ (key_after)
# Предполагаем, что key_before известен или его влияние учтено.
# В реальном DES атакуют последний раунд.
# Здесь мы показываем принцип: угадываем key_after.
# ----------------------------------------------
def differential_attack(ciphertext_pairs, key_before_known, diff_in):
    """
    ciphertext_pairs: список пар (c1, c2) для пар открытых текстов
                      с известной разностью diff_in перед S-блоком.
    key_before_known: известен или угадан (здесь для простоты задан).
    diff_in: входная разность до S-блока (XOR).
    """
    dd = compute_differential_distribution()
    candidates = Counter()

    # Пробуем все возможные ключи key_after
    for key_guess in range(16):
        count = 0
        for (c1, c2) in ciphertext_pairs:
            # Предполагаем: c1 = S(x1) ^ key_guess, c2 = S(x2) ^ key_guess
            # Тогда S(x1) = c1 ^ key_guess, S(x2) = c2 ^ key_guess
            s_out1 = c1 ^ key_guess
            s_out2 = c2 ^ key_guess
            dy = s_out1 ^ s_out2

            # Если dy возможна для данной входной разности diff_in -> увеличиваем счёт
            if dy in dd[diff_in] and dd[diff_in][dy] > 0:
                # Грубо: если эта выходная разность вообще возможна
                count += 1
        candidates[key_guess] = count

    # Лучший ключ — тот, который даёт максимальное совпадение с характеристикой
    best_key = max(candidates, key = lambda k: candidates[k])
    return best_key, candidates

# ----------------------------------------------
# Генерация пар с фиксированной входной разностью
# ----------------------------------------------
def generate_pairs(key_before, key_after, diff_in, num_pairs):
    pairs = []
    plain_pairs = []
    for _ in range(num_pairs):
        # Выбираем x1 случайно
        x1 = random.randint(0, 15)
        x2 = x1 ^ diff_in
        c1 = encrypt(x1, key_before, key_after)
        c2 = encrypt(x2, key_before, key_after)
        pairs.append((c1, c2))
        plain_pairs.append((x1, x2))
    return pairs, plain_pairs

# ----------------------------------------------
# Главная демонстрация
# ----------------------------------------------
def main():
    print("=== Демонстрация принципа разностного криптоанализа ===")
    print("Шифр: 4-битный блок, 1 раунд: текст -> XOR K1 -> S-Box -> XOR K2")
    print()

    # Секретные ключи (неизвестны атакующему)
    KEY_BEFORE = 0b1010  # 10
    KEY_AFTER = 0b0111   # 7

    print(f"Реальные ключи: K1 = {KEY_BEFORE:04b} ({KEY_BEFORE}), K2 = {KEY_AFTER:04b} ({KEY_AFTER})")
    print()

    # Атакующий выбирает входную разность до S-блока
    # В реальных условиях он пытается найти хорошую характеристику.
    # Здесь используем разность 0b1100 (12), которая даёт сильную неравномерность.
    diff_in = 0b1100

    # Вычисляем распределение для S-блока
    dd = compute_differential_distribution()
    print(f"Дифференциальное распределение S-блока (входная разность {diff_in:04b}):")
    for dy, count in dd[diff_in].items():
        if count > 0:
            print(f"  dy = {dy:04b} -> {count} пар из 16")
    print()

    # Генерируем пары шифртекстов (атакующий знает только их, но знает,
    # что открытые тексты имели разность diff_in до S-блока)
    num_pairs = 200
    pairs, _ = generate_pairs(KEY_BEFORE, KEY_AFTER, diff_in, num_pairs)

    # Предполагаем, что K1 (key_before) известен (или найден другим способом).
    # В полном DES так не делают, но здесь для простоты — чтобы показать атаку на K2.
    # Можно показать, что атака работает и без точного знания K1,
    # если diff_in подобран правильно — но для учебного примера достаточно.
    print(f"Атакующий предполагает, что K1 известен = {KEY_BEFORE:04b} (это упрощение)")
    guessed_key, stats = differential_attack(pairs, KEY_BEFORE, diff_in)

    print(f"\nРезультат атаки:")
    print(f"  Реальный ключ K2: {KEY_AFTER:04b} ({KEY_AFTER})")
    print(f"  Угаданный ключ:   {guessed_key:04b} ({guessed_key})")

    if guessed_key == KEY_AFTER:
        print("  -> Атака успешна! Ключ восстановлен.")
    else:
        print("  -> Атака не удалась (нужно больше пар или другая разность).")

    print("\n=== Примечание ===")
    print("В реальном DES:")
    print("- S-блоки больше (6 входных бит → 4 выходных).")
    print("- Много раундов (16).")
    print("- Атакуют последний раунд, угадывая части ключа.")
    print("- Требуется ~2^47 выбранных открытых текстов для полного 16-раундового DES.")
    print("Данная программа показывает только математический принцип.")

if __name__ == "__main__":
    main()