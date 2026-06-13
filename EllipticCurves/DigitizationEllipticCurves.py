# 2. Оцифровка эллиптических кривых
"""
Вероятностный метод оцифровки сообщений в точки эллиптической кривой.
Автоматический подбор параметров для заданного количества сообщений.
"""

import random
import math
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class EllipticCurve:
    """Эллиптическая кривая над F_p: y ^ 2 = x ^ 3 + ax + b."""
    p: int          # характеристика поля (простое число, p ≠ 2,3)
    a: int
    b: int

    def __post_init__(self):
        # Проверка, что кривая неособая: дискриминант ≠ 0
        discriminant = (-16 * (4 * self.a ** 3 + 27 * self.b ** 2)) % self.p
        if discriminant == 0:
            raise ValueError("Кривая особая (дискриминант = 0)")

    def is_on_curve(self, x: int, y: int) -> bool:
        """Проверяет, лежит ли точка (x,y) на кривой."""
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0


@dataclass
class Point:
    """Точка на эллиптической кривой."""
    x: int
    y: int
    curve: EllipticCurve

    def __post_init__(self):
        if not self.curve.is_on_curve(self.x, self.y):
            raise ValueError(f"Точка ({self.x}, {self.y}) не лежит на кривой")
    
    def __str__(self):
        return f"({self.x}, {self.y})"


class ProbabilisticEncoding:
    """
    Вероятностное кодирование сообщений в точки эллиптической кривой.
    """
    def __init__(self, curve: EllipticCurve, k: int = 30):
        """
        curve: эллиптическая кривая
        k: количество попыток на одно сообщение (обычно 20-50)
        """
        self.curve = curve
        self.k = k
        self.p = curve.p
        
        # Максимальное количество сообщений
        self.M = (self.p - 1) // k
        
        print(f"Инициализация кодировщика:")
        print(f"  Поле: F_{self.p}")
        print(f"  Кривая: y ^ 2 = x ^ 3 + {curve.a}x + {curve.b}")
        print(f"  k = {self.k}")
        print(f"  Максимум сообщений M = {self.M}")
        print(f"  Вероятность неудачи для одного сообщения: {0.5 ** self.k:.2e}\n")

    def _is_quadratic_residue(self, value: int) -> bool:
        """Проверяет, является ли value квадратичным вычетом в F_p (включая 0)."""
        value = value % self.p
        if value == 0:
            return True
        legendre = pow(value, (self.p - 1) // 2, self.p)
        return legendre == 1

    def _sqrt_mod(self, value: int) -> Optional[int]:
        """
        Находит квадратный корень из value в F_p.
        Для p ≡ 3 mod 4 используется простая формула.
        """
        value = value % self.p
        if not self._is_quadratic_residue(value):
            return None

        if value == 0:
            return 0

        # Для p ≡ 3 mod 4: sqrt(a) = a ^ {(p + 1) / 4} mod p
        if self.p % 4 == 3:
            root = pow(value, (self.p + 1) // 4, self.p)
            # Проверяем, что это действительно корень
            if (root * root) % self.p == value:
                return root
        
        # Для p ≡ 1 mod 4 используем алгоритм Тонелли-Шенкса
        # Находим Q и S: p-1 = Q * 2 ^ S
        Q = self.p - 1
        S = 0
        while Q % 2 == 0:
            Q //= 2
            S += 1

        # Находим квадратичный невычет z
        z = 2
        while self._is_quadratic_residue(z):
            z += 1

        M = S
        c = pow(z, Q, self.p)
        t = pow(value, Q, self.p)
        R = pow(value, (Q + 1) // 2, self.p)

        while t != 1:
            # Находим наименьшее i (1 ≤ i < M) такое, что t ^ {2 ^ i} ≡ 1
            i = 1
            t2i = pow(t, 2, self.p)
            while t2i != 1 and i < M:
                t2i = pow(t2i, 2, self.p)
                i += 1

            b = pow(c, 1 << (M - i - 1), self.p)
            M = i
            c = (b * b) % self.p
            t = (t * c) % self.p
            R = (R * b) % self.p

        return R

    def encode(self, m: int) -> Optional[Point]:
        """
        Кодирует сообщение m (0 ≤ m < M) в точку на кривой.
        Возвращает точку или None, если ни одна из k попыток не удалась.
        """
        if not (0 <= m < self.M):
            raise ValueError(f"m должно быть в [0, {self.M - 1}], получено {m}")

        # Перебираем j = 1..k
        for j in range(1, self.k + 1):
            t = m * self.k + j
            x = t % self.p  # Простое отображение числа в элемент поля
            if x == 0:
                x = self.p - 1  # Избегаем 0

            # Вычисляем f(x) = x ^ 3 + a * x + b
            fx = (x * x * x + self.curve.a * x + self.curve.b) % self.p

            # Пытаемся извлечь квадратный корень
            y = self._sqrt_mod(fx)
            if y is not None:
                # Берем меньший корень для детерминированности
                y = min(y, self.p - y) % self.p
                return Point(x = x, y = y, curve = self.curve)

        return None

    def decode(self, point: Point) -> int:
        """
        Восстанавливает сообщение m из точки на кривой.
        """
        x = point.x
        # Находим t: для x != 0, t = x (так как мы отображали t -> t mod p)
        # Но нужно учесть, что 0 мы отображали в p-1
        if x == 0:
            t = self.p - 1
        else:
            t = x
        
        m = (t - 1) // self.k
        return m
    
    def encode_with_retry(self, m: int, max_retries: int = 3) -> Point:
        """
        Кодирует сообщение с повторными попытками при неудаче.
        При неудаче увеличиваем k (берем больше кандидатов).
        """
        for retry in range(max_retries):
            point = self.encode(m)
            if point is not None:
                return point
            # При неудаче увеличиваем k для следующей попытки
            old_k = self.k
            self.k = int(self.k * 1.5) + 1
            self.M = (self.p - 1) // self.k
            print(f"  Попытка {retry + 1} не удалась, увеличиваем k: {old_k} -> {self.k}")
        
        raise RuntimeError(f"Не удалось закодировать сообщение {m} после {max_retries} попыток")


def find_suitable_curve(p: int, k: int, num_messages: int) -> Tuple[EllipticCurve, int]:
    """
    Находит подходящую кривую и корректирует k для заданного количества сообщений.
    """
    # Убеждаемся, что p достаточно большое
    required_p = num_messages * k + 1
    if p < required_p:
        print(f"Предупреждение: поле F_{p} слишком мало для {num_messages} сообщений при k = {k}")
        print(f"Требуется p >= {required_p}")
        # Корректируем k
        new_k = (p - 1) // num_messages
        if new_k < 1:
            raise ValueError(f"Невозможно: даже с k = 1 требуется p >= {num_messages + 1}")
        print(f"Уменьшаем k до {new_k}")
        k = new_k
    
    # Простая кривая для примера
    curve = EllipticCurve(p, a = 2, b = 3)
    return curve, k


def main():
    print("=" * 70)
    print("Вероятностное кодирование сообщений в точки эллиптической кривой")
    print("=" * 70)
    
    # Параметры
    p = 97          # Поле F_97
    k = 20          # Количество попыток
    num_messages = 5  # Сколько сообщений хотим закодировать
    
    print(f"\nЗаданные параметры:")
    print(f"  Поле F_{p}")
    print(f"  k = {k}")
    print(f"  Количество сообщений для кодирования: {num_messages}")
    
    # Находим подходящую кривую
    try:
        curve, adjusted_k = find_suitable_curve(p, k, num_messages)
        if adjusted_k != k:
            print(f"  k скорректирован: {k} -> {adjusted_k}")
            k = adjusted_k
    except ValueError as e:
        print(f"Ошибка: {e}")
        return
    
    # Создаем кодировщик
    encoder = ProbabilisticEncoding(curve, k)
    
    # Проверяем, сколько сообщений можно закодировать
    if num_messages > encoder.M:
        print(f"\nПредупреждение: можно закодировать только {encoder.M} сообщений, но запрошено {num_messages}")
        num_messages = encoder.M
        print(f"Будет закодировано {num_messages} сообщений")
    
    # Тестируем кодирование
    print("-" * 70)
    print("Кодирование сообщений:")
    print("-" * 70)
    
    success_count = 0
    encoded_points = []
    
    for m in range(num_messages):
        point = encoder.encode(m)
        if point is not None:
            success_count += 1
            m_recovered = encoder.decode(point)
            status = "✓"
            encoded_points.append(point)
            print(f"{status} m = {m:3d} → точка {point} → восстановлено m = {m_recovered}")
        else:
            print(f"✗ m = {m:3d} → НЕ УДАЛОСЬ (вероятность {0.5 ** k:.2e})")
    
    # Статистика
    print("\n" + "-" * 70)
    print("Статистика:")
    print("-" * 70)
    print(f"Успешно закодировано: {success_count} / {num_messages}")
    print(f"Процент успеха: {100 * success_count / num_messages:.1f}%")
    print(f"Теоретическая вероятность неудачи: {0.5 ** k:.2e}")
    
    # Демонстрация влияния k на вероятность
    print("\n" + "-" * 70)
    print("Влияние параметра k на вероятность неудачи:")
    print("-" * 70)
    print("k\tВероятность неудачи\tПримерный смысл")
    print("-" * 70)
    for k_val in [10, 20, 30, 40, 50]:
        prob = 0.5 ** k_val
        if prob > 1e-3:
            desc = f"~{1 / prob:.0f} сообщений"
        elif prob > 1e-6:
            desc = f"1 на {1 / prob:.0f}"
        elif prob > 1e-9:
            desc = f"1 на {1 / prob:.0e}"
        else:
            desc = "пренебрежимо мала"
        print(f"{k_val}\t{prob:.2e}\t\t{desc}")
    
    # Демонстрация восстановления
    if encoded_points:
        print("\n" + "-" * 70)
        print("Проверка восстановления для всех успешно закодированных точек:")
        print("-" * 70)
        for i, point in enumerate(encoded_points):
            m = encoder.decode(point)
            print(f"Точка {point} → сообщение m = {m}")


if __name__ == "__main__":
    main()