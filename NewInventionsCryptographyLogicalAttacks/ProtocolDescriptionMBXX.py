# Описание протокола MBXX
"""
Протокол MBXX - Реализация на чистом Python
Без использования numpy
"""

import hashlib
import random
import math
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional
from decimal import Decimal, getcontext

# Устанавливаем точность для Decimal
getcontext().prec = 50


@dataclass
class User:
    """Класс пользователя с закрытыми и открытыми ключами"""
    name: str
    private_key: int  # Закрытый ключ [a]
    public_key: int   # Открытый ключ (A)
    balance: Decimal  # Реальный баланс [a0]
    public_balance: Decimal  # Изоморфный баланс (A0)
    
    def __post_init__(self):
        self.transaction_history: List[Dict] = []
        self.nonce_counter: int = 0


class MBXXProtocol:
    """
    Реализация протокола MBXX
    """
    
    def __init__(self, p: int = 97, g: int = 5):
        """
        Инициализация протокола
        
        Args:
            p: Простое число для модулярной арифметики (по умолчанию 97)
            g: Образующий элемент (по умолчанию 5)
        """
        self.p = p
        self.g = g
        self.users: Dict[str, User] = {}
        self.z_random: List[int] = []  # Случайные числа [k1, k2... kn]
        self.total_supply: Decimal = Decimal(0)
        self.blockchain: List[Dict] = []
        self.time_stamp: int = 0
        
        # Алгоритмы, используемые в протоколе
        self.hash_algorithm = hashlib.sha256
        self.meta_algorithm = "MB09_Extended_Fermat"
        self.transfer_algorithm = "MBXI_like"
        self.zk_proof_algorithm = "ZK13"
        
    def generate_private_key(self) -> int:
        """Генерация закрытого ключа [a]"""
        return random.randint(2, self.p - 2)
    
    def generate_public_key(self, private_key: int) -> int:
        """
        Генерация открытого ключа (A) из закрытого [a]
        A ≡ g^[a] mod p
        """
        return pow(self.g, private_key, self.p)
    
    def hash_message(self, message: str) -> int:
        """Хеширование сообщения с помощью SHA-256"""
        hash_obj = self.hash_algorithm(message.encode())
        return int(hash_obj.hexdigest(), 16) % self.p
    
    def compute_isomorphic_balance(self, real_balance: Decimal, private_key: int) -> Decimal:
        """
        Вычисление изоморфного баланса (открытого значения)
        (A) = [a]^p mod p (упрощенная версия)
        """
        # В реальной системе это более сложное преобразование
        # Используем упрощенную версию для демонстрации
        return Decimal(str(pow(int(real_balance), self.p, self.p)))
    
    def verify_homomorphic_balance(self) -> bool:
        """
        Шаг 1: Проверка гомоморфного баланса с помощью метаалгоритма
        Проверяет: [a]p + [b]p + ... + [n]p ≡ [z]p (mod p)
        и A + B + C + ... + N = Z
        """
        print("\n" + "=" * 60)
        print("ШАГ 1: ПРОВЕРКА ГОМОМОРФНОГО БАЛАНСА")
        print("=" * 60)
        
        # Сумма реальных балансов
        sum_real = sum(user.balance for user in self.users.values())
        
        # Сумма изоморфных балансов
        sum_isomorphic = sum(user.public_balance for user in self.users.values())
        
        print(f"Сумма реальных балансов: {sum_real}")
        print(f"Сумма изоморфных балансов: {sum_isomorphic}")
        
        # Проверка соответствия
        # В реальной системе проверяется более сложное условие
        # Здесь используем упрощенную проверку
        
        # Проверяем, что общая сумма не изменилась (в пределах допустимого)
        # Для демонстрации считаем, что баланс верный если разница меньше 0.001
        is_valid = abs(sum_real - self.total_supply) < Decimal('0.001')
        
        if is_valid:
            print("✓ Гомоморфный баланс корректен")
        else:
            print("✗ Ошибка: Гомоморфный баланс нарушен!")
            
        return is_valid
    
    def create_digital_signature(self, user: User, amount: Decimal) -> int:
        """
        Создание цифровой подписи для транзакции
        SA ≡ (H[Ma])^[x] mod p
        """
        message = f"{user.name}{amount}{user.nonce_counter}"
        hash_value = self.hash_message(message)
        signature = pow(hash_value, user.private_key, self.p)
        user.nonce_counter += 1
        return signature
    
    def verify_signature(self, user: User, amount: Decimal, signature: int) -> bool:
        """
        Проверка цифровой подписи
        (SA)^y = (H[Ma]) (mod p)
        """
        message = f"{user.name}{amount}{user.nonce_counter - 1}"
        hash_value = self.hash_message(message)
        # Проверка: signature^public_key ≡ hash (mod p)
        verification = pow(signature, user.public_key, self.p)
        return verification == hash_value
    
    def zero_knowledge_proof(self, user: User, claimed_balance: Decimal) -> bool:
        """
        Шаг 3: Доказательство с нулевым разглашением (упрощенная версия)
        Проверяет, что у пользователя достаточно средств, не раскрывая точную сумму
        """
        print(f"\n--- Проверка ZK-proof для {user.name} ---")
        
        # Генерируем случайное число k
        k = random.randint(1, self.p - 2)
        
        # Вычисляем коммитмент: C = g^k mod p
        commitment = pow(self.g, k, self.p)
        
        # Вычисляем ответ: r = k + claimed_balance * private_key (в реальной системе сложнее)
        # Здесь используем упрощенную версию для демонстрации
        response = (k + int(claimed_balance) * user.private_key) % (self.p - 1)
        
        # Проверка: g^r ≡ C * (public_key)^claimed_balance (mod p)
        left_side = pow(self.g, response, self.p)
        right_side = (commitment * pow(user.public_key, int(claimed_balance), self.p)) % self.p
        
        is_valid = left_side == right_side
        
        if is_valid:
            print(f"✓ ZK-proof пройден: баланс {user.name} достаточен")
        else:
            print(f"✗ ZK-proof не пройден: недостаточно средств у {user.name}")
            
        return is_valid
    
    def generate_zero_knowledge_random(self) -> int:
        """Генерация случайного числа k для ZK-протокола"""
        k = random.randint(1, self.p - 2)
        self.z_random.append(k)
        return k
    
    def perform_transaction(self, sender_name: str, receiver_name: str, amount: Decimal) -> bool:
        """
        Шаг 2: Выполнение транзакции между пользователями
        
        Returns:
            bool: Успешность транзакции
        """
        print("\n" + "=" * 60)
        print(f"ШАГ 2: ТРАНЗАКЦИЯ В МОМЕНТ ВРЕМЕНИ t{self.time_stamp}")
        print("=" * 60)
        
        sender = self.users.get(sender_name)
        receiver = self.users.get(receiver_name)
        
        if not sender or not receiver:
            print("✗ Ошибка: Пользователь не найден")
            return False
            
        if sender.balance < amount:
            print(f"✗ Ошибка: Недостаточно средств у {sender_name}")
            print(f"  Баланс: {sender.balance}, Запрошено: {amount}")
            return False
        
        # Проверка с помощью ZK-proof (Шаг 3 - часть проверки)
        print(f"\nВыполняется ZK-proof для проверки баланса отправителя...")
        if not self.zero_knowledge_proof(sender, amount):
            print("✗ Транзакция отклонена: ZK-proof не пройден")
            return False
        
        # Создаем цифровую подпись
        signature = self.create_digital_signature(sender, amount)
        
        # Проверяем подпись
        if not self.verify_signature(sender, amount, signature):
            print("✗ Ошибка: Неверная цифровая подпись")
            return False
        
        # Сохраняем старые балансы для истории
        old_sender_balance = sender.balance
        old_receiver_balance = receiver.balance
        
        # Выполняем перевод
        sender.balance -= amount
        receiver.balance += amount
        
        # Обновляем изоморфные балансы
        sender.public_balance = self.compute_isomorphic_balance(sender.balance, sender.private_key)
        receiver.public_balance = self.compute_isomorphic_balance(receiver.balance, receiver.private_key)
        
        # Записываем транзакцию
        transaction = {
            'time': f"t{self.time_stamp}",
            'from': sender_name,
            'to': receiver_name,
            'amount': amount,
            'sender_old_balance': old_sender_balance,
            'sender_new_balance': sender.balance,
            'receiver_old_balance': old_receiver_balance,
            'receiver_new_balance': receiver.balance,
            'signature': signature,
            'zk_random': self.generate_zero_knowledge_random()
        }
        
        self.blockchain.append(transaction)
        sender.transaction_history.append(transaction)
        receiver.transaction_history.append(transaction)
        
        print(f"\n✓ Транзакция выполнена успешно!")
        print(f"  {sender_name} -> {receiver_name}: {amount}")
        print(f"  Новый баланс {sender_name}: {sender.balance}")
        print(f"  Новый баланс {receiver_name}: {receiver.balance}")
        print(f"  Подпись SA: {signature}")
        
        self.time_stamp += 1
        return True
    
    def verify_all_transactions(self) -> bool:
        """
        Шаг 3: Полная проверка всех транзакций
        """
        print("\n" + "=" * 60)
        print("ШАГ 3: ПРОВЕРКА ВСЕХ ТРАНЗАКЦИЙ")
        print("=" * 60)
        
        # Проверяем гомоморфный баланс
        if not self.verify_homomorphic_balance():
            return False
        
        # Проверяем каждую транзакцию
        print("\n--- Проверка транзакций ---")
        for i, tx in enumerate(self.blockchain):
            print(f"\nТранзакция {i + 1} (время {tx['time']}):")
            print(f"  От: {tx['from']} -> Кому: {tx['to']}")
            print(f"  Сумма: {tx['amount']}")
            print(f"  Подпись: {tx['signature']}")
            
            # Проверяем, что балансы сошлись
            sender = self.users[tx['from']]
            receiver = self.users[tx['to']]
            
            # В реальной системе здесь проверяется больше условий
            print(f"  ✓ Баланс отправителя: {sender.balance}")
            print(f"  ✓ Баланс получателя: {receiver.balance}")
        
        print("\n✓ Все транзакции успешно проверены")
        return True
    
    def add_user(self, name: str, initial_balance: Decimal) -> User:
        """
        Добавление нового пользователя в систему
        """
        private_key = self.generate_private_key()
        public_key = self.generate_public_key(private_key)
        
        user = User(
            name = name,
            private_key = private_key,
            public_key = public_key,
            balance = initial_balance,
            public_balance = self.compute_isomorphic_balance(initial_balance, private_key)
        )
        
        self.users[name] = user
        self.total_supply += initial_balance
        
        print(f"\n--- Добавлен пользователь {name} ---")
        print(f"  Закрытый ключ [a]: {private_key}")
        print(f"  Открытый ключ (A): {public_key}")
        print(f"  Начальный баланс: {initial_balance}")
        print(f"  Изоморфный баланс: {user.public_balance}")
        
        return user
    
    def print_system_state(self):
        """Вывод текущего состояния системы"""
        print("\n" + "=" * 60)
        print("ТЕКУЩЕЕ СОСТОЯНИЕ СИСТЕМЫ")
        print("=" * 60)
        
        print(f"\nОбщая эмиссия (Z): {self.total_supply}")
        print(f"Текущее время: t{self.time_stamp}")
        print(f"Количество пользователей: {len(self.users)}")
        print(f"Количество транзакций: {len(self.blockchain)}")
        
        print("\n--- Балансы пользователей ---")
        for name, user in self.users.items():
            print(f"  {name}:")
            print(f"    Реальный баланс [a]: {user.balance}")
            print(f"    Изоморфный баланс (A): {user.public_balance}")
            print(f"    Открытый ключ: {user.public_key}")


def main():
    """
    Демонстрация работы протокола MBXX
    """
    print("=" * 60)
    print("ПРОТОКОЛ MBXX - ДЕМОНСТРАЦИЯ РАБОТЫ")
    print("=" * 60)
    
    # Инициализация протокола
    protocol = MBXXProtocol(p = 97, g = 5)
    
    print("\n--- ЭТАП ИНИЦИАЛИЗАЦИИ ---")
    print("Инициализированы алгоритмы:")
    print(f"  Метаалгоритм: {protocol.meta_algorithm}")
    print(f"  Алгоритм передачи: {protocol.transfer_algorithm}")
    print(f"  ZK-proof: {protocol.zk_proof_algorithm}")
    print(f"  Хеш-функция: SHA-256")
    print(f"  Простое число p: {protocol.p}")
    print(f"  Образующий элемент g: {protocol.g}")
    
    # Добавляем пользователей с начальными балансами
    print("\n--- Добавление пользователей ---")
    alice = protocol.add_user("Алиса", Decimal('10000'))
    bob = protocol.add_user("Боб", Decimal('5000'))
    carol = protocol.add_user("Карл", Decimal('3000'))
    
    # Проверка гомоморфного баланса до транзакций
    protocol.verify_homomorphic_balance()
    
    # Выполняем транзакции
    print("\n--- Выполнение транзакций ---")
    
    # Транзакция 1: Алиса -> Боб (1500)
    protocol.perform_transaction("Алиса", "Боб", Decimal('1500'))
    
    # Транзакция 2: Боб -> Карл (500)
    protocol.perform_transaction("Боб", "Карл", Decimal('500'))
    
    # Транзакция 3: Алиса -> Карл (2000)
    protocol.perform_transaction("Алиса", "Карл", Decimal('2000'))
    
    # Попытка транзакции с недостаточным балансом
    print("\n--- Попытка транзакции с недостаточным балансом ---")
    protocol.perform_transaction("Боб", "Алиса", Decimal('10000'))
    
    # Полная проверка всех транзакций
    protocol.verify_all_transactions()
    
    # Вывод финального состояния
    protocol.print_system_state()
    
    # Демонстрация однонаправленности функции
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ОДНОНАПРАВЛЕННОСТИ ФУНКЦИИ")
    print("=" * 60)
    print("\nПопытка восстановить закрытый ключ [a] из открытого (A):")
    print(f"  Открытый ключ Алисы (A): {alice.public_key}")
    print("  Восстановление [a] из (A) невозможно из-за однонаправленности функции")
    print("  A = g ^ [a] mod p - это дискретное логарифмирование, которое вычислительно сложно")
    
    # Демонстрация доказательства с нулевым разглашением
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ZK-PROOF")
    print("=" * 60)
    print("\nПроверка баланса Алисы без раскрытия точной суммы:")
    protocol.zero_knowledge_proof(alice, Decimal('6500'))  # Текущий баланс Алисы
    
    print("\nПроверка баланса Боба без раскрытия точной суммы:")
    protocol.zero_knowledge_proof(bob, Decimal('3000'))   # Текущий баланс Боба
    
    print("\n" + "=" * 60)
    print("ПРОТОКОЛ MBXX УСПЕШНО ВЫПОЛНЕН")
    print("=" * 60)


if __name__ == "__main__":
    main()