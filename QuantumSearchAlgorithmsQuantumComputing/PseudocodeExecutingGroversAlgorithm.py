# Псевдокод для выполнения алгоритма Гровера 
"""
Классическая симуляция алгоритма Гровера на чистом Python (без NumPy)
Симулирует поиск одного элемента в неструктурированной базе данных из N элементов
"""

import math
import copy

class GroverSimulator:
    def __init__(self, n_qubits):
        """
        Инициализация симулятора
        
        Args:
            n_qubits: количество кубитов (N = 2 ^ n_qubits)
        """
        self.n_qubits = n_qubits
        self.N = 2 ** n_qubits  # количество элементов в базе данных
        
        # Состояние системы - вектор амплитуд (список комплексных чисел)
        # Каждое число представлено как [real, imag]
        self.state = None
        
        # Искомый элемент (индекс)
        self.target = None
        
    def initialize_superposition(self):
        """
        Этап 1: Создание равномерной суперпозиции
        Применяем вентиль Адамара ко всем кубитам
        """
        # Начинаем с состояния |0...0>
        self.state = [[0.0, 0.0] for _ in range(self.N)]
        self.state[0] = [1.0, 0.0]  # |0⟩ состояние
        
        # Применяем H^⊗n ко всем кубитам
        # Каждая амплитуда становится 1/√N
        amplitude = 1.0 / math.sqrt(self.N)
        for i in range(self.N):
            self.state[i] = [amplitude, 0.0]
        
        print(f"✓ Суперпозиция создана для {self.N} состояний")
        print(f"  Амплитуда каждого состояния: {amplitude:.4f}")
        print(f"  Вероятность каждого состояния: {amplitude ** 2:.2%}\n")
    
    def oracle(self, target_index):
        """
        Оракул: меняет фазу целевого состояния на -1
        В квантовых вычислениях это U_ω |x⟩ = (-1) ^ {f(x)} |x⟩
        
        Args:
            target_index: индекс искомого элемента
        """
        self.target = target_index
        print(f"🔍 Оракул: поиск элемента с индексом {target_index}")
        
        # Меняем знак амплитуды у целевого состояния
        self.state[target_index] = [-self.state[target_index][0], -self.state[target_index][1]]
        
        print(f"  ✓ Фаза состояния |{target_index}⟩ изменена на -1\n")
    
    def diffusion_operator(self):
        """
        Оператор диффузии (усиление амплитуды)
        U_s = 2|s⟩⟨s| - I, где |s⟩ - состояние равномерной суперпозиции
        """
        # Шаг 1: Вычисляем среднюю амплитуду
        avg_real = 0.0
        avg_imag = 0.0
        for i in range(self.N):
            avg_real += self.state[i][0]
            avg_imag += self.state[i][1]
        avg_real /= self.N
        avg_imag /= self.N
        
        # Шаг 2: Отражаем амплитуды относительно среднего
        # new_amplitude = 2*avg - old_amplitude
        for i in range(self.N):
            self.state[i][0] = 2 * avg_real - self.state[i][0]
            self.state[i][1] = 2 * avg_imag - self.state[i][1]
    
    def grover_iteration(self):
        """
        Одна полная итерация оператора Гровера G = U_s * U_ω
        """
        print("  ─── Итерация оператора Гровера ───")
        print("  1. Применение оракула...")
        # Исправление: передаем target в oracle
        self.oracle(self.target)
        
        print("  2. Применение оператора диффузии...")
        self.diffusion_operator()
        print("  ✓ Диффузия применена\n")
    
    def calculate_probabilities(self):
        """
        Вычисляет вероятности для каждого состояния
        P(i) = |amplitude_i|²
        """
        probabilities = []
        for i in range(self.N):
            real = self.state[i][0]
            imag = self.state[i][1]
            prob = real ** 2 + imag ** 2
            probabilities.append(prob)
        return probabilities
    
    def measure(self):
        """
        Этап 3: Измерение состояния
        Возвращает индекс с вероятностью, пропорциональной |амплитуда|²
        """
        probabilities = self.calculate_probabilities()
        
        # Проверяем, что сумма вероятностей ≈ 1
        total_prob = sum(probabilities)
        if abs(total_prob - 1.0) > 1e-10:
            print(f"⚠️  Предупреждение: сумма вероятностей = {total_prob:.6f}")
        
        # Симулируем измерение (детерминированно выбираем состояние с макс. вероятностью)
        # В реальном квантовом компьютере это было бы случайным выбором
        max_prob_index = max(range(self.N), key = lambda i: probabilities[i])
        
        return max_prob_index, probabilities
    
    def run(self, target_index, verbose = True):
        """
        Запуск полного алгоритма Гровера
        
        Args:
            target_index: индекс искомого элемента
            verbose: выводить подробную информацию
        """
        print("=" * 60)
        print("АЛГОРИТМ ГРОВЕРА - КВАНТОВЫЙ ПОИСК")
        print("=" * 60)
        print(f"Количество кубитов: {self.n_qubits}")
        print(f"Размер базы данных: {self.N} элементов")
        print(f"Целевой индекс: {target_index}\n")
        
        # Сохраняем целевой индекс для использования в итерациях
        self.target = target_index
        
        # Этап 1: Подготовка суперпозиции
        print("🔵 ЭТАП 1: Подготовка суперпозиции")
        self.initialize_superposition()
        
        # Вычисляем оптимальное количество итераций
        t = int(math.floor((math.pi / 4) * math.sqrt(self.N)))
        print(f"🔵 ЭТАП 2: {t} итераций оператора Гровера")
        print(f"  (оптимальное число для N = {self.N})\n")
        
        # Этап 2: Итерации Гровера
        for iteration in range(t):
            print(f"  Итерация {iteration + 1} / {t}:")
            self.grover_iteration()
            
            # Показываем прогресс (каждые 2 итерации)
            if verbose and (iteration + 1) % 2 == 0:
                probs = self.calculate_probabilities()
                target_prob = probs[target_index]
                print(f"  📊 Вероятность найти целевой элемент: {target_prob:.2%}\n")
        
        # Этап 3: Измерение
        print("🔵 ЭТАП 3: Измерение")
        result_index, probabilities = self.measure()
        
        # Вывод результатов
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 60)
        
        # Показываем топ-5 наиболее вероятных состояний
        sorted_indices = sorted(range(self.N), key = lambda i: probabilities[i], reverse = True)
        
        print("Топ-5 наиболее вероятных состояний:")
        for rank, idx in enumerate(sorted_indices[:5], 1):
            prob = probabilities[idx]
            is_target = "🎯 ЦЕЛЬ!" if idx == target_index else ""
            print(f"  {rank}. |{idx}⟩: {prob:.2%} {is_target}")
        
        print(f"\n✓ Измеренный результат: |{result_index}⟩")
        
        if result_index == target_index:
            print("✅ УСПЕХ! Найден правильный элемент!")
            success = True
        else:
            print("❌ Неудача. Попробуйте изменить количество итераций.")
            success = False
        
        print("=" * 60)
        return result_index, success, probabilities


def test_grover_with_small_database():
    """
    Тест алгоритма на маленькой базе данных (8 элементов, 3 кубита)
    """
    print("\n" + "🧪 ТЕСТ 1: Маленькая база данных (N = 8, 3 кубита)")
    print("-" * 60)
    
    simulator = GroverSimulator(n_qubits = 3)
    target = 5  # ищем элемент с индексом 5
    result, success, probs = simulator.run(target_index = target, verbose = True)
    
    # Дополнительная визуализация
    print("\n📊 Полное распределение вероятностей:")
    for i, prob in enumerate(probs):
        if prob > 0.01:
            bar = "█" * int(prob * 50)
            marker = " ← ЦЕЛЬ" if i == target else ""
            print(f"  |{i:3d}⟩: {prob:6.2%} {bar}{marker}")
    
    return result, success


def test_grover_with_large_database():
    """
    Тест алгоритма на большой базе данных (128 элементов, 7 кубитов)
    """
    print("\n" + "🧪 ТЕСТ 2: Большая база данных (N = 128, 7 кубитов)")
    print("-" * 60)
    
    simulator = GroverSimulator(n_qubits = 7)
    target = 42  # ищем элемент с индексом 42 (как в "Автостопом по галактике")
    result, success, probs = simulator.run(target_index = target, verbose = True)
    
    return result, success


def visualize_probabilities(simulator, target_index):
    """
    Визуализация распределения вероятностей (текстовая)
    """
    print("\n📊 Распределение вероятностей:")
    print("-" * 60)
    
    probabilities = simulator.calculate_probabilities()
    
    # Группируем для наглядности
    max_prob = max(probabilities)
    bar_width = 50
    
    for i, prob in enumerate(probabilities):
        if prob > 0.01:  # показываем только значимые вероятности
            bar_length = int((prob / max_prob) * bar_width)
            bar = "█" * bar_length
            marker = " ← ЦЕЛЬ" if i == target_index else ""
            print(f"  |{i:3d}⟩: {prob:6.2%} {bar}{marker}")


def analyze_grover_performance():
    """
    Анализ производительности алгоритма для разных размеров базы данных
    """
    print("\n" + "📈 АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ АЛГОРИТМА ГРОВЕРА")
    print("=" * 60)
    print("Размер БД | Кубиты | Итерации | Классические шаги | Ускорение")
    print("-" * 60)
    
    for n in range(2, 9):  # от 2 до 8 кубитов
        N = 2 ** n
        t = int(math.floor((math.pi / 4) * math.sqrt(N)))
        classical = N // 2  # в среднем нужно проверить половину элементов
        speedup = classical / t if t > 0 else 0
        
        print(f"  {N:6d}   |   {n:2d}    |   {t:2d}     |      {classical:3d}        |   {speedup:5.1f}x")


if __name__ == "__main__":
    # Запускаем тесты
    
    print("=" * 60)
    print("КВАНТОВЫЙ АЛГОРИТМ ГРОВЕРА - СИМУЛЯЦИЯ НА ЧИСТОМ PYTHON")
    print("=" * 60)
    
    # Тест 1: Маленькая база данных (для проверки работы)
    test_grover_with_small_database()
    
    print("\n" + "=" * 60)
    print("ПЕРЕХОД К БОЛЬШОЙ БАЗЕ ДАННЫХ")
    print("=" * 60)
    
    # Тест 2: Большая база данных (как в вашем тексте)
    test_grover_with_large_database()
    
    # Дополнительный тест: визуализация для 16 элементов
    print("\n" + "🧪 ТЕСТ 3: Детальная визуализация для N = 16 (4 кубита)")
    print("-" * 60)
    
    simulator = GroverSimulator(n_qubits = 4)
    target = 7
    print(f"Ищем элемент с индексом {target}\n")
    
    # Создаем суперпозицию
    simulator.initialize_superposition()
    print("Начальное состояние:")
    visualize_probabilities(simulator, target)
    
    # Делаем итерации
    for i in range(3):
        print(f"\n--- После итерации {i + 1} ---")
        simulator.oracle(target)
        simulator.diffusion_operator()
        visualize_probabilities(simulator, target)
    
    # Анализ производительности
    analyze_grover_performance()