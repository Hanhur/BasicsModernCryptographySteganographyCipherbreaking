# Доказательства с нулевым знанием
import random
import math
from typing import Dict, List, Tuple, Optional

# ============================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ RSA
# ============================================================

def gcd(a: int, b: int) -> int:
    """Наибольший общий делитель (алгоритм Евклида)"""
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a: int, m: int) -> int:
    """
    Обратное число по модулю m (расширенный алгоритм Евклида)
    """
    if gcd(a, m) != 1:
        raise ValueError(f"Число {a} не имеет обратного по модулю {m}")
    
    # Расширенный алгоритм Евклида
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    
    return x1 % m0

def is_prime(n: int, k: int = 5) -> bool:
    """Проверка на простоту (тест Миллера-Рабина)"""
    if n < 2:
        return False
    if n in [2, 3]:
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Проверяем k раз
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits: int = 8) -> int:
    """Генерация простого числа заданной битности"""
    while True:
        n = random.randint(2 ** (bits - 1), 2 ** bits - 1)
        if n % 2 == 0:
            continue
        if is_prime(n):
            return n

def generate_rsa_keys(bits: int = 8) -> Tuple[int, int, int]:
    """
    Генерация ключей RSA
    Возвращает: (public_key, private_key, modulus)
    где public_key = e, private_key = d
    """
    # Выбираем два простых числа
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (обычно 65537, но для маленьких чисел используем 3 или 17)
    e = 3
    while gcd(e, phi) != 1:
        e += 2
    
    d = mod_inverse(e, phi)
    return e, d, n

def rsa_encrypt(m: int, e: int, n: int) -> int:
    """Шифрование RSA: c = m ^ e mod n"""
    return pow(m, e, n)

def rsa_decrypt(c: int, d: int, n: int) -> int:
    """Дешифрование RSA: m = c ^ d mod n"""
    return pow(c, d, n)


# ============================================================
# 2. КЛАССЫ ДЛЯ ПРОТОКОЛА
# ============================================================

class Color:
    """Цвета для раскраски графа"""
    RED = 0
    BLUE = 1
    YELLOW = 2
    
    @staticmethod
    def to_string(color: int) -> str:
        mapping = {0: 'R (Красный)', 1: 'B (Синий)', 2: 'Y (Желтый)'}
        return mapping.get(color, 'Неизвестно')
    
    @staticmethod
    def to_short_string(color: int) -> str:
        mapping = {0: 'R', 1: 'B', 2: 'Y'}
        return mapping.get(color, '?')


class Graph:
    """Класс для представления графа"""
    
    def __init__(self, vertices: int, edges: List[Tuple[int, int]]):
        """
        Создание графа
        vertices: количество вершин (0..vertices-1)
        edges: список ребер (u, v)
        """
        self.n = vertices
        self.edges = edges
        self.adj_matrix = [[0] * vertices for _ in range(vertices)]
        for u, v in edges:
            self.adj_matrix[u][v] = 1
            self.adj_matrix[v][u] = 1
    
    def get_edges(self) -> List[Tuple[int, int]]:
        return self.edges
    
    def get_vertices(self) -> List[int]:
        return list(range(self.n))
    
    def is_valid_coloring(self, coloring: Dict[int, int]) -> bool:
        """Проверяет, является ли раскраска правильной"""
        for u, v in self.edges:
            if coloring[u] == coloring[v]:
                return False
        return True
    
    def print_graph(self):
        """Вывод графа в виде матрицы смежности"""
        print("Матрица смежности графа:")
        print("   " + " ".join(f"{i:2}" for i in range(self.n)))
        for i in range(self.n):
            print(f"{i:2} " + " ".join(f"{self.adj_matrix[i][j]:2}" for j in range(self.n)))


class Alice:
    """Алиса - доказывающая сторона"""
    
    def __init__(self, graph: Graph, coloring: Dict[int, int]):
        """
        Инициализация Алисы
        graph: граф
        coloring: правильная раскраска графа (словарь {вершина: цвет})
        """
        self.graph = graph
        self.coloring = coloring.copy()
        self.bit_length = 8  # Длина случайных чисел
        
        # Генерируем ключи RSA для каждой вершины
        self.rsa_keys = {}
        for v in graph.get_vertices():
            e, d, n = generate_rsa_keys(bits = self.bit_length)
            self.rsa_keys[v] = {'e': e, 'd': d, 'n': n}
        
        # Для текущего раунда
        self.current_permutation = None
        self.current_permuted_coloring = None
        self.current_r_values = None
        self.current_encrypted = None
    
    def get_public_keys(self) -> Dict[int, Tuple[int, int]]:
        """Возвращает публичные ключи RSA для всех вершин"""
        return {v: (self.rsa_keys[v]['e'], self.rsa_keys[v]['n']) for v in self.graph.get_vertices()}
    
    def start_round(self) -> Dict[int, int]:
        """
        Шаг 1-4 протокола:
        1. Случайная перестановка цветов
        2. Генерация случайных чисел с кодировкой цвета
        3. RSA шифрование
        4. Отправка зашифрованных значений
        
        Возвращает: словарь {вершина: зашифрованное значение}
        """
        # Шаг 1: Случайная перестановка цветов
        colors = [Color.RED, Color.BLUE, Color.YELLOW]
        random.shuffle(colors)
        self.current_permutation = colors
        
        # Применяем перестановку к раскраске
        self.current_permuted_coloring = {}
        for v in self.graph.get_vertices():
            original_color = self.coloring[v]
            self.current_permuted_coloring[v] = colors[original_color]
        
        # Шаг 2-4: Шифрование
        self.current_r_values = {}
        self.current_encrypted = {}
        
        for v in self.graph.get_vertices():
            # Генерируем случайное число с закодированным цветом в двух младших битах
            color = self.current_permuted_coloring[v]
            r = random.randint(0, 2 ** self.bit_length - 1)
            # Очищаем два младших бита и устанавливаем цвет
            r = (r & ~3) | color  # Устанавливаем два младших бита
            self.current_r_values[v] = r
            
            # Шифруем
            d = self.rsa_keys[v]['d']
            n = self.rsa_keys[v]['n']
            z = pow(r, d, n)
            self.current_encrypted[v] = z
        
        return self.current_encrypted
    
    def respond_to_edge(self, edge: Tuple[int, int]) -> Tuple[int, int]:
        """
        Шаг 5: Ответ на запрос ребра
        Возвращает зашифрованные значения c_v1 и c_v2
        """
        u, v = edge
        # В протоколе c_v - это закрытый ключ RSA для вершины v
        # В нашей реализации мы возвращаем сами зашифрованные значения,
        # и Боб расшифровывает их публичным ключом (e)
        return self.current_encrypted[u], self.current_encrypted[v]
    
    def reveal_colors_for_edge(self, edge: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Раскрывает цвета для конкретного ребра (для проверки Бобом)
        Возвращает: (r_u, r_v, d_u, d_v)
        """
        u, v = edge
        r_u = self.current_r_values[u]
        r_v = self.current_r_values[v]
        d_u = self.rsa_keys[u]['d']
        d_v = self.rsa_keys[v]['d']
        return r_u, r_v, d_u, d_v


class Bob:
    """Боб - проверяющая сторона"""
    
    def __init__(self, graph: Graph, public_keys: Dict[int, Tuple[int, int]]):
        """
        Инициализация Боба
        graph: граф (известен Бобу)
        public_keys: публичные ключи Алисы {вершина: (e, n)}
        """
        self.graph = graph
        self.public_keys = public_keys
        self.encrypted_values = None
        self.current_edge = None
        self.trust = True  # Доверяет ли Боб Алисе
    
    def receive_encrypted(self, encrypted: Dict[int, int]):
        """Получение зашифрованных значений от Алисы"""
        self.encrypted_values = encrypted
    
    def choose_edge(self) -> Tuple[int, int]:
        """Боб случайно выбирает ребро для проверки"""
        edges = self.graph.get_edges()
        self.current_edge = random.choice(edges)
        return self.current_edge
    
    def verify_edge(self, r_u: int, r_v: int, d_u: int, d_v: int) -> bool:
        """
        Проверка правильности раскраски для выбранного ребра
        """
        if self.current_edge is None:
            return False
        
        u, v = self.current_edge
        
        # Проверяем, что расшифровка соответствует полученным зашифрованным значениям
        e_u, n_u = self.public_keys[u]
        e_v, n_v = self.public_keys[v]
        
        # Используем d_u, d_v для расшифровки (в протоколе это делается на стороне Боба)
        # На самом деле в протоколе Боб вычисляет Z_v^c_v mod N_v = r_v
        # Мы симулируем это, используя d как показатель степени
        z_u = self.encrypted_values[u]
        z_v = self.encrypted_values[v]
        
        # Расшифровываем (в протоколе: Z_v = r_v^d_v mod N_v)
        # Проверяем, что r_u правильно расшифровывается
        decrypted_u = pow(z_u, e_u, n_u)  # В протоколе: Z^c mod N = r
        decrypted_v = pow(z_v, e_v, n_v)
        
        # В протоколе используется d, но у нас e - публичный ключ
        # В нашей симуляции мы используем e для расшифровки (как в RSA)
        # Алиса зашифровала r^d mod N, Боб расшифровывает (r^d)^e mod N = r
        
        # Проверяем соответствие
        if decrypted_u != r_u or decrypted_v != r_v:
            print(f"  ❌ Ошибка расшифровки!")
            return False
        
        # Проверяем, что цвета разные (два младших бита)
        color_u = r_u & 3
        color_v = r_v & 3
        
        if color_u == color_v:
            print(f"  ❌ Одинаковые цвета! Вершины {u} и {v}: {Color.to_short_string(color_u)} == {Color.to_short_string(color_v)}")
            return False
        
        print(f"  ✅ Вершины {u} и {v}: {Color.to_short_string(color_u)} != {Color.to_short_string(color_v)}")
        return True


# ============================================================
# 3. СИМУЛЯЦИЯ ПРОТОКОЛА
# ============================================================

def run_zero_knowledge_protocol(graph: Graph, coloring: Dict[int, int], rounds: int = 5, verbose: bool = True):
    """
    Запуск протокола доказательства с нулевым знанием
    
    graph: граф
    coloring: правильная раскраска
    rounds: количество раундов
    verbose: вывод подробной информации
    """
    print("=" * 70)
    print("ПРОТОКОЛ ДОКАЗАТЕЛЬСТВА С НУЛЕВЫМ ЗНАНИЕМ")
    print("Задача: Раскраска графа в 3 цвета")
    print("=" * 70)
    
    # Инициализация
    alice = Alice(graph, coloring)
    public_keys = alice.get_public_keys()
    bob = Bob(graph, public_keys)
    
    print("\n📊 Исходный граф:")
    graph.print_graph()
    print("\n🎨 Правильная раскраска (известна только Алисе):")
    for v in sorted(coloring.keys()):
        print(f"  Вершина {v}: {Color.to_string(coloring[v])}")
    print()
    
    # Проверка, что раскраска правильная
    if not graph.is_valid_coloring(coloring):
        print("❌ ОШИБКА: Раскраска не является правильной!")
        return False
    
    print(f"🔄 Запуск протокола ({rounds} раундов)...\n")
    
    for round_num in range(1, rounds + 1):
        print(f"--- Раунд {round_num} ---")
        
        # Шаг 1-4: Алиса генерирует и шифрует данные
        encrypted = alice.start_round()
        bob.receive_encrypted(encrypted)
        print(f"  📤 Алиса отправила зашифрованные данные для {len(encrypted)} вершин")
        
        # Шаг 5: Боб выбирает ребро
        edge = bob.choose_edge()
        print(f"  🔍 Боб выбрал ребро: {edge}")
        
        # Алиса отвечает
        r_u, r_v, d_u, d_v = alice.reveal_colors_for_edge(edge)
        
        # Боб проверяет
        if bob.verify_edge(r_u, r_v, d_u, d_v):
            print(f"  ✅ Раунд {round_num} пройден успешно!")
        else:
            print(f"  ❌ Раунд {round_num} ПРОВАЛЕН! Алиса разоблачена!")
            return False
        
        print()
    
    print("=" * 70)
    print("🎉 ПРОТОКОЛ УСПЕШНО ЗАВЕРШЕН!")
    print("   Алиса доказала знание правильной раскраски")
    print("   Боб не узнал саму раскраску")
    print("=" * 70)
    return True


# ============================================================
# 4. ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================

def example_honest_alice():
    """Пример с честной Алисой, которая знает правильную раскраску"""
    print("\n" + "🔵" * 35)
    print("ПРИМЕР 1: Честная Алиса")
    print("🔵" * 35 + "\n")
    
    # Создаем граф (как на рис. 5.1 в тексте)
    # Вершины: 0-6
    edges = [
        (0, 1), (0, 2), (0, 5), (0, 6),  # Вершина 0 связана с 1,2,5,6
        (1, 2), (1, 3), (1, 6),           # Вершина 1 связана с 2,3,6
        (2, 3), (2, 4), (2, 5),           # Вершина 2 связана с 3,4,5
        (3, 4),                           # Вершина 3 связана с 4
        (4, 5), (4, 6),                   # Вершина 4 связана с 5,6
        (5, 6)                            # Вершина 5 связана с 6
    ]
    graph = Graph(7, edges)
    
    # Правильная раскраска (пример из текста)
    coloring = {
        0: Color.RED,
        1: Color.YELLOW,
        2: Color.RED,
        3: Color.BLUE,
        4: Color.YELLOW,
        5: Color.RED,
        6: Color.YELLOW
    }
    
    # Запускаем протокол
    run_zero_knowledge_protocol(graph, coloring, rounds = 5)


def example_dishonest_alice():
    """Пример с нечестной Алисой, которая не знает правильной раскраски"""
    print("\n" + "🔴" * 35)
    print("ПРИМЕР 2: Нечестная Алиса (не знает раскраски)")
    print("🔴" * 35 + "\n")
    
    # Тот же граф
    edges = [
        (0, 1), (0, 2), (0, 5), (0, 6),
        (1, 2), (1, 3), (1, 6),
        (2, 3), (2, 4), (2, 5),
        (3, 4),
        (4, 5), (4, 6),
        (5, 6)
    ]
    graph = Graph(7, edges)
    
    # НЕПРАВИЛЬНАЯ раскраска (вершины 0 и 1 одного цвета)
    wrong_coloring = {
        0: Color.RED,
        1: Color.RED,   # Ошибка: ребро (0,1) соединяет вершины одного цвета
        2: Color.BLUE,
        3: Color.YELLOW,
        4: Color.RED,
        5: Color.BLUE,
        6: Color.YELLOW
    }
    
    # Запускаем протокол (должен провалиться)
    run_zero_knowledge_protocol(graph, wrong_coloring, rounds = 3)


def example_small_graph():
    """Пример с маленьким графом для наглядности"""
    print("\n" + "🟢" * 35)
    print("ПРИМЕР 3: Маленький граф")
    print("🟢" * 35 + "\n")
    
    # Простой граф-треугольник
    edges = [(0, 1), (1, 2), (0, 2)]
    graph = Graph(3, edges)
    
    # Правильная раскраска треугольника
    coloring = {
        0: Color.RED,
        1: Color.BLUE,
        2: Color.YELLOW
    }
    
    run_zero_knowledge_protocol(graph, coloring, rounds = 3)


# ============================================================
# 5. ЗАПУСК ПРИМЕРОВ
# ============================================================

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запускаем примеры
    example_honest_alice()
    print("\n" + "=" * 70 + "\n")
    
    example_dishonest_alice()
    print("\n" + "=" * 70 + "\n")
    
    example_small_graph()