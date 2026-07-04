# Шифр Шамира
import random
import math

def gcd_extended(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), где g = gcd(a, b) и a * x + b * y = g.
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd_extended(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inverse(a, m):
    """
    Находит обратное число к a по модулю m.
    Использует расширенный алгоритм Евклида.
    """
    g, x, _ = gcd_extended(a, m)
    if g != 1:
        raise ValueError(f"Число {a} не взаимно просто с {m}")
    return x % m

def generate_keys(p):
    """
    Генерирует пару ключей (c, d) для абонента,
    где c * d ≡ 1 (mod p - 1).
    c выбирается случайно взаимно простым с p - 1.
    """
    phi = p - 1
    # Выбираем c случайно среди нечётных чисел (так как p-1 чётно)
    while True:
        c = random.randrange(2, phi, 2)  # только нечётные числа
        if math.gcd(c, phi) == 1:
            break
    d = mod_inverse(c, phi)
    return c, d

def shamir_step(message, exponent, p):
    """
    Один шаг протокола Шамира: возведение в степень по модулю p.
    """
    return pow(message, exponent, p)

def shamir_protocol(m, p, cA, dA, cB, dB, verbose = True):
    """
    Полная реализация протокола Шамира.
    
    Параметры:
        m - исходное сообщение (число < p)
        p - простое число
        cA, dA - ключи абонента A
        cB, dB - ключи абонента B
        verbose - выводить ли промежуточные результаты
    
    Возвращает:
        x4 - расшифрованное сообщение (должно быть равно m)
    """
    if m >= p:
        raise ValueError(f"Сообщение m = {m} должно быть меньше p = {p}")
    
    # Шаг 1: A → B
    x1 = pow(m, cA, p)
    if verbose:
        print(f"Шаг 1: x1 = {m} ^ {cA} mod {p} = {x1}")
    
    # Шаг 2: B → A
    x2 = pow(x1, cB, p)
    if verbose:
        print(f"Шаг 2: x2 = {x1} ^ {cB} mod {p} = {x2}")
    
    # Шаг 3: A → B
    x3 = pow(x2, dA, p)
    if verbose:
        print(f"Шаг 3: x3 = {x2} ^ {dA} mod {p} = {x3}")
    
    # Шаг 4: B расшифровывает
    x4 = pow(x3, dB, p)
    if verbose:
        print(f"Шаг 4: x4 = {x3} ^ {dB} mod {p} = {x4}")
    
    return x4

def split_message(message, p):
    """
    Разбивает сообщение на блоки, каждый из которых меньше p.
    Возвращает список чисел.
    """
    if message < p:
        return [message]
    
    blocks = []
    # Преобразуем сообщение в строку и разбиваем посимвольно
    # (или можно использовать побайтовое разбиение)
    msg_str = str(message)
    block_size = len(str(p)) - 1
    
    for i in range(0, len(msg_str), block_size):
        block = int(msg_str[i:i + block_size])
        if block >= p:
            # Если блок всё ещё больше p, уменьшаем размер
            block = int(msg_str[i:i + block_size // 2])
        blocks.append(block)
    
    return blocks

def main():
    """
    Пример использования протокола Шамира.
    """
    print("=" * 60)
    print("ПРОТОКОЛ ШАМИРА - Бесключевая передача секрета")
    print("=" * 60)
    
    # 1. Выбор простого числа p
    # Для примера возьмём маленькое p, но в реальности p должно быть большим
    p = 23
    print(f"\nОткрытое простое число p = {p}")
    
    # 2. Генерация ключей для абонента A
    print("\n--- Генерация ключей для абонента A ---")
    cA, dA = generate_keys(p)
    print(f"cA = {cA}, dA = {dA}")
    print(f"Проверка: {cA} * {dA} mod {p - 1} = {(cA * dA) % (p - 1)}")
    
    # 3. Генерация ключей для абонента B
    print("\n--- Генерация ключей для абонента B ---")
    cB, dB = generate_keys(p)
    print(f"cB = {cB}, dB = {dB}")
    print(f"Проверка: {cB} * {dB} mod {p - 1} = {(cB * dB) % (p - 1)}")
    
    # 4. Исходное сообщение
    m = 10
    print(f"\nИсходное сообщение m = {m}")
    
    # 5. Выполнение протокола
    print("\n--- Выполнение протокола ---")
    result = shamir_protocol(m, p, cA, dA, cB, dB, verbose = True)
    
    # 6. Проверка результата
    print(f"\n{'=' * 60}")
    if result == m:
        print(f"✓ УСПЕХ! Сообщение успешно передано: {result}")
    else:
        print(f"✗ ОШИБКА! Получено {result}, ожидалось {m}")
    print("=" * 60)
    
    # 7. Дополнительный пример с блочной передачей
    print("\n\n--- Пример с блочной передачей ---")
    p_big = 97  # Большое простое число
    message_big = 123456789
    print(f"Сообщение: {message_big}, p = {p_big}")
    
    # Генерируем ключи для большого p
    cA2, dA2 = generate_keys(p_big)
    cB2, dB2 = generate_keys(p_big)
    print(f"Ключи A: cA = {cA2}, dA = {dA2}")
    print(f"Ключи B: cB = {cB2}, dB = {dB2}")
    
    # Разбиваем сообщение на блоки
    blocks = split_message(message_big, p_big)
    print(f"Блоки: {blocks}")
    
    # Передаём каждый блок
    decrypted_blocks = []
    for i, block in enumerate(blocks):
        print(f"\nПередача блока {i + 1}: {block}")
        decrypted = shamir_protocol(block, p_big, cA2, dA2, cB2, dB2, verbose = True)
        decrypted_blocks.append(decrypted)
    
    # Восстанавливаем сообщение
    recovered = int(''.join(str(b) for b in decrypted_blocks))
    print(f"\nВосстановленное сообщение: {recovered}")
    if recovered == message_big:
        print("✓ Блочная передача выполнена успешно!")
    else:
        print("✗ Ошибка в блочной передаче")

if __name__ == "__main__":
    # Для воспроизводимости результатов
    random.seed(42)
    main()