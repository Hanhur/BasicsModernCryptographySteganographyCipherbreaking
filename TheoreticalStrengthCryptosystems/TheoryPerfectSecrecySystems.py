# Теория систем с совершенной секретностью
from itertools import product
from collections import defaultdict

class CryptoSytem:
    """
    Модель криптосистемы для проверки совершенной секретности.
    """
    def __init__(self, messages, keys, encrypt_func):
        """
        :param messages: список сообщений (строки)
        :param keys: список ключей (строки или числа)
        :param encrypt_func: функция шифрования f(M, K) -> E (строка)
        """
        self.messages = messages
        self.keys = keys
        self.encrypt = encrypt_func
        
        # Генерируем все возможные пары (M, K) и соответствующие шифротексты
        self.pairs = list(product(messages, keys))
        self.cryptograms = [self.encrypt(m, k) for m, k in self.pairs]  # ИСПРАВЛЕНО!
        self.unique_cryptograms = list(set(self.cryptograms))
        
        # Количество
        self.m = len(messages)
        self.n = len(keys)
        self.k = len(self.unique_cryptograms)
        
        print(f"Сообщений (m) = {self.m}, Ключей (n) = {self.n}, Шифротекстов (k) = {self.k}")
        print(f"Условие Шеннона (n >= m): {self.n >= self.m}")
        
    def set_prior_probabilities(self, prior_probs):
        """
        Устанавливает априорное распределение P(M) на сообщениях.
        :param prior_probs: список вероятностей, сумма == 1
        """
        assert len(prior_probs) == self.m, "Длина списка вероятностей должна совпадать с числом сообщений"
        assert abs(sum(prior_probs) - 1.0) < 1e-9, "Сумма вероятностей должна быть равна 1"
        self.P_M = {msg: prob for msg, prob in zip(self.messages, prior_probs)}
        
        # Вычисляем P(E) - полную вероятность каждого шифротекста
        self.P_E = {e: 0.0 for e in self.unique_cryptograms}
        for (m, k), e in zip(self.pairs, self.cryptograms):
            self.P_E[e] += self.P_M[m] * (1.0 / self.n)  # считаем ключи равновероятными
        
        # Вычисляем P(E|M) и P(M|E)
        self.P_E_given_M = {}
        self.P_M_given_E = {}
        
        for m in self.messages:
            for e in self.unique_cryptograms:
                # Сколько ключей для данного M дают шифротекст e?
                count_keys = sum(1 for k in self.keys if self.encrypt(m, k) == e)
                # P(E|M) = (число ключей, дающих E) / (общее число ключей)
                self.P_E_given_M[(m, e)] = count_keys / self.n
                
                # P(M|E) по формуле Байеса
                if self.P_E[e] > 0:
                    self.P_M_given_E[(m, e)] = (self.P_M[m] * self.P_E_given_M[(m, e)]) / self.P_E[e]
                else:
                    self.P_M_given_E[(m, e)] = 0.0
                    
    def check_perfect_secrecy(self):
        """
        Проверяет условие совершенной секретности:
        P(M_i | E_j) == P(M_i) для всех i, j, где P(E_j) > 0
        """
        perfect = True
        violations = []
        for m in self.messages:
            for e in self.unique_cryptograms:
                if self.P_E[e] > 0:
                    a_posteriori = self.P_M_given_E[(m, e)]
                    a_priori = self.P_M[m]
                    if abs(a_posteriori - a_priori) > 1e-9:
                        perfect = False
                        violations.append((m, e, a_priori, a_posteriori))
        return perfect, violations
    
    def display_probabilities(self):
        """Выводит таблицы вероятностей."""
        print("\n" + "=" * 60)
        print("Априорные вероятности P(M):")
        for m in self.messages:
            print(f"  P({m}) = {self.P_M[m]:.6f}")
        
        print("\nВероятности шифротекстов P(E):")
        for e in self.unique_cryptograms:
            print(f"  P({e}) = {self.P_E[e]:.6f}")
        
        print("\nУсловные вероятности P(M|E) (апостериорные):")
        
        # Определяем ширину столбцов для форматирования
        col_width = 12
        # Заголовок
        header = f"{'M \\ E':<{col_width}}"
        for e in self.unique_cryptograms:
            header += f"{e:<{col_width}}"
        print(header)
        print("-" * len(header))
        
        # Строки данных
        for m in self.messages:
            row = f"{m:<{col_width}}"
            for e in self.unique_cryptograms:
                if self.P_E[e] > 0:
                    val = self.P_M_given_E[(m, e)]
                    row += f"{val:<{col_width}.6f}"
                else:
                    row += f"{'---':<{col_width}}"
            print(row)
        
        # Проверка совершенной секретности
        perfect, violations = self.check_perfect_secrecy()
        print("\n" + "=" * 60)
        if perfect:
            print("✅ СИСТЕМА ЯВЛЯЕТСЯ СОВЕРШЕННО СЕКРЕТНОЙ (условие (7.1) выполнено)")
        else:
            print("❌ СИСТЕМА НЕ ЯВЛЯЕТСЯ СОВЕРШЕННО СЕКРЕТНОЙ")
            print("Нарушения (M, E, P(M), P(M|E)):")
            for m, e, prior, post in violations[:5]:
                print(f"  M = {m}, E = {e}: P(M) = {prior:.6f}, P(M|E) = {post:.6f}")


# ============================================================
# Пример 1: СОВЕРШЕННАЯ СИСТЕМА (|K| >= |M|)
# ============================================================
print("=" * 60)
print("ПРИМЕР 1: СОВЕРШЕННАЯ СИСТЕМА (одноразовый блокнот)")
print("=" * 60)

def encrypt_perfect(m, k):
    """Шифрование: сообщение и ключ — числа, шифротекст = сумма по модулю."""
    return str((int(m) + int(k)) % 3)

messages1 = ["0", "1", "2"]          # m = 3
keys1 = ["0", "1", "2"]              # n = 3 (n >= m)

sys1 = CryptoSytem(messages1, keys1, encrypt_perfect)
sys1.set_prior_probabilities([0.2, 0.3, 0.5])  # априорные вероятности
sys1.display_probabilities()


# ============================================================
# Пример 2: НЕСОВЕРШЕННАЯ СИСТЕМА (|K| < |M|)
# ============================================================
print("\n\n" + "=" * 60)
print("ПРИМЕР 2: НЕСОВЕРШЕННАЯ СИСТЕМА (ключей меньше сообщений)")
print("=" * 60)

def encrypt_bad(m, k):
    """Плохое шифрование: ключ просто добавляется, но ключей мало."""
    return str((int(m) + int(k)) % 3)

messages2 = ["0", "1", "2", "3"]     # m = 4
keys2 = ["0", "1"]                   # n = 2 (n < m)

sys2 = CryptoSytem(messages2, keys2, encrypt_bad)
sys2.set_prior_probabilities([0.1, 0.2, 0.3, 0.4])
sys2.display_probabilities()


# ============================================================
# Пример 3: СОВЕРШЕННАЯ СИСТЕМА с XOR
# ============================================================
print("\n\n" + "=" * 60)
print("ПРИМЕР 3: СОВЕРШЕННАЯ СИСТЕМА (XOR)")
print("=" * 60)

def encrypt_xor(m, k):
    """XOR для битовых строк (длина 2 бита)."""
    return format(int(m, 2) ^ int(k, 2), '02b')

messages3 = ["00", "01", "10", "11"]   # m = 4
keys3 = ["00", "01", "10", "11"]       # n = 4

sys3 = CryptoSytem(messages3, keys3, encrypt_xor)
sys3.set_prior_probabilities([0.4, 0.3, 0.2, 0.1])
sys3.display_probabilities()


# ============================================================
# Пример 4: СЛОЖНЫЙ СЛУЧАЙ - проверка теоремы 7.1
# ============================================================
print("\n\n" + "=" * 60)
print("ПРИМЕР 4: ПРОВЕРКА ТЕОРЕМЫ 7.1 (P(E|M) = P(E))")
print("=" * 60)

def encrypt_complex(m, k):
    """Более сложное шифрование."""
    return chr((ord(m) + ord(k)) % 256)

messages4 = ["A", "B", "C"]          # m = 3
keys4 = ["X", "Y", "Z"]              # n = 3

sys4 = CryptoSytem(messages4, keys4, encrypt_complex)
sys4.set_prior_probabilities([0.5, 0.3, 0.2])

# Дополнительно проверяем равенство P(E|M) = P(E)
print("\nПроверка равенства P(E|M) = P(E) (теорема 7.1):")
for m in messages4:
    for e in sys4.unique_cryptograms:
        if sys4.P_E[e] > 0:
            p_e_given_m = sys4.P_E_given_M[(m, e)]
            p_e = sys4.P_E[e]
            if abs(p_e_given_m - p_e) < 1e-9:
                print(f"  ✅ P({e}|{m}) = {p_e_given_m:.6f} = P({e}) = {p_e:.6f}")
            else:
                print(f"  ❌ P({e}|{m}) = {p_e_given_m:.6f} ≠ P({e}) = {p_e:.6f}")

sys4.display_probabilities()