# Предыстория и основные идеи
"""
Криптография с открытым ключом: Демонстрация односторонних функций
На основе текста о дискретном логарифме y = a^x mod p

Реализованы три классические задачи:
1. Хранение паролей (без сохранения самих паролей)
2. Система ПВО "Свой-Чужой" (с временной меткой)
3. Challenge-Response аутентификация (с вызовом)
"""

import hashlib
import time
import random
import math
from datetime import datetime
from typing import Tuple, Dict, Optional


class OneWayFunction:
    """
    Реализация односторонней функции y = a^x mod p
    С методами для прямого и обратного вычисления
    """
    
    def __init__(self, p: int, a: int):
        """
        Инициализация с параметрами функции
        
        Args:
            p: простое число (модуль)
            a: основание (примитивный корень по модулю p)
        """
        self.p = p
        self.a = a
        self._cache = {}  # Кэш для ускорения вычислений
        
    def compute_forward(self, x: int) -> int:
        """
        Вычисление y = a^x mod p (быстрое возведение в степень)
        Сложность: O(log x) операций умножения
        
        Реализует алгоритм из текста (бинарное возведение в степень)
        """
        if x in self._cache:
            return self._cache[x]
            
        # Бинарное возведение в степень (метод квадратирования)
        result = 1
        base = self.a % self.p
        exponent = x
        
        while exponent > 0:
            if exponent & 1:  # Если текущий бит = 1
                result = (result * base) % self.p
            base = (base * base) % self.p
            exponent >>= 1
            
        self._cache[x] = result
        return result
    
    def compute_forward_with_trace(self, x: int, verbose: bool = True) -> int:
        """
        Вычисление y = a^x mod p с выводом промежуточных шагов
        Демонстрирует алгоритм из примера 2.1
        """
        if verbose:
            print(f"\nВычисление {self.a} ^ {x} mod {self.p}")
            print("-" * 50)
            
            # Вычисляем ряд a, a^2, a^4, a^8, ...
            series = []
            current = self.a % self.p
            t = x.bit_length()
            
            print("Ряд значений:")
            for i in range(t + 1):
                series.append(current)
                print(f"  a ^ {2 ** i} = {current}")
                current = (current * current) % self.p
            
            # Двоичное представление показателя
            binary = bin(x)[2:]
            print(f"\nПоказатель x = {x} в двоичной системе: {binary}")
            
            # Вычисление результата
            result = 1
            steps = []
            for i, bit in enumerate(reversed(binary)):
                if bit == '1':
                    result = (result * series[i]) % self.p
                    steps.append(f"a ^ {2 ** i} ({series[i]})")
            
            print(f"Перемножаем: {' · '.join(steps)}")
            print(f"Результат: {result}")
            
        return self.compute_forward(x)
    
    def compute_backward_bruteforce(self, y: int, max_x: int = None) -> Optional[int]:
        """
        Вычисление дискретного логарифма x = log_a(y) mod p
        МЕТОД "ШАГ МЛАДЕНЦА, ШАГ ВЕЛИКАНА" (Baby-step Giant-step)
        Сложность: O(sqrt(p))
        
        Это демонстрация сложности обратной функции из текста
        """
        if max_x is None:
            max_x = self.p - 1
            
        print(f"\nПоиск дискретного логарифма log_{self.a}({y}) mod {self.p}")
        print("Используется метод 'шаг младенца, шаг великана'")
        print(f"Сложность: O(√p) ≈ O({int(math.sqrt(self.p))}) операций")
        
        # Шаг 1: Baby steps
        m = int(math.sqrt(self.p)) + 1
        baby_steps = {}
        
        print(f"Вычисление baby-steps (m = {m})...")
        current = 1
        for j in range(m):
            baby_steps[current] = j
            current = (current * self.a) % self.p
        
        # Шаг 2: Giant steps
        factor = pow(self.a, -m, self.p)  # a^(-m) mod p
        current = y
        
        print("Поиск giant-steps...")
        for i in range(m):
            if current in baby_steps:
                x = i * m + baby_steps[current]
                if pow(self.a, x, self.p) == y:
                    print(f"Найдено решение: x = {x}")
                    return x
            current = (current * factor) % self.p
            
        print("Решение не найдено")
        return None


class PasswordManager:
    """
    Задача 1: Хранение паролей в памяти компьютера
    Пароли не хранятся! Хранятся только хеши (результат односторонней функции)
    """
    
    def __init__(self, one_way: OneWayFunction):
        self.one_way = one_way
        self.users = {}  # username -> (y, salt)
        
    def register_user(self, username: str, password: str):
        """
        Регистрация пользователя
        
        Вместо хранения пароля, храним y = a^password mod p
        """
        # Преобразуем пароль в число
        x = self._string_to_int(password)
        
        # Добавляем соль для защиты от радужных таблиц
        salt = random.randint(1000, 9999)
        x_with_salt = x ^ salt  # XOR с солью
        
        # Вычисляем одностороннюю функцию
        y = self.one_way.compute_forward(x_with_salt)
        
        self.users[username] = (y, salt)
        print(f"✅ Пользователь '{username}' зарегистрирован")
        print(f"   Хранится в БД: {username} -> {y}")
        print(f"   Пароль '{password}' НЕ хранится!")
        
    def authenticate(self, username: str, password: str) -> bool:
        """
        Аутентификация пользователя
        
        Сравниваем вычисленное значение с хранимым
        """
        if username not in self.users:
            print(f"❌ Пользователь '{username}' не найден")
            return False
            
        stored_y, salt = self.users[username]
        
        # Вычисляем y для введенного пароля
        x = self._string_to_int(password)
        x_with_salt = x ^ salt
        computed_y = self.one_way.compute_forward(x_with_salt)
        
        if computed_y == stored_y:
            print(f"✅ Пользователь '{username}' успешно аутентифицирован")
            return True
        else:
            print(f"❌ Неверный пароль для пользователя '{username}'")
            return False
    
    @staticmethod
    def _string_to_int(s: str) -> int:
        """Преобразование строки в число"""
        return int.from_bytes(s.encode('utf-8'), 'big')


class IFFSystem:
    """
    Задача 2: Система "Свой-Чужой" (Identification Friend or Foe)
    Используется временная метка для защиты от повторного использования
    """
    
    def __init__(self, one_way: OneWayFunction):
        self.one_way = one_way
        self.secret_names = {}  # aircraft_id -> secret_name
        self.used_responses = set()  # Защита от повторов
        self.time_window = 2  # Окно в минутах (для рассинхронизации)
        
    def register_aircraft(self, aircraft_id: str, secret_name: str):
        """Регистрация самолета с секретным именем"""
        self.secret_names[aircraft_id] = secret_name
        print(f"✈️ Самолет '{aircraft_id}' зарегистрирован с секретным именем '{secret_name}'")
        
    def generate_challenge(self, aircraft_id: str) -> Tuple[int, str]:
        """
        Локатор генерирует запрос для самолета
        Возвращает: (timestamp, current_time_str)
        """
        # Формируем временную метку
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M")
        
        print(f"\n📡 Локатор: Запрос к самолету '{aircraft_id}'")
        print(f"   Время: {now.strftime('%Y-%m-%d %H:%M')}")
        
        return int(timestamp), timestamp
    
    def aircraft_respond(self, aircraft_id: str, timestamp: int) -> int:
        """
        Бортовой компьютер самолета вычисляет ответ
        x = secret_name + timestamp
        y = a^x mod p
        """
        if aircraft_id not in self.secret_names:
            print(f"❌ Самолет '{aircraft_id}' не зарегистрирован")
            return -1
            
        secret = self.secret_names[aircraft_id]
        
        # Формируем слово: secret + timestamp
        word = f"{secret}{timestamp}"
        x = self._string_to_int(word)
        
        # Вычисляем ответ
        y = self.one_way.compute_forward(x)
        
        print(f"✈️ Самолет '{aircraft_id}': Ответ = {y}")
        return y
    
    def verify_response(self, aircraft_id: str, timestamp: int, response: int) -> bool:
        """
        Локатор проверяет ответ самолета
        С учетом временного окна для защиты от рассинхронизации
        """
        print(f"\n🔍 Локатор: Проверка ответа от '{aircraft_id}'")
        print(f"   Получен ответ: {response}")
        print(f"   Метка времени: {timestamp}")
        
        # Проверка на повторное использование
        response_key = f"{aircraft_id}:{response}"
        if response_key in self.used_responses:
            print("❌ ОТКЛОНЕНО: Ответ уже был использован (атака повторного воспроизведения)")
            return False
        
        # Проверяем несколько временных меток (для компенсации рассинхронизации)
        for offset in range(-self.time_window, self.time_window + 1):
            check_time = timestamp + offset
            
            # Формируем слово, как у самолета
            secret = self.secret_names.get(aircraft_id)
            if not secret:
                return False
                
            word = f"{secret}{check_time}"
            x = self._string_to_int(word)
            
            # Вычисляем ожидаемый ответ
            expected = self.one_way.compute_forward(x)
            
            if expected == response:
                print(f"✅ ПОДТВЕРЖДЕНО: Самолет '{aircraft_id}' свой!")
                print(f"   (Временная метка: {check_time}, смещение: {offset})")
                self.used_responses.add(response_key)
                return True
        
        print("❌ ОТКЛОНЕНО: Неверный ответ")
        return False
    
    @staticmethod
    def _string_to_int(s: str) -> int:
        """Преобразование строки в число"""
        return int.from_bytes(s.encode('utf-8'), 'big')


class ChallengeResponseSystem:
    """
    Задача 3: Challenge-Response аутентификация с вызовом
    Локатор посылает случайное число (вызов), самолет отвечает
    """
    
    def __init__(self, one_way: OneWayFunction):
        self.one_way = one_way
        self.secrets = {}  # entity_id -> secret
        self.used_challenges = set()  # Защита от повторов
        
    def register_entity(self, entity_id: str, secret: str):
        """Регистрация сущности с секретным словом"""
        self.secrets[entity_id] = secret
        print(f"🔐 Сущность '{entity_id}' зарегистрирована")
        
    def generate_challenge(self) -> int:
        """
        Генерация случайного вызова
        """
        challenge = random.randint(1000, 999999)
        print(f"📢 Вызов: {challenge}")
        return challenge
    
    def compute_response(self, entity_id: str, challenge: int) -> Optional[int]:
        """
        Вычисление ответа на вызов
        y = (secret + challenge)^x mod p
        """
        if entity_id not in self.secrets:
            print(f"❌ Сущность '{entity_id}' не зарегистрирована")
            return None
            
        secret = self.secrets[entity_id]
        
        # Формируем слово: secret + challenge
        word = f"{secret}{challenge}"
        x = self._string_to_int(word)
        
        response = self.one_way.compute_forward(x)
        print(f"🔑 Ответ от '{entity_id}': {response}")
        return response
    
    def verify_response(self, entity_id: str, challenge: int, response: int) -> bool:
        """
        Проверка ответа
        """
        print(f"\n🔍 Проверка ответа от '{entity_id}'")
        print(f"   Вызов: {challenge}")
        print(f"   Ответ: {response}")
        
        # Проверка на повторное использование вызова
        challenge_key = f"{entity_id}:{challenge}"
        if challenge_key in self.used_challenges:
            print("❌ ОТКЛОНЕНО: Вызов уже использован")
            return False
        
        # Вычисляем ожидаемый ответ
        secret = self.secrets.get(entity_id)
        if not secret:
            return False
            
        word = f"{secret}{challenge}"
        x = self._string_to_int(word)
        expected = self.one_way.compute_forward(x)
        
        if expected == response:
            print(f"✅ ПОДТВЕРЖДЕНО: '{entity_id}' аутентифицирован!")
            self.used_challenges.add(challenge_key)
            return True
        else:
            print("❌ ОТКЛОНЕНО: Неверный ответ")
            return False
    
    @staticmethod
    def _string_to_int(s: str) -> int:
        """Преобразование строки в число"""
        return int.from_bytes(s.encode('utf-8'), 'big')


def demonstrate_complexity():
    """
    Демонстрация сложности вычислений из Таблицы 2.1
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ СЛОЖНОСТИ ВЫЧИСЛЕНИЙ")
    print("=" * 70)
    
    # Маленькое p для демонстрации
    p = 97  # Простое число
    a = 5   # Примитивный корень по модулю 97
    
    one_way = OneWayFunction(p, a)
    
    # Прямое вычисление (быстрое)
    x = 42
    print(f"\nПрямое вычисление y = {a} ^ {x} mod {p}")
    start = time.time()
    y = one_way.compute_forward_with_trace(x)
    elapsed = time.time() - start
    print(f"✅ Вычислено за {elapsed:.6f} секунд")
    
    # Обратное вычисление (медленное - только для маленького p!)
    print(f"\nОбратное вычисление x = log_{a}({y}) mod {p}")
    print("(Для демонстрации используется маленькое p = 97)")
    start = time.time()
    x_found = one_way.compute_backward_bruteforce(y)
    elapsed = time.time() - start
    if x_found is not None:
        print(f"✅ Найдено x = {x_found} за {elapsed:.6f} секунд")
    else:
        print("❌ Решение не найдено")
    
    # Сравнение с большим p (только оценка)
    print("\n" + "-" * 70)
    print("ОЦЕНКА ДЛЯ БОЛЬШИХ p (как в Таблице 2.1)")
    print("-" * 70)
    
    for digits in [10, 20, 50]:
        p_size = 10 ** digits
        sqrt_p = math.sqrt(p_size)
        log_p = math.log2(p_size)
        
        print(f"\np ≈ 10^{digits} (около {digits} цифр):")
        print(f"  Прямая функция: O(log p) ≈ {log_p:.0f} операций (быстро)")
        print(f"  Обратная функция: O(√p) ≈ {sqrt_p:.2e} операций (медленно)")
        
        if digits >= 50:
            print(f"  ⚠️ Разница: √p / log p ≈ {sqrt_p/log_p:.2e} раз!")


def main():
    """
    Главная функция с демонстрацией всех задач
    """
    print("=" * 70)
    print("КРИПТОГРАФИЯ С ОТКРЫТЫМ КЛЮЧОМ")
    print("Демонстрация односторонних функций на практике")
    print("=" * 70)
    
    # Параметры для односторонней функции
    # Используем небольшое простое число для демонстрации
    # В реальных системах p должно быть > 2^512
    p = 101  # Простое число
    a = 2    # Примитивный корень по модулю 101 (2 является примитивным корнем для 101)
    
    print(f"\nПараметры системы:")
    print(f"  p = {p} (простое число)")
    print(f"  a = {a} (основание)")
    print(f"  Функция: y = {a}^x mod {p}")
    
    one_way = OneWayFunction(p, a)
    
    # ========== ЗАДАЧА 1: Хранение паролей ==========
    print("\n" + "=" * 70)
    print("ЗАДАЧА 1: ХРАНЕНИЕ ПАРОЛЕЙ")
    print("=" * 70)
    
    password_manager = PasswordManager(one_way)
    
    # Регистрация пользователей
    password_manager.register_user("fruit", "абрикос")
    password_manager.register_user("alice", "secret123")
    password_manager.register_user("bob", "qwerty")
    
    print("\n" + "-" * 40)
    
    # Попытка входа
    password_manager.authenticate("fruit", "абрикос")
    password_manager.authenticate("fruit", "неправильный")
    password_manager.authenticate("alice", "secret123")
    
    print("\n💡 Пароли хранятся в виде y = a ^ x mod p")
    print(f"   Злоумышленник, получивший БД, не сможет восстановить пароли")
    print(f"   (потребуется {2 * math.sqrt(p):.0f} операций для взлома)")
    
    # ========== ЗАДАЧА 2: Система ПВО ==========
    print("\n" + "=" * 70)
    print("ЗАДАЧА 2: СИСТЕМА 'СВОЙ-ЧУЖОЙ' (ПВО)")
    print("=" * 70)
    
    iff = IFFSystem(one_way)
    
    # Регистрация самолетов
    iff.register_aircraft("SU-27", "СОКОЛ")
    iff.register_aircraft("F-16", "EAGLE")
    
    print("\n" + "-" * 40)
    
    # Сеанс связи
    aircraft = "SU-27"
    timestamp, time_str = iff.generate_challenge(aircraft)
    response = iff.aircraft_respond(aircraft, timestamp)
    iff.verify_response(aircraft, timestamp, response)
    
    # Попытка повторного использования (атака)
    print("\n" + "!" * 50)
    print("ПОПЫТКА АТАКИ ПОВТОРНОГО ВОСПРОИЗВЕДЕНИЯ")
    print("!" * 50)
    print("Ева перехватила ответ и пытается использовать его снова...")
    iff.verify_response(aircraft, timestamp, response)  # Будет отклонено
    
    print("\n💡 Система защищена от повторов благодаря временной метке")
    print(f"   и проверке использованных ответов")
    
    # ========== ЗАДАЧА 3: Challenge-Response ==========
    print("\n" + "=" * 70)
    print("ЗАДАЧА 3: CHALLENGE-RESPONSE АУТЕНТИФИКАЦИЯ")
    print("=" * 70)
    
    challenge_system = ChallengeResponseSystem(one_way)
    
    # Регистрация
    challenge_system.register_entity("банк", "SECRET_KEY_2024")
    challenge_system.register_entity("клиент", "MY_PASSWORD")
    
    print("\n" + "-" * 40)
    
    # Успешная аутентификация
    challenge = challenge_system.generate_challenge()
    response = challenge_system.compute_response("клиент", challenge)
    challenge_system.verify_response("клиент", challenge, response)
    
    # Попытка взлома (Ева не знает секрет)
    print("\n" + "!" * 50)
    print("ПОПЫТКА ВЗЛОМА (Ева пытается угадать ответ)")
    print("!" * 50)
    challenge = challenge_system.generate_challenge()
    fake_response = random.randint(1, 1000)
    challenge_system.verify_response("клиент", challenge, fake_response)
    
    print("\n💡 Даже зная вызов, Ева не может вычислить правильный ответ")
    print(f"   без знания секретного слова")
    
    # ========== ДЕМОНСТРАЦИЯ СЛОЖНОСТИ ==========
    demonstrate_complexity()
    
    # ========== ИТОГИ ==========
    print("\n" + "=" * 70)
    print("ИТОГИ")
    print("=" * 70)
    print("""
    ✅ Все три задачи решены с использованием одной односторонней функции:
       y = a ^ x mod p
    
    ✅ Прямое вычисление (возведение в степень) — БЫСТРО (O(log x))
    ✅ Обратное вычисление (дискретный логарифм) — МЕДЛЕННО (O(√p))
    
    ✅ Защита от атак:
       - Пароли не хранятся в открытом виде
       - Временные метки предотвращают повторное использование
       - Случайные вызовы делают каждый сеанс уникальным
    
    ⚠️ ВАЖНО: Для реальной безопасности нужно использовать p > 2^512
       (здесь используется маленькое p=101 только для демонстрации)
    """)


if __name__ == "__main__":
    main()