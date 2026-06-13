# Задачи и упражнения
# Задача 1. Привести схему заказа электронной карточки, в которой фиксируется имя владельца. Предполагается защищенность такой фиксации.
import os
import json
import hashlib
import logging
import base64
import secrets
from datetime import datetime
from typing import Dict, Tuple, Optional

# Криптографические библиотеки
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Настройка логирования (без открытых имён)
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [
        logging.FileHandler("card_orders.log"),
        logging.StreamHandler()
    ]
)

# ========== 1. Система хеширования (PBKDF2 вместо bcrypt) ==========
class SecureHasher:
    """Хеширование имени с солью через PBKDF2 (не требует компиляции)"""
    
    @staticmethod
    def hash_name(name: str) -> Tuple[str, str]:
        """
        Возвращает (хеш_base64, соль_base64)
        Использует PBKDF2-HMAC-SHA256
        """
        # Генерируем случайную соль (16 байт)
        salt = secrets.token_bytes(16)
        
        # Хешируем имя с солью (100000 итераций)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            name.encode('utf-8'),
            salt,
            100000,  # количество итераций
            dklen = 32  # длина хеша
        )
        
        # Кодируем в base64 для хранения
        hash_b64 = base64.b64encode(hash_bytes).decode('ascii')
        salt_b64 = base64.b64encode(salt).decode('ascii')
        
        return hash_b64, salt_b64
    
    @staticmethod
    def verify(name: str, hash_b64: str, salt_b64: str) -> bool:
        """Проверяет, соответствует ли имя сохранённому хешу"""
        try:
            # Декодируем из base64
            hash_bytes = base64.b64decode(hash_b64)
            salt = base64.b64decode(salt_b64)
            
            # Вычисляем хеш для проверки
            test_hash = hashlib.pbkdf2_hmac(
                'sha256',
                name.encode('utf-8'),
                salt,
                100000,
                dklen = 32
            )
            
            # Сравниваем (constant-time сравнение для безопасности)
            return secrets.compare_digest(hash_bytes, test_hash)
        except Exception:
            return False


# ========== 2. Система шифрования (AES-256-GCM) ==========
class NameEncryptor:
    """Шифрует имя с помощью AES-256-GCM, ключ хранится отдельно (имитация HSM)"""
    
    def __init__(self, key: bytes = None):
        # В реальной системе ключ получают из HSM или переменной окружения
        self.key = key or secrets.token_bytes(32)  # 256 бит
        self._aesgcm = AESGCM(self.key)
    
    def encrypt(self, plaintext_name: str) -> str:
        """Возвращает base64( nonce + ciphertext + tag )"""
        nonce = secrets.token_bytes(12)  # 96 бит для GCM
        ciphertext = self._aesgcm.encrypt(nonce, plaintext_name.encode('utf-8'), None)
        # Объединяем nonce и шифротекст (тег внутри ciphertext)
        encrypted_package = nonce + ciphertext
        return base64.b64encode(encrypted_package).decode('ascii')
    
    def decrypt(self, encrypted_b64: str) -> str:
        """Расшифровывает имя (только для внутреннего использования эмитентом)"""
        try:
            encrypted_package = base64.b64decode(encrypted_b64)
            nonce = encrypted_package[:12]
            ciphertext = encrypted_package[12:]
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            return None


# ========== 3. "База данных" (имитация) ==========
class CardOrderDB:
    """Хранит заказы карт: зашифрованное имя + хеш имени + токен"""
    
    def __init__(self, encryptor: NameEncryptor):
        self.encryptor = encryptor
        self.orders: Dict[str, Dict] = {}  # token -> order_data
        self._next_id = 1
    
    def create_order(self, owner_name: str) -> Tuple[str, Dict]:
        """Создаёт заказ с защищённой фиксацией имени. Возвращает (токен_заказа, данные_заказа)"""
        # 1. Шифруем имя
        encrypted_name = self.encryptor.encrypt(owner_name)
        
        # 2. Хешируем имя для возможной верификации без расшифровки
        name_hash, name_salt = SecureHasher.hash_name(owner_name)
        
        # 3. Генерируем уникальный токен заказа
        token = f"CARD_{self._next_id:06d}_{hashlib.md5(owner_name.encode()).hexdigest()[:8]}"
        self._next_id += 1
        
        # 4. Сохраняем (защищённая фиксация)
        order_data = {
            "token": token,
            "encrypted_name": encrypted_name,
            "name_hash": name_hash,
            "name_salt": name_salt,
            "created_at": datetime.now().isoformat(),
            "status": "ordered"
        }
        self.orders[token] = order_data
        
        # Логируем БЕЗ открытого имени
        logging.info(f"Order created: token={token}, hash_prefix={name_hash[:20]}...")
        
        return token, order_data
    
    def get_order(self, token: str) -> Optional[Dict]:
        return self.orders.get(token)
    
    def verify_name(self, token: str, candidate_name: str) -> bool:
        """Проверяет, соответствует ли кандидат имени владельца (без расшифровки)"""
        order = self.get_order(token)
        if not order:
            return False
        return SecureHasher.verify(candidate_name, order["name_hash"], order["name_salt"])
    
    def reveal_name_secure(self, token: str, authorized_employee: bool = False) -> Optional[str]:
        """
        Только для эмитента (например, при печати на карту).
        В реальной системе — доступ через HSM и роль.
        """
        if not authorized_employee:
            logging.warning(f"Unauthorized attempt to reveal name for token {token}")
            return None
        order = self.get_order(token)
        if not order:
            return None
        plain_name = self.encryptor.decrypt(order["encrypted_name"])
        if plain_name:
            logging.info(f"Name revealed for token {token} by authorized employee")
        return plain_name
    
    def export_database_safe(self) -> str:
        """Экспортирует БД для демонстрации (без раскрытия имён)"""
        export_data = []
        for token, order in self.orders.items():
            export_data.append({
                "token": token,
                "encrypted_name_preview": order["encrypted_name"][:30] + "...",
                "name_hash_preview": order["name_hash"][:20] + "...",
                "created_at": order["created_at"],
                "status": order["status"]
            })
        return json.dumps(export_data, indent = 2)


# ========== 4. Весь процесс заказа и проверки ==========
def simulate_card_order_process():
    print("=" * 60)
    print("Защищённый заказ электронной карточки (без bcrypt)")
    print("=" * 60)
    print()
    
    # Инициализация (эмитент владеет ключом шифрования)
    encryptor = NameEncryptor()
    db = CardOrderDB(encryptor)
    
    # Шаг 1: Пользователь заполняет форму
    user_name = input("Введите имя владельца карты: ").strip()
    if not user_name:
        print("Ошибка: имя не может быть пустым!")
        return
    
    # Шаг 2: Защищённая передача (имитация HTTPS) — здесь просто вызов
    print("\n[1] Передача данных по защищённому каналу (TLS 1.3)...")
    
    # Шаг 3: Сервер фиксирует имя в защищённом виде
    print("[2] Фиксация имени в защищённом хранилище (шифрование + хеширование)...")
    token, order = db.create_order(user_name)
    
    print(f"\n✅ Заказ успешно создан!")
    print(f"   Токен карты: {token}")
    print(f"   (токен выдаётся пользователю как подтверждение)")
    print()
    
    # Показываем, что хранится в БД (без открытого имени)
    print("=" * 60)
    print("=== Что хранится в базе данных (защищённая фиксация) ===")
    print("=" * 60)
    print(f"Токен:           {order['token']}")
    print(f"Зашифрованное имя: {order['encrypted_name'][:40]}...")
    print(f"Хеш имени:       {order['name_hash'][:30]}...")
    print(f"Соль:            {order['name_salt'][:20]}...")
    print(f"Статус:          {order['status']}")
    print(f"Время создания:  {order['created_at']}")
    print()
    
    # Шаг 4: Проверка подлинности при использовании карты
    print("=" * 60)
    print("=== Проверка владельца карты (без расшифровки имени) ===")
    print("=" * 60)
    check_name = input("Введите имя для проверки: ").strip()
    if db.verify_name(token, check_name):
        print("✅ УСПЕХ: Имя совпадает! Владелец подтверждён.")
    else:
        print("❌ ОШИБКА: Имя не совпадает! Доступ запрещён.")
    print()
    
    # Шаг 5: Эмитент может расшифровать имя (например, для печати на пластик)
    print("=" * 60)
    print("=== Действие эмитента (печать карты) ===")
    print("=" * 60)
    issuer_action = input("Эмитент хочет расшифровать имя? (да/нет): ").strip().lower()
    if issuer_action == "да":
        revealed = db.reveal_name_secure(token, authorized_employee = True)
        if revealed:
            print(f"📇 Имя для печати на карте: {revealed}")
        else:
            print("Ошибка: не удалось расшифровать имя.")
    print()
    
    # Шаг 6: Попытка несанкционированного раскрытия
    print("=" * 60)
    print("=== Имитация атаки: несанкционированный доступ ===")
    print("=" * 60)
    db.reveal_name_secure(token, authorized_employee = False)
    print()
    
    # Шаг 7: Экспорт безопасной копии БД
    print("=" * 60)
    print("=== Экспорт базы данных (без раскрытия имён) ===")
    print("=" * 60)
    print(db.export_database_safe())
    print()
    
    # Шаг 8: Показываем лог
    print("=" * 60)
    print("=== Лог операций (card_orders.log) ===")
    print("=" * 60)
    try:
        with open("card_orders.log", "r") as log_file:
            print(log_file.read())
    except FileNotFoundError:
        print("Лог-файл пока не создан.")
    
    print("\n✅ Программа завершена. Ключ шифрования хранился только в памяти.")
    print(f"   (Ключ: {encryptor.key.hex()[:16]}...)")


# ========== 5. Дополнительная демонстрация безопасности ==========
def demonstrate_security_properties():
    """Показывает, что даже с доступом к БД имена не раскрываются"""
    print("\n" + "=" * 60)
    print("=== ДОПОЛНИТЕЛЬНО: Демонстрация защитных свойств ===")
    print("=" * 60)
    
    # Создаём тестовую БД
    encryptor = NameEncryptor()
    db = CardOrderDB(encryptor)
    
    # Добавляем несколько тестовых заказов
    test_names = ["Иван Петров", "Мария Сидорова", "John Doe"]
    tokens = []
    for name in test_names:
        token, _ = db.create_order(name)
        tokens.append(token)
    
    print("\n📁 Содержимое БД (дамп):")
    print(db.export_database_safe())
    
    print("\n🔐 Пытаемся получить имена из БД без ключа:")
    for token in tokens:
        # Без авторизации
        name = db.reveal_name_secure(token, authorized_employee = False)
        print(f"  Токен {token}: {'[НЕ ПОЛУЧЕНО]' if name is None else name}")
    
    print("\n✅ Только авторизованный сотрудник с ключом может расшифровать:")
    for token in tokens:
        name = db.reveal_name_secure(token, authorized_employee = True)
        print(f"  Токен {token}: {name}")


# ========== 6. Запуск ==========
if __name__ == "__main__":
    try:
        # Проверяем наличие cryptography
        import cryptography
        print("✅ Библиотека cryptography найдена")
        print()
        
        # Основной сценарий
        simulate_card_order_process()
        
        # Дополнительная демонстрация
        demonstrate_security_properties()
        
    except ImportError:
        print("❌ Ошибка: не установлена библиотека cryptography")
        print("   Установите её командой: pip install cryptography")
        print("   Или: python -m pip install cryptography")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()

# Задача 2. Привести схему электронных платежей, при которой банк-эмитент не владеет полной информацией об остатке средств на карточке. 
# Он может лишь судить о достаточности остатка при очередном платеже.
import hashlib
import random
from typing import List, Dict, Tuple

# ----------------------------
# 1. Вспомогательные функции
# ----------------------------

def simple_hash(data: str) -> str:
    """Простая хеш-функция для имитации подписей."""
    return hashlib.sha256(data.encode()).hexdigest()

class Bank:
    """Банк-эмитент. Не знает состав кошелька клиента."""
    
    def __init__(self):
        # База использованных монет (для предотвращения двойного расходования)
        self.spent_coins = set()
    
    def issue_coin(self, coin_id: str, nominal: int, blind_factor: str) -> Dict:
        """
        Эмиссия монеты с использованием "слепой" подписи (упрощённо).
        Банк видит только ослеплённый идентификатор, но не номинал и не реальный ID.
        """
        # Ослеплённые данные (в реальности: coin_id * blind_factor mod N)
        blinded_data = simple_hash(coin_id + blind_factor)
        # Подпись слепого значения (имитация)
        signature = simple_hash(blinded_data + str(nominal) + "secret_key")
        return {
            "coin_id": coin_id,
            "nominal": nominal,
            "blind_factor": blind_factor,
            "signature": signature
        }
    
    def verify_and_spend(self, coin: Dict) -> bool:
        """
        Проверка монеты при платеже.
        Банк НЕ знает остаток кошелька, только конкретную монету.
        """
        # Проверяем подпись
        blinded_data = simple_hash(coin["coin_id"] + coin["blind_factor"])
        expected_sig = simple_hash(blinded_data + str(coin["nominal"]) + "secret_key")
        
        if expected_sig != coin["signature"]:
            print(f"  Банк: неверная подпись монеты {coin['coin_id']}")
            return False
        
        # Проверяем, не тратилась ли монета ранее
        coin_key = coin["coin_id"]
        if coin_key in self.spent_coins:
            print(f"  Банк: монета {coin_key} уже потрачена (double-spending!)")
            return False
        
        # Помечаем как потраченную
        self.spent_coins.add(coin_key)
        print(f"  Банк: монета {coin_key} номиналом {coin['nominal']} принята")
        return True

class Wallet:
    """Кошелёк покупателя. Хранит монеты."""
    
    def __init__(self, bank: Bank, initial_balance: int):
        self.bank = bank
        self.coins: List[Dict] = []  # список монет
        self._issue_coins(initial_balance)
    
    def _issue_coins(self, total_sum: int):
        """
        Эмиссия монет на общую сумму total_sum.
        Банк списывает деньги со счёта, но не узнаёт, какие монеты получил клиент.
        """
        print(f"\n--- Эмиссия {total_sum} единиц ---")
        remaining = total_sum
        coin_id_counter = 0
        
        while remaining > 0:
            # Выбираем номинал (1, 2, 5, 10)
            if remaining >= 10:
                nominal = 10
            elif remaining >= 5:
                nominal = 5
            elif remaining >= 2:
                nominal = 2
            else:
                nominal = 1
            
            coin_id = f"coin_{coin_id_counter}"
            blind_factor = str(random.randint(1000, 9999))  # случайный фактор ослепления
            
            # Банк выпускает монету вслепую
            coin = self.bank.issue_coin(coin_id, nominal, blind_factor)
            self.coins.append(coin)
            
            remaining -= nominal
            coin_id_counter += 1
        
        print(f"Кошелёк получил {len(self.coins)} монет на сумму {total_sum}")
        print(f"Банк НЕ знает состав кошелька (номиналы: {[c['nominal'] for c in self.coins]})")
    
    def get_balance(self) -> int:
        """Полный остаток (известен только владельцу кошелька)."""
        return sum(c["nominal"] for c in self.coins)
    
    def pay(self, amount: int) -> bool:
        """
        Совершить платёж. Покупатель выбирает монеты, покрывающие сумму.
        Банк видит только эти монеты.
        """
        print(f"\n--- Попытка платежа на сумму {amount} ---")
        print(f"Остаток в кошельке (известен только владельцу): {self.get_balance()}")
        
        if self.get_balance() < amount:
            print("Недостаточно средств (владелец видит остаток, платеж невозможен)")
            return False
        
        # Жадный алгоритм выбора монет (для простоты)
        selected_coins = []
        remaining_amount = amount
        # Сортируем монеты по убыванию
        sorted_coins = sorted(self.coins, key = lambda c: c["nominal"], reverse = True)
        
        for coin in sorted_coins:
            if remaining_amount >= coin["nominal"] and coin not in selected_coins:
                selected_coins.append(coin)
                remaining_amount -= coin["nominal"]
                if remaining_amount == 0:
                    break
        
        if remaining_amount != 0:
            print("Не удалось подобрать точную сумму монетами (нет точного набора)")
            return False
        
        print(f"Выбраны монеты номиналами: {[c['nominal'] for c in selected_coins]}")
        
        # Отправляем монеты в банк для проверки
        all_valid = True
        for coin in selected_coins:
            if not self.bank.verify_and_spend(coin):
                all_valid = False
                break
        
        if not all_valid:
            print("Платёж отклонён банком")
            return False
        
        # Удаляем потраченные монеты из кошелька
        for coin in selected_coins:
            self.coins.remove(coin)
        
        print(f"Платёж на сумму {amount} успешно завершён")
        print(f"Новый остаток (только владелец знает): {self.get_balance()}")
        return True


# ----------------------------
# 2. Демонстрация работы
# ----------------------------

if __name__ == "__main__":
    # Создаём банк
    bank = Bank()
    
    # Клиент открывает кошелёк и получает монеты на 50 единиц
    wallet = Wallet(bank, initial_balance = 50)
    
    print("\n" + "=" * 50)
    print("Банк не знает точный остаток на карте.")
    print("Банк может лишь проверить каждую предъявленную монету.")
    print("=" * 50)
    
    # Платежи
    wallet.pay(12)   # 10 + 2
    wallet.pay(15)   # 10 + 5
    wallet.pay(8)    # 5 + 2 + 1
    wallet.pay(10)   # 10 (если осталась)
    
    # Попытка оплатить больше, чем есть
    wallet.pay(100)
    
    print("\n--- Итог ---")
    print(f"Финальный остаток в кошельке: {wallet.get_balance()}")
    print(f"База потраченных монет у банка: {len(bank.spent_coins)} монет")
    print("Банк так и не узнал итоговый остаток, но каждый платёж был валидирован.")