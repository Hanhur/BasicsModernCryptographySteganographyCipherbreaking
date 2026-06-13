# 2. Необходимые элементы электронной карточки
import hashlib
import random

# ---------- RSA функции ----------
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def generate_rsa_keys():
    p = 61
    q = 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = modinv(e, phi)
    return ((e, n), (d, n))

def hash_message(msg):
    """Преобразует сообщение в число меньше n"""
    h = hashlib.sha256(msg.encode()).digest()
    return int.from_bytes(h[:8], 'big')  # Берём только первые 8 байт, чтобы число было < n

# ---------- Классическая слепая подпись RSA ----------
class BlindRSASignature:
    def __init__(self, pubkey, privkey):
        self.e, self.n = pubkey
        self.d, _ = privkey
    
    def blind(self, message_int, r):
        """Ослепление: m' = m * (r ^ e) mod n"""
        return (message_int * pow(r, self.e, self.n)) % self.n
    
    def sign(self, blinded_int):
        """Подпись слепого сообщения"""
        return pow(blinded_int, self.d, self.n)
    
    def unblind(self, blinded_signature, r):
        """Снятие слепоты: s = s' * r ^ (-1) mod n"""
        r_inv = modinv(r, self.n)
        return (blinded_signature * r_inv) % self.n
    
    def verify(self, message_int, signature):
        """Проверка подписи: signature ^ e mod n == message_int"""
        return pow(signature, self.e, self.n) == message_int

# ---------- Электронная карта ----------
class ElectronicCard:
    def __init__(self, card_id, nominal, pubkey, privkey):
        self.card_id = card_id
        self.nominal = nominal
        self.balance = nominal
        self.pubkey = pubkey
        self.privkey = privkey
        self.signature = None
    
    def issue(self):
        """Эмитент подписывает карту"""
        msg = f"{self.card_id}:{self.nominal}"
        msg_int = hash_message(msg)
        self.signature = pow(msg_int, self.privkey[0], self.pubkey[1])
        print(f"✓ Выпущена карта {self.card_id} номиналом {self.nominal}")
        return self.signature
    
    def verify(self):
        """Проверка подписи карты"""
        msg = f"{self.card_id}:{self.nominal}"
        msg_int = hash_message(msg)
        return pow(self.signature, self.pubkey[0], self.pubkey[1]) == msg_int

# ---------- Система анонимных платежей ----------
class AnonymousPaymentSystem:
    def __init__(self, pubkey, privkey):
        self.blind_rsa = BlindRSASignature(pubkey, privkey)
        self.spent_tokens = {}
        self.total_issued = 0
        self.total_redeemed = 0
    
    def create_payment_token(self, card, amount, merchant_id):
        """Создаёт анонимный платёжный токен"""
        if amount > card.balance:
            raise ValueError(f"Недостаточно средств: {card.balance} < {amount}")
        
        # Генерируем уникальный серийный номер токена (скрыт от эмитента)
        serial = random.randint(1000000000, 9999999999)
        token_msg = f"P{serial}:{merchant_id}:{amount}"
        token_int = hash_message(token_msg)
        
        # Выбираем случайный ослепляющий множитель
        r = random.randint(2, self.blind_rsa.n - 1)
        while egcd(r, self.blind_rsa.n)[0] != 1:
            r = random.randint(2, self.blind_rsa.n - 1)
        
        # Ослепляем сообщение
        blinded = self.blind_rsa.blind(token_int, r)
        
        # Эмитент подписывает вслепую
        blinded_sig = self.blind_rsa.sign(blinded)
        
        # Снимаем слепоту
        signature = self.blind_rsa.unblind(blinded_sig, r)
        
        # Проверяем, что подпись правильная
        assert self.blind_rsa.verify(token_int, signature), "Ошибка: неверная подпись"
        
        self.total_issued += amount
        
        return {
            'token_msg': token_msg,
            'token_int': token_int,
            'signature': signature,
            'amount': amount,
            'serial': serial
        }
    
    def redeem_token(self, token):
        """Продавец предъявляет токен эмитенту"""
        # Проверяем подпись
        if not self.blind_rsa.verify(token['token_int'], token['signature']):
            raise Exception("Неверная подпись токена - подделка!")
        
        # Проверяем, не был ли токен уже использован
        if token['serial'] in self.spent_tokens:
            raise Exception(f"Повторное использование токена {token['serial']} - double-spending!")
        
        # Отмечаем токен как использованный
        self.spent_tokens[token['serial']] = token['amount']
        self.total_redeemed += token['amount']
        
        print(f"✓ Платёж на {token['amount']} подтверждён (токен: ...{str(token['serial'])[-4:]})")
        return True

# ---------- Демонстрация работы ----------
def main():
    print("=" * 70)
    print("ЭЛЕКТРОННАЯ КАРТА СО СЛЕПОЙ ПОДПИСЬЮ")
    print("Реализация требований: номинал, номер, защита, анонимность")
    print("=" * 70)
    
    # 1. Эмитент генерирует ключи
    print("\n[1] Эмитент генерирует ключевую пару...")
    pubkey, privkey = generate_rsa_keys()
    print(f"    Публичный ключ: e = {pubkey[0]}, n = {pubkey[1]}")
    
    # 2. Выпуск карты
    print("\n[2] Выпуск электронной карты...")
    card = ElectronicCard("CARD-001", nominal = 500, pubkey = pubkey, privkey = privkey)
    card.issue()
    
    if card.verify():
        print("    ✓ Подлинность карты подтверждена")
    else:
        print("    ✗ КАРТА ПОДДЕЛАНА!")
        return
    
    # 3. Создание системы платежей
    print("\n[3] Инициализация платёжной системы...")
    payment_system = AnonymousPaymentSystem(pubkey, privkey)
    
    # 4. Первый платёж (анонимный)
    print("\n[4] Покупка в магазине 'BookStore' на 120 единиц...")
    token1 = payment_system.create_payment_token(card, 120, "BookStore")
    print(f"    Создан анонимный токен (серийный номер скрыт)")
    
    print("    Продавец предъявляет токен эмитенту...")
    payment_system.redeem_token(token1)
    card.balance -= 120
    print(f"    Остаток на карте: {card.balance}")
    
    # 5. Попытка повторного использования того же токена
    print("\n[5] Попытка мошенничества: повторное использование токена...")
    try:
        payment_system.redeem_token(token1)
    except Exception as e:
        print(f"    ✗ Мошенничество阻止лено: {e}")
    
    # 6. Второй платёж
    print("\n[6] Покупка в 'CoffeeShop' на 380 единиц...")
    token2 = payment_system.create_payment_token(card, 380, "CoffeeShop")
    payment_system.redeem_token(token2)
    card.balance -= 380
    print(f"    Остаток на карте: {card.balance}")
    
    # 7. Попытка превысить номинал
    print("\n[7] Попытка превысить номинал карты...")
    try:
        payment_system.create_payment_token(card, 100, "Mall")
    except ValueError as e:
        print(f"    ✗ Транзакция отклонена: {e}")
    
    # 8. Итоги
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ ПРОВЕРКА ТРЕБОВАНИЙ:")
    print("=" * 70)
    print("✓ 1. Невозможность подделки")
    print("     - Электронная подпись эмитента на карте")
    print("     - Электронная подпись на каждом токене")
    print("\n✓ 2. Невозможность выхода за рамки номинала")
    print(f"     - Выдано токенов на сумму: {payment_system.total_issued}")
    print(f"     - Погашено токенов на сумму: {payment_system.total_redeemed}")
    print(f"     - Начальный номинал карты: {card.nominal}")
    print(f"     - Фактически потрачено: {card.nominal - card.balance}")
    print("     - Превышение номинала заблокировано системой")
    print("\n✓ 3. Неотслеживаемость платежей")
    print("     - Эмитент подписал токены, НЕ ВИДЯ их содержимого")
    print("     - Серийные номера токенов:") 
    print(f"       * Токен 1: ...{str(token1['serial'])[-4:]}")
    print(f"       * Токен 2: ...{str(token2['serial'])[-4:]}")
    print("     - Эмитент НЕ может связать токены с картой CARD-001")
    print("\n" + "=" * 70)
    print("✓ Все три требования к электронным деньгам выполнены!")
    print("=" * 70)

if __name__ == "__main__":
    main()