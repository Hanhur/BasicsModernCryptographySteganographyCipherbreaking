# Построение криптосистем
import hashlib
import random
import secrets
from ecdsa import ellipticcurve, numbertheory
from ecdsa.curves import SECP256k1

# Используем стандартную кривую SECP256k1
# Параметры: p, a, b, G (базовая точка), q (порядок точки)
CURVE = SECP256k1
G = CURVE.generator
q = CURVE.order  # простое число, порядок точки G

def int_to_bytes(n, length = None):
    """Преобразует целое число в байты."""
    if length is None:
        length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, 'big')

def bytes_to_int(b):
    """Преобразует байты в целое число."""
    return int.from_bytes(b, 'big')

def hash_message(message):
    """Вычисляет хеш сообщения (SHA-256) и возвращает целое число по модулю q."""
    if isinstance(message, str):
        message = message.encode('utf-8')
    h = hashlib.sha256(message).digest()
    return bytes_to_int(h) % q

def randrange_custom(start, stop):
    """
    Безопасная генерация случайного числа в диапазоне [start, stop).
    Использует secrets для криптостойкости.
    """
    if start >= stop:
        raise ValueError("start must be less than stop")
    range_size = stop - start
    # Определяем количество бит, необходимое для представления range_size
    bit_length = range_size.bit_length()
    while True:
        # Генерируем случайное число с нужным количеством бит
        random_bytes = secrets.token_bytes((bit_length + 7) // 8)
        candidate = int.from_bytes(random_bytes, 'big')
        # Обрезаем до нужного количества бит
        candidate = candidate & ((1 << bit_length) - 1)
        if candidate < range_size:
            return start + candidate

# ============================================================
# 1. ШИФР ЭЛЬ-ГАМАЛЯ НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ
# ============================================================

class ElGamalECC:
    """
    Шифр Эль-Гамаля на эллиптической кривой.
    """
    def __init__(self, curve = CURVE, generator = G):
        self.curve = curve
        self.G = generator
        self.q = curve.order

    def generate_keypair(self):
        """
        Генерирует пару ключей:
        - секретный ключ c (0 < c < q)
        - открытый ключ D = [c]G (точка на кривой)
        """
        c = randrange_custom(1, self.q)  # случайное число от 1 до q-1
        D = c * self.G            # умножение точки на скаляр
        return c, D

    def encrypt(self, message_int, public_key_B):
        """
        Шифрует сообщение (целое число < p) для пользователя B.
        Возвращает (R, e), где R - точка, e - число.
        """
        p = self.curve.curve.p()
        if not (0 < message_int < p):
            raise ValueError(f"Сообщение должно быть целым числом в диапазоне (0, {p})")

        # 1. Случайное k
        k = randrange_custom(1, self.q)

        # 2. R = [k]G
        R = k * self.G

        # 3. P = [k]D_B = (x, y)
        P = k * public_key_B
        x = P.x()

        # Если x == 0, шифрование не удастся (нет обратного)
        if x == 0:
            # В реальных системах перезапускают с новым k
            raise ValueError("Абсцисса x == 0, выберите другое k")

        # 4. e = m * x mod p
        e = (message_int * x) % p

        return R, e

    def decrypt(self, R, e, private_key_B):
        """
        Расшифровывает сообщение (R, e) с помощью секретного ключа B.
        Возвращает исходное целое число m.
        """
        # 1. Q = [c_B]R = (x, y)
        Q = private_key_B * R
        x = Q.x()

        p = self.curve.curve.p()

        # 2. m' = e * x^{-1} mod p
        x_inv = numbertheory.inverse_mod(x, p)
        m = (e * x_inv) % p
        return m


# ============================================================
# 2. ЦИФРОВАЯ ПОДПИСЬ (ВАРИАНТ ИЗ ТЕКСТА)
# ============================================================

class DigitalSignatureECC:
    """
    Цифровая подпись на эллиптической кривой по схеме из текста:
    s = (k * h + r * xA) mod q
    Проверка: u1 = s * h ^ {-1} mod q, u2 = -r * h ^ {-1} mod q
    """
    def __init__(self, curve = CURVE, generator = G):
        self.curve = curve
        self.G = generator
        self.q = curve.order

    def generate_keypair(self):
        """Генерирует пару ключей: (секретный x, открытый Y = [x]G)."""
        x = randrange_custom(1, self.q)
        Y = x * self.G
        return x, Y

    def sign(self, message, private_key_A):
        """
        Подписывает сообщение.
        Возвращает (r, s).
        """
        h = hash_message(message)

        while True:
            # 2. Случайное k
            k = randrange_custom(1, self.q)

            # 3. P = [k]G = (x, y)
            P = k * self.G
            r = P.x() % self.q

            if r == 0:
                continue  # шаг 4: при r=0 возвращаемся к шагу 2

            # 5. s = (k*h + r*xA) mod q
            s = (k * h + r * private_key_A) % self.q

            if s == 0:
                continue  # шаг 5: при s=0 возвращаемся к шагу 2

            return r, s

    def verify(self, message, r, s, public_key_A):
        """
        Проверяет подпись (r, s) для сообщения.
        Возвращает True, если подпись верна.
        """
        # 1. Проверка диапазона
        if not (0 < r < self.q and 0 < s < self.q):
            return False

        # 2. Хеш сообщения
        h = hash_message(message)

        # 3. u1 = s * h^{-1} mod q, u2 = -r * h^{-1} mod q
        try:
            h_inv = numbertheory.inverse_mod(h, self.q)
        except ZeroDivisionError:
            # Если h == 0 (маловероятно), считаем подпись недействительной
            return False
            
        u1 = (s * h_inv) % self.q
        u2 = (-r * h_inv) % self.q

        # 4. P = [u1]G + [u2]Y_A
        P = u1 * self.G + u2 * public_key_A

        if P == ellipticcurve.INFINITY:
            return False  # отвергаем подпись

        # 5. Проверка абсциссы
        x = P.x() % self.q
        return x == r


# ============================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ============================================================

def demo_elgamal():
    print("\n" + "=" * 50)
    print("1. ШИФР ЭЛЬ-ГАМАЛЯ НА ЭЛЛИПТИЧЕСКОЙ КРИВОЙ")
    print("=" * 50)

    elgamal = ElGamalECC()

    # Генерация ключей пользователя B
    print("\nГенерация ключей пользователя B...")
    cB, DB = elgamal.generate_keypair()
    print(f"Секретный ключ B (cB): {cB}")
    print(f"Открытый ключ B (DB): ({DB.x()}, {DB.y()})")

    # Сообщение (число меньше p)
    p = elgamal.curve.curve.p()
    message = 123456789
    print(f"\nИсходное сообщение (m): {message}")

    # Шифрование (пользователь A отправляет B)
    print("\nШифрование (A -> B)...")
    R, e = elgamal.encrypt(message, DB)
    print(f"R = ({R.x()}, {R.y()})")
    print(f"e = {e}")

    # Дешифрование (пользователь B)
    print("\nДешифрование (B)...")
    decrypted = elgamal.decrypt(R, e, cB)
    print(f"Расшифрованное сообщение (m'): {decrypted}")

    assert message == decrypted, "Ошибка: сообщения не совпадают!"
    print("\n✅ Шифрование/дешифрование прошло успешно!")


def demo_signature():
    print("\n" + "=" * 50)
    print("2. ЦИФРОВАЯ ПОДПИСЬ (ВАРИАНТ ИЗ ТЕКСТА)")
    print("=" * 50)

    sig = DigitalSignatureECC()

    # Генерация ключей пользователя A
    print("\nГенерация ключей пользователя A...")
    xA, YA = sig.generate_keypair()
    print(f"Секретный ключ A (xA): {xA}")
    print(f"Открытый ключ A (YA): ({YA.x()}, {YA.y()})")

    # Сообщение
    message = "Важное сообщение для подписи"
    print(f"\nСообщение: '{message}'")

    # Подпись
    print("\nПодписание сообщения...")
    r, s = sig.sign(message, xA)
    print(f"Подпись: r = {r}")
    print(f"          s = {s}")

    # Проверка подписи
    print("\nПроверка подписи...")
    is_valid = sig.verify(message, r, s, YA)
    print(f"Результат проверки: {'✅ Подпись верна' if is_valid else '❌ Подпись неверна'}")

    # Демонстрация: изменение сообщения
    print("\nПроверка с изменённым сообщением...")
    tampered_message = "Важное сообщение для подписи (изменено)"
    is_valid_tampered = sig.verify(tampered_message, r, s, YA)
    print(f"Результат проверки: {'✅ Подпись верна' if is_valid_tampered else '❌ Подпись неверна (ожидаемо)'}")

    # Демонстрация: изменение подписи
    print("\nПроверка с изменённой подписью...")
    r_tampered = (r + 1) % q
    is_valid_r_tampered = sig.verify(message, r_tampered, s, YA)
    print(f"Результат проверки с изменённым r: {'✅ Подпись верна' if is_valid_r_tampered else '❌ Подпись неверна (ожидаемо)'}")

    assert is_valid, "Ошибка: подпись должна быть верной!"
    assert not is_valid_tampered, "Ошибка: подпись не должна быть верной для изменённого сообщения!"
    assert not is_valid_r_tampered, "Ошибка: подпись не должна быть верной с изменённым r!"
    print("\n✅ Все проверки подписи пройдены!")


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости (опционально)
    # random.seed(42)  # Раскомментируйте для отладки
    
    demo_elgamal()
    demo_signature()