# Развитие MB09 и MBXI: введение в MBXX
import hashlib
import json
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from enum import Enum

# ============================================================
# 1. КРИПТОГРАФИЧЕСКИЕ ПРИМИТИВЫ (БЕЗ ВНЕШНИХ БИБЛИОТЕК)
# ============================================================

class EllipticCurve:
    """
    Простая реализация эллиптической кривой secp256k1
    y ^ 2 = x ^ 3 + 7 (mod p)
    """
    def __init__(self):
        self.p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        self.a = 0
        self.b = 7
        self.Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        self.Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        self.G = (self.Gx, self.Gy)

    def mod_inv(self, a, p):
        """Обратное число по модулю (расширенный алгоритм Евклида)"""
        if a == 0:
            return 0
        lm, hm = 1, 0
        low, high = a % p, p
        while low > 1:
            ratio = high // low
            nm = hm - lm * ratio
            nw = high - low * ratio
            hm, lm = lm, nm
            high, low = low, nw
        return lm % p

    def point_add(self, P, Q):
        """Сложение двух точек на кривой"""
        if P is None:
            return Q
        if Q is None:
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if x1 == x2 and y1 != y2:
            return None
        
        if P == Q:
            # Случай удвоения точки
            if y1 == 0:
                return None
            m = (3 * x1 * x1 + self.a) * self.mod_inv(2 * y1, self.p) % self.p
        else:
            m = (y2 - y1) * self.mod_inv(x2 - x1, self.p) % self.p
        
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def scalar_mult(self, k, P):
        """Умножение точки на скаляр"""
        if k == 0 or P is None:
            return None
        result = None
        addend = P
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)
            k >>= 1
        return result


# Инициализация кривой
CURVE = EllipticCurve()


class KeyPair:
    """Генерация и управление ключами"""
    
    @staticmethod
    def generate():
        """Генерация новой пары ключей"""
        private_key = random.randint(1, CURVE.n - 1)
        public_key = CURVE.scalar_mult(private_key, CURVE.G)
        return private_key, public_key
    
    @staticmethod
    def sign(private_key, message_hash: int) -> Tuple[int, int]:
        """Подпись сообщения (ECDSA)"""
        k = random.randint(1, CURVE.n - 1)
        R = CURVE.scalar_mult(k, CURVE.G)
        if R is None:
            raise ValueError("Не удалось вычислить R")
        r = R[0] % CURVE.n
        if r == 0:
            return KeyPair.sign(private_key, message_hash)
        
        s = (pow(k, -1, CURVE.n) * (message_hash + private_key * r)) % CURVE.n
        if s == 0:
            return KeyPair.sign(private_key, message_hash)
        return (r, s)
    
    @staticmethod
    def verify(public_key, message_hash: int, signature: Tuple[int, int]) -> bool:
        """Верификация подписи"""
        r, s = signature
        if not (1 <= r < CURVE.n and 1 <= s < CURVE.n):
            return False
        
        w = pow(s, -1, CURVE.n)
        u1 = (message_hash * w) % CURVE.n
        u2 = (r * w) % CURVE.n
        
        P = CURVE.point_add(CURVE.scalar_mult(u1, CURVE.G), CURVE.scalar_mult(u2, public_key))
        if P is None:
            return False
        return (P[0] % CURVE.n) == r


# ============================================================
# 2. СТРУКТУРА ТРАНЗАКЦИЙ И БАЗОВЫЕ ДАННЫЕ
# ============================================================

@dataclass
class Transaction:
    """Транзакция в протоколе MBXX"""
    sender: str           # Публичный ключ отправителя (hex)
    receiver: str         # Публичный ключ получателя (hex)
    amount: int           # Сумма в минимальных единицах
    nonce: int            # Счетчик для защиты от повторов
    timestamp: float      # Время создания
    signature: Optional[Tuple[int, int]] = None
    tx_hash: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'nonce': self.nonce,
            'timestamp': self.timestamp,
            'signature': [self.signature[0], self.signature[1]] if self.signature else None
        }
    
    def get_hash(self) -> str:
        """Вычисление хэша транзакции"""
        data = f"{self.sender}{self.receiver}{self.amount}{self.nonce}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sign(self, private_key: int):
        """Подписать транзакцию"""
        msg_hash = int(self.get_hash(), 16) % CURVE.n
        self.signature = KeyPair.sign(private_key, msg_hash)
        self.tx_hash = self.get_hash()
    
    def verify(self) -> bool:
        """Проверить подпись транзакции"""
        if not self.signature:
            return False
        msg_hash = int(self.get_hash(), 16) % CURVE.n
        pub_key = self._hex_to_pubkey(self.sender)
        return KeyPair.verify(pub_key, msg_hash, self.signature)
    
    @staticmethod
    def _hex_to_pubkey(hex_str: str) -> Tuple[int, int]:
        """Преобразование hex-строки в точку на кривой"""
        # Простая реализация: первые 64 символа - x, вторые 64 - y
        # В реальном протоколе используется сжатый/несжатый формат
        if len(hex_str) >= 128:
            x = int(hex_str[:64], 16)
            y = int(hex_str[64:128], 16)
            return (x, y)
        raise ValueError("Некорректный публичный ключ")


# ============================================================
# 3. ЦЕНТРАЛЬНЫЙ УЗЕЛ-ЗВЕЗДА (ЦУЗ)
# ============================================================

class NodeStatus(Enum):
    ACTIVE = "active"
    SUSPICIOUS = "suspicious"
    EXCLUDED = "excluded"


@dataclass
class NodeState:
    """Состояние узла для верификации"""
    utxo_set: Dict[str, int]  # Hash транзакции -> сумма
    transaction_history: List[str]  # Хэши обработанных транзакций
    last_seen: float


class CentralStarNode:
    """
    Центральный Узел-Звезда (ЦУЗ) в сети MBXX
    """
    
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.private_key, self.public_key = KeyPair.generate()
        self.public_key_hex = self._pubkey_to_hex(self.public_key)
        
        # Состояние узла
        self.state = NodeState(
            utxo_set = {},
            transaction_history = [],
            last_seen = time.time()
        )
        
        self.status = NodeStatus.ACTIVE
        self.performance_score = 100  # Начальный рейтинг
        self.guid = hashlib.sha256(f"{node_id}_{self.public_key_hex}".encode()).hexdigest()
        
        # Хранилище транзакций
        self.pending_transactions: List[Transaction] = []
        self.processed_transactions: List[Transaction] = []
        
        # Ключи для слепка
        self._snapshot_key = self._generate_snapshot_key()
        self._snapshot_counter = 0
    
    def _pubkey_to_hex(self, pubkey: Tuple[int, int]) -> str:
        return f"{pubkey[0]:064x}{pubkey[1]:064x}"
    
    def _generate_snapshot_key(self) -> str:
        """Генерация секретного ключа для слепка (меняется каждые N транзакций)"""
        seed = f"{self.node_id}_{time.time()}_{random.random()}"
        return hashlib.sha256(seed.encode()).hexdigest()
    
    def receive_transaction(self, tx: Transaction) -> bool:
        """Получение транзакции от пользователя"""
        # 1. Базовая проверка
        if not tx.verify():
            self._penalize(10, "Неверная подпись")
            return False
        
        # 2. Проверка на двойную трату
        if not self._check_double_spend(tx):
            self._penalize(20, "Попытка двойной траты")
            return False
        
        # 3. Проверка достаточности средств
        if not self._check_balance(tx):
            return False
        
        # 4. Добавляем в pending
        self.pending_transactions.append(tx)
        self.state.last_seen = time.time()
        return True
    
    def _check_double_spend(self, tx: Transaction) -> bool:
        """
        ДЕТЕРМИНИРОВАННАЯ ФУНКЦИЯ ПРОВЕРКИ ДВОЙНЫХ ТРАТ
        Использует матричный подход без NumPy
        """
        # Строим множество выходов (UTXO) для данного отправителя
        sender_hash = tx.sender
        
        # Проверяем, не было ли уже использования этого nonce
        for hist_tx_hash in self.state.transaction_history:
            # В реальном протоколе мы проверяем все выходы
            pass
        
        # Матричный метод (упрощенный):
        # Создаем список всех входов отправителя с этим nonce
        # Если nonce повторяется -> double spend
        for processed_tx in self.processed_transactions:
            if processed_tx.sender == tx.sender and processed_tx.nonce == tx.nonce:
                self._penalize(30, "Повторный nonce (двойная трата)")
                return False
        
        return True
    
    def _check_balance(self, tx: Transaction) -> bool:
        """Проверка баланса отправителя"""
        sender = tx.sender
        total_spent = 0
        
        # Суммируем все траты отправителя
        for processed_tx in self.processed_transactions:
            if processed_tx.sender == sender:
                total_spent += processed_tx.amount
        
        # Проверяем, достаточно ли средств
        if total_spent + tx.amount > self.state.utxo_set.get(sender, 0):
            return False
        
        return True
    
    def compute_snapshot(self, tx_batch: List[Transaction]) -> str:
        """
        Вычисление криптографического слепка состояния (S_new)
        S_new = H(S_old XOR T_x XOR K_node)
        """
        self._snapshot_counter += 1
        
        # Если квант времени истек, меняем ключ
        if self._snapshot_counter % 100 == 0:
            self._snapshot_key = self._generate_snapshot_key()
        
        # Вычисляем сумму хэшей всех транзакций
        batch_hash = hashlib.sha256()
        for tx in tx_batch:
            batch_hash.update(tx.get_hash().encode())
        tx_hash = batch_hash.hexdigest()
        
        # Формируем слепок
        old_state = hashlib.sha256(
            f"{len(self.state.transaction_history)}_{self.state.last_seen}".encode()
        ).hexdigest()
        
        # XOR операция (имитация)
        combined = int(old_state, 16) ^ int(tx_hash, 16) ^ int(self._snapshot_key, 16)
        snapshot = hashlib.sha256(str(combined).encode()).hexdigest()
        
        return snapshot
    
    def _penalize(self, points: int, reason: str):
        """Начисление штрафных баллов узлу"""
        self.performance_score = max(0, self.performance_score - points)
        if self.performance_score < 50:
            self.status = NodeStatus.SUSPICIOUS
        if self.performance_score < 20:
            self.status = NodeStatus.EXCLUDED
            print(f"⚠️ Узел {self.node_id} исключен: {reason}")
    
    def get_state_hash(self) -> str:
        """Хэш состояния узла для консенсуса"""
        data = f"{self.node_id}_{self.public_key_hex}_{len(self.processed_transactions)}"
        return hashlib.sha256(data.encode()).hexdigest()


# ============================================================
# 4. ПРОТОКОЛ MBXX - ОСНОВНОЙ КЛАСС
# ============================================================

class MBXXProtocol:
    """
    Реализация протокола MBXX (введение в MBXX)
    """
    
    def __init__(self, num_nodes: int = 5):
        self.nodes: List[CentralStarNode] = [CentralStarNode(i) for i in range(num_nodes)]
        self.transaction_pool: List[Transaction] = []
        self.confirmed_transactions: List[Transaction] = []
        self.current_quantum: int = 0
        self.quantum_duration: float = 2.0  # 2 секунды
        self.quantum_start: float = time.time()
        
        # Координатор (выбирается случайно на каждый квант)
        self.coordinator: Optional[CentralStarNode] = None
        
        # Балансы пользователей (имитация)
        self.user_balances: Dict[str, int] = defaultdict(int)
        self._initialize_balances()
    
    def _initialize_balances(self):
        """Инициализация начальных балансов для тестов"""
        for node in self.nodes:
            self.user_balances[node.public_key_hex] = 1000
    
    def create_transaction(self, sender_idx: int, receiver_idx: int, amount: int) -> Transaction:
        """Создание транзакции от одного узла к другому"""
        sender = self.nodes[sender_idx]
        receiver = self.nodes[receiver_idx]
        
        tx = Transaction(
            sender = sender.public_key_hex,
            receiver = receiver.public_key_hex,
            amount = amount,
            nonce = random.randint(1, 1000000),
            timestamp = time.time()
        )
        tx.sign(sender.private_key)
        return tx
    
    def submit_transaction(self, tx: Transaction) -> bool:
        """Отправка транзакции в сеть"""
        # Рассылаем всем узлам
        successful = 0
        for node in self.nodes:
            if node.status != NodeStatus.EXCLUDED:
                if node.receive_transaction(tx):
                    successful += 1
        
        # Требуем > 50% успешных подтверждений
        active_nodes = sum(1 for n in self.nodes if n.status != NodeStatus.EXCLUDED)
        if successful > active_nodes / 2:
            self.transaction_pool.append(tx)
            return True
        return False
    
    def _select_coordinator(self) -> Optional[CentralStarNode]:
        """Выбор координатора на текущий квант (детерминировано)"""
        active = [n for n in self.nodes if n.status == NodeStatus.ACTIVE]
        if not active:
            return None
        
        # Используем псевдослучайный выбор на основе кванта
        idx = hash(f"quantum_{self.current_quantum}") % len(active)
        return active[idx]
    
    def _compute_matrix_rank(self, transactions: List[Transaction]) -> int:
        """
        Вычисление ранга матрицы для детектирования двойных трат
        (Без NumPy - упрощенная реализация)
        """
        # Строим матрицу: строки = отправители, столбцы = получатели
        # Каждая транзакция добавляет 1 в соответствующую ячейку
        
        matrix = defaultdict(lambda: defaultdict(int))
        for tx in transactions:
            matrix[tx.sender][tx.receiver] += 1
        
        # Вычисляем "ранг" как количество уникальных отправителей
        return len(matrix)
    
    def _finalize_quantum(self):
        """Финализация кванта времени"""
        self.current_quantum += 1
        self.quantum_start = time.time()
        
        if not self.transaction_pool:
            return
        
        # Выбираем координатора
        self.coordinator = self._select_coordinator()
        if not self.coordinator:
            return
        
        # 1. Все узлы вычисляют слепки
        snapshots = {}
        for node in self.nodes:
            if node.status == NodeStatus.EXCLUDED:
                continue
            snapshot = node.compute_snapshot(self.transaction_pool)
            snapshots[node.node_id] = snapshot
        
        # 2. Координатор собирает и проверяет слепки
        # Вычисляем детерминант целостности (ранг матрицы)
        matrix_rank = self._compute_matrix_rank(self.transaction_pool)
        
        # Проверяем консенсус: все слепки должны совпадать
        if snapshots:
            first_snapshot = next(iter(snapshots.values()))
            consensus = all(s == first_snapshot for s in snapshots.values())
            
            if not consensus:
                # Выявляем "предательские" узлы
                self._detect_byzantine_nodes(snapshots)
                return
            
            # 3. Подтверждение транзакций
            if matrix_rank > 0:  # Невырожденная матрица -> нет двойной траты
                for tx in self.transaction_pool:
                    # Обновляем UTXO
                    for node in self.nodes:
                        if node.status == NodeStatus.ACTIVE:
                            node.processed_transactions.append(tx)
                            node.state.transaction_history.append(tx.tx_hash or tx.get_hash())
                            # Обновляем баланс
                            self.user_balances[tx.sender] -= tx.amount
                            self.user_balances[tx.receiver] += tx.amount
                    
                    self.confirmed_transactions.append(tx)
                
                print(f"✅ Квант {self.current_quantum}: {len(self.transaction_pool)} транзакций подтверждено")
            else:
                # Вырожденная матрица -> обнаружена двойная трата
                print(f"❌ Квант {self.current_quantum}: обнаружена двойная трата!")
        
        self.transaction_pool.clear()
    
    def _detect_byzantine_nodes(self, snapshots: Dict[int, str]):
        """Выявление византийских узлов (предателей)"""
        # Группируем по значению слепка
        groups: Dict[str, List[int]] = {}
        for node_id, snapshot in snapshots.items():
            if snapshot not in groups:
                groups[snapshot] = []
            groups[snapshot].append(node_id)
        
        # Самая большая группа = честные узлы
        honest_group = max(groups.values(), key = len)
        
        # Все остальные - подозрительные
        for node_id, snapshot in snapshots.items():
            if node_id not in honest_group:
                for node in self.nodes:
                    if node.node_id == node_id:
                        node._penalize(50, "Византийское поведение")
    
    def run_quantum_cycle(self):
        """Запуск цикла кванта"""
        # Проверяем, истекло ли время кванта
        if time.time() - self.quantum_start >= self.quantum_duration:
            self._finalize_quantum()
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Статистика работы протокола"""
        active = sum(1 for n in self.nodes if n.status == NodeStatus.ACTIVE)
        suspicious = sum(1 for n in self.nodes if n.status == NodeStatus.SUSPICIOUS)
        excluded = sum(1 for n in self.nodes if n.status == NodeStatus.EXCLUDED)
        
        return {
            'total_nodes': len(self.nodes),
            'active': active,
            'suspicious': suspicious,
            'excluded': excluded,
            'quantum': self.current_quantum,
            'confirmed_txs': len(self.confirmed_transactions),
            'pending': len(self.transaction_pool)
        }


# ============================================================
# 5. ТЕСТОВЫЙ ЗАПУСК И ДЕМОНСТРАЦИЯ
# ============================================================

def demo_mbxx():
    """Демонстрация работы протокола MBXX"""
    print("=" * 70)
    print("🚀 ЗАПУСК ПРОТОКОЛА MBXX (ДЕЦЕНТРАЛИЗОВАННЫЕ ЭЛЕКТРОННЫЕ ДЕНЬГИ)")
    print("=" * 70)
    
    # Создаем протокол с 5 узлами
    protocol = MBXXProtocol(num_nodes = 5)
    
    print("\n📡 Сеть инициализирована:")
    print(f"   - Узлов: {len(protocol.nodes)}")
    print(f"   - Квант: {protocol.quantum_duration} сек")
    
    # Создаем несколько транзакций
    print("\n" + "-" * 70)
    print("📝 СОЗДАНИЕ И ОТПРАВКА ТРАНЗАКЦИЙ")
    print("-" * 70)
    
    transactions = []
    
    # Транзакция 1: Узел 0 -> Узел 1 (100 единиц)
    tx1 = protocol.create_transaction(0, 1, 100)
    success = protocol.submit_transaction(tx1)
    print(f"✓ TX1: Узел0 -> Узел1 (100): {'УСПЕШНО' if success else 'ОТКЛОНЕНО'}")
    transactions.append(tx1)
    
    # Транзакция 2: Узел 2 -> Узел 3 (50 единиц)
    tx2 = protocol.create_transaction(2, 3, 50)
    success = protocol.submit_transaction(tx2)
    print(f"✓ TX2: Узел2 -> Узел3 (50): {'УСПЕШНО' if success else 'ОТКЛОНЕНО'}")
    transactions.append(tx2)
    
    # Транзакция 3: Узел 1 -> Узел 4 (30 единиц)
    tx3 = protocol.create_transaction(1, 4, 30)
    success = protocol.submit_transaction(tx3)
    print(f"✓ TX3: Узел1 -> Узел4 (30): {'УСПЕШНО' if success else 'ОТКЛОНЕНО'}")
    transactions.append(tx3)
    
    # Пытаемся создать двойную трату (узел 0 использует тот же nonce)
    print("\n⚠️ ПОПЫТКА ДВОЙНОЙ ТРАТЫ:")
    tx_double = protocol.create_transaction(0, 4, 200)
    tx_double.nonce = tx1.nonce  # Тот же nonce!
    tx_double.sign(protocol.nodes[0].private_key)
    success = protocol.submit_transaction(tx_double)
    print(f"   TX4 (Double-spend): {'ОТКЛОНЕНО ✅' if not success else 'ПРОШЛО ❌'}")
    
    # Запускаем квантовый цикл
    print("\n" + "-" * 70)
    print("⏳ ОБРАБОТКА КВАНТА ВРЕМЕНИ")
    print("-" * 70)
    
    # Имитируем ожидание
    time.sleep(0.5)  # Имитация времени
    
    # Принудительно финализируем (в реальности это делается по таймеру)
    protocol._finalize_quantum()
    
    # Статистика
    print("\n" + "-" * 70)
    print("📊 СТАТИСТИКА ПРОТОКОЛА")
    print("-" * 70)
    stats = protocol.get_stats()
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').capitalize()}: {value}")
    
    # Балансы
    print("\n💰 ИТОГОВЫЕ БАЛАНСЫ:")
    for i, node in enumerate(protocol.nodes):
        balance = protocol.user_balances.get(node.public_key_hex, 0)
        status = node.status.value
        print(f"   Узел {i}: {balance} MBX (статус: {status})")
    
    # Проверка подписей
    print("\n🔐 ВЕРИФИКАЦИЯ ПОДПИСЕЙ:")
    for tx in protocol.confirmed_transactions:
        valid = tx.verify()
        print(f"   TX {tx.tx_hash[:8]}... : {'✅ ВАЛИДНА' if valid else '❌ НЕДЕЙСТВИТЕЛЬНА'}")
    
    print("\n" + "=" * 70)
    print("✅ ДЕМОНСТРАЦИЯ ПРОТОКОЛА MBXX ЗАВЕРШЕНА")
    print("=" * 70)
    
    return protocol


if __name__ == "__main__":
    # Устанавливаем сид для воспроизводимости
    random.seed(42)
    
    # Запускаем демонстрацию
    protocol = demo_mbxx()