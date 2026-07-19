# Атаки на DES
"""
Симулятор атак на DES (демонстрационный)
Основано на тексте об истории и методах взлома DES
"""

import random
import time
from collections import Counter
from itertools import product

# ============================================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БИТАМИ
# ============================================================================

def int_to_bits(n, bits = 64):
    """Преобразование числа в список битов (целые 0/1)"""
    return [int(b) for b in format(n, f'0{bits}b')]

def bits_to_int(bits):
    """Преобразование списка битов в число"""
    return int(''.join(str(b) for b in bits), 2)

def xor_bits(a, b):
    """Побитовое XOR двух списков"""
    return [x ^ y for x, y in zip(a, b)]

def permute(bits, table):
    """Перестановка битов по таблице"""
    return [bits[i-1] for i in table]

def split_half(bits):
    """Разделение на левую и правую половины"""
    mid = len(bits) // 2
    return bits[:mid], bits[mid:]

# ============================================================================
# 2. УПРОЩЕННАЯ ВЕРСИЯ DES (16 РАУНДОВ, УМЕНЬШЕННЫЙ РАЗМЕР ДЛЯ ДЕМОНСТРАЦИИ)
# ============================================================================

class SimplifiedDES:
    """
    Упрощенный DES для демонстрации атак:
    - Блок: 16 бит (вместо 64)
    - Ключ: 8 бит (вместо 56)
    - 4 раунда (вместо 16)
    """
    
    def __init__(self, key):
        self.key = self._fix_key(key)
        self.round_keys = self._generate_round_keys()
        
    def _fix_key(self, key):
        """Приведение ключа к 8 битам"""
        if isinstance(key, int):
            key = int_to_bits(key, 8)
        elif len(key) != 8:
            raise ValueError("Ключ должен быть 8 бит")
        return key
    
    def _generate_round_keys(self):
        """Генерация раундовых ключей (упрощенно)"""
        keys = []
        # Используем простой сдвиг для имитации расписания ключей DES
        for i in range(4):
            shifted = self.key[i:] + self.key[:i]
            # Берем первые 6 бит для раундового ключа
            keys.append(shifted[:6])
        return keys
    
    def _s_box(self, bits, sbox_num):
        """Упрощенный S-блок (4x4)"""
        # Для демонстрации используем фиксированную таблицу
        sboxes = [
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
        ]
        # Берем 4 бита, преобразуем в индекс
        idx = bits_to_int(bits[:4]) % 16
        val = sboxes[sbox_num % 4][idx]
        return int_to_bits(val, 4)
    
    def _f_function(self, right, round_key):
        """Функция Фейстеля (упрощенная)"""
        # Расширение: 6 бит
        expanded = right + [right[0], right[1]]  # Добавляем 2 бита
        expanded = expanded[:6]
        
        # XOR с раундовым ключом
        xored = xor_bits(expanded, round_key)
        
        # S-блоки: разбиваем на две части по 3 бита
        left_sbox = self._s_box(xored[:3] + [0], 0)
        right_sbox = self._s_box(xored[3:] + [1], 1)
        
        # Объединяем
        result = left_sbox + right_sbox
        return result[:6]  # Возвращаем 6 бит
    
    def _round(self, left, right, round_key):
        """Один раунд Фейстеля"""
        new_left = right
        f_output = self._f_function(right, round_key)
        new_right = xor_bits(left, f_output + [0, 0])  # Дополняем до 8 бит
        return new_left, new_right
    
    def encrypt_block(self, plaintext):
        """Шифрование одного блока (16 бит)"""
        if isinstance(plaintext, int):
            plaintext = int_to_bits(plaintext, 16)
        
        left, right = split_half(plaintext)
        
        # 4 раунда
        for i in range(4):
            left, right = self._round(left, right, self.round_keys[i])
        
        # Перестановка перед выходом
        return left + right
    
    def decrypt_block(self, ciphertext):
        """Дешифрование (обратный порядок ключей)"""
        if isinstance(ciphertext, int):
            ciphertext = int_to_bits(ciphertext, 16)
        
        left, right = split_half(ciphertext)
        
        # Обратный порядок раундов
        for i in range(3, -1, -1):
            left, right = self._round(left, right, self.round_keys[i])
        
        return left + right

# ============================================================================
# 3. РЕАЛИЗАЦИЯ АТАК ИЗ ТЕКСТА
# ============================================================================

class DESAttackSimulator:
    """Симулятор атак на DES"""
    
    def __init__(self):
        self.attack_results = {}
    
    def brute_force_attack(self, plaintext, ciphertext, key_bits = 8):
        """
        Атака грубой силой (перебор всех ключей)
        Из текста: "перебор всех возможных комбинаций битов"
        """
        print(f"\n{'=' * 60}")
        print(f"МЕТОД: ГРУБАЯ СИЛА (BRUTE FORCE)")
        print(f"{'=' * 60}")
        print(f"Длина ключа: {key_bits} бит")
        print(f"Количество возможных ключей: 2 ^ {key_bits} = {2 ** key_bits}")
        
        start_time = time.time()
        attempts = 0
        found_key = None
        
        # Перебор всех возможных ключей
        for key_int in range(2 ** key_bits):
            attempts += 1
            key_bits_list = int_to_bits(key_int, key_bits)
            des = SimplifiedDES(key_bits_list)
            
            # Пробуем зашифровать и сравнить
            if des.encrypt_block(plaintext) == ciphertext:
                found_key = key_bits_list
                break
            
            # Показываем прогресс каждые 1000 попыток
            if attempts % 1000 == 0:
                print(f"  Проверено ключей: {attempts}")
        
        elapsed = time.time() - start_time
        
        # Результат
        result = {
            'found': found_key is not None,
            'key': found_key,
            'attempts': attempts,
            'time': elapsed,
            'total_keys': 2 ** key_bits,
            'keys_per_second': attempts / elapsed if elapsed > 0 else 0
        }
        
        print(f"\nРЕЗУЛЬТАТ:")
        if result['found']:
            print(f"  ✓ Ключ найден: {''.join(str(b) for b in found_key)}")
        else:
            print(f"  ✗ Ключ не найден (возможно, не тот открытый текст)")
        print(f"  Попыток: {attempts:,}")
        print(f"  Время: {elapsed:.3f} сек")
        print(f"  Скорость: {result['keys_per_second']:.0f} ключей/сек")
        
        self.attack_results['brute_force'] = result
        return result
    
    def linear_cryptanalysis_simulation(self, plaintext, ciphertext, num_pairs = 100):
        """
        Симуляция линейного криптоанализа
        Из текста: "статистический метод атаки по открытому тексту"
        """
        print(f"\n{'=' * 60}")
        print(f"МЕТОД: ЛИНЕЙНЫЙ КРИПТОАНАЛИЗ")
        print(f"{'=' * 60}")
        print(f"Используется {num_pairs} пар (открытый текст → шифртекст)")
        print("Основан на статистическом анализе битов")
        
        # Генерируем случайные пары для анализа
        pairs = []
        for _ in range(num_pairs):
            pt = random.randint(0, 2 ** 16 - 1)
            ct = self._simulate_encryption(pt)
            pairs.append((pt, ct))
        
        # Анализ корреляции битов (упрощенная версия)
        correlations = []
        for bit_pos in range(16):
            # Считаем, сколько раз бит в открытом тексте = биту в шифртексте
            matches = sum(
                1 for pt, ct in pairs
                if ((pt >> bit_pos) & 1) == ((ct >> bit_pos) & 1)
            )
            correlation = matches / num_pairs
            correlations.append((bit_pos, correlation))
        
        # Находим наиболее коррелированные биты
        correlations.sort(key = lambda x: abs(x[1] - 0.5), reverse = True)
        
        print(f"\nСтатистический анализ:")
        for bit_pos, corr in correlations[:5]:
            deviation = abs(corr - 0.5) * 2
            print(f"  Бит {bit_pos}: корреляция {corr:.3f} (отклонение {deviation:.3f})")
        
        # "Угадываем" ключ на основе статистики
        guessed_key_bits = []
        for i in range(8):
            # Имитация: используем биты с наибольшей корреляцией
            bit_val = 1 if correlations[i][1] > 0.5 else 0
            guessed_key_bits.append(bit_val)
        
        result = {
            'method': 'linear',
            'pairs_used': num_pairs,
            'guessed_key': guessed_key_bits,
            'confidence': max(abs(c - 0.5) for _, c in correlations[:8]) * 2
        }
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"  Предполагаемый ключ: {''.join(str(b) for b in guessed_key_bits)}")
        print(f"  Уверенность: {result['confidence']:.1%}")
        print("  ⚠ Примечание: Линейный криптоанализ не дает 100% гарантии")
        
        self.attack_results['linear'] = result
        return result
    
    def differential_cryptanalysis_simulation(self, plaintext_pairs):
        """
        Симуляция дифференциального криптоанализа
        Из текста: "атакующий пытается выяснить открытый текст или ключ посредством выбранного открытого текста"
        """
        print(f"\n{'=' * 60}")
        print(f"МЕТОД: ДИФФЕРЕНЦИАЛЬНЫЙ КРИПТОАНАЛИЗ")
        print(f"{'=' * 60}")
        print(f"Используются выбранные открытые тексты")
        print("Анализируется различие (XOR) между парами")
        
        # Анализируем дифференциалы
        differentials = {}
        
        for pt1, pt2 in plaintext_pairs:
            # Шифруем оба текста
            ct1 = self._simulate_encryption(pt1)
            ct2 = self._simulate_encryption(pt2)
            
            # Вычисляем разницу
            diff_in = pt1 ^ pt2
            diff_out = ct1 ^ ct2
            
            # Сохраняем дифференциал
            key = (diff_in, diff_out)
            differentials[key] = differentials.get(key, 0) + 1
        
        # Находим наиболее частый дифференциал
        most_common = Counter(differentials.values()).most_common(5)
        
        print(f"\nНайдены дифференциалы:")
        for i, ((diff_in, diff_out), count) in enumerate(
            sorted(differentials.items(), key = lambda x: x[1], reverse = True)[:5]
        ):
            prob = count / len(plaintext_pairs)
            print(f"  #{i + 1}: ΔIN = {diff_in:04X} → ΔOUT = {diff_out:04X} " f"(встречается {count} / {len(plaintext_pairs)}, вероятность {prob:.3f})")
        
        # Восстанавливаем ключ через дифференциал
        # (упрощенно: используем самый частый дифференциал)
        if differentials:
            best_diff = max(differentials, key = differentials.get)
            recovered_key = int_to_bits(best_diff[0] & 0xFF, 8)
        else:
            recovered_key = [0] * 8
        
        result = {
            'method': 'differential',
            'pairs_used': len(plaintext_pairs),
            'recovered_key': recovered_key,
            'top_differentials': sorted(differentials.items(), key = lambda x: x[1], reverse = True)[:5]
        }
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"  Восстановленный ключ: {''.join(str(b) for b in recovered_key)}")
        print("  ⚠ Примечание: Для полного DES требуется 2 ^ 47 пар")
        
        self.attack_results['differential'] = result
        return result
    
    def weak_keys_demo(self):
        """
        Демонстрация слабых ключей
        Из текста: "слабые ключи возникают, когда на 16-м этапе генерации ключа получается 16 идентичных ключей"
        """
        print(f"\n{'=' * 60}")
        print(f"ДЕМОНСТРАЦИЯ СЛАБЫХ КЛЮЧЕЙ")
        print(f"{'=' * 60}")
        
        # Слабые ключи из текста
        weak_keys = [
            ([0,0,0,0,0,0,0,0], "Все нули"),
            ([1,1,1,1,1,1,1,1], "Все единицы"),
            ([0,1,0,1,0,1,0,1], "Чередующиеся 0101"),
            ([1,0,1,0,1,0,1,0], "Чередующиеся 1010")
        ]
        
        test_plaintext = int_to_bits(0x1234, 16)
        
        print(f"Тестовый открытый текст: {''.join(str(b) for b in test_plaintext)}")
        print(f"Значение: 0x{bits_to_int(test_plaintext):04X}\n")
        
        for key_bits, desc in weak_keys:
            print(f"СЛАБЫЙ КЛЮЧ: {desc}")
            print(f"  Ключ: {''.join(str(b) for b in key_bits)}")
            
            des = SimplifiedDES(key_bits)
            
            # Шифруем
            ciphertext = des.encrypt_block(test_plaintext)
            print(f"  Шифртекст: {''.join(str(b) for b in ciphertext)}")
            
            # Шифруем еще раз (автообратимость)
            decrypted = des.encrypt_block(ciphertext)  # В DES шифрование = дешифрование
            print(f"  Повторное шифрование: {''.join(str(b) for b in decrypted)}")
            
            # Проверяем автообратимость
            is_involution = decrypted == test_plaintext
            print(f"  Автообратимость: {'✓ ДА' if is_involution else '✗ НЕТ'}")
            
            # Демонстрируем, что все раундовые ключи одинаковые
            round_keys = des.round_keys
            all_same = all(k == round_keys[0] for k in round_keys)
            print(f"  Раундовые ключи одинаковы: {'✓ ДА' if all_same else '✗ НЕТ'}")
            if all_same:
                print(f"    K1 = K2 = K3 = K4 = {''.join(str(b) for b in round_keys[0])}")
            print()
    
    def _simulate_encryption(self, plaintext):
        """Имитация шифрования для статистических атак"""
        key = random.randint(0, 255)  # Случайный ключ
        des = SimplifiedDES(key)
        ciphertext = des.encrypt_block(plaintext)
        return bits_to_int(ciphertext)
    
    def compare_attack_methods(self):
        """Сравнение эффективности методов"""
        print(f"\n{'=' * 60}")
        print(f"СРАВНЕНИЕ МЕТОДОВ АТАК")
        print(f"{'=' * 60}")
        
        methods = {
            'Грубая сила': self.attack_results.get('brute_force'),
            'Линейный анализ': self.attack_results.get('linear'),
            'Дифференциальный': self.attack_results.get('differential')
        }
        
        print(f"{'Метод':<20} {'Успех':<10} {'Время/Сложность':<20}")
        print("-" * 50)
        
        for name, result in methods.items():
            if result:
                if name == 'Грубая сила':
                    status = "✓" if result['found'] else "✗"
                    complexity = f"{result['attempts']:,} попыток"
                elif name == 'Линейный анализ':
                    status = f"{result['confidence']:.0%}"
                    complexity = f"{result['pairs_used']} пар"
                else:  # Дифференциальный
                    status = "✓" if result['recovered_key'] else "✗"
                    complexity = f"{result['pairs_used']} пар"
                
                print(f"{name:<20} {status:<10} {complexity:<20}")
            else:
                print(f"{name:<20} {'N/A':<10} {'Не запущен':<20}")

# ============================================================================
# 4. ЗАПУСК ДЕМОНСТРАЦИИ
# ============================================================================

def main():
    """Главная функция демонстрации"""
    
    print("=" * 70)
    print("  СИМУЛЯТОР АТАК НА DES")
    print("  Основано на истории криптоанализа DES")
    print("  Автор: Упрощенная демонстрация для образовательных целей")
    print("=" * 70)
    
    # Инициализация
    simulator = DESAttackSimulator()
    
    # Создаем тестовые данные
    test_plaintext = int_to_bits(0xABCD, 16)
    test_key = int_to_bits(0x37, 8)
    
    print(f"\nТЕСТОВЫЕ ДАННЫЕ:")
    print(f"  Открытый текст: {''.join(str(b) for b in test_plaintext)} (0x{bits_to_int(test_plaintext):04X})")
    print(f"  Ключ: {''.join(str(b) for b in test_key)} (0x{bits_to_int(test_key):02X})")
    
    # Шифруем тестовый блок
    des = SimplifiedDES(test_key)
    ciphertext = des.encrypt_block(test_plaintext)
    print(f"  Шифртекст: {''.join(str(b) for b in ciphertext)} (0x{bits_to_int(ciphertext):04X})")
    
    # --- 1. АТАКА ГРУБОЙ СИЛОЙ ---
    simulator.brute_force_attack(test_plaintext, ciphertext, key_bits = 8)
    
    # --- 2. ЛИНЕЙНЫЙ КРИПТОАНАЛИЗ ---
    simulator.linear_cryptanalysis_simulation(
        bits_to_int(test_plaintext), 
        bits_to_int(ciphertext),
        num_pairs = 200
    )
    
    # --- 3. ДИФФЕРЕНЦИАЛЬНЫЙ КРИПТОАНАЛИЗ ---
    # Генерируем пары открытых текстов с малыми различиями
    pairs = []
    for i in range(50):
        pt1 = random.randint(0, 65535)
        # Изменяем несколько бит
        pt2 = pt1 ^ (1 << (i % 16)) ^ (1 << ((i + 3) % 16))
        pairs.append((pt1, pt2))
    
    simulator.differential_cryptanalysis_simulation(pairs)
    
    # --- 4. ДЕМОНСТРАЦИЯ СЛАБЫХ КЛЮЧЕЙ ---
    simulator.weak_keys_demo()
    
    # --- 5. СРАВНЕНИЕ МЕТОДОВ ---
    simulator.compare_attack_methods()
    
    print("\n" + "=" * 70)
    print("  ВЫВОДЫ:")
    print("  1. Грубая сила работает для коротких ключей, но для 56-бит требует")
    print("     огромных вычислительных ресурсов (EFF потребовалось 56 часов).")
    print("  2. Линейный криптоанализ эффективен статистически, но требует")
    print("     большого количества известных пар текстов.")
    print("  3. Дифференциальный анализ использует выбранные тексты и")
    print("     является мощным инструментом против блочных шифров.")
    print("  4. Слабые ключи делают шифрование бесполезным - они были")
    print("     известны с самого начала и исключаются из использования.")
    print("=" * 70)
    
    print("\n💡 РЕАЛЬНЫЙ DES (56-бит):")
    print("  - Взломан аппаратно в 1998 году")
    print("  - Использовано 1500 микрочипов по 40 МГц")
    print("  - Поиск занял 4.5 машинных дня")
    print("  - Заменен на AES с ключами 128 / 192 / 256 бит")

if __name__ == "__main__":
    main()