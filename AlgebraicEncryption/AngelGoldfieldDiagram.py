# 3. Схема Аншель - Аншеля - Голдфилда (L. Anshel, М. Anshel, G. Goldfeld)
"""
Демонстрация схемы Anshel-Anshel-Goldfeld (AAG) для выработки общего ключа.
Платформа: группа (например, GL(2, Z_p) или просто группа обратимых матриц).
"""

import random
import sys
from typing import List, Tuple

# ============================================================
# 1. Абстрактный класс для группы с операциями, необходимыми для AAG
# ============================================================
class GroupElement:
    """Базовый класс для элемента группы."""
    def multiply(self, other: 'GroupElement') -> 'GroupElement':
        raise NotImplementedError

    def inverse(self) -> 'GroupElement':
        raise NotImplementedError

    def conjugate(self, other: 'GroupElement') -> 'GroupElement':
        """Возвращает other^{-1} * self * other"""
        return other.inverse().multiply(self).multiply(other)

    def normal_form(self) -> str:
        """Каноническое представление (для публикации)."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.normal_form()


# ============================================================
# 2. Конкретная реализация: группа вычетов по модулю (просто для демонстрации)
#    Здесь умножение по модулю, но в реальных сценариях должна быть неабелева группа
# ============================================================
class ModularElement(GroupElement):
    def __init__(self, value: int, modulus: int):
        self.value = value % modulus
        self.mod = modulus

    def multiply(self, other: 'ModularElement') -> 'ModularElement':
        if self.mod != other.mod:
            raise ValueError("Moduli mismatch")
        return ModularElement((self.value * other.value) % self.mod, self.mod)

    def inverse(self) -> 'ModularElement':
        # Требуется, чтобы value был обратим по модулю.
        # Для простоты: если не обратим, генерируем исключение.
        try:
            inv = pow(self.value, -1, self.mod)
        except ValueError:
            raise ValueError(f"Element {self.value} not invertible mod {self.mod}")
        return ModularElement(inv, self.mod)

    def normal_form(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModularElement):
            return False
        return self.value == other.value and self.mod == other.mod


# ============================================================
# 3. Реализация протокола AAG для абстрактной группы
# ============================================================
class AAGProtocol:
    def __init__(self, group_generators: List[GroupElement]):
        """
        group_generators: открытые порождающие a1,...,ak, c1,...,cl (все вместе)
        Первые k элементов — a_i, следующие l — c_j.
        """
        self.generators = group_generators
        self.k = len(group_generators) // 2
        self.l = len(group_generators) - self.k
        if self.k == 0 or self.l == 0:
            raise ValueError("Нужны оба набора a_i и c_j")

        self.a_list = group_generators[:self.k]
        self.c_list = group_generators[self.k:]

    def random_word(self, generators: List[GroupElement], length: int) -> GroupElement:
        """Случайное слово из генераторов и обратных к ним."""
        result = None
        for _ in range(length):
            g = random.choice(generators)
            if random.choice([True, False]):  # иногда берем обратный
                g = g.inverse()
            if result is None:
                result = g
            else:
                result = result.multiply(g)
        if result is None:
            # если length=0, вернуть нейтральный элемент – для простоты используем первый генератор
            return generators[0].multiply(generators[0].inverse())
        return result

    def generate_user_secret(self, generators: List[GroupElement]) -> GroupElement:
        """Секретный элемент u или v как слово от своих генераторов."""
        word_length = random.randint(3, 8)
        return self.random_word(generators, word_length)

    def compute_conjugates(self, secret: GroupElement,
                           target_list: List[GroupElement]) -> List[GroupElement]:
        """Вычисляет secret^{-1} * x * secret для каждого x в target_list."""
        return [x.conjugate(secret) for x in target_list]

    def compute_shared_key(self, my_secret: GroupElement, conjugates_of_other: List[GroupElement], my_original_generators: List[GroupElement]) -> GroupElement:
        """
        my_secret: свой секретный элемент (u для A, v для C)
        conjugates_of_other: опубликованные сопряжённые от другой стороны:
            для A: a'_i = v^{-1} a_i v
            для C: c'_j = u^{-1} c_j u
        my_original_generators: оригинальные генераторы, от которых строился my_secret.
        Возвращает [my_secret, other_secret] = my_secret^{-1} * other_secret^{-1} * my_secret * other_secret
        """
        # Вычисляем my_original_generators, сопряжённые с помощью чужого секрета
        # Но мы их уже получили как conjugates_of_other.
        # Поэтому строим от них то же слово, что и для my_secret
        word = self._reconstruct_word(my_secret, my_original_generators, conjugates_of_other)
        if word is None:
            raise RuntimeError("Не удалось восстановить слово от conjugates_of_other")
        # result = my_secret^{-1} * word
        return my_secret.inverse().multiply(word)

    def _reconstruct_word(self, secret: GroupElement, original_gens: List[GroupElement], conjugated_gens: List[GroupElement]) -> GroupElement:
        """
        В реальной системе мы не знаем точное слово, но знаем, что secret = f(original_gens).
        Мы применяем ту же функцию f к conjugated_gens.
        Здесь для простоты: перебираем короткие слова, пока не найдём совпадение с secret.
        Это демонстрационный, неэффективный метод.
        """
        # Простейший перебор (только для учебных целей!)
        # В реальном протоколе Алиса ЗНАЕТ своё слово u(a1..ak) и просто подставляет a'_i.
        # У нас сейчас secret уже вычислен, но мы не хранили слово.
        # Поэтому в учебной реализации допустим, что мы храним слово явно.
        # Для честной симуляции переделаем логику: будем хранить слово при создании secret.
        raise NotImplementedError("Этот метод должен быть заменён на прямое хранение слова.")

# ============================================================
# 4. Полноценная симуляция с хранением слова (исправленный подход)
# ============================================================
class AAGProtocolWithWord(AAGProtocol):
    def generate_user_secret(self, generators: List[GroupElement]) -> Tuple[GroupElement, List[int]]:
        """
        Возвращает (secret, word_indices), где word_indices хранит последовательность:
        (index, is_inverse)
        """
        length = random.randint(3, 8)
        word = []
        result = None
        for _ in range(length):
            idx = random.randint(0, len(generators) - 1)
            inv = random.choice([True, False])
            word.append((idx, inv))
            g = generators[idx]
            if inv:
                g = g.inverse()
            if result is None:
                result = g
            else:
                result = result.multiply(g)
        if result is None:
            # Нейтральный элемент (не совсем корректно, но для demo)
            result = generators[0].multiply(generators[0].inverse())
        return result, word

    def apply_word_to_generators(self, word: List[Tuple[int, bool]], generator_list: List[GroupElement]) -> GroupElement:
        """Применяет слово (индексы+признак инверсии) к новому списку генераторов."""
        result = None
        for idx, inv in word:
            g = generator_list[idx]
            if inv:
                g = g.inverse()
            if result is None:
                result = g
            else:
                result = result.multiply(g)
        if result is None:
            # Пустое слово: нейтральный элемент
            return generator_list[0].multiply(generator_list[0].inverse())
        return result

    def compute_shared_key_from_word(self, my_secret: GroupElement, my_word: List[Tuple[int, bool]], conjugates_of_other: List[GroupElement]) -> GroupElement:
        """
        my_secret: u или v
        my_word: слово, выражающее my_secret через my_original_generators
        conjugates_of_other: список сопряжённых генераторов другой стороны
        """
        reconstructed = self.apply_word_to_generators(my_word, conjugates_of_other)
        return my_secret.inverse().multiply(reconstructed)


# ============================================================
# 5. Демонстрация протокола в группе вычетов (неабелевость не используется!)
# ============================================================
def demo_modular_group():
    print("=== Демонстрация AAG на мультипликативной группе по модулю 101 ===")
    mod = 101
    # Выберем несколько обратимых элементов по модулю 101 в качестве генераторов
    # a1, a2, c1, c2
    a1 = ModularElement(2, mod)
    a2 = ModularElement(3, mod)
    c1 = ModularElement(5, mod)
    c2 = ModularElement(7, mod)

    generators = [a1, a2, c1, c2]  # k=2, l=2

    protocol = AAGProtocolWithWord(generators)

    # ---- Сторона A ----
    u, word_u = protocol.generate_user_secret(protocol.a_list)  # u = u(a1,a2)
    print(f"A: секрет u = {u}")
    # Публикует c'_j = u^{-1} c_j u
    pub_c = protocol.compute_conjugates(u, protocol.c_list)
    print(f"A публикует c' = {pub_c}")

    # ---- Сторона C ----
    v, word_v = protocol.generate_user_secret(protocol.c_list)  # v = v(c1,c2)
    print(f"C: секрет v = {v}")
    # Публикует a'_i = v^{-1} a_i v
    pub_a = protocol.compute_conjugates(v, protocol.a_list)
    print(f"C публикует a' = {pub_a}")

    # ---- A вычисляет ключ ----
    key_A = protocol.compute_shared_key_from_word(u, word_u, pub_a)
    print(f"A вычислил ключ: {key_A}")

    # ---- C вычисляет ключ ----
    key_C = protocol.compute_shared_key_from_word(v, word_v, pub_c)
    print(f"C вычислил ключ: {key_C} (обратный к ключу A)")

    # Проверка: [u,v] и [v,u] = [u,v]^{-1}
    # В абелевом случае [u,v] = 1, так что ключи совпадут
    if key_A.multiply(key_C).normal_form() == "1":
        print("\nКлючи совпали с точностью до обращения (в абелевой группе [u, v] = 1).")
    else:
        print("\nКлючи различаются (но в неабелевой группе это было бы [u, v] и его обратный).")


if __name__ == "__main__":
    demo_modular_group()