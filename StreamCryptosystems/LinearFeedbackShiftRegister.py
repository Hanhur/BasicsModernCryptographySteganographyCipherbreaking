# 4. Линейный регистр сдвига с обратной связью (Linear feedback shift register - LFSR)
class LFSR:
    """
    Линейный регистр сдвига с обратной связью (LFSR).
    Работает в GF(2) (биты 0/1).
    """
    
    def __init__(self, c_coeffs: list[int], state: list[int]):
        """
        Инициализация LFSR.
        
        Параметры:
        c_coeffs : список коэффициентов c1, c2, ..., cL (int 0 / 1) для многочлена c(D) = 1 + c1 * D + c2 * D ^ 2 + ... + cL * D ^ L cL обязательно должен быть 1 для несингулярности.
        state    : начальное состояние [s_{L - 1}, s_{L - 2}, ..., s_1, s_0] (L элементов, каждый 0 / 1)
        """
        self.c = c_coeffs          # коэффициенты c1..cL
        self.L = len(c_coeffs)     # длина LFSR
        assert self.L == len(state), "Длина состояния должна совпадать с L"
        assert c_coeffs[-1] == 1, "Многочлен должен быть несингулярным (cL = 1)"
        
        self.state = list(state)   # текущее состояние [s_{L - 1}, ..., s_0]
    
    def next_bit(self) -> int:
        """
        Выполняет один такт работы LFSR:
        1) Выводит s0 (младший бит состояния)
        2) Вычисляет новый бит обратной связи
        3) Сдвигает состояние
        """
        # Шаг 4.1: выходной бит = s0 (последний элемент состояния)
        output_bit = self.state[-1]
        
        # Шаг 4.3: вычисляем feedback bit = сумма c_i * s_{L - i} по mod2
        # В состоянии: state[0] = s_{L - 1}, state[1] = s_{L - 2}, ..., state[L - 1] = s_0
        # feedback = c1 * s_{L - 1} + c2 * s_{L - 2} + ... + cL * s_0 (mod 2)
        feedback = 0
        for i in range(self.L):
            feedback ^= (self.c[i] & self.state[i])
        
        # Шаг 4.2: сдвиг вправо (от s_{L - 1} к s_0)
        # Новое состояние = [feedback, s_{L - 1}, s_{L - 2}, ..., s_1]
        self.state = [feedback] + self.state[:-1]
        
        return output_bit
    
    def generate_sequence(self, n_bits: int) -> list[int]:
        """Генерирует n_bits битов выходной последовательности."""
        return [self.next_bit() for _ in range(n_bits)]
    
    def find_period(self, max_steps: int = 10000) -> int:
        """
        Находит период выходной последовательности,
        начиная с текущего состояния.
        """
        # Сохраняем начальное состояние
        start_state = tuple(self.state)
        # Словарь: состояние -> номер такта
        seen = {start_state: 0}
        
        sequence = []
        for t in range(1, max_steps + 1):
            bit = self.next_bit()
            sequence.append(bit)
            state_tuple = tuple(self.state)
            if state_tuple in seen:
                period = t - seen[state_tuple]
                # Восстанавливаем состояние
                self.state = list(start_state)
                return period
            seen[state_tuple] = t
        
        self.state = list(start_state)
        return -1  # период не найден


def check_maximum_period(c_coeffs: list[int], verbose: bool = True) -> bool:
    """
    Проверяет, даёт ли LFSR с данными коэффициентами
    максимальный период 2 ^ L - 1 для ненулевых начальных состояний.
    """
    L = len(c_coeffs)
    max_possible = (1 << L) - 1
    if verbose:
        print(f"L = {L}, максимальный период = {max_possible}")
    
    # Проверяем все ненулевые начальные состояния
    from itertools import product
    
    all_max = True
    for state in product([0, 1], repeat = L):
        if all(v == 0 for v in state):
            continue  # пропускаем нулевое состояние
        lfsr = LFSR(c_coeffs, list(state))
        period = lfsr.find_period(max_steps = 2 * max_possible)
        if period != max_possible:
            if verbose:
                print(f"  Состояние {state}: период {period} (не максимальный)")
            all_max = False
        elif verbose:
            print(f"  Состояние {state}: период {period} ✓")
    
    return all_max


def demonstrate_statistical_properties(c_coeffs: list[int], state: list[int]):
    """
    Демонстрирует статистические свойства из вашего текста:
    для максимальной длины LFSR и k <= L - 1 подпоследовательности
    длины k распределены почти равномерно.
    """
    lfsr = LFSR(c_coeffs, state)
    L = lfsr.L
    period = lfsr.find_period()
    
    print(f"Длина L = {L}, период = {period}")
    
    # Генерируем один полный период + немного
    full_sequence = lfsr.generate_sequence(period + L)
    
    for k in range(1, L):
        # Считаем все подпоследовательности длины k
        from collections import defaultdict
        counts = defaultdict(int)
        total_windows = period + L - k
        for i in range(total_windows):
            window = tuple(full_sequence[i:i + k])
            counts[window] += 1
        
        # Ожидаемые значения
        expected_nonzero = 1 << (L - k)      # для ненулевых
        expected_zero = (1 << (L - k)) - 1   # для нулевой
        
        print(f"\nk = {k}:")
        print(f"  Нулевая последовательность {tuple([0] * k)}: получено {counts[tuple([0] * k)]}, ожидается ~{expected_zero}")
        
        # Покажем несколько ненулевых
        nonzero_counts = [cnt for pat, cnt in counts.items() if any(pat)]
        if nonzero_counts:
            print(f"  Остальные {len(nonzero_counts)} ненулевых последовательностей:")
            print(f"    минимум {min(nonzero_counts)}, максимум {max(nonzero_counts)}, ожидается ~{expected_nonzero}")


if __name__ == "__main__":
    # Пример 59 из текста: L = 4, c(D) = 1 + D + D ^ 4 => c1 = 1, c2 = 0, c3 = 0, c4 = 1
    c = [1, 0, 0, 1]
    state = [0, 1, 1, 0]  # [s3, s2, s1, s0]
    
    print("=" * 60)
    print("Пример из текста (максимальный период 15)")
    lfsr = LFSR(c, state)
    seq = lfsr.generate_sequence(20)
    print(f"Первые 20 битов: {seq}")
    print(f"Период: {lfsr.find_period()}")
    
    # Проверка, что для всех ненулевых состояний период максимальный
    print("\n" + "=" * 60)
    print("Проверка максимальности периода для всех ненулевых состояний:")
    check_maximum_period(c, verbose = False)
    
    # Демонстрация статистических свойств
    print("\n" + "=" * 60)
    print("Статистические свойства (подпоследовательности):")
    demonstrate_statistical_properties(c, state)
    
    # Пример с НЕ примитивным многочленом (пример 58)
    print("\n" + "=" * 60)
    print("Пример с непрмитивным (приводимым) многочленом:")
    c_bad = [1, 0, 1, 1]  # 1 + D + D ^ 3 + D ^ 4 = (1 + D ^ 3)(1 + D)
    state_bad = [0, 1, 0, 1]
    lfsr_bad = LFSR(c_bad, state_bad)
    seq_bad = lfsr_bad.generate_sequence(20)
    print(f"Многочлен: 1 + D + D ^ 3 + D ^ 4")
    print(f"Первые 20 битов: {seq_bad}")
    print(f"Период: {lfsr_bad.find_period()} (ожидается 2)")