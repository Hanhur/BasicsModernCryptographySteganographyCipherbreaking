# Задачи и упражнения
# Задача 1. =========================================================================================================================================
import math
from typing import List, Tuple

def find_cycle_length(perm: List[int], element: int) -> int:
    """
    Находит длину цикла, содержащего element, в перестановке perm.
    
    Аргументы:
        perm: список, представляющий перестановку, где perm[i] = d(i)
        element: элемент, для которого ищем длину цикла
    
    Возвращает:
        минимальное k > 0 такое, что d^k(element) = element
    """
    current = element
    visited = set()
    length = 0
    
    while current not in visited:
        visited.add(current)
        current = perm[current]
        length += 1
    
    # Если мы вышли из цикла, значит current уже был посещён,
    # и мы нашли длину цикла, содержащего element
    return length

def order_of_permutation(perm: List[int]) -> int:
    """
    Вычисляет порядок перестановки (НОК длин всех циклов).
    
    Аргументы:
        perm: список, представляющий перестановку
    
    Возвращает:
        порядок перестановки |d|
    """
    n = len(perm)
    visited = [False] * n
    cycle_lengths = []
    
    for i in range(n):
        if not visited[i]:
            # Находим длину цикла, содержащего i
            current = i
            length = 0
            while not visited[current]:
                visited[current] = True
                current = perm[current]
                length += 1
            cycle_lengths.append(length)
    
    # Порядок = НОК длин всех циклов
    result = 1
    for length in cycle_lengths:
        result = result * length // math.gcd(result, length)
    
    return result

def check_division(perm: List[int]) -> List[Tuple[int, int, bool]]:
    """
    Проверяет для каждого элемента, что длина его цикла делит порядок перестановки.
    
    Аргументы:
        perm: список, представляющий перестановку
    
    Возвращает:
        список кортежей (элемент, длина_цикла, делится_ли_на_порядок)
    """
    n = len(perm)
    order = order_of_permutation(perm)
    results = []
    
    for element in range(n):
        k = find_cycle_length(perm, element)
        divides = (order % k == 0)
        results.append((element, k, divides))
    
    return results, order

def print_permutation(perm: List[int]) -> None:
    """Красиво выводит перестановку в виде стрелок."""
    n = len(perm)
    print("Перестановка d:")
    for i in range(n):
        print(f"  {i} -> {perm[i]}")
    print()

def print_cycles(perm: List[int]) -> None:
    """Выводит разложение перестановки на циклы."""
    n = len(perm)
    visited = [False] * n
    cycles = []
    
    for i in range(n):
        if not visited[i]:
            cycle = []
            current = i
            while not visited[current]:
                visited[current] = True
                cycle.append(current)
                current = perm[current]
            if cycle:
                cycles.append(cycle)
    
    print("Разложение на независимые циклы:")
    for cycle in cycles:
        print(f"  ({' '.join(map(str, cycle))})")
    print()

def main():
    # Пример 1: простая перестановка
    print("=" * 50)
    print("ПРИМЕР 1: Простая перестановка")
    print("=" * 50)
    
    # Перестановка: 0->1, 1->2, 2->0, 3->4, 4->3
    # Циклы: (0 1 2) и (3 4)
    perm1 = [1, 2, 0, 4, 3]
    
    print_permutation(perm1)
    print_cycles(perm1)
    
    order1 = order_of_permutation(perm1)
    print(f"Порядок перестановки |d| = {order1}")
    print()
    
    results1, _ = check_division(perm1)
    print("Проверка деления длин циклов на порядок:")
    for element, k, divides in results1:
        status = "✓" if divides else "✗"
        print(f"  Элемент {element}: длина цикла k = {k}, {order1} % {k} = {order1 % k}  {status}")
    
    print("\n" + "=" * 50)
    print("ПРИМЕР 2: Перестановка с циклами разных длин")
    print("=" * 50)
    
    # Перестановка: (0 1 2 3) и (4 5) и (6)
    # Циклы: (0 1 2 3), (4 5), (6)
    perm2 = [1, 2, 3, 0, 5, 4, 6]
    
    print_permutation(perm2)
    print_cycles(perm2)
    
    order2 = order_of_permutation(perm2)
    print(f"Порядок перестановки |d| = {order2}")
    print()
    
    results2, _ = check_division(perm2)
    print("Проверка деления длин циклов на порядок:")
    for element, k, divides in results2:
        status = "✓" if divides else "✗"
        print(f"  Элемент {element}: длина цикла k = {k}, {order2} % {k} = {order2 % k}  {status}")
    
    print("\n" + "=" * 50)
    print("ПРИМЕР 3: Произвольная перестановка (проверка всех элементов)")
    print("=" * 50)
    
    # Перестановка: (0)(1 2 3 4)(5 6 7)
    perm3 = [0, 2, 3, 4, 1, 6, 7, 5]
    
    print_permutation(perm3)
    print_cycles(perm3)
    
    order3 = order_of_permutation(perm3)
    print(f"Порядок перестановки |d| = {order3}")
    print()
    
    results3, _ = check_division(perm3)
    print("Проверка деления длин циклов на порядок:")
    for element, k, divides in results3:
        status = "✓" if divides else "✗"
        print(f"  Элемент {element}: длина цикла k = {k}, {order3} % {k} = {order3 % k}  {status}")
    
    print("\n" + "=" * 50)
    print("ПРИМЕР 4: Интерактивный ввод")
    print("=" * 50)
    
    # Позволяем пользователю ввести свою перестановку
    try:
        n = int(input("Введите размер множества M (количество элементов): "))
        print(f"Введите перестановку как список из {n} чисел через пробел")
        print("(например, для n = 3: 1 2 0 означает 0 -> 1, 1 -> 2, 2 -> 0)")
        perm_str = input("Ваша перестановка: ")
        perm_user = list(map(int, perm_str.split()))
        
        if len(perm_user) != n:
            print(f"Ошибка: нужно ровно {n} чисел")
        else:
            # Проверяем, что это действительно перестановка
            if sorted(perm_user) != list(range(n)):
                print("Ошибка: введённые числа не образуют перестановку (должны быть все числа от 0 до n - 1)")
            else:
                print("\n" + "-" * 40)
                print_permutation(perm_user)
                print_cycles(perm_user)
                
                order_user = order_of_permutation(perm_user)
                print(f"Порядок перестановки |d| = {order_user}")
                print()
                
                results_user, _ = check_division(perm_user)
                print("Проверка деления длин циклов на порядок:")
                all_divide = True
                for element, k, divides in results_user:
                    status = "✓" if divides else "✗"
                    if not divides:
                        all_divide = False
                    print(f"  Элемент {element}: длина цикла k = {k}, {order_user} % {k} = {order_user % k}  {status}")
                
                if all_divide:
                    print("\n✅ Все длины циклов делят порядок перестановки!")
                else:
                    print("\n❌ Найдены длины циклов, не делящие порядок (такого быть не должно!)")
    except ValueError:
        print("Ошибка ввода: пожалуйста, введите целые числа")
    except KeyboardInterrupt:
        print("\nПрограмма завершена.")

if __name__ == "__main__":
    main()
# Задача 2. =========================================================================================================================================
"""
Программа для проверки свойств S-блоков DES:
1) При фиксированных крайних битах центральные 4 бита взаимно-однозначно соответствуют выходу
2) Если входы отличаются только одним битом, выходы отличаются не менее чем на 2 бита
"""

def hamming_distance(x, y):
    """Вычисляет расстояние Хэмминга между двумя числами"""
    return bin(x ^ y).count('1')

def check_property_1(s_box):
    """
    Проверяет свойство 1: для каждой строки (фиксированные крайние биты)
    все 16 значений в строке должны быть уникальными (перестановка 0..15)
    """
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВОЙСТВА 1: Взаимно-однозначное соответствие")
    print("=" * 60)
    
    all_passed = True
    
    for row in range(4):
        values = s_box[row]
        unique_values = set(values)
        
        if len(unique_values) == 16:
            print(f"✓ Строка {row:02b}: Все 16 значений уникальны -> ПЕРЕСТАНОВКА")
        else:
            print(f"✗ Строка {row:02b}: Найдены повторения! {len(unique_values)} уникальных значений из 16")
            # Найдем повторяющиеся значения
            from collections import Counter
            counter = Counter(values)
            duplicates = [val for val, count in counter.items() if count > 1]
            print(f"  Повторяющиеся значения: {duplicates}")
            all_passed = False
    
    if all_passed:
        print("\n✅ СВОЙСТВО 1 ВЫПОЛНЯЕТСЯ: Для всех строк центральные биты дают биекцию на выход")
    else:
        print("\n❌ СВОЙСТВО 1 НЕ ВЫПОЛНЯЕТСЯ")
    
    return all_passed

def check_property_2(s_box):
    """
    Проверяет свойство 2: для любых двух входов, отличающихся в 1 бите,
    расстояние Хэмминга между выходами >= 2
    """
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВОЙСТВА 2: Лавинный эффект (1 бит на входе -> >=2 бит на выходе)")
    print("=" * 60)
    
    all_passed = True
    violations = []
    
    # Перебираем все 6-битовые входы (0..63)
    for input1 in range(64):
        # Получаем строку и столбец для входа
        row1 = (input1 >> 4) & 0b11  # Первый и последний биты
        col1 = input1 & 0b1111       # Центральные 4 бита
        
        # Проверяем все входы, отличающиеся на 1 бит (меняем каждый из 6 битов)
        for bit_pos in range(6):
            input2 = input1 ^ (1 << bit_pos)  # Инвертируем bit_pos-й бит
            
            row2 = (input2 >> 4) & 0b11
            col2 = input2 & 0b1111
            
            # Получаем выходы
            output1 = s_box[row1][col1]
            output2 = s_box[row2][col2]
            
            dist = hamming_distance(output1, output2)
            
            if dist < 2:
                # Найдено нарушение
                violation = {
                    'input1': input1,
                    'input2': input2,
                    'bit_pos': bit_pos,
                    'row1': row1,
                    'col1': col1,
                    'row2': row2,
                    'col2': col2,
                    'output1': output1,
                    'output2': output2,
                    'dist': dist
                }
                violations.append(violation)
                all_passed = False
    
    # Выводим результаты
    if all_passed:
        print("✅ СВОЙСТВО 2 ВЫПОЛНЯЕТСЯ: Все пары дают расстояние >= 2")
    else:
        print(f"❌ СВОЙСТВО 2 НЕ ВЫПОЛНЯЕТСЯ: Найдено {len(violations)} нарушений")
        print("\nПервые 5 нарушений (примеры):")
        for i, v in enumerate(violations[:5]):
            print(f"\nНарушение {i + 1}:")
            print(f"  Вход 1: {v['input1']:06b} (строка {v['row1']:02b}, столбец {v['col1']:04b}) -> выход {v['output1']:04b} ({v['output1']})")
            print(f"  Вход 2: {v['input2']:06b} (строка {v['row2']:02b}, столбец {v['col2']:04b}) -> выход {v['output2']:04b} ({v['output2']})")
            print(f"  Меняется бит {v['bit_pos']}, расстояние Хэмминга на выходе = {v['dist']}")
    
    return all_passed, violations

def print_s_box(s_box):
    """Красиво выводит S-блок"""
    print("\nS-БЛОК:")
    print("       " + " ".join(f"{i:3d}" for i in range(16)))
    print("  " + "-" * 55)
    for row in range(4):
        print(f"{row:02b} | " + " ".join(f"{val:3d}" for val in s_box[row]))

def analyze_s_box(s_box, name = "S-блок"):
    """Полный анализ S-блока"""
    print(f"\n{'=' * 60}")
    print(f"АНАЛИЗ {name}")
    print(f"{'=' * 60}")
    
    print_s_box(s_box)
    
    prop1_ok = check_property_1(s_box)
    prop2_ok, violations = check_property_2(s_box)
    
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 60)
    print(f"Свойство 1 (биекция): {'✅ ВЫПОЛНЯЕТСЯ' if prop1_ok else '❌ НЕ ВЫПОЛНЯЕТСЯ'}")
    print(f"Свойство 2 (>= 2 бит): {'✅ ВЫПОЛНЯЕТСЯ' if prop2_ok else '❌ НЕ ВЫПОЛНЯЕТСЯ'}")
    
    return prop1_ok, prop2_ok

# ============================================================================
# S-БЛОКИ ИЗ СТАНДАРТА DES
# ============================================================================

# S1 - тот, для которого в тексте найден контрпример
S1 = [
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
]

# Другие S-блоки DES (для полноты)
S2 = [
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
    [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
    [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
    [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
]

S3 = [
    [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
    [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
    [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
    [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
]

S4 = [
    [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
    [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
    [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
    [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
]

S5 = [
    [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
    [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
    [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
    [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
]

S6 = [
    [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
    [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
    [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
    [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
]

S7 = [
    [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
    [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
    [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
    [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
]

S8 = [
    [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
    [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
    [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
    [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
]

ALL_S_BOXES = [S1, S2, S3, S4, S5, S6, S7, S8]

# ============================================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВОЙСТВ S-БЛОКОВ DES")
    print("=" * 60)
    
    # Анализируем S1 (как в тексте)
    analyze_s_box(S1, "S1 (первый S-блок DES)")
    
    # Можно также проанализировать все S-блоки
    print("\n\n" + "=" * 60)
    print("СВОДНЫЙ АНАЛИЗ ВСЕХ 8 S-БЛОКОВ")
    print("=" * 60)
    
    summary = []
    for i, s_box in enumerate(ALL_S_BOXES, 1):
        print(f"\n--- S{i} ---")
        prop1, prop2 = analyze_s_box(s_box, f"S{i}")
        summary.append((f"S{i}", prop1, prop2))
    
    print("\n\n" + "=" * 60)
    print("СВОДНАЯ ТАБЛИЦА")
    print("=" * 60)
    print(f"{'S-блок':<8} {'Свойство 1 (биекция)':<25} {'Свойство 2 (>= 2 бит)':<25}")
    print("-" * 60)
    for name, p1, p2 in summary:
        status1 = "✅" if p1 else "❌"
        status2 = "✅" if p2 else "❌"
        print(f"{name:<8} {status1} {'Выполняется' if p1 else 'НЕ выполняется':<20} {status2} {'Выполняется' if p2 else 'НЕ выполняется'}")