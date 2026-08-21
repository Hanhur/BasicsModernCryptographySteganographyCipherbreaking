# Атаки и технические вопросы 
import random
import math

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (без numpy)
# ============================================================

def bits_to_str(bits):
    """Преобразует список битов в строку"""
    return ''.join(str(b) for b in bits)

def hamming_distance(bits1, bits2):
    """Вычисляет расстояние Хэмминга (количество несовпадающих битов)"""
    return sum(1 for a, b in zip(bits1, bits2) if a != b)

def calculate_qber(key1, key2):
    """Вычисляет уровень ошибок QBER (в процентах)"""
    if len(key1) != len(key2) or len(key1) == 0:
        return 100.0
    errors = hamming_distance(key1, key2)
    return (errors / len(key1)) * 100.0

# ============================================================
# 2. КЛАССЫ УЧАСТНИКОВ
# ============================================================

class Alice:
    """Алиса - отправитель"""
    def __init__(self, key_length = 100):
        self.key_length = key_length
        # Случайные биты (0 или 1)
        self.raw_bits = [random.randint(0, 1) for _ in range(key_length)]
        # Случайные базисы: 0 = B1 (прямой), 1 = B2 (диагональный)
        self.bases = [random.randint(0, 1) for _ in range(key_length)]
        # Поляризация фотонов: 
        # для бита 0 и базы 0 -> '→' (горизонтальный)
        # для бита 1 и базы 0 -> '↑' (вертикальный)
        # для бита 0 и базы 1 -> '↖' (диагональный 45°)
        # для бита 1 и базы 1 -> '↗' (диагональный 135°)
        self.photons = []
        for bit, basis in zip(self.raw_bits, self.bases):
            if basis == 0:  # B1
                self.photons.append('→' if bit == 0 else '↑')
            else:  # B2
                self.photons.append('↖' if bit == 0 else '↗')
    
    def send_photons(self):
        """Возвращает фотоны для отправки по квантовому каналу"""
        return self.photons.copy()
    
    def get_public_info(self):
        """Возвращает базисы для публичного обсуждения (НЕ биты!)"""
        return self.bases.copy()

class Eve:
    """Ева - перехватчик (с квантовым компьютером)"""
    def __init__(self):
        self.measured_bits = []
        self.measured_bases = []
        self.caught = False
    
    def intercept_photons(self, photons, alice_bases = None):
        """
        Ева перехватывает фотоны и измеряет их в случайном базисе.
        Возвращает изменённые фотоны для Боба.
        """
        self.measured_bits = []
        self.measured_bases = []
        modified_photons = []
        
        for photon in photons:
            # Ева выбирает случайный базис для измерения
            eve_basis = random.randint(0, 1)
            self.measured_bases.append(eve_basis)
            
            # Измерение фотона (с вероятностью ошибки, если базис не совпал)
            # Идеальное измерение: если базис совпадает, бит восстанавливается точно
            # Если не совпадает - случайный результат (50/50)
            if eve_basis == 0:  # B1
                if photon in ['→', '↑']:
                    measured_bit = 0 if photon == '→' else 1
                else:
                    # Если фотон в диагональном базисе, а Ева мерит в прямом
                    measured_bit = random.randint(0, 1)
            else:  # B2
                if photon in ['↖', '↗']:
                    measured_bit = 0 if photon == '↖' else 1
                else:
                    # Если фотон в прямом базисе, а Ева мерит в диагональном
                    measured_bit = random.randint(0, 1)
            
            self.measured_bits.append(measured_bit)
            
            # Ева пересылает фотон дальше (с коллапсированным состоянием)
            # После измерения Евы фотон меняет поляризацию
            if eve_basis == 0:
                new_photon = '→' if measured_bit == 0 else '↑'
            else:
                new_photon = '↖' if measured_bit == 0 else '↗'
            
            modified_photons.append(new_photon)
        
        return modified_photons
    
    def get_measured_key(self, bob_bases):
        """
        Ева пытается восстановить ключ, используя свои измеренные базисы.
        Если её базис совпал с базисом Боба - она знает бит.
        """
        eve_key = []
        for i, (eve_basis, bob_basis) in enumerate(zip(self.measured_bases, bob_bases)):
            if eve_basis == bob_basis:
                eve_key.append(self.measured_bits[i])
        return eve_key

class Bob:
    """Боб - получатель"""
    def __init__(self):
        self.bases = []
        self.raw_measurements = []
        self.measured_photons = []
    
    def measure_photons(self, photons):
        """
        Боб измеряет полученные фотоны в случайном базисе.
        """
        self.bases = []
        self.raw_measurements = []
        self.measured_photons = []
        
        for photon in photons:
            bob_basis = random.randint(0, 1)
            self.bases.append(bob_basis)
            
            # Измерение Бобом
            if bob_basis == 0:  # B1
                if photon == '→':
                    bit = 0
                elif photon == '↑':
                    bit = 1
                else:
                    # Если фотон в диагональном базисе, а Боб мерит в прямом
                    bit = random.randint(0, 1)
            else:  # B2
                if photon == '↖':
                    bit = 0
                elif photon == '↗':
                    bit = 1
                else:
                    # Если фотон в прямом базисе, а Боб мерит в диагональном
                    bit = random.randint(0, 1)
            
            self.raw_measurements.append(bit)
            self.measured_photons.append(photon)
        
        return self.raw_measurements.copy()
    
    def generate_raw_key(self, alice_bases):
        """
        Формирует сырой ключ, отбрасывая биты, где базисы не совпали.
        """
        raw_key = []
        for i, (alice_basis, bob_basis) in enumerate(zip(alice_bases, self.bases)):
            if alice_basis == bob_basis:
                raw_key.append(self.raw_measurements[i])
        return raw_key

# ============================================================
# 3. ФУНКЦИЯ СИМУЛЯЦИИ ПРОТОКОЛА BB84
# ============================================================

def simulate_bb84(key_length = 100, with_eve = True, eve_measure_all = True):
    """
    Симуляция полного протокола BB84.
    
    Параметры:
    - key_length: длина исходного ключа
    - with_eve: если True, Ева перехватывает фотоны
    - eve_measure_all: если True, Ева измеряет все фотоны (иначе только часть)
    
    Возвращает словарь с результатами:
    - alice_key: исходный ключ Алисы
    - bob_key: ключ Боба (после согласования)
    - eve_key: ключ Евы (если она перехватывала)
    - qber: уровень ошибок
    - eva_detected: обнаружена ли Ева (QBER > 11%)
    - raw_bits_match: совпадают ли биты
    """
    
    print("=" * 70)
    print("СИМУЛЯЦИЯ ПРОТОКОЛА КВАНТОВОГО РАСПРЕДЕЛЕНИЯ КЛЮЧА BB84")
    print("=" * 70)
    print(f"Длина ключа: {key_length} бит")
    print(f"Ева активна: {'ДА' if with_eve else 'НЕТ'}")
    print("-" * 70)
    
    # --- ШАГ 1: Алиса генерирует фотоны ---
    alice = Alice(key_length)
    print(f"\n[Алиса] Сгенерировала {key_length} фотонов:")
    print(f"  Биты:       {bits_to_str(alice.raw_bits)}")
    print(f"  Базисы:     {bits_to_str(alice.bases)}")
    print(f"  Фотоны:     {' '.join(alice.photons)}")
    
    photons = alice.send_photons()
    
    # --- ШАГ 2: Перехват Евой (опционально) ---
    eve = None
    modified_photons = photons.copy()
    
    if with_eve:
        eve = Eve()
        print(f"\n[Ева] Перехватывает квантовый канал...")
        
        if eve_measure_all:
            modified_photons = eve.intercept_photons(photons)
            print(f"  Ева измерила ВСЕ фотоны в случайных базисах")
        else:
            # Ева измеряет только часть фотонов (например, 50%)
            modified_photons = []
            for i, photon in enumerate(photons):
                if random.random() < 0.5:
                    # Измеряет этот фотон
                    single_measure = eve.intercept_photons([photon])
                    modified_photons.append(single_measure[0])
                else:
                    # Пропускает без измерения
                    modified_photons.append(photon)
            print(f"  Ева измерила ~50% фотонов")
        
        print(f"  Базисы Евы: {bits_to_str(eve.measured_bases)}")
        print(f"  Биты Евы:   {bits_to_str(eve.measured_bits)}")
    
    # --- ШАГ 3: Боб получает и измеряет фотоны ---
    bob = Bob()
    print(f"\n[Боб] Получает фотоны и измеряет их...")
    bob_measurements = bob.measure_photons(modified_photons)
    print(f"  Базисы Боба: {bits_to_str(bob.bases)}")
    print(f"  Измерения:   {bits_to_str(bob.raw_measurements)}")
    
    # --- ШАГ 4: Публичное обсуждение базисов ---
    print(f"\n[Публичный канал] Алиса и Боб сравнивают базисы...")
    alice_bases = alice.get_public_info()
    
    alice_key = []
    bob_key = []
    matching_positions = []
    
    for i, (alice_b, bob_b) in enumerate(zip(alice_bases, bob.bases)):
        if alice_b == bob_b:
            alice_key.append(alice.raw_bits[i])
            bob_key.append(bob.raw_measurements[i])
            matching_positions.append(i)
    
    print(f"  Совпало позиций: {len(matching_positions)} из {key_length}")
    print(f"  Ключ Алисы:      {bits_to_str(alice_key)}")
    print(f"  Ключ Боба:        {bits_to_str(bob_key)}")
    
    # --- ШАГ 5: Проверка ошибок (QBER) ---
    qber = calculate_qber(alice_key, bob_key)
    print(f"\n[Проверка] Уровень ошибок QBER: {qber:.2f}%")
    
    eva_detected = qber > 11.0
    if eva_detected:
        print("  ⚠️  ВНИМАНИЕ: QBER > 11%! Ева обнаружена!")
        print("  → Алиса и Боб прерывают сеанс и повторяют процедуру.")
        print("  → (Атака DoS: Ева может повторять это бесконечно!)")
    else:
        print("  ✅ QBER в допустимых пределах. Ева не обнаружена.")
    
    # --- ШАГ 6: Попытка Евы восстановить ключ ---
    if with_eve and eve is not None:
        eve_key = eve.get_measured_key(bob.bases)
        print(f"\n[Ева] Попытка восстановить ключ...")
        print(f"  Ключ Евы (известные биты): {bits_to_str(eve_key)}")
        
        if len(eve_key) > 0:
            # Сравниваем ключ Евы с ключом Алисы (только на совпадающих позициях)
            eve_match_count = 0
            for i in range(min(len(alice_key), len(eve_key))):
                if alice_key[i] == eve_key[i]:
                    eve_match_count += 1
            eve_accuracy = (eve_match_count / len(eve_key)) * 100 if len(eve_key) > 0 else 0
            print(f"  Точность Евы: {eve_accuracy:.2f}% (случайное угадывание = 50%)")
            
            if eve_accuracy > 80:
                print("  ⚠️  Ева восстановила значительную часть ключа!")
            else:
                print("  ✅ Ева не может восстановить ключ (принцип неопределённости).")
    
    # --- ИТОГОВЫЙ РЕЗУЛЬТАТ ---
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ СИМУЛЯЦИИ")
    print("=" * 70)
    
    result = {
        'alice_key': alice_key,
        'bob_key': bob_key,
        'eve_key': eve_key if with_eve and eve else [],
        'qber': qber,
        'eva_detected': eva_detected,
        'key_length': len(alice_key),
        'matching_positions': matching_positions
    }
    
    print(f"✅ Ключ успешно сгенерирован: {'ДА' if not eva_detected else 'НЕТ (прерван)'}")
    print(f"📊 Длина финального ключа: {len(alice_key)} бит")
    print(f"🔒 Совпадение бит: {'ДА' if alice_key == bob_key else 'НЕТ (есть ошибки)'}")
    
    return result

# ============================================================
# 4. ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ АНАЛИЗА
# ============================================================

def analyze_attack_scenarios():
    """
    Анализирует разные сценарии атак и показывает, почему QKD безопасен.
    """
    print("\n" + "=" * 70)
    print("АНАЛИЗ СЦЕНАРИЕВ АТАК")
    print("=" * 70)
    
    scenarios = [
        ("🔹 Сценарий 1: Без Евы", False, True),
        ("🔹 Сценарий 2: Ева измеряет все фотоны (классическая атака)", True, True),
        ("🔹 Сценарий 3: Ева измеряет только часть фотонов", True, False),
    ]
    
    for desc, with_eve, measure_all in scenarios:
        print(f"\n{desc}")
        print("-" * 50)
        
        result = simulate_bb84(
            key_length = 30,
            with_eve = with_eve,
            eve_measure_all = measure_all
        )
        
        # Показываем философский вывод
        if with_eve and result['eva_detected']:
            print("\n💡 Вывод: Принцип неопределённости Гейзенберга защищает ключ!")
            print("   Ева не может измерить фотон, не изменив его состояние.")
            print("   Любая попытка перехвата обнаруживается через QBER.")
        elif not with_eve:
            print("\n💡 Вывод: В отсутствие Евы ключ передаётся идеально.")
            print("   (Но проблема аутентификации остаётся - нужен MAC или подпись)")

def simulate_dos_attack():
    """
    Симулирует атаку отказа в обслуживании (DoS).
    Ева повторяет перехват, заставляя Алису и Боба бесконечно повторять протокол.
    """
    print("\n" + "=" * 70)
    print("СИМУЛЯЦИЯ АТАКИ ОТКАЗА В ОБСЛУЖИВАНИИ (DoS)")
    print("=" * 70)
    
    max_attempts = 5
    success = False
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Попытка #{attempt} ---")
        result = simulate_bb84(
            key_length = 30,
            with_eve = True,
            eve_measure_all = True
        )
        
        if result['eva_detected']:
            print(f"❌ Попытка {attempt} провалена! Ева обнаружена.")
            print("   → Алиса и Боб переключают канал (меняют длину волны).")
            if attempt < max_attempts:
                print("   → Повторная попытка...")
        else:
            print(f"✅ Попытка {attempt} успешна! Ключ сгенерирован.")
            success = True
            break
    
    if not success:
        print("\n" + "=" * 70)
        print("⚠️  DoS АТАКА УСПЕШНА!")
        print("   Ева заблокировала обмен ключами на всех {max_attempts} попытках.")
        print("   → Алиса и Боб вынуждены сменить квантовый канал связи.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✅ Атака DoS отражена переключением каналов.")
        print("=" * 70)

# ============================================================
# 5. ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА
# ============================================================

def main():
    """
    Основная функция для запуска всех симуляций.
    """
    print("=" * 70)
    print("КВАНТОВОЕ РАСПРЕДЕЛЕНИЕ КЛЮЧА (BB84)")
    print("Симуляция на чистом Python (без NumPy)")
    print("=" * 70)
    print("\nСогласно принципу неопределённости Гейзенберга:")
    print("  → Ева не может измерить фотон, не изменив его поляризацию.")
    print("  → Любая атака вносит ошибки (QBER).")
    print("  → При QBER > 11% сеанс прерывается.")
    print("=" * 70)
    
    while True:
        print("\nВыберите режим симуляции:")
        print("  1. Базовая симуляция BB84 (без Евы)")
        print("  2. BB84 с перехватом Евой (все фотоны)")
        print("  3. BB84 с перехватом Евой (часть фотонов)")
        print("  4. Сравнительный анализ всех сценариев")
        print("  5. Симуляция DoS-атаки (отказ в обслуживании)")
        print("  6. Выйти")
        
        choice = input("\nВаш выбор (1-6): ").strip()
        
        if choice == '1':
            simulate_bb84(key_length = 40, with_eve = False)
        elif choice == '2':
            simulate_bb84(key_length = 40, with_eve = True, eve_measure_all = True)
        elif choice == '3':
            simulate_bb84(key_length = 40, with_eve = True, eve_measure_all = False)
        elif choice == '4':
            analyze_attack_scenarios()
        elif choice == '5':
            simulate_dos_attack()
        elif choice == '6':
            print("\n👋 До свидания! Квантовая криптография ждёт вас!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        input("\nНажмите Enter, чтобы продолжить...")

# ============================================================
# 6. ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    # Устанавливаем сид для воспроизводимости (опционально)
    # random.seed(42)
    main()