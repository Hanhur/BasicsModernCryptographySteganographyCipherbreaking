# 5. Шифр Вернама и гаммирование
import random
import string

# ============================================================
# 1. Шифр Вернама (XOR) для бинарных последовательностей
# ============================================================
def vernam_xor(message_bits: str, key_bits: str) -> str:
    """
    Шифрование/дешифрование Вернама (XOR).
    message_bits и key_bits — бинарные строки из '0' и '1'.
    Длина key_bits должна быть >= длины message_bits.
    """
    if len(key_bits) < len(message_bits):
        raise ValueError("Длина ключа должна быть не меньше длины сообщения")
    # Берём только первые len(message_bits) битов ключа
    key_trimmed = key_bits[:len(message_bits)]
    result = ''.join(str(int(m) ^ int(k)) for m, k in zip(message_bits, key_trimmed))
    return result

def text_to_bits(text: str, encoding='utf-8') -> str:
    """Преобразует текст в бинарную строку."""
    bytes_data = text.encode(encoding)
    return ''.join(f'{byte:08b}' for byte in bytes_data)

def bits_to_text(bits: str, encoding='utf-8') -> str:
    """Преобразует бинарную строку обратно в текст."""
    if len(bits) % 8 != 0:
        raise ValueError("Длина бинарной строки должна быть кратна 8")
    bytes_data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return bytes_data.decode(encoding)

# ============================================================
# 2. Гаммирование по модулю n
# ============================================================
def gamma_mod_n(message: list, key: list, n: int, encrypt: bool = True) -> list:
    """
    Гаммирование по модулю n.
    message и key — списки целых чисел (вычеты по модулю n).
    Если encrypt=True:  c_i = (m_i + k_i) mod n
    Если encrypt=False: m_i = (c_i - k_i) mod n
    """
    if len(key) < len(message):
        raise ValueError("Длина ключа должна быть не меньше длины сообщения")
    key_trimmed = key[:len(message)]
    result = []
    for i, val in enumerate(message):
        if encrypt:
            result.append((val + key_trimmed[i]) % n)
        else:
            result.append((val - key_trimmed[i]) % n)
    return result

def text_to_numbers(text: str, alphabet: str = None) -> list:
    """
    Преобразует текст в числа по алфавиту.
    Если alphabet не задан, использует ASCII коды (0..255).
    """
    if alphabet is None:
        return [ord(ch) for ch in text]  # n = 256
    else:
        return [alphabet.index(ch) for ch in text]

def numbers_to_text(numbers: list, alphabet: str = None) -> str:
    """Преобразует числа обратно в текст."""
    if alphabet is None:
        return ''.join(chr(n) for n in numbers)
    else:
        return ''.join(alphabet[n] for n in numbers)

# ============================================================
# 3. Демонстрация: из текста можно получить ЛЮБОЙ другой текст
# ============================================================
def demonstrate_any_text():
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: ИЗ ТЕКСТА M МОЖНО ПОЛУЧИТЬ ЛЮБОЙ ТЕКСТ C")
    print("=" * 60)
    
    original_text = "Hello"
    desired_text = "World"
    
    print(f"Исходный текст M: {original_text}")
    print(f"Желаемый текст C: {desired_text}")
    
    # Переводим в биты
    m_bits = text_to_bits(original_text)
    c_bits = text_to_bits(desired_text)
    
    # Проверяем, что длины совпадают
    if len(m_bits) != len(c_bits):
        print(f"\nВНИМАНИЕ: Длины сообщений в битах различаются!")
        print(f"Длина M: {len(m_bits)} бит")
        print(f"Длина C: {len(c_bits)} бит")
        print(f"Для демонстрации свойства нужно брать сообщения одинаковой длины в байтах.")
        print(f"Используем сообщения одинаковой длины:")
        
        # Берём сообщения одинаковой длины
        original_text = "Hi!"
        desired_text = "OK!"
        print(f"Исходный текст M: {original_text}")
        print(f"Желаемый текст C: {desired_text}")
        
        m_bits = text_to_bits(original_text)
        c_bits = text_to_bits(desired_text)
    
    # Вычисляем необходимый ключ: K = M XOR C
    key_bits = ''.join(str(int(m) ^ int(c)) for m, c in zip(m_bits, c_bits))
    
    # Шифруем M с этим ключом
    encrypted_bits = vernam_xor(m_bits, key_bits)
    encrypted_text = bits_to_text(encrypted_bits)
    
    print(f"\nM в битах: {m_bits}")
    print(f"C в битах: {c_bits}")
    print(f"Ключ K = M XOR C: {key_bits}")
    print(f"Результат шифрования M XOR K: {encrypted_text}")
    print(f"Совпадает с желаемым C? {encrypted_text == desired_text}")
    
    # Частичная дешифровка не помогает восстановить остаток ключа
    print("\n--- Частичная дешифровка не помогает ---")
    print("(Теоретическое свойство: зная часть ключа, нельзя восстановить остаток)")
    print("Потому что каждый бит ключа независим и случаен.")

# ============================================================
# 4. Простейший генератор гаммы (псевдослучайная последовательность)
#    Линейный конгруэнтный метод — пример к лекциям 13-14
# ============================================================
class GammaGenerator:
    """Генератор псевдослучайной гаммы."""
    def __init__(self, seed: int, a: int = 1664525, c: int = 1013904223, m: int = 2 ** 32):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m
    
    def next_bit(self) -> int:
        """Генерирует следующий бит гаммы."""
        self.state = (self.a * self.state + self.c) % self.m
        return (self.state >> 16) & 1  # берём старший бит
    
    def next_byte(self) -> int:
        """Генерирует следующий байт (0..255) для гаммирования mod 256."""
        self.state = (self.a * self.state + self.c) % self.m
        return self.state % 256
    
    def generate_bits(self, length: int) -> str:
        """Генерирует бинарную строку длины length."""
        return ''.join(str(self.next_bit()) for _ in range(length))
    
    def generate_numbers(self, length: int, mod_n: int) -> list:
        """Генерирует последовательность чисел по модулю mod_n."""
        if mod_n == 2:
            return [self.next_bit() for _ in range(length)]
        else:
            return [self.next_byte() % mod_n for _ in range(length)]

# ============================================================
# 5. Примеры использования
# ============================================================
def example_vernam():
    print("\n" + "=" * 60)
    print("ПРИМЕР 1: ШИФР ВЕРНАМА (XOR) ДЛЯ ТЕКСТА")
    print("=" * 60)
    
    message = "Hello, Vernam!"
    print(f"Сообщение: {message}")
    
    # Генерируем случайный ключ той же длины (в битах)
    message_bits = text_to_bits(message)
    key_bits = ''.join(str(random.randint(0, 1)) for _ in range(len(message_bits)))
    print(f"Длина сообщения: {len(message)} символов")
    print(f"Длина в битах: {len(message_bits)} бит")
    print(f"Длина ключа: {len(key_bits)} бит")
    
    cipher_bits = vernam_xor(message_bits, key_bits)
    decrypted_bits = vernam_xor(cipher_bits, key_bits)
    decrypted_text = bits_to_text(decrypted_bits)
    
    print(f"Зашифровано (первые 64 бита): {cipher_bits[:64]}...")
    print(f"Расшифровано: {decrypted_text}")
    print(f"Успех: {message == decrypted_text}")

def example_gamma_mod_n():
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: ГАММИРОВАНИЕ ПО МОДУЛЮ 256 (ASCII)")
    print("=" * 60)
    
    message = "Gamma cipher example."
    print(f"Сообщение: {message}")
    
    # Переводим в числа (ASCII коды)
    m_numbers = text_to_numbers(message)  # n=256
    print(f"Числовое представление (первые 10): {m_numbers[:10]}...")
    
    # Генерируем гамму тем же генератором
    seed = 12345
    gamma_gen = GammaGenerator(seed)
    key_numbers = gamma_gen.generate_numbers(len(m_numbers), mod_n = 256)
    
    # Шифрование
    c_numbers = gamma_mod_n(m_numbers, key_numbers, n = 256, encrypt = True)
    cipher_text = numbers_to_text(c_numbers)
    print(f"Зашифрованный текст (нечитаемый): {repr(cipher_text)}")
    
    # Дешифрование
    decrypted_numbers = gamma_mod_n(c_numbers, key_numbers, n = 256, encrypt = False)
    decrypted_text = numbers_to_text(decrypted_numbers)
    print(f"Расшифрованный текст: {decrypted_text}")
    print(f"Успех: {message == decrypted_text}")

def example_vernam_number():
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: ШИФР ВЕРНАМА КАК ЧАСТНЫЙ СЛУЧАЙ (n=2)")
    print("=" * 60)
    
    # Бинарное сообщение
    m_bits = "10110011"
    k_bits = "01101010"
    print(f"Сообщение: {m_bits}")
    print(f"Ключ:     {k_bits}")
    
    c_bits = vernam_xor(m_bits, k_bits)
    m_restored = vernam_xor(c_bits, k_bits)
    
    print(f"Шифротекст: {c_bits}")
    print(f"Восстановлено: {m_restored}")
    print(f"Формула (5.1): ci = mi XOR ki")
    
    # То же через gamma_mod_n с n=2
    m_list = [int(b) for b in m_bits]
    k_list = [int(b) for b in k_bits]
    c_list = gamma_mod_n(m_list, k_list, n = 2, encrypt = True)
    print(f"gamma_mod_n c n=2: {c_list} → {''.join(map(str, c_list))}")

def example_different_lengths():
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: РАЗНАЯ ДЛИНА СООБЩЕНИЙ (КЛЮЧ МОЖЕТ БЫТЬ ДЛИННЕЕ)")
    print("=" * 60)
    
    message = "Hi"
    print(f"Сообщение: {message}")
    
    # Ключ длиннее сообщения
    message_bits = text_to_bits(message)
    longer_key_bits = text_to_bits("This is a much longer key!!!")
    
    print(f"Длина сообщения в битах: {len(message_bits)}")
    print(f"Длина ключа в битах: {len(longer_key_bits)}")
    
    cipher_bits = vernam_xor(message_bits, longer_key_bits)
    decrypted_bits = vernam_xor(cipher_bits, longer_key_bits)
    decrypted_text = bits_to_text(decrypted_bits)
    
    print(f"Расшифровано: {decrypted_text}")
    print(f"Успех: {message == decrypted_text}")

# ============================================================
# 6. Запуск
# ============================================================
if __name__ == "__main__":
    random.seed(42)  # для воспроизводимости случайного ключа
    
    example_vernam()
    example_gamma_mod_n()
    example_vernam_number()
    example_different_lengths()
    demonstrate_any_text()
    
    print("\n" + "=" * 60)
    print("ПРИМЕЧАНИЕ:")
    print("- Для абсолютной стойкости ключ должен быть истинно случайным и одноразовым.")
    print("- Генератор гаммы в примере — псевдослучайный (не подходит для одноразового блокнота).")
    print("- В реальных системах гаммирования используют криптостойкие генераторы (LFSR, и т.п.)")
    print("- Свойство 'любой текст той же длины' выполняется ТОЛЬКО при одинаковой длине")
    print("  сообщений в байтах (а значит, и в битах).")
    print("=" * 60)