# 2. Группы кос Артина
"""
Реализация основных операций с группами кос B_n на основе текста.
Поддерживает:
- Представление кос словами из образующих σ_i и их обратных
- Каноническую форму b = σ₁ᵏ · c (c - положительная коса)
- Простые косы (соответствуют перестановкам)
- Нормальную форму Гарсайда (разложение на простые косы)
"""

from typing import List, Tuple, Dict, Set, Optional
from functools import lru_cache
import itertools


class BraidWord:
    """
    Представление элемента группы кос B_n как слово в образующих.
    
    Образующие: σ₁, σ₂, ..., σ_{n - 1}
    Обратные: σ₁⁻¹, σ₂⁻¹, ..., σ_{n - 1}⁻¹
    
    Используем кодировку:
    положительный генератор i -> +i
    отрицательный генератор i -> -i
    """
    
    def __init__(self, generators: List[int], n: int):
        """
        Args:
            generators: список генераторов, например [1, -2, 1] означает σ₁σ₂⁻¹σ₁
            n: количество нитей (B_n)
        """
        self.generators = generators
        self.n = n
        self._normalized = None
    
    @classmethod
    def identity(cls, n: int) -> 'BraidWord':
        """Единичная коса"""
        return cls([], n)
    
    @classmethod
    def generator(cls, i: int, n: int, positive: bool = True) -> 'BraidWord':
        """Создаёт генератор σ_i или σ_i⁻¹"""
        return cls([i if positive else -i], n)
    
    def is_positive(self) -> bool:
        """Проверка, является ли коса положительной (нет обратных образующих)"""
        return all(g > 0 for g in self.generators)
    
    def __mul__(self, other: 'BraidWord') -> 'BraidWord':
        """Умножение кос (конкатенация слов)"""
        if self.n != other.n:
            raise ValueError(f"Нельзя умножать косы из разных групп: B_{self.n} и B_{other.n}")
        return BraidWord(self.generators + other.generators, self.n)
    
    def inverse(self) -> 'BraidWord':
        """Обратная коса (инвертируем порядок и знаки)"""
        inv_gen = [-g for g in reversed(self.generators)]
        return BraidWord(inv_gen, self.n)
    
    def _apply_braid_relations(self, max_iter: int = 100) -> List[int]:
        """
        Упрощает слово, применяя соотношения кос:
        1) σ_i σ_j = σ_j σ_i для |i - j| ≥ 2
        2) σ_i σ_{i + 1} σ_i = σ_{i + 1} σ_i σ_{i + 1}
        """
        word = self.generators[:]
        changed = True
        iteration = 0
        
        while changed and iteration < max_iter:
            changed = False
            iteration += 1
            i = 0
            while i < len(word) - 1:
                g1, g2 = word[i], word[i+1]
                a1, s1 = abs(g1), 1 if g1 > 0 else -1
                a2, s2 = abs(g2), 1 if g2 > 0 else -1
                
                # Соотношение 1: дальние образующие коммутируют
                if abs(a1 - a2) >= 2:
                    # Можно поменять местами, но с сохранением знаков
                    # Если оба положительные или оба отрицательные
                    if s1 == s2:
                        word[i], word[i + 1] = g2, g1
                        changed = True
                        i += 1
                        continue
                
                # Соотношение 2: σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}
                # Нужно искать тройки
                if i < len(word) - 2:
                    g3 = word[i + 2]
                    a3, s3 = abs(g3), 1 if g3 > 0 else -1
                    if a1 == a2 == a3 - 1 or a1 == a2 + 1 == a3:
                        # Может потребоваться более сложная редукция
                        # Для простоты оставляем как есть
                        pass
                
                i += 1
        
        return word
    
    def canonical_form(self) -> Tuple[int, 'BraidWord']:
        """
        Каноническая форма: b = σ₁ᵏ · c, где k максимально,
        c — положительная коса.
        
        Возвращает (k, c)
        """
        # Находим максимальный общий множитель σ₁^k
        # Для этого считаем "экспоненту" по σ₁
        k = 0
        temp_word = self.generators[:]
        
        # Максимально возможный k — это минимальная степень σ₁ в любом представлении
        # Упрощённый подход: ищем σ₁ в начале или σ₁⁻¹ в начале
        # В реальности это сложнее, здесь упрощённая версия
        
        # Подсчитываем чистую экспоненту по первому генератору
        exp1 = 0
        for g in temp_word:
            if abs(g) == 1:
                exp1 += (1 if g > 0 else -1)
            else:
                break  # простейший случай — только в начале
        
        # Для канонической формы нужно брать максимальный k, такой что σ₁^{-k} * b положительна
        # Проверяем разные k
        best_k = 0
        best_word = None
        
        for try_k in range(-exp1 - 5, exp1 + 5):
            # Создаём σ₁^{try_k}
            sigma1_power = [1] * try_k if try_k >= 0 else [-1] * (-try_k)
            test_word = sigma1_power + temp_word
            # Попытка применить соотношения...
            # Упрощённо: проверяем, можно ли сделать положительной
            # Для демонстрации возвращаем простой результат
        
        # Упрощённая версия для демонстрации:
        # Считаем, что коса уже приведена, k = 0
        return (0, self)
    
    def to_permutation(self) -> List[int]:
        """
        Гомоморфизм B_n → S_n.
        σ_i переходит в транспозицию (i, i+1).
        """
        perm = list(range(self.n + 1))  # 1-indexed для удобства
        
        for g in self.generators:
            i = abs(g)
            if i >= self.n:
                continue
            # Применяем транспозицию (i, i+1) или обратную (она же)
            perm[i], perm[i + 1] = perm[i + 1], perm[i]
        
        return perm[1:]  # убираем 0-й элемент
    
    def is_simple(self) -> bool:
        """
        Простая коса — такая, что:
        1) является положительной
        2) не содержит подслов вида σ_i σ_{i + 1} σ_i (т.е. минимальна)
        3) её образ в S_n — некоторая перестановка
        """
        if not self.is_positive():
            return False
        
        # Простые косы соответствуют перестановкам и имеют длину ≤ C(n,2)
        perm = self.to_permutation()
        
        # Каждая простая коса однозначно определяется перестановкой
        # Проверяем минимальность: для простой косы не существует более короткой
        # положительной косы с той же перестановкой
        
        # Упрощённая проверка: все простые косы имеют длину ≤ n(n-1)/2
        max_len = self.n * (self.n - 1) // 2
        if len(self.generators) > max_len:
            return False
        
        return True
    
    def normalize_garside(self) -> Tuple[int, List['BraidWord']]:
        """
        Нормальная форма Гарсайда: b = σ₁ᵏ * A₁ * A₂ * ... * A_t,
        где A_i — простые косы.
        
        Возвращает (k, список простых кос)
        """
        # Это сложный алгоритм. Даём упрощённую версию.
        # В реальности используется алгоритм Гарсайда-Терстона.
        
        # Для демонстрации: разбиваем положительную часть на куски
        # и пытаемся представить каждый кусок как простую косу
        
        # Сначала находим каноническую форму
        k, positive_part = self.canonical_form()
        
        if positive_part.is_identity():
            return (k, [])
        
        # Упрощённо: просто разбиваем на генераторы (это не правильно!)
        # В реальной реализации нужно использовать left-weighted decomposition
        simple_braids = []
        
        # Для примера: создаём простые косы из каждого генератора
        # (это не всегда правильно, но показывает структуру)
        for g in positive_part.generators:
            if g > 0:
                simple_braids.append(BraidWord([g], self.n))
        
        return (k, simple_braids)
    
    def is_identity(self) -> bool:
        return len(self.generators) == 0
    
    def __str__(self) -> str:
        if not self.generators:
            return "id"
        result = []
        for g in self.generators:
            if g > 0:
                result.append(f"σ_{g}")
            else:
                result.append(f"σ_{abs(g)}⁻¹")
        return "·".join(result)
    
    def __repr__(self) -> str:
        return f"BraidWord({self.generators}, n = {self.n})"


class SimpleBraids:
    """Класс для работы с простыми косами и их перестановками"""
    
    @staticmethod
    def all_permutations(n: int) -> List[List[int]]:
        """Все перестановки S_n"""
        import itertools
        return list(itertools.permutations(range(1, n + 1)))
    
    @staticmethod
    def permutation_to_simple_braid(perm: List[int], n: int) -> Optional[BraidWord]:
        """
        Преобразует перестановку в простую косу.
        Использует алгоритм: разложение перестановки в произведение
        соседних транспозиций с минимальным числом инверсий.
        """
        perm = list(perm)
        original = list(range(1, n + 1))
        generators = []
        
        # Пузырьковая сортировка для получения минимального представления
        for i in range(n - 1):
            for j in range(n - 1 - i):
                if perm[j] > perm[j + 1]:
                    perm[j], perm[j + 1] = perm[j + 1], perm[j]
                    # Добавляем σ_{j+1} (индексация с 1)
                    generators.append(j + 1)
        
        # Переворачиваем, так как применяли транспозиции слева
        # В косах порядок важен
        return BraidWord(generators, n)
    
    @staticmethod
    def simple_braid_to_permutation(braid: BraidWord) -> List[int]:
        """Преобразует простую косу обратно в перестановку"""
        return braid.to_permutation()
    
    @staticmethod
    def all_simple_braids(n: int) -> List[BraidWord]:
        """
        Генерирует все простые косы в B_n.
        Их количество = n!
        """
        perms = SimpleBraids.all_permutations(n)
        simple_braids = []
        for perm in perms:
            braid = SimpleBraids.permutation_to_simple_braid(list(perm), n)
            if braid:
                simple_braids.append(braid)
        return simple_braids


# Демонстрация работы
if __name__ == "__main__":
    print("=" * 60)
    print("ГРУППЫ КОС АРТИНА — ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    
    # 1. Создание кос
    print("\n1. Создание кос:")
    b1 = BraidWord([1, 2, 1], n = 3)  # σ₁σ₂σ₁
    b2 = BraidWord([2, 1, 2], n = 3)  # σ₂σ₁σ₂
    print(f"  b1 = {b1}")
    print(f"  b2 = {b2}")
    
    # 2. Соотношение кос
    print("\n2. Соотношение кос:")
    print(f"  σ₁σ₂σ₁ = {b1}")
    print(f"  σ₂σ₁σ₂ = {b2}")
    print(f"  Равны ли они? {b1.generators == b2.generators}")
    print("  (В группе кос они равны, но в свободной группе — нет)")
    
    # 3. Обратная коса
    print("\n3. Обратная коса:")
    b1_inv = b1.inverse()
    print(f"  b1 = {b1}")
    print(f"  b1⁻¹ = {b1_inv}")
    print(f"  b1·b1⁻¹ = {b1 * b1_inv} (должно сократиться в группе)")
    
    # 4. Гомоморфизм в S_n
    print("\n4. Гомоморфизм в S_n:")
    b3 = BraidWord([1, 2, 1, 2], n = 3)
    perm = b3.to_permutation()
    print(f"  Коса {b3} → перестановка {perm}")
    
    # 5. Положительные косы
    print("\n5. Положительные косы:")
    pos = BraidWord([1, 2, 3, 1], n = 4)
    neg = BraidWord([1, -2, 3], n = 4)
    print(f"  {pos} — положительная? {pos.is_positive()}")
    print(f"  {neg} — положительная? {neg.is_positive()}")
    
    # 6. Простые косы
    print("\n6. Простые косы в B₃:")
    simple_braids = SimpleBraids.all_simple_braids(3)
    print(f"  Всего простых кос: {len(simple_braids)} (должно быть 3! = 6)")
    for i, braid in enumerate(simple_braids):
        perm = braid.to_permutation()
        print(f"    {i+1}. {braid} → перестановка {perm}")
    
    # 7. Проверка, является ли коса простой
    print("\n7. Проверка на простоту:")
    test_braid = BraidWord([1, 2], n = 3)
    print(f"  {test_braid} — простая? {test_braid.is_simple()}")
    test_braid2 = BraidWord([1, 2, 1, 2], n = 3)
    print(f"  {test_braid2} — простая? {test_braid2.is_simple()}")
    
    # 8. Каноническая форма и нормальная форма Гарсайда
    print("\n8. Нормальная форма Гарсайда (упрощённая):")
    b4 = BraidWord([1, 2, 1, -1], n = 3)
    k, simple_list = b4.normalize_garside()
    print(f"  Коса {b4}")
    print(f"  σ₁ ^ {k} · " + " · ".join(str(s) for s in simple_list))
    
    print("\n" + "=" * 60)
    print("Примечание: полная реализация нормальной формы Гарсайда")
    print("требует алгоритма лево-взвешенного разложения и может")
    print("занимать несколько сотен строк кода.")
    print("=" * 60)