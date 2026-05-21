# 4. Хэш-функции
import hashlib
import secrets
from typing import Union, Any

# Простая имитация хэш-функции со значениями в конечном поле (GF(p))
class HashInFiniteField:
    """Хэш-функция, возвращающая значение в конечном поле по модулю p"""
    
    def __init__(self, p: int):
        self.p = p  # модуль конечного поля GF(p)
    
    def hash(self, message: str) -> int:
        """Вычисляет хэш сообщения как число в конечном поле GF(p)"""
        # Берём SHA-256, переводим в число и берём по модулю p
        h = hashlib.sha256(message.encode()).hexdigest()
        int_hash = int(h, 16)
        return int_hash % self.p


# Простая имитация хэш-функции со значениями в кольце вычетов Z_n
class HashInResidueRing:
    """Хэш-функция, возвращающая значение в кольце вычетов Z_n"""
    
    def __init__(self, n: int):
        self.n = n  # модуль кольца вычетов
    
    def hash(self, message: str) -> int:
        h = hashlib.sha256(message.encode()).hexdigest()
        int_hash = int(h, 16)
        return int_hash % self.n


# Основной класс, демонстрирующий стандартную криптографическую хэш-функцию
class CryptographicHashDemo:
    """Демонстрация использования хэш-функций в криптографии"""
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm
        self.hash_func = getattr(hashlib, algorithm)
    
    def compute_digest(self, message: Union[str, bytes]) -> str:
        """Вычисляет дайджест h(m) для сообщения m"""
        if isinstance(message, str):
            message = message.encode()
        h = self.hash_func(message)
        return h.hexdigest()
    
    def secure_storage_demo(self, password: str) -> str:
        """Демонстрация безопасного хранения паролей (образ данных)"""
        # Добавляем "соль" для защиты от радужных таблиц
        salt = secrets.token_hex(16)
        stored_hash = hashlib.pbkdf2_hmac(
            self.algorithm, 
            password.encode(), 
            salt.encode(), 
            100000
        ).hex()
        return f"{salt}:{stored_hash}"
    
    def verify_password(self, stored: str, candidate: str) -> bool:
        """Проверка пароля по сохранённому хэшу"""
        salt, stored_hash = stored.split(":")
        candidate_hash = hashlib.pbkdf2_hmac(
            self.algorithm, 
            candidate.encode(), 
            salt.encode(), 
            100000
        ).hex()
        return candidate_hash == stored_hash


# Демонстрация свойств односторонней функции
def demo_one_way_property():
    """Демонстрирует, что хэш-функция односторонняя:
       легко вычислить h(m), но сложно найти m по h(m)"""
    
    demo = CryptographicHashDemo()
    message = "Секретное сообщение"
    
    # Легко: вычисляем хэш
    digest = demo.compute_digest(message)
    print(f"Сообщение: {message}")
    print(f"Хэш (дайджест): {digest}")
    print("\n✅ Из сообщения легко получить хэш.")
    print("❌ Из хэша практически невозможно восстановить исходное сообщение.\n")


def demo_collision_resistance():
    """Демонстрирует устойчивость к коллизиям"""
    
    demo = CryptographicHashDemo()
    
    msg1 = "Привет, мир!"
    msg2 = "Привет, мир! "  # Отличается пробелом в конце
    
    hash1 = demo.compute_digest(msg1)
    hash2 = demo.compute_digest(msg2)
    
    print(f"Сообщение 1: '{msg1}' -> {hash1[:16]}...")
    print(f"Сообщение 2: '{msg2}' -> {hash2[:16]}...")
    print(f"Хэши совпадают? {hash1 == hash2}")
    print("✅ Даже небольшое изменение сообщения полностью меняет хэш.\n")


def demo_digest_usage():
    """Демонстрирует использование дайджестов"""
    
    demo = CryptographicHashDemo()
    
    # Дайджест для целого документа
    document = "Это важный договор между сторонами А и Б..."
    digest = demo.compute_digest(document)
    
    print("📄 Документ: договор.pdf")
    print(f"🔑 Дайджест (отпечаток): {digest[:32]}...")
    print("Использование: подписание документа, проверка целостности\n")


def demo_finite_field_hash():
    """Демонстрирует хэш-функцию со значениями в конечном поле"""
    
    # Конечное поле GF(97) - простое поле характеристики 97
    field_hash = HashInFiniteField(p = 97)
    
    value = field_hash.hash("тестовое сообщение")
    print(f"Хэш в GF(97): {value}")
    print(f"Проверка: 0 <= {value} < 97\n")


def demo_residue_ring_hash():
    """Демонстрирует хэш-функцию со значениями в кольце вычетов"""
    
    # Кольцо вычетов Z_100
    ring_hash = HashInResidueRing(n = 100)
    
    value = ring_hash.hash("тестовое сообщение")
    print(f"Хэш в Z_100: {value}")
    print(f"Проверка: 0 <= {value} < 100\n")


def main():
    print("=" * 60)
    print("КРИПТОГРАФИЧЕСКИЕ ХЭШ-ФУНКЦИИ")
    print("=" * 60)
    
    # Основные свойства
    demo_one_way_property()
    demo_collision_resistance()
    demo_digest_usage()
    
    # Хэши в алгебраических структурах
    print("--- Хэш-функции со значениями в алгебраических структурах ---")
    demo_finite_field_hash()
    demo_residue_ring_hash()
    
    # Безопасное хранение паролей
    print("--- Безопасное хранение паролей (образ данных) ---")
    demo_hash = CryptographicHashDemo()
    
    password = "my_secure_password"
    stored = demo_hash.secure_storage_demo(password)
    print(f"Пароль: {password}")
    print(f"Хранится в БД: {stored[:30]}...")
    
    # Проверка пароля
    is_valid = demo_hash.verify_password(stored, "my_secure_password")
    print(f"Проверка правильного пароля: {is_valid}")
    
    is_valid_fake = demo_hash.verify_password(stored, "wrong_password")
    print(f"Проверка неправильного пароля: {is_valid_fake}")
    
    print("\n" + "=" * 60)
    print("ЗАКЛЮЧЕНИЕ:")
    print("- Хэш-функции преобразуют сообщение произвольной длины")
    print("  в последовательность фиксированной длины (дайджест)")
    print("- Являются односторонними: легко вычислить, сложно обратить")
    print("- Используются для дайджестов, безопасного хранения, подписей")
    print("=" * 60)


if __name__ == "__main__":
    main()