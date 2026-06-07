# 2. Многократная идентификация
import hashlib
import secrets
from typing import Dict, Optional

# ------------------------------------------------------------
# 1. Односторонняя функция H (SHA-256)
# ------------------------------------------------------------
def H(value: bytes, rounds: int = 1) -> bytes:
    """
    Применяет SHA-256 rounds раз (цепочка хэшей).
    """
    result = value
    for _ in range(rounds):
        result = hashlib.sha256(result).digest()
    return result

def to_hex(b: bytes) -> str:
    """Для удобного отображения байтов."""
    return b.hex()[:16] + "..."  # сокращённый вывод

# ------------------------------------------------------------
# 2. Пользователь (клиент)
# ------------------------------------------------------------
class User:
    def __init__(self, name: str, system):
        self.name = name
        self.system = system
        self.w = None          # финальный секрет (H^0(w))
        self.t = None          # максимальное число идентификаций
        self.current_index = 1

    def register(self, t: int) -> bool:
        """
        Шаг 1: пользователь запрашивает у системы случайное w.
        Система генерирует w, возвращает его пользователю (по защищённому каналу).
        """
        w_hex = self.system.generate_secret(self.name, t)
        if w_hex is None:
            print(f"[{self.name}] Ошибка регистрации: имя уже существует или t<=0")
            return False
        self.w = bytes.fromhex(w_hex)
        self.t = t
        self.current_index = 1
        print(f"[{self.name}] Зарегистрирован. Всего попыток: {t}")
        return True

    def authenticate(self) -> bool:
        """
        i-я идентификация.
        Пользователь отправляет (имя, i, w_i = H ^ {t - i}(w)).
        """
        if self.current_index > self.t:
            print(f"[{self.name}] Исчерпан лимит идентификаций ({self.t})")
            return False

        # Вычисляем w_i = H ^ {t - i}(w)
        i = self.current_index
        remaining = self.t - i   # сколько раз применить H
        w_i = H(self.w, rounds = remaining)

        print(f"[{self.name}] -> Системе: ({self.name}, {i}, {to_hex(w_i)})")
        ok = self.system.verify(self.name, i, w_i)

        if ok:
            self.current_index += 1
            print(f"[{self.name}] Успешный вход. Следующая попытка #{self.current_index}")
        else:
            print(f"[{self.name}] Ошибка аутентификации (неверный пароль или счётчик)")
        return ok

# ------------------------------------------------------------
# 3. Система (сервер)
# ------------------------------------------------------------
class System:
    def __init__(self):
        # user_data[username] = (last_hash, current_index, t)
        self.user_data: Dict[str, tuple[bytes, int, int]] = {}

    def generate_secret(self, username: str, t: int) -> Optional[str]:
        """
        Генерирует случайное w (32 байта), вычисляет H ^ t(w),
        сохраняет его и счётчик = 1.
        Возвращает w пользователю в hex.
        """
        if username in self.user_data or t <= 0:
            return None

        w = secrets.token_bytes(32)            # случайное w
        w0 = H(w, rounds = t)                    # начальный секрет H^t(w)

        self.user_data[username] = (w0, 1, t)
        print(f"[Система] Пользователь '{username}' зарегистрирован. "f"Храним H ^ {t}(w) = {to_hex(w0)}. Счётчик = 1")
        return w.hex()  # передаём w пользователю

    def verify(self, username: str, i: int, w_i: bytes) -> bool:
        """
        Проверка при i-й идентификации.
        Требует: i == i(A)   и   H(w_i) == last_hash
        """
        if username not in self.user_data:
            return False

        last_hash, expected_i, t = self.user_data[username]

        # 1) проверка счётчика
        if i != expected_i:
            print(f"[Система] Ошибка счётчика: ожидался {expected_i}, получен {i}")
            return False

        # 2) проверка H(w_i) == last_hash
        if H(w_i) != last_hash:
            print(f"[Система] Неверный пароль: H(w_i) != сохранённому хэшу")
            return False

        # Успех: обновляем данные
        new_hash = w_i
        new_index = expected_i + 1
        self.user_data[username] = (new_hash, new_index, t)

        print(f"[Система] Успех! Теперь храним H ^ {t - new_index + 1}(w) = {to_hex(new_hash)}, "f"счётчик = {new_index}")
        return True

# ------------------------------------------------------------
# 4. Демонстрация работы
# ------------------------------------------------------------
if __name__ == "__main__":
    # Инициализация системы
    server = System()

    # Пользователь Алиса
    alice = User("Alice", server)
    alice.register(t = 3)          # разрешаем 3 входа

    print("\n--- Попытка 1 (успешная) ---")
    alice.authenticate()

    print("\n--- Попытка 2 (успешная) ---")
    alice.authenticate()

    print("\n--- Попытка 3 (успешная) ---")
    alice.authenticate()

    print("\n--- Попытка 4 (должна провалиться) ---")
    alice.authenticate()

    # Попробуем подделать: создадим злоумышленника
    print("\n--- Атака: повторное использование старого пароля ---")
    # В реальности злоумышленник мог бы перехватить w_2 = H ^ {t - 2}(w)
    # и попытаться послать его снова. Смоделируем:
    # (Здесь в программе мы не сохраняем старые w_i, но по логике системы
    #  после успешного входа старый w_{i - 1} уже не подойдёт, так как
    #  last_hash изменился на w_i. Покажем это)
    print("Пользователь Mallory пытается подделать запрос:")
    # Для наглядности создадим отдельного злоумышленника, который не знает текущего состояния.
    mallory = User("Mallory", server)
    # Но регистрация нормальная — он не может подделать чужую аутентификацию без w.
    # Просто покажем, что сброс счётчика не помогает.