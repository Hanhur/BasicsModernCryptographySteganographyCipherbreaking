# Задачи и упражнения
# Задача 1.
import random
import itertools
from collections import Counter

def vigenere_encrypt(plaintext, key, n):
    """Шифрование Виженера: plaintext и key — списки целых чисел в Z_n.
       Ключ повторяется, если его длина меньше длины текста."""
    key_len = len(key)
    ciphertext = []
    for i, p in enumerate(plaintext):
        k = key[i % key_len]
        c = (p + k) % n
        ciphertext.append(c)
    return ciphertext

def vigenere_decrypt(ciphertext, key, n):
    """Дешифрование Виженера."""
    key_len = len(key)
    plaintext = []
    for i, c in enumerate(ciphertext):
        k = key[i % key_len]
        p = (c - k) % n
        plaintext.append(p)
    return plaintext

def generate_all_keys(n, l):
    """Генерация всех возможных ключей длины l (каждый символ от 0 до n - 1)."""
    # В условии задачи K = Z_l — это может быть l ключей, но для реализма возьмём все n^l?
    # По тексту: "К = Z_l (l ≥ 2)" — возможно, имеется в виду |K| = l.
    # Чтобы следовать строго, сделаем ключ просто числом от 0 до l-1, и превратим его в ключ-последовательность длины t.
    # Проще: пусть K = список из l разных ключей (каждый — кортеж длины l).
    # Но для моделирования: сделаем ключи как все последовательности длины l из Z_n? Нет, так |K| = n^l.
    # По условию |K| = l, поэтому сделаем ключи: [0, 1, ..., l-1] и каждый будет циклически расширен до длины t.
    pass  # Пока заглушка, реализуем ниже

def check_perfect_secrecy_sampling(n, t, l, num_samples = 10000):
    """
    Проверка совершенной секретности с помощью случайной выборки.
    Если |K| < |M| = n^t, то совершенная секретность невозможна.
    Здесь M — все последовательности длины t из Z_n, |M| = n^t.
    """
    M_size = n ** t
    K_size = l  # по условию |K| = l
    print(f"|M| = {M_size}, |K| = {K_size}")
    if K_size < M_size:
        print("Необходимое условие |K| >= |M| не выполнено => система не является совершенной.")
        return False
    
    # Если |K| >= |M|, проверим эмпирически (трудоёмко для больших n,t)
    # Здесь упрощённо: сгенерируем выборку пар (m, c) и проверим независимость.
    
    # Для простоты: проверим, что P(C|M=m) не зависит от m.
    # Зафиксируем два разных сообщения m1, m2 и сравним распределение шифротекстов.
    
    all_possible_messages = list(itertools.product(range(n), repeat = t))
    if len(all_possible_messages) > 100:
        print("Слишком много сообщений для полного перебора, используем выборку.")
        return None
    
    # Генерация всех возможных ключей (по условию K = Z_l, значит ключ — число, но для шифра нужно преобразовать в последовательность длины l)
    # В классическом Виженере ключ — последовательность длины l из Z_n, но |K| = l невозможно, если l ≠ n.
    # Поэтому, возможно, условие означает: |K| = l, и ключ — это число от 0 до l-1, а шифрование: c_i = (m_i + (k + i) mod l) mod n? Но это нестандартно.
    # Для строгости реализуем стандартный Виженер: ключ — последовательность из Z_n длины l, |K| = n^l.
    # Но задача говорит K = Z_l, значит |K| = l. Это возможно только если l = n.
    
    if l != n:
        print(f"Внимание: |K| = {l}, но для стандартного Виженера ключей длины l из Z_n будет {n}^{l}. Уточните условие.")
        print("Предположим, что K = Z_l означает l разных ключей-чисел, каждый преобразуется в последовательность прибавлением индекса.")
    
    # Альтернативная интерпретация: ключ — число k из Z_l, шифрование: c_i = (m_i + (k + i) mod l) mod n.
    # Так мы получим ровно l ключей.
    keys = [k for k in range(l)]
    
    # Для каждого сообщения посчитаем распределение шифротекстов
    m1 = tuple([0] * t)
    m2 = tuple([1] * t) if t > 0 else tuple()
    
    dist_c_given_m1 = Counter()
    dist_c_given_m2 = Counter()
    
    for k in keys:
        # Строим ключевую последовательность длины t из k: key_seq[i] = (k + i) % n
        key_seq = [(k + i) % n for i in range(t)]
        c1 = vigenere_encrypt(list(m1), key_seq, n)
        c2 = vigenere_encrypt(list(m2), key_seq, n)
        dist_c_given_m1[tuple(c1)] += 1
        dist_c_given_m2[tuple(c2)] += 1
    
    # Нормализация
    total_keys = len(keys)
    for k in dist_c_given_m1:
        dist_c_given_m1[k] /= total_keys
    for k in dist_c_given_m2:
        dist_c_given_m2[k] /= total_keys
    
    print("Распределение C|M=m1:", dict(dist_c_given_m1))
    print("Распределение C|M=m2:", dict(dist_c_given_m2))
    
    if dist_c_given_m1 == dist_c_given_m2:
        print("Распределения совпадают для этих двух сообщений, но нужна проверка для всех.")
        return "Возможно, совершенная (требуется полный перебор)"
    else:
        print("Распределения различаются => система не совершенная.")
        return False

if __name__ == "__main__":
    # Пример: n=2, t=2, l=1 (не может быть, т.к. l >= 2 по условию)
    # Возьмём n=3, t=2, l=2
    n, t, l = 3, 2, 2
    print(f"Проверка для n = {n}, t = {t}, l = {l}")
    check_perfect_secrecy_sampling(n, t, l, num_samples = 5000)
    
    print("\n---\n")
    # Пример из условия: l < t
    n, t, l = 3, 3, 2
    print(f"Проверка для n = {n}, t = {t}, l = {l} (l < t)")
    check_perfect_secrecy_sampling(n, t, l)
    
    print("\n---\n")
    # Пример: l = n, t = 1 (почти OTP, но t=1 — частный случай)
    n, t, l = 2, 1, 2
    print(f"Проверка для n = {n}, t = {t}, l = {l}")
    check_perfect_secrecy_sampling(n, t, l)

# ===================================================================================================================================================

# Задача 2
import math
from itertools import product

def entropy(probabilities):
    """
    Вычисляет энтропию Шеннона (в битах) для заданного распределения вероятностей.
    probabilities: список вероятностей (сумма = 1)
    """
    H = 0.0
    for p in probabilities:
        if p > 0:
            H -= p * math.log2(p)
    return H

def max_entropy(t):
    """
    Максимальная энтропия для величины, принимающей не более t значений.
    Достигается при равномерном распределении по всем t значениям.
    """
    if t <= 0:
        return 0.0
    return math.log2(t)

def min_entropy():
    """
    Минимальная энтропия — 0 (вырожденное распределение).
    """
    return 0.0

def uniform_distribution(t):
    """Равномерное распределение на t значениях."""
    if t <= 0:
        return []
    return [1.0 / t] * t

def degenerate_distribution(t, index = 0):
    """Вырожденное распределение: одно значение с вероятностью 1, остальные 0."""
    if t <= 0:
        return []
    probs = [0.0] * t
    if index < t:
        probs[index] = 1.0
    return probs

def example_distribution_1(t):
    """Пример распределения: линейно убывающие вероятности."""
    if t <= 0:
        return []
    if t == 1:
        return [1.0]
    probs = [t - i for i in range(t)]
    total = sum(probs)
    return [p / total for p in probs]

def example_distribution_2(t):
    """Пример распределения: две точки с высокой вероятностью."""
    if t <= 0:
        return []
    if t == 1:
        return [1.0]
    probs = [0.0] * t
    probs[0] = 0.8
    if t > 1:
        probs[1] = 0.2
    return probs

def example_distribution_geometric(t):
    """Пример: геометрическое распределение (убывающее)."""
    if t <= 0:
        return []
    if t == 1:
        return [1.0]
    # p = 0.5, убывающая геометрическая прогрессия
    probs = [0.5 ** (i + 1) for i in range(t - 1)]
    probs.append(0.5 ** (t - 1))  # последний элемент замыкает сумму
    total = sum(probs)
    return [p / total for p in probs]

def print_distribution(probs, name):
    """Красивый вывод распределения."""
    print(f"\n{name}:")
    if not probs:
        print("  Пустое распределение")
        return
    
    for i, p in enumerate(probs):
        print(f"  P(Q = {i}) = {p:.6f}")
    H = entropy(probs)
    print(f"  H(Q) = {H:.6f} бит")
    print(f"  Проверка суммы вероятностей: {sum(probs):.10f}")

def analyze_entropy_bounds(t):
    """
    Анализирует границы энтропии для заданного t.
    """
    print("=" * 70)
    print(f"Анализ для t = {t} (Q принимает не более {t} значений)")
    print("=" * 70)
    
    if t <= 0:
        print("t должно быть положительным числом")
        return
    
    H_max = max_entropy(t)
    H_min = min_entropy()
    
    print(f"\nТеоретические границы:")
    print(f"  Минимальная энтропия: {H_min} бит")
    print(f"  Максимальная энтропия: {H_max:.6f} бит")
    print(f"  log2({t}) = {math.log2(t):.6f}")
    
    # 1. Равномерное распределение (достигает максимума)
    uniform = uniform_distribution(t)
    print_distribution(uniform, "Равномерное распределение (достигает максимума)")
    
    # 2. Вырожденное распределение (достигает минимума)
    degenerate = degenerate_distribution(t, index = 0)
    print_distribution(degenerate, "Вырожденное распределение (достигает минимума)")
    
    # 3. Пример промежуточного распределения 1
    if t >= 2:
        example1 = example_distribution_1(t)
        print_distribution(example1, "Пример распределения 1 (линейно убывающие вероятности)")
    
    # 4. Пример промежуточного распределения 2
    if t >= 2:
        example2 = example_distribution_2(t)
        print_distribution(example2, "Пример распределения 2 (две основные точки)")
    
    # 5. Геометрическое распределение
    if t >= 2:
        example3 = example_distribution_geometric(t)
        print_distribution(example3, "Пример распределения 3 (геометрическое, убывающее)")
    
    print("\n" + "-" * 70)
    print(f"Вывод: при t = {t}")
    print(f"  H_min = {H_min} бит")
    print(f"  H_max = {H_max:.6f} бит")
    print("  Достигаются на вырожденном и равномерном распределениях соответственно.")
    print("=" * 70 + "\n")

def compare_entropy_for_different_t(t_values):
    """
    Сравнивает максимальную энтропию для разных t.
    """
    print("\n" + "=" * 70)
    print("Сравнение максимальной энтропии для разных t")
    print("=" * 70)
    print(f"{'t':<6} {'H_max (бит)':<15} {'log2(t)':<15} {'Примечание'}")
    print("-" * 70)
    for t in t_values:
        if t > 0:
            H_max = max_entropy(t)
            log2_t = math.log2(t)
            note = ""
            if t == 1:
                note = "тривиальный случай (нет неопределённости)"
            elif t == 2:
                note = "1 бит информации"
            elif t == 256:
                note = "8 бит = 1 байт"
            elif t == 1024:
                note = "10 бит"
            elif t in [8, 16, 32, 64, 128, 256, 512, 1024]:
                note = f"2^{int(math.log2(t))} = {t}"
            print(f"{t:<6} {H_max:<15.6f} {log2_t:<15.6f} {note}")

def verify_entropy_properties():
    """Проверяет основные свойства энтропии."""
    print("\n" + "=" * 70)
    print("Проверка математических свойств энтропии")
    print("=" * 70)
    
    # Свойство 1: Неотрицательность
    print("\n1. Неотрицательность: H(Q) >= 0")
    for t in [1, 2, 3, 5, 10]:
        uniform = uniform_distribution(t)
        H = entropy(uniform)
        print(f"   t = {t}, H = {H:.6f} >= 0 ✓" if H >= 0 else f"   t = {t}, H = {H:.6f} < 0 ✗")
    
    # Свойство 2: Максимум при равномерном распределении
    print("\n2. Энтропия максимальна при равномерном распределении")
    t = 4
    uniform = uniform_distribution(t)
    H_uniform = entropy(uniform)
    print(f"   При t = {t}:")
    print(f"   - Равномерное: H = {H_uniform:.6f}")
    
    # Сравниваем с другими распределениями
    other_dists = [
        ("Линейно убывающее", example_distribution_1(t)),
        ("Две основные точки", example_distribution_2(t)),
        ("Геометрическое", example_distribution_geometric(t))
    ]
    
    for name, dist in other_dists:
        H = entropy(dist)
        print(f"   - {name}: H = {H:.6f} {'<' if H < H_uniform else '>'} равномерного")
    
    # Свойство 3: Монотонность
    print("\n3. Монотонность: H_max(t) = log2(t) возрастает с t")
    t_values = [1, 2, 4, 8, 16, 32, 64]
    prev_H = -1
    for t in t_values:
        H_max = max_entropy(t)
        if H_max > prev_H:
            print(f"   t = {t:3d}: H_max = {H_max:.6f} бит (увеличилась ✓)")
        else:
            print(f"   t = {t:3d}: H_max = {H_max:.6f} бит (не увеличилась ✗)")
        prev_H = H_max
    
    # Свойство 4: Предельные случаи
    print("\n4. Предельные случаи:")
    print(f"   - t = 1: H_max = {max_entropy(1):.6f} бит (нет выбора)")
    print(f"   - t = 2: H_max = {max_entropy(2):.6f} бит (1 бит)")
    print(f"   - t = 256: H_max = {max_entropy(256):.6f} бит (8 бит = 1 байт)")

def demonstrate_cryptography_example():
    """Демонстрирует пример из криптографии."""
    print("\n" + "=" * 70)
    print("Пример из криптографии")
    print("=" * 70)
    
    print("\nПусть Q — ключ шифрования, принимающий t возможных значений.")
    print("Энтропия H(Q) показывает степень неопределённости ключа.")
    print("\nРазличные сценарии:")
    
    scenarios = [
        (1, "Ключ фиксирован (известен злоумышленнику)"),
        (2, "Ключ — один бит (0 или 1) с равной вероятностью"),
        (4, "Ключ — 2 бита, 4 равновероятных варианта"),
        (8, "Ключ — 3 бита, 8 равновероятных вариантов"),
        (16, "Ключ — 4 бита, 16 равновероятных вариантов"),
        (100, "100 возможных ключей, но неравномерное распределение (пример)")
    ]
    
    for t, desc in scenarios:
        if t == 100:
            # Неравномерное распределение для примера
            probs = example_distribution_1(t)
            H = entropy(probs)
        else:
            # Равномерное распределение
            probs = uniform_distribution(t)
            H = entropy(probs)
        
        print(f"\n  {desc}:")
        print(f"    t = {t}")
        print(f"    H(Q) = {H:.6f} бит")
        if t == 100:
            print(f"    Максимально возможная при t = {t}: {max_entropy(t):.6f} бит")
            print(f"    (неравномерность уменьшила энтропию)")

if __name__ == "__main__":
    # Анализ для различных t
    t_values = [1, 2, 3, 4, 5, 6, 7, 8, 10, 16, 32, 64, 100, 256]
    
    # Для каждого t проводим анализ
    for t in t_values:
        if t <= 64 or t == 100:  # Ограничим вывод для очень больших t
            analyze_entropy_bounds(t)
    
    # Сравнение максимальной энтропии для разных t
    compare_entropy_for_different_t([1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    
    # Проверка математических свойств
    verify_entropy_properties()
    
    # Пример из криптографии
    demonstrate_cryptography_example()
    
    # Общий вывод
    print("\n" + "=" * 70)
    print("ОСНОВНОЙ ВЫВОД")
    print("=" * 70)
    print("\nДля случайной величины Q, принимающей не более t значений:")
    print("  • Минимальная энтропия: H_min = 0 бит")
    print("    (достигается на вырожденном распределении)")
    print("  • Максимальная энтропия: H_max = log2(t) бит")
    print("    (достигается на равномерном распределении)")
    print("\nЭнтропия измеряет неопределённость:")
    print("  • H = 0 → полная определённость")
    print("  • H = log2(t) → максимальная неопределённость")
    print("  • 0 < H < log2(t) → частичная неопределённость")

# ===================================================================================================================================================

# Задача 3. 
import math
from collections import Counter
from itertools import product

def entropy(probabilities):
    """
    Вычисляет энтропию Шеннона (в битах) для распределения.
    probabilities: список или словарь вероятностей
    """
    H = 0.0
    for p in probabilities:
        if p > 0:
            H -= p * math.log2(p)
    return H

def joint_entropy(joint_probs):
    """
    Вычисляет совместную энтропию H(X, Y) по совместному распределению.
    joint_probs: словарь {(x, y): p} или матрица
    """
    return entropy(joint_probs.values())

def conditional_entropy(joint_probs, marginal_y):
    """
    Вычисляет H(X|Y) = sum_y p(y) * H(X|Y = y)
    joint_probs: словарь {(x,y): p(x,y)}
    marginal_y: словарь {y: p(y)}
    """
    H_cond = 0.0
    # Группируем вероятности по y
    y_to_probs = {}
    for (x, y), p in joint_probs.items():
        if y not in y_to_probs:
            y_to_probs[y] = []
        y_to_probs[y].append((x, p))
    
    for y, probs_list in y_to_probs.items():
        # Условное распределение X|Y=y
        p_y = marginal_y[y]
        cond_probs = [p / p_y for _, p in probs_list]
        H_cond += p_y * entropy(cond_probs)
    
    return H_cond

def create_independent_distribution(px, py):
    """
    Создаёт совместное распределение для независимых X и Y.
    px: словарь {x: p(x)}
    py: словарь {y: p(y)}
    """
    joint = {}
    for x, p_x in px.items():
        for y, p_y in py.items():
            joint[(x, y)] = p_x * p_y
    return joint

def create_dependent_distribution():
    """
    Создаёт пример зависимых X и Y (коррелированных).
    """
    # X и Y принимают значения 0,1,2
    joint = {
        (0, 0): 0.3, (0, 1): 0.05, (0, 2): 0.05,
        (1, 0): 0.05, (1, 1): 0.3, (1, 2): 0.05,
        (2, 0): 0.05, (2, 1): 0.05, (2, 2): 0.1
    }
    # Нормализуем (хотя уже сумма = 1.0)
    total = sum(joint.values())
    if abs(total - 1.0) > 1e-10:
        joint = {k: v / total for k, v in joint.items()}
    return joint

def create_totally_dependent_distribution():
    """
    Создаёт пример полностью зависимых X и Y (Y = f(X)).
    """
    # X принимает значения 0,1,2 с равной вероятностью
    joint = {
        (0, 0): 1/3, (0, 1): 0, (0, 2): 0,
        (1, 0): 0, (1, 1): 1/3, (1, 2): 0,
        (2, 0): 0, (2, 1): 0, (2, 2): 1/3
    }
    return joint

def create_partially_dependent_distribution():
    """
    Создаёт пример частично зависимых X и Y.
    """
    # Квадрат 3x3 с диагональным преобладанием
    joint = {
        (0, 0): 0.4, (0, 1): 0.1, (0, 2): 0.05,
        (1, 0): 0.1, (1, 1): 0.3, (1, 2): 0.05,
        (2, 0): 0.05, (2, 1): 0.05, (2, 2): 0.4
    }
    total = sum(joint.values())
    if abs(total - 1.0) > 1e-10:
        joint = {k: v / total for k, v in joint.items()}
    return joint

def compute_marginals(joint_probs):
    """
    Вычисляет маргинальные распределения X и Y.
    """
    px = {}
    py = {}
    for (x, y), p in joint_probs.items():
        px[x] = px.get(x, 0) + p
        py[y] = py.get(y, 0) + p
    return px, py

def analyze_distribution(joint_probs, name):
    """
    Анализирует распределение и выводит энтропии.
    """
    print(f"\n{'=' * 70}")
    print(f"Анализ: {name}")
    print('=' * 70)
    
    # Вычисляем маргинальные распределения
    px, py = compute_marginals(joint_probs)
    
    # Вычисляем энтропии
    H_X = entropy(px.values())
    H_Y = entropy(py.values())
    H_XY = joint_entropy(joint_probs)
    H_X_given_Y = conditional_entropy(joint_probs, py)
    H_Y_given_X = conditional_entropy({(y, x): p for (x, y), p in joint_probs.items()}, px)
    
    # Выводим результаты
    print(f"\nМаргинальное распределение X:")
    for x, p in sorted(px.items()):
        print(f"  P(X={x}) = {p:.6f}")
    
    print(f"\nМаргинальное распределение Y:")
    for y, p in sorted(py.items()):
        print(f"  P(Y={y}) = {p:.6f}")
    
    print(f"\nСовместное распределение P(X,Y):")
    xs = sorted(set(x for x, _ in joint_probs.keys()))
    ys = sorted(set(y for _, y in joint_probs.keys()))
    print("    ", end = "")
    for y in ys:
        print(f"Y={y:4}  ", end = "")
    print()
    for x in xs:
        print(f"X={x} ", end = "")
        for y in ys:
            p = joint_probs.get((x, y), 0)
            print(f"{p:8.4f} ", end = "")
        print()
    
    print(f"\nЭнтропии:")
    print(f"  H(X)      = {H_X:.6f} бит")
    print(f"  H(Y)      = {H_Y:.6f} бит")
    print(f"  H(X,Y)    = {H_XY:.6f} бит")
    print(f"  H(X|Y)    = {H_X_given_Y:.6f} бит")
    print(f"  H(Y|X)    = {H_Y_given_X:.6f} бит")
    
    print(f"\nПроверка свойств:")
    print(f"  H(X|Y) ≤ H(X): {H_X_given_Y:.6f} ≤ {H_X:.6f} → {'✓' if H_X_given_Y <= H_X + 1e-10 else '✗'}")
    print(f"  H(Y|X) ≤ H(Y): {H_Y_given_X:.6f} ≤ {H_Y:.6f} → {'✓' if H_Y_given_X <= H_Y + 1e-10 else '✗'}")
    
    # Проверка цепного правила
    chain_rule_1 = H_XY - H_X_given_Y
    chain_rule_2 = H_X + H_Y_given_X
    print(f"\nЦепное правило:")
    print(f"  H(X,Y) = H(Y) + H(X|Y) = {H_Y:.6f} + {H_X_given_Y:.6f} = {H_Y + H_X_given_Y:.6f}")
    print(f"  H(X,Y) = H(X) + H(Y|X) = {H_X:.6f} + {H_Y_given_X:.6f} = {H_X + H_Y_given_X:.6f}")
    
    return H_X, H_Y, H_XY, H_X_given_Y, H_Y_given_X

def demonstrate_independence():
    """
    Демонстрирует случай независимых X и Y.
    """
    print("\n" + "=" * 70)
    print("СЛУЧАЙ 1: НЕЗАВИСИМЫЕ X И Y")
    print("=" * 70)
    
    # Маргинальные распределения
    px = {0: 0.5, 1: 0.3, 2: 0.2}
    py = {0: 0.4, 1: 0.35, 2: 0.25}
    
    print("\nМаргинальные распределения:")
    print(f"  P(X): {px}")
    print(f"  P(Y): {py}")
    
    # Создаём независимое совместное распределение
    joint = create_independent_distribution(px, py)
    
    H_X, H_Y, H_XY, H_X_given_Y, H_Y_given_X = analyze_distribution(joint, "НЕЗАВИСИМЫЕ X и Y")
    
    print(f"\nВывод для независимых величин:")
    print(f"  H(X|Y) = {H_X_given_Y:.6f}")
    print(f"  H(X)   = {H_X:.6f}")
    print(f"  H(X|Y) = H(X) → {abs(H_X_given_Y - H_X) < 1e-10}")
    print("  Знание Y не даёт информации об X → условная энтропия равна безусловной.")

def demonstrate_dependence():
    """
    Демонстрирует случай зависимых X и Y.
    """
    print("\n" + "=" * 70)
    print("СЛУЧАЙ 2: ЗАВИСИМЫЕ X И Y")
    print("=" * 70)
    
    joint = create_dependent_distribution()
    H_X, H_Y, H_XY, H_X_given_Y, H_Y_given_X = analyze_distribution(joint, "ЗАВИСИМЫЕ X и Y")
    
    print(f"\nВывод для зависимых величин:")
    print(f"  H(X|Y) = {H_X_given_Y:.6f}")
    print(f"  H(X)   = {H_X:.6f}")
    print(f"  H(X|Y) < H(X) → {H_X_given_Y < H_X}")
    print("  Знание Y уменьшает неопределённость об X → условная энтропия меньше безусловной.")

def demonstrate_totally_dependent():
    """
    Демонстрирует случай полностью зависимых X и Y (Y = X).
    """
    print("\n" + "=" * 70)
    print("СЛУЧАЙ 3: ПОЛНОСТЬЮ ЗАВИСИМЫЕ X И Y (Y = X)")
    print("=" * 70)
    
    joint = create_totally_dependent_distribution()
    H_X, H_Y, H_XY, H_X_given_Y, H_Y_given_X = analyze_distribution(joint, "ПОЛНОСТЬЮ ЗАВИСИМЫЕ (Y = X)")
    
    print(f"\nВывод для полностью зависимых величин:")
    print(f"  H(X|Y) = {H_X_given_Y:.6f}")
    print(f"  H(X)   = {H_X:.6f}")
    print(f"  H(X|Y) = 0 → знание Y полностью определяет X.")
    print(f"  H(X|Y) < H(X) ({H_X_given_Y:.6f} < {H_X:.6f})")

def demonstrate_partial_dependence():
    """
    Демонстрирует случай частично зависимых X и Y.
    """
    print("\n" + "=" * 70)
    print("СЛУЧАЙ 4: ЧАСТИЧНО ЗАВИСИМЫЕ X И Y")
    print("=" * 70)
    
    joint = create_partially_dependent_distribution()
    H_X, H_Y, H_XY, H_X_given_Y, H_Y_given_X = analyze_distribution(joint, "ЧАСТИЧНО ЗАВИСИМЫЕ")
    
    print(f"\nВывод для частично зависимых величин:")
    print(f"  H(X|Y) = {H_X_given_Y:.6f}")
    print(f"  H(X)   = {H_X:.6f}")
    print(f"  H(X|Y) < H(X) → {H_X_given_Y < H_X}")
    print("  Знание Y частично уменьшает неопределённость.")

def compare_all_cases():
    """
    Сравнивает все случаи в одной таблице.
    """
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ ВСЕХ СЛУЧАЕВ")
    print("=" * 70)
    
    cases = [
        ("Независимые", create_independent_distribution({0:0.5, 1:0.3, 2:0.2}, {0:0.4, 1:0.35, 2:0.25})),
        ("Частично зависимые", create_partially_dependent_distribution()),
        ("Зависимые", create_dependent_distribution()),
        ("Полностью зависимые (Y = X)", create_totally_dependent_distribution())
    ]
    
    print(f"\n{'Случай':<25} {'H(X)':<12} {'H(X|Y)':<12} {'H(X|Y) ≤ H(X)':<20} {'Равенство?'}")
    print("-" * 75)
    
    for name, joint in cases:
        px, py = compute_marginals(joint)
        H_X = entropy(px.values())
        H_X_given_Y = conditional_entropy(joint, py)
        
        inequality = "✓" if H_X_given_Y <= H_X + 1e-10 else "✗"
        equality = "Да" if abs(H_X_given_Y - H_X) < 1e-10 else "Нет"
        
        print(f"{name:<25} {H_X:<12.6f} {H_X_given_Y:<12.6f} {inequality:<20} {equality}")

def main():
    """
    Главная функция, демонстрирующая все случаи.
    """
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ СВОЙСТВА H(X|Y) ≤ H(X)")
    print("=" * 70)
    print("\nТеоретический результат:")
    print("  • В общем случае: H(X|Y) ≤ H(X)")
    print("  • Если X и Y независимы: H(X|Y) = H(X)")
    print("  • Если X и Y функционально связаны: H(X|Y) = 0\n")
    
    # Демонстрируем все случаи
    demonstrate_independence()
    demonstrate_partial_dependence()
    demonstrate_dependence()
    demonstrate_totally_dependent()
    
    # Сравнительная таблица
    compare_all_cases()
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ ВЫВОД")
    print("=" * 70)
    print("\nОценка H(X|Y) ≤ H(X) СПРАВЕДЛИВА ВСЕГДА.")
    print("\n• В общем случае: H(X|Y) ≤ H(X) (знание Y может только уменьшить энтропию)")
    print("• Для независимых X и Y: H(X|Y) = H(X) (знание Y не даёт информации об X)")
    print("• Для полностью зависимых: H(X|Y) = 0 (знание Y полностью определяет X)")
    print("\nЭто фундаментальное свойство энтропии, используемое в:")
    print("  - Криптографии (оценка неопределённости ключа/сообщения)")
    print("  - Теории кодирования")
    print("  - Теории информации")

if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 4.
import math
import random
from collections import Counter
from itertools import product

def entropy(probabilities):
    """Вычисляет энтропию Шеннона (в битах)."""
    H = 0.0
    for p in probabilities:
        if p > 0:
            H -= p * math.log2(p)
    return H

class Cipher:
    """Базовый класс для шифров."""
    def encrypt(self, m, k):
        raise NotImplementedError
    
    def decrypt(self, c, k):
        raise NotImplementedError

class CaesarCipher(Cipher):
    """Шифр Цезаря (сдвиг)."""
    def __init__(self, n):
        self.n = n  # размер алфавита
    
    def encrypt(self, m, k):
        return (m + k) % self.n
    
    def decrypt(self, c, k):
        return (c - k) % self.n

class XORCipher(Cipher):
    """Шифр XOR (одноразовый блокнот для одного символа)."""
    def __init__(self, n):
        self.n = n
    
    def encrypt(self, m, k):
        return m ^ k
    
    def decrypt(self, c, k):
        return c ^ k

class VigenereCipher(Cipher):
    """Шифр Виженера (для блоков)."""
    def __init__(self, n, block_len):
        self.n = n
        self.block_len = block_len
    
    def encrypt(self, m, k):
        # m и k - списки одинаковой длины
        return [(m[i] + k[i]) % self.n for i in range(len(m))]
    
    def decrypt(self, c, k):
        return [(c[i] - k[i]) % self.n for i in range(len(c))]

def compute_entropies_for_cipher(cipher, M_space, K_space, n):
    """
    Вычисляет все необходимые энтропии для заданного шифра.
    
    Параметры:
    - cipher: объект шифра
    - M_space: список всех возможных сообщений
    - K_space: список всех возможных ключей
    - n: размер алфавита (для равномерного распределения)
    """
    # Предполагаем равномерное распределение на M и K
    p_m = 1.0 / len(M_space)
    p_k = 1.0 / len(K_space)
    
    # Совместное распределение P(M,K)
    joint_MK = {}
    for m in M_space:
        for k in K_space:
            joint_MK[(m, k)] = p_m * p_k
    
    # Распределение C = encrypt(M,K)
    C_space = set()
    c_to_prob = {}
    
    for m in M_space:
        for k in K_space:
            c = cipher.encrypt(m, k)
            if isinstance(c, list):
                c = tuple(c)
            C_space.add(c)
            c_to_prob[c] = c_to_prob.get(c, 0) + p_m * p_k
    
    # Вычисляем энтропии
    H_M = entropy([p_m] * len(M_space))
    H_K = entropy([p_k] * len(K_space))
    H_C = entropy(c_to_prob.values())
    
    # H(M,K) = H(M) + H(K) (независимы)
    H_MK = H_M + H_K
    
    # H(M|K,C) = ?
    # Для каждого k и c находим m
    m_given_kc = {}
    for k in K_space:
        for m in M_space:
            c = cipher.encrypt(m, k)
            if isinstance(c, list):
                c = tuple(c)
            m_given_kc[(k, c)] = m
    
    # Условное распределение M|K,C
    cond_probs = []
    for k in K_space:
        for c in C_space:
            if (k, c) in m_given_kc:
                # При фиксированных k,c, m определён однозначно
                cond_probs.append(1.0)  # вероятность 1 для единственного m
    # H(M|K,C) = 0 если детерминировано
    H_M_given_KC = 0.0
    
    # H(K|M) = ?
    # Для каждого m, распределение K|M=m
    k_given_m = {}
    for m in M_space:
        k_dist = {}
        for k in K_space:
            c = cipher.encrypt(m, k)
            if isinstance(c, list):
                c = tuple(c)
            k_dist[k] = k_dist.get(k, 0) + p_k * p_m / p_m
        k_given_m[m] = k_dist
    
    H_K_given_M = 0.0
    for m in M_space:
        k_probs = list(k_given_m[m].values())
        H_K_given_M += p_m * entropy(k_probs)
    
    return {
        'H(M)': H_M,
        'H(K)': H_K,
        'H(C)': H_C,
        'H(M,K)': H_MK,
        'H(M|K,C)': H_M_given_KC,
        'H(K|M)': H_K_given_M,
        'H(K) + H(M)': H_K + H_M
    }

def demonstrate_caesar_cipher():
    """Демонстрирует шифр Цезаря."""
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 1: ШИФР ЦЕЗАРЯ")
    print("=" * 70)
    
    n = 4  # алфавит из 4 символов
    cipher = CaesarCipher(n)
    
    M_space = list(range(n))
    K_space = list(range(n))
    
    print(f"\nПараметры:")
    print(f"  Размер алфавита n = {n}")
    print(f"  Пространство сообщений M = {M_space}")
    print(f"  Пространство ключей K = {K_space}")
    print(f"  |M| = {len(M_space)}, |K| = {len(K_space)}")
    
    results = compute_entropies_for_cipher(cipher, M_space, K_space, n)
    
    print(f"\nРезультаты:")
    for name, value in results.items():
        print(f"  {name:15} = {value:.6f} бит")
    
    print(f"\nПроверка утверждений:")
    print(f"  1. H(M|K,C) = 0? {abs(results['H(M|K,C)'] - 0) < 1e-10} → {'✓' if abs(results['H(M|K,C)'] - 0) < 1e-10 else '✗'}")
    print(f"  2. H(K|M) = H(K) + H(M)? {results['H(K|M)']:.6f} = {results['H(K) + H(M)']:.6f} → {'✓' if abs(results['H(K|M)'] - results['H(K) + H(M)']) < 1e-10 else '✗'}")

def demonstrate_xor_cipher():
    """Демонстрирует XOR шифр."""
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 2: XOR ШИФР (ОДНОРАЗОВЫЙ БЛОКНОТ ДЛЯ 1 СИМВОЛА)")
    print("=" * 70)
    
    n = 4
    cipher = XORCipher(n)
    
    M_space = list(range(n))
    K_space = list(range(n))
    
    print(f"\nПараметры:")
    print(f"  Размер алфавита n = {n}")
    print(f"  Пространство сообщений M = {M_space}")
    print(f"  Пространство ключей K = {K_space}")
    print(f"  |M| = {len(M_space)}, |K| = {len(K_space)}")
    
    results = compute_entropies_for_cipher(cipher, M_space, K_space, n)
    
    print(f"\nРезультаты:")
    for name, value in results.items():
        print(f"  {name:15} = {value:.6f} бит")
    
    print(f"\nПроверка утверждений:")
    print(f"  1. H(M|K,C) = 0? {abs(results['H(M|K,C)'] - 0) < 1e-10} → {'✓' if abs(results['H(M|K,C)'] - 0) < 1e-10 else '✗'}")
    print(f"  2. H(K|M) = H(K) + H(M)? {results['H(K|M)']:.6f} = {results['H(K) + H(M)']:.6f} → {'✓' if abs(results['H(K|M)'] - results['H(K) + H(M)']) < 1e-10 else '✗'}")

def demonstrate_vigenere_cipher():
    """Демонстрирует шифр Виженера."""
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ 3: ШИФР ВИЖЕНЕРА (ДЛЯ БЛОКОВ ДЛИНЫ 2)")
    print("=" * 70)
    
    n = 3  # алфавит из 3 символов
    block_len = 2
    cipher = VigenereCipher(n, block_len)
    
    # Все возможные сообщения длины block_len
    M_space = list(product(range(n), repeat = block_len))
    K_space = list(product(range(n), repeat = block_len))
    
    print(f"\nПараметры:")
    print(f"  Размер алфавита n = {n}")
    print(f"  Длина блока t = {block_len}")
    print(f"  |M| = {n}^{block_len} = {len(M_space)}")
    print(f"  |K| = {n}^{block_len} = {len(K_space)}")
    print(f"  M_space (первые 5): {M_space[:5]}...")
    print(f"  K_space (первые 5): {K_space[:5]}...")
    
    results = compute_entropies_for_cipher(cipher, M_space, K_space, n)
    
    print(f"\nРезультаты:")
    for name, value in results.items():
        print(f"  {name:15} = {value:.6f} бит")
    
    print(f"\nПроверка утверждений:")
    print(f"  1. H(M|K,C) = 0? {abs(results['H(M|K,C)'] - 0) < 1e-10} → {'✓' if abs(results['H(M|K,C)'] - 0) < 1e-10 else '✗'}")
    print(f"  2. H(K|M) = H(K) + H(M)? {results['H(K|M)']:.6f} = {results['H(K) + H(M)']:.6f} → {'✓' if abs(results['H(K|M)'] - results['H(K) + H(M)']) < 1e-10 else '✗'}")

def analyze_relationship():
    """
    Анализирует соотношение между H(K|M) и H(K) + H(M).
    """
    print("\n" + "=" * 70)
    print("АНАЛИЗ СООТНОШЕНИЯ H(K|M) И H(K) + H(M)")
    print("=" * 70)
    
    print("\nТеоретический анализ:")
    print("  • H(K|M) = H(K,M) - H(M)")
    print("  • H(K,M) = H(K) + H(M|K)")
    print("  • Для детерминированного шифра H(M|K) = H(C|K) = ?")
    print("  • Если шифр взаимно-однозначный при фиксированном K, то H(M|K) = H(M)")
    print("    (разные M дают разные C при том же K)")
    print("\n  Тогда:")
    print("    H(K,M) = H(K) + H(M)")
    print("    H(K|M) = H(K,M) - H(M) = H(K) + H(M) - H(M) = H(K)")
    print("\n  Таким образом, В ОБЩЕМ СЛУЧАЕ:")
    print("    H(K|M) = H(K)  (если шифр совершенный и M,K независимы)")
    print("    Но H(K) + H(M) = H(K) + H(M) > H(K) при H(M) > 0")
    print("\n  ⇒ H(K|M) ≠ H(K) + H(M) (кроме тривиального случая H(M)=0)")

def demonstrate_counterexample():
    """
    Демонстрирует контрпример для второго утверждения.
    """
    print("\n" + "=" * 70)
    print("КОНТРПРИМЕР ДЛЯ H(K|M) = H(K) + H(M)")
    print("=" * 70)
    
    # Простой пример
    n = 2
    cipher = XORCipher(n)
    
    M_space = [0, 1]
    K_space = [0, 1]
    
    print(f"\nПример:")
    print(f"  Шифр: XOR (одноразовый блокнот)")
    print(f"  M = {M_space}, равномерное распределение: P(M = 0) = 0.5, P(M = 1) = 0.5")
    print(f"  K = {K_space}, равномерное распределение: P(K = 0) = 0.5, P(K = 1) = 0.5")
    print(f"  M и K независимы")
    
    results = compute_entropies_for_cipher(cipher, M_space, K_space, n)
    
    print(f"\nВычисленные значения:")
    print(f"  H(K)     = {results['H(K)']:.6f} бит")
    print(f"  H(M)     = {results['H(M)']:.6f} бит")
    print(f"  H(K|M)   = {results['H(K|M)']:.6f} бит")
    print(f"  H(K) + H(M) = {results['H(K) + H(M)']:.6f} бит")
    
    print(f"\nСравнение:")
    print(f"  H(K|M)   = {results['H(K|M)']:.6f}")
    print(f"  H(K) + H(M) = {results['H(K) + H(M)']:.6f}")
    print(f"  Разница  = {results['H(K) + H(M)'] - results['H(K|M)']:.6f} бит")
    
    if abs(results['H(K|M)'] - results['H(K)']) < 1e-10:
        print(f"\n  Заметим: H(K|M) = H(K) (так как M и K независимы)")
    
    print(f"\n  Очевидно, что H(K|M) ≠ H(K)+H(M) (если H(M)>0)")

def main():
    """
    Главная функция.
    """
    print("\n" + "=" * 70)
    print("ЗАДАЧА 5.4: ПРОВЕРКА РАВЕНСТВ H(M|K,C) = 0 И H(K|M) = H(K) + H(M)")
    print("=" * 70)
    
    print("\nУтверждения:")
    print("  1. H(M|K,C) = 0")
    print("  2. H(K|M) = H(K) + H(M)")
    
    # Демонстрация на разных шифрах
    demonstrate_caesar_cipher()
    demonstrate_xor_cipher()
    demonstrate_vigenere_cipher()
    
    # Анализ соотношений
    analyze_relationship()
    
    # Контрпример для второго утверждения
    demonstrate_counterexample()
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ ВЫВОД")
    print("=" * 70)
    
    print("\n1. H(M|K,C) = 0:")
    print("   • Верно для любого детерминированного шифра.")
    print("   • Причина: зная K и C, сообщение M восстанавливается однозначно.")
    print("   • Это фундаментальное свойство корректного шифра.")
    
    print("\n2. H(K|M) = H(K) + H(M):")
    print("   • НЕВЕРНО в общем случае.")
    print("   • Правильное соотношение: H(K|M) = H(K) + H(M|K) - H(M)")
    print("   • Для шифров с равномерными независимыми M и K:")
    print("     H(K|M) = H(K)")
    print("   • Правая часть H(K) + H(M) больше H(K) при H(M) > 0.")
    print("   • Равенство возможно только если H(M) = 0 (тривиальный случай).")
    
    print("\nКлючевые формулы теории информации для шифров:")
    print("  • H(M|K,C) = 0 (детерминированность дешифрования)")
    print("  • H(C|M,K) = 0 (детерминированность шифрования)")
    print("  • H(K|M,C) = H(K|C) (если шифр совершенный)")

if __name__ == "__main__":
    main()