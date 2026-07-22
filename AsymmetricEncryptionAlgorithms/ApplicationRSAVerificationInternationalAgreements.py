# Применение RSA для проверки международных соглашений
import random
import hashlib

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БОЛЬШИМИ ЧИСЛАМИ
# ============================================================

def gcd_extended(a, b):
    """Расширенный алгоритм Евклида: возвращает (gcd, x, y), где ax + by = gcd"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd_extended(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """Обратное число по модулю m"""
    g, x, _ = gcd_extended(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def is_prime(n, k = 10):
    """Тест Миллера-Рабина на простоту"""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    
    # Представляем n-1 как d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проверяем k раз
    for _ in range(k):
        a = random.randrange(2, n - 1)
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

def generate_prime(bits):
    """Генерация простого числа заданной битности"""
    while True:
        n = random.getrandbits(bits)
        # Устанавливаем старший и младший биты для нечетности и нужного размера
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n

def generate_rsa_keys(bits = 512):
    """
    Генерация ключей RSA
    Возвращает: (N, e, d)
    """
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    N = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (обычно 65537)
    e = 65537
    while gcd_extended(e, phi)[0] != 1:
        e = random.randrange(3, phi, 2)
    
    d = mod_inverse(e, phi)
    return N, e, d


# ============================================================
# 2. ОСНОВНАЯ ЛОГИКА ПРОТОКОЛА
# ============================================================

class SeismicSensor:
    """Датчик, установленный глубоко в земле"""
    
    def __init__(self, N, e, d):
        self.N = N          # Модуль RSA
        self.e = e          # Открытая экспонента (для проверки)
        self.d = d          # Закрытая экспонента (хранится в защищенном чипе)
        self.sensor_id = random.randint(1000, 9999)
    
    def collect_data(self, raw_value):
        """
        Датчик собирает данные (сырое сейсмическое значение)
        и подписывает их закрытым ключом
        """
        # Добавляем идентификатор датчика и случайную соль для защиты от подделок
        timestamp = random.randint(100000, 999999)
        # Формируем сообщение: [значение, ID датчика, временная метка]
        x = (raw_value << 32) | (self.sensor_id << 16) | timestamp
        
        # Подпись: y = x^d mod N (инвертированный RSA)
        y = pow(x, self.d, self.N)
        
        return x, y
    
    def verify_signature(self, x, y):
        """Проверка подписи открытым ключом"""
        # x = y^e mod N
        return pow(y, self.e, self.N) == x


class CountryAlpha:
    """Страна Альфа (проверяющая сторона)"""
    
    def __init__(self, bits=512):
        self.N, self.e, self.d = generate_rsa_keys(bits)
        self.verified_data = []
        print(f"[Альфа] Сгенерированы ключи RSA (битность: {bits})")
        print(f"[Альфа] Открытый ключ: (N = {self.N}, e = {self.e})")
        print(f"[Альфа] Закрытый ключ: d = {self.d}\n")
    
    def get_public_key(self):
        """Отправляет открытый ключ стране Бета и датчикам"""
        return self.N, self.e
    
    def verify_data(self, x, y):
        """
        Проверяет достоверность полученных данных
        Возвращает True, если данные подписаны легитимным датчиком
        """
        # Проверка: x = y^e mod N
        calculated_x = pow(y, self.e, self.N)
        is_valid = (calculated_x == x)
        
        if is_valid:
            # Извлекаем сырые данные (восстанавливаем)
            raw_value = x >> 32
            sensor_id = (x >> 16) & 0xFFFF
            timestamp = x & 0xFFFF
            self.verified_data.append({
                'raw': raw_value,
                'sensor_id': sensor_id,
                'timestamp': timestamp
            })
            print(f"[Альфа] ✅ Данные ДОСТОВЕРНЫ! raw = {raw_value}, " f"sensor = {sensor_id}, time = {timestamp}")
        else:
            print(f"[Альфа] ❌ Данные НЕДОСТОВЕРНЫ! Подпись не совпадает")
        
        return is_valid


class CountryBeta:
    """Страна Бета (посредник, пытающаяся проверить и, возможно, подделать)"""
    
    def __init__(self, N, e):
        self.N = N
        self.e = e
        self.known_valid_pairs = []  # Хранит легитимные пары (x, y)
        print(f"[Бета] Получен открытый ключ от Альфы: (N = {N}, e = {e})")
    
    def verify_and_relay(self, sensor, x, y):
        """
        Проверяет данные от датчика и решает,
        отправлять их Альфе или подменить
        """
        # Сначала проверяем подпись
        if pow(y, self.e, self.N) == x:
            print(f"[Бета] ✅ Подпись датчика верна")
            
            # Сохраняем легитимные данные для возможных атак
            self.known_valid_pairs.append((x, y))
            
            # В честном случае просто передаём дальше
            return x, y, True
        else:
            print(f"[Бета] ❌ Подпись НЕВЕРНА! Возможна атака")
            return x, y, False
    
    def forge_attack(self, x_fake):
        """
        Пытается подделать данные (атака мультипликативностью RSA)
        Если есть две легитимные пары, можно создать третью
        """
        if len(self.known_valid_pairs) < 2:
            print("[Бета] Недостаточно данных для мультипликативной атаки")
            return None, None
        
        # Берем две легитимные пары
        (x1, y1) = self.known_valid_pairs[0]
        (x2, y2) = self.known_valid_pairs[1]
        
        # Создаем фальшивое сообщение: x_fake = x1 * x2 (по модулю N)
        x_forged = (x1 * x2) % self.N
        y_forged = (y1 * y2) % self.N
        
        print(f"[Бета] 🔥 МУЛЬТИПЛИКАТИВНАЯ АТАКА: создана фальшивая пара")
        print(f"[Бета]    x_fake = {x_forged}")
        print(f"[Бета]    y_fake = {y_forged}")
        
        return x_forged, y_forged
    
    def blind_signature_attack(self, sensor, target_x):
        """
        Атака "слепой подписи": заставляет датчик подписать нужное значение
        """
        # Выбираем случайное маскирующее число r
        r = random.randrange(2, self.N - 1)
        while gcd_extended(r, self.N)[0] != 1:
            r = random.randrange(2, self.N - 1)
        
        # Маскируем целевое сообщение: x_blind = target_x * r^e mod N
        x_blind = (target_x * pow(r, self.e, self.N)) % self.N
        
        print(f"[Бета] Попытка атаки 'слепой подписи'...")
        
        # Отправляем замаскированное значение датчику (датчик думает, что это легитимные данные)
        x_blind_signed, y_blind = sensor.collect_data(x_blind)
        
        # Снимаем маску: y_target = y_blind * r^{-1} mod N
        r_inv = mod_inverse(r, self.N)
        y_target = (y_blind * r_inv) % self.N
        
        print(f"[Бета] 🔥 АТАКА 'СЛЕПАЯ ПОДПИСЬ' успешна!")
        print(f"[Бета]    Целевое x = {target_x}")
        print(f"[Бета]    Подпись y = {y_target}")
        
        return target_x, y_target


# ============================================================
# 3. ДЕМОНСТРАЦИЯ РАБОТЫ ПРОТОКОЛА
# ============================================================

def main():
    print("=" * 70)
    print("МОДЕЛИРОВАНИЕ ПРОТОКОЛА RSA ДЛЯ МОНИТОРИНГА СЕЙСМИЧЕСКИХ ДАННЫХ")
    print("=" * 70)
    print()
    
    # Шаг 1: Альфа генерирует ключи
    alpha = CountryAlpha(bits = 256)  # Для демонстрации используем 256 бит
    
    # Шаг 2: Альфа отправляет открытый ключ Бете и датчику
    N, e = alpha.get_public_key()
    beta = CountryBeta(N, e)
    
    # Шаг 3: Устанавливаем датчик с закрытым ключом
    sensor = SeismicSensor(N, e, alpha.d)
    print(f"[Датчик] Установлен глубоко в земле. ID = {sensor.sensor_id}\n")
    
    print("-" * 70)
    print("СЦЕНАРИЙ 1: ЛЕГИТИМНАЯ ПЕРЕДАЧА ДАННЫХ")
    print("-" * 70)
    
    # Датчик собирает данные
    raw_1 = 12345  # Сейсмическое значение
    x1, y1 = sensor.collect_data(raw_1)
    print(f"[Датчик] Собраны данные: x = {x1}, подпись y = {y1}")
    
    # Бета проверяет и передает Альфе
    x_relay, y_relay, is_valid = beta.verify_and_relay(sensor, x1, y1)
    if is_valid:
        alpha.verify_data(x_relay, y_relay)
    
    print("\n" + "-" * 70)
    print("СЦЕНАРИЙ 2: БЕТА ПЫТАЕТСЯ ПОДДЕЛАТЬ ДАННЫЕ (МУЛЬТИПЛИКАТИВНАЯ АТАКА)")
    print("-" * 70)
    
    # Собираем вторые легитимные данные для атаки
    raw_2 = 67890
    x2, y2 = sensor.collect_data(raw_2)
    beta.verify_and_relay(sensor, x2, y2)
    
    # Теперь Бета создает фальшивые данные
    x_fake, y_fake = beta.forge_attack(None)
    if x_fake:
        print(f"\n[Бета] Отправляет фальшивые данные Альфе...")
        alpha.verify_data(x_fake, y_fake)
    
    print("\n" + "-" * 70)
    print("СЦЕНАРИЙ 3: АТАКА 'СЛЕПАЯ ПОДПИСЬ' (БЕТА ПЫТАЕТСЯ ПОДПИСАТЬ ПЛОХИЕ ДАННЫЕ)")
    print("-" * 70)
    
    # Бета хочет получить подпись для плохого значения 999999
    target_bad = 999999
    x_bad, y_bad = beta.blind_signature_attack(sensor, target_bad)
    
    print(f"\n[Бета] Отправляет подписанные плохие данные Альфе...")
    alpha.verify_data(x_bad, y_bad)
    
    print("\n" + "-" * 70)
    print("СЦЕНАРИЙ 4: АТАКА ПЕРЕБОРОМ (МАЛЫЕ СООБЩЕНИЯ)")
    print("-" * 70)
    
    # Датчик подписывает маленькое значение (например, 42)
    raw_small = 42
    x_small, y_small = sensor.collect_data(raw_small)
    print(f"[Датчик] Подписал маленькое значение: x = {x_small}, y = {y_small}")
    
    # Альфа проверяет - всё легитимно
    print("[Альфа] Проверка легитимной подписи:")
    alpha.verify_data(x_small, y_small)
    
    # ДЕМОНСТРАЦИЯ ПЕРЕБОРА (только если N небольшое)
    print("[Альфа] Попытка перебора малых сообщений (только демонстрация):")
    # В реальности перебор по 256-битному ключу невозможен,
    # но мы показываем принцип для маленького пространства поиска
    
    # Перебираем возможные значения в диапазоне, где известно, что данные малы
    found = False
    for test_value in range(1, 100):
        # Формируем структуру сообщения как в датчике
        test_x = (test_value << 32) | (sensor.sensor_id << 16) | (x_small & 0xFFFF)
        if pow(y_small, e, N) == test_x:
            print(f"[Альфа] ✅ Найдено исходное значение путем перебора: {test_value}")
            found = True
            break
    
    if not found:
        print("[Альфа] ❌ Перебор не удался (возможно, значение вне диапазона)")
    
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"Альфа проверила {len(alpha.verified_data)} легитимных пакетов данных")
    print("Все проверки завершены.")


if __name__ == "__main__":
    main()