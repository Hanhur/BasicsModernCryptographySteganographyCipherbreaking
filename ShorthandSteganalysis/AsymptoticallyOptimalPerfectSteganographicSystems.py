# Асимптотически оптимальные совершенные стеганографические системы
import math
import itertools
from collections import Counter
from typing import List, Tuple, Any, Optional

class StegSystem:
    """
    Реализация стегосистемы St_n(A) из раздела 10.4.
    
    Система позволяет скрыто передавать биты в последовательности символов,
    используя перестановочные классы равновероятных блоков.
    """
    
    def __init__(self, alphabet: List[Any], block_size: int = 3):
        """
        Инициализация стегосистемы.
        
        Args:
            alphabet: Список символов алфавита A
            block_size: Длина блока n (параметр метода)
        """
        self.alphabet = sorted(alphabet)  # упорядочиваем для лексикографического порядка
        self.block_size = block_size
        self.alphabet_size = len(alphabet)
        
        # Кэш для ускорения вычислений
        self._factorial_cache = {}
        self._frequency_cache = {}
    
    def _factorial(self, n: int) -> int:
        """Вычисление факториала с кэшированием."""
        if n in self._factorial_cache:
            return self._factorial_cache[n]
        result = math.factorial(n)
        self._factorial_cache[n] = result
        return result
    
    def _count_permutations(self, freq: dict) -> int:
        """
        Вычисление числа перестановок с заданными частотами.
        
        Формула: n! / (∏ freq(a)!)
        """
        total = sum(freq.values())
        result = self._factorial(total)
        for count in freq.values():
            result //= self._factorial(count)
        return result
    
    def _get_frequency_class(self, block: tuple) -> List[tuple]:
        """
        Генерация всех перестановок блока (частотный класс).
        
        Возвращает отсортированный список всех уникальных перестановок.
        """
        # Используем Counter для подсчета частот
        freq = Counter(block)
        
        # Генерируем все уникальные перестановки
        # Для больших n это может быть очень медленно!
        # В реальной реализации нужен алгоритм быстрой нумерации
        unique_permutations = set()
        for perm in itertools.permutations(block):
            unique_permutations.add(perm)
        
        return sorted(unique_permutations)
    
    def _get_block_index(self, block: tuple, permutations: List[tuple]) -> int:
        """Получение индекса блока в отсортированном списке перестановок."""
        return permutations.index(block)
    
    def _find_j(self, size: int, index: int) -> Tuple[int, int, List[int]]:
        """
        Нахождение j(u) - старшего разряда, где α_j != λ_j.
        
        Args:
            size: Размер множества Su (|Su|)
            index: Индекс блока δ(u)
            
        Returns:
            (j, m, alpha_bits) где:
            - j: найденное значение
            - m: максимальная степень двойки
            - alpha_bits: биты числа |Su|
        """
        # Находим m = floor(log2(|Su|))
        m = int(math.floor(math.log2(size)))
        
        # Двоичное представление |Su|
        alpha_bits = []
        temp = size
        for i in range(m, -1, -1):
            if temp >= (1 << i):
                alpha_bits.append(1)
                temp -= (1 << i)
            else:
                alpha_bits.append(0)
        
        # Двоичное представление индекса
        lambda_bits = []
        temp = index
        for i in range(m, -1, -1):
            if temp >= (1 << i):
                lambda_bits.append(1)
                temp -= (1 << i)
            else:
                lambda_bits.append(0)
        
        # Находим j - старший разряд, где α_j != λ_j
        j = -1
        for i in range(m, -1, -1):
            if alpha_bits[m - i] != lambda_bits[m - i]:
                j = i
                break
        
        return j, m, alpha_bits
    
    def encode_block(self, block: tuple, secret_bits: str) -> Tuple[tuple, str, int]:
        """
        Кодирование одного блока.
        
        Args:
            block: Исходный блок (кортеж символов)
            secret_bits: Строка секретных битов
            
        Returns:
            (закодированный_блок, оставшиеся_биты, использовано_бит)
        """
        # Получаем частотный класс
        permutations = self._get_frequency_class(block)
        size = len(permutations)
        index = self._get_block_index(block, permutations)
        
        # Находим j(u)
        j, m, alpha_bits = self._find_j(size, index)
        
        if j < 0:
            # Блок не может быть использован для кодирования
            return block, secret_bits, 0
        
        # Считываем j бит из секретного сообщения
        if len(secret_bits) < j:
            # Недостаточно бит для кодирования
            return block, secret_bits, 0
        
        bits_to_use = secret_bits[:j]
        remaining_bits = secret_bits[j:]
        
        # Преобразуем биты в число τ
        tau = int(bits_to_use, 2) if bits_to_use else 0
        
        # Вычисляем новый индекс
        # new_index = sum_{s=j+1}^{m} α_s * 2^s + τ
        new_index = 0
        for s in range(j + 1, m + 1):
            if alpha_bits[m - s] == 1:
                new_index += (1 << s)
        new_index += tau
        
        # Проверяем, что новый индекс в допустимом диапазоне
        if new_index >= size:
            return block, secret_bits, 0
        
        # Получаем закодированный блок
        encoded_block = permutations[new_index]
        
        return encoded_block, remaining_bits, j
    
    def decode_block(self, block: tuple) -> Tuple[str, int]:
        """
        Декодирование одного блока.
        
        Args:
            block: Полученный блок
            
        Returns:
            (извлеченные_биты, количество_извлеченных_бит)
        """
        # Получаем частотный класс (такой же как при кодировании)
        permutations = self._get_frequency_class(block)
        size = len(permutations)
        index = self._get_block_index(block, permutations)
        
        # Находим j(u)
        j, m, alpha_bits = self._find_j(size, index)
        
        if j < 0:
            # Блок не содержит скрытой информации
            return "", 0
        
        # Вычисляем τ
        # τ = index - sum_{s=j+1}^{m} α_s * 2^s
        base_sum = 0
        for s in range(j + 1, m + 1):
            if alpha_bits[m - s] == 1:
                base_sum += (1 << s)
        
        tau = index - base_sum
        
        # Преобразуем τ в двоичную строку длины j
        if j == 0:
            return "", 0
        
        bits = format(tau, f'0{j}b')
        return bits, j
    
    def encode(self, container: List[Any], secret: str) -> Tuple[List[Any], int]:
        """
        Встраивание секретного сообщения в контейнер.
        
        Args:
            container: Список символов-контейнеров
            secret: Строка бит для встраивания
            
        Returns:
            (заполненный_контейнер, количество_встроенных_бит)
        """
        if len(secret) == 0:
            return container.copy(), 0
        
        # Разбиваем контейнер на блоки
        blocks = []
        for i in range(0, len(container), self.block_size):
            block = tuple(container[i:i + self.block_size])
            if len(block) < self.block_size:
                # Последний неполный блок передаем без изменений
                blocks.append(block)
                break
            blocks.append(block)
        
        # Кодируем каждый блок
        encoded_blocks = []
        remaining_bits = secret
        total_bits_encoded = 0
        
        for block in blocks:
            if len(block) < self.block_size:
                encoded_blocks.append(block)
                continue
            
            encoded_block, remaining_bits, bits_used = self.encode_block(block, remaining_bits)
            encoded_blocks.append(encoded_block)
            total_bits_encoded += bits_used
            
            if len(remaining_bits) == 0:
                # Все биты встроены, остальные блоки передаем без изменений
                break
        
        # Добавляем оставшиеся блоки без изменений
        remaining_blocks_start = len(encoded_blocks)
        for i in range(remaining_blocks_start, len(blocks)):
            encoded_blocks.append(blocks[i])
        
        # Собираем результат
        result = []
        for block in encoded_blocks:
            result.extend(block)
        
        return result, total_bits_encoded
    
    def decode(self, container: List[Any], expected_bits: int = None) -> str:
        """
        Извлечение секретного сообщения из контейнера.
        
        Args:
            container: Заполненный контейнер
            expected_bits: Ожидаемое количество бит (опционально)
            
        Returns:
            Извлеченная строка бит
        """
        # Разбиваем на блоки
        blocks = []
        for i in range(0, len(container), self.block_size):
            block = tuple(container[i:i + self.block_size])
            if len(block) < self.block_size:
                break
            blocks.append(block)
        
        # Декодируем каждый блок
        decoded_bits = ""
        
        for block in blocks:
            bits, count = self.decode_block(block)
            decoded_bits += bits
            
            if expected_bits is not None and len(decoded_bits) >= expected_bits:
                break
        
        return decoded_bits


def test_steg_system():
    """Пример использования стегосистемы."""
    
    # Тест 1: Бинарный алфавит
    print("=== Тест 1: Бинарный алфавит ===")
    alphabet = ['a', 'b']
    steg = StegSystem(alphabet, block_size=2)
    
    container = ['a', 'a', 'b', 'a', 'b', 'a', 'b', 'b']
    secret = "101"
    
    print(f"Контейнер: {container}")
    print(f"Секретное сообщение: {secret}")
    
    encoded, bits_encoded = steg.encode(container, secret)
    print(f"Заполненный контейнер: {encoded}")
    print(f"Встроено бит: {bits_encoded}")
    
    decoded = steg.decode(encoded, expected_bits = len(secret))
    print(f"Извлеченное сообщение: {decoded}")
    print(f"Успешно: {decoded == secret[:bits_encoded]}")
    print()
    
    # Тест 2: Алфавит из 3 символов
    print("=== Тест 2: Алфавит из 3 символов ===")
    alphabet = ['a', 'b', 'c']
    steg = StegSystem(alphabet, block_size = 3)
    
    container = ['b', 'a', 'c', 'a', 'c', 'b', 'c', 'b', 'a']
    secret = "110"
    
    print(f"Контейнер: {container}")
    print(f"Секретное сообщение: {secret}")
    
    encoded, bits_encoded = steg.encode(container, secret)
    print(f"Заполненный контейнер: {encoded}")
    print(f"Встроено бит: {bits_encoded}")
    
    decoded = steg.decode(encoded, expected_bits = len(secret))
    print(f"Извлеченное сообщение: {decoded}")
    print(f"Успешно: {decoded == secret[:bits_encoded]}")
    print()
    
    # Тест 3: Длинное сообщение
    print("=== Тест 3: Длинное сообщение ===")
    alphabet = ['a', 'b', 'c', 'd']
    steg = StegSystem(alphabet, block_size = 4)
    
    # Генерируем контейнер с разными символами для большей емкости
    import random
    random.seed(42)
    container = [random.choice(alphabet) for _ in range(20)]
    secret = "101101001110"
    
    print(f"Контейнер: {container}")
    print(f"Секретное сообщение: {secret}")
    
    encoded, bits_encoded = steg.encode(container, secret)
    print(f"Заполненный контейнер: {encoded}")
    print(f"Встроено бит: {bits_encoded} из {len(secret)}")
    
    decoded = steg.decode(encoded, expected_bits = bits_encoded)
    print(f"Извлеченное сообщение: {decoded}")
    print(f"Успешно: {decoded == secret[:bits_encoded]}")
    print()
    
    # Тест 4: Совершенность системы (проверка статистики)
    print("=== Тест 4: Проверка статистической неразличимости ===")
    alphabet = ['a', 'b']
    steg = StegSystem(alphabet, block_size = 2)
    
    # Создаем много блоков
    import random
    random.seed(123)
    
    # Считаем статистику для исходных и закодированных блоков
    stats_original = Counter()
    stats_encoded = Counter()
    
    for _ in range(1000):
        # Генерируем случайный блок
        block = tuple(random.choice(alphabet) for _ in range(2))
        stats_original[block] += 1
        
        # Кодируем с случайным битом
        secret_bit = str(random.randint(0, 1))
        encoded_block, _, _ = steg.encode_block(block, secret_bit)
        stats_encoded[encoded_block] += 1
    
    print("Распределение исходных блоков:")
    for block, count in sorted(stats_original.items()):
        print(f"  {block}: {count / 1000:.3f}")
    
    print("Распределение закодированных блоков:")
    for block, count in sorted(stats_encoded.items()):
        print(f"  {block}: {count / 1000:.3f}")
    
    print("(Распределения должны быть близки, что подтверждает совершенность системы)")


if __name__ == "__main__":
    test_steg_system()