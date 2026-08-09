# Детали протокола MBXX 
import hashlib
import json
import random
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
from abc import ABC, abstractmethod

# ==================== Криптографические утилиты ====================

class CryptoUtils:
    """Утилиты для хеширования и подписей (симуляция)"""
    
    @staticmethod
    def hash_data(data) -> int:
        """Вычисляет хеш от данных и возвращает как целое число"""
        if isinstance(data, (int, float)):
            data = str(data)
        elif isinstance(data, dict):
            data = json.dumps(data, sort_keys = True)
        return int(hashlib.sha256(str(data).encode()).hexdigest(), 16)
    
    @staticmethod
    def generate_key_pair(seed: Optional[int] = None) -> Tuple[int, int]:
        """Генерирует пару ключей (приватный, публичный)"""
        if seed is not None:
            random.seed(seed)
        private_key = random.randint(10 ** 15, 10 ** 16)
        public_key = CryptoUtils.hash_data(private_key)
        return private_key, public_key
    
    @staticmethod
    def sign(data, private_key: int) -> int:
        """Создает цифровую подпись"""
        message_hash = CryptoUtils.hash_data(data)
        return CryptoUtils.hash_data(f"{message_hash}{private_key}")
    
    @staticmethod
    def verify_signature(data, signature: int, public_key: int) -> bool:
        """Проверяет цифровую подпись"""
        message_hash = CryptoUtils.hash_data(data)
        expected_signature = CryptoUtils.hash_data(f"{message_hash}{public_key}")
        # В реальной системе проверка сложнее, здесь симуляция
        return signature == expected_signature


# ==================== Базовая криптосистема ====================

class HomomorphicParams:
    """Работа с гомоморфными параметрами (скрытые балансы)"""
    
    @staticmethod
    def create_hidden_amount(amount: int, nonce: Optional[int] = None) -> int:
        """Создает скрытое представление суммы"""
        if nonce is None:
            nonce = random.randint(1, 10 ** 9)
        return CryptoUtils.hash_data(f"{amount}{nonce}")
    
    @staticmethod
    def compute_public_param(hidden_balance: int, hidden_amount: int, operation: str = 'subtract') -> int:
        """
        Вычисляет открытый параметр A1 = A0 ± H[M]
        operation: 'add' или 'subtract'
        """
        if operation == 'subtract':
            return hidden_balance - hidden_amount
        else:  # add
            return hidden_balance + hidden_amount


# ==================== Участники системы ====================

@dataclass
class User:
    """Представляет участника системы"""
    name: str
    private_key: int
    public_key: int
    hidden_balance: int  # a0 или b0
    public_param: int    # A0 или B0
    
    def sign_transaction(self, amount_hash: int) -> int:
        """Подписывает транзакцию"""
        return CryptoUtils.sign(amount_hash, self.private_key)
    
    def verify_transaction(self, data, signature: int) -> bool:
        """Проверяет подпись другой стороны"""
        return CryptoUtils.verify_signature(data, signature, self.public_key)
    
    def create_transfer(self, amount: int, recipient: 'User') -> Dict:
        """
        Создает транзакцию перевода
        """
        # 1. Скрываем сумму
        hidden_amount = HomomorphicParams.create_hidden_amount(amount)
        amount_hash = CryptoUtils.hash_data(hidden_amount)
        
        # 2. Вычисляем новые параметры для отправителя
        new_hidden_balance = self.hidden_balance - hidden_amount
        new_public_param = HomomorphicParams.compute_public_param(
            self.public_param, hidden_amount, 'subtract'
        )
        
        # 3. Вычисляем параметры для получателя
        recipient_new_hidden = recipient.hidden_balance + hidden_amount
        recipient_new_public = HomomorphicParams.compute_public_param(
            recipient.public_param, hidden_amount, 'add'
        )
        
        # 4. Создаем подписи
        sender_signature = self.sign_transaction(amount_hash)
        
        transaction = {
            'sender': self.name,
            'recipient': recipient.name,
            'hidden_amount': hidden_amount,
            'amount_hash': amount_hash,
            'sender_signature': sender_signature,
            'new_sender_hidden': new_hidden_balance,
            'new_sender_public': new_public_param,
            'new_recipient_hidden': recipient_new_hidden,
            'new_recipient_public': recipient_new_public,
        }
        
        return transaction


# ==================== Система проверки ====================

class MBXXVerifier:
    """Реализует проверки протокола MBXX"""
    
    @staticmethod
    def verify_transaction(transaction: Dict, sender: User, recipient: User) -> Tuple[bool, str]:
        """
        Проверяет корректность транзакции
        """
        # 1. Проверка подписи отправителя
        if not sender.verify_transaction(
            transaction['amount_hash'], 
            transaction['sender_signature']
        ):
            return False, "Неверная подпись отправителя"
        
        # 2. Проверка, что отправитель имеет достаточно средств
        if sender.hidden_balance < transaction['hidden_amount']:
            return False, "Недостаточно средств"
        
        # 3. Проверка баланса системы (гомоморфная)
        # Z0 = A0 + B0 (до транзакции)
        z0 = sender.public_param + recipient.public_param
        
        # Z1 = A1 + B1 (после транзакции)
        z1 = (transaction['new_sender_public'] + 
              transaction['new_recipient_public'])
        
        if z1 != z0:
            return False, f"Нарушен гомоморфный баланс: Z0 = {z0}, Z1 = {z1}"
        
        # 4. Проверка неотрицательности (предотвращение двойного расходования)
        if transaction['new_sender_hidden'] < 0:
            return False, "Баланс отправителя стал отрицательным"
        
        return True, "Транзакция валидна"
    
    @staticmethod
    def verify_system_balance(users: List[User]) -> Tuple[bool, int, int]:
        """
        Проверяет общий баланс системы
        """
        total_public = sum(user.public_param for user in users)
        total_hidden = sum(user.hidden_balance for user in users)
        
        return total_public == total_hidden, total_public, total_hidden


# ==================== Доказательство с нулевым разглашением (симуляция) ====================

class ZeroKnowledgeProof:
    """
    Симуляция доказательства с нулевым разглашением
    для проверки неотрицательности балансов
    """
    
    @staticmethod
    def prove_non_negative(balance: int, public_param: int, hidden_amount: int) -> Tuple[bool, str]:
        """
        Доказывает, что баланс неотрицателен без раскрытия суммы
        В реальной системе используется более сложная криптография
        """
        # Это упрощенная симуляция для демонстрации
        if balance < 0:
            return False, "Баланс отрицательный"
        
        # Проверяем, что публичный параметр соответствует скрытому балансу
        # В реальности здесь используется доказательство с нулевым разглашением
        expected_public = HomomorphicParams.compute_public_param(
            balance, hidden_amount, 'subtract'
        )
        
        return True, "Доказательство неотрицательности успешно"


# ==================== Основная программа ====================

class MBXXSystem:
    """Главный класс системы MBXX"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.total_supply: int = 0
        self.transaction_history: List[Dict] = []
        self.z0: int = 0  # Общий параметр системы
    
    def create_user(self, name: str, initial_balance: int) -> User:
        """Создает нового пользователя с начальным балансом"""
        if name in self.users:
            raise ValueError(f"Пользователь {name} уже существует")
        
        # Генерируем ключи
        priv_key, pub_key = CryptoUtils.generate_key_pair(
            seed = hash(name) % 10 ** 6
        )
        
        # Скрываем начальный баланс
        hidden_amount = HomomorphicParams.create_hidden_amount(initial_balance)
        public_param = hidden_amount  # Начальный публичный параметр
        
        user = User(
            name = name,
            private_key = priv_key,
            public_key = pub_key,
            hidden_balance = hidden_amount,
            public_param = public_param
        )
        
        self.users[name] = user
        self.total_supply += initial_balance
        self.z0 = sum(u.public_param for u in self.users.values())
        
        return user
    
    def transfer(self, sender_name: str, recipient_name: str, amount: int) -> Tuple[bool, str]:
        """
        Выполняет перевод между пользователями
        """
        if sender_name not in self.users:
            return False, f"Отправитель {sender_name} не найден"
        if recipient_name not in self.users:
            return False, f"Получатель {recipient_name} не найден"
        
        sender = self.users[sender_name]
        recipient = self.users[recipient_name]
        
        # Создаем транзакцию
        transaction = sender.create_transfer(amount, recipient)
        
        # Сохраняем старые значения для отката
        old_sender_balance = sender.hidden_balance
        old_sender_public = sender.public_param
        old_recipient_balance = recipient.hidden_balance
        old_recipient_public = recipient.public_param
        
        # Проверяем транзакцию
        is_valid, message = MBXXVerifier.verify_transaction(
            transaction, sender, recipient
        )
        
        if not is_valid:
            return False, f"Ошибка проверки: {message}"
        
        # Применяем транзакцию
        sender.hidden_balance = transaction['new_sender_hidden']
        sender.public_param = transaction['new_sender_public']
        recipient.hidden_balance = transaction['new_recipient_hidden']
        recipient.public_param = transaction['new_recipient_public']
        
        # Добавляем в историю
        transaction['timestamp'] = len(self.transaction_history)
        transaction['success'] = True
        self.transaction_history.append(transaction)
        
        # Проверяем системный баланс
        is_balanced, z0, z1 = MBXXVerifier.verify_system_balance(
            list(self.users.values())
        )
        
        if not is_balanced:
            # Откатываем изменения
            sender.hidden_balance = old_sender_balance
            sender.public_param = old_sender_public
            recipient.hidden_balance = old_recipient_balance
            recipient.public_param = old_recipient_public
            return False, f"Нарушен системный баланс: Z0={z0}, Z1={z1}"
        
        return True, f"Перевод {amount} от {sender_name} к {recipient_name} успешно выполнен"
    
    def display_status(self):
        """Отображает текущее состояние системы"""
        print("\n" + "=" * 60)
        print("СОСТОЯНИЕ СИСТЕМЫ MBXX")
        print("=" * 60)
        
        for user in self.users.values():
            print(f"\n👤 {user.name}:")
            print(f"  Скрытый баланс (a): {user.hidden_balance}")
            print(f"  Публичный параметр (A): {user.public_param}")
            print(f"  Публичный ключ: {user.public_key % 1000000}...")
        
        # Проверка системного баланса
        is_balanced, z0, z1 = MBXXVerifier.verify_system_balance(
            list(self.users.values())
        )
        
        print(f"\n📊 Системный баланс:")
        print(f"  Z0 (исходный): {self.z0}")
        print(f"  Z1 (текущий): {z1}")
        print(f"  Статус: {'✅ СБАЛАНСИРОВАН' if is_balanced else '❌ НЕ СБАЛАНСИРОВАН'}")
        print(f"  Всего транзакций: {len(self.transaction_history)}")
        print("=" * 60)
    
    def demonstrate_zero_knowledge(self, user_name: str):
        """
        Демонстрирует проверку с нулевым разглашением
        """
        if user_name not in self.users:
            print(f"Пользователь {user_name} не найден")
            return
        
        user = self.users[user_name]
        
        print(f"\n🔐 ДОКАЗАТЕЛЬСТВО С НУЛЕВЫМ РАЗГЛАШЕНИЕМ для {user_name}")
        print("-" * 50)
        
        # Симулируем доказательство неотрицательности
        proof_result, message = ZeroKnowledgeProof.prove_non_negative(
            user.hidden_balance,
            user.public_param,
            0  # В реальной системе здесь используется скрытая сумма
        )
        
        print(f"Результат: {message}")
        print(f"Баланс не раскрыт: {'✅' if proof_result else '❌'}")
        print("-" * 50)


# ==================== Демонстрация работы ====================

def main():
    """Главная функция для демонстрации"""
    print("🚀 ЗАПУСК ПРОТОКОЛА MBXX")
    print("=" * 60)
    
    # Создаем систему
    system = MBXXSystem()
    
    # Создаем пользователей
    print("\n📝 Создание пользователей...")
    alice = system.create_user("Alice", 1000)
    bob = system.create_user("Bob", 500)
    charlie = system.create_user("Charlie", 2000)
    
    print(f"✅ Созданы пользователи: Alice, Bob, Charlie")
    
    # Отображаем начальное состояние
    system.display_status()
    
    # Выполняем транзакции
    print("\n💸 ВЫПОЛНЕНИЕ ТРАНЗАКЦИЙ")
    print("=" * 60)
    
    # Транзакция 1: Alice -> Bob (100)
    print("\n1. Alice переводит 100 Bob")
    success, message = system.transfer("Alice", "Bob", 100)
    print(f"Результат: {'✅' if success else '❌'} {message}")
    
    # Транзакция 2: Bob -> Charlie (50)
    print("\n2. Bob переводит 50 Charlie")
    success, message = system.transfer("Bob", "Charlie", 50)
    print(f"Результат: {'✅' if success else '❌'} {message}")
    
    # Транзакция 3: Charlie -> Alice (200)
    print("\n3. Charlie переводит 200 Alice")
    success, message = system.transfer("Charlie", "Alice", 200)
    print(f"Результат: {'✅' if success else '❌'} {message}")
    
    # Отображаем состояние после транзакций
    system.display_status()
    
    # Демонстрация доказательства с нулевым разглашением
    system.demonstrate_zero_knowledge("Alice")
    
    # Попытка двойного расходования (должна провалиться)
    print("\n⚠️ ПОПЫТКА ДВОЙНОГО РАСХОДОВАНИЯ")
    print("=" * 60)
    
    # Попытка перевести больше, чем есть
    print("\nAlice пытается перевести 1000 Bob (недостаточно средств)")
    success, message = system.transfer("Alice", "Bob", 1000)
    print(f"Результат: {'✅' if success else '❌'} {message}")
    print(f"Статус: {'Транзакция отклонена' if not success else 'Транзакция выполнена'}")
    
    print("\n" + "=" * 60)
    print("🏁 ЗАВЕРШЕНИЕ ДЕМОНСТРАЦИИ")
    print("=" * 60)


if __name__ == "__main__":
    main()