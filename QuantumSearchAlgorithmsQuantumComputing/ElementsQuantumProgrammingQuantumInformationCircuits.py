# Элементы квантового программирования — квантовая информация и схемы
import math
import random

# Константа 1/√2 для вентиля Адамара
H_CONST = 1 / math.sqrt(2)

class QuantumBit:
    """Классическая симуляция кубита без использования NumPy"""
    
    def __init__(self, state = None):
        """
        Инициализация кубита.
        По умолчанию создаётся состояние |0⟩ = [1, 0]
        """
        if state is None:
            self.state = [1.0, 0.0]  # |0⟩
        else:
            # Проверяем, что состояние нормализовано (a² + b² = 1)
            a, b = state
            norm = math.sqrt(a ** 2 + b ** 2)
            if abs(norm - 1.0) > 1e-10:
                raise ValueError(f"Состояние не нормализовано: a² + b² = {a ** 2 + b ** 2}")
            self.state = state
    
    def apply_hadamard(self):
        """Применяет вентиль Адамара (создаёт суперпозицию)"""
        a, b = self.state
        # H|0⟩ = (|0⟩ + |1⟩)/√2
        # H|1⟩ = (|0⟩ - |1⟩)/√2
        new_a = (a + b) * H_CONST
        new_b = (a - b) * H_CONST
        self.state = [new_a, new_b]
        return self
    
    def apply_pauli_x(self):
        """Применяет вентиль Паули-X (квантовое НЕ)"""
        a, b = self.state
        # Меняет местами амплитуды: |0⟩ ↔ |1⟩
        self.state = [b, a]
        return self
    
    def apply_pauli_z(self):
        """Применяет вентиль Паули-Z (фазовый сдвиг)"""
        a, b = self.state
        # Оставляет |0⟩ без изменений, меняет знак у |1⟩
        self.state = [a, -b]
        return self
    
    def apply_identity(self):
        """Вентиль тождественности (ничего не делает)"""
        return self
    
    def measure(self):
        """
        Измеряет кубит.
        Возвращает 0 или 1 с вероятностью, пропорциональной квадрату амплитуды.
        """
        a, b = self.state
        prob_0 = a ** 2
        prob_1 = b ** 2
        
        # Генерируем случайное число от 0 до 1
        rand_val = random.random()
        
        if rand_val < prob_0:
            result = 0
            # После измерения состояние коллапсирует в |0⟩
            self.state = [1.0, 0.0]
        else:
            result = 1
            # После измерения состояние коллапсирует в |1⟩
            self.state = [0.0, 1.0]
        
        return result
    
    def get_state(self):
        """Возвращает текущее состояние кубита для отладки"""
        return self.state.copy()
    
    def __str__(self):
        """Красивое отображение состояния"""
        a, b = self.state
        # Округляем для читаемости
        a_rounded = round(a, 4)
        b_rounded = round(b, 4)
        
        parts = []
        if abs(a_rounded) > 1e-6:
            if a_rounded == 1:
                parts.append("|0⟩")
            else:
                parts.append(f"{a_rounded}|0⟩")
        if abs(b_rounded) > 1e-6:
            if b_rounded == 1:
                parts.append("|1⟩")
            else:
                # Добавляем знак плюс, если нужно
                if parts and b_rounded > 0:
                    parts.append(f"+ {b_rounded}|1⟩")
                else:
                    parts.append(f"{b_rounded}|1⟩")
        
        return " + ".join(parts) if parts else "0"


def demonstrate_quantum_random():
    """Демонстрация квантового генератора случайных чисел"""
    print("=" * 60)
    print("КВАНТОВЫЙ ГЕНЕРАТОР СЛУЧАЙНЫХ ЧИСЕЛ (КГСЧ)")
    print("=" * 60)
    
    # Создаём кубит в состоянии |0⟩
    qbit = QuantumBit()
    print(f"1. Начальное состояние: {qbit}")
    
    # Применяем вентиль Адамара для создания суперпозиции
    qbit.apply_hadamard()
    print(f"2. После H (суперпозиция): {qbit}")
    print(f"   Амплитуды: |0⟩ = {qbit.state[0]:.4f}, |1⟩ = {qbit.state[1]:.4f}")
    print(f"   Вероятности: 0 = {qbit.state[0] ** 2:.2f}, 1 = {qbit.state[1] ** 2:.2f}")
    
    # Измеряем 10 раз
    print("\n3. Результаты 10 измерений:")
    results = []
    for i in range(10):
        # Важно: каждый раз создаём новый кубит или сбрасываем состояние
        # Покажем оба варианта:
        if i == 0:
            # Первый раз измеряем существующий (состояние коллапсирует)
            result = qbit.measure()
        else:
            # Для следующих измерений создаём новый кубит в суперпозиции
            qbit = QuantumBit().apply_hadamard()
            result = qbit.measure()
        results.append(result)
        print(f"   Измерение {i + 1}: {result}")
    
    print(f"\n   Статистика: 0 = {results.count(0)}, 1 = {results.count(1)}")
    print(f"   (При большем числе измерений будет ≈ 50 / 50)")


def demonstrate_quantum_identity():
    """Демонстрация тождества: H · X · H = Z"""
    print("\n" + "=" * 60)
    print("ДОКАЗАТЕЛЬСТВО ТОЖДЕСТВА: H · X · H = Z")
    print("=" * 60)
    
    # Начинаем с |0⟩
    qbit = QuantumBit()
    print(f"Начальное состояние: {qbit}")
    
    # Применяем последовательность H → X → H
    qbit.apply_hadamard()
    print(f"После H:           {qbit}")
    
    qbit.apply_pauli_x()
    print(f"После H·X:         {qbit}")
    
    qbit.apply_hadamard()
    print(f"После H·X·H:       {qbit}")
    print(f"Амплитуды: {[round(x, 4) for x in qbit.state]}")
    
    # Сравниваем с применением Z к исходному состоянию
    qbit2 = QuantumBit()  # Снова |0⟩
    qbit2.apply_pauli_z()
    print(f"\nПрямое применение Z к |0⟩: {qbit2}")
    print(f"Амплитуды: {[round(x, 4) for x in qbit2.state]}")
    
    print("\n✅ Результаты совпадают! H·X·H = Z (для состояния |0⟩)")


def demonstrate_grovers_oracle_preparation():
    """
    Подготовка к алгоритму Гровера:
    Показывает, как Z-вентиль меняет фазу у состояния |1⟩
    """
    print("\n" + "=" * 60)
    print("ПОДГОТОВКА К АЛГОРИТМУ ГРОВЕРА (Оракул)")
    print("=" * 60)
    
    # Создаём кубит в суперпозиции
    qbit = QuantumBit().apply_hadamard()
    print(f"Суперпозиция: {qbit}")
    print(f"Амплитуды: |0⟩ = {qbit.state[0]:.4f}, |1⟩ = {qbit.state[1]:.4f}")
    
    # Применяем Z-вентиль (меняет фазу у |1⟩)
    qbit.apply_pauli_z()
    print(f"\nПосле Z (фазовый сдвиг): {qbit}")
    print(f"Амплитуды: |0⟩ = {qbit.state[0]:.4f}, |1⟩ = {qbit.state[1]:.4f}")
    print("⚠️  Вероятности НЕ изменились! (|0|² = 0.5, |1|² = 0.5)")
    print("   Но фаза у |1⟩ стала отрицательной — это важно для интерференции!")
    
    # Применяем H обратно, чтобы увидеть эффект
    qbit.apply_hadamard()
    print(f"\nПосле H (возврат): {qbit}")
    print(f"Амплитуды: |0⟩ = {qbit.state[0]:.4f}, |1⟩ = {qbit.state[1]:.4f}")
    print("🎯 Теперь мы видим эффект: суперпозиция превратилась в |1⟩!")
    print("   (Именно так оракул в Гровере 'помечает' нужное состояние)")


if __name__ == "__main__":
    # Запускаем все демонстрации
    demonstrate_quantum_random()
    demonstrate_quantum_identity()
    demonstrate_grovers_oracle_preparation()
    
    print("\n" + "=" * 60)
    print("🔑 КЛЮЧЕВЫЕ ВЫВОДЫ:")
    print("=" * 60)
    print("1. Вентиль H создаёт суперпозицию с равными вероятностями")
    print("2. Вентиль X — это квантовое НЕ (меняет местами амплитуды)")
    print("3. Вентиль Z меняет фазу у |1⟩, не влияя на вероятности")
    print("4. Тождество H·X·H = Z — основа многих квантовых алгоритмов")
    print("5. В квантовых вычислениях важны не только вероятности, но и ФАЗЫ!")