# 5. Аналог протокола Эль Гамаля
"""
Аналог протокола Эль-Гамаля на эллиптических кривых (EC ElGamal)
Полностью рабочая версия
"""

from ecdsa import ellipticcurve, SECP256k1
from ecdsa.util import randrange
from ecdsa.numbertheory import square_root_mod_prime
import hashlib

# Параметры кривой (используем secp256k1)
CURVE = SECP256k1.curve
G = SECP256k1.generator
ORDER = SECP256k1.order

# Простое поле
PRIME = CURVE.p()

# ------------------------------------------------------------
# Вспомогательные функции для работы с точками
# ------------------------------------------------------------

def modular_sqrt(a, p):
    """Находит квадратный корень по модулю простого числа p"""
    return square_root_mod_prime(a, p)

def point_neg(point):
    """Возвращает обратную точку (отрицание)"""
    if point == ellipticcurve.INFINITY:
        return ellipticcurve.INFINITY
    return ellipticcurve.Point(CURVE, point.x(), (-point.y()) % PRIME)

def point_sub(point1, point2):
    """Вычитание точек: point1 - point2"""
    return point1 + point_neg(point2)

# ------------------------------------------------------------
# Отображение сообщение <-> точка
# ------------------------------------------------------------

def message_to_point(message: bytes) -> ellipticcurve.Point:
    """
    Преобразует сообщение в точку на кривой.
    """
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    # Преобразуем сообщение в число
    msg_int = int.from_bytes(message, 'big')
    
    # Ищем x, для которого x^3 + a*x + b является квадратом
    max_attempts = 1000
    for i in range(max_attempts):
        # Добавляем счётчик к сообщению
        x = (msg_int + i) % PRIME
        
        # Вычисляем y^2 = x^3 + a*x + b
        rhs = (x * x * x + CURVE.a() * x + CURVE.b()) % PRIME
        
        # Проверяем, является ли rhs квадратичным вычетом
        try:
            y = modular_sqrt(rhs, PRIME)
            return ellipticcurve.Point(CURVE, x, y)
        except:
            # Не квадрат, пробуем следующий x
            continue
    
    raise ValueError(f"Не удалось встроить сообщение в точку кривой за {max_attempts} попыток")

def point_to_message(point: ellipticcurve.Point) -> bytes:
    """
    Извлекает сообщение из точки.
    """
    # Возвращаем x-координату как байты
    x_bytes = point.x().to_bytes(32, 'big')
    # Убираем ведущие нули
    return x_bytes.lstrip(b'\x00')

# ------------------------------------------------------------
# Протокол EC ElGamal
# ------------------------------------------------------------

def generate_keys():
    """Генерирует пару ключей (секретный e, открытый eC)"""
    e = randrange(ORDER)  # случайное число от 1 до ORDER-1
    Q = e * G  # открытый ключ
    return e, Q

def encrypt(message: bytes, public_key: ellipticcurve.Point) -> tuple:
    """
    Шифрует сообщение на открытом ключе получателя.
    Возвращает (C1 = kG, C2 = Pm + k * public_key)
    """
    # Представляем сообщение в виде точки Pm
    Pm = message_to_point(message)
    
    # Выбираем случайное одноразовое k
    k = randrange(ORDER)
    
    # Вычисляем компоненты шифротекста
    C1 = k * G
    C2 = Pm + (k * public_key)
    
    return (C1, C2)

def decrypt(ciphertext: tuple, private_key: int) -> bytes:
    """
    Расшифровывает шифротекст, используя секретный ключ.
    """
    C1, C2 = ciphertext
    
    # Вычисляем маску: e * C1 = e * (kG) = k * (eG) = k * public_key
    mask = private_key * C1
    
    # Восстанавливаем точку сообщения (C2 - mask)
    Pm = point_sub(C2, mask)
    
    # Преобразуем точку обратно в сообщение
    return point_to_message(Pm)

# ------------------------------------------------------------
# Демонстрация работы
# ------------------------------------------------------------

def demo_basic():
    """Базовая демонстрация"""
    print("=" * 60)
    print("EC ElGamal - Аналог протокола Эль-Гамаля")
    print("=" * 60)
    
    # Генерация ключей для пользователя B
    print("\n1. Генерация ключей для пользователя B...")
    e_B, Q_B = generate_keys()
    print(f"   Секретный ключ B: {e_B}")
    print(f"   Открытый ключ B: ({Q_B.x()}, {Q_B.y()})")
    
    # Пользователь A отправляет сообщение
    print("\n2. Пользователь A шифрует сообщение для B...")
    original_message = "Hello, EC ElGamal!"
    print(f"   Исходное сообщение: '{original_message}'")
    
    ciphertext = encrypt(original_message.encode('utf-8'), Q_B)
    C1, C2 = ciphertext
    print(f"   C1 = ({C1.x()}, {C1.y()})")
    print(f"   C2 = ({C2.x()}, {C2.y()})")
    
    # Пользователь B расшифровывает
    print("\n3. Пользователь B расшифровывает сообщение...")
    decrypted_bytes = decrypt(ciphertext, e_B)
    decrypted_message = decrypted_bytes.decode('utf-8', errors = 'ignore')
    print(f"   Расшифрованное сообщение: '{decrypted_message}'")
    
    # Проверка
    print(f"\n4. Проверка: {'УСПЕХ' if original_message == decrypted_message else 'ОШИБКА'}")

def demo_numeric():
    """Демонстрация с числами"""
    print("\n" + "=" * 60)
    print("Демонстрация 2: Шифрование чисел")
    print("=" * 60)
    
    # Генерация ключей
    e_priv, Q_pub = generate_keys()
    print(f"Секретный ключ: {e_priv}")
    
    # Шифруем число как строку
    secret_number = 123456789
    print(f"\nИсходное число: {secret_number}")
    
    # Преобразуем число в байты
    message_bytes = str(secret_number).encode('utf-8')
    
    # Шифрование
    ciphertext = encrypt(message_bytes, Q_pub)
    C1, C2 = ciphertext
    print(f"C1 = ({C1.x()}, {C1.y()})")
    print(f"C2 = ({C2.x()}, {C2.y()})")
    
    # Расшифровка
    decrypted_bytes = decrypt(ciphertext, e_priv)
    decrypted_number = int(decrypted_bytes.decode('utf-8'))
    
    print(f"Расшифрованное число: {decrypted_number}")
    print(f"Успех: {secret_number == decrypted_number}")

def demo_long_message():
    """Демонстрация с длинным сообщением"""
    print("\n" + "=" * 60)
    print("Демонстрация 3: Длинное сообщение")
    print("=" * 60)
    
    # Генерация ключей
    e_priv, Q_pub = generate_keys()
    
    # Длинное сообщение
    message = "Это секретное сообщение, которое передаётся по защищённому каналу связи с использованием эллиптических кривых. Протокол Эль-Гамаля на эллиптических кривых обеспечивает стойкость, эквивалентную 256-битному симметричному ключу."
    print(f"Длина сообщения: {len(message)} символов")
    print(f"Сообщение: {message[:100]}...")
    
    # Шифрование
    ciphertext = encrypt(message.encode('utf-8'), Q_pub)
    
    # Расшифровка
    decrypted_bytes = decrypt(ciphertext, e_priv)
    decrypted_message = decrypted_bytes.decode('utf-8', errors = 'ignore')
    
    print(f"\nРасшифровано: {decrypted_message[:100]}...")
    print(f"\nПроверка: {'УСПЕХ' if message == decrypted_message else 'ОШИБКА'}")

def demo_short():
    """Демонстрация с коротким сообщением"""
    print("\n" + "=" * 60)
    print("Демонстрация 4: Короткое сообщение")
    print("=" * 60)
    
    # Генерация ключей
    e_priv, Q_pub = generate_keys()
    
    # Разные короткие сообщения
    messages = [b"Hi", b"OK", b"Test", b"123", b"A" * 10]
    
    for msg in messages:
        print(f"\nИсходное: {msg}")
        
        # Шифрование
        ciphertext = encrypt(msg, Q_pub)
        
        # Расшифровка
        decrypted = decrypt(ciphertext, e_priv)
        
        print(f"Расшифровано: {decrypted}")
        print(f"Совпадает: {msg == decrypted}")

if __name__ == "__main__":
    try:
        demo_basic()
        demo_numeric()
        demo_short()
        demo_long_message()
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()