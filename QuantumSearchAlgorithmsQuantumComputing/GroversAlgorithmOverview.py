# Обзор алгоритма Гровера
import math
import cmath

# ------------------------------------------------------------
# 1. БАЗОВЫЕ ОПЕРАЦИИ НАД ВЕКТОРАМИ (без NumPy)
# ------------------------------------------------------------

def vector_add(v1, v2):
    """Сложение двух векторов"""
    return [v1[i] + v2[i] for i in range(len(v1))]

def vector_scalar_mult(v, scalar):
    """Умножение вектора на скаляр"""
    return [v[i] * scalar for i in range(len(v))]

def vector_dot(v1, v2):
    """Скалярное произведение (для проверки)"""
    return sum(v1[i] * v2[i] for i in range(len(v1)))

def print_state(state, title = "Состояние"):
    """Красиво выводим амплитуды и вероятности"""
    print(f"\n{title}:")
    n = len(state)
    num_bits = int(math.log2(n))
    for i, amp in enumerate(state):
        prob = abs(amp) ** 2
        # Бинарное представление индекса (ключ)
        binary = format(i, f'0{num_bits}b')
        print(f"  |{binary}⟩ (ключ {i}): амплитуда = {amp.real:+.3f} {amp.imag:+.3f}i, вероятность = {prob:.2%}")

# ------------------------------------------------------------
# 2. ОПЕРАТОРЫ АЛГОРИТМА ГРОВЕРА
# ------------------------------------------------------------

def apply_hadamard_to_all(n):
    """
    Создает вектор суперпозиции для n кубитов.
    Все амплитуды = 1 / sqrt(N)
    """
    N = 1 << n  # 2^n
    amplitude = 1.0 / math.sqrt(N)
    return [complex(amplitude, 0.0) for _ in range(N)]

def grover_oracle(state, target_index):
    """
    ОРАКУЛ: инвертирует фазу (меняет знак) у целевого состояния.
    Если состояние = target_index, умножаем амплитуду на -1.
    """
    new_state = state.copy()
    new_state[target_index] = -new_state[target_index]
    return new_state

def grover_diffusion(state):
    """
    ОПЕРАТОР ДИФФУЗИИ (инверсия относительно среднего).
    Формула: amp_i = -amp_i + 2 * average
    """
    n = len(state)
    # Вычисляем среднюю амплитуду
    avg = sum(state) / n
    
    # Применяем преобразование: new_amp_i = -amp_i + 2*avg
    new_state = []
    for amp in state:
        new_amp = -amp + 2 * avg
        new_state.append(new_amp)
    
    return new_state

def grover_iteration(state, target_index):
    """Одна полная итерация Гровера: Оракул → Диффузия"""
    state = grover_oracle(state, target_index)
    state = grover_diffusion(state)
    return state

# ------------------------------------------------------------
# 3. ОСНОВНАЯ ПРОГРАММА
# ------------------------------------------------------------

def main():
    # --- ПАРАМЕТРЫ ---
    num_qubits = 3          # Ищем 3-битный ключ (0..7)
    N = 1 << num_qubits     # 8 состояний
    target = 5              # Искомый ключ (в двоичном виде: 101)
    
    print("=" * 60)
    print(f"АЛГОРИТМ ГРОВЕРА (чистый Python, без NumPy)")
    print(f"Ищем ключ: {target} (двоичный: {format(target, f'0{num_qubits}b')})")
    print(f"Размер пространства ключей: {N}")
    print("=" * 60)
    
    # --- ШАГ 1: Суперпозиция ---
    state = apply_hadamard_to_all(num_qubits)
    print_state(state, "1. Суперпозиция (равномерное распределение)")
    
    # --- ШАГ 2: Вычисление оптимального числа итераций ---
    # Формула: R = floor(pi/4 * sqrt(N))
    optimal_iterations = int(math.floor((math.pi / 4.0) * math.sqrt(N)))
    print(f"\nОптимальное число итераций: {optimal_iterations}")
    
    # --- ШАГ 3: Запоминаем состояние ДО для сравнения ---
    state_before = state.copy()
    
    # --- ШАГ 4: Выполняем итерации Гровера ---
    print(f"\n--- Запускаем {optimal_iterations} итераций ---")
    for i in range(optimal_iterations):
        state = grover_iteration(state, target)
        # Показываем прогресс после каждой итерации (опционально)
        if (i + 1) % 1 == 0:  # показываем все
            prob_target = abs(state[target]) ** 2
            print(f"  Итерация {i + 1}: вероятность ключа {target} = {prob_target:.2%}")
    
    # --- ШАГ 5: Финальное состояние ---
    print_state(state, f"\n6. Финальное состояние после {optimal_iterations} итераций")
    
    # --- ШАГ 6: Анализ результатов ---
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    
    # Вероятность найти искомый ключ
    prob_target = abs(state[target]) ** 2
    print(f"✅ Вероятность найти ключ {target}: {prob_target:.2%}")
    
    # Сравнение с классическим поиском
    classical_prob = 0.5  # 50% для N/2 попыток
    print(f"📊 Классический поиск (N/2 попыток): {classical_prob:.2%}")
    print(f"🚀 Ускорение: квадратичное (вместо {N} проверок нужно ~{optimal_iterations})")
    
    # Проверяем, все ли вероятности суммируются в 1
    total_prob = sum(abs(amp) ** 2 for amp in state)
    print(f"\nСумма всех вероятностей: {total_prob:.4f} (должна быть ≈ 1.0)")
    
    # Находим состояние с максимальной вероятностью
    max_prob = 0
    max_index = 0
    for i, amp in enumerate(state):
        prob = abs(amp) ** 2
        if prob > max_prob:
            max_prob = prob
            max_index = i
    
    print(f"\n🎯 Состояние с максимальной вероятностью: {max_index} (вероятность {max_prob:.2%})")
    if max_index == target:
        print("✅ АЛГОРИТМ СРАБОТАЛ ПРАВИЛЬНО! Найден искомый ключ.")
    else:
        print("⚠️ Что-то пошло не так (возможно, нужно другое число итераций).")
    
    # --- ДОПОЛНИТЕЛЬНО: показываем, как менялась бы вероятность ---
    print("\n" + "=" * 60)
    print("ДИНАМИКА ВЕРОЯТНОСТИ (пошагово):")
    print("=" * 60)
    
    # Сбросим состояние и пройдем все итерации с выводом
    test_state = apply_hadamard_to_all(num_qubits)
    for i in range(optimal_iterations + 2):  # +2 чтобы показать перелет
        prob = abs(test_state[target]) ** 2
        if i <= optimal_iterations + 1:
            marker = " ← ОПТИМУМ" if i == optimal_iterations else ""
            print(f"  Итерация {i:2d}: вероятность ключа {target} = {prob:.2%}{marker}")
        test_state = grover_iteration(test_state, target)

if __name__ == "__main__":
    main()