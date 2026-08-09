# Особенности алгоритма MBXI и предисловие к атаке на RSA
"""
Реализация алгоритма MBXI (Modular Binary eXponentiation with Inversion)
на основе описанного в тексте примера.
Без использования numpy - только встроенные возможности Python.
"""

import math
import random

def egcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), где g = НОД(a, b), а x и y - коэффициенты Безу.
    """
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1

def modinv(a, m):
    """
    Вычисление обратного числа по модулю m.
    Возвращает x, такой что a * x ≡ 1 (mod m).
    """
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного числа для {a} по модулю {m} не существует (НОД = {g})")
    return x % m

def mod_pow(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю (бинарный метод).
    base^exponent mod modulus
    """
    if modulus == 1:
        return 0
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result

class MBXI:
    """
    Класс, реализующий алгоритм MBXI.
    """
    
    def __init__(self, p, fixed_part = 7036543210):
        """
        Инициализация системы MBXI.
        
        Аргументы:
        - p: большое открытое простое число (модуль)
        - fixed_part: фиксированная часть для вычисления A (из текста)
        """
        self.p = p
        self.fixed_part = fixed_part
        self.p_minus_1 = p - 1
        self.eB = None
        self.A = None
        self.x = None  # секретный ключ
    
    def generate_key(self, eB_range = (1, 10)):
        """
        Генерация ключей MBXI с поиском подходящего eB.
        
        Возвращает:
        - eB: подобранный параметр (открытый)
        - x: секретный ключ
        - A: промежуточное значение (для демонстрации)
        """
        print(f"\n=== Генерация ключей MBXI ===")
        print(f"p = {self.p}, p-1 = {self.p_minus_1}")
        
        for eB in range(eB_range[0], eB_range[1] + 1):
            self.eB = eB
            self.A = (self.fixed_part + eB) % self.p
            
            print(f"\nПопытка eB = {eB}:")
            print(f"  A = ({self.fixed_part} + {eB}) mod {self.p} = {self.A}")
            
            # Проверка взаимной простоты A и (p-1)
            gcd_val = math.gcd(self.A, self.p_minus_1)
            print(f"  НОД({self.A}, {self.p_minus_1}) = {gcd_val}")
            
            if gcd_val == 1:
                try:
                    self.x = modinv(self.A, self.p_minus_1)
                    print(f"  ✓ УСПЕХ! Обратное число x = {self.x}")
                    print(f"  Проверка: {self.A} * {self.x} ≡ 1 (mod {self.p_minus_1})")
                    return eB, self.x, self.A
                except ValueError as e:
                    print(f"  Ошибка: {e}")
            else:
                print(f"  ✗ НЕ УДАЛОСЬ: числа не взаимно просты")
        
        raise RuntimeError("Не удалось найти подходящее eB в заданном диапазоне")
    
    def encrypt(self, M, eB = None):
        """
        Шифрование сообщения M.
        
        Аргументы:
        - M: исходное сообщение (целое число)
        - eB: параметр шифрования (если None, используется последний сгенерированный)
        
        Возвращает:
        - C: шифротекст
        - x: использованный секретный ключ
        - eB: использованный параметр
        """
        if eB is None:
            eB = self.eB
            if eB is None:
                raise ValueError("Сначала необходимо сгенерировать ключи методом generate_key()")
        
        # Находим x по eB (если он не совпадает с текущим)
        if eB != self.eB or self.x is None:
            A = (self.fixed_part + eB) % self.p
            if math.gcd(A, self.p_minus_1) != 1:
                raise ValueError(f"eB = {eB} не подходит: НОД({A}, {self.p_minus_1}) != 1")
            x = modinv(A, self.p_minus_1)
        else:
            x = self.x
            A = self.A
        
        print(f"\n=== Шифрование ===")
        print(f"M = {M}")
        print(f"x = {x} (секретный ключ)")
        print(f"p = {self.p}")
        print(f"Формула: C ≡ {M} ^ {x} (mod {self.p})")
        
        C = mod_pow(M, x, self.p)
        
        print(f"C = {C}")
        
        return C, x, eB
    
    def decrypt(self, C, eB, x = None):
        """
        Расшифровка сообщения C.
        
        Аргументы:
        - C: шифротекст
        - eB: параметр шифрования
        - x: секретный ключ (если None, вычисляется из eB)
        
        Возвращает:
        - M: расшифрованное сообщение
        """
        print(f"\n=== Расшифровка ===")
        print(f"C = {C}")
        print(f"eB = {eB}")
        
        if x is None:
            A = (self.fixed_part + eB) % self.p
            if math.gcd(A, self.p_minus_1) != 1:
                raise ValueError(f"eB = {eB} не подходит для расшифровки")
            x = modinv(A, self.p_minus_1)
            print(f"Вычислен x = {x} из eB = {eB}")
        else:
            print(f"Используется переданный x = {x}")
        
        print(f"Формула: M ≡ {C} ^ {{x}} (mod {self.p})")
        
        M = mod_pow(C, x, self.p)
        
        print(f"M = {M}")
        
        return M
    
    def demo_full_cycle(self, M):
        """
        Демонстрация полного цикла: генерация ключей -> шифрование -> расшифровка.
        
        Возвращает кортеж (исходное_сообщение, шифротекст, расшифрованное_сообщение, eB, x)
        """
        print(f"\n{'=' * 60}")
        print(f"ДЕМОНСТРАЦИЯ ПОЛНОГО ЦИКЛА MBXI")
        print(f"Исходное сообщение M = {M}")
        print(f"{'=' * 60}")
        
        # 1. Генерация ключей
        eB, x, A = self.generate_key()
        
        # 2. Шифрование
        C, used_x, used_eB = self.encrypt(M, eB)
        
        # 3. Формирование тройки для передачи
        KB = 4997  # K_B из текста (может быть любым числом)
        print(f"\n=== Передача ===")
        print(f"Боб передает Алисе тройку: (C, K_B, eB) = ({C}, {KB}, {used_eB})")
        
        # 4. Расшифровка
        M_decrypted = self.decrypt(C, used_eB, used_x)
        
        # 5. Проверка
        print(f"\n=== Проверка ===")
        print(f"Исходное сообщение: {M}")
        print(f"Расшифрованное сообщение: {M_decrypted}")
        print(f"Успешно: {M == M_decrypted}")
        
        return M, C, M_decrypted, used_eB, used_x


def main():
    """
    Основная функция с демонстрацией всех примеров из текста.
    """
    print("=" * 60)
    print("РЕАЛИЗАЦИЯ АЛГОРИТМА MBXI")
    print("=" * 60)
    
    # Параметры из текста
    p = 7919
    fixed_part = 7036543210
    
    # Создание экземпляра MBXI
    mbxi = MBXI(p, fixed_part)
    
    # ------------------------------------------------------------
    # ПРИМЕР 1: Проверка eB = 6 (неудачная попытка)
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 1: Проверка eB = 6 (должна провалиться)")
    print(f"{'#' * 60}")
    
    mbxi_fail = MBXI(p, fixed_part)
    try:
        # Принудительно проверяем eB = 6
        eB_test = 6
        A_test = (fixed_part + eB_test) % p
        print(f"eB = {eB_test}")
        print(f"A = ({fixed_part} + {eB_test}) mod {p} = {A_test}")
        gcd_test = math.gcd(A_test, p - 1)
        print(f"НОД({A_test}, {p-1}) = {gcd_test}")
        
        if gcd_test != 1:
            print(f"✗ ОШИБКА: обратного числа не существует (как и сказано в тексте)")
            print("  Reduce[4960*x == 1, x, Modulus -> 7918] = False")
        else:
            x_test = modinv(A_test, p - 1)
            print(f"  x = {x_test}")
    except Exception as e:
        print(f"  Исключение: {e}")
    
    # ------------------------------------------------------------
    # ПРИМЕР 2: Проверка eB = 7 (успешная попытка)
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 2: Проверка eB = 7 (должна быть успешной)")
    print(f"{'#' * 60}")
    
    mbxi_success = MBXI(p, fixed_part)
    eB_test = 7
    A_test = (fixed_part + eB_test) % p
    print(f"eB = {eB_test}")
    print(f"A = ({fixed_part} + {eB_test}) mod {p} = {A_test}")
    gcd_test = math.gcd(A_test, p - 1)
    print(f"НОД({A_test}, {p - 1}) = {gcd_test}")
    
    if gcd_test == 1:
        x_test = modinv(A_test, p - 1)
        print(f"✓ УСПЕХ! x = {x_test}")
        print(f"  Проверка: {A_test} * {x_test} = {A_test * x_test}")
        print(f"  {A_test} * {x_test} mod {p - 1} = {(A_test * x_test) % (p - 1)}")
    
    # ------------------------------------------------------------
    # ПРИМЕР 3: Полный цикл шифрования с M = 88 (из текста)
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 3: Полный цикл с M = 88 (как в тексте)")
    print(f"{'#' * 60}")
    
    mbxi_main = MBXI(p, fixed_part)
    
    # Генерация ключей с автоматическим поиском eB
    eB, x, A = mbxi_main.generate_key()
    
    # Шифрование
    M = 88
    C, used_x, used_eB = mbxi_main.encrypt(M, eB)
    
    # В тексте указано C = 2195, проверяем
    print(f"\n  Ожидаемый шифротекст из текста: 2195")
    print(f"  Полученный шифротекст: {C}")
    print(f"  Совпадает: {C == 2195}")
    
    # Расшифровка
    M_dec = mbxi_main.decrypt(C, used_eB, used_x)
    print(f"\n  Ожидаемое сообщение: 88")
    print(f"  Полученное сообщение: {M_dec}")
    print(f"  Совпадает: {M_dec == 88}")
    
    # ------------------------------------------------------------
    # ПРИМЕР 4: Особенность M = 1 (C всегда равно 1)
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 4: Особенность M = 1")
    print(f"{'#' * 60}")
    
    mbxi_one = MBXI(p, fixed_part)
    eB_one, x_one, _ = mbxi_one.generate_key()
    
    C1 = mbxi_one.encrypt(1, eB_one)[0]
    print(f"\n  M = 1, C = {C1}")
    print(f"  C всегда равно 1 независимо от ключа: {C1 == 1}")
    
    # ------------------------------------------------------------
    # ПРИМЕР 5: Сравнение с RSA (демонстрация инверсии параметров)
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 5: Сравнение MBXI и RSA")
    print(f"{'#' * 60}")
    
    print("\n  RSA:     C ≡ M^e (mod N)   где e - открытый, N - открытый")
    print("  MBXI:    C ≡ M^x (mod p)    где x - секретный, p - открытый")
    print("\n  В MBXI секретным является ПОКАЗАТЕЛЬ СТЕПЕНИ (x),")
    print("  а в RSA - модуль N (точнее, его множители p и q)")
    print("  Это главное отличие и основа для атак, описанных в тексте")
    
    # ------------------------------------------------------------
    # ПРИМЕР 6: Атака на основе предсказуемого сообщения
    # ------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("ПРИМЕР 6: Уязвимость при M = 1 (атака)")
    print(f"{'#' * 60}")
    
    print("\n  Если злоумышленник знает, что M = 1,")
    print("  то C = 1 ^ x mod p = 1 ВСЕГДА")
    print("  Это делает шифрование бессмысленным,")
    print("  так как шифротекст не зависит от ключа!")
    print("\n  Именно поэтому в реальных криптосистемах")
    print("  используются ПАДДИНГИ (дополнения) сообщений")


if __name__ == "__main__":
    main()