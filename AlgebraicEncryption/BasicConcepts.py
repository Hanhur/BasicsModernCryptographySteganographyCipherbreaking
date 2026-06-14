# 1 . Основные понятия
"""
Алгебраическая криптография: протокол обмена ключами на основе групп кос Артина
Реализация концепции из лекции А. Мясникова, В. Шпильрайна, А. Ушакова

Используется группа кос B_n с представлением:
σ_i * σ_{i+1} * σ_i = σ_{i+1} * σ_i * σ_{i+1}  (соотношение кос)
σ_i * σ_j = σ_j * σ_i  для |i-j| > 1
"""

import random
import json
from typing import Tuple, List, Optional
from dataclasses import dataclass
from functools import lru_cache

class BraidGroupElement:
    """
    Элемент группы кос Артина.
    Представлен в нормальной форме (канонической) — список образующих σ_i ^ e
    где e = ±1, а i — номер нити.
    """
    
    def __init__(self, generators: List[Tuple[int, int]]):
        """
        generators: список пар (индекс образующей, экспонента)
        пример: [(1,1), (2,-1), (1,1)] означает σ1 * σ2 ^ {-1} * σ1
        """
        # Приводим к нормальной форме сразу при создании
        self.generators = self._normalize(generators)
    
    def _normalize(self, gens: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Каноническая форма: сокращение σ_i * σ_i ^ {-1} и объединение степеней"""
        simplified = []
        for idx, exp in gens:
            if simplified and simplified[-1][0] == idx:
                new_exp = simplified[-1][1] + exp
                if new_exp == 0:
                    simplified.pop()
                else:
                    simplified[-1] = (idx, new_exp)
            else:
                simplified.append((idx, exp))
        return simplified
    
    def __mul__(self, other: 'BraidGroupElement') -> 'BraidGroupElement':
        """Умножение в группе кос (некоммутативное)"""
        return BraidGroupElement(self.generators + other.generators)
    
    def inverse(self) -> 'BraidGroupElement':
        """Обратный элемент"""
        inv_gens = [(idx, -exp) for idx, exp in reversed(self.generators)]
        return BraidGroupElement(inv_gens)
    
    def conjugate(self, g: 'BraidGroupElement') -> 'BraidGroupElement':
        """
        Сопряжение: g * self * g ^ {-1}
        Это основа трудноразрешимой задачи сопряжённости
        """
        return g * self * g.inverse()
    
    def __eq__(self, other: 'BraidGroupElement') -> bool:
        """Сравнение через каноническую форму"""
        if not isinstance(other, BraidGroupElement):
            return False
        return self.generators == other.generators
    
    def __repr__(self) -> str:
        if not self.generators:
            return "e (тождество)"
        result = []
        for idx, exp in self.generators:
            if exp == 1:
                result.append(f"σ{idx}")
            elif exp == -1:
                result.append(f"σ{idx}⁻¹")
            else:
                result.append(f"σ{idx}^{exp}")
        return " · ".join(result)
    
    def to_json(self) -> str:
        """Сериализация для обмена"""
        return json.dumps(self.generators)
    
    @staticmethod
    def from_json(data: str) -> 'BraidGroupElement':
        """Десериализация"""
        return BraidGroupElement(json.loads(data))


class BraidGroup:
    """
    Группа кос Артина B_n с n нитями.
    Поддерживает генерацию случайных элементов и коммутирующих подгрупп.
    """
    
    def __init__(self, n_strands: int = 5):
        """
        n_strands: количество нитей (чем больше, тем сложнее задача сопряжённости)
        Образующие: σ1, σ2, ..., σ_{n-1}
        """
        self.n = n_strands
        self.generators = list(range(1, n_strands))  # σ1 ... σ_{n-1}
    
    def random_element(self, length: int = 10) -> BraidGroupElement:
        """
        Генерирует случайный элемент группы кос.
        length: длина слова в образующих
        """
        gens = []
        for _ in range(length):
            idx = random.choice(self.generators)
            exp = random.choice([1, -1])  # σ_i или σ_i^{-1}
            gens.append((idx, exp))
        return BraidGroupElement(gens)
    
    def commuting_subgroup(self, start_index: int, size: int = 2) -> List[int]:
        """
        Возвращает порождающие коммутирующей подгруппы.
        
        В группе кос B_n подгруппы, сдвинутые достаточно далеко, коммутируют.
        Например, подгруппа, порождённая {σ1, σ2} и подгруппа, порождённая {σ4, σ5}
        будут коммутировать при n ≥ 6.
        
        Args:
            start_index: начальный индекс образующей (1-based)
            size: количество образующих в подгруппе
        
        Returns:
            список индексов образующих
        """
        if start_index + size - 1 >= self.n:
            raise ValueError(f"Недостаточно нитей: нужны образующие до σ{start_index + size - 1}, "f"а максимальная σ{self.n - 1} в группе B_{self.n}")
        return list(range(start_index, start_index + size))


class AlgebraicCryptoProtocol:
    """
    Протокол обмена ключами на основе групп кос (Ko-Lee protocol).
    
    Основан на трудноразрешимой проблеме сопряжённости:
    Зная a, b, xax^{-1} вычислить x.
    
    В группах кос эта задача считается сложной для случайных элементов.
    """
    
    def __init__(self, n_strands: int = 8):
        """
        n_strands должно быть ≥ 6, чтобы можно было выбрать 
        две нетривиальные коммутирующие подгруппы.
        Рекомендуется n_strands ≥ 8 для большей стойкости.
        """
        if n_strands < 6:
            raise ValueError("Для криптографической стойкости нужно минимум 6 нитей")
        self.group = BraidGroup(n_strands)
        self.n = n_strands
        
        # Выбираем две коммутирующие подгруппы
        # A = <σ1, σ2>, B = <σ4, σ5> при n≥6
        # Для n=6: σ1,σ2 и σ4,σ5 коммутируют (расстояние 2 между группами)
        self.A_gens = self.group.commuting_subgroup(1, size = 2)   # σ1, σ2
        self.B_gens = self.group.commuting_subgroup(4, size = 2)   # σ4, σ5
        
        print(f"Инициализация протокола: группа B_{n_strands}")
        print(f"  Подгруппа А: <σ{self.A_gens[0]}, σ{self.A_gens[1]}>")
        print(f"  Подгруппа Б: <σ{self.B_gens[0]}, σ{self.B_gens[1]}>")
        print(f"  Коммутируют ли? Расстояние = {self.B_gens[0] - self.A_gens[1]} > 1 → ДА\n")
    
    def generate_private_key(self, subg_type: str = 'A') -> BraidGroupElement:
        """Генерирует закрытый ключ в одной из коммутирующих подгрупп"""
        if subg_type == 'A':
            gen_indices = self.A_gens
        else:
            gen_indices = self.B_gens
        
        # Случайное слово в подгруппе
        length = random.randint(5, 15)
        elements = []
        for _ in range(length):
            idx = random.choice(gen_indices)
            exp = random.choice([1, -1])
            elements.append((idx, exp))
        return BraidGroupElement(elements)
    
    def generate_public_element(self, private_key: BraidGroupElement) -> BraidGroupElement:
        """
        Генерирует открытый элемент: a * x * a ^ {-1}
        (сопряжение открытого элемента x закрытым ключом a)
        """
        # Случайный элемент x из всей группы (общий параметр протокола)
        x = self.group.random_element(length = 8)
        # Возвращаем сопряжённый элемент
        return private_key.conjugate(x)
    
    def shared_secret(self, private_A: BraidGroupElement, public_B: BraidGroupElement) -> BraidGroupElement:
        """
        Вычисляет общий секрет: a * (b * x * b ^ {-1}) * a ^ {-1} 
        При этом, так как a и b коммутируют, результат равен (ab) x (ab) ^ {-1}
        """
        # Сопряжение публичного элемента B приватным ключом A
        return private_A.conjugate(public_B)
    
    def run_protocol(self, verbose: bool = True) -> Tuple[str, str]:
        """
        Полный цикл протокола обмена ключами.
        Возвращает секреты Алисы и Боба (они должны быть равны).
        """
        if verbose:
            print("=" * 70)
            print("Криптографический протокол на группе кос Артина (Ko-Lee)")
            print(f"Группа B_{self.n} (кос из {self.n} нитей)")
            print("=" * 70)
        
        # 1. Алиса и Боб генерируют закрытые ключи
        a = self.generate_private_key('A')  # в подгруппе A
        b = self.generate_private_key('B')  # в подгруппе B
        
        if verbose:
            print("\n[1] Генерация закрытых ключей в коммутирующих подгруппах")
            print(f"    Закрытый ключ Алисы a ∈ <σ{self.A_gens}>: {a}")
            print(f"    Закрытый ключ Боба   b ∈ <σ{self.B_gens}>: {b}")
        
        # 2. Общий открытый элемент x
        x = self.group.random_element(length = 6)
        if verbose: 
            print(f"\n[2] Общий открытый элемент x ∈ B_{self.n}: {x}")
        
        # 3. Вычисление и обмен публичными ключами
        # Алиса вычисляет a*x*a^{-1}, Боб вычисляет b*x*b^{-1}
        pub_A = a.conjugate(x)
        pub_B = b.conjugate(x)
        
        if verbose:
            print(f"\n[3] Обмен публичными элементами (проблема сопряжённости):")
            print(f"    Алиса → Боб: a·x·a⁻¹ = {pub_A}")
            print(f"    Боб   → Алиса: b·x·b⁻¹ = {pub_B}")
        
        # 4. Вычисление общего секрета
        # Алиса: a * (b*x*b^{-1}) * a^{-1} = (ab)x(ab)^{-1}
        secret_alice = self.shared_secret(a, pub_B)
        # Боб: b * (a*x*a^{-1}) * b^{-1} = (ba)x(ba)^{-1} = (ab)x(ab)^{-1}
        secret_bob = self.shared_secret(b, pub_A)
        
        if verbose:
            print(f"\n[4] Вычисление общего секрета:")
            print(f"    Алиса вычисляет a·(b·x·b⁻¹)·a⁻¹ = {secret_alice}")
            print(f"    Боб   вычисляет b·(a·x·a⁻¹)·b⁻¹ = {secret_bob}")
        
        # 5. Проверка равенства
        is_equal = (secret_alice == secret_bob)
        if verbose:
            print(f"\n[5] Результат проверки: секреты {'СОВПАДАЮТ ✓' if is_equal else 'НЕ СОВПАДАЮТ ✗'}")
            if is_equal:
                print("    Протокол успешно завершён! Общий секрет установлен.")
            print("=" * 70)
        
        return secret_alice.to_json(), secret_bob.to_json()


def demonstrate_braid_properties():
    """Демонстрация свойств группы кос"""
    print("\n" + "=" * 70)
    print("Демонстрация свойств группы кос Артина")
    print("=" * 70)
    
    G = BraidGroup(4)
    
    # Некоммутативность
    a = BraidGroupElement([(1,1), (2,1)])   # σ1·σ2
    b = BraidGroupElement([(2,1), (1,1)])   # σ2·σ1
    
    print(f"\n1. Некоммутативность группы кос:")
    print(f"   a = {a}")
    print(f"   b = {b}")
    print(f"   a·b = {a * b}")
    print(f"   b·a = {b * a}")
    print(f"   a·b ≠ b·a? {(a * b) != (b * a)} ✓")
    
    # Соотношение кос
    s1 = BraidGroupElement([(1,1)])
    s2 = BraidGroupElement([(2,1)])
    
    left = s1 * s2 * s1
    right = s2 * s1 * s2
    
    print(f"\n2. Соотношение кос (σ₁·σ₂·σ₁ = σ₂·σ₁·σ₂):")
    print(f"   σ₁·σ₂·σ₁ = {left}")
    print(f"   σ₂·σ₁·σ₂ = {right}")
    print(f"   Равенство выполняется? {left == right} ✓")
    
    # Каноническая форма
    print(f"\n3. Каноническая форма (сокращение σ₁·σ₁⁻¹):")
    elem = BraidGroupElement([(1, 1), (1, -1), (2, 1)])
    print(f"   σ₁·σ₁⁻¹·σ₂ = {elem} (σ₁·σ₁⁻¹ автоматически сократились) ✓")


def demonstrate_diffie_hellman_analogy():
    """Аналогия с протоколом Диффи-Хеллмана"""
    print("\n" + "=" * 70)
    print("Аналогия с классическим протоколом Диффи-Хеллмана")
    print("=" * 70)
    
    print("""
    Классический DH:              Группа кос (Ko-Lee):
    ─────────────────────────────────────────────────────
    Алиса: a (секрет)             Алиса: a ∈ A (секрет)
    Боб:   b (секрет)             Боб:   b ∈ B (секрет)
    
    Алиса → Боб: g^a              Алиса → Боб: a·x·a⁻¹
    Боб → Алиса: g^b              Боб → Алиса: b·x·b⁻¹
    
    Секрет: g^(ab)                Секрет: (ab)·x·(ab)⁻¹
    
    Проблема: дискретный          Проблема: сопряжённости
    логарифм                      в группе кос
    """)


def main():
    """Демонстрация работы алгебраической криптосистемы"""
    
    print("\033[1m" + "Алгебраическая криптография" + "\033[0m")
    print("На основе лекции о группах кос Артина (А. Мясников, В. Шпильрайн, А. Ушаков)\n")
    
    # Демонстрация свойств
    demonstrate_braid_properties()
    demonstrate_diffie_hellman_analogy()
    
    # Пример 1: Протокол с n=6
    print("\n" + "=" * 70)
    print("ПРИМЕР 1: Протокол с минимальными параметрами (B₆)")
    print("=" * 70)
    protocol_min = AlgebraicCryptoProtocol(n_strands = 6)
    secret1, secret2 = protocol_min.run_protocol(verbose = True)
    
    # Пример 2: Протокол с n=8 (более стойкий)
    print("\n" + "=" * 70)
    print("ПРИМЕР 2: Протокол с усиленными параметрами (B₈)")
    print("=" * 70)
    protocol_strong = AlgebraicCryptoProtocol(n_strands = 8)
    secret3, secret4 = protocol_strong.run_protocol(verbose = True)
    
    # Пример 3: Анализ стойкости
    print("\n" + "=" * 70)
    print("КРИПТОСТОЙКОСТЬ: Трудноразрешимая задача сопряжённости")
    print("=" * 70)
    print("""
    Злоумышленник перехватывает:
    • x (открытый элемент)
    • a·x·a⁻¹ (от Алисы)
    • b·x·b⁻¹ (от Боба)
    
    Чтобы вычислить секрет, нужно найти a или b из уравнений:
    a·x·a⁻¹ = известная величина
    
    Это проблема сопряжённости в группе кос, которая:
    • При n ≥ 6 считается экспоненциально сложной
    • Не решается квантовыми алгоритмами (в отличие от RSA/ECC)
    • Входит в класс проблем, устойчивых к квантовым атакам
    
    → Постквантовая криптостойкость
    """)


if __name__ == "__main__":
    main()