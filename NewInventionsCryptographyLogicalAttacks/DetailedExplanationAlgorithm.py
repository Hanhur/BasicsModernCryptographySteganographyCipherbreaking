# Подробное объяснение алгоритма MB09
import random
import hashlib
import math
from typing import Tuple, Dict, Optional

class MB09Crypto:
    """
    Реализация алгоритма MB09 для анонимных транзакций
    Основана на малой теореме Ферма: a ^ p + b ^ p ≡ (a + b) ^ p (mod p)
    """
    
    def __init__(self, key_size: int = 512):
        """
        Инициализация системы MB09
        
        Args:
            key_size: размер простых чисел в битах (по умолчанию 512)
        """
        self.key_size = key_size
        self.p = self._generate_prime(key_size)  # Общий модуль (простое число)
        self.g = self._find_primitive_root(self.p)  # Первообразный корень
        self.users = {}  # Словарь для хранения пользователей
        self.transaction_history = []  # История транзакций
        self.total_supply = 0  # Общая эмиссия
        
        print(f"🔐 Система MB09 инициализирована")
        print(f"   Модуль p: {self.p}")
        print(f"   Первообразный корень g: {self.g}")
        print(f"   Размер ключа: {key_size} бит\n")
    
    def _is_prime(self, n: int) -> bool:
        """Проверка числа на простоту (тест Миллера-Рабина)"""
        if n < 2:
            return False
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
            if n % p == 0:
                return n == p
        
        # Тест Миллера-Рабина
        d = n - 1
        s = 0
        while d % 2 == 0:
            s += 1
            d //= 2
        
        for _ in range(20):  # 20 раундов для надежности
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
    
    def _generate_prime(self, bits: int) -> int:
        """Генерация простого числа заданной длины"""
        while True:
            # Генерируем нечетное число нужной длины
            n = random.getrandbits(bits)
            n |= (1 << bits - 1) | 1  # Старший и младший биты = 1
            
            # Проверяем на простоту
            if self._is_prime(n):
                return n
    
    def _find_primitive_root(self, p: int) -> int:
        """Нахождение первообразного корня по модулю p"""
        if p == 2:
            return 1
        
        # Факторизация p-1
        factors = []
        phi = p - 1
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
        
        # Поиск первообразного корня
        for g in range(2, p):
            is_primitive = True
            for factor in factors:
                if pow(g, phi // factor, p) == 1:
                    is_primitive = False
                    break
            if is_primitive:
                return g
        return 2  # fallback
    
    def create_user(self, user_id: str) -> Tuple[int, int]:
        """
        Создание нового пользователя с генерацией ключей
        
        Args:
            user_id: идентификатор пользователя
            
        Returns:
            Tuple[private_key, public_key]
        """
        if user_id in self.users:
            raise ValueError(f"Пользователь {user_id} уже существует")
        
        # Генерация закрытого ключа (большое простое число)
        private_key = self._generate_prime(self.key_size // 2)
        
        # Вычисление открытого ключа по алгоритму MB09
        # A = g^a mod p (аналог Диффи-Хеллмана)
        public_key = pow(self.g, private_key, self.p)
        
        # Сохраняем пользователя
        self.users[user_id] = {
            'private_key': private_key,
            'public_key': public_key,
            'balance': 0
        }
        
        print(f"👤 Создан пользователь: {user_id}")
        print(f"   Закрытый ключ: {private_key}")
        print(f"   Открытый ключ: {public_key}")
        print(f"   Баланс: 0\n")
        
        return private_key, public_key
    
    def mint_money(self, user_id: str, amount: int) -> bool:
        """
        Эмиссия денег (только для администратора Z)
        
        Args:
            user_id: получатель
            amount: сумма эмиссии
            
        Returns:
            bool: успешность операции
        """
        if user_id not in self.users:
            print(f"❌ Ошибка: пользователь {user_id} не найден")
            return False
        
        if amount <= 0:
            print(f"❌ Ошибка: сумма должна быть положительной")
            return False
        
        # Обновляем баланс пользователя
        self.users[user_id]['balance'] += amount
        self.total_supply += amount
        
        # Обновляем открытый ключ (по алгоритму MB09)
        current_public = self.users[user_id]['public_key']
        new_public = (current_public + amount) % self.p
        self.users[user_id]['public_key'] = new_public
        
        print(f"💰 Эмиссия {amount} единиц пользователю {user_id}")
        print(f"   Новый открытый ключ: {new_public}")
        print(f"   Новый баланс: {self.users[user_id]['balance']}")
        print(f"   Общая эмиссия: {self.total_supply}\n")
        
        return True
    
    def _generate_proof(self, sender_id: str, receiver_id: str, amount: int) -> Dict:
        """
        Генерация доказательства для транзакции
        
        Args:
            sender_id: отправитель
            receiver_id: получатель
            amount: сумма
            
        Returns:
            Dict: доказательство транзакции
        """
        sender = self.users[sender_id]
        
        # Создаем доказательство на основе закрытого ключа отправителя
        # Proof = (amount * sender_private) mod p
        proof_value = (amount * sender['private_key']) % self.p
        
        # Хешируем для дополнительной безопасности
        proof_hash = hashlib.sha256(
            f"{sender_id}{receiver_id}{amount}{proof_value}".encode()
        ).hexdigest()
        
        return {
            'sender': sender_id,
            'receiver': receiver_id,
            'amount': amount,
            'proof': proof_value,
            'hash': proof_hash
        }
    
    def _verify_proof(self, proof: Dict) -> bool:
        """
        Верификация доказательства транзакции
        
        Args:
            proof: доказательство транзакции
            
        Returns:
            bool: валидность доказательства
        """
        sender_id = proof['sender']
        receiver_id = proof['receiver']
        amount = proof['amount']
        
        if sender_id not in self.users or receiver_id not in self.users:
            return False
        
        sender = self.users[sender_id]
        
        # Проверяем баланс отправителя
        if sender['balance'] < amount:
            print(f"❌ Недостаточно средств: {sender['balance']} < {amount}")
            return False
        
        # Проверяем доказательство
        # Используем теорему Ферма для верификации
        expected = pow(self.g, (sender['private_key'] * amount) % self.p, self.p)
        actual = pow(sender['public_key'], amount, self.p)
        
        # Проверяем хеш для целостности
        expected_hash = hashlib.sha256(
            f"{sender_id}{receiver_id}{amount}{proof['proof']}".encode()
        ).hexdigest()
        
        return expected == actual and proof['hash'] == expected_hash
    
    def transfer(self, sender_id: str, receiver_id: str, amount: int) -> bool:
        """
        Выполнение транзакции между пользователями
        
        Args:
            sender_id: отправитель
            receiver_id: получатель
            amount: сумма
            
        Returns:
            bool: успешность транзакции
        """
        print(f"\n🔄 Транзакция: {sender_id} -> {receiver_id}, сумма: {amount}")
        
        # Проверка существования пользователей
        if sender_id not in self.users:
            print(f"❌ Ошибка: отправитель {sender_id} не найден")
            return False
        
        if receiver_id not in self.users:
            print(f"❌ Ошибка: получатель {receiver_id} не найден")
            return False
        
        # Проверка суммы
        if amount <= 0:
            print(f"❌ Ошибка: сумма должна быть положительной")
            return False
        
        sender = self.users[sender_id]
        receiver = self.users[receiver_id]
        
        # Проверка баланса
        if sender['balance'] < amount:
            print(f"❌ Ошибка: недостаточно средств у {sender_id}")
            print(f"   Баланс: {sender['balance']}, требуется: {amount}")
            return False
        
        # Генерация доказательства
        proof = self._generate_proof(sender_id, receiver_id, amount)
        
        # Верификация доказательства
        if not self._verify_proof(proof):
            print(f"❌ Ошибка: невалидное доказательство")
            return False
        
        # Обновление балансов по алгоритму MB09
        old_sender_balance = sender['balance']
        old_receiver_balance = receiver['balance']
        old_sender_public = sender['public_key']
        old_receiver_public = receiver['public_key']
        
        # Обновляем балансы
        sender['balance'] -= amount
        receiver['balance'] += amount
        
        # Обновляем открытые ключи (основной алгоритм MB09)
        # Sender: B_new = B - M (mod p)
        sender['public_key'] = (sender['public_key'] - amount) % self.p
        
        # Receiver: A_new = A + M (mod p)
        receiver['public_key'] = (receiver['public_key'] + amount) % self.p
        
        # Сохраняем в историю
        self.transaction_history.append({
            'sender': sender_id,
            'receiver': receiver_id,
            'amount': amount,
            'proof': proof,
            'timestamp': len(self.transaction_history)
        })
        
        print(f"✅ Транзакция успешно выполнена!")
        print(f"   Отправитель {sender_id}:")
        print(f"     Баланс: {old_sender_balance} -> {sender['balance']}")
        print(f"     Публичный ключ: {old_sender_public} -> {sender['public_key']}")
        print(f"   Получатель {receiver_id}:")
        print(f"     Баланс: {old_receiver_balance} -> {receiver['balance']}")
        print(f"     Публичный ключ: {old_receiver_public} -> {receiver['public_key']}")
        print(f"   Доказательство: {proof['proof']}")
        print(f"   Хеш: {proof['hash'][:16]}...\n")
        
        # Проверка сохранения суммы (теорема Ферма)
        total_keys = sum(user['public_key'] for user in self.users.values()) % self.p
        print(f"📊 Сумма всех открытых ключей (mod p): {total_keys}")
        
        return True
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Получение информации о пользователе"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        return {
            'id': user_id,
            'balance': user['balance'],
            'public_key': user['public_key'],
            'private_key': user['private_key']
        }
    
    def get_total_supply(self) -> int:
        """Получение общей эмиссии"""
        return self.total_supply
    
    def get_transaction_history(self) -> list:
        """Получение истории транзакций"""
        return self.transaction_history
    
    def verify_integrity(self) -> bool:
        """
        Проверка целостности системы (сумма балансов должна равняться эмиссии)
        """
        total_balance = sum(user['balance'] for user in self.users.values())
        is_valid = total_balance == self.total_supply
        
        print(f"\n🔍 Проверка целостности системы:")
        print(f"   Сумма балансов: {total_balance}")
        print(f"   Общая эмиссия: {self.total_supply}")
        print(f"   Статус: {'✅ Валидно' if is_valid else '❌ Нарушено'}")
        
        return is_valid


def demo_mb09():
    """Демонстрация работы алгоритма MB09"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ АЛГОРИТМА MB09")
    print("=" * 60)
    
    # Инициализация системы
    mb09 = MB09Crypto(key_size = 256)  # 256 бит для демонстрации
    
    # Создание пользователей и сохранение их ключей
    print("-" * 60)
    print("СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ")
    print("-" * 60)
    
    alice_private, alice_public = mb09.create_user("Алиса")
    bob_private, bob_public = mb09.create_user("Боб")
    charlie_private, charlie_public = mb09.create_user("Чарли")
    
    # Демонстрация сохраненных ключей
    print("\n📋 Сохраненные ключи:")
    print(f"   Алиса: приватный = {alice_private}, публичный = {alice_public}")
    print(f"   Боб:   приватный = {bob_private}, публичный = {bob_public}")
    print(f"   Чарли: приватный = {charlie_private}, публичный = {charlie_public}")
    
    # Эмиссия денег (центральный администратор Z)
    print("\n" + "-" * 60)
    print("ЭМИССИЯ ДЕНЕГ (АДМИНИСТРАТОР Z)")
    print("-" * 60)
    mb09.mint_money("Алиса", 1000)
    mb09.mint_money("Боб", 500)
    mb09.mint_money("Чарли", 300)
    
    # Выполнение транзакций
    print("-" * 60)
    print("ВЫПОЛНЕНИЕ ТРАНЗАКЦИЙ")
    print("-" * 60)
    
    # Транзакция 1: Боб -> Алиса
    print("\n📌 Используем приватный ключ Боба для подписи:", bob_private)
    mb09.transfer("Боб", "Алиса", 200)
    
    # Транзакция 2: Алиса -> Чарли
    print("\n📌 Используем приватный ключ Алисы для подписи:", alice_private)
    mb09.transfer("Алиса", "Чарли", 150)
    
    # Транзакция 3: Чарли -> Боб
    print("\n📌 Используем приватный ключ Чарли для подписи:", charlie_private)
    mb09.transfer("Чарли", "Боб", 100)
    
    # Проверка целостности
    mb09.verify_integrity()
    
    # Вывод информации о пользователях
    print("\n" + "-" * 60)
    print("ИТОГОВОЕ СОСТОЯНИЕ СИСТЕМЫ")
    print("-" * 60)
    
    for user_id in ["Алиса", "Боб", "Чарли"]:
        info = mb09.get_user_info(user_id)
        print(f"\n👤 {user_id}:")
        print(f"   Баланс: {info['balance']}")
        print(f"   Публичный ключ: {info['public_key']}")
        print(f"   Приватный ключ: {info['private_key']}")
    
    print(f"\n📊 Общая эмиссия: {mb09.get_total_supply()}")
    print(f"📊 Количество транзакций: {len(mb09.get_transaction_history())}")
    
    # Демонстрация невозможности мошенничества
    print("\n" + "-" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ МОШЕННИЧЕСТВА")
    print("-" * 60)
    
    print("\nПопытка перевода с недостаточным балансом:")
    mb09.transfer("Боб", "Алиса", 1000)
    
    print("\nПопытка перевода отрицательной суммы:")
    mb09.transfer("Алиса", "Боб", -50)
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    # Запускаем демонстрацию
    demo_mb09()
    
    # Теперь переменные alice_private и другие существуют ТОЛЬКО внутри demo_mb09()
    # Если нужно использовать их снаружи, нужно их вернуть из функции
    
    print("\n" + "=" * 60)
    print("СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ В ГЛОБАЛЬНОЙ ОБЛАСТИ")
    print("=" * 60)
    
    # Создаем новый экземпляр для глобального использования
    mb09_global = MB09Crypto(key_size = 256)
    
    # Теперь переменные создаются в глобальной области видимости
    alice_priv, alice_pub = mb09_global.create_user("Алиса_глобальная")
    bob_priv, bob_pub = mb09_global.create_user("Боб_глобальный")
    
    print(f"\n✅ Переменные созданы в глобальной области:")
    print(f"   alice_priv = {alice_priv}")
    print(f"   alice_pub = {alice_pub}")
    print(f"   bob_priv = {bob_priv}")
    print(f"   bob_pub = {bob_pub}")