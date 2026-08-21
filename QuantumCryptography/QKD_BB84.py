# QKD: BB84
import random

# ==============================================
# 1. КВАНТОВОЕ СОСТОЯНИЕ (СИМУЛЯЦИЯ)
# ==============================================
# В реальной физике это волновые функции, но для симуляции мы используем
# классические метки поляризаций. 
# Словарь "состояний" описывает, как фотон выглядит в каждом базисе.
# Ключ = (базис_Алисы, бит) -> возвращает метку поляризации
POLARIZATIONS = {
    ('B1', 0): '↑',   # Вертикальная
    ('B1', 1): '→',   # Горизонтальная
    ('B2', 0): '↖',   # Диагональная 135°
    ('B2', 1): '↗',   # Диагональная 45°
}

# Базисы для измерения Боба
BASIS_CHOICES = ['B1', 'B2']

def alice_encode(bits, bases):
    """Алиса кодирует биты в фотоны (поляризации) согласно своим базисам."""
    photons = []
    for bit, basis in zip(bits, bases):
        photons.append(POLARIZATIONS[(basis, bit)])
    return photons

def bob_measure(photons, bob_bases):
    """
    Боб измеряет фотоны в своих случайных базисах.
    Если базис Боба совпадает с базисом Алисы, он получает правильный бит.
    Если нет - результат случаен (50/50).
    """
    measured_bits = []
    for photon, bob_basis in zip(photons, bob_bases):
        # Находим все возможные состояния, которые могли дать этот фотон
        possible_states = []
        for (alice_basis, bit), pol in POLARIZATIONS.items():
            if pol == photon:
                possible_states.append((alice_basis, bit))
        
        # Если Боб выбрал базис, который использовала Алиса, он точно узнает бит
        found = False
        for alice_basis, bit in possible_states:
            if alice_basis == bob_basis:
                measured_bits.append(bit)
                found = True
                break
        
        # Если базисы не совпали - измерение дает случайный бит
        if not found:
            measured_bits.append(random.randint(0, 1))
    
    return measured_bits

# ==============================================
# 2. ЕВА (ПЕРЕХВАТЧИК)
# ==============================================
def eve_intercept(photons, eve_bases = None):
    """
    Ева перехватывает фотоны, измеряет их в случайном базисе,
    и отправляет Бобу новые фотоны (поддельные).
    """
    if eve_bases is None:
        eve_bases = [random.choice(BASIS_CHOICES) for _ in photons]
    
    # Ева измеряет фотоны
    eve_bits = bob_measure(photons, eve_bases)
    
    # Ева пересылает Бобу новые фотоны, закодированные в её базисе
    new_photons = []
    for bit, basis in zip(eve_bits, eve_bases):
        new_photons.append(POLARIZATIONS[(basis, bit)])
    
    return new_photons, eve_bases, eve_bits

# ==============================================
# 3. ОСНОВНОЙ ПРОТОКОЛ BB84
# ==============================================
def run_bb84(num_bits = 16, with_eve = False):
    print("=" * 60)
    print(f"СИМУЛЯЦИЯ BB84 ({num_bits} бит)")
    print("=" * 60)
    
    # ---- Шаг 1: Алиса генерирует случайные биты и базисы ----
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(BASIS_CHOICES) for _ in range(num_bits)]
    
    print("\n[Алиса] Исходные биты:", alice_bits)
    print("[Алиса] Базисы:      ", alice_bases)
    
    # ---- Шаг 2: Алиса кодирует фотоны ----
    photons = alice_encode(alice_bits, alice_bases)
    print("[Алиса] Отправленные фотоны:", photons)
    
    # ---- Вмешательство Евы (если включено) ----
    if with_eve:
        print("\n[Ева] 🔥 ПЕРЕХВАТЫВАЕТ фотоны!")
        eve_bases = [random.choice(BASIS_CHOICES) for _ in range(num_bits)]
        photons, eve_bases, eve_bits = eve_intercept(photons, eve_bases)
        print(f"[Ева] Базисы Евы:    {eve_bases}")
        print(f"[Ева] Базисы Евы:    {eve_bits}")
        print(f"[Ева] Пересылает:    {photons}")
    
    # ---- Шаг 3: Боб генерирует случайные базисы и измеряет ----
    bob_bases = [random.choice(BASIS_CHOICES) for _ in range(num_bits)]
    bob_bits = bob_measure(photons, bob_bases)
    
    print("\n[Боб] Базисы Боба:  ", bob_bases)
    print("[Боб] Измеренные биты:", bob_bits)
    
    # ---- Шаг 4: Сравнение базисов (открытый классический канал) ----
    print("\n--- Сравнение базисов по открытому каналу ---")
    matching_positions = []
    raw_key_bits = []
    
    for i, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases)):
        if a_basis == b_basis:
            matching_positions.append(i)
            raw_key_bits.append(bob_bits[i])  # или alice_bits[i] - они совпадают, если нет Евы
    
    print(f"[Совпадения] Позиции: {matching_positions}")
    print(f"[Сырой ключ] Биты:    {raw_key_bits}")
    
    # ---- Шаг 5: Обнаружение ошибок и проверка четности ----
    print("\n--- Проверка четности (Parity Check) ---")
    
    # Количество бит для проверки (берём первые 30%, но не менее 2)
    check_size = max(2, len(raw_key_bits) // 3)
    if len(raw_key_bits) < check_size:
        check_size = len(raw_key_bits)
    
    # Берем первые check_size бит сырого ключа у Алисы и Боба
    alice_check_bits = []
    bob_check_bits = []
    
    for i in range(check_size):
        pos = matching_positions[i]
        alice_check_bits.append(alice_bits[pos])
        bob_check_bits.append(bob_bits[pos])
    
    alice_parity = sum(alice_check_bits) % 2
    bob_parity = sum(bob_check_bits) % 2
    
    print(f"Проверяемые биты (Алиса): {alice_check_bits} -> четность = {alice_parity}")
    print(f"Проверяемые биты (Боб):   {bob_check_bits} -> четность = {bob_parity}")
    
    if alice_parity == bob_parity:
        print("✅ Четность совпадает! Ключи идентичны.")
    else:
        print("❌ Четность НЕ совпадает! Есть ошибка или перехват.")
    
    # ---- Шаг 6: Формирование финального ключа (отбрасываем проверенные биты) ----
    final_key = raw_key_bits[check_size:]
    print(f"\n[Финальный ключ] ({len(final_key)} бит): {final_key}")
    
    # ---- Шаг 7: Статистика по Еве (если была) ----
    if with_eve:
        print("\n--- СТАТИСТИКА ПЕРЕХВАТА ---")
        # Считаем ошибки на совпадающих позициях (где базисы Алисы и Боба совпали)
        errors = 0
        for pos in matching_positions:
            if alice_bits[pos] != bob_bits[pos]:
                errors += 1
        
        error_rate = (errors / len(matching_positions)) * 100 if matching_positions else 0
        print(f"Ошибок на совпадающих позициях: {errors} из {len(matching_positions)}")
        print(f"Уровень ошибок (QBER): {error_rate:.1f}%")
        
        if error_rate > 11:
            print("⚠️  QBER > 11%! Ключ НЕ БЕЗОПАСЕН. Ева обнаружена!")
        else:
            print("✅ QBER в пределах нормы. Ключ считается безопасным.")
    
    return {
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_bits': bob_bits,
        'raw_key': raw_key_bits,
        'final_key': final_key,
        'matching_positions': matching_positions
    }

# ==============================================
# 4. ЗАПУСК СИМУЛЯЦИИ
# ==============================================
if __name__ == "__main__":
    # ---- Без Евы (идеальный канал) ----
    print("\n" + "=" * 60)
    print("СЦЕНАРИЙ 1: БЕЗ ПЕРЕХВАТЧИКА (ИДЕАЛЬНЫЙ КАНАЛ)")
    print("=" * 60)
    run_bb84(num_bits = 16, with_eve = False)
    
    # ---- С Евой (атака Intercept-Resend) ----
    print("\n" + "=" * 60)
    print("СЦЕНАРИЙ 2: С ПЕРЕХВАТЧИКОМ (ЕВА)")
    print("=" * 60)
    run_bb84(num_bits = 16, with_eve = True)