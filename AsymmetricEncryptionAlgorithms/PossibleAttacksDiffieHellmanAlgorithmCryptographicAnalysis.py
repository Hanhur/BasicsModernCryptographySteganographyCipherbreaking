# Возможные атаки на алгоритм Диффи — Хеллмана и криптоанализ
import random
import hashlib
from typing import Tuple, Optional

class DiffieHellman:
    """Реализация алгоритма Диффи-Хеллмана"""
    
    def __init__(self, p: int, g: int):
        """
        Инициализация параметров DH
        
        Args:
            p: Простое число (модуль)
            g: Примитивный корень по модулю p (генератор)
        """
        self.p = p
        self.g = g
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
    
    def generate_private_key(self) -> int:
        """Генерация закрытого ключа (случайное число от 2 до p - 2)"""
        self.private_key = random.randint(2, self.p - 2)
        return self.private_key
    
    def generate_public_key(self) -> int:
        """Генерация открытого ключа: A = g ^ a mod p"""
        if self.private_key is None:
            self.generate_private_key()
        self.public_key = pow(self.g, self.private_key, self.p)
        return self.public_key
    
    def compute_shared_secret(self, other_public_key: int) -> int:
        """
        Вычисление общего секрета: K = B ^ a mod p
        
        Args:
            other_public_key: Открытый ключ собеседника
        """
        if self.private_key is None:
            raise ValueError("Закрытый ключ не сгенерирован")
        self.shared_secret = pow(other_public_key, self.private_key, self.p)
        return self.shared_secret
    
    def derive_key(self, secret: Optional[int] = None) -> bytes:
        """
        Получение ключа шифрования из общего секрета
        
        Args:
            secret: Общий секрет (если не указан, используется self.shared_secret)
        """
        if secret is None:
            secret = self.shared_secret
        if secret is None:
            raise ValueError("Общий секрет не вычислен")
        # Используем SHA-256 для получения 32-байтового ключа
        return hashlib.sha256(str(secret).encode()).digest()


class DHMessage:
    """Класс для шифрования/дешифрования сообщений с использованием общего ключа"""
    
    @staticmethod
    def encrypt(message: str, key: bytes) -> str:
        """
        XOR-шифрование (для демонстрации)
        В реальности используется AES, но для наглядности используем XOR
        """
        key_bytes = key * (len(message) // len(key) + 1)
        encrypted = []
        for i, char in enumerate(message):
            encrypted_char = ord(char) ^ key_bytes[i]
            encrypted.append(chr(encrypted_char))
        return ''.join(encrypted)
    
    @staticmethod
    def decrypt(encrypted_message: str, key: bytes) -> str:
        """Дешифрование XOR-зашифрованного сообщения"""
        # XOR симметричен, поэтому дешифрование - это та же операция
        return DHMessage.encrypt(encrypted_message, key)
    
    @staticmethod
    def format_for_display(encrypted: str) -> str:
        """Форматирование зашифрованного сообщения для отображения"""
        if not encrypted:
            return ""
        # Показываем первые 10 символов и длину
        if len(encrypted) <= 20:
            return encrypted
        return f"{encrypted[:10]}...{encrypted[-10:]} (длина: {len(encrypted)})"


class DHParticipant:
    """Участник обмена (Алиса, Боб или Ева)"""
    
    def __init__(self, name: str, p: int, g: int):
        self.name = name
        self.dh = DiffieHellman(p, g)
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
        self.encryption_key = None
    
    def generate_keys(self) -> int:
        """Генерация пары ключей"""
        self.private_key = self.dh.generate_private_key()
        self.public_key = self.dh.generate_public_key()
        print(f"  [{self.name}] Закрытый ключ: {self.private_key}")
        print(f"  [{self.name}] Открытый ключ:  {self.public_key}")
        return self.public_key
    
    def compute_secret(self, other_public_key: int) -> bytes:
        """Вычисление общего секрета и ключа шифрования"""
        self.shared_secret = self.dh.compute_shared_secret(other_public_key)
        self.encryption_key = self.dh.derive_key()
        print(f"  [{self.name}] Общий секрет: {self.shared_secret}")
        print(f"  [{self.name}] Ключ шифрования: {self.encryption_key.hex()[:16]}...")
        return self.encryption_key
    
    def send_message(self, message: str) -> str:
        """Отправка зашифрованного сообщения"""
        if self.encryption_key is None:
            raise ValueError(f"{self.name}: Ключ шифрования не установлен")
        encrypted = DHMessage.encrypt(message, self.encryption_key)
        print(f"  [{self.name}] Отправляет (зашифровано): {DHMessage.format_for_display(encrypted)}")
        return encrypted
    
    def receive_message(self, encrypted_message: str) -> str:
        """Прием и расшифровка сообщения"""
        if self.encryption_key is None:
            raise ValueError(f"{self.name}: Ключ шифрования не установлен")
        decrypted = DHMessage.decrypt(encrypted_message, self.encryption_key)
        print(f"  [{self.name}] Расшифровал: \"{decrypted}\"")
        return decrypted


def find_primitive_root(p: int) -> int:
    """
    Поиск примитивного корня по модулю p
    (для демонстрации используется упрощенный алгоритм)
    """
    # Для демонстрационных целей используем фиксированные значения
    known_roots = {
        23: 5,
        97: 5,
        101: 2,
        103: 5,
        107: 2,
        109: 6,
        113: 3,
        127: 3,
        131: 2,
        137: 3,
        139: 2,
        149: 2,
        151: 6,
        157: 5,
        163: 2,
        167: 5,
        173: 2,
        179: 2,
        181: 2,
        191: 19,
        193: 5,
        197: 2,
        199: 3,
    }
    
    if p in known_roots:
        return known_roots[p]
    
    # Если нет - пробуем найти (упрощенно)
    for g in range(2, p):
        if pow(g, (p - 1) // 2, p) != 1:
            return g
    
    return 2


def demonstrate_mitm_attack():
    """Демонстрация атаки посредника (Man-in-the-Middle)"""
    
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ АТАКИ ПОСРЕДНИКА (MITM) НА АЛГОРИТМ ДИФФИ-ХЕЛЛМАНА")
    print("=" * 70)
    
    # 1. Инициализация параметров
    print("\n[ШАГ 1] Инициализация параметров протокола")
    print("-" * 50)
    
    # Используем достаточно маленькое простое число для наглядности
    p = 97
    g = find_primitive_root(p)
    
    print(f"  Модуль (p):      {p}")
    print(f"  Генератор (g):   {g}")
    print(f"  Порядок группы:  {p - 1} = 2 ^5 * 3 (гладкое число, уязвимо для Pohlig-Hellman)")
    
    # 2. Генерация ключей участниками
    print("\n[ШАГ 2] Генерация ключей")
    print("-" * 50)
    
    alice = DHParticipant("Алиса", p, g)
    bob = DHParticipant("Боб", p, g)
    eve = DHParticipant("Ева (злоумышленник)", p, g)
    
    print("\n  Алиса генерирует ключи:")
    alice_public = alice.generate_keys()
    
    print("\n  Боб генерирует ключи:")
    bob_public = bob.generate_keys()
    
    print("\n  Ева генерирует ключи:")
    eve_public = eve.generate_keys()
    
    # 3. Атака посредника
    print("\n[ШАГ 3] АТАКА ПОСРЕДНИКА (Man-in-the-Middle)")
    print("-" * 50)
    print("  Ева перехватывает и подменяет открытые ключи!")
    
    print("\n  3.1. Алиса отправляет свой открытый ключ Бобу...")
    print(f"       Алиса -> Боб: {alice_public}")
    print(f"       Ева перехватывает A и отправляет E вместо него!")
    print(f"       Боб получает: {eve_public} (думая, что это ключ Алисы)")
    
    print("\n  3.2. Боб отправляет свой открытый ключ Алисе...")
    print(f"       Боб -> Алиса: {bob_public}")
    print(f"       Ева перехватывает B и отправляет E вместо него!")
    print(f"       Алиса получает: {eve_public} (думая, что это ключ Боба)")
    
    # 4. Вычисление общих секретов (с подменой)
    print("\n[ШАГ 4] Вычисление общих секретов (с подменой)")
    print("-" * 50)
    
    # Алиса вычисляет секрет с E (думая, что это Боб)
    print("\n  Алиса вычисляет общий секрет с ключом Евы:")
    alice_key = alice.compute_secret(eve_public)
    
    # Боб вычисляет секрет с E (думая, что это Алиса)
    print("\n  Боб вычисляет общий секрет с ключом Евы:")
    bob_key = bob.compute_secret(eve_public)
    
    # Ева вычисляет два секрета: с Алисой и с Бобом
    print("\n  Ева вычисляет общие секреты:")
    print("    Секрет с Алисой (используя ключ Алисы):")
    eve_key_alice = eve.compute_secret(alice_public)
    
    # Для второго соединения создаем новый объект с тем же закрытым ключом
    # ИСПРАВЛЕНИЕ: создаем объект и УСТАНАВЛИВАЕМ закрытый ключ через dh
    eve2 = DHParticipant("Ева (с Бобом)", p, g)
    # Копируем закрытый ключ Евы в объект dh
    eve2.dh.private_key = eve.private_key
    eve2.dh.public_key = eve.public_key
    # Также копируем в атрибуты самого участника
    eve2.private_key = eve.private_key
    eve2.public_key = eve.public_key
    
    print("    Секрет с Бобом (используя ключ Боба):")
    eve_key_bob = eve2.compute_secret(bob_public)
    
    # Проверяем, что ключи совпадают у каждой пары
    print("\n  Проверка ключей:")
    print(f"    Ключ Алисы: {alice_key.hex()[:16]}...")
    print(f"    Ключ Евы (с Алисой): {eve_key_alice.hex()[:16]}...")
    print(f"    {'✓ СОВПАДАЮТ' if alice_key == eve_key_alice else '✗ НЕ СОВПАДАЮТ'}")
    print(f"    Ключ Боба: {bob_key.hex()[:16]}...")
    print(f"    Ключ Евы (с Бобом): {eve_key_bob.hex()[:16]}...")
    print(f"    {'✓ СОВПАДАЮТ' if bob_key == eve_key_bob else '✗ НЕ СОВПАДАЮТ'}")
    
    # 5. Перехват и изменение сообщения
    print("\n[ШАГ 5] Ева перехватывает и изменяет сообщение")
    print("-" * 50)
    
    # Исходное сообщение от Алисы
    original_message = "Боб, пожалуйста, переведи 10000 долларов на мой счет № 1234567"
    print(f"  Исходное сообщение Алисы:")
    print(f"    \"{original_message}\"")
    
    # Алиса шифрует и отправляет (но перехватывает Ева)
    print("\n  5.1. Алиса шифрует сообщение ключом Евы:")
    alice_encrypted = alice.send_message(original_message)
    
    # Ева расшифровывает сообщение Алисы
    print("\n  5.2. Ева расшифровывает сообщение Алисы:")
    decrypted_by_eve = eve.receive_message(alice_encrypted)
    
    # Ева изменяет сообщение
    modified_message = "Боб, пожалуйста, переведи 10000 долларов на мой счет № 3217654"
    print(f"\n  5.3. Ева изменяет сообщение:")
    print(f"    Новое сообщение Евы: \"{modified_message}\"")
    
    # Ева шифрует измененное сообщение ключом Боба
    print("\n  5.4. Ева шифрует измененное сообщение ключом Боба:")
    eve_encrypted = DHMessage.encrypt(modified_message, eve_key_bob)
    print(f"    Зашифровано: {DHMessage.format_for_display(eve_encrypted)}")
    
    # Боб получает и расшифровывает (думая, что от Алисы)
    print("\n  5.5. Боб получает сообщение (думая, что от Алисы):")
    bob_received = bob.receive_message(eve_encrypted)
    
    # 6. Итог
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТ АТАКИ")
    print("=" * 70)
    print(f"""
    Алиса отправила:     "{original_message}"
    Боб получил:         "{bob_received}"
    
    РАЗЛИЧИЯ:
    - Номер счета изменен с 1234567 на 3217654
    - Деньги будут переведены злоумышленнику (Еве)!
    
    Вывод: Протокол Диффи-Хеллмана БЕЗ аутентификации уязвим для атаки "человек посередине" (Man-in-the-Middle).
    """)
    
    print("\n[СПОСОБЫ ЗАЩИТЫ]")
    print("-" * 50)
    print("""
    1. Использование цифровых подписей (RSA, ECDSA)
    2. Сертификаты X.509 (как в TLS / HTTPS)
    3. Статичные открытые ключи, подписанные доверенным центром
    4. Использование протоколов с аутентификацией (STS, SIGMA)
    """)


def demonstrate_birthday_attack_explanation():
    """Объяснение атаки дней рождения на дискретный логарифм"""
    print("\n" + "=" * 70)
    print("ОБЪЯСНЕНИЕ АТАКИ ДНЕЙ РОЖДЕНИЯ (ПАРАДОКС ДНЕЙ РОЖДЕНИЯ)")
    print("=" * 70)
    
    print("""
    Атака дней рождения (Birthday Attack) — это криптографическая атака,
    основанная на парадоксе дней рождения.

    ПАРАДОКС ДНЕЙ РОЖДЕНИЯ:
    В группе из 23 человек вероятность того, что у двух человек день рождения
    совпадает, составляет примерно 50%.

    ПРИМЕНЕНИЕ В КРИПТОАНАЛИЗЕ DH:
    1. Злоумышленник пытается найти коллизию в функции f(x) = g ^ x mod p
    2. Если найти два разных x и y, такие что f(x) = f(y), то: g ^ x ≡ g ^ y (mod p)  =>  g ^ (x - y) ≡ 1 (mod p)
    3. Это означает, что порядок g делит (x - y)
    4. Зная разность, можно восстановить закрытый ключ

    СЛОЖНОСТЬ:
    - Для группы порядка n требуется O(√n) операций
    - Для 256-битной группы это ~2 ^ 128 операций (невозможно)
    - Для 64-битной группы это ~2 ^ 32 операций (реально)

    ЗАЩИТА:
    - Использование достаточно больших групп (≥ 2048 бит для DH)
    - Использование эллиптических кривых (ECDH) — 256 бит достаточно
    - Использование безопасных простых чисел
    """)
    
    # Простая демонстрация коллизий
    print("\n[ДЕМОНСТРАЦИЯ КОЛЛИЗИЙ]")
    print("-" * 50)
    p = 97
    g = 5
    
    print(f"Модуль p = {p}, генератор g = {g}")
    print("Ищем коллизии для функции f(x) = g ^ x mod p:")
    
    values = {}
    found_collision = False
    
    for x in range(1, p):
        fx = pow(g, x, p)
        if fx in values:
            print(f"  НАЙДЕНА КОЛЛИЗИЯ: f({values[fx]}) = {fx} и f({x}) = {fx}")
            print(f"  Это означает, что g ^ {values[fx]} ≡ g ^ {x} mod {p}")
            print(f"  Разность: {x - values[fx]}")
            found_collision = True
            break
        values[fx] = x
    
    if not found_collision:
        print("  Коллизий не найдено (что нормально для этого p)")


def main():
    """Основная функция программы"""
    print("=" * 70)
    print("КРИПТОАНАЛИЗ АЛГОРИТМА ДИФФИ-ХЕЛЛМАНА")
    print("Демонстрация атак и уязвимостей")
    print("=" * 70)
    
    # Демонстрация основной атаки
    demonstrate_mitm_attack()
    
    # Дополнительное объяснение
    demonstrate_birthday_attack_explanation()
    
    print("\n" + "=" * 70)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 70)


if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов
    random.seed(42)
    main()