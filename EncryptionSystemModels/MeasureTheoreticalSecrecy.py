# 2. Мера теоретической секретности
from collections import Counter
import math

def entropy(prob_dist):
    """
    Вычисляет энтропию H(X) = -sum(p_i * log2(p_i))
    prob_dist: список вероятностей (сумма = 1)
    """
    return -sum(p * math.log2(p) for p in prob_dist if p > 0)

def entropy_from_data(data):
    """
    Вычисляет энтропию по выборочным данным.
    data: список значений
    """
    counts = Counter(data)
    total = len(data)
    prob_dist = [count / total for count in counts.values()]
    return entropy(prob_dist)

def conditional_entropy(joint_probs, x_vals, y_vals):
    """
    Вычисляет H(X|Y) = -sum_{x, y} p(x, y) * log2(p(x|y))
    joint_probs: словарь (x, y) -> p(x, y)
    """
    # Сначала вычислим p(y)
    p_y = {}
    for (x, y), p_xy in joint_probs.items():
        p_y[y] = p_y.get(y, 0) + p_xy
    
    h_x_given_y = 0.0
    for (x, y), p_xy in joint_probs.items():
        if p_y[y] > 0 and p_xy > 0:
            p_x_given_y = p_xy / p_y[y]
            h_x_given_y -= p_xy * math.log2(p_x_given_y)
    return h_x_given_y

def mutual_information(entropy_k, conditional_entropy_k_given_c):
    """
    I(K; C) = H(K) - H(K|C)
    """
    return entropy_k - conditional_entropy_k_given_c

class ShannonCipherSystem:
    """
    Модель системы шифрования для демонстрации теоремы Шеннона.
    """
    def __init__(self, messages, keys, ciphertexts):
        """
        messages: список возможных сообщений
        keys: список возможных ключей
        ciphertexts: список возможных шифровок
        """
        self.M = messages
        self.K = keys
        self.C = ciphertexts
        self.n = len(messages)
    
    def uniform_distribution(self, space):
        """Равномерное распределение на пространстве"""
        return {x: 1 / len(space) for x in space}
    
    def compute_entropies_and_redundancy(self, p_m, p_k, p_c_given_m_k):
        """
        Вычисляет все необходимые величины:
        - H(M), H(K), H(C)
        - H(K|C)
        - I(K;C)
        - D(M)
        - Проверка теоремы I(K;C) <= D(M)
        
        p_m: dict {message: probability}
        p_k: dict {key: probability}
        p_c_given_m_k: dict {(message, key): {ciphertext: probability}}
        """
        # Совместное распределение p(m,k,c) = p(m)*p(k)*p(c|m,k)
        joint = {}
        for m in self.M:
            for k in self.K:
                for c, p_c in p_c_given_m_k[(m, k)].items():
                    joint[(m, k, c)] = p_m[m] * p_k[k] * p_c
        
        # Маргинальные распределения
        p_marg_c = {}
        p_joint_k_c = {}
        
        for (m, k, c), prob in joint.items():
            p_marg_c[c] = p_marg_c.get(c, 0) + prob
            p_joint_k_c[(k, c)] = p_joint_k_c.get((k, c), 0) + prob
        
        # Энтропии
        H_M = entropy(list(p_m.values()))
        H_K = entropy(list(p_k.values()))
        H_C = entropy(list(p_marg_c.values()))
        
        # H(K|C) через совместное p(k,c)
        H_K_given_C = conditional_entropy(p_joint_k_c, self.K, self.C)
        
        # I(K;C)
        I_KC = mutual_information(H_K, H_K_given_C)
        
        # Избыточность D(M) = log|M| - H(M)
        log_M = math.log2(len(self.M))
        D_M = log_M - H_M
        
        print(f"H(M)   = {H_M:.4f} бит")
        print(f"H(K)   = {H_K:.4f} бит")
        print(f"H(C)   = {H_C:.4f} бит")
        print(f"H(K|C) = {H_K_given_C:.4f} бит")
        print(f"I(K;C) = {I_KC:.4f} бит")
        print(f"log|M|  = {log_M:.4f} бит")
        print(f"D(M)   = {D_M:.4f} бит (избыточность языка)")
        print(f"Проверка теоремы Шеннона: I(K;C) <= D(M) -> {I_KC <= D_M}")
        
        return {
            'H_M': H_M, 'H_K': H_K, 'H_C': H_C,
            'H_K_given_C': H_K_given_C, 'I_KC': I_KC, 'D_M': D_M
        }


def demo_ideal_cipher():
    """
    Демонстрация 1: совершенная система с равномерными распределениями.
    |M| = |C| = |K| = 4. Шифрование: c = (m + k) mod 4.
    """
    print("\n=== Демонстрация 1: Идеальная система (равномерные распределения) ===")
    
    M = [0, 1, 2, 3]
    K = [0, 1, 2, 3]
    C = [0, 1, 2, 3]
    
    system = ShannonCipherSystem(M, K, C)
    
    # Равномерные распределения
    p_m = system.uniform_distribution(M)
    p_k = system.uniform_distribution(K)
    
    # p(c|m,k) - детерминированное шифрование (совершенное)
    p_c_given = {}
    for m in M:
        for k in K:
            c = (m + k) % 4
            p_c_given[(m, k)] = {c: 1.0}
    
    system.compute_entropies_and_redundancy(p_m, p_k, p_c_given)


def demo_redundant_language():
    """
    Демонстрация 2: Язык с избыточностью (неравномерное распределение сообщений).
    """
    print("\n=== Демонстрация 2: Язык с избыточностью ===")
    
    M = ['A', 'B', 'C', 'D']
    K = [0, 1, 2, 3]
    C = ['00', '01', '10', '11']
    
    system = ShannonCipherSystem(M, K, C)
    
    # Неравномерное распределение сообщений (избыточность)
    p_m = {'A': 0.5, 'B': 0.25, 'C': 0.125, 'D': 0.125}
    # Ключи равномерны
    p_k = system.uniform_distribution(K)
    
    # Шифрование: отображение M x K -> C
    idx_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    rev_map = {0: '00', 1: '01', 2: '10', 3: '11'}
    
    p_c_given = {}
    for m in M:
        for k in K:
            c_idx = idx_map[m] ^ k
            c = rev_map[c_idx]
            p_c_given[(m, k)] = {c: 1.0}
    
    results = system.compute_entropies_and_redundancy(p_m, p_k, p_c_given)
    
    print("\nИнтерпретация: Избыточность языка D(M) > 0 позволяет")
    print("получить информацию о ключе I(K;C) > 0.")


def demo_low_redundancy():
    """
    Демонстрация 3: Низкая избыточность (почти равномерные сообщения).
    """
    print("\n=== Демонстрация 3: Низкая избыточность языка ===")
    
    M = [0, 1, 2, 3]
    K = [0, 1, 2, 3]
    C = [0, 1, 2, 3]
    
    system = ShannonCipherSystem(M, K, C)
    
    # Почти равномерные сообщения
    p_m = {0: 0.26, 1: 0.25, 2: 0.25, 3: 0.24}
    p_k = system.uniform_distribution(K)
    
    p_c_given = {}
    for m in M:
        for k in K:
            c = (m + k) % 4
            p_c_given[(m, k)] = {c: 1.0}
    
    results = system.compute_entropies_and_redundancy(p_m, p_k, p_c_given)


def demo_inequality_jensen():
    """
    Демонстрация неравенства Йенсена для энтропии.
    """
    print("\n=== Демонстрация неравенства Йенсена ===")
    
    # Покажем, что 0 <= H(Q) <= log(n)
    test_distributions = [
        [1.0, 0.0, 0.0, 0.0],  # детерминированная
        [0.5, 0.5, 0.0, 0.0],
        [0.25, 0.25, 0.25, 0.25],  # равномерная
        [0.5, 0.3, 0.1, 0.1]
    ]
    
    n = 4
    log_n = math.log2(n)
    
    print(f"Для n = {n}, log2(n) = {log_n:.4f} бит")
    for i, prob in enumerate(test_distributions):
        H = entropy(prob)
        print(f"Распределение {i + 1}: H = {H:.4f} бит, 0 <= H <= log(n): {0 <= H <= log_n}")


if __name__ == "__main__":
    demo_inequality_jensen()
    demo_ideal_cipher()
    demo_redundant_language()
    demo_low_redundancy()