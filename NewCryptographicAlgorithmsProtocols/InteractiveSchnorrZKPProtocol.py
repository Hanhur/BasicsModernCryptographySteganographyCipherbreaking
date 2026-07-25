# Интерактивный протокол ZKP Шнорра
"""
Интерактивный протокол ZKP Шнорра
Реализация на чистом Python без использования numpy
"""

import random
import math

class Peggy:
    """Доказывающая сторона (Пегги)"""
    
    def __init__(self, p, g, a):
        """
        Инициализация Пегги
        
        Args:
            p: большое простое число
            g: образующий элемент группы Zp
            a: секретное число (пароль)
        """
        self.p = p
        self.g = g
        self.a = a  # Секретное число
        
        # Вычисляем открытый ключ B = g^a mod p
        self.B = pow(g, a, p)
        print(f"[Пегги] Сгенерирован открытый ключ B = {self.B}")
        print(f"[Пегги] Секрет a = {self.a} (не разглашается!)")
    
    def step1_commitment(self):
        """
        Шаг 1: Пегги выбирает случайное k и вычисляет V = g ^ k mod p
        
        Returns:
            V: обязательство (commitment)
        """
        # Выбираем случайное k: 1 <= k < p-1
        self.k = random.randint(1, self.p - 2)
        
        # Вычисляем V = g^k mod p
        self.V = pow(self.g, self.k, self.p)
        
        print(f"[Пегги] Шаг 1: Выбрано k = {self.k}, вычислено V = {self.V}")
        print(f"[Пегги] Отправляю V Виктору...")
        
        return self.V
    
    def step3_response(self, r):
        """
        Шаг 3: Пегги получает случайное r от Виктора и вычисляет w
        
        Args:
            r: случайное число от Виктора
            
        Returns:
            w: ответ Пегги
        """
        # Вычисляем w = (k - a * r) mod (p - 1)
        self.w = (self.k - self.a * r) % (self.p - 1)
        
        print(f"[Пегги] Шаг 3: Получено r = {r}")
        print(f"[Пегги] Вычислено w = {self.w}")
        print(f"[Пегги] Отправляю w Виктору...")
        
        return self.w


class Victor:
    """Проверяющая сторона (Виктор)"""
    
    def __init__(self, p, g, B):
        """
        Инициализация Виктора
        
        Args:
            p: большое простое число
            g: образующий элемент группы Zp
            B: открытый ключ Пегги
        """
        self.p = p
        self.g = g
        self.B = B
        
        print(f"[Виктор] Инициализирован с открытыми параметрами:")
        print(f"        p = {p}, g = {g}, B = {B}")
    
    def step2_challenge(self):
        """
        Шаг 2: Виктор выбирает случайное r и отправляет его Пегги
        
        Returns:
            r: случайный челлендж
        """
        # Выбираем случайное r: 1 <= r < p-1
        self.r = random.randint(1, self.p - 2)
        
        print(f"[Виктор] Шаг 2: Выбрано случайное r = {self.r}")
        print(f"[Виктор] Отправляю r Пегги...")
        
        return self.r
    
    def step4_verify(self, V, w):
        """
        Шаг 4: Виктор проверяет доказательство
        
        Args:
            V: обязательство от Пегги
            w: ответ Пегги
            
        Returns:
            bool: True если доказательство верное, иначе False
        """
        print(f"[Виктор] Шаг 4: Проверка доказательства...")
        print(f"        V = {V}, w = {w}, r = {self.r}")
        
        # Вычисляем левую часть: g^w * B^r mod p
        left_side = (pow(self.g, w, self.p) * pow(self.B, self.r, self.p)) % self.p
        
        # Правая часть - это V
        right_side = V
        
        print(f"        g ^ w * B ^ r mod p = {left_side}")
        print(f"        V = {right_side}")
        
        if left_side == right_side:
            print("[Виктор] ✅ Доказательство ПРИНЯТО! Пегги знает секрет a.")
            return True
        else:
            print("[Виктор] ❌ Доказательство ОТКЛОНЕНО! Пегги не знает секрет.")
            return False


def is_prime(n):
    """Проверка числа на простоту (для небольших чисел)"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_primitive_root(g, p):
    """
    Проверка, является ли g образующим элементом группы Zp
    Для простого p: g является образующим, если g ^ ((p - 1) / q) != 1 mod p
    для всех простых делителей q числа (p - 1)
    """
    if g == 0 or g == 1:
        return False
    
    # Находим простые делители p-1
    phi = p - 1
    factors = []
    n = phi
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
        i += 1
    if n > 1:
        factors.append(n)
    
    # Проверяем условие для каждого простого делителя
    for factor in factors:
        if pow(g, phi // factor, p) == 1:
            return False
    return True

def find_primitive_root(p):
    """Находит образующий элемент для простого числа p"""
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    return None


def run_protocol(p, g, a):
    """
    Запуск интерактивного протокола Шнорра
    
    Args:
        p: большое простое число
        g: образующий элемент
        a: секретное число (пароль)
    """
    print("=" * 70)
    print("ЗАПУСК ИНТЕРАКТИВНОГО ПРОТОКОЛА ШНОРРА")
    print("=" * 70)
    print(f"Открытые параметры: p = {p}, g = {g}")
    print(f"Секрет Пегги: a = {a}")
    print("-" * 70)
    
    # Создаём участников
    peggy = Peggy(p, g, a)
    victor = Victor(p, g, peggy.B)
    
    print("-" * 70)
    
    # Шаг 1: Пегги отправляет V
    V = peggy.step1_commitment()
    
    # Шаг 2: Виктор отправляет r
    r = victor.step2_challenge()
    
    # Шаг 3: Пегги вычисляет w
    w = peggy.step3_response(r)
    
    # Шаг 4: Виктор проверяет
    print("-" * 70)
    result = victor.step4_verify(V, w)
    
    print("=" * 70)
    return result


def main():
    """Основная функция с демонстрацией различных сценариев"""
    
    print("ИНТЕРАКТИВНЫЙ ПРОТОКОЛ ZKP ШНОРРА")
    print("=" * 70)
    
    # Выбираем простое число и образующий элемент
    # Для демонстрации возьмём небольшое простое число
    
    # Вариант 1: Простое число 23 (как в примере)
    p1 = 23
    g1 = 5  # 5 - образующий для 23
    
    print("\n--- СЦЕНАРИЙ 1: Честная Пегги (знает секрет) ---")
    a1 = 7  # Секрет
    success = run_protocol(p1, g1, a1)
    print(f"Результат: {'УСПЕШНО' if success else 'ПРОВАЛ'}\n")
    
    # Вариант 2: Попытка обмана (Пегги не знает секрет)
    print("\n--- СЦЕНАРИЙ 2: Недобросовестная Пегги (не знает секрет) ---")
    print("[!] Пегги пытается выдать себя за знающую секрет...")
    
    # Создаём "злую" Пегги с другим секретом
    p2 = 23
    g2 = 5
    a_wrong = 3  # Неправильный секрет (не совпадает с публичным ключом)
    
    # Симулируем, что у Виктора уже есть публичный ключ от настоящей Пегги
    # (настоящий секрет 7, но злая Пегги использует 3)
    print("[!] У Виктора есть публичный ключ B = 17 (от настоящей Пегги с a = 7)")
    print("[!] Злая Пегги пытается доказать знание a, используя a = 3")
    
    # Виктор использует правильный B
    peggy_evil = Peggy(p2, g2, a_wrong)
    victor2 = Victor(p2, g2, 17)  # Используем правильный B от a=7
    
    V_evil = peggy_evil.step1_commitment()
    r2 = victor2.step2_challenge()
    w_evil = peggy_evil.step3_response(r2)
    result_evil = victor2.step4_verify(V_evil, w_evil)
    print(f"Результат: {'УСПЕШНО' if result_evil else 'ПРОВАЛ'}")
    print("[!] Как и ожидалось, Виктор отклонил доказательство!\n")
    
    # Вариант 3: Демонстрация с большим простым числом
    print("\n--- СЦЕНАРИЙ 3: Демонстрация с большим простым числом ---")
    # Простое число 101
    p3 = 101
    g3 = 2  # 2 - образующий для 101
    a3 = 42
    
    print(f"[!] Используем p = {p3} (больше для демонстрации)")
    success = run_protocol(p3, g3, a3)
    print(f"Результат: {'УСПЕШНО' if success else 'ПРОВАЛ'}")
    
    # Вариант 4: Автоматический поиск параметров
    print("\n--- СЦЕНАРИЙ 4: Автоматическая генерация параметров ---")
    # Ищем простое число и образующий
    p_candidates = [97, 101, 103, 107, 109, 113]
    for p in p_candidates:
        if is_prime(p):
            g = find_primitive_root(p)
            if g:
                print(f"Найдены параметры: p = {p}, g = {g}")
                a = random.randint(2, p - 2)
                success = run_protocol(p, g, a)
                print(f"Результат: {'✅ УСПЕШНО' if success else '❌ ПРОВАЛ'}\n")
                break
    
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)


if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов (опционально)
    random.seed(42)
    
    main()