# Ментальный покер
import random
import math

# ----------------------------------------------------------------------
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ----------------------------------------------------------------------

def egcd(a, b):
    """Расширенный алгоритм Евклида: возвращает (g, x, y), где ax + by = g = gcd(a, b)"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1

def modinv(a, m):
    """Обратное число к a по модулю m (m должно быть простым или взаимно простым)"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"Обратного элемента для {a} по модулю {m} не существует")
    return x % m

def is_primitive_root(g, p):
    """Проверяет, является ли g первообразным корнем по модулю p (для справки, не используется)"""
    if g == 0 or g == 1:
        return False
    factors = set()
    phi = p - 1
    n = phi
    i = 2
    while i * i <= n:
        if n % i == 0:
            factors.add(i)
            while n % i == 0:
                n //= i
        i += 1
    if n > 1:
        factors.add(n)
    for q in factors:
        if pow(g, phi // q, p) == 1:
            return False
    return True

# ----------------------------------------------------------------------
# 2. КЛАССЫ ИГРОКОВ
# ----------------------------------------------------------------------

class Player:
    """Базовый класс для игрока (Алисы или Боба)"""
    def __init__(self, name, p):
        self.name = name
        self.p = p
        self.c = None          # секретный показатель (шифрование)
        self.d = None          # секретный показатель (дешифрование)
        self.card = None       # карта, которая досталась игроку (в открытом виде)
        self.card_code = None  # закодированное значение карты (число от 1 до p-1)

    def generate_keys(self):
        """Генерирует пару (c, d): c * d ≡ 1 (mod p - 1)"""
        phi = self.p - 1
        while True:
            c = random.randint(2, phi - 1)
            if math.gcd(c, phi) == 1:
                d = modinv(c, phi)
                self.c = c
                self.d = d
                return c, d

    def encrypt(self, x):
        """Шифрование: x ^ c mod p"""
        return pow(x, self.c, self.p)

    def decrypt(self, y):
        """Дешифрование: y ^ d mod p"""
        return pow(y, self.d, self.p)

    def __repr__(self):
        return f"{self.name}(c = {self.c}, d = {self.d}, card = {self.card})"


class Alice(Player):
    """Алиса — инициирует протокол"""
    def __init__(self, p):
        super().__init__("Алиса", p)
        # Словарь: открытое имя карты -> её числовой код
        self.card_mapping = {}
        # Обратный словарь: числовой код -> имя карты
        self.reverse_mapping = {}

    def setup_cards(self, card_names, card_codes):
        """
        Устанавливает соответствие между именами карт и их кодами.
        card_names: ['α', 'β', 'γ'] или ['Тройка', 'Семерка', 'Туз']
        card_codes: [2, 3, 5]  (числа по модулю p)
        """
        for name, code in zip(card_names, card_codes):
            self.card_mapping[name] = code
            self.reverse_mapping[code] = name
        # Сохраняем исходные коды для дальнейшей работы
        self.alpha_code, self.beta_code, self.gamma_code = card_codes

    def step1_send_encrypted(self):
        """
        Шаг 1: Алиса шифрует все три карты своей степенью,
        перемешивает и отправляет Бобу.
        Возвращает: (перемешанный список зашифрованных чисел, словарь соответствия)
        """
        # Зашифровываем каждую карту
        encrypted = {
            self.alpha_code: pow(self.alpha_code, self.c, self.p),
            self.beta_code:  pow(self.beta_code, self.c, self.p),
            self.gamma_code: pow(self.gamma_code, self.c, self.p),
        }
        # Создаём список и перемешиваем
        encrypted_list = list(encrypted.values())
        random.shuffle(encrypted_list)
        # Сохраняем маппинг для себя (чтобы знать, где какая карта)
        self.encrypted_mapping = encrypted
        return encrypted_list

    def step2_receive_card(self, chosen_encrypted):
        """
        Шаг 2: Алиса получает от Боба зашифрованное число,
        расшифровывает его и узнаёт свою карту.
        Возвращает: имя карты, которая досталась Алисе.
        """
        # Расшифровываем число своим d_A
        decrypted = pow(chosen_encrypted, self.d, self.p)
        # Определяем, какая это карта по маппингу
        card_name = None
        for name, code in self.card_mapping.items():
            if code == decrypted:
                card_name = name
                break
        self.card_code = decrypted
        self.card = card_name
        return card_name

    def step4_choose_and_encrypt(self, received_two):
        """
        Шаг 4: Алиса получает от Боба два числа (зашифрованные дважды),
        выбирает одно случайно, расшифровывает его своей степенью d_A
        и отправляет результат Бобу.
        Возвращает: (выбранное число для Боба, оставшееся в прикупе, отправленное Бобу значение)
        """
        # Выбираем случайное число из двух
        chosen = random.choice(received_two)
        # Расшифровываем его: (u^{c_B})^{d_A} = u^{c_B * d_A}
        # Но так как мы не знаем c_B, просто применяем d_A:
        w = pow(chosen, self.d, self.p)
        # Оставшееся число — в прикупе
        remaining = received_two[0] if received_two[1] == chosen else received_two[1]
        return chosen, remaining, w


class Bob(Player):
    """Боб — второй игрок"""
    def __init__(self, p):
        super().__init__("Боб", p)
        self.alice_mapping = None  # Здесь будет маппинг от Алисы (кто есть кто)

    def receive_encrypted_list(self, encrypted_list):
        """
        Получает от Алисы перемешанный список зашифрованных чисел.
        Сохраняет его для дальнейшей работы.
        """
        self.encrypted_list = encrypted_list
        return encrypted_list

    def step2_choose_for_alice(self):
        """
        Шаг 2: Боб выбирает случайное число из полученного списка
        и отправляет его Алисе.
        Возвращает: выбранное число (оно пойдёт Алисе)
        """
        chosen = random.choice(self.encrypted_list)
        # Удаляем это число из списка (оно уходит Алисе)
        self.remaining_for_bob = [x for x in self.encrypted_list if x != chosen]
        return chosen

    def step3_encrypt_remaining(self):
        """
        Шаг 3: Боб шифрует оставшиеся два числа своей степенью c_B,
        с вероятностью 1/2 переставляет их и отправляет Алисе.
        Возвращает: список из двух чисел (v1, v3) в случайном порядке
        """
        # Шифруем оставшиеся числа
        encrypted_remaining = [pow(x, self.c, self.p) for x in self.remaining_for_bob]
        # С вероятностью 1/2 переставляем
        if random.random() < 0.5:
            encrypted_remaining.reverse()
        self.sent_to_alice = encrypted_remaining
        return encrypted_remaining

    def step4_receive_and_decrypt(self, w):
        """
        Шаг 4: Боб получает от Алисы число w (уже расшифрованное ею),
        применяет свой d_B и узнаёт свою карту.
        Возвращает: имя карты, которая досталась Бобу.
        """
        z = pow(w, self.d, self.p)
        self.card_code = z
        # Определяем карту по маппингу от Алисы (мы его пока не знаем,
        # но в реальном протоколе Боб получает маппинг на предварительном этапе)
        # В нашей симуляции мы передадим маппинг отдельно
        return z

    def set_card_mapping(self, mapping):
        """
        Устанавливает соответствие чисел -> имён карт (получает от Алисы на предварительном этапе)
        """
        self.card_mapping = mapping
        # Создаём обратный словарь для быстрого поиска
        self.reverse_mapping = {v: k for k, v in mapping.items()}

    def get_card_name(self, code):
        """По числовому коду возвращает имя карты"""
        return self.reverse_mapping.get(code, None)


# ----------------------------------------------------------------------
# 3. ОСНОВНОЙ ПРОТОКОЛ
# ----------------------------------------------------------------------

def run_mental_poker(p = 23, card_names = None, card_codes = None):
    """
    Запускает полный протокол ментального покера для двух игроков.
    Возвращает: (карта Алисы, карта Боба, карта в прикупе)
    """
    if card_names is None:
        card_names = ['Тройка', 'Семерка', 'Туз']
    if card_codes is None:
        card_codes = [2, 3, 5]  # должны быть взаимно просты с p-1? Нет, просто числа < p

    print("=" * 60)
    print("МЕНТАЛЬНЫЙ ПОКЕР (3 карты)")
    print("=" * 60)

    # --- ПРЕДВАРИТЕЛЬНЫЙ ЭТАП ---
    print(f"\n1. ПРЕДВАРИТЕЛЬНЫЙ ЭТАП")
    print(f"   Простое число p = {p}")
    print(f"   Соответствие карт: {dict(zip(card_names, card_codes))}")

    # Создаём игроков
    alice = Alice(p)
    bob = Bob(p)

    # Генерируем ключи
    cA, dA = alice.generate_keys()
    cB, dB = bob.generate_keys()
    print(f"   Алиса: cA = {cA}, dA = {dA}")
    print(f"   Боб:   cB = {cB}, dB = {dB}")

    # Алиса устанавливает соответствие карт
    alice.setup_cards(card_names, card_codes)
    # Передаёт маппинг Бобу (в открытом виде)
    alice_mapping = alice.card_mapping
    bob.set_card_mapping(alice_mapping)
    print(f"   Маппинг передан Бобу: {alice_mapping}")

    # --- ШАГ 1 ---
    print(f"\n2. РАЗДАЧА КАРТ")
    print(f"   Шаг 1: Алиса шифрует карты и перемешивает...")
    encrypted_list = alice.step1_send_encrypted()
    print(f"   Алиса отправляет Бобу: {encrypted_list}")

    # Боб получает список
    bob.receive_encrypted_list(encrypted_list)

    # --- ШАГ 2 ---
    print(f"\n   Шаг 2: Боб выбирает карту для Алисы...")
    chosen_for_alice = bob.step2_choose_for_alice()
    print(f"   Боб отправляет Алисе: {chosen_for_alice}")

    # Алиса расшифровывает и узнаёт свою карту
    alice_card_name = alice.step2_receive_card(chosen_for_alice)
    print(f"   Алиса расшифровала: {alice.card_code} -> это {alice_card_name}")
    print(f"   ✅ Карта Алисы: {alice_card_name}")

    # --- ШАГ 3 ---
    print(f"\n   Шаг 3: Боб шифрует оставшиеся карты...")
    remaining_encrypted = bob.step3_encrypt_remaining()
    print(f"   Боб отправляет Алисе: {remaining_encrypted}")

    # --- ШАГ 4 ---
    print(f"\n   Шаг 4: Алиса выбирает карту для Боба...")
    chosen_for_bob, remaining_for_bob, w = alice.step4_choose_and_encrypt(remaining_encrypted)
    print(f"   Алиса выбрала: {chosen_for_bob}, расшифровала: {w}")
    print(f"   Алиса отправляет Бобу: {w}")

    # Боб расшифровывает и узнаёт свою карту
    bob_card_code = bob.step4_receive_and_decrypt(w)
    bob_card_name = bob.get_card_name(bob_card_code)
    print(f"   Боб расшифровал: {bob_card_code} -> это {bob_card_name}")
    print(f"   ✅ Карта Боба: {bob_card_name}")

    # Определяем карту в прикупе
    # В прикупе осталось то число, которое Алиса НЕ выбрала на шаге 4
    # Но нам нужно узнать, какая карта осталась. Мы знаем все три кода.
    all_codes = set(card_codes)
    dealt_codes = {alice.card_code, bob_card_code}
    remaining_code = (all_codes - dealt_codes).pop()
    remaining_name = alice.reverse_mapping[remaining_code]
    print(f"\n   🃏 Карта в прикупе: {remaining_name} (код {remaining_code})")

    # --- ПРОВЕРКА КОРРЕКТНОСТИ ---
    print("\n" + "=" * 60)
    print("ПРОВЕРКА КОРРЕКТНОСТИ РАЗДАЧИ")
    print("=" * 60)
    print(f"Алиса: {alice_card_name}")
    print(f"Боб:   {bob_card_name}")
    print(f"Прикуп: {remaining_name}")

    # Проверяем, что все карты разные
    if len({alice_card_name, bob_card_name, remaining_name}) == 3:
        print("✅ Все карты разные — раздача корректна!")
    else:
        print("❌ ОШИБКА: карты повторяются!")

    return alice_card_name, bob_card_name, remaining_name


# ----------------------------------------------------------------------
# 4. ЗАПУСК ПРОТОКОЛА С РАЗНЫМИ ПАРАМЕТРАМИ
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # --- Пример 1: как в тексте (p=23, карты 2,3,5) ---
    print("\n" + "🔹" * 30)
    print("ПРИМЕР 1: ИЗ УЧЕБНИКА (p = 23)")
    print("🔹" * 30)
    run_mental_poker(p = 23, card_names = ['α', 'β', 'γ'], card_codes = [2, 3, 5])

    # --- Пример 2: с другими картами и большим p ---
    print("\n" + "🔹" * 30)
    print("ПРИМЕР 2: БОЛЬШОЕ ПРОСТОЕ ЧИСЛО (p = 101)")
    print("🔹" * 30)
    # Для p=101 возьмём другие коды карт (главное, чтобы они были < p и различны)
    run_mental_poker(p = 101, card_names = ['Король', 'Дама', 'Валет'], card_codes = [10, 20, 30])

    # --- Пример 3: многократный запуск для проверки статистики ---
    print("\n" + "🔹" * 30)
    print("ПРИМЕР 3: СТАТИСТИКА ПО 10 РАЗДАЧАМ")
    print("🔹" * 30)
    stats = {"Алиса": {}, "Боб": {}, "Прикуп": {}}
    for i in range(10):
        a, b, r = run_mental_poker(p = 23, card_names = ['α', 'β', 'γ'], card_codes = [2, 3, 5])
        for name, card in [("Алиса", a), ("Боб", b), ("Прикуп", r)]:
            stats[name][card] = stats[name].get(card, 0) + 1
        print("-" * 40)

    print("\nСтатистика по 10 раздачам:")
    for player, dist in stats.items():
        print(f"{player}: {dist}")