# Глубокое погружение в алгоритм Гровера
"""
Симуляция алгоритма Гровера на чистом Python (без NumPy)
Реализовано:
- Работа с комплексными числами
- Суперпозиция состояний
- Оракул (маркировка решения)
- Оператор диффузии
- Вычисление оптимального числа итераций
- Визуализация вероятностей
"""

import math
import cmath
import random
from typing import List, Tuple, Dict

class Complex:
    """Класс для работы с комплексными числами без использования complex из Python"""
    def __init__(self, re: float = 0.0, im: float = 0.0):
        self.re = re
        self.im = im
    
    def __add__(self, other):
        return Complex(self.re + other.re, self.im + other.im)
    
    def __sub__(self, other):
        return Complex(self.re - other.re, self.im - other.im)
    
    def __mul__(self, other):
        # (a+bi)(c+di) = (ac-bd) + (ad+bc)i
        return Complex(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re
        )
    
    def __truediv__(self, scalar: float):
        return Complex(self.re / scalar, self.im / scalar)
    
    def conjugate(self):
        return Complex(self.re, -self.im)
    
    def abs_squared(self) -> float:
        return self.re * self.re + self.im * self.im
    
    def abs(self) -> float:
        return math.sqrt(self.abs_squared())
    
    def __repr__(self):
        if abs(self.im) < 1e-10:
            return f"{self.re:.4f}"
        elif self.im >= 0:
            return f"{self.re:.4f} + {self.im:.4f}i"
        else:
            return f"{self.re:.4f} - {abs(self.im):.4f}i"

class QuantumState:
    """Квантовое состояние как вектор амплитуд"""
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.n_states = 1 << n_qubits  # 2^n
        # Инициализируем все амплитуды нулями
        self.amplitudes = [Complex(0.0, 0.0) for _ in range(self.n_states)]
        # Начальное состояние |0...0>
        self.amplitudes[0] = Complex(1.0, 0.0)
    
    def apply_hadamard_all(self):
        """Применяем вентиль Адамара ко всем кубитам"""
        # Создаем равномерную суперпозицию
        norm = Complex(1.0 / math.sqrt(self.n_states), 0.0)
        for i in range(self.n_states):
            self.amplitudes[i] = norm
    
    def apply_oracle(self, solution: int):
        """
        Оракул: меняет фазу у состояния-решения
        Если состояние == solution, умножаем амплитуду на -1
        """
        self.amplitudes[solution] = self.amplitudes[solution] * Complex(-1.0, 0.0)
    
    def apply_diffusion(self):
        """
        Оператор диффузии: отражение относительно среднего
        D = 2|s><s| - I
        """
        # Вычисляем среднюю амплитуду
        avg = Complex(0.0, 0.0)
        for amp in self.amplitudes:
            avg = avg + amp
        avg = avg / self.n_states
        
        # Применяем преобразование: amp -> 2*avg - amp
        for i in range(self.n_states):
            self.amplitudes[i] = (avg * Complex(2.0, 0.0)) - self.amplitudes[i]
    
    def apply_grover_iteration(self, solution: int):
        """Одна полная итерация Гровера: Оракул + Диффузия"""
        self.apply_oracle(solution)
        self.apply_diffusion()
    
    def get_probabilities(self) -> List[float]:
        """Получаем вероятности для всех состояний"""
        return [amp.abs_squared() for amp in self.amplitudes]
    
    def measure(self) -> int:
        """
        Производим квантовое измерение
        Возвращает индекс состояния с вероятностью, пропорциональной |амплитуда|²
        """
        probs = self.get_probabilities()
        # Кумулятивная сумма для рулетки
        cumulative = []
        running_sum = 0.0
        for p in probs:
            running_sum += p
            cumulative.append(running_sum)
        
        # Случайное число от 0 до 1
        r = random.random()
        
        # Находим состояние
        for i, cum in enumerate(cumulative):
            if r <= cum:
                return i
        
        return self.n_states - 1
    
    def print_state(self, title: str = ""):
        """Выводим состояние в удобочитаемом виде"""
        if title:
            print(f"\n{title}")
            print("=" * 50)
        
        probs = self.get_probabilities()
        for i, (amp, prob) in enumerate(zip(self.amplitudes, probs)):
            if prob > 1e-6:  # Показываем только значимые состояния
                binary = format(i, f'0{self.n_qubits}b')
                print(f"|{binary}⟩: амплитуда = {amp}, вероятность = {prob * 100:.2f}%")

class GroverSearch:
    """Класс, реализующий полный алгоритм Гровера"""
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.n_states = 1 << n_qubits
        self.state = QuantumState(n_qubits)
    
    def find_solution(self, solution: int, verbose: bool = True) -> Tuple[int, int]:
        """
        Запускает алгоритм Гровера для поиска решения
        Возвращает (найденное_решение, количество_итераций)
        """
        # Вычисляем оптимальное число итераций
        t_optimal = int(round((math.pi / 4) * math.sqrt(self.n_states)))
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"АЛГОРИТМ ГРОВЕРА")
            print(f"{'=' * 60}")
            print(f"Кубитов: {self.n_qubits}")
            print(f"Размер пространства: {self.n_states}")
            print(f"Искомое состояние: {format(solution, f'0{self.n_qubits}b')} (индекс {solution})")
            print(f"Оптимальное число итераций: {t_optimal}")
            print(f"\nНачальное состояние (равная суперпозиция):")
            self.state.print_state()
        
        # Инициализация: суперпозиция
        self.state.apply_hadamard_all()
        
        if verbose:
            print("\nПосле инициализации:")
            self.state.print_state()
        
        # Итерации Гровера
        for t in range(t_optimal):
            self.state.apply_grover_iteration(solution)
            
            if verbose and (t < 3 or t == t_optimal - 1):
                print(f"\n--- Итерация {t + 1} ---")
                self.state.print_state()
        
        # Измерение
        measured = self.state.measure()
        prob_success = self.state.get_probabilities()[solution]
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"РЕЗУЛЬТАТ ИЗМЕРЕНИЯ")
            print(f"{'=' * 60}")
            print(f"Найденное состояние: {format(measured, f'0{self.n_qubits}b')} (индекс {measured})")
            print(f"Вероятность найти решение: {prob_success * 100:.2f}%")
            
            # Проверяем, правильный ли ответ
            if measured == solution:
                print("✅ УСПЕХ! Найдено правильное решение!")
            else:
                print("❌ Неудача. Попробуйте запустить снова (квантовые измерения вероятностны)")
        
        return measured, prob_success
    
    def run_statistics(self, solution: int, num_runs: int = 100):
        """
        Запускает алгоритм множество раз и собирает статистику
        """
        print(f"\n{'=' * 60}")
        print(f"СТАТИСТИЧЕСКИЙ АНАЛИЗ")
        print(f"{'=' * 60}")
        print(f"Количество запусков: {num_runs}")
        print(f"Ищем состояние: {format(solution, f'0{self.n_qubits}b')}")
        
        # Сохраняем оригинальное состояние
        original_state = self.state
        
        results = {}
        for _ in range(num_runs):
            self.state = QuantumState(self.n_qubits)
            # Сначала вычисляем оптимальное t
            t_optimal = int(round((math.pi / 4) * math.sqrt(self.n_states)))
            self.state.apply_hadamard_all()
            for _ in range(t_optimal):
                self.state.apply_grover_iteration(solution)
            
            measured = self.state.measure()
            results[measured] = results.get(measured, 0) + 1
        
        # Восстанавливаем состояние
        self.state = original_state
        
        # Выводим статистику
        print(f"\nРезультаты {num_runs} измерений:")
        for state, count in sorted(results.items()):
            binary = format(state, f'0{self.n_qubits}b')
            percentage = (count / num_runs) * 100
            mark = " ★" if state == solution else ""
            print(f"  {binary} (индекс {state}): {count} / {num_runs} ({percentage:.1f}%){mark}")
        
        success_rate = results.get(solution, 0) / num_runs * 100
        print(f"\nУспешность: {success_rate:.1f}%")

def demo_grover():
    """Демонстрация алгоритма Гровера на нескольких примерах"""
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АЛГОРИТМА ГРОВЕРА")
    print("=" * 60)
    
    # Пример 1: 3 кубита (8 состояний), ищем состояние |101⟩ (индекс 5)
    print("\n" + "─" * 60)
    print("ПРИМЕР 1: 3 кубита, ищем состояние |101⟩")
    print("─" * 60)
    
    grover3 = GroverSearch(n_qubits = 3)
    solution = 5  # |101⟩ в двоичном виде
    grover3.find_solution(solution, verbose = True)
    
    # Пример 2: 4 кубита (16 состояний), ищем состояние |1111⟩ (индекс 15)
    print("\n\n" + "─" * 60)
    print("ПРИМЕР 2: 4 кубита, ищем состояние |1111⟩")
    print("─" * 60)
    
    grover4 = GroverSearch(n_qubits = 4)
    solution = 15  # |1111⟩
    grover4.find_solution(solution, verbose = True)
    
    # Пример 3: Статистический анализ для 5 кубитов
    print("\n\n" + "─" * 60)
    print("ПРИМЕР 3: Статистический анализ (5 кубитов, 100 запусков)")
    print("─" * 60)
    
    grover5 = GroverSearch(n_qubits = 5)
    solution = 17  # |10001⟩
    grover5.run_statistics(solution, num_runs = 100)

def compare_with_bruteforce():
    """Сравнение алгоритма Гровера с классическим перебором"""
    
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ С КЛАССИЧЕСКИМ ПЕРЕБОРОМ")
    print("=" * 60)
    
    n_qubits = 8  # 256 элементов
    n_states = 1 << n_qubits
    
    print(f"\nРазмер базы данных: {n_states} элементов (n = {n_qubits} кубитов)")
    
    # Классический поиск
    print("\nКлассический поиск:")
    print(f"  В среднем нужно проверить: {n_states / 2:.0f} элементов")
    print(f"  В худшем случае: {n_states} элементов")
    
    # Квантовый поиск
    t_optimal = int(round((math.pi / 4) * math.sqrt(n_states)))
    print(f"\nКвантовый поиск (Гровер):")
    print(f"  Нужно итераций: {t_optimal}")
    print(f"  Ускорение: {n_states / t_optimal:.1f}x")
    
    # Таблица для разных размеров
    print("\n\nТаблица сравнения для разных размеров:")
    print("-" * 60)
    print(f"{'Кубиты':>6} | {'Элементы':>10} | {'Классика (средн.)':>15} | {'Гровер':>10} | {'Ускорение':>10}")
    print("-" * 60)
    
    for n in range(2, 13):
        states = 1 << n
        classical_avg = states / 2
        grover_steps = int(round((math.pi / 4) * math.sqrt(states)))
        speedup = classical_avg / grover_steps if grover_steps > 0 else 0
        
        print(f"{n:6d} | {states:10d} | {classical_avg:15.0f} | {grover_steps:10d} | {speedup:10.1f}x")

if __name__ == "__main__":
    # Устанавливаем seed для воспроизводимости
    random.seed(42)
    
    # Запускаем демонстрацию
    demo_grover()
    
    # Сравнение с классикой
    compare_with_bruteforce()
    
    print("\n" + "=" * 60)
    print("КОНЕЦ ПРОГРАММЫ")
    print("=" * 60)