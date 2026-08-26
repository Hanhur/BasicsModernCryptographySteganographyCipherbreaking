# Задача поиска с единственным решением и вероятность усиления амплитуды
import math
import cmath

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С СОСТОЯНИЯМИ
# ============================================================

def create_uniform_superposition(n):
    """
    Создаёт равномерную суперпозицию всех |x> для n кубитов.
    Возвращает словарь {двоичная_строка: комплексная_амплитуда}
    """
    N = 1 << n  # 2^n
    amp = 1.0 / math.sqrt(N)
    state = {}
    for i in range(N):
        # Формируем двоичную строку длиной n
        binary_str = format(i, f'0{n}b')
        state[binary_str] = complex(amp, 0.0)
    return state

def apply_oracle(state, target):
    """
    Оракул: меняет знак амплитуды у целевого состояния |target>.
    Это соответствует отражению относительно оси |A0> (не-решений).
    """
    if target in state:
        state[target] = -state[target]
    return state

def apply_diffusion(state):
    """
    Оператор диффузии (усиление амплитуды).
    Выполняет отражение относительно равномерной суперпозиции |u>.
    Формула: D = 2|u><u| - I
    """
    N = len(state)
    # Шаг 1: найти среднюю амплитуду <u|state>
    sum_amplitudes = sum(state.values())
    mean = sum_amplitudes / N
    
    # Шаг 2: применить D: amp_i -> 2*mean - amp_i
    for key in state:
        state[key] = 2.0 * mean - state[key]
    
    return state

def apply_grover_iteration(state, target):
    """
    Одна полная итерация G:
    1) Оракул (отражение относительно |A0>)
    2) Диффузия (отражение относительно |u>)
    """
    state = apply_oracle(state, target)
    state = apply_diffusion(state)
    return state

def measure_probabilities(state):
    """
    Вычисляет вероятности для каждого состояния.
    """
    probs = {}
    for key, amp in state.items():
        probs[key] = abs(amp) ** 2
    return probs

def find_max_probability(state):
    """
    Находит состояние с максимальной вероятностью.
    """
    probs = measure_probabilities(state)
    best = max(probs, key = probs.get)
    return best, probs[best]

# ============================================================
# 2. ОСНОВНАЯ ФУНКЦИЯ АЛГОРИТМА ГРОВЕРА
# ============================================================

def grover_search(n, target, max_iterations = None, verbose = True):
    """
    Реализует алгоритм Гровера для поиска единственного решения.

    Аргументы:
        n              -- число кубитов (N = 2 ^ n)
        target         -- строка-решение (например, '101')
        max_iterations -- если None, то используется оптимальное число
        verbose        -- печатать ли детали на каждом шаге

    Возвращает:
        best_state, best_prob, iterations_done
    """
    N = 1 << n
    if max_iterations is None:
        # Оптимальное число итераций: t = floor(pi/4 * sqrt(N) - 0.5)
        theta = math.asin(1.0 / math.sqrt(N))
        t_opt = int(round(math.pi / (4 * theta) - 0.5))
        max_iterations = max(0, t_opt)  # не может быть отрицательным

    # Шаг 1: Инициализация
    state = create_uniform_superposition(n)
    if verbose:
        print(f"Начальное состояние (равномерная суперпозиция из {N} состояний)")
        print(f"Целевое состояние: |{target}>\n")
        print(f"Оптимальное число итераций: {max_iterations}\n")
        print("-" * 60)

    # Шаг 2: Итерации Гровера
    for t in range(1, max_iterations + 1):
        state = apply_grover_iteration(state, target)
        
        if verbose:
            best_state, best_prob = find_max_probability(state)
            print(f"Итерация {t}:")
            print(f"  Наиболее вероятное состояние: |{best_state}>")
            print(f"  Вероятность решения |{target}>: {abs(state.get(target, 0)) ** 2:.4%}")
            print(f"  Вероятность лучшего состояния: {best_prob:.4%}")
            print("-" * 60)

    # Шаг 3: Финальное измерение
    best_state, best_prob = find_max_probability(state)
    target_prob = abs(state.get(target, 0)) ** 2
    
    if verbose:
        print("\n=== РЕЗУЛЬТАТ ИЗМЕРЕНИЯ ===")
        print(f"Состояние с максимальной вероятностью: |{best_state}> (вероятность {best_prob:.4%})")
        print(f"Вероятность найти ЦЕЛЕВОЕ состояние |{target}>: {target_prob:.4%}")
        if best_state == target:
            print("✅ УСПЕХ: алгоритм нашёл правильное решение!")
        else:
            print("❌ НЕУДАЧА: алгоритм не попал в целевое состояние.")
        print("=" * 60)
    
    return best_state, best_prob, max_iterations

# ============================================================
# 3. ПРОВЕРКА НА ПРИМЕРАХ ИЗ ВАШЕГО ТЕКСТА
# ============================================================

def run_example(n, target):
    """
    Запускает пример и выводит сравнение с теоретической формулой.
    """
    N = 1 << n
    theta = math.asin(1.0 / math.sqrt(N))
    t_theory = math.pi / (4 * theta) - 0.5
    
    print(f"\n{'=' * 70}")
    print(f"ПРИМЕР: n = {n} кубитов, N = {N} состояний, решение = |{target}>")
    print(f"Теоретический угол θ = {math.degrees(theta):.2f}°")
    print(f"Теоретическое оптимальное t = {t_theory:.3f} (целое ≈ {round(t_theory)})")
    print('=' * 70)
    
    best, prob, iters = grover_search(n, target, verbose = True)
    
    # Проверка соответствия формуле из текста
    t_used = iters
    prob_formula = math.sin((2 * t_used + 1) * theta) ** 2
    print(f"\nПроверка по формуле p = sin²((2t + 1)θ):")
    print(f"  t = {t_used}, (2t + 1)θ = {(2 * t_used + 1) * theta:.4f} рад = {math.degrees((2 * t_used + 1) * theta):.2f}°")
    print(f"  Теоретическая вероятность: {prob_formula:.4%}")
    print(f"  Фактическая вероятность:   {prob:.4%}")
    print(f"  Отклонение: {abs(prob_formula - prob):.6%}")

# ============================================================
# 4. ЗАПУСК
# ============================================================

if __name__ == "__main__":
    # Пример 1: N = 4 (из текста: 100% за 1 итерацию)
    run_example(2, '11')   # 2 кубита -> 4 состояния
    
    # Пример 2: N = 8 (для наглядности)
    run_example(3, '101')
    
    # Пример 3: N = 128 (как в вашем тексте)
    run_example(7, '1010101')
    
    # Демонстрация, что происходит при переборе (N=16)
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ПЕРЕЛЁТА (перебор итераций)")
    print("=" * 70)
    n = 4
    N = 1 << n
    target = '1111'
    theta = math.asin(1.0 / math.sqrt(N))
    state = create_uniform_superposition(n)
    
    print(f"n = {n}, N = {N}, target = |{target}>, θ = {math.degrees(theta):.2f}°")
    print("Итерация | Вероятность | Угол (2t + 1)θ")
    print("-" * 40)
    for t in range(0, 9):
        if t > 0:
            state = apply_grover_iteration(state, target)
        prob = abs(state.get(target, 0)) ** 2
        angle_deg = math.degrees((2 * t + 1) * theta)
        print(f"  {t}     |   {prob:.2%}    |   {angle_deg:.1f}°")