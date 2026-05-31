# 1. Аксиомы группы
"""
Модуль для работы с группами на основе аксиом из теории групп.
Реализует: абстрактную группу, циклическую подгруппу,
порядок элемента, группу вычетов по модулю,
простейшую матричную группу GL(2, Z_n).
"""

from math import gcd
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class Group:
    """
    Абстрактный класс, представляющий группу.
    Для конкретной группы нужно определить:
    - множество элементов
    - бинарную операцию
    - единицу
    - функцию, возвращающую обратный элемент
    """
    def __init__(self, elements: Set[Any], operation: Callable[[Any, Any], Any], 
                 identity: Any, inverse_func: Callable[[Any], Any], 
                 name: str = "Group", is_abelian: Optional[bool] = None):
        self.elements = elements
        self.op = operation
        self.e = identity
        self.inv = inverse_func
        self.name = name
        self._is_abelian = is_abelian

    def __contains__(self, item):
        return item in self.elements

    def multiply(self, a: Any, b: Any) -> Any:
        """Выполняет групповую операцию a * b."""
        if a not in self or b not in self:
            raise ValueError(f"Элементы {a} или {b} не принадлежат группе")
        return self.op(a, b)

    def order_of_element(self, g: Any) -> int:
        """
        Вычисляет порядок элемента g.
        Порядок — наименьшее положительное k, такое что g^k = e.
        Если такого k нет, возвращает float('inf').
        """
        if g not in self:
            raise ValueError(f"Элемент {g} не принадлежит группе")

        if g == self.e:
            return 1

        current = g
        k = 1
        # Ограничиваем поиск размером группы (если группа конечна)
        max_steps = len(self.elements) if self.is_finite() else 1000
        while k <= max_steps:
            if current == self.e:
                return k
            current = self.multiply(current, g)
            k += 1

        # Если группа бесконечна и не нашли единицу
        if not self.is_finite():
            return float('inf')
        else:
            # На случай, если что-то пошло не так в конечной группе
            raise RuntimeError(f"Не удалось найти порядок для {g} в конечной группе")

    def cyclic_subgroup(self, g: Any) -> Set[Any]:
        """Возвращает циклическую подгруппу, порождённую элементом g."""
        if g not in self:
            raise ValueError(f"Элемент {g} не принадлежит группе")

        result = set()
        current = g
        # Идём по степеням, пока не встретим единицу или зацикливание
        while current not in result:
            result.add(current)
            current = self.multiply(current, g)
            if current == self.e:
                result.add(self.e)
                break
        return result

    def is_finite(self) -> bool:
        """Проверяет, конечна ли группа."""
        return len(self.elements) < float('inf')

    def check_associativity(self, sample_size: int = 20) -> bool:
        """
        Проверяет ассоциативность на выборке (для конечных групп).
        Для полной проверки нужно перебрать все тройки.
        """
        if not self.is_finite():
            print("Ассоциативность для бесконечных групп не проверяется автоматически")
            return True

        elems = list(self.elements)
        # Проверяем все тройки (осторожно — O(n^3))
        for a in elems:
            for b in elems:
                for c in elems:
                    if self.multiply(self.multiply(a, b), c) != self.multiply(a, self.multiply(b, c)):
                        print(f"Нарушена ассоциативность: ({a} * {b}) * {c} != {a} * ({b} * {c})")
                        return False
        return True

    @property
    def is_abelian(self) -> bool:
        """Проверяет коммутативность (если группа конечна)."""
        if self._is_abelian is not None:
            return self._is_abelian

        if not self.is_finite():
            print("Коммутативность бесконечной группы не проверена автоматически")
            return False

        elems = list(self.elements)
        for a in elems:
            for b in elems:
                if self.multiply(a, b) != self.multiply(b, a):
                    return False
        return True

    def __repr__(self):
        return f"Group({self.name}, |G| = {len(self.elements) if self.is_finite() else '∞'}, abelian={self.is_abelian})"


# ============ Конкретные группы ============

class AdditiveGroup(Group):
    """Абелева группа с аддитивной записью (операция — сложение)."""
    def __init__(self, elements: Set[Any], zero: Any, add_func: Callable[[Any, Any], Any], neg_func: Callable[[Any], Any], name: str = "AdditiveGroup"):
        super().__init__(elements, add_func, zero, neg_func, name, is_abelian = True)

    def order_of_element(self, g: Any) -> int:
        """Порядок в аддитивной группе: наименьшее k, такое что k*g = 0."""
        if g not in self:
            raise ValueError(f"Элемент {g} не принадлежит группе")
        if g == self.e:
            return 1

        current = g
        k = 1
        max_steps = len(self.elements) if self.is_finite() else 1000
        while k <= max_steps:
            if current == self.e:
                return k
            current = self.multiply(current, g)  # здесь multiply = add
            k += 1
        return float('inf') if not self.is_finite() else -1


def group_z_n(n: int) -> Group:
    """
    Создаёт группу вычетов по модулю n: (Z_n, +).
    Аддитивная циклическая группа порядка n.
    """
    elements = set(range(n))

    def add(a: int, b: int) -> int:
        return (a + b) % n

    def inv(a: int) -> int:
        return (-a) % n

    return AdditiveGroup(elements, 0, add, inv, name=f"Z_{n}")


def group_gl2_z_n(n: int) -> Group:
    """
    Создаёт группу GL(2, Z_n) — обратимых матриц 2x2 над кольцом Z_n.
    Матрица обратима, если её определитель обратим в Z_n (т.е. gcd(det, n) = 1).
    """
    elements_set = set()
    # Представляем матрицу как кортеж (a, b, c, d)
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    det = (a*d - b*c) % n
                    if gcd(det, n) == 1:  # определитель обратим по модулю n
                        elements_set.add((a, b, c, d))

    def mat_mul(m1: Tuple[int, int, int, int], m2: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        a1, b1, c1, d1 = m1
        a2, b2, c2, d2 = m2
        return (
            (a1 * a2 + b1 * c2) % n,
            (a1 * b2 + b1 * d2) % n,
            (c1 * a2 + d1 * c2) % n,
            (c1 * b2 + d1 * d2) % n
        )

    def mat_inv(m: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        a, b, c, d = m
        det = (a*d - b*c) % n
        # Находим обратный к det в Z_n
        det_inv = pow(det, -1, n)  # Python 3.8+ поддерживает модульный обратный
        return (
            (d * det_inv) % n,
            ((-b) * det_inv) % n,
            ((-c) * det_inv) % n,
            (a * det_inv) % n
        )

    identity = (1, 0, 0, 1)

    return Group(elements_set, mat_mul, identity, mat_inv, name = f"GL(2, Z_{n})", is_abelian = False)


# ============ Демонстрация ============

def demo():
    print("=" * 60)
    print("Демонстрация работы с группами")
    print("=" * 60)

    # 1. Группа Z_6 (аддитивная, циклическая)
    print("\n1. Группа Z_6 (вычеты по модулю 6, сложение):")
    G1 = group_z_n(6)
    print(G1)
    print(f"Элементы: {sorted(G1.elements)}")
    print(f"2 + 5 = {G1.multiply(2, 5)}")
    print(f"Порядок элемента 2: {G1.order_of_element(2)}")
    print(f"Циклическая подгруппа, порождённая 2: {G1.cyclic_subgroup(2)}")
    print(f"Группа абелева: {G1.is_abelian}")

    # 2. Группа GL(2, Z_2)
    print("\n2. Группа GL(2, Z_2) (невырожденные матрицы 2 x 2 над Z_2):")
    G2 = group_gl2_z_n(2)
    print(G2)
    print(f"Количество элементов (порядок группы): |GL(2, Z_2)| = {len(G2.elements)}")
    print("Некоторые элементы:")
    for i, m in enumerate(sorted(G2.elements)[:5]):
        print(f"  {m}")
    print("Проверка умножения:")
    A = (1, 1, 0, 1)  # матрица [1 1; 0 1]
    B = (0, 1, 1, 0)  # матрица [0 1; 1 0]
    print(f"A = {A}, B = {B}")
    print(f"A * B = {G2.multiply(A, B)}")
    print(f"Порядок элемента A = {G1.order_of_element(2)}? Нет, считаем для GL(2, Z_2): {G2.order_of_element(A)}")
    print(f"Группа абелева: {G2.is_abelian} (ожидаем False)")

    # Проверяем ассоциативность для GL(2,Z_2)
    print(f"Ассоциативность выполняется: {G2.check_associativity()}")

    # 3. Бесконечная аддитивная группа целых чисел (моделируем ограниченно)
    print("\n3. Бесконечная группа (Z, +) — моделируем с ограничением:")

    class InfiniteIntsGroup(AdditiveGroup):
        def __init__(self):
            # Для демонстрации используем только часть элементов,
            # но логически это бесконечная группа
            self._all_ints = set()
            super().__init__(set(), 0, lambda a, b: a + b, lambda a: -a, name = "Z (infinite)")
            self._is_finite = False

        def __contains__(self, item):
            return isinstance(item, int)

        def is_finite(self):
            return False

    G3 = InfiniteIntsGroup()
    print(G3)
    print(f"Порядок элемента 5 в (Z,+): {G3.order_of_element(5)} (бесконечность)")


if __name__ == "__main__":
    demo()