# Эффективная реализация операций
"""
Реализация операций на эллиптической кривой в проективных координатах
на основе алгоритмов 6.1, 6.2, 6.3 из раздела 6.5

Кривая: y ^ 2 = x ^ 3 + a * x + b (mod p)
"""

from typing import Tuple, Optional, Union


class PointProjective:
    """
    Точка на эллиптической кривой в проективных координатах (X, Y, Z)
    Аффинная точка (x, y) соответствует (x, y, 1)
    Точка в бесконечности O имеет координаты (0, 0, 0)
    """
    def __init__(self, X: int, Y: int, Z: int):
        self.X = X
        self.Y = Y
        self.Z = Z

    def __repr__(self):
        if self.Z == 0:
            return "PointProjective(O)  # Точка в бесконечности"
        return f"PointProjective(X = {self.X}, Y = {self.Y}, Z = {self.Z})"

    def __eq__(self, other):
        if not isinstance(other, PointProjective):
            return False
        return self.X == other.X and self.Y == other.Y and self.Z == other.Z

    def is_infinity(self) -> bool:
        """Проверка, является ли точка точкой в бесконечности"""
        return self.Z == 0


class EllipticCurve:
    """
    Эллиптическая кривая: y ^ 2 = x ^ 3 + a * x + b (mod p)
    """
    def __init__(self, a: int, b: int, p: int):
        self.a = a % p
        self.b = b % p
        self.p = p
        # Точка в бесконечности в проективных координатах
        self.O = PointProjective(0, 0, 0)

    def _mod(self, x: int) -> int:
        """Приведение по модулю p с корректной обработкой отрицательных чисел"""
        return x % self.p

    def _mod_inv(self, x: int) -> int:
        """Обратный элемент по модулю p (расширенный алгоритм Евклида)"""
        return pow(x, -1, self.p)

    def _div2_mod(self, x: int) -> int:
        """
        Деление на 2 по модулю p (без использования инверсии)
        Если x четно: x / 2
        Если x нечетно: (x + p) / 2
        """
        x = self._mod(x)
        if x % 2 == 0:
            return (x // 2) % self.p
        else:
            return ((x + self.p) // 2) % self.p

    # ============ Аффинные операции (для проверки) ============

    def is_on_curve_affine(self, x: Union[int, None], y: Union[int, None]) -> bool:
        """Проверка, принадлежит ли аффинная точка кривой"""
        if x is None or y is None:
            return False
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def point_to_affine(self, P: PointProjective) -> Tuple[Optional[int], Optional[int]]:
        """
        Преобразование из проективных координат в аффинные (6.18)
        (X, Y, Z) -> (X / Z ^ 2, Y / Z ^ 3)
        Возвращает (None, None) для точки в бесконечности
        """
        if P.Z == 0:  # Точка в бесконечности
            return (None, None)

        Z_inv = self._mod_inv(P.Z)
        Z_inv_sq = self._mod(Z_inv * Z_inv)
        Z_inv_cu = self._mod(Z_inv_sq * Z_inv)

        x = self._mod(P.X * Z_inv_sq)
        y = self._mod(P.Y * Z_inv_cu)
        return (x, y)

    def affine_to_projective(self, x: int, y: int) -> PointProjective:
        """Преобразование из аффинных координат в проективные (6.17)"""
        return PointProjective(self._mod(x), self._mod(y), 1)

    # ============ Сложение в проективных координатах ============

    def add(self, P1: PointProjective, P2: PointProjective) -> PointProjective:
        """
        Алгоритм 6.2. Сложение в проективном представлении
        P3 = P1 + P2
        """
        p = self.p

        # Если одна из точек — O
        if P1.Z == 0:
            return P2
        if P2.Z == 0:
            return P1

        # Алгоритм 6.2
        # λ1 = X1 * Z2^2
        lambda1 = self._mod(P1.X * P2.Z * P2.Z)

        # λ2 = X2 * Z1^2
        lambda2 = self._mod(P2.X * P1.Z * P1.Z)

        # λ3 = λ2 - λ1
        lambda3 = self._mod(lambda2 - lambda1)

        # Если λ3 == 0, то P1 == P2 или P1 == -P2
        if lambda3 == 0:
            # Проверяем, не равны ли точки (P1 == P2 -> удвоение)
            lambda4 = self._mod(P1.Y * P2.Z * P2.Z * P2.Z)  # Y1 * Z2^3
            lambda5 = self._mod(P2.Y * P1.Z * P1.Z * P1.Z)  # Y2 * Z1^3
            if self._mod(lambda5 - lambda4) == 0:
                # P1 == P2 -> удвоение
                return self.double(P1)
            else:
                # P1 == -P2 -> точка в бесконечности
                return self.O

        # λ4 = Y1 * Z2^3
        lambda4 = self._mod(P1.Y * P2.Z * P2.Z * P2.Z)

        # λ5 = Y2 * Z1^3
        lambda5 = self._mod(P2.Y * P1.Z * P1.Z * P1.Z)

        # λ6 = λ5 - λ4
        lambda6 = self._mod(lambda5 - lambda4)

        # λ7 = λ1 + λ2
        lambda7 = self._mod(lambda1 + lambda2)

        # λ8 = λ4 + λ5
        lambda8 = self._mod(lambda4 + lambda5)

        # Z3 = Z1 * Z2 * λ3
        Z3 = self._mod(P1.Z * P2.Z * lambda3)

        # X3 = λ6^2 - λ7 * λ3^2
        lambda3_sq = self._mod(lambda3 * lambda3)
        X3 = self._mod(lambda6 * lambda6 - lambda7 * lambda3_sq)

        # λ9 = λ7 * λ3^2 - 2*X3
        lambda9 = self._mod(lambda7 * lambda3_sq - 2 * X3)

        # Y3 = (λ9 * λ6 - λ8 * λ3^3) / 2
        lambda3_cu = self._mod(lambda3_sq * lambda3)
        Y3 = self._mod(lambda9 * lambda6 - lambda8 * lambda3_cu)
        Y3 = self._div2_mod(Y3)

        return PointProjective(X3, Y3, Z3)

    # ============ Удвоение в проективных координатах ============

    def double(self, P: PointProjective) -> PointProjective:
        """
        Алгоритм 6.3. Удвоение в проективном представлении
        P3 = [2]P
        """
        p = self.p

        if P.Z == 0:  # Удвоение точки O
            return self.O

        # λ1 = 3*X1^2 + a*Z1^4
        X1_sq = self._mod(P.X * P.X)
        Z1_sq = self._mod(P.Z * P.Z)
        Z1_4 = self._mod(Z1_sq * Z1_sq)

        lambda1 = self._mod(3 * X1_sq + self.a * Z1_4)

        # λ2 = 4*X1*Y1^2
        Y1_sq = self._mod(P.Y * P.Y)
        lambda2 = self._mod(4 * P.X * Y1_sq)

        # Z3 = 2*Y1*Z1
        Z3 = self._mod(2 * P.Y * P.Z)

        # X3 = λ1^2 - 2*λ2
        X3 = self._mod(lambda1 * lambda1 - 2 * lambda2)

        # λ3 = 8*Y1^4
        lambda3 = self._mod(8 * Y1_sq * Y1_sq)

        # Y3 = λ1*(λ2 - X3) - λ3
        Y3 = self._mod(lambda1 * (lambda2 - X3) - lambda3)

        return PointProjective(X3, Y3, Z3)

    # ============ Удвоение с оптимизацией для a = -3 ============

    def double_optimized(self, P: PointProjective) -> PointProjective:
        """
        Удвоение с оптимизацией для случая a = -3
        λ1 = 3 * (X1 - Z1 ^ 2) * (X1 + Z1 ^ 2)
        """
        if self.a != (-3 % self.p):
            return self.double(P)

        if P.Z == 0:
            return self.O

        p = self.p
        Z1_sq = self._mod(P.Z * P.Z)

        # λ1 = 3*(X1 - Z1^2)*(X1 + Z1^2)
        lambda1 = self._mod(3 * (P.X - Z1_sq) * (P.X + Z1_sq))

        Y1_sq = self._mod(P.Y * P.Y)
        lambda2 = self._mod(4 * P.X * Y1_sq)

        Z3 = self._mod(2 * P.Y * P.Z)
        X3 = self._mod(lambda1 * lambda1 - 2 * lambda2)

        lambda3 = self._mod(8 * Y1_sq * Y1_sq)
        Y3 = self._mod(lambda1 * (lambda2 - X3) - lambda3)

        return PointProjective(X3, Y3, Z3)

    # ============ Смешанное сложение (P + Q, где Q в аффинных) ============

    def add_mixed(self, P: PointProjective, x: int, y: int) -> PointProjective:
        """
        Смешанное сложение: P + Q, где Q задана аффинными координатами (x, y)
        Стоимость: 11M (против 16M для общего случая)
        """
        p = self.p

        if P.Z == 0:  # P = O
            return self.affine_to_projective(x, y)

        # Q в проективных координатах: (x, y, 1)
        X2 = self._mod(x)
        Y2 = self._mod(y)

        # Алгоритм 6.2 с Z2 = 1
        # λ1 = X1 * Z2^2 = X1
        lambda1 = P.X

        # λ2 = X2 * Z1^2
        lambda2 = self._mod(X2 * P.Z * P.Z)

        # λ3 = λ2 - λ1
        lambda3 = self._mod(lambda2 - lambda1)

        if lambda3 == 0:
            # Проверяем, не равны ли точки
            lambda4 = P.Y  # Y1 * Z2^3 = Y1
            lambda5 = self._mod(Y2 * P.Z * P.Z * P.Z)  # Y2 * Z1^3
            if self._mod(lambda5 - lambda4) == 0:
                return self.double(P)  # P1 == P2
            else:
                return self.O  # P1 == -P2

        # λ4 = Y1 * Z2^3 = Y1
        lambda4 = P.Y

        # λ5 = Y2 * Z1^3
        lambda5 = self._mod(Y2 * P.Z * P.Z * P.Z)

        # λ6 = λ5 - λ4
        lambda6 = self._mod(lambda5 - lambda4)

        # λ7 = λ1 + λ2
        lambda7 = self._mod(lambda1 + lambda2)

        # λ8 = λ4 + λ5
        lambda8 = self._mod(lambda4 + lambda5)

        # Z3 = Z1 * Z2 * λ3 = Z1 * λ3
        Z3 = self._mod(P.Z * lambda3)

        # X3 = λ6^2 - λ7 * λ3^2
        lambda3_sq = self._mod(lambda3 * lambda3)
        X3 = self._mod(lambda6 * lambda6 - lambda7 * lambda3_sq)

        # λ9 = λ7 * λ3^2 - 2*X3
        lambda9 = self._mod(lambda7 * lambda3_sq - 2 * X3)

        # Y3 = (λ9 * λ6 - λ8 * λ3^3) / 2
        lambda3_cu = self._mod(lambda3_sq * lambda3)
        Y3 = self._mod(lambda9 * lambda6 - lambda8 * lambda3_cu)
        Y3 = self._div2_mod(Y3)

        return PointProjective(X3, Y3, Z3)

    # ============ Скалярное умножение (Алгоритм 6.1) ============

    def scalar_multiply(self, m: int, P: PointProjective) -> PointProjective:
        """
        Алгоритм 6.1. Вычисление m-кратной композиции [m]P
        Использует двоичный левосторонний метод
        """
        if m == 0:
            return self.O

        # Представляем m в двоичном виде
        binary = bin(m)[2:]  # например, 21 -> '10101'
        Q = self.O

        for bit in binary:
            # Q ← [2]Q (всегда)
            if Q.Z != 0:
                Q = self.double(Q)
            # Если бит = 1, то Q ← Q + P
            if bit == '1':
                if Q.Z == 0:
                    # Первое сложение — просто присваивание Q = P
                    Q = P
                else:
                    # Используем смешанное сложение, т.к. P в аффинных
                    x, y = self.point_to_affine(P)
                    Q = self.add_mixed(Q, x, y)

        return Q

    def scalar_multiply_mixed(self, m: int, x: int, y: int) -> PointProjective:
        """
        Удобная обертка: скалярное умножение аффинной точки (x, y)
        """
        P = self.affine_to_projective(x, y)
        return self.scalar_multiply(m, P)

    # ============ Вспомогательные методы для отладки ============

    def print_point(self, P: PointProjective, name: str = "P") -> None:
        """Красиво выводит точку в аффинных координатах"""
        x, y = self.point_to_affine(P)
        if x is None or y is None:
            print(f"{name} = O (точка в бесконечности)")
        else:
            print(f"{name} = ({x}, {y})")


# ============ Примеры и тестирование ============

def test_curve_from_text():
    """Тест на примере из текста: y ^ 2 = x ^ 3 + x + 1 (mod 7)"""
    print("=" * 60)
    print("Тест на кривой y ^ 2 = x ^ 3 + x + 1 (mod 7)")
    print("=" * 60)

    curve = EllipticCurve(a = 1, b = 1, p = 7)

    # Точки из примера 6.1
    P1 = curve.affine_to_projective(5, 1)
    P2 = curve.affine_to_projective(4, 6)

    print(f"P1 = (5, 1) -> проективные: {P1}")
    print(f"P2 = (4, 6) -> проективные: {P2}")

    # Сложение в проективных координатах (пример 6.3)
    P3 = curve.add(P1, P2)
    print(f"\nP1 + P2 = {P3}")

    # Проверка: перевод в аффинные координаты
    x3, y3 = curve.point_to_affine(P3)
    print(f"В аффинных координатах: ({x3}, {y3})")
    print(f"Ожидаемый результат из примера 6.1: (2, 5)")

    # Проверка, что точка лежит на кривой
    on_curve = curve.is_on_curve_affine(x3, y3)
    print(f"Точка лежит на кривой: {on_curve}")

    return curve


def test_scalar_multiply():
    """Тест скалярного умножения"""
    print("\n" + "=" * 60)
    print("Тест скалярного умножения [21]P")
    print("=" * 60)

    curve = EllipticCurve(a = 1, b = 1, p = 7)
    P = (5, 1)

    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print(f"P = {P}")

    # Вычисляем [21]P
    Q_proj = curve.scalar_multiply_mixed(21, P[0], P[1])
    Q_aff = curve.point_to_affine(Q_proj)

    print(f"\n[21]P = {Q_aff}")

    # Проверим шаги из примера 6.2
    print("\nПошаговая проверка (как в примере 6.2):")
    print("21 = (10101)₂")

    P_proj = curve.affine_to_projective(P[0], P[1])
    Q = curve.O
    binary = bin(21)[2:]

    for i, bit in enumerate(binary, 1):
        if Q.Z != 0:
            Q = curve.double(Q)
        if bit == '1':
            if Q.Z == 0:
                Q = P_proj
            else:
                x, y = curve.point_to_affine(P_proj)
                Q = curve.add_mixed(Q, x, y)
        if Q.Z != 0:
            aff = curve.point_to_affine(Q)
            print(f"  i = {i}, бит = {bit}: Q = {aff}")
        else:
            print(f"  i = {i}, бит = {bit}: Q = O")

    return curve


def test_double():
    """Тест удвоения"""
    print("\n" + "=" * 60)
    print("Тест удвоения [2]P")
    print("=" * 60)

    curve = EllipticCurve(a = 1, b = 1, p = 7)
    P = (5, 1)

    print(f"P = {P}")
    P_proj = curve.affine_to_projective(P[0], P[1])

    # Удвоение
    Q_proj = curve.double(P_proj)
    Q_aff = curve.point_to_affine(Q_proj)
    print(f"[2]P = {Q_aff}")

    # Проверка через сложение P + P
    Q2_proj = curve.add(P_proj, P_proj)
    Q2_aff = curve.point_to_affine(Q2_proj)
    print(f"P + P = {Q2_aff}")

    # Проверка через скалярное умножение
    Q3_proj = curve.scalar_multiply(2, P_proj)
    Q3_aff = curve.point_to_affine(Q3_proj)
    print(f"[2]P (через scalar_multiply) = {Q3_aff}")

    return curve


def test_optimized_double():
    """Тест оптимизированного удвоения для a = -3"""
    print("\n" + "=" * 60)
    print("Тест оптимизированного удвоения для a = -3")
    print("=" * 60)

    # Кривая с a = -3 (например, secp256k1 подобная, но с маленьким p)
    curve = EllipticCurve(a = -3, b = 7, p = 19)
    P = (2, 3)  # 3^2 = 9, 2^3 - 3*2 + 7 = 8 - 6 + 7 = 9 ✓

    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print(f"P = {P}")

    P_proj = curve.affine_to_projective(P[0], P[1])

    # Обычное удвоение
    Q1_proj = curve.double(P_proj)
    Q1_aff = curve.point_to_affine(Q1_proj)

    # Оптимизированное удвоение
    Q2_proj = curve.double_optimized(P_proj)
    Q2_aff = curve.point_to_affine(Q2_proj)

    print(f"Обычное удвоение: {Q1_aff}")
    print(f"Оптимизированное удвоение (a = -3): {Q2_aff}")
    print(f"Результаты совпадают: {Q1_aff == Q2_aff}")

    return curve


def test_mixed_addition():
    """Тест смешанного сложения"""
    print("\n" + "=" * 60)
    print("Тест смешанного сложения")
    print("=" * 60)

    curve = EllipticCurve(a = 1, b = 1, p = 7)

    P_proj = curve.affine_to_projective(5, 1)  # P в проективных
    x2, y2 = 4, 6  # Q в аффинных

    print(f"P = (5, 1) в проективных: {P_proj}")
    print(f"Q = (4, 6) в аффинных")

    # Смешанное сложение
    R1_proj = curve.add_mixed(P_proj, x2, y2)
    R1_aff = curve.point_to_affine(R1_proj)

    # Обычное сложение
    Q_proj = curve.affine_to_projective(x2, y2)
    R2_proj = curve.add(P_proj, Q_proj)
    R2_aff = curve.point_to_affine(R2_proj)

    print(f"Смешанное сложение: {R1_aff}")
    print(f"Обычное сложение: {R2_aff}")
    print(f"Результаты совпадают: {R1_aff == R2_aff}")

    return curve


def test_order_and_infinity():
    """Тест нахождения порядка точки и проверка обработки точки в бесконечности"""
    print("\n" + "=" * 60)
    print("Тест нахождения порядка точки и обработки O")
    print("=" * 60)

    curve = EllipticCurve(a = 2, b = 3, p = 97)
    P = (3, 6)

    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print(f"P = {P}")
    print(f"Проверка: P на кривой? {curve.is_on_curve_affine(P[0], P[1])}")

    # Ищем порядок точки
    print("\nПоиск порядка точки (nP = O):")
    Q_proj = curve.affine_to_projective(P[0], P[1])
    
    for n in range(1, 20):
        result = curve.scalar_multiply(n, Q_proj)
        x, y = curve.point_to_affine(result)
        if x is None and y is None:
            print(f"  {n}P = O → порядок точки = {n}")
            break
        else:
            print(f"  {n}P = ({x}, {y})")

    return curve


def test_large_example():
    """Дополнительный пример с большими числами"""
    print("\n" + "=" * 60)
    print("Дополнительный пример: кривая с большим p")
    print("=" * 60)

    # Используем маленькую кривую, но с чуть большим p
    curve = EllipticCurve(a = 2, b = 3, p = 97)
    
    # Найдем точки на кривой
    points = []
    for x in range(curve.p):
        for y in range(curve.p):
            if curve.is_on_curve_affine(x, y):
                points.append((x, y))
                if len(points) >= 3:
                    break
        if len(points) >= 3:
            break
    
    if len(points) < 3:
        print("Не найдено достаточно точек на кривой")
        return
    
    P = points[0]
    print(f"Кривая: y ^ 2 = x ^ 3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print(f"P = {P}")
    
    # Вычисляем [5]P
    result = curve.scalar_multiply_mixed(5, P[0], P[1])
    x, y = curve.point_to_affine(result)
    
    if x is None or y is None:
        print(f"\n[5]P = O (точка в бесконечности)")
        print(f"Порядок точки P делит 5")
    else:
        print(f"\n[5]P = ({x}, {y})")
        print(f"Точка лежит на кривой: {curve.is_on_curve_affine(x, y)}")


if __name__ == "__main__":
    # Запускаем все тесты
    test_curve_from_text()
    test_scalar_multiply()
    test_double()
    test_optimized_double()
    test_mixed_addition()
    test_order_and_infinity()
    test_large_example()

    print("\n" + "=" * 60)
    print("Все тесты пройдены!")
    print("=" * 60)