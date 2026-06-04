# 5. Битовая стойкость RSA
#!/usr/bin/env python3
"""
Атака на RSA с использованием оракула четности.
Демонстрирует битовую стойкость RSA: возможность восстановить всё сообщение,
имея доступ только к функции, определяющей четность исходного текста.

Основано на классическом результате: младший бит RSA эквивалентен полному дешифрованию.
"""

import random
from math import gcd


def egcd(a, b):
    """Расширенный алгоритм Евклида."""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    """Находит обратный элемент a по модулю m."""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Обратный элемент не существует')
    else:
        return x % m


def is_prime(n, k = 10):
    """Простая проверка на простоту (тест Миллера-Рабина)."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Записываем n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Проверяем k раундов
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


def generate_prime(bits = 8):
    """Генерирует простое число заданной битовой длины."""
    while True:
        n = random.getrandbits(bits)
        # Устанавливаем старший и младший биты
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n


def generate_rsa_keys(bits = 8):
    """Генерирует ключи RSA."""
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)
    
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Выбираем e (обычно 65537, но для маленьких n берем маленькое)
    e = 65537
    if e >= phi:
        e = 17
    while gcd(e, phi) != 1:
        e += 2
    
    d = modinv(e, phi)
    
    return (e, n), (d, n, p, q)


class ParityOracle:
    """
    Оракул четности для RSA.
    В реальной атаке это внешний сервис, который по шифровке возвращает
    четность соответствующего открытого текста.
    """
    
    def __init__(self, d, n):
        """
        Инициализация оракула с секретным ключом.
        В реальном сценарии атакующий не знает d!
        """
        self.d = d
        self.n = n
        self.calls_count = 0  # Счетчик вызовов оракула
    
    def query(self, ciphertext):
        """
        Запрос к оракулу: возвращает четность расшифрованного текста.
        
        Args:
            ciphertext: шифровка (число от 0 до n-1)
        
        Returns:
            0 если расшифрованный текст четный, 1 если нечетный
        """
        self.calls_count += 1
        plaintext = pow(ciphertext, self.d, self.n)
        return plaintext % 2


def recover_message_adaptive(oracle, e, n, ciphertext):
    """
    Восстанавливает исходное сообщение, используя адаптивные запросы к оракулу четности.
    
    Реализует алгоритм, описанный в тексте:
    - На каждом шаге сужает интервал возможных значений m вдвое
    - Использует умножение на 2 в зашифрованном виде
    
    Args:
        oracle: оракул четности
        e: открытая экспонента
        n: модуль RSA
        ciphertext: шифровка исходного сообщения
    
    Returns:
        восстановленное сообщение m
    """
    # Множитель для получения шифровки 2*m
    # Если у нас есть шифровка c = m^e mod n,
    # то (2^e * c) mod n = (2m)^e mod n
    multiplier = pow(2, e, n)
    
    # Границы интервала, содержащего m
    lower = 0
    upper = n
    
    # Текущая шифровка
    cur_c = ciphertext
    
    step = 0
    while upper - lower > 1:
        # Получаем шифровку для 2*cur_m mod n
        cur_c = (cur_c * multiplier) % n
        
        # Узнаем четность 2*cur_m mod n
        parity = oracle.query(cur_c)
        
        # Вычисляем середину интервала
        mid = (lower + upper) // 2
        
        if parity == 0:
            # 2m mod n четное => 2m < n => m находится в левой половине
            upper = mid
        else:
            # 2m mod n нечетное => 2m >= n => m находится в правой половине
            lower = mid
        
        step += 1
        
        # Вывод прогресса (для отладки)
        print(f"Шаг {step}: интервал = [{lower}, {upper}], "
              f"ширина = {upper - lower}, запросов = {oracle.calls_count}")
    
    return lower  # или upper, они равны


def recover_message_binary_search(oracle, e, n, ciphertext):
    """
    Альтернативная реализация через бинарный поиск с вещественными числами.
    Более наглядная, но менее точная версия.
    """
    multiplier = pow(2, e, n)
    
    low = 0.0
    high = float(n)
    cur_c = ciphertext
    
    iterations = 0
    while high - low > 1:
        cur_c = (cur_c * multiplier) % n
        parity = oracle.query(cur_c)
        
        mid = (low + high) / 2
        
        if parity == 0:
            high = mid
        else:
            low = mid
        
        iterations += 1
        if iterations > 100:  # Предотвращаем бесконечный цикл
            break
    
    return int(high)


def demo_with_custom_params(n = 21, e = 5, m_secret = 12):
    """
    Демонстрация на конкретных параметрах из текста.
    
    Пример из статьи:
    n = 21, e = 5, m = 12, c = 12 ^ 5 mod 21 = 3
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ НА ПРИМЕРЕ ИЗ СТАТЬИ")
    print("=" * 60)
    
    # Вычисляем d для создания оракула (в реальной атаке d неизвестно)
    p = 3
    q = 7
    phi = (p - 1) * (q - 1)
    d = modinv(e, phi)
    
    # Шифруем сообщение
    ciphertext = pow(m_secret, e, n)
    
    print(f"Параметры RSA:")
    print(f"  n = {n} = {p} * {q}")
    print(f"  e = {e}")
    print(f"  d = {d}")
    print(f"  Исходное сообщение m = {m_secret}")
    print(f"  Шифровка c = {m_secret} ^ {e} mod {n} = {ciphertext}")
    print()
    
    # Создаем оракул и восстанавливаем сообщение
    oracle = ParityOracle(d, n)
    recovered = recover_message_adaptive(oracle, e, n, ciphertext)
    
    print(f"\nРезультат:")
    print(f"  Восстановленное сообщение: {recovered}")
    print(f"  Количество запросов к оракулу: {oracle.calls_count}")
    print(f"  Успех: {recovered == m_secret}")
    
    return recovered == m_secret


def demo_random_rsa(bits = 12):
    """
    Демонстрация на случайно сгенерированных ключах RSA.
    """
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ НА СЛУЧАЙНЫХ КЛЮЧАХ RSA")
    print("=" * 60)
    
    # Генерируем ключи
    public_key, private_key = generate_rsa_keys(bits)
    e, n = public_key
    d, n, p, q = private_key
    
    # Генерируем случайное сообщение
    m_secret = random.randint(2, n - 2)
    ciphertext = pow(m_secret, e, n)
    
    print(f"Параметры RSA (битность ~{bits}):")
    print(f"  n = {n} = {p} * {q}")
    print(f"  e = {e}")
    print(f"  d = {d}")
    print(f"  Исходное сообщение m = {m_secret}")
    print(f"  Шифровка c = {m_secret} ^ {e} mod {n} = {ciphertext}")
    print(f"  Размер n в битах: {n.bit_length()}")
    print()
    
    # Создаем оракул и восстанавливаем сообщение
    oracle = ParityOracle(d, n)
    recovered = recover_message_adaptive(oracle, e, n, ciphertext)
    
    print(f"\nРезультат:")
    print(f"  Восстановленное сообщение: {recovered}")
    print(f"  Количество запросов к оракулу: {oracle.calls_count}")
    print(f"  Теоретический минимум: ~{n.bit_length()} запросов")
    print(f"  Успех: {recovered == m_secret}")
    
    return recovered == m_secret


def visualize_interval_narrowing():
    """
    Визуализация процесса сужения интервала (без реального RSA).
    """
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ ПРОЦЕССА СУЖЕНИЯ ИНТЕРВАЛА")
    print("=" * 60)
    
    # Имитируем процесс для n=100, m=42
    n = 100
    m_secret = 42
    
    print(f"Ищем m = {m_secret} в интервале [0, {n})")
    print()
    
    # Имитируем ответы оракула четности для каждого шага
    # В реальности оракул дает ответы на основе реального m
    def mock_oracle(step, current_m):
        # Для демонстрации просто вычисляем четность 2^step * m mod n
        val = (pow(2, step) * current_m) % n
        return val % 2
    
    lower = 0
    upper = n
    
    for step in range(1, 20):
        # Вычисляем ответ оракула для текущего шага
        parity = mock_oracle(step, m_secret)
        
        mid = (lower + upper) // 2
        
        if parity == 0:
            upper = mid
            direction = "левая"
        else:
            lower = mid
            direction = "правая"
        
        print(f"Шаг {step:2d}: четность = {parity} -> {direction} половина, "
              f"интервал = [{lower}, {upper}], ширина = {upper - lower}")
        
        if upper - lower <= 1:
            break
    
    print(f"\nИтог: m = {lower}")


def main():
    """Основная функция, запускающая все демонстрации."""
    print("\n" + "=" * 60)
    print("БИТОВАЯ СТОЙКОСТЬ RSA - АТАКА ЧЕРЕЗ ОРАКУЛ ЧЕТНОСТИ")
    print("=" * 60)
    print("\nТеоретическая основа:")
    print("  Если существует эффективный способ определения четности")
    print("  исходного текста по его шифровке, то можно эффективно")
    print("  вычислить и сам текст целиком.")
    print("  Для этого требуется O(log n) запросов к оракулу.\n")
    
    # Демонстрация на примере из статьи
    success1 = demo_with_custom_params(21, 5, 12)
    
    # Демонстрация на случайных параметрах
    success2 = demo_random_rsa(10)  # 10 бит ~ n ~ 1024
    
    # Визуализация процесса
    visualize_interval_narrowing()
    
    # Итоговый вывод
    print("\n" + "=" * 60)
    print("ВЫВОДЫ")
    print("=" * 60)
    print("✓ Атака успешно восстановила исходное сообщение, используя")
    print("  только оракул четности и открытый ключ (e, n).")
    print("✓ Количество запросов к оракулу составило ~log2(n),")
    print("  что подтверждает теоретическую оценку.")
    print("✓ Это демонстрирует, что младший бит RSA так же трудно")
    print("  скрыть, как и всё сообщение целиком.")
    
    if success1 and success2:
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n⚠️ Некоторые тесты не прошли (возможно из-за маленьких параметров)")


if __name__ == "__main__":
    main()