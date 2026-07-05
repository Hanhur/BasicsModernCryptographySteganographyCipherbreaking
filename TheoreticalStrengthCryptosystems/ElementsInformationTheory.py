# Элементы теории информации
import math
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Union
import itertools

class InformationTheory:
    """
    Класс для вычисления основных понятий теории информации,
    описанных в разделе 7.4: энтропия Шеннона, условная энтропия,
    совместная энтропия, избыточность и т.д.
    (Реализация без NumPy для совместимости)
    """
    
    def __init__(self, base: int = 2):
        """
        Инициализация с выбором основания логарифма.
        
        Args:
            base: основание логарифма (2 - биты, e - наты, 10 - диты)
        """
        self.base = base
    
    def log(self, x: float) -> float:
        """Логарифм с заданным основанием."""
        if x <= 0:
            return 0
        if self.base == math.e:
            return math.log(x)
        elif self.base == 2:
            return math.log2(x)
        elif self.base == 10:
            return math.log10(x)
        else:
            return math.log(x) / math.log(self.base)
    
    def entropy(self, probabilities: List[float]) -> float:
        """
        Вычисление энтропии Шеннона для дискретной случайной величины.
        
        Формула (7.5): H(ξ) = -∑ Pi * log(Pi)
        
        Args:
            probabilities: список вероятностей P1, P2, ..., Pr
            
        Returns:
            энтропия в выбранных единицах
        """
        # Проверка, что вероятности образуют распределение
        if abs(sum(probabilities) - 1.0) > 1e-10:
            raise ValueError("Сумма вероятностей должна быть равна 1")
        
        H = 0.0
        for p in probabilities:
            if p > 0:  # 0 * log(0) = 0
                H -= p * self.log(p)
        return H
    
    def entropy_from_data(self, data: List) -> float:
        """
        Вычисление энтропии по эмпирическим данным.
        
        Args:
            data: список наблюдений случайной величины
            
        Returns:
            энтропия в выбранных единицах
        """
        counts = Counter(data)
        n = len(data)
        probabilities = [count / n for count in counts.values()]
        return self.entropy(probabilities)
    
    def binary_entropy(self, p: float) -> float:
        """
        Энтропия для бинарной случайной величины.
        
        Формула (7.6): H = -(p * log(p) + (1 - p) * log(1 - p))
        
        Args:
            p: вероятность первого исхода
            
        Returns:
            энтропия в битах (при base = 2)
        """
        if p < 0 or p > 1:
            raise ValueError("Вероятность должна быть в диапазоне [0, 1]")
        
        H = 0.0
        if p > 0:
            H -= p * self.log(p)
        if 1 - p > 0:
            H -= (1 - p) * self.log(1 - p)
        return H
    
    def joint_entropy(self, joint_probs: List[List[float]]) -> float:
        """
        Вычисление совместной энтропии для двумерной случайной величины.
        
        Формула (7.11): H(ξ1, ξ2) = -∑∑ Pij * log(Pij)
        
        Args:
            joint_probs: матрица совместных вероятностей Pij (список списков)
            
        Returns:
            совместная энтропия
        """
        H = 0.0
        for row in joint_probs:
            for p in row:
                if p > 0:
                    H -= p * self.log(p)
        return H
    
    def conditional_entropy(self, joint_probs: List[List[float]]) -> float:
        """
        Вычисление условной энтропии H(ξ2|ξ1).
        
        Формула (7.13): H(ξ2|ξ1) = -∑ Pi· ∑ (Pij / Pi·) * log(Pij / Pi·)
        
        Args:
            joint_probs: матрица совместных вероятностей Pij
            
        Returns:
            условная энтропия
        """
        r = len(joint_probs)
        s = len(joint_probs[0]) if r > 0 else 0
        H = 0.0
        
        for i in range(r):
            # Маргинальная вероятность Pi·
            Pi = sum(joint_probs[i])
            if Pi == 0:
                continue
            
            for j in range(s):
                p_ij = joint_probs[i][j]
                if p_ij > 0:
                    # Условная вероятность P(j|i) = Pij / Pi·
                    cond_prob = p_ij / Pi
                    H -= Pi * cond_prob * self.log(cond_prob)
        
        return H
    
    def get_marginal_distributions(self, joint_probs: List[List[float]]) -> Tuple[List[float], List[float]]:
        """
        Вычисление маргинальных распределений из совместного.
        
        Args:
            joint_probs: матрица совместных вероятностей
            
        Returns:
            (P(ξ1), P(ξ2)) - маргинальные распределения
        """
        r = len(joint_probs)
        s = len(joint_probs[0]) if r > 0 else 0
        
        P_xi1 = [sum(row) for row in joint_probs]
        P_xi2 = [sum(joint_probs[i][j] for i in range(r)) for j in range(s)]
        
        return P_xi1, P_xi2
    
    def joint_entropy_nd(self, probabilities: List) -> float:
        """
        Энтропия для n-мерной случайной величины.
        
        Формула (7.12): H(ξ1, ..., ξn) = -∑ Pijk... * log(Pijk...)
        
        Args:
            probabilities: список или вложенный список вероятностей
            
        Returns:
            энтропия n-мерной величины
        """
        H = 0.0
        
        def process_element(element):
            """Рекурсивная обработка вложенных списков."""
            if isinstance(element, (list, tuple)):
                for item in element:
                    process_element(item)
            else:
                if element > 0:
                    H_local = element * self.log(element)
                    # Используем nonlocal для изменения H во внешней функции
                    return element * self.log(element)
            return 0
        
        def flatten_and_process(lst):
            """Преобразование вложенного списка в плоский и вычисление энтропии."""
            result = []
            for item in lst:
                if isinstance(item, (list, tuple)):
                    result.extend(flatten_and_process(item))
                else:
                    result.append(item)
            return result
        
        flat_probs = flatten_and_process(probabilities)
        H = 0.0
        for p in flat_probs:
            if p > 0:
                H -= p * self.log(p)
        return H
    
    def specific_entropy(self, joint_probs: List, n: int) -> float:
        """
        Удельная энтропия n-го порядка: h_n ^ + = (1 / n) * H(ξ1, ..., ξn)
        
        Args:
            joint_probs: массив вероятностей для n-мерной случайной величины
            n: размерность (длина последовательности)
            
        Returns:
            удельная энтропия n-го порядка
        """
        H_n = self.joint_entropy_nd(joint_probs)
        return H_n / n if n > 0 else 0
    
    def redundancy(self, alphabet_size: int, h_inf: float) -> float:
        """
        Вычисление избыточности.
        
        Формула (7.23): R = log(r) - h∞
        
        Args:
            alphabet_size: размер алфавита r
            h_inf: предельная энтропия h∞
            
        Returns:
            избыточность на символ
        """
        max_entropy = self.log(alphabet_size)
        return max_entropy - h_inf
    
    def estimate_h_inf(self, data_sequence: List, max_order: int = 5) -> float:
        """
        Оценка предельной энтропии h∞ для стационарного процесса.
        
        Используется аппроксимация: h∞ ≈ h_n^- для достаточно больших n.
        
        Args:
            data_sequence: последовательность символов
            max_order: максимальный порядок для оценки
            
        Returns:
            оценка предельной энтропии
        """
        n = len(data_sequence)
        if n < max_order + 1:
            raise ValueError("Недостаточно данных для оценки")
        
        # Вычисляем h_n^- для разных n
        h_minus = []
        for order in range(1, max_order + 1):
            # Строим (order)-граммы
            prev_grams = [tuple(data_sequence[i:i + order - 1]) for i in range(n - order + 1)]
            full_grams = [tuple(data_sequence[i:i + order]) for i in range(n - order + 1)]
            
            # Считаем вероятности
            prev_counts = Counter(prev_grams)
            full_counts = Counter(full_grams)
            
            # Вычисляем H(ξ1,...,ξ_{order-1})
            total_prev = len(prev_grams)
            probs_prev = [count / total_prev for count in prev_counts.values()]
            H_prev = self.entropy(probs_prev)
            
            # Вычисляем H(ξ1,...,ξ_order)
            total_full = len(full_grams)
            probs_full = [count / total_full for count in full_counts.values()]
            H_full = self.entropy(probs_full)
            
            # h_n^- = H(ξ_order|ξ1,...,ξ_{order-1}) = H_full - H_prev
            h = H_full - H_prev
            h_minus.append(h)
        
        # Берем последнее значение как оценку h∞ (если процесс стационарный)
        # В реальности нужно проверять сходимость
        return h_minus[-1] if h_minus else 0.0
    
    def estimate_h_inf_by_blocks(self, data_sequence: List, block_size: int = 100) -> float:
        """
        Альтернативная оценка h∞ через энтропию блоков.
        
        Args:
            data_sequence: последовательность символов
            block_size: размер блока для оценки
            
        Returns:
            оценка предельной энтропии
        """
        n = len(data_sequence)
        if n < block_size:
            raise ValueError("Недостаточно данных")
        
        # Разбиваем на блоки
        blocks = []
        for i in range(0, n - block_size + 1, block_size):
            block = tuple(data_sequence[i:i + block_size])
            blocks.append(block)
        
        # Вычисляем энтропию блоков
        block_counts = Counter(blocks)
        total_blocks = len(blocks)
        probs = [count / total_blocks for count in block_counts.values()]
        H_blocks = self.entropy(probs)
        
        # Удельная энтропия
        return H_blocks / block_size


def demonstrate_examples():
    """Демонстрация примеров из текста."""
    it = InformationTheory(base = 2)
    
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПОНЯТИЙ ТЕОРИИ ИНФОРМАЦИИ")
    print("=" * 60)
    
    # Пример 1: Энтропия для бинарных источников (из текста)
    print("\n1. БИНАРНАЯ ЭНТРОПИЯ (пример из текста):")
    print("-" * 40)
    
    # ξ1: P(a1)=1, P(a2)=0
    H1 = it.binary_entropy(1.0)
    print(f"ξ1: P(a1) = 1, P(a2) = 0 → H(ξ1) = {H1:.4f} бит")
    
    # ξ2: P(a1)=0.5, P(a2)=0.5
    H2 = it.binary_entropy(0.5)
    print(f"ξ2: P(a1) = 0.5, P(a2) = 0.5 → H(ξ2) = {H2:.4f} бит")
    
    # ξ3: P(a1)=0.01, P(a2)=0.99
    H3 = it.binary_entropy(0.01)
    print(f"ξ3: P(a1) = 0.01, P(a2) = 0.99 → H(ξ3) = {H3:.4f} бит")
    
    # Пример 2: Совместная и условная энтропия (таблица 7.1)
    print("\n2. СОВМЕСТНАЯ И УСЛОВНАЯ ЭНТРОПИЯ (таблица 7.1):")
    print("-" * 40)
    
    # Матрица из таблицы 7.1
    joint_probs = [
        [0.20, 0.05, 0.00],
        [0.05, 0.30, 0.05],
        [0.00, 0.05, 0.30]
    ]
    
    print("Матрица совместных вероятностей P(ξ1, ξ2):")
    for row in joint_probs:
        print(f"  {row}")
    
    # Маргинальные распределения
    P_xi1, P_xi2 = it.get_marginal_distributions(joint_probs)
    print(f"\nМаргинальные P(ξ1): {[f'{p:.2f}' for p in P_xi1]}")
    print(f"Маргинальные P(ξ2): {[f'{p:.2f}' for p in P_xi2]}")
    
    # Энтропии
    H_xi1 = it.entropy(P_xi1)
    H_xi2 = it.entropy(P_xi2)
    H_joint = it.joint_entropy(joint_probs)
    H_cond = it.conditional_entropy(joint_probs)
    
    print(f"\nH(ξ1) = {H_xi1:.4f} бит")
    print(f"H(ξ2) = {H_xi2:.4f} бит")
    print(f"H(ξ1, ξ2) = {H_joint:.4f} бит")
    print(f"H(ξ2|ξ1) = {H_cond:.4f} бит")
    
    # Проверка свойства (7.14): H(ξ1,ξ2) = H(ξ1) + H(ξ2|ξ1)
    print(f"\nПроверка свойства (7.14):")
    print(f"H(ξ1) + H(ξ2|ξ1) = {H_xi1 + H_cond:.4f} бит")
    print(f"H(ξ1, ξ2) = {H_joint:.4f} бит")
    print(f"Равенство выполняется: {abs(H_xi1 + H_cond - H_joint) < 1e-10}")
    
    # Пример 3: Удельная энтропия и избыточность
    print("\n3. УДЕЛЬНАЯ ЭНТРОПИЯ И ИЗБЫТОЧНОСТЬ:")
    print("-"*40)
    
    # Генерируем данные для процесса без памяти (равномерное распределение)
    import random
    random.seed(42)
    alphabet = list('ABCDEFGHIJ')  # r = 10 символов
    data_equiprobable = random.choices(alphabet, k = 1000)
    
    # Генерируем данные с избыточностью (неравномерное распределение)
    probs = [0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05, 0.03, 0.02, 0.01]
    data_biased = random.choices(alphabet, weights = probs, k = 1000)
    
    # Оценка h∞ для обоих случаев
    print("Оценка предельной энтропии h∞:")
    
    h_inf_equiprobable = it.estimate_h_inf(data_equiprobable, max_order = 5)
    h_inf_biased = it.estimate_h_inf(data_biased, max_order = 5)
    
    print(f"Равновероятные символы: h∞ ≈ {h_inf_equiprobable:.4f} бит")
    print(f"Неравновероятные символы: h∞ ≈ {h_inf_biased:.4f} бит")
    
    # Избыточность
    r = len(alphabet)
    R_equiprobable = it.redundancy(r, h_inf_equiprobable)
    R_biased = it.redundancy(r, h_inf_biased)
    
    print(f"\nИзбыточность (R = log({r}) - h∞):")
    print(f"Равновероятные: R = {R_equiprobable:.4f} бит")
    print(f"Неравновероятные: R = {R_biased:.4f} бит")
    print(f"Максимальная энтропия: log2({r}) = {it.log(r):.4f} бит")
    
    # Пример 4: Проверка свойств энтропии из утверждения 7.3
    print("\n4. ПРОВЕРКА СВОЙСТВ ЭНТРОПИИ (утверждение 7.3):")
    print("-" * 40)
    
    for r in [2, 3, 5]:
        # Равномерное распределение
        probs_uniform = [1.0 / r] * r
        H_uniform = it.entropy(probs_uniform)
        log_r = it.log(r)
        print(f"r = {r}, равномерное: H = {H_uniform:.4f}, log(r) = {log_r:.4f}")
        print(f"  H ≤ log(r): {H_uniform <= log_r + 1e-10}")
    
    # Пример 5: Для независимых случайных величин
    print("\n5. СВОЙСТВО ДЛЯ НЕЗАВИСИМЫХ ВЕЛИЧИН (7.15):")
    print("-" * 40)
    
    # Создаем две независимые случайные величины
    probs1 = [0.7, 0.3]
    probs2 = [0.4, 0.6]
    
    # Совместное распределение для независимых величин
    joint_independent = [
        [probs1[0] * probs2[0], probs1[0] * probs2[1]],
        [probs1[1] * probs2[0], probs1[1] * probs2[1]]
    ]
    
    H1 = it.entropy(probs1)
    H2 = it.entropy(probs2)
    H_joint_ind = it.joint_entropy(joint_independent)
    H_cond_ind = it.conditional_entropy(joint_independent)
    
    print(f"H(ξ1) = {H1:.4f}, H(ξ2) = {H2:.4f}")
    print(f"H(ξ1, ξ2) = {H_joint_ind:.4f}")
    print(f"H(ξ2|ξ1) = {H_cond_ind:.4f}")
    print(f"H(ξ1) + H(ξ2) = {H1 + H2:.4f}")
    print(f"H(ξ2|ξ1) = H(ξ2): {abs(H_cond_ind - H2) < 1e-10}")
    print(f"H(ξ1, ξ2) = H(ξ1) + H(ξ2): {abs(H_joint_ind - (H1 + H2)) < 1e-10}")
    
    # Дополнительно: энтропия текста
    print("\n6. ЭНТРОПИЯ РЕАЛЬНОГО ТЕКСТА (демонстрация):")
    print("-" * 40)
    
    # Пример текста на русском
    text = "энтропия шеннона это количественная мера неопределенности случайной величины"
    chars = list(text.lower().replace(" ", ""))
    
    H_text = it.entropy_from_data(chars)
    print(f"Текст: '{text}'")
    print(f"Количество символов: {len(chars)}")
    print(f"Уникальных символов: {len(set(chars))}")
    print(f"Энтропия текста: {H_text:.4f} бит на символ")
    
    # Оценка h∞ для текста
    try:
        h_inf_text = it.estimate_h_inf(chars, max_order = 3)
        print(f"Оценка h∞ для текста: {h_inf_text:.4f} бит")
        r_text = len(set(chars))
        R_text = it.redundancy(r_text, h_inf_text)
        print(f"Избыточность текста: {R_text:.4f} бит")
    except:
        print("Недостаточно данных для оценки h∞")


if __name__ == "__main__":
    demonstrate_examples()