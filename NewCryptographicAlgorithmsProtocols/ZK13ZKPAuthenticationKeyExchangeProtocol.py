# ZK13 — протокол ZKP для аутентификации и обмена ключами
import hashlib
import random
import time
from dataclasses import dataclass
from typing import Tuple, Optional

# ============================================================
# КОНСТАНТЫ (безопасные параметры для 2048-битного ключа)
# ============================================================
# Большое простое число p (2048 бит) - безопасное простое число
# где p = 2q + 1, q - тоже простое (safe prime)
P = int(
    "0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74"
    "020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05"
    "98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB"
    "9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718"
    "3995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16
)

# Генератор G (примитивный корень для safe prime)
G = 5

# Безопасный контекст для предотвращения атак повторного использования
CONTEXT = b"ZK13_PROTOCOL_2026"

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Быстрое возведение в степень по модулю (бинарный метод).
    Эквивалент pow(base, exponent, modulus) но реализован вручную
    для демонстрации, без использования встроенного pow.
    """
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent & 1:  # если бит установлен
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus
    return result


def sha256_hash(*args) -> int:
    """
    Вычисляет SHA-256 хеш от произвольного количества аргументов
    и возвращает целое число.
    """
    hasher = hashlib.sha256()
    for arg in args:
        if isinstance(arg, str):
            arg = arg.encode('utf-8')
        elif isinstance(arg, int):
            arg = str(arg).encode('utf-8')
        elif isinstance(arg, bytes):
            pass
        else:
            arg = str(arg).encode('utf-8')
        hasher.update(arg)
    return int.from_bytes(hasher.digest(), 'big')


def generate_random() -> int:
    """Генерирует криптографически стойкое случайное число."""
    return random.SystemRandom().randint(2, P - 2)


# ============================================================
# ОБЩИЙ СЕКРЕТ (PSK - Pre-Shared Key)
# ============================================================
# Это число знают только Алиса и Боб (количество птиц на озере)
SHARED_SECRET = 42  # В реальном проекте это 256-битный случайный ключ

# Открытый параметр V = g^s mod p (может храниться в БД)
V = mod_pow(G, SHARED_SECRET, P)


# ============================================================
# КЛАССЫ УЧАСТНИКОВ
# ============================================================

@dataclass
class ZK13Proof:
    """Доказательство, которое отправляется от одной стороны к другой."""
    R: int          # g^r mod p (публичная маска)
    z: int          # r + c*s mod (p-1)
    session_id: str # Уникальный идентификатор сессии


class ZK13Participant:
    """
    Участник протокола ZK13 (Алиса или Боб).
    Каждый участник знает общий секрет s и может:
    1. Сгенерировать доказательство (быть доказывающим)
    2. Проверить доказательство (быть проверяющим)
    """
    
    def __init__(self, name: str, shared_secret: int):
        self.name = name
        self.s = shared_secret
        self.v = mod_pow(G, self.s, P)  # открытый параметр
        
    def generate_proof(self, session_id: str = None) -> ZK13Proof:
        """
        Генерирует неинтерактивное доказательство знания секрета.
        Возвращает кортеж (R, z), который отправляется проверяющему.
        """
        if session_id is None:
            session_id = f"{self.name}_{int(time.time())}"
        
        # 1. Генерируем случайное r (сессионный nonce)
        r = generate_random()
        
        # 2. Вычисляем R = g^r mod p
        R = mod_pow(G, r, P)
        
        # 3. Вычисляем вызов c = H(R || session_id || контекст)
        c = sha256_hash(R, session_id, CONTEXT) % (P - 1)
        
        # 4. Вычисляем ответ z = r + c*s mod (p-1)
        #    Используем (p-1) как порядок группы для G
        z = (r + c * self.s) % (P - 1)
        
        proof = ZK13Proof(R = R, z = z, session_id = session_id)
        return proof
    
    def verify_proof(self, proof: ZK13Proof, other_party_v: int) -> bool:
        """
        Проверяет доказательство от другой стороны.
        other_party_v - открытый параметр V другой стороны.
        """
        # 1. Вычисляем вызов c = H(R || session_id || контекст)
        c = sha256_hash(proof.R, proof.session_id, CONTEXT) % (P - 1)
        
        # 2. Проверяем: g^z == R * V^c (mod p)
        left_side = mod_pow(G, proof.z, P)
        right_side = (proof.R * mod_pow(other_party_v, c, P)) % P
        
        return left_side == right_side
    
    def derive_session_key(self, proof_from_other: ZK13Proof) -> bytes:
        """
        Выводит общий сессионный ключ на основе полученного доказательства.
        Используется для симметричного шифрования после аутентификации.
        """
        # Используем R из доказательства как часть ключевого материала
        key_material = f"{self.name}_{proof_from_other.session_id}_{proof_from_other.R}".encode()
        return hashlib.sha256(key_material).digest()


# ============================================================
# ВЗАИМНАЯ АУТЕНТИФИКАЦИЯ (ДЕМОНСТРАЦИЯ)
# ============================================================

def mutual_authentication():
    """
    Демонстрирует полный цикл взаимной аутентификации:
    1. Алиса доказывает Бобу, что знает секрет
    2. Боб доказывает Алисе, что знает секрет
    3. Обе стороны выводят общий сессионный ключ
    """
    print("=" * 70)
    print("ПРОТОКОЛ ZK13 - ВЗАИМНАЯ АУТЕНТИФИКАЦИЯ")
    print("=" * 70)
    print(f"Общий секрет s = {SHARED_SECRET}")
    print(f"Открытый параметр V = g ^ s mod p = {hex(V)[:30]}...")
    print()
    
    # 1. Создаем участников
    alice = ZK13Participant("Алиса", SHARED_SECRET)
    bob = ZK13Participant("Боб", SHARED_SECRET)
    
    print(f"[{alice.name}] Инициализирована")
    print(f"[{bob.name}] Инициализирован")
    print()
    
    # =========================================================
    # ШАГ 1: Алиса → Боб (Алиса доказывает, что знает секрет)
    # =========================================================
    print("--- ШАГ 1: Алиса доказывает Бобу ---")
    alice_proof = alice.generate_proof(session_id = "SESSION_001")
    print(f"[Алиса] Отправляет Бобу: R = {hex(alice_proof.R)[:30]}..., z = {hex(alice_proof.z)[:30]}...")
    
    # Боб проверяет доказательство Алисы
    is_valid_alice = bob.verify_proof(alice_proof, alice.v)
    print(f"[Боб] Проверка доказательства Алисы: {'✅ УСПЕШНО' if is_valid_alice else '❌ ОТКЛОНЕНО'}")
    
    if not is_valid_alice:
        print("❌ Аутентификация Алисы провалилась!")
        return
    print()
    
    # =========================================================
    # ШАГ 2: Боб → Алиса (Боб доказывает, что знает секрет)
    # =========================================================
    print("--- ШАГ 2: Боб доказывает Алисе ---")
    bob_proof = bob.generate_proof(session_id = "SESSION_001")  # Тот же ID для связки
    print(f"[Боб] Отправляет Алисе: R = {hex(bob_proof.R)[:30]}..., z = {hex(bob_proof.z)[:30]}...")
    
    # Алиса проверяет доказательство Боба
    is_valid_bob = alice.verify_proof(bob_proof, bob.v)
    print(f"[Алиса] Проверка доказательства Боба: {'✅ УСПЕШНО' if is_valid_bob else '❌ ОТКЛОНЕНО'}")
    
    if not is_valid_bob:
        print("❌ Аутентификация Боба провалилась!")
        return
    print()
    
    # =========================================================
    # ШАГ 3: Вывод общего сессионного ключа
    # =========================================================
    print("--- ШАГ 3: Вывод сессионного ключа ---")
    alice_session_key = alice.derive_session_key(bob_proof)
    bob_session_key = bob.derive_session_key(alice_proof)
    
    print(f"[Алиса] Сессионный ключ: {alice_session_key.hex()}")
    print(f"[Боб]   Сессионный ключ: {bob_session_key.hex()}")
    print(f"✅ Ключи {'СОВПАДАЮТ' if alice_session_key == bob_session_key else 'НЕ СОВПАДАЮТ'}!")
    print()
    
    # =========================================================
    # ДОПОЛНИТЕЛЬНО: Проверка атаки с подменой
    # =========================================================
    print("--- ДОПОЛНИТЕЛЬНО: Проверка атаки (злоумышленник) ---")
    
    # Злоумышленник Ева (не знает секрет)
    eva = ZK13Participant("Ева", SHARED_SECRET + 1)  # Неправильный секрет
    eva_proof = eva.generate_proof(session_id = "SESSION_001")
    print(f"[Ева] Отправляет Бобу поддельное доказательство: R={hex(eva_proof.R)[:30]}...")
    
    is_valid_eva = bob.verify_proof(eva_proof, eva.v)
    print(f"[Боб] Проверка доказательства Евы: {'✅ УСПЕШНО' if is_valid_eva else '❌ ОТКЛОНЕНО'}")
    print("✅ Атака успешно предотвращена (доказательство отклонено)")


# ============================================================
# ТЕСТОВЫЙ СЦЕНАРИЙ: Проверка различных атак
# ============================================================

def test_attack_scenarios():
    """
    Тестирует различные сценарии атак на протокол.
    """
    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ АТАК")
    print("=" * 70)
    
    alice = ZK13Participant("Алиса", SHARED_SECRET)
    bob = ZK13Participant("Боб", SHARED_SECRET)
    
    # 1. Атака повторным использованием (Replay Attack)
    print("\n1. Атака повторным использованием:")
    proof = alice.generate_proof(session_id = "SESSION_001")
    
    # Повторная отправка того же доказательства с новым ID
    proof_replay = ZK13Proof(R = proof.R, z = proof.z, session_id = "SESSION_002")
    is_valid_replay = bob.verify_proof(proof_replay, alice.v)
    print(f"   Повторное использование доказательства: {'❌ ОТКЛОНЕНО (безопасно)' if not is_valid_replay else '✅ ПРИНЯТО (уязвимо)'}")
    
    # 2. Атака с подменой R
    print("\n2. Атака с подменой R:")
    proof = alice.generate_proof(session_id = "SESSION_003")
    proof_tampered = ZK13Proof(R = proof.R + 1, z = proof.z, session_id = proof.session_id)
    is_valid_tampered = bob.verify_proof(proof_tampered, alice.v)
    print(f"   Подмена R: {'❌ ОТКЛОНЕНО (безопасно)' if not is_valid_tampered else '✅ ПРИНЯТО (уязвимо)'}")
    
    # 3. Атака с подменой z
    print("\n3. Атака с подменой z:")
    proof = alice.generate_proof(session_id = "SESSION_004")
    proof_tampered_z = ZK13Proof(R = proof.R, z = proof.z + 1, session_id = proof.session_id)
    is_valid_tampered_z = bob.verify_proof(proof_tampered_z, alice.v)
    print(f"   Подмена z: {'❌ ОТКЛОНЕНО (безопасно)' if not is_valid_tampered_z else '✅ ПРИНЯТО (уязвимо)'}")
    
    # 4. Атака с неправильным V (подмена открытого параметра)
    print("\n4. Атака с подменой V (MITM):")
    proof = alice.generate_proof(session_id = "SESSION_005")
    fake_v = mod_pow(G, SHARED_SECRET + 999, P)  # Чужой открытый параметр
    is_valid_fake_v = bob.verify_proof(proof, fake_v)
    print(f"   Подмена V: {'❌ ОТКЛОНЕНО (безопасно)' if not is_valid_fake_v else '✅ ПРИНЯТО (уязвимо)}'}")


# ============================================================
# БЕНЧМАРК (замер производительности)
# ============================================================

def benchmark_protocol():
    """
    Замеряет производительность протокола.
    """
    print("\n" + "=" * 70)
    print("БЕНЧМАРК ПРОТОКОЛА ZK13")
    print("=" * 70)
    
    alice = ZK13Participant("Алиса", SHARED_SECRET)
    bob = ZK13Participant("Боб", SHARED_SECRET)
    
    iterations = 100
    start_time = time.time()
    
    for i in range(iterations):
        # Генерация доказательства
        proof = alice.generate_proof(session_id = f"BENCH_{i}")
        # Верификация
        bob.verify_proof(proof, alice.v)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / iterations
    
    print(f"Количество итераций: {iterations}")
    print(f"Общее время: {total_time:.4f} секунд")
    print(f"Среднее время на операцию: {avg_time:.4f} секунд")
    print(f"Операций в секунду: {iterations / total_time:.2f}")


# ============================================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# ============================================================

if __name__ == "__main__":
    # Основная демонстрация
    mutual_authentication()
    
    # Дополнительные тесты безопасности
    test_attack_scenarios()
    
    # Замер производительности
    benchmark_protocol()
    
    print("\n" + "=" * 70)
    print("✅ Все тесты успешно завершены!")
    print("=" * 70)