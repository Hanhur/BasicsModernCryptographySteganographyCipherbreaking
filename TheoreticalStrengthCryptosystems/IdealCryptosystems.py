# Идеальные криптосистемы
import math
import random
from typing import Tuple, List, Optional
from itertools import combinations


class IdealCipher:
    """
    Реализация строго идеального шифра на основе метода Шеннона.
    
    Шифр работает с двоичным источником без памяти, разбивая сообщение
    на блоки длины n и шифруя только случайную компоненту w.
    """
    
    def __init__(self, n: int, key: str):
        """
        Инициализация шифра.
        
        Args:
            n: длина блока (n > 1)
            key: секретный ключ (бинарная строка)
        """
        self.n = n
        self.key = key
        self.key_len = len(key)
        
        # Размер поля для хранения числа n1 (от 0 до n)
        self.u_bits = math.ceil(math.log2(n + 1))
        
        # Для кэширования комбинаторных чисел
        self._comb_cache = {}
    
    def _comb(self, n: int, k: int) -> int:
        """Вычисление числа сочетаний C(n, k) с кэшированием."""
        if k < 0 or k > n:
            return 0
        if k > n - k:
            k = n - k
        key = (n, k)
        if key in self._comb_cache:
            return self._comb_cache[key]
        
        result = 1
        for i in range(1, k + 1):
            result = result * (n - k + i) // i
        self._comb_cache[key] = result
        return result
    
    def _count_ones(self, block: str) -> int:
        """Подсчет количества единиц (a2) в блоке."""
        return block.count('1')
    
    def _block_to_number(self, block: str) -> int:
        """Преобразование блока в число (a1 = 0, a2 = 1)."""
        return int(block, 2) if block else 0
    
    def _number_to_block(self, num: int, length: int) -> str:
        """Преобразование числа обратно в блок."""
        return format(num, f'0{length}b')
    
    def _generate_all_blocks(self, n1: int, n2: int) -> List[str]:
        """
        Генерация всех блоков с n1 нулями и n2 единицами.
        Используется для демонстрации, для больших n применяется
        комбинаторный алгоритм.
        """
        positions = list(range(n1 + n2))
        blocks = []
        for ones_pos in combinations(positions, n2):
            block = ['0'] * (n1 + n2)
            for pos in ones_pos:
                block[pos] = '1'
            blocks.append(''.join(block))
        return sorted(blocks)
    
    def _compute_rank(self, block: str) -> int:
        """
        Вычисление ранга блока в упорядоченном множестве всех блоков
        с таким же количеством единиц (комбинаторная нумерация).
        
        Используется алгоритм ранжирования сочетаний.
        """
        n = len(block)
        ones = block.count('1')
        zeros = n - ones
        
        # Ранг среди всех блоков с таким же количеством единиц
        rank = 0
        ones_left = ones
        zeros_left = zeros
        
        for i, char in enumerate(block):
            if char == '1':
                # Если на этой позиции стоит 1, то все блоки с 0 здесь
                # идут раньше
                if zeros_left > 0:
                    rank += self._comb(zeros_left + ones_left - 1, ones_left)
                ones_left -= 1
            else:
                zeros_left -= 1
        
        return rank
    
    def _unrank_block(self, n1: int, n2: int, rank: int) -> str:
        """
        Восстановление блока по его рангу (обратная операция).
        """
        n = n1 + n2
        block = []
        ones_left = n2
        zeros_left = n1
        
        for pos in range(n):
            if zeros_left == 0:
                block.append('1')
                ones_left -= 1
            elif ones_left == 0:
                block.append('0')
                zeros_left -= 1
            else:
                # Количество блоков, начинающихся с 0
                count_with_zero = self._comb(zeros_left + ones_left - 1, ones_left)
                if rank < count_with_zero:
                    block.append('0')
                    zeros_left -= 1
                else:
                    block.append('1')
                    rank -= count_with_zero
                    ones_left -= 1
        
        return ''.join(block)
    
    def _split_into_subsets(self, total: int) -> List[int]:
        """
        Разбиение множества размера total на подмножества
        с размерами, равными степеням двойки.
        
        Например: 21 -> [16, 4, 1]
        """
        if total <= 0:
            return []
        
        subsets = []
        remaining = total
        power = 1 << (remaining.bit_length() - 1)  # Наибольшая степень двойки <= total
        
        while remaining > 0:
            while power > remaining:
                power >>= 1
            subsets.append(power)
            remaining -= power
        
        return subsets
    
    def _get_v_bits(self, subsets: List[int]) -> int:
        """Определяет количество бит для кодирования v."""
        if len(subsets) <= 1:
            return 0
        return math.ceil(math.log2(len(subsets)))
    
    def _get_w_bits(self, subsets: List[int], v_value: int) -> int:
        """Определяет количество бит для кодирования w."""
        if v_value >= len(subsets):
            raise ValueError(f"v_value = {v_value} выходит за пределы subsets = {subsets}")
        return int(math.log2(subsets[v_value]))
    
    def encode_block(self, block: str) -> Tuple[str, str, str]:
        """
        Преобразование блока в формат (u, v, w).
        
        Returns:
            u: количество единиц в блоке (закодированное)
            v: номер подмножества
            w: номер внутри подмножества (случайная компонента)
        """
        if len(block) != self.n:
            raise ValueError(f"Длина блока должна быть {self.n}")
        
        # Подсчет количества единиц (a2)
        n1 = self._count_ones(block)
        n2 = self.n - n1
        
        # u - кодирование n1
        u = format(n1, f'0{self.u_bits}b')
        
        # Всего блоков с таким количеством единиц
        total = self._comb(self.n, n1)
        
        # Ранг блока в упорядоченном множестве
        rank = self._compute_rank(block)
        
        # Разбиение на подмножества со степенями двойки
        subsets = self._split_into_subsets(total)
        
        # Определяем, в какое подмножество попадает блок
        cumulative = 0
        v_value = 0
        w_value = 0
        
        for idx, size in enumerate(subsets):
            if rank < cumulative + size:
                v_value = idx
                w_value = rank - cumulative
                break
            cumulative += size
        
        # Определяем количество бит для v
        v_bits = self._get_v_bits(subsets)
        if v_bits > 0:
            v = format(v_value, f'0{v_bits}b')
        else:
            v = ''
        
        # Определяем количество бит для w (размер подмножества - степень двойки)
        w_bits = self._get_w_bits(subsets, v_value)
        w = format(w_value, f'0{w_bits}b')
        
        return u, v, w
    
    def decode_block(self, u: str, v: str, w: str) -> str:
        """
        Восстановление блока из формата (u, v, w).
        """
        # Восстанавливаем n1 из u
        n1 = int(u, 2)
        n2 = self.n - n1
        
        # Восстанавливаем v_value
        if v == '':
            v_value = 0
        else:
            v_value = int(v, 2)
        
        # Восстанавливаем w_value
        w_value = int(w, 2)
        
        # Восстанавливаем полный ранг
        total = self._comb(self.n, n1)
        subsets = self._split_into_subsets(total)
        
        if v_value >= len(subsets):
            raise ValueError(f"v_value = {v_value} выходит за пределы subsets = {subsets}")
        
        cumulative = 0
        for idx, size in enumerate(subsets):
            if idx == v_value:
                rank = cumulative + w_value
                break
            cumulative += size
        
        # Восстанавливаем блок по рангу
        return self._unrank_block(n1, n2, rank)
    
    def _parse_encoded_blocks(self, ciphertext: str) -> List[Tuple[str, str, str]]:
        """
        Разбор зашифрованного сообщения на компоненты (u, v, w_encrypted).
        """
        if not ciphertext:
            return []
        
        blocks = []
        idx = 0
        
        while idx < len(ciphertext):
            # Извлекаем u
            if idx + self.u_bits > len(ciphertext):
                raise ValueError(f"Недостаточно данных для чтения u на позиции {idx}")
            
            u = ciphertext[idx:idx + self.u_bits]
            idx += self.u_bits
            
            n1 = int(u, 2)
            n2 = self.n - n1
            
            # Определяем размер множества и разбиение
            total = self._comb(self.n, n1)
            subsets = self._split_into_subsets(total)
            
            # Определяем количество бит для v
            v_bits = self._get_v_bits(subsets)
            
            # Извлекаем v
            if v_bits > 0:
                if idx + v_bits > len(ciphertext):
                    raise ValueError(f"Недостаточно данных для чтения v на позиции {idx}")
                v = ciphertext[idx:idx + v_bits]
                idx += v_bits
                v_value = int(v, 2)
            else:
                v = ''
                v_value = 0
            
            # Определяем размер w
            if v_value >= len(subsets):
                raise ValueError(f"v_value = {v_value} выходит за пределы subsets = {subsets}")
            
            w_bits = self._get_w_bits(subsets, v_value)
            
            # Извлекаем зашифрованное w
            if idx + w_bits > len(ciphertext):
                raise ValueError(f"Недостаточно данных для чтения w на позиции {idx}")
            
            w_encrypted = ciphertext[idx:idx + w_bits]
            idx += w_bits
            
            blocks.append((u, v, w_encrypted))
        
        return blocks
    
    def encrypt(self, message: str) -> str:
        """
        Шифрование сообщения.
        
        Args:
            message: бинарное сообщение для шифрования
        
        Returns:
            зашифрованное сообщение в формате u|v|z|u|v|z|...
        """
        if not message:
            return ""
        
        # Дополняем сообщение до кратности n
        padding_len = (self.n - len(message) % self.n) % self.n
        if padding_len > 0:
            # Добавляем случайные биты в конец
            message = message + '0' * padding_len
        
        # Разбиваем на блоки
        blocks = [message[i:i + self.n] for i in range(0, len(message), self.n)]
        
        result_parts = []
        w_stream = []  # Собираем все w для шифрования
        
        # Сначала кодируем все блоки, чтобы собрать w
        encoded_blocks = []
        for block in blocks:
            u, v, w = self.encode_block(block)
            encoded_blocks.append((u, v, w))
            w_stream.append(w)
        
        # Склеиваем все w в одну последовательность
        w_all = ''.join(w_stream)
        
        # Шифруем w с помощью XOR с повторяющимся ключом
        w_encrypted = self._xor_with_key(w_all)
        
        # Разбиваем зашифрованные w обратно по блокам
        w_encrypted_parts = []
        idx = 0
        for _, _, w in encoded_blocks:
            w_len = len(w)
            w_encrypted_parts.append(w_encrypted[idx:idx + w_len])
            idx += w_len
        
        # Формируем итоговый шифртекст
        for i, (u, v, _) in enumerate(encoded_blocks):
            result_parts.append(u)
            if v:  # v может быть пустым
                result_parts.append(v)
            result_parts.append(w_encrypted_parts[i])
        
        return ''.join(result_parts)
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Дешифрование сообщения.
        
        Args:
            ciphertext: зашифрованное сообщение
        
        Returns:
            расшифрованное бинарное сообщение
        """
        if not ciphertext:
            return ""
        
        # Разбираем шифртекст на компоненты
        encoded_blocks = self._parse_encoded_blocks(ciphertext)
        
        # Собираем все зашифрованные w
        w_encrypted_parts = [w_enc for _, _, w_enc in encoded_blocks]
        w_all_encrypted = ''.join(w_encrypted_parts)
        
        # Расшифровываем все w
        w_all = self._xor_with_key(w_all_encrypted)
        
        # Разбиваем расшифрованные w по блокам
        w_parts = []
        pos = 0
        for w_enc in w_encrypted_parts:
            w_len = len(w_enc)
            w_parts.append(w_all[pos:pos + w_len])
            pos += w_len
        
        # Восстанавливаем блоки
        decoded_blocks = []
        for i, (u, v, _) in enumerate(encoded_blocks):
            block = self.decode_block(u, v, w_parts[i])
            decoded_blocks.append(block)
        
        return ''.join(decoded_blocks)
    
    def _xor_with_key(self, data: str) -> str:
        """Выполняет XOR с периодически повторяющимся ключом."""
        result = []
        for i, bit in enumerate(data):
            key_bit = self.key[i % self.key_len]
            result.append(str(int(bit) ^ int(key_bit)))
        return ''.join(result)


# Пример использования
def example():
    print("=" * 70)
    print("СТРОГО ИДЕАЛЬНЫЙ ШИФР (метод Шеннона)")
    print("=" * 70)
    
    # Параметры
    n = 5  # длина блока
    key = "011"  # секретный ключ
    
    # Создаем шифр
    cipher = IdealCipher(n, key)
    
    # Исходное сообщение из примера в учебнике
    message = "1101110110"  # a2a2a1a2a2a2a1a2a2a1
    # где 1 = a2, 0 = a1
    
    print(f"Исходное сообщение: {message}")
    print(f"Длина: {len(message)} бит")
    print(f"Ключ: {key}")
    print(f"Длина ключа: {len(key)} бит")
    print("-" * 70)
    
    # Шифрование
    ciphertext = cipher.encrypt(message)
    print(f"Зашифрованное сообщение: {ciphertext}")
    print(f"Длина шифртекста: {len(ciphertext)} бит")
    
    # Дешифрование
    decrypted = cipher.decrypt(ciphertext)
    print(f"Расшифрованное сообщение: {decrypted}")
    
    # Проверка
    print("-" * 70)
    print(f"Проверка: {'УСПЕШНО' if decrypted == message else 'ОШИБКА'}")
    
    # Демонстрация процесса для одного блока
    print("\n" + "=" * 70)
    print("ДЕТАЛЬНЫЙ РАЗБОР ОДНОГО БЛОКА")
    print("=" * 70)
    
    block = "11011"  # a2a2a1a2a2
    print(f"Блок: {block}")
    print(f"Количество единиц (a2): {block.count('1')}")
    print(f"Количество нулей (a1): {block.count('0')}")
    
    u, v, w = cipher.encode_block(block)
    print(f"u (количество единиц): {u} ({int(u, 2)})")
    print(f"v (номер подмножества): {v if v else '(пусто)'}")
    print(f"w (номер внутри подмножества): {w}")
    
    print(f"\nПреобразованный блок: {u}{v}{w}")
    
    # Шифрование только w
    w_encrypted = cipher._xor_with_key(w)
    print(f"Зашифрованное w: {w_encrypted}")
    
    # Демонстрация восстановления
    decoded = cipher.decode_block(u, v, w)
    print(f"\nВосстановленный блок: {decoded}")
    print(f"Проверка: {'✓' if decoded == block else '✗'}")


def demo_random_messages():
    """Демонстрация работы с большим количеством случайных сообщений."""
    print("\n" + "=" * 70)
    print("ТЕСТ НА СЛУЧАЙНЫХ СООБЩЕНИЯХ")
    print("=" * 70)
    
    n = 5  # Используем меньший n для наглядности
    key = "101"
    cipher = IdealCipher(n, key)
    
    tests_passed = 0
    tests_total = 10
    
    for test_num in range(tests_total):
        # Генерируем случайное сообщение, кратное n
        length = random.randint(2, 10) * n
        message = ''.join(random.choice('01') for _ in range(length))
        
        try:
            ciphertext = cipher.encrypt(message)
            decrypted = cipher.decrypt(ciphertext)
            
            # Обрезаем до исходной длины (из-за дополнения)
            decrypted = decrypted[:len(message)]
            
            if decrypted == message:
                tests_passed += 1
                print(f"Тест {test_num + 1}: ✓")
            else:
                print(f"Тест {test_num + 1}: ✗")
                print(f"  Ожидалось: {message}")
                print(f"  Получено:  {decrypted[:50]}...")
        except Exception as e:
            print(f"Тест {test_num + 1}: ОШИБКА - {e}")
    
    print(f"\nРезультат: {tests_passed} / {tests_total} тестов пройдено")


def demo_statistics():
    """Демонстрация статистических свойств шифра."""
    print("\n" + "=" * 70)
    print("СТАТИСТИЧЕСКИЙ АНАЛИЗ ШИФРА")
    print("=" * 70)
    
    n = 4
    key = "01"
    cipher = IdealCipher(n, key)
    
    # Генерируем все возможные блоки длины n
    all_blocks = [format(i, f'0{n}b') for i in range(2 ** n)]
    
    print(f"Все возможные блоки длины {n}:")
    for block in all_blocks[:8]:  # Показываем только первые 8
        u, v, w = cipher.encode_block(block)
        print(f"  {block} -> u = {u}, v = {v if v else '(пусто)'}, w = {w}")
    
    # Анализируем распределение w
    w_values = []
    for block in all_blocks:
        _, _, w = cipher.encode_block(block)
        w_values.append(w)
    
    print(f"\nРаспределение длин w:")
    from collections import Counter
    w_lengths = Counter([len(w) for w in w_values])
    for length, count in sorted(w_lengths.items()):
        print(f"  |w| = {length}: {count} блоков ({count / len(all_blocks) * 100:.1f}%)")
    
    # Проверяем, что w равномерно распределены
    print(f"\nПроверка равномерности w:")
    w_counts = Counter(w_values)
    for w, count in sorted(w_counts.items()):
        print(f"  w = {w}: {count} раз")


if __name__ == "__main__":
    example()
    demo_statistics()
    demo_random_messages()