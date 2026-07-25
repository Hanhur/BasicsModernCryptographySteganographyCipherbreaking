# Демонстрация интерактивного ZKP
import random
import math

class ZKPProtocol:
    """
    Реализация интерактивного протокола доказательства с нулевым разглашением
    на основе задачи дискретного логарифмирования (схема Шнорра)
    """
    
    def __init__(self, p = None, g = None):
        """
        Инициализация протокола с параметрами p и g
        Если параметры не заданы, генерируются автоматически
        """
        if p is None or g is None:
            self.p, self.g = self._generate_parameters()
        else:
            self.p = p
            self.g = g
            
        print(f"Открытые параметры:")
        print(f"  p = {self.p} (простое число)")
        print(f"  g = {self.g} (генератор)")
        print(f"  Разрядность p: {self.p.bit_length()} бит")
        print("-" * 60)
    
    def _is_prime(self, n, k = 10):
        """
        Тест Миллера-Рабина для проверки простоты числа
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        # Записываем n-1 как d * 2^s
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        
        # Проверяем k раз
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def _find_primitive_root(self, p):
        """
        Находит первообразный корень по модулю p
        """
        if p == 2:
            return 1
        
        # Факторизуем p-1
        factors = []
        temp = p - 1
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                factors.append(d)
                while temp % d == 0:
                    temp //= d
            d += 1 if d == 2 else 2  # Проверяем только 2 и нечетные числа
        
        if temp > 1:
            factors.append(temp)
        
        # Ищем первообразный корень
        for g in range(2, p):
            is_primitive = True
            for factor in factors:
                if pow(g, (p - 1) // factor, p) == 1:
                    is_primitive = False
                    break
            if is_primitive:
                return g
        return None
    
    def _generate_parameters(self, bits = 12):
        """
        Генерирует простое число p и первообразный корень g
        bits - количество бит для p (для демонстрации достаточно 12-16 бит)
        """
        while True:
            # Генерируем простое число
            p = random.randint(2 ** (bits - 1), 2 ** bits)
            if p % 2 == 0:
                p += 1
            while not self._is_prime(p):
                p += 2
            
            # Находим первообразный корень
            g = self._find_primitive_root(p)
            if g is not None:
                return p, g
    
    def peggy_generate_keypair(self, a = None):
        """
        Пегги генерирует пару ключей:
        a - секретный ключ (если не задан, генерируется случайно)
        B - открытый ключ
        """
        if a is None:
            # Генерируем случайный секретный ключ (1 < a < p-1)
            a = random.randint(2, self.p - 2)
        
        # Вычисляем открытый ключ: B = g^a mod p
        B = pow(self.g, a, self.p)
        
        print(f"Пегги (доказатель):")
        print(f"  Секретный ключ a = {a}")
        print(f"  Открытый ключ B = g ^ {a} mod {self.p} = {B}")
        print("-" * 60)
        
        return a, B
    
    def peggy_commit(self, k = None):
        """
        Шаг 1: Пегги выбирает случайное k и вычисляет обязательство V = g ^ k mod p
        """
        if k is None:
            k = random.randint(2, self.p - 2)
        
        V = pow(self.g, k, self.p)
        
        print(f"Шаг 1 - Обязательство:")
        print(f"  k = {k} (случайное секретное число)")
        print(f"  V = g ^ {k} mod {self.p} = {V}")
        print("-" * 60)
        
        return k, V
    
    def victor_challenge(self, r = None):
        """
        Шаг 2: Виктор выбирает случайный вызов r
        """
        if r is None:
            r = random.randint(1, self.p - 2)
        
        print(f"Шаг 2 - Вызов:")
        print(f"  r = {r} (случайное число от Виктора)")
        print("-" * 60)
        
        return r
    
    def peggy_respond(self, a, k, r):
        """
        Шаг 3: Пегги вычисляет ответ w = k - a * r mod (p - 1)
        """
        # Вычисляем w = k - a*r mod (p-1)
        w = (k - a * r) % (self.p - 1)
        
        print(f"Шаг 3 - Ответ:")
        print(f"  w = ({k} - {a} * {r}) mod {self.p - 1} = {w}")
        print("-" * 60)
        
        return w
    
    def victor_verify(self, V, B, r, w):
        """
        Шаг 4: Виктор проверяет, что V = g ^ w * B ^ r mod p
        """
        print(f"Шаг 4 - Проверка:")
        print(f"  Проверяем: g ^ {w} * {B} ^ {r} mod {self.p} == {V} ?")
        
        # Вычисляем левую часть: g^w * B^r mod p
        left_side = (pow(self.g, w, self.p) * pow(B, r, self.p)) % self.p
        
        print(f"  Результат: {left_side}")
        print(f"  Ожидалось: {V}")
        print(f"  Совпадает: {left_side == V}")
        print("-" * 60)
        
        return left_side == V
    
    def run_full_protocol(self, a = None, k = None, r = None, verbose = True):
        """
        Запускает полный протокол аутентификации
        """
        print("\n" + "=" * 60)
        print("ЗАПУСК ПРОТОКОЛА ZKP")
        print("=" * 60)
        
        # Пегги генерирует ключевую пару
        a, B = self.peggy_generate_keypair(a)
        
        # Шаг 1: Пегги отправляет обязательство
        k, V = self.peggy_commit(k)
        
        # Шаг 2: Виктор отправляет вызов
        r = self.victor_challenge(r)
        
        # Шаг 3: Пегги вычисляет ответ
        w = self.peggy_respond(a, k, r)
        
        # Шаг 4: Виктор проверяет
        is_valid = self.victor_verify(V, B, r, w)
        
        if is_valid:
            print("✅ АУТЕНТИФИКАЦИЯ УСПЕШНА! Пегги доказала знание секретного ключа.")
        else:
            print("❌ АУТЕНТИФИКАЦИЯ ПРОВАЛЕНА! Проверка не прошла.")
        
        print("=" * 60 + "\n")
        
        return {
            'a': a,
            'B': B,
            'k': k,
            'V': V,
            'r': r,
            'w': w,
            'is_valid': is_valid
        }
    
    def demonstrate_attack(self):
        """
        Демонстрирует, что злоумышленник не может обмануть Виктора
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ПОПЫТКИ ОБМАНА")
        print("=" * 60)
        print("Злоумышленник (Ева) не знает секретный ключ a,")
        print("но пытается выдать себя за Пегги.")
        print("-" * 60)
        
        # Ева не знает a, но знает открытый ключ B
        # Настоящая Пегги ранее опубликовала B
        a_real, B = self.peggy_generate_keypair()
        print(f"Ева знает открытый ключ B = {B}, но не знает a = {a_real}")
        print("-" * 60)
        
        # Ева пытается подделать ответ
        # Она может выбрать случайные V и w, и надеяться, что они подойдут
        print("Ева пытается обмануть:")
        
        # Вариант 1: Ева выбирает случайные значения
        fake_k = random.randint(2, self.p - 2)
        fake_V = pow(self.g, fake_k, self.p)
        
        # Виктор отправляет случайный r
        r = random.randint(1, self.p - 2)
        print(f"Виктор отправляет r = {r}")
        
        # Ева не может вычислить правильный w, потому что не знает a
        # Она может попытаться угадать w или подобрать
        fake_w = random.randint(2, self.p - 2)
        print(f"Ева отправляет w = {fake_w} (случайное число)")
        
        # Проверка Виктора
        print(f"\nВиктор проверяет: g ^ {fake_w} * {B} ^ {r} mod {self.p} == {fake_V} ?")
        left_side = (pow(self.g, fake_w, self.p) * pow(B, r, self.p)) % self.p
        
        print(f"  Результат: {left_side}")
        print(f"  Ожидалось: {fake_V}")
        print(f"  Совпадает: {left_side == fake_V}")
        
        if left_side != fake_V:
            print("❌ ВИКТОР ОТКЛОНИЛ АУТЕНТИФИКАЦИЮ! Обман не удался.")
            print("\nПочему обман невозможен?")
            print("  Уравнение: V = g ^ w * B ^ r mod p")
            print("  B = g ^ a, поэтому V = g ^ w * g ^ (a * r) = g ^ (w + a * r) mod p")
            print("  Еве нужно, чтобы w + a * r = k (для некоторого k)")
            print("  Но a неизвестно, поэтому Ева не может подобрать правильный w")
            print("  для произвольного r, не зная a!")
        
        print("=" * 60 + "\n")


def run_demo_with_small_numbers():
    """
    Демонстрация с небольшими числами, как в примере из текста
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ С КОНКРЕТНЫМИ ЧИСЛАМИ")
    print("=" * 60)
    print("Используем числа из примера: p = 1987, g = 3, a = 17")
    print("=" * 60)
    
    # Создаем протокол с конкретными параметрами
    protocol = ZKPProtocol(p = 1987, g = 3)
    
    # Запускаем протокол с конкретными числами
    # a=17, k=67, r=37 - как в примере
    result = protocol.run_full_protocol(a = 17, k = 67, r = 37)
    
    return result


def run_demo_with_large_numbers():
    """
    Демонстрация с большими числами (реалистичный сценарий)
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ С БОЛЬШИМИ ЧИСЛАМИ")
    print("=" * 60)
    print("Генерируем 16-битное простое число (для скорости)")
    print("В реальных системах используются 2048-битные числа")
    print("=" * 60)
    
    # Генерируем параметры с 16-битным простым числом
    protocol = ZKPProtocol()
    
    # Запускаем протокол со случайными ключами
    result = protocol.run_full_protocol()
    
    return result


def demonstrate_multiple_sessions():
    """
    Демонстрация нескольких сессий протокола
    """
    print("=" * 60)
    print("МНОЖЕСТВЕННЫЕ СЕССИИ АУТЕНТИФИКАЦИИ")
    print("=" * 60)
    print("Пегги проходит аутентификацию 3 раза с разными случайными числами")
    print("=" * 60)
    
    protocol = ZKPProtocol(p = 1987, g = 3)
    a, B = protocol.peggy_generate_keypair(a = 17)
    
    results = []
    for session in range(1, 4):
        print(f"\n--- Сессия {session} ---")
        k = random.randint(2, protocol.p - 2)
        r = random.randint(1, protocol.p - 2)
        result = protocol.run_full_protocol(a = a, k = k, r = r, verbose = True)
        results.append(result)
    
    print("\nВсе сессии успешно завершены!")
    print(f"Секретный ключ a = {a} остался неизвестным для Виктора")
    print("=" * 60 + "\n")


def main():
    """
    Главная функция с выбором демонстрации
    """
    print("\n" + "█" * 70)
    print("█" + " " * 20 + "ПРОТОКОЛ ZKP (СХЕМА ШНОРРА)" + " " * 21 + "█")
    print("█" * 70)
    print("\nПрограмма демонстрирует интерактивное доказательство")
    print("с нулевым разглашением на основе дискретного логарифма.\n")
    
    # Меню выбора
    while True:
        print("\nВыберите демонстрацию:")
        print("  1. Пример с числами из текста (p = 1987, g = 3, a = 17)")
        print("  2. Случайные числа (16-битный модуль)")
        print("  3. Множественные сессии аутентификации")
        print("  4. Демонстрация попытки обмана")
        print("  5. Выход")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == '1':
            run_demo_with_small_numbers()
        elif choice == '2':
            run_demo_with_large_numbers()
        elif choice == '3':
            demonstrate_multiple_sessions()
        elif choice == '4':
            protocol = ZKPProtocol(p = 1987, g = 3)
            protocol.demonstrate_attack()
        elif choice == '5':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    # Для воспроизводимости результатов
    random.seed(42)
    main()