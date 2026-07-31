# Демонстрация атаки на протокол zk-SNARK
import random
import hashlib

class SchnorrProtocol:
    """
    Реализация протокола идентификации Шнорра с демонстрацией атаки посредника
    """
    
    def __init__(self, p, g, x):
        """
        Инициализация протокола
        
        Args:
            p: простое число (модуль)
            g: генератор группы
            x: секретный ключ Анны (private key)
        """
        self.p = p
        self.g = g
        self.x = x
        self.p_minus_1 = p - 1
        
        # Открытый ключ Анны (public key)
        self.y = pow(g, x, p)
        
        print(f"=== ПАРАМЕТРЫ СИСТЕМЫ ===")
        print(f"p = {p}")
        print(f"g = {g}")
        print(f"x (секретный ключ Анны) = {x}")
        print(f"y (открытый ключ Анны) = {self.y}")
        print("=" * 40)
    
    def hash_function(self, g, y, t):
        """
        Простая хеш-функция для демонстрации
        
        В реальных протоколах используется SHA-256, но для наглядности мы берем остаток от деления на (p - 1)
        """
        # Конкатенируем значения и хешируем
        data = f"{g}{y}{t}".encode()
        hash_bytes = hashlib.sha256(data).digest()
        # Преобразуем в число и берем по модулю (p-1)
        hash_int = int.from_bytes(hash_bytes, 'big') % (self.p - 1)
        return hash_int if hash_int > 0 else 1
    
    def anna_commit(self, v):
        """
        Анна: первый шаг - отправка коммитмента
        
        Args:
            v: случайное число (nonce)
        
        Returns:
            t: коммитмент
        """
        t = pow(self.g, v, self.p)
        print(f"\n--- Анна выбирает v = {v} ---")
        print(f"t = g ^ v mod p = {self.g} ^ {v} mod {self.p} = {t}")
        return t
    
    def anna_response(self, v, c):
        """
        Анна: второй шаг - вычисление ответа r
        
        Args:
            v: случайное число (nonce)
            c: челлендж от Карла (или хеш)
        
        Returns:
            r: ответ
        """
        r = (v - c * self.x) % (self.p - 1)
        print(f"r = (v - c * x) mod (p - 1) = ({v} - {c} * {self.x}) mod {self.p - 1} = {r}")
        return r
    
    def carl_verify(self, r, t, c, y = None, g = None, p = None):
        """
        Карл: верификация доказательства
        
        Проверяет: g ^ r * y ^ c ≡ t (mod p)
        
        Args:
            r: ответ Анны
            t: коммитмент
            c: челлендж
            y: открытый ключ (если None, используется y Анны)
            g: генератор (если None, используется g Анны)
            p: модуль (если None, используется p Анны)
        
        Returns:
            bool: результат верификации
        """
        if y is None:
            y = self.y
        if g is None:
            g = self.g
        if p is None:
            p = self.p
        
        # Вычисляем левую часть: g^r * y^c mod p
        left_side = (pow(g, r, p) * pow(y, c, p)) % p
        
        # Правая часть: t
        right_side = t % p
        
        is_valid = (left_side == right_side)
        
        print(f"\n=== ВЕРИФИКАЦИЯ КАРЛА ===")
        print(f"Проверка: g ^ r * y ^ c ≡ t (mod p)")
        print(f"Левая часть: {self.g} ^ {r} * {y} ^ {c} mod {p} = {left_side}")
        print(f"Правая часть (t): {right_side}")
        print(f"Результат: {'✅ УСПЕШНО' if is_valid else '❌ ПРОВАЛ'}")
        
        return is_valid
    
    def honest_protocol_demo(self, v, c = None):
        """
        Демонстрация честного протокола
        
        Args:
            v: случайное число Анны
            c: челлендж (если None, вычисляется как хеш)
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ЧЕСТНОГО ПРОТОКОЛА (АННА → КАРЛ)")
        print("=" * 60)
        
        # Шаг 1: Анна вычисляет t
        t = self.anna_commit(v)
        
        # Шаг 2: Карл (или хеш) вычисляет c
        if c is None:
            c = self.hash_function(self.g, self.y, t)
            print(f"c = H(g, y, t) = {c}")
        else:
            print(f"c = {c} (задан вручную)")
        
        # Шаг 3: Анна вычисляет r
        r = self.anna_response(v, c)
        
        # Шаг 4: Карл верифицирует
        result = self.carl_verify(r, t, c)
        
        return {
            'v': v,
            't': t,
            'c': c,
            'r': r,
            'valid': result
        }
    
    def eve_attack_demo(self, v1):
        """
        Демонстрация атаки Евы (человек-посредник)
        
        Args:
            v1: произвольное число, выбранное Евой
        """
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ АТАКИ ЕВЫ (MAN-IN-THE-MIDDLE)")
        print("=" * 60)
        
        print(f"\n--- Ева перехватывает коммуникацию ---")
        print(f"Ева выбирает v1 = {v1}")
        
        # Ева вычисляет t1
        t1 = pow(self.g, v1, self.p)
        print(f"t1 = g ^ v1 mod p = {self.g} ^ {v1} mod {self.p} = {t1}")
        
        # Ева устанавливает c1 = p - 1 (ключевой момент атаки!)
        c1 = self.p - 1
        print(f"c1 = p - 1 = {c1}")
        
        # Ева устанавливает r1 = v1
        r1 = v1
        print(f"r1 = v1 = {r1}")
        
        print(f"\n--- Ева отправляет Карлу (r1, t1, c1) = ({r1}, {t1}, {c1}) ---")
        print(f"Открытый ключ y = {self.y} (не изменен)")
        
        # Карл верифицирует поддельные данные
        print(f"\n--- Карл проверяет данные от Евы ---")
        result = self.carl_verify(r1, t1, c1)
        
        # Математическое объяснение
        print(f"\n--- МАТЕМАТИЧЕСКОЕ ОБЪЯСНЕНИЕ ---")
        print(f"По малой теореме Ферма: y ^ (p - 1) ≡ 1 (mod p)")
        print(f"Проверка: g ^ {r1} * y ^ {c1} = g ^ {v1} * y ^ {{p - 1}} ≡ g ^ {v1} * 1 = t1 (mod p)")
        print(f"✅ Уравнение выполняется, даже не зная секретного ключа x!")
        
        return {
            'v1': v1,
            't1': t1,
            'c1': c1,
            'r1': r1,
            'valid': result
        }
    
    def secure_protocol_with_hash_demo(self, v):
        """
        Демонстрация защищенного протокола (с хешированием)
        
        Показывает, почему атака Евы не работает,
        если Карл сам вычисляет c через хеш
        """
        print("\n" + "=" * 60)
        print("ЗАЩИЩЕННЫЙ ПРОТОКОЛ (ЕВА НЕ МОЖЕТ ПОДМЕНИТЬ C)")
        print("=" * 60)
        
        # Анна отправляет t
        t = pow(self.g, v, self.p)
        print(f"\nАнна отправляет Карлу t = {t}")
        
        # Карл вычисляет c сам
        c_real = self.hash_function(self.g, self.y, t)
        print(f"Карл вычисляет c = H(g, y, t) = {c_real}")
        
        # Ева перехватывает и пытается подменить t
        v1 = random.randint(2, 100)
        t1 = pow(self.g, v1, self.p)
        print(f"\nЕва пытается подменить t = {t} на t1 = {t1}")
        print(f"Ева хочет установить c1 = p - 1 = {self.p - 1}")
        
        # Но Карл вычисляет c1 через хеш от t1!
        c1_from_hash = self.hash_function(self.g, self.y, t1)
        print(f"Карл вычисляет c1 = H(g, y, t1) = {c1_from_hash}")
        
        if c1_from_hash == self.p - 1:
            print("⚠️  Случайно совпало! (вероятность крайне мала)")
        else:
            print(f"❌ c1 = {c1_from_hash} ≠ p - 1 = {self.p - 1}")
            print(f"   Атака проваливается, так как c нельзя подменить!")
        
        # Пытаемся подобрать r1
        print(f"\nПытаемся найти r1, чтобы g ^ r1 * y ^ {c1_from_hash} = t1")
        print("Это эквивалентно нахождению дискретного логарифма - вычислительно невозможно!")
        
        return {
            't_original': t,
            'c_real': c_real,
            't1': t1,
            'c1_from_hash': c1_from_hash,
            'attack_failed': c1_from_hash != self.p - 1
        }


def main():
    """
    Главная функция с числовым примером из вашего текста
    """
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА ШНОРРА И АТАКИ ПОСРЕДНИКА")
    print("=" * 70)
    
    # Параметры из вашего примера
    p = 3571
    g = 7
    x = 23
    
    # Создаем экземпляр протокола
    protocol = SchnorrProtocol(p, g, x)
    
    # 1. Честный протокол (как в вашем примере)
    print("\n" + "🔵" * 35)
    protocol.honest_protocol_demo(v = 67, c = 37)
    
    # 2. Атака Евы (как в вашем примере)
    print("\n" + "🔴" * 35)
    protocol.eve_attack_demo(v1 = 57)
    
    # 3. Почему атака не работает в реальных системах
    print("\n" + "🟢" * 35)
    print("\n*** ПОЧЕМУ ЭТА АТАКА НЕ ПРОХОДИТ В РЕАЛЬНЫХ СИСТЕМАХ ***")
    print("В реальных протоколах Карл САМ вычисляет c = H(g, y, t)\n")
    
    v_secure = random.randint(10, 100)
    protocol.secure_protocol_with_hash_demo(v = v_secure)
    
    # 4. Дополнительно: проверка разных сценариев
    print("\n" + "📊" * 35)
    print("\nДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ")
    print("=" * 70)
    
    # Тест 1: Случайный челлендж
    print("\nТест 1: Честный протокол со случайным v и вычисленным c")
    v_random = random.randint(2, 1000)
    protocol.honest_protocol_demo(v = v_random)
    
    # Тест 2: Атака с другим v1
    print("\nТест 2: Атака Евы с другим v1")
    v1_random = random.randint(2, 100)
    protocol.eve_attack_demo(v1 = v1_random)
    
    # Тест 3: Демонстрация вероятности
    print("\nТест 3: Вероятность успешной атаки при хешировании")
    print("-" * 40)
    attempts = 1000
    success_count = 0
    
    for i in range(attempts):
        v_test = random.randint(2, 1000)
        t_test = pow(g, v_test, p)
        c_hash = protocol.hash_function(g, protocol.y, t_test)
        if c_hash == p - 1:
            success_count += 1
    
    print(f"Из {attempts} попыток хеш совпал с (p - 1) {success_count} раз")
    print(f"Вероятность: {success_count / attempts:.6%}")
    print("На практике для SHA-256 эта вероятность равна 1 / 2 ^ 256 ≈ 0")


if __name__ == "__main__":
    main()