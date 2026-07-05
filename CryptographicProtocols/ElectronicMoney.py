# Электронные деньги
"""
Электронные деньги - реализация трех схем электронных платежей
На основе текста Д. Чаума о слепых подписях и анонимных платежах
"""

import random
import math
from typing import Tuple, Optional, List, Set

class Bank:
    """
    Класс, представляющий банк в системе электронных платежей
    """
    def __init__(self, P: int, Q: int, c: int):
        """
        Инициализация банка с параметрами RSA
        
        Args:
            P, Q: простые числа для генерации ключей
            c: секретный показатель для подписи (взаимно прост с (P - 1)(Q - 1))
        """
        self.P = P
        self.Q = Q
        self.N = P * Q
        self.c = c
        # Вычисляем d = c^(-1) mod (P-1)(Q-1)
        phi = (P - 1) * (Q - 1)
        self.d = pow(c, -1, phi)  # Используем встроенную функцию Python 3.8+
        
        # Счета участников (в рублях)
        self.accounts = {}
        
        # Хранилище использованных банкнот (для защиты от двойной траты)
        self.used_notes = set()
        
        # История транзакций (для отладки)
        self.transactions = []
        
        print(f"Банк создан с параметрами:")
        print(f"  N = {self.N}, c = {self.c}, d = {self.d}")
        print(f"  P = {P}, Q = {Q}, phi = {phi}")
        print()
    
    def create_account(self, user_id: str, initial_balance: int = 1000):
        """Создание счета для пользователя"""
        self.accounts[user_id] = initial_balance
        print(f"Создан счет для {user_id}: баланс = {initial_balance}$")
        return initial_balance
    
    def get_balance(self, user_id: str) -> int:
        """Получение баланса пользователя"""
        return self.accounts.get(user_id, 0)
    
    def sign_message(self, message: int) -> int:
        """
        Подпись сообщения с использованием секретного ключа
        s = message^c mod N
        """
        return pow(message, self.c, self.N)
    
    def verify_signature(self, n: int, s: int, d: int = None) -> bool:
        """
        Проверка подписи банка
        Проверяет, что s^d mod N == n (или s^d mod N == f(n) для схемы 3)
        """
        if d is None:
            d = self.d
        return pow(s, d, self.N) == n
    
    def scheme1_issue_note(self, user_id: str, n: int) -> Tuple[int, int]:
        """
        Схема 1 (плохая): обычная подпись без анонимности
        Банк подписывает n и списывает 100$ со счета
        """
        if self.accounts.get(user_id, 0) < 100:
            raise ValueError(f"Недостаточно средств у {user_id}")
        
        # Списываем 100$
        self.accounts[user_id] -= 100
        
        # Подписываем номер банкноты
        s = self.sign_message(n)
        
        self.transactions.append({
            'scheme': 'Схема 1',
            'user': user_id,
            'n': n,
            'amount': 100,
            'action': 'выдача'
        })
        
        print(f"  Банк выдал банкноту 〈{n}, {s}〉 пользователю {user_id}")
        print(f"  Баланс {user_id}: {self.accounts[user_id]}$")
        return n, s
    
    def scheme2_issue_anonymous(self, user_id: str, n_hat: int) -> int:
        """
        Схема 2: слепая подпись (анонимная, но уязвимая к подделке)
        Банк подписывает n_hat и списывает 100$
        """
        if self.accounts.get(user_id, 0) < 100:
            raise ValueError(f"Недостаточно средств у {user_id}")
        
        # Списываем 100$
        self.accounts[user_id] -= 100
        
        # Слепая подпись: s_hat = n_hat^c mod N
        s_hat = self.sign_message(n_hat)
        
        # Банк не знает реальный номер n, только n_hat
        self.transactions.append({
            'scheme': 'Схема 2',
            'user': user_id,
            'n_hat': n_hat,
            's_hat': s_hat,
            'amount': 100,
            'action': 'слепая выдача'
        })
        
        print(f"  Банк выполнил слепую подпись для n̂={n_hat}, выдал ŝ={s_hat}")
        print(f"  Баланс {user_id}: {self.accounts[user_id]}$")
        return s_hat
    
    def scheme3_issue_anonymous(self, user_id: str, f_n: int) -> int:
        """
        Схема 3 (хорошая): слепая подпись с хеш-функцией
        Банк подписывает f(n) и списывает 100$
        """
        if self.accounts.get(user_id, 0) < 100:
            raise ValueError(f"Недостаточно средств у {user_id}")
        
        # Списываем 100$
        self.accounts[user_id] -= 100
        
        # Слепая подпись: s_hat = (f(n))^c mod N
        s_hat = self.sign_message(f_n)
        
        self.transactions.append({
            'scheme': 'Схема 3',
            'user': user_id,
            'f_n': f_n,
            's_hat': s_hat,
            'amount': 100,
            'action': 'слепая выдача с хешем'
        })
        
        print(f"  Банк выполнил слепую подпись для f(n) = {f_n}, выдал ŝ = {s_hat}")
        print(f"  Баланс {user_id}: {self.accounts[user_id]}$")
        return s_hat
    
    def process_payment(self, n: int, s: int, merchant_id: str, scheme: int = 1, f_n: Optional[int] = None) -> bool:
        """
        Обработка платежа магазину
        
        Args:
            n: номер банкноты
            s: подпись
            merchant_id: ID магазина
            scheme: номер схемы (1, 2 или 3)
            f_n: для схемы 3 - хеш от n
            
        Returns:
            True если платеж принят
        """
        print(f"\n--- Магазин {merchant_id} проверяет банкноту 〈{n}, {s}〉 ---")
        
        # Проверка 1: не использовалась ли банкнота раньше
        if n in self.used_notes:
            print(f"  ❌ Ошибка: банкнота с номером {n} уже использована!")
            return False
        
        # Проверка 2: корректность подписи
        if scheme == 3:
            # Для схемы 3 проверяем: s^d mod N == f(n)
            if f_n is None:
                print("  ❌ Ошибка: для схемы 3 требуется f(n)")
                return False
            is_valid = self.verify_signature(f_n, s)
            print(f"  Проверка: {s} ^ {self.d} mod {self.N} = {pow(s, self.d, self.N)}")
            print(f"  Ожидается: f(n) = {f_n}")
        else:
            # Для схем 1 и 2 проверяем: s^d mod N == n
            is_valid = self.verify_signature(n, s)
            print(f"  Проверка: {s} ^ {self.d} mod {self.N} = {pow(s, self.d, self.N)}")
            print(f"  Ожидается: n = {n}")
        
        if not is_valid:
            print("  ❌ Ошибка: подпись неверна!")
            return False
        
        # Все проверки пройдены
        self.used_notes.add(n)
        
        # Зачисляем 100$ на счет магазина
        if merchant_id not in self.accounts:
            self.accounts[merchant_id] = 0
        self.accounts[merchant_id] += 100
        
        self.transactions.append({
            'scheme': f'Схема {scheme}',
            'n': n,
            's': s,
            'merchant': merchant_id,
            'amount': 100,
            'action': 'оплата'
        })
        
        print(f"  ✅ Платеж принят! На счет {merchant_id} зачислено 100$")
        print(f"  Баланс {merchant_id}: {self.accounts[merchant_id]}$")
        return True


class Buyer:
    """
    Класс покупателя
    """
    def __init__(self, name: str, bank: Bank):
        self.name = name
        self.bank = bank
        self.notes = []  # Хранит полученные банкноты
        
    def generate_note_number(self, N: int) -> int:
        """Генерация случайного номера банкноты"""
        return random.randint(2, N - 1)
    
    def scheme1_get_note(self) -> Tuple[int, int]:
        """
        Схема 1: получить банкноту
        """
        print(f"\n{self.name} хочет получить банкноту (Схема 1)")
        n = self.generate_note_number(self.bank.N)
        print(f"  Генерирует номер n = {n}")
        
        n, s = self.bank.scheme1_issue_note(self.name, n)
        self.notes.append((n, s, 1))
        return n, s
    
    def scheme2_get_note(self) -> Tuple[int, int, int]:
        """
        Схема 2: получить анонимную банкноту со слепой подписью
        Возвращает (n, s, r) где r - случайное число
        """
        print(f"\n{self.name} хочет получить анонимную банкноту (Схема 2)")
        
        # Генерируем номер n (никому не показываем)
        n = self.generate_note_number(self.bank.N)
        print(f"  Генерирует номер n = {n} (секретно)")
        
        # Генерируем случайное r, взаимно простое с N
        while True:
            r = random.randint(2, self.bank.N - 1)
            if math.gcd(r, self.bank.N) == 1:
                break
        print(f"  Генерирует r = {r}, взаимно простое с {self.bank.N}")
        
        # Вычисляем n̂ = n * r^d mod N
        n_hat = (n * pow(r, self.bank.d, self.bank.N)) % self.bank.N
        print(f"  Вычисляет n̂ = {n} * {r} ^ {self.bank.d} mod {self.bank.N} = {n_hat}")
        print(f"  Отправляет n̂ = {n_hat} в банк")
        
        # Банк делает слепую подпись
        s_hat = self.bank.scheme2_issue_anonymous(self.name, n_hat)
        
        # Покупатель вычисляет s = ŝ * r^{-1} mod N
        r_inv = pow(r, -1, self.bank.N)
        s = (s_hat * r_inv) % self.bank.N
        print(f"  Вычисляет r⁻¹ = {r_inv} mod {self.bank.N}")
        print(f"  Вычисляет s = {s_hat} * {r_inv} mod {self.bank.N} = {s}")
        
        # Проверка: s^d mod N должно быть равно n
        check = pow(s, self.bank.d, self.bank.N)
        print(f"  Проверка: {s} ^ {self.bank.d} mod {self.bank.N} = {check} (ожидается {n})")
        
        self.notes.append((n, s, 2))
        return n, s, r
    
    def scheme3_get_note(self, f) -> Tuple[int, int, int]:
        """
        Схема 3: получить анонимную банкноту с хеш-функцией
        f - односторонняя функция (хеш)
        """
        print(f"\n{self.name} хочет получить анонимную банкноту (Схема 3)")
        
        # Генерируем номер n (никому не показываем)
        n = self.generate_note_number(self.bank.N)
        print(f"  Генерирует номер n = {n} (секретно)")
        
        # Вычисляем f(n)
        f_n = f(n)
        print(f"  Вычисляет f(n) = {f_n}")
        
        # Генерируем случайное r, взаимно простое с N
        while True:
            r = random.randint(2, self.bank.N - 1)
            if math.gcd(r, self.bank.N) == 1:
                break
        print(f"  Генерирует r = {r}, взаимно простое с {self.bank.N}")
        
        # Вычисляем n̂ = f(n) * r^d mod N
        n_hat = (f_n * pow(r, self.bank.d, self.bank.N)) % self.bank.N
        print(f"  Вычисляет n̂ = {f_n} * {r} ^ {self.bank.d} mod {self.bank.N} = {n_hat}")
        print(f"  Отправляет n̂ = {n_hat} в банк")
        
        # Банк делает слепую подпись
        s_hat = self.bank.scheme3_issue_anonymous(self.name, n_hat)
        
        # Покупатель вычисляет s = ŝ * r^{-1} mod N
        r_inv = pow(r, -1, self.bank.N)
        s = (s_hat * r_inv) % self.bank.N
        print(f"  Вычисляет r⁻¹ = {r_inv} mod {self.bank.N}")
        print(f"  Вычисляет s = {s_hat} * {r_inv} mod {self.bank.N} = {s}")
        
        # Проверка: s^d mod N должно быть равно f(n)
        check = pow(s, self.bank.d, self.bank.N)
        print(f"  Проверка: {s} ^ {self.bank.d} mod {self.bank.N} = {check}")
        print(f"  Ожидается: f(n) = {f_n}")
        
        self.notes.append((n, s, 3))
        return n, s, r


def simple_hash(x: int) -> int:
    """
    Простая односторонняя функция (для демонстрации)
    В реальных системах используется криптографическая хеш-функция
    """
    # Используем простую нелинейную функцию
    # f(x) = (x^3 + 7*x + 1) mod N
    # Это не криптостойко, но демонстрирует идею
    return (x * x * x + 7 * x + 1) % 119


def demo_scheme1():
    """Демонстрация первой схемы (неанонимной)"""
    print("=" * 60)
    print("СХЕМА 1: Обычная подпись (НЕТ анонимности)")
    print("=" * 60)
    
    # Создаем банк
    bank = Bank(P = 17, Q = 7, c = 77)
    
    # Создаем участников
    alice = Buyer("Алиса", bank)
    shop = "Магазин"
    bank.create_account(alice.name, 1000)
    bank.create_account(shop, 0)
    
    # Получаем банкноту
    n, s = alice.scheme1_get_note()
    
    # Тратим в магазине
    bank.process_payment(n, s, shop, scheme = 1)
    
    print(f"\nБалансы:")
    print(f"  Алиса: {bank.get_balance('Алиса')}$")
    print(f"  Магазин: {bank.get_balance('Магазин')}$")
    print()
    
    # Показываем проблему: банк знает владельца
    print("❗ ПРОБЛЕМА: Банк знает, что банкнота 〈{n}, {s}〉 принадлежит Алисе")
    print("   Банк может отследить все покупки Алисы!\n")


def demo_scheme2():
    """Демонстрация второй схемы (анонимная, но уязвимая)"""
    print("=" * 60)
    print("СХЕМА 2: Слепая подпись (ЕСТЬ анонимность, НО уязвима к подделке)")
    print("=" * 60)
    
    bank = Bank(P = 17, Q = 7, c = 77)
    alice = Buyer("Алиса", bank)
    shop = "Магазин"
    bank.create_account(alice.name, 1000)
    bank.create_account(shop, 0)
    
    # Получаем анонимную банкноту
    n, s, r = alice.scheme2_get_note()
    
    # Тратим в магазине
    bank.process_payment(n, s, shop, scheme = 2)
    
    print(f"\nБалансы:")
    print(f"  Алиса: {bank.get_balance('Алиса')}$")
    print(f"  Магазин: {bank.get_balance('Магазин')}$")
    print()
    
    # Показываем уязвимость
    print("❗ УЯЗВИМОСТЬ: Мультипликативное свойство RSA")
    print("   Если злоумышленник имеет две банкноты:")
    
    # Демонстрируем подделку
    n1, s1, _ = alice.scheme2_get_note()
    n2, s2, _ = alice.scheme2_get_note()
    
    # Фальшивая банкнота
    n_fake = (n1 * n2) % bank.N
    s_fake = (s1 * s2) % bank.N
    print(f"\n  Злоумышленник создает фальшивую банкноту:")
    print(f"  n₁ = {n1}, s₁ = {s1}")
    print(f"  n₂ = {n2}, s₂ = {s2}")
    print(f"  n₃ = {n1} * {n2} mod {bank.N} = {n_fake}")
    print(f"  s₃ = {s1} * {s2} mod {bank.N} = {s_fake}")
    
    # Проверяем, что фальшивая банкнота проходит проверку
    print(f"\n  Проверка фальшивой банкноты:")
    is_valid = bank.verify_signature(n_fake, s_fake)
    print(f"  s₃ ^ {bank.d} mod {bank.N} = {pow(s_fake, bank.d, bank.N)}")
    print(f"  n₃ = {n_fake}")
    print(f"  Результат: {'✅ Подпись верна!' if is_valid else '❌ Неверна'}")
    if is_valid:
        print("  ❌ Банк НЕ СМОЖЕТ отличить фальшивую банкноту от настоящей!\n")


def demo_scheme3():
    """Демонстрация третьей схемы (безопасной)"""
    print("=" * 60)
    print("СХЕМА 3: Слепая подпись с хеш-функцией (БЕЗОПАСНАЯ)")
    print("=" * 60)
    
    bank = Bank(P = 17, Q = 7, c = 77)
    alice = Buyer("Алиса", bank)
    shop = "Магазин"
    bank.create_account(alice.name, 1000)
    bank.create_account(shop, 0)
    
    # Получаем анонимную банкноту с хешем
    n, s, r = alice.scheme3_get_note(simple_hash)
    
    # Тратим в магазине
    f_n = simple_hash(n)
    bank.process_payment(n, s, shop, scheme = 3, f_n = f_n)
    
    print(f"\nБалансы:")
    print(f"  Алиса: {bank.get_balance('Алиса')}$")
    print(f"  Магазин: {bank.get_balance('Магазин')}$")
    print()
    
    # Показываем, почему мультипликативность не работает
    print("✅ ПРЕИМУЩЕСТВО: Хеш-функция разрушает мультипликативность")
    print("   Для подделки нужно найти n₃ такое, что f(n₃) = f(n₁) * f(n₂)")
    print("   Это невозможно без обращения односторонней функции!\n")


def demo_multi_denomination():
    """Демонстрация использования разных номиналов"""
    print("=" * 60)
    print("БАНКНОТЫ РАЗНОГО НОМИНАЛА")
    print("=" * 60)
    
    # Банк с несколькими парами ключей
    print("Банк создает несколько пар ключей для разных номиналов:")
    
    # В реальной системе это были бы разные пары (P, Q, c)
    # Для демонстрации используем разные c
    bank = Bank(P = 17, Q = 7, c = 77)
    print(f"  Номинал 100$: c₁ = {bank.c}, d₁ = {bank.d}")
    
    # Создаем второй ключ для номинала 50$
    # (в реальной системе использовались бы разные простые числа)
    bank50 = Bank(P = 17, Q = 7, c = 55)  # Упрощенно: другой c
    print(f"  Номинал 50$:  c₂ = {bank50.c}, d₂ = {bank50.d}")
    
    print("\nПокупатель может запросить банкноту нужного номинала:")
    print("  - Для запроса 100$ используется пара (c₁, d₁)")
    print("  - Для запроса 50$ используется пара (c₂, d₂)")
    print("\nПри проверке банк перебирает все номиналы\n")


def demo_redudancy_method():
    """Демонстрация метода избыточности"""
    print("=" * 60)
    print("МЕТОД ИЗБЫТОЧНОСТИ (защита от мультипликативности)")
    print("=" * 60)
    
    print("Вместо хеш-функции можно использовать избыточность:")
    print("  - Номер банкноты содержит фиксированный заголовок")
    print("  - Например, старшие биты = 0xA5A5... (ID банка)")
    print("  - Младшие биты = случайное число")
    print()
    print("При перемножении двух номеров заголовок разрушается")
    print("Вероятность случайного совпадения с заголовком: 2 ^ {-512}")
    print("Это практически невозможно\n")


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("ЭЛЕКТРОННЫЕ ДЕНЬГИ - ДЕМОНСТРАЦИЯ ПРОТОКОЛОВ")
    print("=" * 60 + "\n")
    
    print("В этом примере используются параметры RSA из учебного примера:")
    print("  P = 17, Q = 7, N = 119, c = 77, d = 5\n")
    print("Демонстрируются все три схемы платежей:\n")
    
    # Запускаем все демонстрации
    demo_scheme1()
    demo_scheme2()
    demo_scheme3()
    demo_multi_denomination()
    demo_redudancy_method()
    
    print("=" * 60)
    print("ВЫВОД:")
    print("=" * 60)
    print("1. Схема 1: ❌ Нет анонимности")
    print("2. Схема 2: ✅ Анонимность, но ❌ Уязвима к подделке")
    print("3. Схема 3: ✅ Анонимность и ✅ Безопасность")
    print("\nВывод: Только схема 3 обеспечивает полную защиту")
    print("как обычные наличные деньги.")


if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    main()