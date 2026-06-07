# 1. Основные понятия
import hashlib
import os
import time
from typing import Dict, Tuple, List

# ============================================================
# 1. ХРАНЕНИЕ ФИКСИРОВАННЫХ ПАРОЛЕЙ (как в UNIX)
# Используем одностороннюю функцию (хэш SHA-256) вместо DES
# ============================================================

class PasswordStorage:
    """Хранит образы паролей (хеши) вместо открытых паролей"""
    
    def __init__(self):
        # Словарь: username -> (хеш_пароля, соль)
        self._storage: Dict[str, Tuple[bytes, bytes]] = {}
    
    def _hash_password(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """Односторонняя функция: превращает пароль в хеш с солью"""
        if salt is None:
            salt = os.urandom(16)  # случайная соль
        # Используем PBKDF2 для замедления (защита от перебора)
        hash_value = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hash_value, salt
    
    def set_password(self, username: str, password: str):
        """Установка пароля (хранится только хеш)"""
        hash_val, salt = self._hash_password(password)
        self._storage[username] = (hash_val, salt)
        print(f"[Система] Пароль для '{username}' установлен и захэширован (хранится образ).")
    
    def verify_password(self, username: str, password: str) -> bool:
        """Проверка пароля: система хэширует введённый пароль и сравнивает"""
        if username not in self._storage:
            return False
        stored_hash, salt = self._storage[username]
        test_hash, _ = self._hash_password(password, salt)
        return test_hash == stored_hash


# ============================================================
# 2. PIN + ФИЗИЧЕСКИЙ НОСИТЕЛЬ (симуляция карты)
# ============================================================

class SmartCard:
    """Физический носитель (карта) с блокировкой после 3 неудачных вводов PIN"""
    
    def __init__(self, card_id: str, correct_pin: str):
        self.card_id = card_id
        self._correct_pin = correct_pin
        self._failed_attempts = 0
        self._is_blocked = False
    
    def verify_pin(self, entered_pin: str) -> bool:
        """Проверка PIN с конфискацией карты после 3 ошибок"""
        if self._is_blocked:
            print(f"[Карта {self.card_id}] КАРТА КОНФИСКОВАНА (слишком много ошибок).")
            return False
        
        if entered_pin == self._correct_pin:
            self._failed_attempts = 0
            print(f"[Карта {self.card_id}] PIN верный.")
            return True
        else:
            self._failed_attempts += 1
            remaining = 3 - self._failed_attempts
            print(f"[Карта {self.card_id}] Неверный PIN. Осталось попыток: {remaining}")
            if self._failed_attempts >= 3:
                self._is_blocked = True
                print(f"[Карта {self.card_id}] КАРТА КОНФИСКОВАНА!")
            return False


# ============================================================
# 3. ТЕХНОЛОГИЯ PASSKEY
# Пароль -> односторонняя функция -> ключ шифрования
# ============================================================

class PasskeyExample:
    """Passkey: пароль преобразуется в ключ шифрования"""
    
    @staticmethod
    def derive_key(password: str, context: str = "passkey") -> bytes:
        """Одностороннее преобразование пароля в ключ (например, для шифрования)"""
        # Смешиваем пароль с контекстом, чтобы избежать коллизий
        material = f"{context}:{password}".encode('utf-8')
        # Возвращаем 32-байтный ключ (для AES-256)
        key = hashlib.sha256(material).digest()
        return key
    
    @staticmethod
    def demo():
        print("\n--- Пример Passkey ---")
        user_password = "my_secret_phrase"
        key = PasskeyExample.derive_key(user_password)
        print(f"Пароль пользователя: {user_password}")
        print(f"Полученный ключ шифрования (hex): {key.hex()}")
        print("Односторонняя функция: восстановить пароль из ключа невозможно.")


# ============================================================
# 4. ОДНОРАЗОВЫЕ ПАРОЛИ (список пар)
# ============================================================

class OneTimePassword:
    """
    Используется список допустимых пар.
    Пользователь выбирает пару, система знает, что правильный пароль - второй элемент.
    Каждая пара используется один раз.
    """
    
    def __init__(self):
        # Хранилище: для каждого пользователя список кортежей (index, (prompt, correct_password))
        self._user_otps: Dict[str, List[Tuple[int, Tuple[str, str]]]] = {}
    
    def generate_otp_list(self, username: str, num_passwords: int = 5):
        """Генерация списка пар паролей для пользователя"""
        pairs = []
        for i in range(num_passwords):
            prompt = f"OTP-{i+1}-prompt-{os.urandom(2).hex()}"  # первый элемент (вопрос/метка)
            correct = f"pass-{os.urandom(4).hex()}"              # второй элемент (правильный пароль)
            pairs.append((i, (prompt, correct)))
        self._user_otps[username] = pairs
        print(f"[OTP] Для {username} сгенерировано {num_passwords} одноразовых пар (пар).")
        return pairs
    
    def get_available_prompts(self, username: str) -> List[Tuple[int, str]]:
        """Возвращает список доступных prompt'ов (первых элементов пар)"""
        if username not in self._user_otps:
            return []
        return [(idx, prompt) for idx, (prompt, _) in self._user_otps[username]]
    
    def verify_otp(self, username: str, prompt_text: str, entered_password: str) -> bool:
        """Проверка: правильный пароль — это второй элемент пары"""
        if username not in self._user_otps:
            return False
        
        for idx, (prompt, correct) in enumerate(self._user_otps[username]):
            if prompt == prompt_text:
                if entered_password == correct:
                    # Удаляем использованную пару
                    del self._user_otps[username][idx]
                    print(f"[OTP] Пара использована. Осталось пар: {len(self._user_otps[username])}")
                    return True
                else:
                    return False
        return False


# ============================================================
# 5. ДЕМОНСТРАЦИЯ ПРОТОКОЛА АУТЕНТИФИКАЦИИ (реальное время)
# ============================================================

class AuthenticationProtocol:
    """
    Реализует процедуру аутентификации с ответами: кто, где, когда?
    Устойчивость к подбору, подлогу, подделке (базовая).
    """
    
    def __init__(self):
        self.password_storage = PasswordStorage()
        self.otp_system = OneTimePassword()
        self.sessions = {}  # username -> timestamp последней аутентификации
    
    def register_user(self, username: str, password: str):
        """Регистрация с фиксированным паролем (слабая аутентификация)"""
        self.password_storage.set_password(username, password)
    
    def authenticate_with_password(self, username: str, password: str, client_ip: str) -> bool:
        """Аутентификация по паролю — отвечает: кто, где, когда?"""
        print(f"\n[Аутентификация] Кто: {username}, Где: {client_ip}, Когда: {time.ctime()}")
        
        if self.password_storage.verify_password(username, password):
            self.sessions[username] = time.time()
            print(f"[Результат] ✅ Пользователь {username} АУТЕНТИФИЦИРОВАН (пароль)")
            return True
        else:
            print(f"[Результат] ❌ Отклонено: неверный пароль для {username}")
            return False
    
    def demo_pin_with_card(self):
        """Демонстрация PIN + физическая карта"""
        print("\n=== Демонстрация PIN + физический носитель ===")
        card = SmartCard("Visa-1234", correct_pin = "1234")
        
        # Попытки ввода PIN
        card.verify_pin("1111")  # ошибка
        card.verify_pin("2222")  # ошибка
        card.verify_pin("1234")  # верно -> не заблокировано, т.к. было только 2 ошибки
        card.verify_pin("0000")  # снова ошибка, но карта ещё активна
        card.verify_pin("9999")  # третья ошибка после успешного ввода? Счётчик обнулился после успеха
        
        # Создадим новую карту для демонстрации блокировки
        print("\n--- Карта, которая будет сконфискована ---")
        card2 = SmartCard("BlockedCard", correct_pin = "0000")
        for pin in ["1111", "2222", "3333"]:
            card2.verify_pin(pin)
    
    def demo_otp(self):
        """Демонстрация одноразовых паролей"""
        print("\n=== Демонстрация одноразовых паролей ===")
        user = "alice_otp"
        self.otp_system.generate_otp_list(user, num_passwords = 3)
        
        prompts = self.otp_system.get_available_prompts(user)
        print(f"Доступные 'первые элементы пар': {prompts}")
        
        # Симуляция правильного использования
        if prompts:
            idx, prompt_text = prompts[0]
            # Здесь в реальности пользователь знает правильный пароль для этого prompt
            # Для демо: нужно знать сгенерированный correct, но мы не храним его открыто.
            # Зато в системе хранятся пары. Давайте получим correct из системы (для демо):
            correct_pw = None
            for i, (p, c) in self.otp_system._user_otps[user]:
                if p == prompt_text:
                    correct_pw = c
                    break
            
            print(f"Пользователь вводит пароль: {correct_pw} для промпта '{prompt_text}'")
            result = self.otp_system.verify_otp(user, prompt_text, correct_pw)
            print(f"Результат проверки OTP: {result}")
            
            # Повторно использовать тот же prompt нельзя
            result2 = self.otp_system.verify_otp(user, prompt_text, correct_pw)
            print(f"Повторная попытка с тем же паролем: {result2} (должно быть False)")
    
    def run_full_demo(self):
        """Полная демонстрация протокола аутентификации"""
        print("=" * 60)
        print("ПРОГРАММА АУТЕНТИФИКАЦИИ (по тексту)")
        print("=" * 60)
        
        # Регистрация
        self.register_user("ivan", "StrongP@ssw0rd")
        
        # Успешная аутентификация
        self.authenticate_with_password("ivan", "StrongP@ssw0rd", "192.168.1.100")
        
        # Неуспешная аутентификация
        self.authenticate_with_password("ivan", "wrong_password", "192.168.1.101")
        
        # Несуществующий пользователь
        self.authenticate_with_password("petr", "anything", "10.0.0.1")
        
        # Демонстрация PIN + карта
        self.demo_pin_with_card()
        
        # Демонстрация Passkey
        PasskeyExample.demo()
        
        # Демонстрация OTP
        self.demo_otp()
        
        print("\n" + "=" * 60)
        print("Все требования из текста выполнены:")
        print("✓ Пользователь доказывает правомочность, проверяющий проверяет")
        print("✓ Вероятность ошибки пренебрежимо мала (хеши, соли, OTP)")
        print("✓ Устойчивость к подбору (PBKDF2), подлогу (соли), подделке (одноразовые)")
        print("✓ Протокол реального времени — отвечает: кто, где, когда")
        print("=" * 60)


if __name__ == "__main__":
    protocol = AuthenticationProtocol()
    protocol.run_full_demo()