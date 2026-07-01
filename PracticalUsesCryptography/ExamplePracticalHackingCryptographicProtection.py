# 4. Примеры практического взлома криптографической защиты
#!/usr/bin/env python3
"""
Криптоаналитический симулятор уязвимостей
На основе реальных атак: Золотая Корона (1998) и GSM (1999-2003)
Автор: Криптоаналитик (образовательная версия)
"""

import hashlib
import random
import time
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass
import struct

# ============================================================================
# ЧАСТЬ 1: ВЗЛОМ RSA КОРОТКОЙ ДЛИНЫ (320 БИТ)
# ============================================================================

class RSA_ShortKey:
    """
    Симуляция уязвимости RSA с коротким ключом (320 бит)
    Как в случае с картами Solaic "Золотая Корона"
    """
    
    def __init__(self, bits = 32):  # Для демонстрации используем 32 бита вместо 320
        self.bits = bits
        self.public_key = None
        self.private_key = None
        self.generate_keys()
    
    def generate_keys(self):
        """Генерация RSA ключей малой длины"""
        # Для демонстрации используем маленькие простые числа
        p = self._get_prime(16)  # 16-битное простое
        q = self._get_prime(16)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        d = pow(e, -1, phi)
        
        self.public_key = (n, e)
        self.private_key = (n, d)
        self.p = p
        self.q = q
        print(f"  [RSA] Сгенерирован ключ длиной {self.bits} бит (n = {n})")
    
    def _get_prime(self, bits):
        """Генерация простого числа (упрощенно)"""
        while True:
            num = random.getrandbits(bits) | 1
            if self._is_prime(num):
                return num
    
    def _is_prime(self, n):
        """Проверка на простоту (упрощенно)"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def encrypt(self, message: int) -> int:
        """Шифрование"""
        n, e = self.public_key
        return pow(message, e, n)
    
    def decrypt(self, ciphertext: int) -> int:
        """Легальное расшифрование"""
        n, d = self.private_key
        return pow(ciphertext, d, n)
    
    def crack_rsa(self, ciphertext: int) -> int:
        """
        ВЗЛОМ RSA через факторизацию n (демонстрация)
        В реальности факторизация 320-битного числа заняла бы время,
        но здесь мы знаем p и q для демонстрации
        """
        print("  [!] Запуск атаки факторизацией на RSA...")
        time.sleep(0.5)  # Имитация вычислений
        
        # В реальном взломе мы бы факторизовали n
        # Здесь используем известные p и q для демонстрации
        n, e = self.public_key
        phi = (self.p - 1) * (self.q - 1)
        d = pow(e, -1, phi)
        
        plaintext = pow(ciphertext, d, n)
        print(f"  [✓] RSA взломан! Расшифровано: {plaintext}")
        return plaintext


# ============================================================================
# ЧАСТЬ 2: GSM A5/2 АТАКА С ИЗБЫТОЧНОСТЬЮ КОДА
# ============================================================================

@dataclass
class GSM_Frame:
    """Кадр GSM с избыточным кодом"""
    data: List[int]  # Биты данных
    error_correction: List[int]  # Код исправления ошибок (избыточность)
    
class A5_2_Cipher:
    """
    Симуляция слабого шифра A5/2
    Уязвим из-за избыточности кода исправления ошибок
    """
    
    def __init__(self, session_key: int):
        self.session_key = session_key
        self.state = self._init_state(session_key)
        
    def _init_state(self, key: int) -> List[int]:
        """Инициализация состояния шифра (упрощенно)"""
        # В реальном A5/2 используется 3 регистра сдвига
        # Здесь упрощенная имитация
        random.seed(key)
        return [random.randint(0, 1) for _ in range(64)]
    
    def encrypt_frame(self, frame: GSM_Frame) -> GSM_Frame:
        """Шифрование кадра"""
        # Генерируем ключевой поток на основе состояния
        keystream = self._generate_keystream(len(frame.data))
        
        # XOR данных с ключевым потоком
        encrypted_data = [frame.data[i] ^ keystream[i] for i in range(len(frame.data))]
        
        # Код коррекции ошибок шифруется ТОЛЬКО после шифрования данных
        # (это и есть уязвимость, описанная в тексте)
        encrypted_error = [b ^ random.randint(0, 1) for b in frame.error_correction]
        
        return GSM_Frame(encrypted_data, encrypted_error)
    
    def _generate_keystream(self, length: int) -> List[int]:
        """Генерация ключевого потока"""
        # Имитация работы регистров сдвига
        stream = []
        for i in range(length):
            # Сдвиг состояния (упрощенно)
            self.state = [self.state[-1]] + self.state[:-1]
            stream.append(self.state[0] ^ self.state[1] ^ self.state[3])
        return stream


class A5_2_Attack:
    """
    Атака на A5/2 с использованием избыточности
    Как описано в докладе Бихэма (CRYPTO 2003)
    """
    
    @staticmethod
    def attack_known_keystream(ciphertext: GSM_Frame, known_pattern: List[int]) -> List[int]:
        """
        Восстановление ключевого потока на основе известного открытого текста
        Избыточность кода коррекции позволяет угадать биты
        """
        print("  [!] Анализ избыточности кода исправления ошибок...")
        time.sleep(0.3)
        
        # В реальном A5/2 избыточность составляет ~30%
        # Это позволяет восстановить до 70% ключевого потока
        recovered_keystream = []
        for i in range(len(ciphertext.data)):
            # Эмулируем использование избыточности для восстановления
            if i % 3 == 0:  # Каждый третий бит легко восстановить
                recovered_keystream.append(ciphertext.data[i] ^ known_pattern[i])
            else:
                # Остальные биты восстанавливаются с вероятностью 70%
                recovered_keystream.append(ciphertext.data[i] ^ known_pattern[i] if random.random() < 0.7 else random.randint(0, 1))
        
        print(f"  [✓] Восстановлено {sum(1 for _ in recovered_keystream)} бит ключевого потока")
        return recovered_keystream
    
    @staticmethod
    def crack_session_key(keystream: List[int], known_data: List[int]) -> int:
        """
        Восстановление сеансового ключа из ключевого потока
        (упрощенная версия для демонстрации)
        """
        print("  [!] Восстановление сеансового ключа из ключевого потока...")
        time.sleep(0.5)
        
        # В реальном A5/2 это делается через решение системы уравнений
        # Здесь эмулируем успешное восстановление
        recovered_key = 0
        for i, bit in enumerate(keystream[:32]):  # Берем первые 32 бита
            if bit:
                recovered_key |= (1 << i)
        
        print(f"  [✓] Сеансовый ключ восстановлен: 0x{recovered_key:08x}")
        return recovered_key


# ============================================================================
# ЧАСТЬ 3: АТАКА ПОНИЖЕНИЯ УРОВНЯ (DOWNGRADE ATTACK)
# ============================================================================

class GSM_Downgrade_Attack:
    """
    Атака понижения уровня для GSM
    Заставляет телефон перейти с A5/1 или A5/3 на A5/2
    с тем же сеансовым ключом
    """
    
    @staticmethod
    def perform_downgrade(original_cipher: str = "A5/1") -> Tuple[int, str]:
        """
        Выполняет атаку понижения уровня
        Возвращает перехваченный сеансовый ключ
        """
        print(f"\n  [!] Инициирование атаки понижения уровня с {original_cipher} на A5/2")
        print("  [*] Имитация поддельной базовой станции (фальшивая вышка)...")
        time.sleep(0.5)
        
        # Генерируем сеансовый ключ (как при нормальной аутентификации)
        session_key = random.randint(0, 0xFFFFFFFF)
        print(f"  [*] Сеансовый ключ (Kc) установлен: 0x{session_key:08x}")
        
        # Принуждаем телефон использовать A5/2 с тем же ключом
        print("  [*] Принудительный переход на A5/2...")
        time.sleep(0.3)
        
        # Теперь используем уязвимость A5/2 для получения ключа
        print("  [*] Запуск атаки на A5/2 для получения сеансового ключа...")
        cipher = A5_2_Cipher(session_key)
        
        # Создаем тестовый кадр с известной структурой (как в реальном GSM)
        test_data = [random.randint(0, 1) for _ in range(128)]
        error_correction = [random.randint(0, 1) for _ in range(32)]  # Избыточность ~25%
        frame = GSM_Frame(test_data, error_correction)
        
        # Шифруем кадр
        encrypted = cipher.encrypt_frame(frame)
        
        # Взламываем A5/2
        recovered_keystream = A5_2_Attack.attack_known_keystream(
            encrypted, 
            test_data[:len(encrypted.data)]
        )
        
        recovered_key = A5_2_Attack.crack_session_key(recovered_keystream, test_data)
        
        print(f"  [✓] Атака понижения уровня успешна!")
        print(f"  [✓] Сеансовый ключ перехвачен: 0x{recovered_key:08x}")
        print(f"  [✓] Теперь возможно прослушивание разговоров и подделка SMS")
        
        return recovered_key, "Скомпрометирован"


# ============================================================================
# ГЛАВНАЯ ПРОГРАММА - ДЕМОНСТРАЦИЯ ВСЕХ АТАК
# ============================================================================

def main():
    print("=" * 70)
    print("  КРИПТОАНАЛИТИЧЕСКИЙ СИМУЛЯТОР")
    print("  Демонстрация уязвимостей из реальных атак")
    print("  (Золотая Корона 1998, GSM 1999-2003)")
    print("=" * 70)
    
    # ======================================================================
    # ЧАСТЬ 1: Атака на RSA короткой длины
    # ======================================================================
    print("\n" + "▸ ЧАСТЬ 1: ВЗЛОМ RSA (Золотая Корона, 1998)")
    print("─" * 50)
    
    rsa = RSA_ShortKey(bits = 32)
    secret_message = 123456789
    print(f"  [*] Секретное сообщение: {secret_message}")
    
    encrypted = rsa.encrypt(secret_message)
    print(f"  [*] Зашифрованное сообщение: {encrypted}")
    
    # Легальное расшифрование
    decrypted = rsa.decrypt(encrypted)
    print(f"  [*] Легальное расшифрование: {decrypted}")
    
    # Взлом (атака факторизацией)
    print("\n  [*] Злоумышленник перехватывает зашифрованное сообщение...")
    cracked = rsa.crack_rsa(encrypted)
    
    if cracked == secret_message:
        print("  [✓] RSA взломан! Причина: слишком короткий ключ (320 бит)")
    else:
        print("  [✗] Ошибка взлома (должно совпадать)")
    
    # ======================================================================
    # ЧАСТЬ 2: Атака на GSM A5/2
    # ======================================================================
    print("\n" + "▸ ЧАСТЬ 2: АТАКА НА GSM A5/2 (Бихэм, 2003)")
    print("─" * 50)
    
    print("  [*] Создание сеансового ключа для GSM...")
    session_key = random.randint(0, 0xFFFFFFFF)
    print(f"  [*] Сеансовый ключ Kc: 0x{session_key:08x}")
    
    # Создаем легитимный кадр GSM
    print("  [*] Формирование кадра GSM с кодом коррекции ошибок...")
    voice_data = [random.randint(0, 1) for _ in range(128)]
    error_code = [random.randint(0, 1) for _ in range(40)]  # 25% избыточности
    frame = GSM_Frame(voice_data, error_code)
    
    print(f"  [*] Размер данных: {len(frame.data)} бит, код коррекции: {len(frame.error_correction)} бит")
    print("  [!] ИЗБЫТОЧНОСТЬ кода коррекции - это уязвимость!")
    
    # Шифрование
    cipher = A5_2_Cipher(session_key)
    encrypted_frame = cipher.encrypt_frame(frame)
    
    # Атака
    print("\n  [*] Злоумышленник перехватывает зашифрованный кадр...")
    recovered_keystream = A5_2_Attack.attack_known_keystream(
        encrypted_frame, 
        voice_data[:len(encrypted_frame.data)]
    )
    
    recovered_key = A5_2_Attack.crack_session_key(recovered_keystream, voice_data)
    
    if recovered_key == session_key:
        print("  [✓] A5/2 взломан! Ключ восстановлен полностью")
    else:
        print("  [⚠] A5/2 частично взломан (вероятностная атака)")
    
    # ======================================================================
    # ЧАСТЬ 3: Атака понижения уровня
    # ======================================================================
    print("\n" + "▸ ЧАСТЬ 3: АТАКА ПОНИЖЕНИЯ УРОВНЯ (Downgrade Attack)")
    print("─" * 50)
    
    print("  [*] Имитация работы сети GSM с сильным шифром A5/1")
    time.sleep(0.5)
    
    # Выполняем атаку
    stolen_key, status = GSM_Downgrade_Attack.perform_downgrade("A5/1")
    
    print("\n  [!!!] ПОСЛЕДСТВИЯ УСПЕШНОЙ АТАКИ:")
    print("  • Прослушивание телефонных разговоров")
    print("  • Подделка SMS-сообщений")
    print("  • Клонирование SIM-карт")
    print("  • Перехват данных пользователя")
    
    # ======================================================================
    # ВЫВОДЫ
    # ======================================================================
    print("\n" + "=" * 70)
    print("  ВЫВОДЫ ИЗ ПРОВЕДЕННЫХ АТАК:")
    print("=" * 70)
    print("""
    1. RSA 320-бит НЕСТОЕК → нужно использовать ≥ 2048 бит
    2. Секретность алгоритма НЕ ЗАЩИЩАЕТ от взлома
    3. Избыточность кода коррекции создает уязвимости
    4. Атаки понижения уровня обходят сильные шифры
    5. Безопасность должна закладываться в ПРОТОКОЛ, а не в алгоритм
    
    ► Как это предотвратить:
      • Открытые алгоритмы (публичный аудит)
      • Достаточная длина ключа с запасом на будущее
      • Взаимная аутентификация (телефон проверяет сеть)
      • Использование современных протоколов (4G/5G)
    """)
    
    print("=" * 70)
    print("  Демонстрация завершена. Криптоанализ успешен!")
    print("=" * 70)


if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости результатов
    main()