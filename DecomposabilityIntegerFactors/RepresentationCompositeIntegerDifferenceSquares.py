# 1 . Представление целого составного числа в виде разности квцдратов
import math
from math import isqrt

def factor_fermat(n: int, k: int = 1, max_iter: int = 10000):
    """
    Факторизация числа n методом Ферма (обобщённым).
    
    Ищет представление k * n = t ^ 2 - s ^ 2, перебирая t начиная с ceil(sqrt(k * n)).
    
    Параметры:
        n: факторизуемое число
        k: множитель для сближения сомножителей (1, 2, 3, 5, 7, ...)
        max_iter: максимальное число итераций
        
    Возвращает:
        (a, b) — нетривиальные делители n (a <= b) или (n, 1) если не найдено
    """
    if n % 2 == 0:
        # Чётное число — тривиальный случай
        return (2, n // 2)
    
    target = k * n
    sqrt_target = isqrt(target)
    
    # Если target — полный квадрат, то k*n = t^2, тогда s=0 — особый случай
    if sqrt_target * sqrt_target == target:
        t = sqrt_target
        # k*n = t^2, значит n = t^2/k, но делители получаются через gcd
        # В общем случае этот случай редок.
    
    t = sqrt_target + 1
    for _ in range(max_iter):
        diff = t * t - target
        if diff < 0:
            t += 1
            continue
        
        s = isqrt(diff)
        if s * s == diff:
            # Нашли представление: k*n = t^2 - s^2 = (t - s)(t + s)
            a_candidate = t - s
            b_candidate = t + s
            
            # Извлекаем делители n
            from math import gcd
            d1 = gcd(n, a_candidate)
            d2 = gcd(n, b_candidate)
            
            if d1 != 1 and d1 != n:
                d2 = n // d1
                return (min(d1, d2), max(d1, d2))
            if d2 != 1 and d2 != n:
                d1 = n // d2
                return (min(d1, d2), max(d1, d2))
        
        t += 1
    
    # Не нашли разложение
    return (n, 1)


def factor_fermat_adaptive(n: int, max_k: int = 20, max_iter_per_k: int = 10000):
    """
    Пытается факторизовать n, перебирая небольшие значения k.
    """
    if n <= 3:
        return (n, 1)
    
    # Сначала проверяем малые делители (оптимизация)
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        if n % p == 0:
            return (p, n // p)
    
    # Перебираем k
    for k in [1, 2, 3, 5, 7, 11, 13, 17, 19]:
        if k > max_k:
            break
        a, b = factor_fermat(n, k, max_iter_per_k)
        if a != 1 and a != n:
            return (a, b)
    
    return (n, 1)


def main():
    # Примеры из текста
    examples = [4559, 223027]
    
    print("Факторизация методом Ферма (разность квадратов)")
    print("=" * 50)
    
    for n in examples:
        print(f"\nn = {n}")
        
        # Сначала пробуем классический метод Ферма (k=1)
        a, b = factor_fermat(n, k = 1, max_iter = 10000)
        if a != 1 and a != n:
            print(f"  k = 1: {n} = {a} * {b}")
        else:
            print(f"  k = 1: не удалось (возможно, множители далеки)")
            # Пробуем адаптивный поиск по k
            a, b = factor_fermat_adaptive(n, max_k = 20)
            if a != 1 and a != n:
                print(f"  адаптивный поиск: {n} = {a} * {b}")
            else:
                print(f"  не удалось разложить за разумное число шагов")
        
        # Демонстрация обобщённого метода для примера 44
        if n == 223027:
            print("\n  --- Проверка обобщённого метода с k = 5 (как в тексте) ---")
            a, b = factor_fermat(n, k = 5, max_iter = 10)
            if a != 1 and a != n:
                print(f"  5 * n = {5 * n}")
                print(f"  k = 5: {n} = {a} * {b}")


if __name__ == "__main__":
    main()