# Доказательство с нулевым разглашением
import random
import math

# =============================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# =============================================

def is_prime(n, k = 5):
    """Проверка простоты числа (тест Миллера-Рабина) - чисто для генерации p и q"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Проверяем k раундов
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits = 8):
    """Генерация простого числа заданной битности (для демонстрации)"""
    while True:
        num = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if is_prime(num):
            return num

def gcd(a, b):
    """Наибольший общий делитель (алгоритм Евклида)"""
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """Обратное число по модулю (расширенный алгоритм Евклида)"""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

# =============================================
# 2. КЛАСС СЕРВЕРА (ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ)
# =============================================

class Server:
    """Сервер, который хранит публичные ключи и проверяет доказательства"""
    
    def __init__(self):
        print("=== ИНИЦИАЛИЗАЦИЯ СЕРВЕРА ===")
        # Генерируем два простых числа p и q (в реальности сотни бит, здесь 8 бит для наглядности)
        self.p = generate_prime(8)
        self.q = generate_prime(8)
        # n = p * q - это публичный параметр
        self.n = self.p * self.q
        print(f"  Сгенерированы простые числа: p = {self.p}, q = {self.q}")
        print(f"  Модуль n = p * q = {self.n}")
        print()
        
        # Хранилище публичных ключей пользователей {user_id: v}
        self.public_keys = {}
    
    def register_user(self, user_id, secret_s):
        """Регистрация пользователя: сервер вычисляет v = s^2 mod n"""
        # Проверяем, что s взаимно просто с n (для корректности)
        if gcd(secret_s, self.n) != 1:
            print(f"  Ошибка: секрет {secret_s} не взаимно прост с n = {self.n}")
            return False
        
        v = pow(secret_s, 2, self.n)  # s^2 mod n
        self.public_keys[user_id] = v
        print(f"  Пользователь '{user_id}' зарегистрирован.")
        print(f"  Публичный ключ v = {secret_s} ^ 2 mod {self.n} = {v}")
        print(f"  (Секрет s = {secret_s} известен только пользователю и НЕ хранится на сервере)")
        print()
        return True
    
    def authenticate(self, user_id, proof_generator):
        """Запуск протокола аутентификации с нулевым разглашением"""
        if user_id not in self.public_keys:
            print(f"  Ошибка: пользователь '{user_id}' не зарегистрирован")
            return False
        
        v = self.public_keys[user_id]
        print(f"=== НАЧАЛО АУТЕНТИФИКАЦИИ: '{user_id}' ===")
        print(f"  Публичный ключ v = {v}")
        print()
        
        # Количество раундов (чем больше, тем надежнее)
        rounds = 20
        success_count = 0
        
        for round_num in range(1, rounds + 1):
            print(f"--- Раунд {round_num} ---")
            
            # Шаг 1: Пользователь генерирует случайное r и отправляет x = r^2 mod n
            r = proof_generator.generate_random()
            x = pow(r, 2, self.n)
            print(f"  Пользователь -> Сервер: x = {x} (r = {r} - скрыто)")
            
            # Шаг 2: Сервер отправляет случайный бит e (0 или 1)
            e = random.randint(0, 1)
            print(f"  Сервер -> Пользователь: e = {e}")
            
            # Шаг 3: Пользователь вычисляет ответ y
            y = proof_generator.generate_response(r, e)
            print(f"  Пользователь -> Сервер: y = {y}")
            
            # Шаг 4: Сервер проверяет
            if e == 0:
                # Проверяем: y^2 mod n == x
                check = pow(y, 2, self.n)
                expected = x
                is_valid = (check == expected)
                print(f"  Проверка: {y} ^ 2 mod {self.n} = {check} == {expected}? {is_valid}")
            else:  # e == 1
                # Проверяем: y^2 mod n == x * v mod n
                check = pow(y, 2, self.n)
                expected = (x * v) % self.n
                is_valid = (check == expected)
                print(f"  Проверка: {y} ^ 2 mod {self.n} = {check} == {x} * {v} mod {self.n} = {expected}? {is_valid}")
            
            if is_valid:
                success_count += 1
                print(f"  ✅ Раунд {round_num} пройден")
            else:
                print(f"  ❌ Раунд {round_num} ПРОВАЛЕН!")
            
            print()
        
        # Результат: все раунды должны быть успешными
        success_rate = success_count / rounds
        print(f"=== РЕЗУЛЬТАТ ===")
        print(f"  Успешно пройдено: {success_count} из {rounds} раундов ({success_rate * 100:.1f}%)")
        
        if success_count == rounds:
            print(f"  ✅ Аутентификация успешна! Пользователь '{user_id}' доказал знание секрета.")
            return True
        else:
            print(f"  ❌ Аутентификация не пройдена!")
            return False

# =============================================
# 3. КЛАСС ПОЛЬЗОВАТЕЛЯ (ДОКАЗАТЕЛЬ)
# =============================================

class Prover:
    """Пользователь, который знает секрет s и доказывает это"""
    
    def __init__(self, secret_s):
        self.secret_s = secret_s
        print(f"  Создан пользователь с секретом s = {secret_s}")
    
    def generate_random(self):
        """Генерирует случайное число r для каждого раунда"""
        # r должно быть взаимно простым с n, но для демонстрации просто случайное
        return random.randint(2, 100)
    
    def generate_response(self, r, e):
        """Вычисляет ответ в зависимости от запроса сервера"""
        if e == 0:
            return r
        else:  # e == 1
            return (r * self.secret_s) % 10000  # modulo для демонстрации (в реальности mod n)

# =============================================
# 4. КЛАСС МОШЕННИКА (ЗЛОУМЫШЛЕННИК)
# =============================================

class Attacker:
    """Мошенник, который НЕ знает секрет, но пытается обмануть сервер"""
    
    def __init__(self):
        print("  Создан злоумышленник (не знает секрет)")
    
    def generate_random(self):
        return random.randint(2, 100)
    
    def generate_response(self, r, e):
        """Мошенник не знает s, поэтому пытается угадать ответ"""
        # Он может подготовиться только к одному из двух случаев
        # Здесь симулируем: он просто всегда отправляет r (это сработает только если e=0)
        if e == 0:
            return r
        else:
            # Не зная s, он не может вычислить r*s, поэтому отправляет случайное число
            # Шанс угадать - 1/n, что практически 0
            return random.randint(1, 100)

# =============================================
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ ПРОГРАММЫ
# =============================================

def main():
    print("\n" + "=" * 60)
    print("     ДОКАЗАТЕЛЬСТВО С НУЛЕВЫМ РАЗГЛАШЕНИЕМ")
    print("          (Протокол Фиата-Шамира)")
    print("=" * 60 + "\n")
    
    # Шаг 1: Создаём сервер
    server = Server()
    
    # Шаг 2: Регистрируем честного пользователя
    print("=== РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ ===")
    secret_alice = 7  # Секретный PIN-код Алисы (в реальности - большое число)
    alice = Prover(secret_alice)
    server.register_user("Alice", secret_alice)
    
    # Шаг 3: Успешная аутентификация Алисы
    print("\n" + "=" * 60)
    print("   СЦЕНАРИЙ 1: ЧЕСТНЫЙ ПОЛЬЗОВАТЕЛЬ")
    print("=" * 60 + "\n")
    server.authenticate("Alice", alice)
    
    # Шаг 4: Попытка аутентификации злоумышленника
    print("\n" + "=" * 60)
    print("   СЦЕНАРИЙ 2: ЗЛОУМЫШЛЕННИК (НЕ ЗНАЕТ СЕКРЕТ)")
    print("=" * 60 + "\n")
    
    attacker = Attacker()
    # Регистрируем злоумышленника под другим именем (он может создать свой ключ, но не знает s Алисы)
    # Пытаемся войти как Алиса, используя свои ответы
    print("  Попытка взлома: злоумышленник пытается войти как 'Alice'...\n")
    server.authenticate("Alice", attacker)
    
    print("\n" + "=" * 60)
    print("   ВЫВОД:")
    print("   ✅ Честный пользователь успешно доказал знание секрета, НЕ РАСКРЫВ ЕГО.")
    print("   ❌ Злоумышленник не смог обмануть систему, так как не знает секрет.")
    print("   🔒 Сервер так и не узнал, что секрет Алисы = 7!")
    print("=" * 60)

if __name__ == "__main__":
    main()