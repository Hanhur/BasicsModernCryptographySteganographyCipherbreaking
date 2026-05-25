# 2. Шифр Хилла
"""Шифр Хилла - исправленная и оптимизированная версия."""

from math import gcd
from typing import List, Tuple, Optional

# ============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==============

def modinv(a: int, m: int) -> int:
    """
    Нахождение обратного элемента по модулю.
    Возвращает x такой, что a*x ≡ 1 (mod m).
    """
    a = a % m
    if a == 0:
        raise ValueError(f"Нет обратного элемента для 0 по модулю {m}")
    
    # Расширенный алгоритм Евклида (итеративный)
    original_m = m
    x0, x1 = 1, 0
    
    while m > 1:
        q = a // m
        a, m = m, a - q * m
        x0, x1 = x1, x0 - q * x1
    
    if a != 1:
        raise ValueError(f"Нет обратного элемента для {original_m}? (НОД = {a})")
    
    return x0 % original_m


def matrix_multiply(A: List[List[int]], B: List[List[int]], modulus: int) -> List[List[int]]:
    """Умножение матриц с оптимизацией."""
    if not A or not B:
        return []
    
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    
    if cols_A != rows_B:
        raise ValueError(f"Несоответствие размерностей: {cols_A} != {rows_B}")
    
    # Оптимизация для векторов
    if cols_B == 1:
        result = [[0] for _ in range(rows_A)]
        for i in range(rows_A):
            total = 0
            row_A = A[i]
            for k in range(cols_A):
                total = (total + row_A[k] * B[k][0]) % modulus
            result[i][0] = total
        return result
    
    # Умножение матриц с пропуском нулей
    result = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        row_A = A[i]
        for k in range(cols_A):
            if row_A[k] == 0:
                continue
            val = row_A[k]
            row_B = B[k]
            res_row = result[i]
            for j in range(cols_B):
                res_row[j] = (res_row[j] + val * row_B[j]) % modulus
    
    return result


def matrix_inverse_mod(matrix: List[List[int]], modulus: int) -> List[List[int]]:
    """
    Обращение матрицы по модулю методом Гаусса-Жордана.
    Работает только для обратимых матриц.
    """
    n = len(matrix)
    if n == 0:
        return []
    
    if n != len(matrix[0]):
        raise ValueError("Матрица должна быть квадратной")
    
    # Проверяем обратимость через определитель
    det = matrix_determinant_mod(matrix, modulus)
    if det == 0:
        raise ValueError(f"Матрица вырождена (det = {det})")
    
    try:
        modinv(det, modulus)
    except ValueError:
        raise ValueError(f"Определитель {det} не обратим по модулю {modulus}")
    
    # Создаем расширенную матрицу [M | I]
    augmented = []
    for i in range(n):
        row = matrix[i][:] + [1 if i == j else 0 for j in range(n)]
        augmented.append(row)
    
    # Прямой ход (приведение к верхнетреугольному виду)
    for col in range(n):
        # Поиск строки с ненулевым элементом в текущем столбце
        pivot_row = -1
        for row in range(col, n):
            if augmented[row][col] % modulus != 0:
                pivot_row = row
                break
        
        if pivot_row == -1:
            raise ValueError(f"Матрица необратима: нулевой столбец {col}")
        
        # Меняем строки местами
        if pivot_row != col:
            augmented[col], augmented[pivot_row] = augmented[pivot_row], augmented[col]
        
        # Нормализуем строку
        inv_val = modinv(augmented[col][col], modulus)
        for j in range(2 * n):
            augmented[col][j] = (augmented[col][j] * inv_val) % modulus
        
        # Обнуляем другие строки
        for row in range(n):
            if row != col and augmented[row][col] != 0:
                factor = augmented[row][col]
                for j in range(2 * n):
                    augmented[row][j] = (augmented[row][j] - factor * augmented[col][j]) % modulus
    
    # Извлекаем обратную матрицу
    return [row[n:] for row in augmented]


def matrix_determinant_mod(matrix: List[List[int]], modulus: int) -> int:
    """Вычисление определителя матрицы по модулю."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0] % modulus
    
    # Приводим к верхнетреугольному виду
    M = [row[:] for row in matrix]
    det = 1
    
    for i in range(n):
        # Поиск главного элемента
        pivot = -1
        for r in range(i, n):
            if M[r][i] % modulus != 0:
                pivot = r
                break
        
        if pivot == -1:
            return 0
        
        if pivot != i:
            M[i], M[pivot] = M[pivot], M[i]
            det = (-det) % modulus
        
        det = (det * M[i][i]) % modulus
        
        # Нормализация и исключение
        inv_pivot = modinv(M[i][i], modulus)
        for r in range(i + 1, n):
            if M[r][i] == 0:
                continue
            factor = (M[r][i] * inv_pivot) % modulus
            for c in range(i, n):
                M[r][c] = (M[r][c] - factor * M[i][c]) % modulus
    
    return det % modulus


def solve_linear_system_mod(A: List[List[int]], B: List[int], modulus: int) -> List[int]:
    """Решение системы линейных уравнений Ax = B (mod modulus)."""
    if not A:
        return []
    
    n = len(A)
    m = len(A[0])
    
    # Расширенная матрица
    augmented = [A[i] + [B[i]] for i in range(n)]
    
    rank = 0
    for col in range(m):
        # Поиск главного элемента
        pivot = -1
        for row in range(rank, n):
            if augmented[row][col] % modulus != 0:
                pivot = row
                break
        
        if pivot == -1:
            continue
        
        # Перестановка
        if pivot != rank:
            augmented[rank], augmented[pivot] = augmented[pivot], augmented[rank]
        
        # Нормализация
        inv_val = modinv(augmented[rank][col], modulus)
        for j in range(col, m + 1):
            augmented[rank][j] = (augmented[rank][j] * inv_val) % modulus
        
        # Исключение из других строк
        for row in range(n):
            if row != rank and augmented[row][col] != 0:
                factor = augmented[row][col]
                for j in range(col, m + 1):
                    augmented[row][j] = (augmented[row][j] - factor * augmented[rank][j]) % modulus
        
        rank += 1
    
    # Проверка совместности
    for row in range(rank, n):
        if augmented[row][m] % modulus != 0:
            raise ValueError("Система несовместна")
    
    # Извлечение решения (базисное решение)
    solution = [0] * m
    for i in range(rank):
        for j in range(m):
            if augmented[i][j] == 1:
                solution[j] = augmented[i][m]
                break
    
    return solution


# ============== ОСНОВНЫЕ ФУНКЦИИ ШИФРА ==============

class HillCipher:
    """Класс для работы с шифром Хилла."""
    
    def __init__(self, alphabet: str, block_len: int, A: Optional[List[List[int]]] = None, t: Optional[List[int]] = None):
        """
        Инициализация шифра.
        
        Args:
            alphabet: строка алфавита
            block_len: длина блока
            A: матрица шифрования (l x l)
            t: вектор сдвига (длины l)
        """
        self.alphabet = alphabet
        self.modulus = len(alphabet)
        self.block_len = block_len
        
        # Предвычисленные таблицы для быстрого преобразования
        self._char_to_num = {ch: i for i, ch in enumerate(alphabet)}
        self._num_to_char = list(alphabet)
        
        if A is not None:
            self.A = A
            self.t = [[ti] for ti in (t if t else [0] * block_len)]
            # Проверяем обратимость перед вычислением обратной матрицы
            try:
                self.A_inv = matrix_inverse_mod(A, self.modulus)
            except ValueError as e:
                raise ValueError(f"Матрица A не подходит для шифрования: {e}")
    
    def text_to_numbers(self, text: str) -> List[int]:
        """Преобразование текста в числа."""
        return [self._char_to_num[ch] for ch in text if ch in self._char_to_num]
    
    def numbers_to_text(self, nums: List[int]) -> str:
        """Преобразование чисел в текст."""
        return ''.join(self._num_to_char[n % self.modulus] for n in nums)
    
    def encrypt(self, plaintext: str) -> str:
        """Шифрование текста."""
        nums = self.text_to_numbers(plaintext)
        
        # Дополнение до кратности block_len (символом 'A' или первым символом)
        pad_len = (self.block_len - len(nums) % self.block_len) % self.block_len
        nums.extend([0] * pad_len)
        
        cipher_nums = []
        for i in range(0, len(nums), self.block_len):
            # Вектор x как столбец
            x = [[nums[i + j]] for j in range(self.block_len)]
            
            # y = A*x + t
            y = matrix_multiply(self.A, x, self.modulus)
            y = [[(y[j][0] + self.t[j][0]) % self.modulus] for j in range(self.block_len)]
            
            cipher_nums.extend(y[j][0] for j in range(self.block_len))
        
        return self.numbers_to_text(cipher_nums)
    
    def decrypt(self, ciphertext: str) -> str:
        """Дешифрование текста."""
        nums = self.text_to_numbers(ciphertext)
        
        plain_nums = []
        for i in range(0, len(nums), self.block_len):
            # Вектор y как столбец
            y = [[nums[i + j]] for j in range(self.block_len)]
            
            # x = A^{-1} * (y - t)
            y_minus_t = [[(y[j][0] - self.t[j][0]) % self.modulus] for j in range(self.block_len)]
            x = matrix_multiply(self.A_inv, y_minus_t, self.modulus)
            
            plain_nums.extend(x[j][0] for j in range(self.block_len))
        
        # Удаляем дополненные символы (первые символы алфавита)
        result = self.numbers_to_text(plain_nums)
        return result.rstrip(self.alphabet[0])
    
    @classmethod
    def recover_key(cls, plain_blocks: List[List[int]], cipher_blocks: List[List[int]], alphabet: str) -> Tuple[List[List[int]], List[int]]:
        """
        Восстановление ключа по известным парам блоков.
        
        Args:
            plain_blocks: список блоков открытого текста
            cipher_blocks: список блоков шифртекста
            alphabet: алфавит
        
        Returns:
            (A, t) - матрица и вектор ключа
        """
        modulus = len(alphabet)
        l = len(plain_blocks[0])
        
        if len(plain_blocks) < l + 1:
            raise ValueError(f"Нужно минимум {l + 1} блоков, получено {len(plain_blocks)}")
        
        # Формирование системы уравнений
        equations = []
        for p_block, c_block in zip(plain_blocks, cipher_blocks):
            for j in range(l):
                # Уравнение: a_j0*x0 + ... + a_j,l-1*x_{l-1} + t_j = c_block[j]
                equations.append((p_block + [1], c_block[j]))
        
        # Сборка матрицы и правой части
        num_vars = l * l + l
        
        # Берем ровно num_vars уравнений для определенности
        equations = equations[:num_vars]
        
        M = [eq[0] + [0] * (num_vars - len(eq[0])) for eq in equations]
        B = [eq[1] for eq in equations]
        
        # Решение системы
        solution = solve_linear_system_mod(M, B, modulus)
        
        # Формирование матрицы A и вектора t
        A = [solution[i * l:(i + 1) * l] for i in range(l)]
        t = solution[l * l:]
        
        return A, t


# ============== ТЕСТЫ ==============

def test_matrix_operations():
    """Тестирование матричных операций."""
    print("Тестирование матричных операций:")
    
    # Тест 1: Обращение матрицы 2x2
    A = [[2, 5], [1, 3]]
    modulus = 26
    
    try:
        A_inv = matrix_inverse_mod(A, modulus)
        print(f"Матрица A: {A}")
        print(f"Обратная A^-1: {A_inv}")
        
        # Проверка: A * A^-1 = I
        product = matrix_multiply(A, A_inv, modulus)
        print(f"A * A^-1: {product}")
        
        # Проверка определителя
        det = matrix_determinant_mod(A, modulus)
        print(f"Определитель: {det}")
        print(f"Обратим ли? {det % modulus != 0 and gcd(det, modulus) == 1}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print()


def main():
    """Демонстрация работы шифра Хилла."""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МАТРИЧНЫХ ОПЕРАЦИЙ")
    print("=" * 60)
    test_matrix_operations()
    
    # Пример 1: русский алфавит
    print("=" * 60)
    print("ПРИМЕР 1: Русский алфавит (n = 33)")
    print("=" * 60)
    
    rus_alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    A_rus = [[1, 2], [0, 4]]
    t_rus = [0, 1]
    
    try:
        cipher_rus = HillCipher(rus_alphabet, 2, A_rus, t_rus)
        plain_rus = "ВОСТОЧНЫЙКАЗАХСТАН"
        
        print(f"Исходный текст: {plain_rus}")
        encrypted = cipher_rus.encrypt(plain_rus)
        print(f"Зашифровано:    {encrypted}")
        decrypted = cipher_rus.decrypt(encrypted)
        print(f"Расшифровано:    {decrypted}")
        print(f"✓ Успешно: {plain_rus == decrypted}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    print()
    
    # Пример 2: английский алфавит
    print("=" * 60)
    print("ПРИМЕР 2: Английский алфавит (n = 26)")
    print("=" * 60)
    
    eng_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    A_eng = [[2, 5], [1, 3]]
    t_eng = [1, 0]
    
    try:
        cipher_eng = HillCipher(eng_alphabet, 2, A_eng, t_eng)
        plain_eng = "CRYPTOGRAPHY"
        
        print(f"Исходный текст: {plain_eng}")
        encrypted = cipher_eng.encrypt(plain_eng)
        print(f"Зашифровано:    {encrypted}")
        decrypted = cipher_eng.decrypt(encrypted)
        print(f"Расшифровано:    {decrypted}")
        print(f"✓ Успешно: {plain_eng == decrypted}")
        
        # Проверка обратимости матрицы
        det = matrix_determinant_mod(A_eng, 26)
        print(f"\nОпределитель матрицы A: {det}")
        print(f"gcd({det}, 26) = {gcd(det, 26)}")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    print()
    
    # Пример 3: криптоанализ
    print("=" * 60)
    print("ПРИМЕР 3: Криптоанализ (восстановление ключа)")
    print("=" * 60)
    
    try:
        cipher_eng = HillCipher(eng_alphabet, 2, A_eng, t_eng)
        plain_eng = "CRYPTOGRAPHY"
        encrypted = cipher_eng.encrypt(plain_eng)
        
        # Берем первые 6 символов (3 блока) для атаки
        p_nums = cipher_eng.text_to_numbers(plain_eng[:6])
        c_nums = cipher_eng.text_to_numbers(encrypted[:6])
        
        p_blocks = [p_nums[i:i + 2] for i in range(0, 6, 2)]
        c_blocks = [c_nums[i:i + 2] for i in range(0, 6, 2)]
        
        print(f"Известные блоки открытого текста: {p_blocks}")
        print(f"Известные блоки шифртекста: {c_blocks}")
        
        A_rec, t_rec = HillCipher.recover_key(p_blocks, c_blocks, eng_alphabet)
        
        print(f"\nОригинальная матрица A: {A_eng}")
        print(f"Восстановленная A:      {A_rec}")
        print(f"Оригинальный вектор t: {t_eng}")
        print(f"Восстановленный t:      {t_rec}")
        
        # Проверка
        cipher_test = HillCipher(eng_alphabet, 2, A_rec, t_rec)
        test_enc = cipher_test.encrypt(plain_eng[:6])
        print(f"\nПроверка шифрования: {test_enc[:6]} == {encrypted[:6]}")
        print(f"✓ Ключ восстановлен успешно")
        
    except Exception as e:
        print(f"✗ Ошибка при восстановлении: {e}")


if __name__ == "__main__":
    main()