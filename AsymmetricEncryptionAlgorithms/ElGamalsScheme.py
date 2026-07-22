# Схема Эль-Гамаля
"""
Схема Эль-Гамаля — реализация на чистом Python
Основано на тексте из описания алгоритма
"""

import random
import math

# ==============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================

def is_prime(n):
    """Проверка числа на простоту (детерминированная для малых чисел)"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Проверка делителей до sqrt(n)
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def find_primitive_root(p):
    """
    Находит первообразный корень (образующий элемент) по модулю p
    Для простого числа p
    """
    if p == 2:
        return 1
    
    # Разлагаем p-1 на простые множители
    factors = []
    phi = p - 1
    n = phi
    
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
        i += 1 if i == 2 else 2
    
    if n > 1:
        factors.append(n)
    
    # Проверяем кандидатов
    for g in range(2, p):
        is_primitive = True
        for factor in factors:
            if pow(g, phi // factor, p) == 1:
                is_primitive = False
                break
        if is_primitive:
            return g
    
    return None

def modinv(a, p):
    """
    Находит обратное число по модулю p (a ^ (-1) mod p)
    Используем расширенный алгоритм Евклида
    """
    # Расширенный алгоритм Евклида
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    
    g, x, y = egcd(a, p)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {p} не существует")
    else:
        return x % p

def generate_large_prime(bits = 18):
    """
    Генерирует простое число заданной битности
    Для примера используем 18 бит (числа ~200 000)
    """
    while True:
        # Генерируем нечетное число
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # Устанавливаем старший и младший биты
        
        if is_prime(n):
            return n

# ==============================================
# ОСНОВНАЯ РЕАЛИЗАЦИЯ СХЕМЫ ЭЛЬ-ГАМАЛЯ
# ==============================================

class ElGamal:
    """
    Класс для работы со схемой Эль-Гамаля
    """
    
    def __init__(self, p = None, g = None):
        """
        Инициализация с параметрами p (простое число) и g (образующий элемент)
        Если параметры не указаны, генерируются автоматически
        """
        if p is None:
            # Генерируем простое число p
            print("Генерация простого числа p...")
            self.p = generate_large_prime(18)  # 18 бит ~ 200 000
            print(f"p = {self.p}")
        else:
            self.p = p
        
        if g is None:
            # Находим первообразный корень
            print("Поиск первообразного корня g...")
            self.g = find_primitive_root(self.p)
            if self.g is None:
                raise ValueError(f"Не удалось найти первообразный корень для p = {self.p}")
            print(f"g = {self.g}")
        else:
            self.g = g
    
    def generate_keypair(self, private_key = None):
        """
        Генерирует пару ключей:
        - private_key: закрытый ключ (если не указан, генерируется случайно)
        - public_key: открытый ключ = g ^ private_key mod p
        """
        if private_key is None:
            private_key = random.randint(2, self.p - 2)
        
        public_key = pow(self.g, private_key, self.p)
        
        return {
            'private': private_key,
            'public': public_key
        }
    
    def encrypt(self, message, recipient_public_key, k = None):
        """
        Шифрование сообщения M для получателя с открытым ключом recipient_public_key
        
        Возвращает: (y1, y2) — кортеж из двух чисел
        y1 = g ^ k mod p
        y2 = M * (recipient_public_key) ^ k mod p
        """
        if message >= self.p:
            raise ValueError(f"Сообщение M = {message} должно быть меньше p = {self.p}")
        
        # Выбираем случайное k (1 < k < p-1)
        if k is None:
            k = random.randint(2, self.p - 2)
        
        # Вычисляем y1 = g^k mod p
        y1 = pow(self.g, k, self.p)
        
        # Вычисляем общий секрет: (public_key)^k mod p
        shared_secret = pow(recipient_public_key, k, self.p)
        
        # Вычисляем y2 = M * shared_secret mod p
        y2 = (message * shared_secret) % self.p
        
        return {
            'y1': y1,
            'y2': y2,
            'k': k  # Сохраняем для демонстрации (в реальности k держится в секрете)
        }
    
    def decrypt(self, ciphertext, private_key):
        """
        Расшифровка сообщения из пары (y1, y2)
        private_key — закрытый ключ получателя b
        
        M = y2 * (y1 ^ b) ^ (-1) mod p
        """
        y1 = ciphertext['y1']
        y2 = ciphertext['y2']
        
        # Вычисляем общий секрет: K = y1^b mod p
        shared_secret = pow(y1, private_key, self.p)
        
        # Находим обратное значение: K^(-1) mod p
        inv_shared_secret = modinv(shared_secret, self.p)
        
        # Расшифровываем: M = y2 * K^(-1) mod p
        message = (y2 * inv_shared_secret) % self.p
        
        return message

# ==============================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ (С РАЗБОРОМ ПО ШАГАМ)
# ==============================================

def demonstrate_elgamal():
    """
    Демонстрация работы схемы Эль-Гамаля
    Следуем примеру из текста
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ СХЕМЫ ЭЛЬ-ГАМАЛЯ")
    print("=" * 60)
    
    # --- ШАГ 1: Открытые параметры ---
    print("\n[1] ОТКРЫТЫЕ ПАРАМЕТРЫ:")
    print("    Выбираем большое простое число p и образующий элемент g")
    
    p = 200003
    g = 7
    print(f"    p = {p}")
    print(f"    g = {g}")
    
    # Создаем экземпляр схемы Эль-Гамаля
    elgamal = ElGamal(p = p, g = g)
    
    # --- ШАГ 2: Генерация ключей Боба ---
    print("\n[2] ГЕНЕРАЦИЯ КЛЮЧЕЙ БОБА (ПОЛУЧАТЕЛЬ):")
    print("    Боб выбирает закрытый ключ b и вычисляет открытый ключ B = g ^ b mod p")
    
    b = 2367  # Закрытый ключ Боба
    print(f"    Закрытый ключ Боба: b = {b}")
    
    # Генерируем ключевую пару Боба
    bob_keys = elgamal.generate_keypair(private_key = b)
    print(f"    Открытый ключ Боба: B = {bob_keys['public']}")
    
    # --- ШАГ 3: Шифрование Алисы ---
    print("\n[3] ШИФРОВАНИЕ АЛИСЫ (ОТПРАВИТЕЛЬ):")
    print("    Алиса выбирает случайное k, создает сообщение M")
    print("    и вычисляет y1 = g ^ k mod p и y2 = M * B ^ k mod p")
    
    M = 88  # Секретное сообщение
    k = 23  # Случайное число Алисы
    print(f"    Сообщение: M = {M}")
    print(f"    Случайное число Алисы: k = {k}")
    
    # Шифруем
    ciphertext = elgamal.encrypt(
        message = M, 
        recipient_public_key = bob_keys['public'],
        k = k
    )
    
    y1 = ciphertext['y1']
    y2 = ciphertext['y2']
    print(f"    y1 = {y1}")
    print(f"    y2 = {y2}")
    
    # --- ШАГ 4: Расшифровка Боба ---
    print("\n[4] РАСШИФРОВКА БОБА (ПОЛУЧАТЕЛЬ):")
    print("    Боб вычисляет общий секрет K = y1 ^ b mod p")
    print("    и использует обратное значение для расшифровки")
    
    # Расшифровываем
    decrypted = elgamal.decrypt(ciphertext, bob_keys['private'])
    print(f"    Расшифрованное сообщение: M = {decrypted}")
    
    # --- Проверка ---
    print("\n[5] ПРОВЕРКА:")
    if decrypted == M:
        print("    ✓ Шифрование и расшифровка выполнены успешно!")
    else:
        print("    ✗ Ошибка! Сообщения не совпадают.")
    
    # --- Детальный разбор расшифровки (как в тексте) ---
    print("\n[6] ДЕТАЛЬНЫЙ РАЗБОР РАСШИФРОВКИ:")
    K = pow(y1, b, p)
    print(f"    K = y1 ^ {b} mod {p} = {K}")
    
    inv_K = modinv(K, p)
    print(f"    INV(K) = {inv_K}")
    
    result = (y2 * inv_K) % p
    print(f"    M = y2 * INV(K) mod {p} = {result}")
    print(f"    Результат: {result} == {M}")

# ==============================================
# ДОПОЛНИТЕЛЬНЫЙ ТЕСТ С РАЗНЫМИ ЗНАЧЕНИЯМИ
# ==============================================

def test_random_messages():
    """
    Тестируем схему на случайных сообщениях
    """
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ НА СЛУЧАЙНЫХ СООБЩЕНИЯХ")
    print("=" * 60)
    
    # Генерируем параметры
    print("\nГенерация параметров...")
    elgamal = ElGamal()  # Автоматическая генерация p и g
    
    # Генерируем ключи Боба
    print("\nГенерация ключей Боба...")
    bob_keys = elgamal.generate_keypair()
    print(f"    Закрытый ключ: {bob_keys['private']}")
    print(f"    Открытый ключ:  {bob_keys['public']}")
    
    # Шифруем несколько случайных сообщений
    print("\nШифрование и расшифровка случайных сообщений:")
    success_count = 0
    test_count = 5
    
    for i in range(test_count):
        # Случайное сообщение (меньше p)
        M = random.randint(1, elgamal.p - 2)
        
        # Шифруем
        ciphertext = elgamal.encrypt(M, bob_keys['public'])
        
        # Расшифровываем
        decrypted = elgamal.decrypt(ciphertext, bob_keys['private'])
        
        # Проверяем
        if decrypted == M:
            success_count += 1
            print(f"    ✓ Тест {i + 1}: M = {M} -> расшифровано = {decrypted}")
        else:
            print(f"    ✗ Тест {i + 1}: M = {M} -> расшифровано = {decrypted} (ошибка!)")
    
    print(f"\nРезультат: {success_count}/{test_count} тестов пройдено успешно")

# ==============================================
# ФУНКЦИЯ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЬСКИМ ВВОДОМ
# ==============================================

def interactive_demo():
    """
    Интерактивная демонстрация с пользовательским вводом
    """
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    
    try:
        # Параметры по умолчанию
        p = 200003
        g = 7
        
        elgamal = ElGamal(p, g)
        
        # Генерация ключей получателя
        print("\nВведите закрытый ключ получателя (или нажмите Enter для случайного):")
        private_input = input("> ").strip()
        
        if private_input == "":
            bob_keys = elgamal.generate_keypair()
        else:
            bob_keys = elgamal.generate_keypair(int(private_input))
        
        print(f"Открытый ключ получателя: {bob_keys['public']}")
        
        # Ввод сообщения
        print(f"\nВведите сообщение для шифрования (число от 1 до {p - 2}):")
        msg_input = input("> ").strip()
        M = int(msg_input)
        
        if M >= p:
            print(f"Ошибка: сообщение должно быть меньше {p}")
            return
        
        # Ввод k (опционально)
        print("\nВведите случайное число k (или нажмите Enter для автоматического):")
        k_input = input("> ").strip()
        
        if k_input == "":
            ciphertext = elgamal.encrypt(M, bob_keys['public'])
        else:
            ciphertext = elgamal.encrypt(M, bob_keys['public'], int(k_input))
        
        print(f"\nЗашифрованное сообщение:")
        print(f"  y1 = {ciphertext['y1']}")
        print(f"  y2 = {ciphertext['y2']}")
        
        # Расшифровка
        decrypted = elgamal.decrypt(ciphertext, bob_keys['private'])
        print(f"\nРасшифрованное сообщение: {decrypted}")
        
        if decrypted == M:
            print("✓ Успешно!")
        else:
            print("✗ Ошибка!")
            
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

# ==============================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# ==============================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости результатов
    random.seed(42)
    
    # Демонстрация на примере из текста
    demonstrate_elgamal()
    
    # Дополнительное тестирование
    test_random_messages()
    
    # Интерактивный режим (раскомментируйте, если хотите)
    # interactive_demo()
    
    print("\n" + "=" * 60)
    print("ПРОГРАММА ЗАВЕРШЕНА")
    print("=" * 60)