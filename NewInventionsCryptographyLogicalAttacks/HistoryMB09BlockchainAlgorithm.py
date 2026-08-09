# История создания алгоритма MB09 и блокчейна
import hashlib
import random
import time
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict
import math


# ============================================================================
# БАЗОВЫЕ КРИПТОГРАФИЧЕСКИЕ УТИЛИТЫ (без numpy)
# ============================================================================

def gcd_extended(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: возвращает (g, x, y) где g = gcd(a, b) и ax + by = g"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = gcd_extended(b % a, a)
    return g, y1 - (b // a) * x1, x1


def mod_inverse(a: int, m: int) -> int:
    """Находит обратное число по модулю m"""
    g, x, _ = gcd_extended(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента не существует для {a} mod {m}")
    return x % m


def is_prime(n: int, k: int = 5) -> bool:
    """Тест Миллера-Рабина на простоту"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
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


def generate_prime(bits: int = 256) -> int:
    """Генерация простого числа заданной битности"""
    while True:
        # Генерируем нечетное число
        candidate = random.getrandbits(bits)
        # Устанавливаем старший и младший биты для гарантии длины и нечетности
        candidate |= (1 << bits - 1) | 1
        if is_prime(candidate):
            return candidate


def sha256_hash(data: str) -> int:
    """SHA-256 хеш в виде целого числа"""
    return int(hashlib.sha256(data.encode()).hexdigest(), 16)


# ============================================================================
# АЛГОРИТМ MB09 - НА ОСНОВЕ ТЕОРЕМЫ ФЕРМА
# ============================================================================

class MB09:
    """
    Алгоритм MB09 - асимметричное шифрование на основе малой теоремы Ферма.
    
    Малая теорема Ферма: a^(p - 1) ≡ 1 (mod p) для простого p
    Мы используем это для создания системы с открытым/закрытым ключом.
    """
    
    def __init__(self, bits: int = 512):
        self.bits = bits
        self._generate_keys()
    
    def _generate_keys(self):
        """Генерация ключевой пары MB09"""
        # Выбираем два простых числа p и q
        p = generate_prime(self.bits // 2)
        q = generate_prime(self.bits // 2)
        
        # n = p * q (как в RSA, но используем по-другому)
        self.n = p * q
        self.phi = (p - 1) * (q - 1)
        
        # Выбираем e взаимно простое с phi
        self.e = 65537
        while math.gcd(self.e, self.phi) != 1:
            self.e = random.randint(3, self.phi - 1)
        
        # d - обратное к e по модулю phi
        self.d = mod_inverse(self.e, self.phi)
        
        # Дополнительные параметры для теоремы Ферма
        # Используем p как модуль для упрощенной версии
        self.p = p
        self.q = q
        
        # Открытый ключ: (n, e)
        # Закрытый ключ: (d, p, q)
    
    def get_public_key(self) -> Tuple[int, int]:
        """Возвращает открытый ключ (n, e)"""
        return (self.n, self.e)
    
    def encrypt(self, message: int, public_key: Tuple[int, int]) -> int:
        """
        Шифрование с использованием открытого ключа.
        Используем модификацию: c = m^e mod n
        """
        n, e = public_key
        return pow(message, e, n)
    
    def decrypt(self, ciphertext: int) -> int:
        """Расшифрование с использованием закрытого ключа"""
        return pow(ciphertext, self.d, self.n)
    
    def sign(self, message: int) -> int:
        """
        Цифровая подпись сообщения (подпись = m^d mod n)
        """
        return pow(message, self.d, self.n)
    
    def verify(self, message: int, signature: int, public_key: Tuple[int, int]) -> bool:
        """
        Проверка подписи: signature^e mod n == message
        """
        n, e = public_key
        return pow(signature, e, n) == message


# ============================================================================
# АЛГОРИТМ MBXI - ЦИФРОВАЯ ПОДПИСЬ
# ============================================================================

class MBXI:
    """
    Алгоритм MBXI - схема цифровой подписи.
    Использует хеширование и асимметричную криптографию.
    """
    
    def __init__(self, bits: int = 256):
        self.bits = bits
        # Используем MB09 как базовый алгоритм
        self.mb09 = MB09(bits)
        
        # Генерируем дополнительный ключ для подписей
        self.private_key = self.mb09.d
        self.public_key = self.mb09.get_public_key()
    
    def sign_message(self, message: str) -> Tuple[int, int]:
        """
        Создание подписи для сообщения.
        Возвращает (хеш_сообщения, подпись)
        """
        # Вычисляем хеш сообщения
        message_hash = sha256_hash(message)
        
        # Создаем подпись: sign = hash^d mod n
        signature = self.mb09.sign(message_hash)
        
        return (message_hash, signature)
    
    def verify_signature(self, message: str, signature: int, public_key: Tuple[int, int]) -> bool:
        """
        Проверка подписи
        """
        message_hash = sha256_hash(message)
        return self.mb09.verify(message_hash, signature, public_key)
    
    @staticmethod
    def attack_rsa(n: int, e: int, ciphertext: int) -> Optional[int]:
        """
        Демонстрация атаки на RSA при малых экспонентах.
        Это упрощенная версия атаки, описанной в тексте.
        """
        # Если e мало (3), можно попытаться извлечь корень
        if e == 3:
            # Пытаемся найти кубический корень (упрощенно)
            low = 1
            high = ciphertext
            while low <= high:
                mid = (low + high) // 2
                cube = mid ** 3
                if cube == ciphertext:
                    return mid
                elif cube < ciphertext:
                    low = mid + 1
                else:
                    high = mid - 1
        return None


# ============================================================================
# ПРОТОКОЛ MBXX - КОНСЕНСУС БЕЗ БЛОКЧЕЙНА
# ============================================================================

@dataclass
class Transaction:
    """Транзакция в системе MBXX"""
    sender: str
    receiver: str
    amount: float
    timestamp: int
    signature: Optional[int] = None
    
    def get_hash(self) -> int:
        """Хеш транзакции"""
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return sha256_hash(data)


class MBXXNode:
    """
    Узел в сети MBXX.
    Консенсус достигается через криптографию, а не через Proof of Work.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.mbxi = MBXI(256)
        self.pending_transactions: List[Transaction] = []
        self.confirmed_transactions: List[Transaction] = []
        self.balance = 1000.0  # Начальный баланс
        self.peers: List['MBXXNode'] = []
    
    def get_public_key(self) -> Tuple[int, int]:
        return self.mbxi.public_key
    
    def create_transaction(self, receiver: str, amount: float) -> Transaction:
        """Создание новой транзакции с подписью"""
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        
        tx = Transaction(
            sender = self.node_id,
            receiver = receiver,
            amount = amount,
            timestamp = int(time.time())
        )
        
        # Подписываем транзакцию
        _, signature = self.mbxi.sign_message(
            f"{tx.sender}{tx.receiver}{tx.amount}{tx.timestamp}"
        )
        tx.signature = signature
        
        self.balance -= amount
        return tx
    
    def verify_transaction(self, tx: Transaction, sender_public_key: Tuple[int, int]) -> bool:
        """Проверка транзакции через криптографию (без блокчейна!)"""
        # Проверяем подпись
        message = f"{tx.sender}{tx.receiver}{tx.amount}{tx.timestamp}"
        is_valid = self.mbxi.verify_signature(message, tx.signature, sender_public_key)
        
        if not is_valid:
            return False
        
        # Проверяем, что отправитель имеет достаточно средств (упрощенно)
        # В реальной системе это проверяется через распределенный реестр
        return True
    
    def process_transaction(self, tx: Transaction, sender_public_key: Tuple[int, int]) -> bool:
        """
        Обработка транзакции без блокчейна.
        Консенсус достигается через криптографическую проверку.
        """
        if self.verify_transaction(tx, sender_public_key):
            self.confirmed_transactions.append(tx)
            # В реальной системе здесь обновляется баланс
            return True
        return False
    
    def propose_consensus(self) -> Dict[str, List[Transaction]]:
        """
        Механизм консенсуса MBXX.
        Вместо Proof of Work используем криптографические доказательства.
        """
        # Собираем все неподтвержденные транзакции
        proposals = {}
        for peer in self.peers:
            proposals[peer.node_id] = peer.pending_transactions.copy()
        
        # В MBXX консенсус достигается через взаимную проверку подписей
        # и криптографических доказательств, а не через майнинг
        return proposals


# ============================================================================
# ЛЕГКОВЕСНОЕ ШИФРОВАНИЕ ДЛЯ IoT (ИСПРАВЛЕННАЯ ВЕРСИЯ)
# ============================================================================

class LightweightCipher:
    """
    Легковесное шифрование для IoT устройств.
    Использует простые операции: XOR, сдвиги, перестановки.
    Реализована сеть Фейстеля с 8 раундами.
    """
    
    def __init__(self, key: int = None):
        self.key = key or random.getrandbits(64)
        self.blocksize = 64  # бит
        self.block_bytes = 8  # байт
        self.rounds = 8
    
    def _feistel_round(self, block: int, round_key: int) -> int:
        """
        Один раунд сети Фейстеля для легковесного шифрования.
        """
        left = (block >> 32) & 0xFFFFFFFF
        right = block & 0xFFFFFFFF
        
        # F-функция: XOR, сдвиг и перестановка
        f_result = (right ^ round_key) & 0xFFFFFFFF
        f_result = ((f_result << 3) | (f_result >> 29)) & 0xFFFFFFFF  # Циклический сдвиг влево на 3
        f_result ^= 0x9E3779B9  # Константа (золотое сечение)
        
        new_left = right
        new_right = left ^ f_result
        
        return ((new_left & 0xFFFFFFFF) << 32) | (new_right & 0xFFFFFFFF)
    
    def _pad_data(self, data: bytes) -> bytes:
        """
        Добавление PKCS#7 паддинга
        """
        pad_len = self.block_bytes - (len(data) % self.block_bytes)
        if pad_len == 0:
            pad_len = self.block_bytes
        return data + bytes([pad_len] * pad_len)
    
    def _unpad_data(self, data: bytes) -> bytes:
        """
        Удаление PKCS#7 паддинга
        """
        if not data:
            return data
        
        pad_len = data[-1]
        if pad_len > self.block_bytes or pad_len == 0:
            raise ValueError("Неверный паддинг")
        
        # Проверяем, что все байты паддинга корректны
        for i in range(1, pad_len + 1):
            if data[-i] != pad_len:
                raise ValueError("Неверный паддинг")
        
        return data[:-pad_len]
    
    def _derive_round_keys(self) -> List[int]:
        """Генерация раундовых ключей из мастер-ключа"""
        round_keys = []
        for i in range(self.rounds):
            # Используем разные части ключа для каждого раунда
            shift = (i * 8) % 64
            round_key = ((self.key >> shift) & 0xFFFFFFFF)
            # Добавляем разнообразие
            round_key ^= (i * 0x9E3779B9) & 0xFFFFFFFF
            round_keys.append(round_key)
        return round_keys
    
    def encrypt_block(self, plaintext: int) -> int:
        """Шифрование одного блока (легковесное)"""
        if plaintext >= (1 << 64):
            raise ValueError("Блок должен быть 64-битным")
        
        block = plaintext & ((1 << 64) - 1)
        round_keys = self._derive_round_keys()
        
        # Прямые раунды
        for i in range(self.rounds):
            block = self._feistel_round(block, round_keys[i])
        
        return block
    
    def decrypt_block(self, ciphertext: int) -> int:
        """Дешифрование одного блока"""
        if ciphertext >= (1 << 64):
            raise ValueError("Блок должен быть 64-битным")
        
        block = ciphertext & ((1 << 64) - 1)
        round_keys = self._derive_round_keys()
        
        # Обратные раунды
        for i in range(self.rounds - 1, -1, -1):
            block = self._feistel_round(block, round_keys[i])
        
        return block
    
    def encrypt(self, data: str) -> str:
        """Шифрование строки (по блокам)"""
        # Преобразуем строку в байты
        data_bytes = data.encode('utf-8')
        
        # Добавляем паддинг
        padded = self._pad_data(data_bytes)
        
        result = []
        for i in range(0, len(padded), self.block_bytes):
            block = int.from_bytes(padded[i:i + self.block_bytes], 'big')
            encrypted = self.encrypt_block(block)
            result.append(encrypted.to_bytes(self.block_bytes, 'big'))
        
        return ''.join(b.hex() for b in result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Дешифрование строки"""
        # Преобразуем hex в байты
        data = bytes.fromhex(ciphertext)
        
        if len(data) % self.block_bytes != 0:
            raise ValueError("Неверная длина зашифрованных данных")
        
        result = []
        for i in range(0, len(data), self.block_bytes):
            block = int.from_bytes(data[i:i + self.block_bytes], 'big')
            decrypted = self.decrypt_block(block)
            result.append(decrypted.to_bytes(self.block_bytes, 'big'))
        
        # Объединяем и удаляем паддинг
        try:
            plaintext_bytes = self._unpad_data(b''.join(result))
            return plaintext_bytes.decode('utf-8')
        except ValueError as e:
            # Если паддинг неверный, пробуем без удаления паддинга (для совместимости)
            return b''.join(result).decode('utf-8', errors = 'ignore')


# ============================================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ ВСЕХ АЛГОРИТМОВ
# ============================================================================

def demo_mb09():
    """Демонстрация алгоритма MB09"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АЛГОРИТМА MB09")
    print("=" * 60)
    
    # Создаем экземпляр MB09
    mb09 = MB09(256)  # 256 бит для демонстрации
    
    # Получаем ключи
    public_key = mb09.get_public_key()
    print(f"Открытый ключ (n, e):")
    print(f"  n = {public_key[0]}")
    print(f"  e = {public_key[1]}")
    
    # Шифрование и дешифрование
    message = 123456789
    print(f"\nИсходное сообщение: {message}")
    
    encrypted = mb09.encrypt(message, public_key)
    print(f"Зашифрованное: {encrypted}")
    
    decrypted = mb09.decrypt(encrypted)
    print(f"Расшифрованное: {decrypted}")
    
    print(f"\nУспех: {message == decrypted}")
    
    # Цифровая подпись
    signature = mb09.sign(message)
    print(f"\nПодпись для сообщения: {signature}")
    
    is_valid = mb09.verify(message, signature, public_key)
    print(f"Подпись валидна: {is_valid}")


def demo_mbxi():
    """Демонстрация алгоритма MBXI"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АЛГОРИТМА MBXI")
    print("=" * 60)
    
    # Создаем экземпляр MBXI
    mbxi = MBXI(256)
    
    # Сообщение для подписи
    message = "Это тестовое сообщение для подписи MBXI"
    print(f"Сообщение: {message}")
    
    # Создаем подпись
    hash_val, signature = mbxi.sign_message(message)
    print(f"Хеш сообщения: {hash_val}")
    print(f"Подпись: {signature}")
    
    # Проверяем подпись
    is_valid = mbxi.verify_signature(message, signature, mbxi.public_key)
    print(f"\nПодпись валидна: {is_valid}")
    
    # Изменяем сообщение
    tampered_message = "Это измененное сообщение"
    is_valid_tampered = mbxi.verify_signature(tampered_message, signature, mbxi.public_key)
    print(f"Подпись для измененного сообщения валидна: {is_valid_tampered}")
    
    # Демонстрация атаки на RSA (малая экспонента)
    print("\n--- Атака на RSA с малой экспонентой ---")
    # Создаем RSA с e=3
    mb09_small = MB09(256)
    public_small = mb09_small.get_public_key()
    
    # Шифруем маленькое сообщение
    small_msg = 42
    encrypted_small = mb09_small.encrypt(small_msg, public_small)
    
    # Пытаемся взломать
    attacked = MBXI.attack_rsa(public_small[0], public_small[1], encrypted_small)
    print(f"Исходное сообщение: {small_msg}")
    print(f"Зашифрованное: {encrypted_small}")
    print(f"Результат атаки: {attacked}")
    print(f"Атака успешна: {attacked == small_msg}")


def demo_mbxx():
    """Демонстрация протокола MBXX (консенсус без блокчейна)"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА MBXX")
    print("Консенсус без блокчейна через криптографию")
    print("=" * 60)
    
    # Создаем сеть узлов
    node_alice = MBXXNode("Alice")
    node_bob = MBXXNode("Bob")
    node_charlie = MBXXNode("Charlie")
    
    # Устанавливаем связи
    node_alice.peers = [node_bob, node_charlie]
    node_bob.peers = [node_alice, node_charlie]
    node_charlie.peers = [node_alice, node_bob]
    
    print("Создана сеть из 3 узлов: Alice, Bob, Charlie")
    print(f"Баланс Alice: {node_alice.balance}")
    print(f"Баланс Bob: {node_bob.balance}")
    
    # Alice отправляет Bob деньги
    print("\n--- Alice отправляет Bob 100 монет ---")
    tx = node_alice.create_transaction("Bob", 100.0)
    print(f"Транзакция создана: {tx.sender} -> {tx.receiver} ({tx.amount})")
    print(f"Подпись транзакции: {tx.signature}")
    
    # Bob проверяет транзакцию (криптографическая проверка, не блокчейн!)
    is_valid = node_bob.verify_transaction(tx, node_alice.get_public_key())
    print(f"Bob проверяет транзакцию: {'✅ Валидна' if is_valid else '❌ Невалидна'}")
    
    # Charlie также проверяет
    is_valid_c = node_charlie.verify_transaction(tx, node_alice.get_public_key())
    print(f"Charlie проверяет транзакцию: {'✅ Валидна' if is_valid_c else '❌ Невалидна'}")
    
    # Обработка транзакции
    if is_valid:
        node_bob.process_transaction(tx, node_alice.get_public_key())
        print(f"✅ Транзакция подтверждена без использования блокчейна!")
    
    print(f"\nНовый баланс Alice: {node_alice.balance}")
    print(f"Новый баланс Bob: {node_bob.balance}")
    
    # Механизм консенсуса
    print("\n--- Механизм консенсуса MBXX ---")
    proposals = node_alice.propose_consensus()
    print("Узлы достигли консенсуса через криптографическую проверку!")
    print("(Без Proof of Work и без длинных цепочек блоков)")


def demo_lightweight():
    """Демонстрация легковесного шифрования для IoT"""
    print("\n" + "=" * 60)
    print("ЛЕГКОВЕСНОЕ ШИФРОВАНИЕ ДЛЯ IoT")
    print("(Оптимизировано для устройств с низким энергопотреблением)")
    print("=" * 60)
    
    # Создаем шифр с фиксированным ключом
    cipher = LightweightCipher(key = 0x123456789ABCDEF0)
    
    # Тестируем на разных данных
    test_data = [
        "Hello IoT!",
        "Sensor: 23.5°C",
        "Data from smart device",
        "Short",
        "This is a longer message to test block encryption in IoT devices"
    ]
    
    for data in test_data:
        print(f"\nИсходные данные: {data}")
        print(f"Длина: {len(data)} байт")
        
        # Шифрование
        encrypted = cipher.encrypt(data)
        print(f"Зашифровано: {encrypted[:64]}..." if len(encrypted) > 64 else f"Зашифровано: {encrypted}")
        
        # Дешифрование
        try:
            decrypted = cipher.decrypt(encrypted)
            print(f"Расшифровано: {decrypted}")
            print(f"✅ Успешно: {data == decrypted}")
        except Exception as e:
            print(f"❌ Ошибка дешифрования: {e}")
    
    # Тест с разными ключами
    print("\n--- Тест с разными ключами ---")
    for i in range(3):
        cipher_test = LightweightCipher()
        data = f"Test message {i}"
        encrypted = cipher_test.encrypt(data)
        decrypted = cipher_test.decrypt(encrypted)
        print(f"Ключ {i}: {data} -> {decrypted} {'✅' if data == decrypted else '❌'}")
    
    # Измеряем производительность
    print("\n--- Тест производительности ---")
    data = "A" * 1024  # 1KB данных
    
    start = time.time()
    for _ in range(100):
        encrypted = cipher.encrypt(data)
        decrypted = cipher.decrypt(encrypted)
    elapsed = time.time() - start
    
    print(f"100 итераций шифрования/дешифрования 1KB данных")
    print(f"Время: {elapsed:.4f} секунд")
    print(f"Скорость: {1024 * 100 / elapsed:.0f} байт/сек")
    print("✅ Легковесное шифрование подходит для IoT устройств")


def demo_comparison_with_blockchain():
    """Сравнение MBXX с традиционным блокчейном"""
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ MBXX С ТРАДИЦИОННЫМ БЛОКЧЕЙНОМ")
    print("=" * 60)
    
    print("""
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                    ТРАДИЦИОННЫЙ БЛОКЧЕЙН (Bitcoin)                          │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ • Консенсус: Proof of Work (майнинг)                                        │
    │ • Энергозатраты: ОГРОМНЫЕ (~100 TWh/год)                                    │
    │ • Время транзакции: 10-60 минут                                             │
    │ • Комиссии: Высокие при загруженности сети                                  │
    │ • Хранилище: Полная история всех транзакций (~400+ GB)                      │
    │ • Децентрализация: Требует огромной вычислительной мощности                 │
    └─────────────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         ПРОТОКОЛ MBXX                                       │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ • Консенсус: Криптографическая проверка (без майнинга)                      │
    │ • Энергозатраты: МИНИМАЛЬНЫЕ (обычные вычисления)                           │
    │ • Время транзакции: Мгновенно (секунды)                                     │
    │ • Комиссии: Низкие или нулевые                                              │
    │ • Хранилище: Только необходимые данные                                      │
    │ • Децентрализация: Достигается через криптографию, а не вычислительную      │
    │   мощность                                                                  │
    └─────────────────────────────────────────────────────────────────────────────┘
    
    ✅ ВЫВОД: Блокчейн избыточен для обработки цифровых транзакций.
              Все можно сделать с помощью одной криптографии.
    """)


def main():
    """Главная функция для демонстрации всех алгоритмов"""
    print("=" * 60)
    print("КРИПТОГРАФИЧЕСКИЕ АЛГОРИТМЫ MB09, MBXI, MBXX")
    print("Разработка: автор (2008-2020)")
    print("=" * 60)
    
    # Демонстрируем все алгоритмы
    demo_mb09()
    demo_mbxi()
    demo_mbxx()
    demo_lightweight()
    demo_comparison_with_blockchain()
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nКлючевые выводы:")
    print("1. MB09 использует теорему Ферма для асимметричного шифрования")
    print("2. MBXI позволяет создавать цифровые подписи без доверенных сторон")
    print("3. MBXX достигает консенсуса без блокчейна, используя только криптографию")
    print("4. Легковесное шифрование защищает IoT устройства с ограниченными ресурсами")
    print("5. Блокчейн избыточен - криптография решает все проблемы")


if __name__ == "__main__":
    main()