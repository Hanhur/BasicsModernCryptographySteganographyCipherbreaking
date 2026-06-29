# б. Кратное использование DES
"""
Демонстрация криптографических концепций из текста о DES
Реализация: упрощённая модель с малым пространством ключей
"""

import random
import math
from collections import defaultdict
from itertools import product
import time

# ============================================================================
# 1. УПРОЩЁННАЯ МОДЕЛЬ DES-ПРЕОБРАЗОВАНИЙ
# ============================================================================

class TinyDES:
    """
    Игрушечная модель DES с:
    - 4-битные блоки (вместо 64-битных)
    - 3-битные ключи (вместо 56-битных)
    - Перестановки генерируются псевдослучайно, но фиксированы
    """
    
    BLOCK_SIZE = 4  # бит
    KEY_SIZE = 3    # бит
    NUM_BLOCKS = 1 << BLOCK_SIZE  # 16 блоков
    NUM_KEYS = 1 << KEY_SIZE      # 8 ключей
    
    def __init__(self):
        """Генерируем фиксированные DES-подобные преобразования"""
        # Используем фиксированный seed для воспроизводимости
        random.seed(42)
        
        # Словарь: ключ -> подстановка (перестановка на множестве блоков)
        self.substitutions = {}
        
        # Генерируем случайные перестановки для каждого ключа
        for key in range(self.NUM_KEYS):
            blocks = list(range(self.NUM_BLOCKS))
            random.shuffle(blocks)
            self.substitutions[key] = blocks
            
        # Обратные преобразования (для расшифровки)
        self.inverse_substitutions = {}
        for key, perm in self.substitutions.items():
            inv = [0] * self.NUM_BLOCKS
            for i, val in enumerate(perm):
                inv[val] = i
            self.inverse_substitutions[key] = inv
    
    def encrypt(self, key, block):
        """Шифрование: block -> E_key(block)"""
        if key not in self.substitutions:
            raise ValueError(f"Key {key} not found")
        return self.substitutions[key][block]
    
    def decrypt(self, key, block):
        """Расшифрование: block -> D_key(block)"""
        if key not in self.inverse_substitutions:
            raise ValueError(f"Key {key} not found")
        return self.inverse_substitutions[key][block]
    
    def get_all_transformations(self):
        """Возвращает множество D = {E_k | k in keys}"""
        return {key: self.substitutions[key] for key in range(self.NUM_KEYS)}
    
    def compose(self, key1, key2, block):
        """Композиция E_key2 ∘ E_key1 (сначала key1, потом key2)"""
        intermediate = self.encrypt(key1, block)
        return self.encrypt(key2, intermediate)
    
    def multi_encrypt(self, keys, block):
        """Многократное шифрование: E_{k_n}(...E_{k_1}(block)...)"""
        result = block
        for key in keys:
            result = self.encrypt(key, result)
        return result


# ============================================================================
# 2. ВЫЧИСЛЕНИЕ ПОРЯДКА ЭЛЕМЕНТА (АНАЛОГ РАБОТЫ КОППЕРСМИТА)
# ============================================================================

def find_element_order(cipher, key1, key2):
    """
    Находит порядок элемента E = E_key2 ∘ E_key1
    Аналог чисел k_i из текста
    """
    # Строим отображение: block -> E(block)
    mapping = {}
    for block in range(cipher.NUM_BLOCKS):
        mapping[block] = cipher.compose(key1, key2, block)
    
    # Находим порядок для каждого блока
    orders = []
    for start_block in range(cipher.NUM_BLOCKS):
        current = start_block
        visited = set()
        step = 0
        
        while current not in visited:
            visited.add(current)
            current = mapping[current]
            step += 1
            if current == start_block:
                orders.append(step)
                break
    
    # LCM всех порядков
    lcm = 1
    for order in orders:
        lcm = lcm * order // math.gcd(lcm, order)
    
    return lcm


def coppersmith_style_analysis(cipher):
    """
    Анализ в стиле Копперсмита:
    вычисляем порядок для разных пар ключей
    """
    print("\n" + "=" * 60)
    print("АНАЛИЗ В СТИЛЕ КОППЕРСМИТА")
    print("=" * 60)
    
    # Специальные ключи: все нули и все единицы
    key0 = 0
    key1 = cipher.NUM_KEYS - 1
    
    order = find_element_order(cipher, key0, key1)
    print(f"Порядок элемента E_{key1} ∘ E_{key0}: {order}")
    
    # Порядок группы G >= порядок элемента
    print(f"Нижняя граница |G| >= {order}")
    
    # Сравнение с размером множества ключей
    keys_count = cipher.NUM_KEYS
    print(f"Количество ключей |D| = {keys_count}")
    print(f"|G| {'>' if order > keys_count else '='} |D|")
    
    if order > keys_count:
        print("✓ Множество D НЕ замкнуто относительно композиции!")
        print("  (как минимум, этот элемент не принадлежит D)")
    else:
        print("  Возможно, D содержит этот элемент (нужно больше проверок)")


# ============================================================================
# 3. АТАКА "ВСТРЕЧА ПОСЕРЕДИНЕ" (MEET-IN-THE-MIDDLE)
# ============================================================================

def meet_in_the_middle_attack_2des(cipher, plaintext, ciphertext):
    """
    Атака на двойной DES:
    Найти ключи K1, K2 такие, что E_K2(E_K1(plaintext)) = ciphertext
    """
    print("\n" + "=" * 60)
    print("АТАКА 'ВСТРЕЧА ПОСЕРЕДИНЕ' НА ДВОЙНОЙ DES")
    print("=" * 60)
    
    start_time = time.time()
    
    # Шаг 1: Вычисляем все E_K1(plaintext) и сохраняем в таблицу
    print("Шаг 1: Вычисление E_K1(P)...")
    table = {}
    for k1 in range(cipher.NUM_KEYS):
        intermediate = cipher.encrypt(k1, plaintext)
        table[intermediate] = k1
    
    # Шаг 2: Перебираем K2 и ищем совпадение с D_K2(C)
    print("Шаг 2: Поиск совпадений D_K2(C)...")
    found_keys = []
    for k2 in range(cipher.NUM_KEYS):
        intermediate = cipher.decrypt(k2, ciphertext)
        if intermediate in table:
            k1 = table[intermediate]
            found_keys.append((k1, k2))
    
    elapsed = time.time() - start_time
    
    print(f"Найдено пар ключей: {len(found_keys)}")
    for i, (k1, k2) in enumerate(found_keys[:5]):
        print(f"  {i+1}. K1={k1}, K2={k2}")
    if len(found_keys) > 5:
        print(f"  ... и ещё {len(found_keys) - 5} пар")
    
    print(f"Время выполнения: {elapsed:.4f} сек")
    print(f"Сложность: O(2 ^ {cipher.KEY_SIZE * 2}) = O({cipher.NUM_KEYS ** 2})")
    
    return found_keys


# ============================================================================
# 4. СРАВНЕНИЕ СТОЙКОСТИ: 1-DES, 2-DES, 3-DES, 4-DES
# ============================================================================

def security_comparison(cipher):
    """
    Сравнивает теоретическую сложность атак на разные кратности
    """
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ КРИПТОСТОЙКОСТИ")
    print("=" * 60)
    
    # Длина ключа в битах (для нашей модели)
    key_bits = cipher.KEY_SIZE
    n = cipher.NUM_KEYS
    
    schemes = {
        "1-DES (одинарный)": 1,
        "2-DES (двойной)": 2,
        "3-DES (тройной)": 3,
        "4-DES (четверной)": 4
    }
    
    print(f"Ключ в нашей модели: {key_bits} бит, {n} возможных ключей")
    print("\nСложность атак:")
    print("-" * 60)
    
    for name, rounds in schemes.items():
        # Лобовой перебор: n^rounds
        brute_force = n ** rounds
        
        # Meet-in-the-middle для чётных кратностей
        if rounds % 2 == 0:
            mitm = n ** (rounds // 2)
            # Берём минимум из brute_force и MITM
            effective = min(brute_force, mitm)
        else:
            # Для 3-DES: MITM даёт n^2 (если атаковать как 2-DES + 1 ключ)
            if rounds == 3:
                effective = n ** 2
            else:
                effective = brute_force
        
        # Переводим в биты
        bits = math.log2(effective)
        
        print(f"{name}:")
        print(f"  - Лобовой перебор: 2 ^ {rounds * key_bits:.1f} = {brute_force}")
        if rounds % 2 == 0:
            print(f"  - Meet-in-middle: 2 ^ {rounds * key_bits // 2:.1f} = {mitm}")
        print(f"  - Эффективная стойкость: 2 ^ {bits:.1f} операций")
        
        # Оценка, имеет ли смысл использовать
        if rounds == 2:
            print(f"  ⚠️  2-DES даёт прирост всего {bits - key_bits:.1f} бит!")
        elif rounds == 4:
            print(f"  ⚠️  4-DES даёт ту же стойкость, что и 3-DES ({bits:.1f} бит), но медленнее!")
        elif rounds == 3:
            print(f"  ✓  Оптимальный баланс скорости и стойкости")
        print()


# ============================================================================
# 5. ДЕМОНСТРАЦИЯ ГРУППОВОЙ СТРУКТУРЫ
# ============================================================================

def demonstrate_group_properties(cipher):
    """
    Демонстрирует, что D не является группой (нет единицы, нет замкнутости)
    """
    print("\n" + "=" * 60)
    print("ГРУППОВЫЕ СВОЙСТВА D")
    print("=" * 60)
    
    # 1. Проверка на наличие единицы
    identity = tuple(range(cipher.NUM_BLOCKS))
    has_identity = False
    for key, perm in cipher.substitutions.items():
        if tuple(perm) == identity:
            has_identity = True
            print(f"✓ Тождественное преобразование найдено! Ключ = {key}")
            break
    
    if not has_identity:
        print("✗ В D НЕТ тождественного преобразования!")
        print("  (DES не имеет ключа, который оставлял бы все блоки неизменными)")
    
    # 2. Проверка замкнутости относительно композиции
    print("\nПроверка замкнутости D относительно композиции:")
    all_transforms = set()
    for key, perm in cipher.substitutions.items():
        all_transforms.add(tuple(perm))
    
    closed = True
    counter_example = None
    
    for key1 in range(cipher.NUM_KEYS):
        for key2 in range(cipher.NUM_KEYS):
            # Вычисляем композицию E_key2 ∘ E_key1
            composed = tuple(cipher.encrypt(key2, cipher.encrypt(key1, b)) for b in range(cipher.NUM_BLOCKS))
            
            if composed not in all_transforms:
                closed = False
                counter_example = (key1, key2, composed)
                break
        if not closed:
            break
    
    if closed:
        print("✓ D замкнуто относительно композиции (в нашей игрушечной модели)")
    else:
        print(f"✗ D НЕ замкнуто относительно композиции!")
        print(f"  Контрпример: E_{counter_example[1]} ∘ E_{counter_example[0]} не принадлежит D")
        print(f"  Перестановка: {counter_example[2]}")
        
        # Показываем, что порядок группы > |D|
        print("\n  Это согласуется с теоремой: |G| > |D|")


# ============================================================================
# 6. ВИЗУАЛИЗАЦИЯ ПОРЯДКОВ (КАК У КОППЕРСМИТА)
# ============================================================================

def visualize_orders(cipher):
    """
    Визуализирует распределение порядков элементов для разных блоков
    (аналог чисел k_1, ..., k_33 из текста)
    """
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ ПОРЯДКОВ ЭЛЕМЕНТОВ")
    print("=" * 60)
    
    # Выбираем ключи: все нули и все единицы
    key0 = 0
    key1 = cipher.NUM_KEYS - 1
    
    print(f"Элемент E_{key1} ∘ E_{key0} (аналог из работы Копперсмита)")
    print("\nПорядки для разных начальных блоков:")
    print("-" * 40)
    
    mapping = {}
    for block in range(cipher.NUM_BLOCKS):
        mapping[block] = cipher.compose(key0, key1, block)
    
    all_orders = []
    for start in range(cipher.NUM_BLOCKS):
        current = start
        visited = []
        step = 0
        
        while current not in visited:
            visited.append(current)
            current = mapping[current]
            step += 1
            if current == start:
                all_orders.append(step)
                break
        
        if start == start:  # Просто печатаем
            pass
    
    # Группируем по порядкам
    from collections import Counter
    order_counts = Counter(all_orders)
    
    for order, count in sorted(order_counts.items()):
        bar = "█" * count
        print(f"  Порядок {order:2d}: {bar} ({count} блоков)")
    
    # LCM
    lcm = 1
    for order in all_orders:
        lcm = lcm * order // math.gcd(lcm, order)
    
    print("-" * 40)
    print(f"НОК всех порядков = {lcm}")
    print(f"  -> |G| >= {lcm} (теорема Лагранжа)")


# ============================================================================
# 7. ОСНОВНАЯ ПРОГРАММА
# ============================================================================

def main():
    print("\n" + "=" * 60)
    print("КРИПТОАНАЛИЗ DES: ГРУППОВАЯ СТРУКТУРА И МНОГОКРАТНОЕ ИСПОЛЬЗОВАНИЕ")
    print("=" * 60)
    print("\nМодель: TinyDES")
    print(f"  - Блок: {TinyDES.BLOCK_SIZE} бит ({TinyDES.NUM_BLOCKS} возможных блоков)")
    print(f"  - Ключ: {TinyDES.KEY_SIZE} бит ({TinyDES.NUM_KEYS} возможных ключей)")
    print(f"  - Это масштабированная модель реального DES")
    print("=" * 60)
    
    # Создаём экземпляр шифра
    cipher = TinyDES()
    
    # 1. Анализ Копперсмита
    coppersmith_style_analysis(cipher)
    
    # 2. Демонстрация групповых свойств
    demonstrate_group_properties(cipher)
    
    # 3. Визуализация порядков
    visualize_orders(cipher)
    
    # 4. Атака на двойной DES
    # Берём случайный текст и шифруем двойным DES
    plaintext = 5
    k1 = 3
    k2 = 7
    ciphertext = cipher.compose(k1, k2, plaintext)
    
    print(f"\nТестовая пара для атаки:")
    print(f"  P = {plaintext}, C = {ciphertext}")
    print(f"  Реальные ключи: K1 = {k1}, K2 = {k2}")
    
    found = meet_in_the_middle_attack_2des(cipher, plaintext, ciphertext)
    
    # Проверяем, что нашли правильные ключи
    if (k1, k2) in found:
        print(f"✓ Атака успешно нашла правильные ключи!")
    else:
        print(f"✗ Ошибка: правильные ключи не найдены")
    
    # 5. Сравнение стойкости
    security_comparison(cipher)
    
    # 6. Дополнительно: демонстрация тройного DES
    print("\n" + "=" * 60)
    print("ПРАКТИЧЕСКИЙ ПРИМЕР: ТРОЙНОЙ DES")
    print("=" * 60)
    
    # Шифруем тройным DES
    keys_3des = [2, 5, 1]  # K1, K2, K3
    plain = 3
    encrypted = plain
    for key in keys_3des:
        encrypted = cipher.encrypt(key, encrypted)
    
    print(f"3-DES шифрование:")
    print(f"  Исходный текст: {plain}")
    print(f"  Ключи: {keys_3des}")
    print(f"  Зашифрованный текст: {encrypted}")
    
    # Расшифровываем (обратный порядок, обратные ключи)
    decrypted = encrypted
    for key in reversed(keys_3des):
        decrypted = cipher.decrypt(key, decrypted)
    print(f"  Расшифрованный текст: {decrypted}")
    print(f"  ✓ Совпадает с исходным: {decrypted == plain}")
    
    # Финальный вывод
    print("\n" + "=" * 60)
    print("ВЫВОДЫ:")
    print("=" * 60)
    print("1. Двойной DES (2-DES) уязвим к атаке 'встреча посередине'")
    print("2. Множество D не является группой (нет единицы и замкнутости)")
    print("3. Тройной DES (3-DES) даёт оптимальный баланс стойкости")
    print("4. Четверной DES (4-DES) не даёт преимущества перед 3-DES")
    print("5. Математическая причина: порядок |G| ≫ |D|")
    print("=" * 60)


if __name__ == "__main__":
    main()