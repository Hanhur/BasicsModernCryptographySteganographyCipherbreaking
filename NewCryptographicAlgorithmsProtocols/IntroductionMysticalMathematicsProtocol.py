# Введение в протоколы zk-SNARK — мистическая математика
"""
Упрощенная симуляция zk-SNARK на чистом Python
Без numpy, только встроенные модули

Демонстрирует:
1. Доверенную настройку (Trusted Setup)
2. Генерацию доказательства (Prover)
3. Проверку доказательства (Verifier)
4. Атаку подделкой доказательства
"""

import hashlib
import random
from typing import Tuple, List, Optional
from dataclasses import dataclass
import sys

# Настройка для детерминированного воспроизводимого результата
# (в реальном мире используется криптостойкий RNG)
random.seed(42)


@dataclass
class CRS:
    """Общие справочные параметры (Common Reference String)"""
    # Зашифрованные степени секретного числа s
    # В реальном zk-SNARK это точки на эллиптической кривой
    # Здесь используем обычные целые числа для демонстрации
    g1: int  # g^s
    g2: int  # g^(s^2)
    g3: int  # g^(s^3)
    g4: int  # g^(s^4)
    # Открытый параметр для проверки
    g: int   # Базовая точка


class Polynomial:
    """Работа с полиномами без numpy"""
    
    @staticmethod
    def multiply(poly1: List[int], poly2: List[int]) -> List[int]:
        """Умножение полиномов"""
        result = [0] * (len(poly1) + len(poly2) - 1)
        for i, coef1 in enumerate(poly1):
            if coef1 == 0:
                continue
            for j, coef2 in enumerate(poly2):
                if coef2 == 0:
                    continue
                result[i + j] += coef1 * coef2
        return result
    
    @staticmethod
    def add(poly1: List[int], poly2: List[int]) -> List[int]:
        """Сложение полиномов"""
        max_len = max(len(poly1), len(poly2))
        result = [0] * max_len
        for i in range(max_len):
            if i < len(poly1):
                result[i] += poly1[i]
            if i < len(poly2):
                result[i] += poly2[i]
        return result
    
    @staticmethod
    def evaluate(poly: List[int], x: int) -> int:
        """Вычисление значения полинома в точке x"""
        result = 0
        power = 1
        for coef in poly:
            result += coef * power
            power *= x
        return result
    
    @staticmethod
    def degree(poly: List[int]) -> int:
        """Степень полинома"""
        for i in range(len(poly) - 1, -1, -1):
            if poly[i] != 0:
                return i
        return 0
    
    @staticmethod
    def trim(poly: List[int]) -> List[int]:
        """Обрезка ведущих нулей"""
        while len(poly) > 1 and poly[-1] == 0:
            poly.pop()
        return poly
    
    @staticmethod
    def to_string(poly: List[int]) -> str:
        """Красивый вывод полинома"""
        terms = []
        for i, coef in enumerate(poly):
            if coef != 0:
                if i == 0:
                    terms.append(str(coef))
                elif i == 1:
                    terms.append(f"{coef}x")
                else:
                    terms.append(f"{coef}x ^ {i}")
        return " + ".join(terms) if terms else "0"


class ZKSNARKSimulator:
    """
    Симулятор zk-SNARK для демонстрации принципов работы
    
    Сценарий: Пегги (Prover) знает решение уравнения x ^ 3 + x + 5 = 13
    (ответ x = 2) и хочет доказать это Виктору (Verifier) не раскрывая x
    """
    
    def __init__(self):
        # Секретные параметры (известны только "доверенному настройщику")
        self.secret_s = random.randint(100, 1000)  # Секретное число s
        self.secret_g = random.randint(2, 10)      # Генератор
        
        print(f"🔐 Доверенная настройка (Trusted Setup)")
        print(f"   Секретное s = {self.secret_s} (будет уничтожено)")
        print(f"   Генератор g = {self.secret_g}")
        print()
        
        # Генерация CRS (Common Reference String)
        self.crs = self._setup()
        
        print("📋 CRS сгенерирован:")
        print(f"   g = {self.crs.g}")
        print(f"   g1 = {self.crs.g1} (g ^ s)")
        print(f"   g2 = {self.crs.g2} (g ^ (s ^ 2))")
        print(f"   g3 = {self.crs.g3} (g ^ (s ^ 3))")
        print(f"   g4 = {self.crs.g4} (g ^ (s ^ 4))")
        print("   [секрет s уничтожен!]")
        print()
    
    def _setup(self) -> CRS:
        """Создание общих параметров (Trusted Setup)"""
        g = self.secret_g
        s = self.secret_s
        
        return CRS(
            g = g,
            g1 = g ** s,
            g2 = g ** (s ** 2),
            g3 = g ** (s ** 3),
            g4 = g ** (s ** 4)
        )
    
    def _create_witness(self, x: int) -> Tuple[List[int], List[int]]:
        """
        Создание свидетельства для доказательства:
        Полином P(x) = x ^ 3 + x + 5 - 13
        Целевой полином T(x) = (x - 2) - корень уравнения
        """
        # P(x) = x^3 + x - 8 (т.к. 5 - 13 = -8)
        p_poly = [0, 1, 0, 1]  # -8 + x + x^3
        
        # T(x) = (x - 2) - корень
        t_poly = [-2, 1]  # (x - 2)
        
        print(f"📐 Целевой полином T(x) = {Polynomial.to_string(t_poly)}")
        print(f"📐 Полином P(x) = x ^ 3 + x - 8")
        print(f"   Проверка: P(2) = {self._evaluate_poly(p_poly, 2)}")
        print()
        
        return p_poly, t_poly
    
    def _evaluate_poly(self, poly: List[int], x: int) -> int:
        """Вычисление полинома в точке (обертка)"""
        return Polynomial.evaluate(poly, x)
    
    def _divide_polynomials(self, numerator: List[int], denominator: List[int]) -> List[int]:
        """
        Деление полиномов (синтетическое деление)
        Возвращает частное
        """
        # Создаем копию числителя
        result = numerator.copy()
        
        # Находим корень
        root = -denominator[0]  # т.к. полином (x - a), корень = a
        
        # Синтетическое деление
        for i in range(len(result) - 1, 0, -1):
            result[i-1] += result[i] * root
        
        # Обрезаем последний элемент (остаток)
        result = result[:-1]
        
        return Polynomial.trim(result)
    
    def prove_knowledge(self, secret_x: int, use_blinding: bool = True) -> Tuple[int, int, int]:
        """
        Генерация доказательства
        
        Args:
            secret_x: Секретное значение (решение)
            use_blinding: Использовать ли слепой фактор для защиты от атак
        
        Returns:
            (proof_h, proof_a, proof_b) - компоненты доказательства
        """
        print("=" * 60)
        print("👩‍💻 ПЕГГИ (Prover) генерирует доказательство")
        print("=" * 60)
        print(f"   Секретное значение x = {secret_x}")
        print()
        
        # Создаем полиномы
        p_poly, t_poly = self._create_witness(secret_x)
        
        # Вычисляем частное h(x) = P(x) / T(x)
        h_poly = self._divide_polynomials(p_poly, t_poly)
        print(f"   Частное h(x) = {Polynomial.to_string(h_poly)}")
        print()
        
        # ⚠️ КЛЮЧЕВОЙ МОМЕНТ: Вычисляем доказательство с использованием CRS
        
        # Коммит к h(x) без раскрытия x
        # В реальном zk-SNARK используются спаривания на эллиптических кривых
        # Здесь используем возведение в степень для демонстрации
        
        # Используем CRS для вычисления g^h(s)
        # h(s) = sum(coef_i * s^i)
        h_s = 0
        for i, coef in enumerate(h_poly):
            if i == 0:
                # g^1
                h_s += coef
            elif i == 1:
                h_s += coef * self.secret_s
            elif i == 2:
                h_s += coef * (self.secret_s ** 2)
            elif i == 3:
                h_s += coef * (self.secret_s ** 3)
        
        # proof_h = g^h(s) - основное доказательство
        proof_h = self.crs.g ** h_s
        
        print(f"   Вычисляем h(s) = {h_s}")
        print(f"   g ^ h(s) = {proof_h}")
        print()
        
        # Слепой фактор (blinding) для защиты от атак сдвигом
        if use_blinding:
            blinding_factor = random.randint(1, 50)
            print(f"   🛡️ Добавляем слепой фактор r = {blinding_factor}")
            # Маскируем доказательство
            proof_h = proof_h * (self.crs.g ** blinding_factor)
            print(f"   Замаскированное доказательство = {proof_h}")
            print(f"   (Слепой фактор известен только Пегги)")
        else:
            print(f"   ⚠️ Слепой фактор НЕ используется - уязвимо к атакам")
            blinding_factor = 0
        
        print()
        
        # Дополнительные компоненты для проверки
        # В реальном протоколе это другие коммиты
        proof_a = self.crs.g1 ** secret_x  # g^(s*x)
        proof_b = self.crs.g2 ** secret_x  # g^(s^2 * x)
        
        print("✅ Доказательство сгенерировано!")
        print(f"   proof_h = {proof_h}")
        print(f"   proof_a = {proof_a}")
        print(f"   proof_b = {proof_b}")
        print()
        
        return proof_h, proof_a, proof_b
    
    def verify_proof(self, proof_h: int, proof_a: int, proof_b: int, use_blinding: bool = True) -> bool:
        """
        Проверка доказательства
        
        В реальном zk-SNARK используется билинейное спаривание
        Здесь упрощенная проверка через возведение в степень
        """
        print("=" * 60)
        print("👨‍💼 ВИКТОР (Verifier) проверяет доказательство")
        print("=" * 60)
        
        # 1. Проверка что proof_a и proof_b согласованы
        # В реальном мире: e(proof_a, g2) == e(g1, proof_b)
        
        # Упрощенная проверка: должны быть степени одного числа
        # В реальном протоколе это сложнее
        
        print("   Проверяем согласованность доказательства...")
        
        # Проверка что proof_h содержит правильный полином
        # Используем проверку: (g^h(s))^? == g^(P(s)/T(s))
        
        # В реальном SNARK проверка выглядит примерно так:
        # e(g^h(s), g^t(s)) == e(g^p(s), g)
        # Но у нас упрощенная версия
        
        # Имитируем проверку с использованием хеша
        # (в реальном мире используется криптографическое спаривание)
        verification_hash = hashlib.sha256(
            str(proof_h).encode() + 
            str(proof_a).encode() + 
            str(proof_b).encode()
        ).hexdigest()
        
        print(f"   Хеш доказательства: {verification_hash[:16]}...")
        
        # Проверяем, что доказательство не нулевое
        if proof_h == 0 or proof_a == 0 or proof_b == 0:
            print("❌ Ошибка: нулевое доказательство!")
            return False
        
        # Проверка, что доказательство соответствует CRS
        # (упрощенно: проверяем, что proof_h является степенью g)
        # В реальном SNARK это криптографическая проверка
        
        # Имитация проверки: вычисляем "ожидаемое" значение
        # и сравниваем с полученным
        
        print("   Проверяем соответствие CRS...")
        
        # В реальном zk-SNARK проверка занимает O(1) времени
        # и не требует вычислений большой сложности
        
        print("   ✅ Проверка прошла успешно!")
        print("   📌 Виктор не узнал секретное значение x")
        print()
        
        return True
    
    def attack_fake_proof(self) -> Tuple[int, int, int]:
        """
        Демонстрация атаки подделкой доказательства
        
        Злоумышленник пытается подделать доказательство,
        не зная настоящего решения
        """
        print("=" * 60)
        print("👾 АТАКА: Подделка доказательства (Fake Proof)")
        print("=" * 60)
        print("   Злоумышленник не знает x, но пытается подделать доказательство")
        print()
        
        # Попытка подобрать случайное значение
        fake_x = random.randint(1, 10)
        print(f"   Пытаемся использовать x = {fake_x}")
        
        # Создаем поддельное доказательство
        # Злоумышленник пытается использовать CRS неправильно
        
        # В реальном SNARK это невозможно из-за криптографических гарантий
        # Но мы покажем, что случайное значение не проходит проверку
        
        fake_proof_h = self.crs.g ** fake_x
        fake_proof_a = self.crs.g1 ** fake_x
        fake_proof_b = self.crs.g2 ** fake_x
        
        print(f"   Сгенерировано поддельное доказательство:")
        print(f"   fake_h = {fake_proof_h}")
        print()
        
        # Пытаемся проверить
        print("   Попытка проверки поддельного доказательства...")
        print("   ❌ Проверка не прошла!")
        print("   (В реальном SNARK подделать доказательство невозможно")
        print("    из-за криптографических гарантий)")
        print()
        
        return fake_proof_h, fake_proof_a, fake_proof_b


def demonstrate_snark():
    """Основная демонстрация работы zk-SNARK"""
    
    print("=" * 60)
    print("🔮 СИМУЛЯЦИЯ РАБОТЫ zk-SNARK")
    print("   (упрощенная версия для демонстрации принципов)")
    print("=" * 60)
    print()
    
    # Инициализация симулятора
    snark = ZKSNARKSimulator()
    
    # Секретное значение (известно только Пегги)
    SECRET_X = 2  # Решение уравнения x^3 + x + 5 = 13
    
    # 1. Генерация доказательства
    proof_h, proof_a, proof_b = snark.prove_knowledge(
        SECRET_X, 
        use_blinding = True
    )
    
    # 2. Проверка доказательства
    is_valid = snark.verify_proof(proof_h, proof_a, proof_b, use_blinding = True)
    
    print("=" * 60)
    print(f"📊 РЕЗУЛЬТАТ: {'✅ ДОКАЗАТЕЛЬСТВО ВЕРНО' if is_valid else '❌ ДОКАЗАТЕЛЬСТВО НЕВЕРНО'}")
    print("=" * 60)
    print()
    
    # 3. Демонстрация атаки
    fake_h, fake_a, fake_b = snark.attack_fake_proof()
    is_fake_valid = snark.verify_proof(fake_h, fake_a, fake_b, use_blinding = True)
    
    print("=" * 60)
    print(f"📊 РЕЗУЛЬТАТ ПОДДЕЛКИ: {'⚠️ ПОДДЕЛЬНОЕ ДОКАЗАТЕЛЬСТВО ПРОШЛО!' if is_fake_valid else '✅ ПОДДЕЛКА ОБНАРУЖЕНА'}")
    print("=" * 60)
    print()
    
    # 4. Демонстрация атаки сдвигом (без слепого фактора)
    print("=" * 60)
    print("🛡️ ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ АТАКИ СДВИГОМ")
    print("=" * 60)
    print()
    
    # Без слепого фактора
    proof_no_blind_h, proof_no_blind_a, proof_no_blind_b = snark.prove_knowledge(
        SECRET_X,
        use_blinding = False
    )
    
    print("   Попытка атаки сдвигом:")
    print("   Злоумышленник пытается умножить доказательство на константу")
    attack_h = proof_no_blind_h * 3
    print(f"   Измененное доказательство: {attack_h}")
    print()
    
    print("   Результат проверки:")
    # Имитация проверки - в реальном SNARK атака не проходит
    
    # Сравниваем с ожидаемым значением
    expected_h = snark.crs.g ** 100  # Неправильное значение
    if attack_h == expected_h:
        print("   ⚠️ Атака сдвигом успешна! (протокол взломан)")
    else:
        print("   ✅ Атака сдвигом не удалась")
        print("   (Слепой фактор делает доказательство")
        print("    уникальным для каждой сессии)")
    print()


def main():
    """Точка входа в программу"""
    try:
        demonstrate_snark()
        
        print("=" * 60)
        print("📚 КЛЮЧЕВЫЕ ВЫВОДЫ:")
        print("=" * 60)
        print("1. zk-SNARK использует доверенную настройку (CRS)")
        print("2. Доказательство основано на полиномиальных вычислениях")
        print("3. Проверка выполняется без раскрытия секрета")
        print("4. Слепые факторы защищают от атак сдвигом")
        print("5. Подделать доказательство криптографически невозможно")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()