# Открытые параметры
import hashlib
import random
import math

# =============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# =============================================

def is_prime(n, k = 10):
    """Простая проверка на простоту (Miller-Rabin)"""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    # Miller-Rabin
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits = 16):
    """Генерация простого числа заданной битности"""
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n

def primitive_root(p):
    """Поиск первообразного корня по модулю p"""
    if p == 2:
        return 1
    # Факторизация p-1
    phi = p - 1
    factors = []
    temp = phi
    i = 2
    while i * i <= temp:
        if temp % i == 0:
            factors.append(i)
            while temp % i == 0:
                temp //= i
        i += 1
    if temp > 1:
        factors.append(temp)
    
    # Поиск корня
    for g in range(2, p):
        ok = True
        for q in factors:
            if pow(g, phi // q, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None

def mod_inv(a, p):
    """Обратное число по модулю p (расширенный алгоритм Евклида)"""
    a = a % p
    # Для простого p можно использовать малую теорему Ферма
    return pow(a, -1, p)  # Python 3.8+ поддерживает pow(a, -1, mod)

# =============================================
# ПРОТОКОЛ MB09
# =============================================

class MB09Protocol:
    def __init__(self, bits = 16):
        """Инициализация системы с простым числом и генератором"""
        self.bits = bits
        self.p = generate_prime(bits)
        self.g = primitive_root(self.p)
        print(f"[SYSTEM] p = {self.p}, g = {self.g}")
        
        # Хранилище пользователей
        self.users = {}
        
        # Суммарный открытый ключ (Z)
        self.Z = 0
        
    def register_user(self, name, initial_balance = 0):
        """Регистрация пользователя с генерацией ключей"""
        # Генерация закрытого ключа (секретный параметр)
        private_key = random.randrange(2, self.p - 1)
        
        # Генерация открытого ключа
        public_key = pow(self.g, private_key, self.p)
        
        # Добавляем пользователя
        self.users[name] = {
            'private': private_key,
            'public': public_key,
            'balance': initial_balance
        }
        
        # Обновляем суммарный открытый ключ (Z)
        self.Z = (self.Z + public_key) % self.p
        
        print(f"[REGISTER] {name}: private = [{private_key}], public = ({public_key}), balance = {initial_balance}")
        return public_key
    
    def compute_shared_secret(self, user1_private, user2_public):
        """Вычисление общего секрета по протоколу Диффи-Хеллмана"""
        return pow(user2_public, user1_private, self.p)
    
    def encrypt_message(self, sender_name, receiver_name, message):
        """
        Шифрование сообщения [M] с использованием закрытого ключа отправителя
        и открытого ключа получателя
        """
        sender_private = self.users[sender_name]['private']
        receiver_public = self.users[receiver_name]['public']
        
        # Шаг 1: Вычисляем общий секрет [KA]
        K = self.compute_shared_secret(sender_private, receiver_public)
        
        # Шаг 2: Шифруем сообщение (мультипликативное шифрование)
        c = (message * K) % self.p
        
        print(f"[ENCRYPT] {sender_name} -> {receiver_name}: M = [{message}], K = [{K}], c = ({c})")
        return c, K
    
    def decrypt_message(self, receiver_name, sender_name, ciphertext, sender_public):
        """
        Расшифровка сообщения с использованием закрытого ключа получателя
        и открытого ключа отправителя
        """
        receiver_private = self.users[receiver_name]['private']
        
        # Шаг 1: Вычисляем общий секрет [KB]
        K = self.compute_shared_secret(receiver_private, sender_public)
        
        # Шаг 2: Расшифровываем
        K_inv = mod_inv(K, self.p)
        message = (ciphertext * K_inv) % self.p
        
        print(f"[DECRYPT] {receiver_name} <- {sender_name}: c = ({ciphertext}), K = [{K}], M = [{message}]")
        return message, K
    
    def compute_hash(self, value):
        """Вычисление хеша (Hm) для гомоморфного баланса"""
        # Используем SHA-256 и берем остаток от деления на p
        hash_bytes = hashlib.sha256(str(value).encode()).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        return hash_int % self.p
    
    def transfer_money(self, sender_name, receiver_name, amount):
        """
        Полная транзакция с проверкой гомоморфного баланса
        (электронные деньги)
        """
        print("\n" + "=" * 60)
        print(f"ТРАНЗАКЦИЯ: {sender_name} -> {receiver_name} на сумму [{amount}]")
        print("=" * 60)
        
        # Проверка достаточности средств
        if self.users[sender_name]['balance'] < amount:
            print(f"[ERROR] Недостаточно средств у {sender_name}")
            return False
        
        # ---- ШАГ 1: Шифрование ----
        c, K_A = self.encrypt_message(sender_name, receiver_name, amount)
        
        # Получаем публичный ключ отправителя для Боба
        sender_public = self.users[sender_name]['public']
        
        # ---- ШАГ 2: Дешифрование ----
        decrypted_amount, K_B = self.decrypt_message(
            receiver_name, sender_name, c, sender_public
        )
        
        # Проверка корректности расшифровки
        if decrypted_amount != amount:
            print(f"[ERROR] Расшифровка не удалась: {decrypted_amount} != {amount}")
            return False
        
        # ---- ШАГ 3: Гомоморфный баланс ----
        # Вычисляем хеш суммы (Hm)
        Hm = self.compute_hash(amount)
        print(f"[HASH] Hm = {Hm}")
        
        # Сохраняем старые значения для проверки
        old_sender_balance = self.users[sender_name]['balance']
        old_receiver_balance = self.users[receiver_name]['balance']
        old_Z = self.Z
        
        # Обновляем балансы (в закрытых ключах - симулируем)
        self.users[sender_name]['balance'] -= amount
        self.users[receiver_name]['balance'] += amount
        
        # Обновляем открытые ключи (гомоморфно)
        # (A ± Hm) + (B ± Hm) = (Z)
        sender_public_new = (self.users[sender_name]['public'] - Hm) % self.p
        receiver_public_new = (self.users[receiver_name]['public'] + Hm) % self.p
        Z_new = (sender_public_new + receiver_public_new) % self.p
        
        # Проверка гомоморфного баланса
        # Для остальных пользователей их открытые ключи не меняются
        other_users_sum = 0
        for name, data in self.users.items():
            if name not in [sender_name, receiver_name]:
                other_users_sum = (other_users_sum + data['public']) % self.p
        
        Z_calculated = (sender_public_new + receiver_public_new + other_users_sum) % self.p
        
        print(f"[BALANCE_CHECK] (A±Hm) = ({sender_public_new}), (B±Hm) = ({receiver_public_new})")
        print(f"[BALANCE_CHECK] Z_old = {old_Z}, Z_new = {Z_calculated}")
        
        if Z_calculated == old_Z:
            print(f"[SUCCESS] ✓ Гомоморфный баланс сохранен! Z = {Z_calculated}")
            # Обновляем глобальный Z
            self.Z = Z_calculated
            # Обновляем публичные ключи в системе
            self.users[sender_name]['public'] = sender_public_new
            self.users[receiver_name]['public'] = receiver_public_new
            return True
        else:
            print(f"[FAIL] ✗ Гомоморфный баланс нарушен!")
            # Откатываем изменения
            self.users[sender_name]['balance'] = old_sender_balance
            self.users[receiver_name]['balance'] = old_receiver_balance
            return False
    
    def show_state(self):
        """Вывод текущего состояния системы"""
        print("\n" + "=" * 60)
        print("СОСТОЯНИЕ СИСТЕМЫ")
        print("=" * 60)
        for name, data in self.users.items():
            print(f"{name}: balance = [{data['balance']}], public = ({data['public']})")
        print(f"Суммарный Z = {self.Z}")
        print("=" * 60 + "\n")

# =============================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# =============================================

def main():
    print("\n" + "█" * 60)
    print("ПРОТОКОЛ MB09 - ДЕМОНСТРАЦИЯ")
    print("█" * 60 + "\n")
    
    # Инициализация системы (16-битные числа для наглядности)
    protocol = MB09Protocol(bits = 16)
    
    # Регистрация пользователей с начальным балансом
    alice_public = protocol.register_user("Alice", initial_balance = 1000)
    bob_public = protocol.register_user("Bob", initial_balance = 500)
    admin_public = protocol.register_user("Admin", initial_balance = 0)
    
    protocol.show_state()
    
    # ---- Транзакция 1: Alice -> Bob (300) ----
    success = protocol.transfer_money("Alice", "Bob", 300)
    if success:
        print("\n✓ Транзакция успешно завершена!")
    else:
        print("\n✗ Транзакция отклонена!")
    
    protocol.show_state()
    
    # ---- Транзакция 2: Bob -> Alice (100) ----
    success = protocol.transfer_money("Bob", "Alice", 100)
    if success:
        print("\n✓ Транзакция успешно завершена!")
    else:
        print("\n✗ Транзакция отклонена!")
    
    protocol.show_state()
    
    # ---- Транзакция 3: Alice -> Bob (2000) - не хватает средств ----
    success = protocol.transfer_money("Alice", "Bob", 2000)
    if success:
        print("\n✓ Транзакция успешно завершена!")
    else:
        print("\n✗ Транзакция отклонена (недостаточно средств)!")
    
    protocol.show_state()
    
    # ---- Демонстрация гомоморфного свойства ----
    print("\n" + "█" * 60)
    print("ПРОВЕРКА ГОМОМОРФНОГО БАЛАНСА")
    print("█" * 60)
    print("Сумма всех публичных ключей = Z:")
    sum_public = sum(data['public'] for data in protocol.users.values()) % protocol.p
    print(f"Σ(public) = {sum_public}")
    print(f"Z = {protocol.Z}")
    print(f"Равенство: {sum_public == protocol.Z}")
    
    print("\n" + "█" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("█" * 60)

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    main()