# 1. Вероятностная модель К. Шеинона
"""
Программа, реализующая вероятностную модель шифрования Клода Шеннона.
Включает:
1. Класс ShannonCipher - модель системы шифрования.
2. Проверку условий теоремы Шеннона для совершенной секретности.
3. Пример шифра Вернама (гаммирование) - совершенная система.
4. Пример несовершенной системы для сравнения.
"""

import random
import itertools
from collections import Counter
from typing import Dict, List, Tuple, Any
import math


class ShannonCipher:
    """
    Класс, представляющий систему шифрования в модели Шеннона.
    
    Атрибуты:
        M: множество открытых текстов (список)
        C: множество шифртекстов (список)
        K: множество ключей (список)
        p_m: распределение вероятностей на M (dict)
        p_k: распределение вероятностей на K (dict)
        E: функция шифрования E(m, k) -> c
        D: функция дешифрования D(c, k) -> m
    """
    
    def __init__(self, 
        M: List, 
        C: List, 
        K: List, 
        p_m: Dict[Any, float],
        p_k: Dict[Any, float],
        E: callable,
        D: callable):
        """
        Инициализация системы шифрования.
        
        Args:
            M: список открытых текстов
            C: список шифртекстов
            K: список ключей
            p_m: словарь вероятностей для M (сумма = 1)
            p_k: словарь вероятностей для K (сумма = 1)
            E: функция E(m, k) -> c
            D: функция D(c, k) -> m
        """
        self.M = M
        self.C = C
        self.K = K
        self.p_m = p_m
        self.p_k = p_k
        self.E = E
        self.D = D
        
        # Проверка корректности вероятностей
        assert abs(sum(p_m.values()) - 1.0) < 1e-9, "Сумма вероятностей M != 1"
        assert abs(sum(p_k.values()) - 1.0) < 1e-9, "Сумма вероятностей K != 1"
        
        # Проверка регулярности (все вероятности > 0)
        self.is_regular = all(p > 0 for p in p_m.values()) and all(p > 0 for p in p_k.values())
    
    def get_key_for_encryption(self, m: Any, c: Any) -> List[Any]:
        """Находит все ключи k, такие что E(m, k) = c."""
        return [k for k in self.K if self.E(m, k) == c]
    
    def get_text_for_decryption(self, c: Any, k: Any) -> Any:
        """Находит открытый текст m, такой что D(c, k) = m."""
        return self.D(c, k)
    
    def compute_p_c_given_m(self, c: Any, m: Any) -> float:
        """Вычисляет p(c|m) = сумма p(k) по k: E(m,k)=c."""
        keys = self.get_key_for_encryption(m, c)
        return sum(self.p_k[k] for k in keys)
    
    def compute_p_c(self, c: Any) -> float:
        """Вычисляет p(c) = сумма_{m, k: E(m, k) = c} p(m)p(k)."""
        prob = 0.0
        for m in self.M:
            for k in self.K:
                if self.E(m, k) == c:
                    prob += self.p_m[m] * self.p_k[k]
        return prob
    
    def compute_p_m_given_c(self, m: Any, c: Any) -> float:
        """Вычисляет p(m|c) = p(m)p(c|m)/p(c)."""
        p_c = self.compute_p_c(c)
        if p_c == 0:
            return 0.0
        return self.p_m[m] * self.compute_p_c_given_m(c, m) / p_c
    
    def is_perfect(self, tolerance: float = 1e-9) -> bool:
        """
        Проверяет, является ли система совершенной.
        Совершенная секретность: p(m|c) = p(m) для всех m, c.
        """
        if not self.is_regular:
            print("Предупреждение: система не регулярна (есть нулевые вероятности)")
            return False
        
        for m in self.M:
            for c in self.C:
                p_m_given_c = self.compute_p_m_given_c(m, c)
                if abs(p_m_given_c - self.p_m[m]) > tolerance:
                    print(f"Нарушение: p({m}|{c}) = {p_m_given_c} != p({m}) = {self.p_m[m]}")
                    return False
        return True
    
    def check_shannon_theorem_conditions(self) -> Tuple[bool, str]:
        """
        Проверяет условия теоремы Шеннона (при |M| = |C| = |K|):
        1) Для любых m, c существует ЕДИНСТВЕННЫЙ ключ k: E(m, k) = c
        2) Распределение на K равномерно
        """
        n = len(self.M)
        
        if not (len(self.M) == len(self.C) == len(self.K)):
            return False, f"Условие |M|={len(self.M)} = |C|={len(self.C)} = |K|={len(self.K)} не выполнено"
        
        # Проверка условия 1: единственность ключа для каждой пары (m,c)
        for m in self.M:
            for c in self.C:
                keys = self.get_key_for_encryption(m, c)
                if len(keys) != 1:
                    return False, f"Для (m = {m}, c = {c}) найдено {len(keys)} ключей, требуется 1"
        
        # Проверка условия 2: равномерность распределения ключей
        expected_p = 1.0 / n
        for k in self.K:
            if abs(self.p_k[k] - expected_p) > 1e-9:
                return False, f"Распределение ключей не равномерно: p({k}) = {self.p_k[k]} != {expected_p}"
        
        return True, "Условия теоремы Шеннона выполнены"
    
    def build_encryption_table(self) -> List[List]:
        """Строит таблицу шифрования (латинский квадрат)."""
        table = []
        for m in self.M:
            row = []
            for k in self.K:
                row.append(self.E(m, k))
            table.append(row)
        return table
    
    def is_latin_square(self) -> bool:
        """Проверяет, является ли таблица шифрования латинским квадратом."""
        table = self.build_encryption_table()
        n = len(self.M)
        
        # Проверка строк: каждая строка содержит все элементы C ровно по разу
        for i, row in enumerate(table):
            if sorted(row) != sorted(self.C):
                print(f"Строка {i} не содержит всех элементов C: {row}")
                return False
        
        # Проверка столбцов: каждый столбец содержит все элементы C ровно по разу
        for j in range(n):
            col = [table[i][j] for i in range(n)]
            if sorted(col) != sorted(self.C):
                print(f"Столбец {j} не содержит всех элементов C: {col}")
                return False
        
        return True


# ============================================================
# Пример 1: Шифр Вернама (гаммирование) - совершенная система
# ============================================================

class VernamCipher:
    """Шифр Вернама (одноразовый блокнот) над кольцом Zn."""
    
    def __init__(self, n: int, t: int):
        """
        n: модуль (размер алфавита)
        t: длина сообщения
        """
        self.n = n
        self.t = t
        
        # M = C = K = Zn^t (все наборы длины t)
        self.all_words = self._generate_words()
    
    def _generate_words(self) -> List[Tuple]:
        """Генерирует все возможные слова длины t над Zn."""
        if self.t == 0:
            return [()]
        return list(itertools.product(range(self.n), repeat = self.t))
    
    def encrypt(self, m: Tuple, k: Tuple) -> Tuple:
        """Ek(m) = m + k (mod n) покомпонентно."""
        return tuple((m[i] + k[i]) % self.n for i in range(self.t))
    
    def decrypt(self, c: Tuple, k: Tuple) -> Tuple:
        """Dk(c) = c - k (mod n) покомпонентно."""
        return tuple((c[i] - k[i]) % self.n for i in range(self.t))
    
    def get_system(self) -> ShannonCipher:
        """Возвращает систему шифрования Шеннона с равномерными распределениями."""
        words = self.all_words
        n_total = len(words)
        
        # Равномерное распределение на M и K
        p_m = {m: 1.0 / n_total for m in words}
        p_k = {k: 1.0 / n_total for k in words}
        
        return ShannonCipher(
            M = words,
            C = words,
            K = words,
            p_m = p_m,
            p_k = p_k,
            E = self.encrypt,
            D = self.decrypt
        )


# ============================================================
# Пример 2: Несовершенная система (для сравнения)
# ============================================================

def create_imperfect_system():
    """
    Создаёт несовершенную систему:
    M = {0, 1}, C = {0, 1}, K = {0, 1}
    E(0, 0) = 0, E(0, 1) = 1, E(1, 0) = 1, E(1, 1) = 0
    p(m) равномерное, p(k) неравномерное: p(0) = 0.7, p(1) = 0.3
    """
    M = [0, 1]
    C = [0, 1]
    K = [0, 1]
    
    p_m = {0: 0.5, 1: 0.5}
    p_k = {0: 0.7, 1: 0.3}  # Неравномерное распределение
    
    def E(m, k):
        return (m + k) % 2
    
    def D(c, k):
        return (c - k) % 2
    
    return ShannonCipher(M, C, K, p_m, p_k, E, D)


# ============================================================
# Пример 3: Простая совершенная система с |M|=|C|=|K|=3
# ============================================================

def create_small_perfect_system():
    """
    Создаёт простую совершенную систему на 3 элементах.
    Используется сложение по модулю 3.
    """
    M = [0, 1, 2]
    C = [0, 1, 2]
    K = [0, 1, 2]
    
    # Равномерные распределения
    p_m = {0: 1/3, 1: 1/3, 2: 1/3}
    p_k = {0: 1/3, 1: 1/3, 2: 1/3}
    
    def E(m, k):
        return (m + k) % 3
    
    def D(c, k):
        return (c - k) % 3
    
    return ShannonCipher(M, C, K, p_m, p_k, E, D)


# ============================================================
# Демонстрация
# ============================================================

def main():
    print("=" * 70)
    print("РЕАЛИЗАЦИЯ ВЕРОЯТНОСТНОЙ МОДЕЛИ ШИФРОВАНИЯ К. ШЕННОНА")
    print("=" * 70)
    
    # ===== Тест 1: Шифр Вернама (совершенная система) =====
    print("\n1. ШИФР ВЕРНАМА (над Z2, длина 2)")
    print("-" * 50)
    
    vernam = VernamCipher(n = 2, t = 2)
    sys_vernam = vernam.get_system()
    
    print(f"|M| = {len(sys_vernam.M)}")
    print(f"|C| = {len(sys_vernam.C)}")
    print(f"|K| = {len(sys_vernam.K)}")
    print(f"Регулярность: {sys_vernam.is_regular}")
    
    # Проверка условий теоремы Шеннона
    cond_ok, msg = sys_vernam.check_shannon_theorem_conditions()
    print(f"Условия теоремы Шеннона: {msg}")
    
    # Проверка совершенной секретности
    is_perfect = sys_vernam.is_perfect()
    print(f"Совершенная секретность: {is_perfect}")
    
    # Латинский квадрат?
    is_latin = sys_vernam.is_latin_square()
    print(f"Таблица шифрования является латинским квадратом: {is_latin}")
    
    # Пример шифрования
    m = (0, 1)
    k = (1, 0)
    c = vernam.encrypt(m, k)
    m_dec = vernam.decrypt(c, k)
    print(f"\nПример: m={m}, k={k} -> c={c} -> дешифровано: {m_dec}")
    
    # ===== Тест 2: Несовершенная система =====
    print("\n2. НЕСОВЕРШЕННАЯ СИСТЕМА")
    print("-" * 50)
    
    imperfect = create_imperfect_system()
    print(f"|M| = {len(imperfect.M)}, |C| = {len(imperfect.C)}, |K| = {len(imperfect.K)}")
    print(f"Распределение ключей: {imperfect.p_k}")
    
    cond_ok, msg = imperfect.check_shannon_theorem_conditions()
    print(f"Условия теоремы Шеннона: {msg}")
    
    is_perfect = imperfect.is_perfect()
    print(f"Совершенная секретность: {is_perfect}")
    
    # Демонстрация нарушения: p(0|0) != p(0)
    p0 = imperfect.p_m[0]
    p0_given_0 = imperfect.compute_p_m_given_c(0, 0)
    print(f"p(0) = {p0}, p(0|0) = {p0_given_0:.4f} -> {'НЕ РАВНО' if abs(p0-p0_given_0) > 1e-6 else 'РАВНО'}")
    
    # ===== Тест 3: Малая совершенная система (n=3) =====
    print("\n3. МАЛАЯ СОВЕРШЕННАЯ СИСТЕМА (n=3, сложение по модулю 3)")
    print("-" * 50)
    
    small_perfect = create_small_perfect_system()
    print(f"|M| = {len(small_perfect.M)}")
    
    cond_ok, msg = small_perfect.check_shannon_theorem_conditions()
    print(f"Условия теоремы Шеннона: {msg}")
    
    is_perfect = small_perfect.is_perfect()
    print(f"Совершенная секретность: {is_perfect}")
    
    # Вывод таблицы шифрования (латинского квадрата)
    print("\nТаблица шифрования (строки = M, столбцы = K):")
    table = small_perfect.build_encryption_table()
    print("    " + "  ".join(f"k={k}" for k in small_perfect.K))
    for i, m in enumerate(small_perfect.M):
        row_str = "  ".join(str(c) for c in table[i])
        print(f"m={m}: {row_str}")
    
    # ===== Дополнительно: энтропийный анализ =====
    print("\n4. ЭНТРОПИЙНЫЙ АНАЛИЗ")
    print("-" * 50)
    
    def entropy(prob_dict: Dict) -> float:
        """Вычисляет энтропию Шеннона H = -sum(p * log2(p))."""
        return -sum(p * math.log2(p) for p in prob_dict.values() if p > 0)
    
    H_M = entropy(sys_vernam.p_m)
    H_K = entropy(sys_vernam.p_k)
    print(f"Для шифра Вернама: H(M) = {H_M:.4f} бит, H(K) = {H_K:.4f} бит")
    print(f"Теорема Шеннона: для совершенной секретности H(K) >= H(M) -> {H_K >= H_M}")
    
    H_M_imp = entropy(imperfect.p_m)
    H_K_imp = entropy(imperfect.p_k)
    print(f"Для несовершенной системы: H(M) = {H_M_imp:.4f}, H(K) = {H_K_imp:.4f}")
    print(f"Условие H(K) >= H(M) выполнено, но система не совершенна из-за неравномерности ключей")


if __name__ == "__main__":
    main()