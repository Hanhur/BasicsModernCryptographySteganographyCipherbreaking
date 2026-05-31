# 4. Оцифровка конечных полей
def element_to_number(coeffs, p):
    """
    Преобразует элемент поля F_{p^r} в число (стандартная оцифровка).

    coeffs: список коэффициентов [a_{r - 1}, a_{r - 2}, ..., a_0] (длина r) каждый a_i от 0 до p - 1.
    p: характеристика поля (простое число).

    Возвращает целое число от 0 до p ^ r - 1.
    """
    r = len(coeffs)
    number = 0
    # coeffs[0] = a_{r-1} (старший коэффициент)
    # coeffs[-1] = a_0 (свободный член)
    for i, a in enumerate(reversed(coeffs)):
        # i = 0 -> a_0 * p ^ 0
        # i = 1 -> a_1 * p ^ 1, ...
        number += a * (p ** i)
    return number


def number_to_element(number, p, r):
    """
    Преобразует число (от 0 до p^r - 1) в элемент поля F_{p ^ r}
    в виде списка коэффициентов [a_{r - 1}, ..., a_0].

    number: целое число.
    p: характеристика поля.
    r: степень расширения.

    Возвращает список длины r с коэффициентами a_i из Z_p.
    """
    coeffs_reversed = []  # сначала младший коэффициент a_0
    n = number
    for _ in range(r):
        coeffs_reversed.append(n % p)
        n //= p
    # coeffs_reversed = [a_0, a_1, ..., a_{r - 1}]
    # Восстанавливаем [a_{r - 1}, ..., a_0]
    coeffs = coeffs_reversed[::-1]
    return coeffs


def print_element(coeffs):
    """
    Красиво выводит многочлен.
    coeffs: [a_{r - 1}, ..., a_0]
    """
    r = len(coeffs)
    terms = []
    for i, a in enumerate(reversed(coeffs)):
        power = i
        if a == 0:
            continue
        if power == 0:
            term = str(a)
        elif power == 1:
            term = f"{a} * x"
        else:
            term = f"{a} * x ^ {power}"
        terms.append(term)
    if not terms:
        print("0")
    else:
        print(" + ".join(terms[::-1]))  # старшая степень слева


if __name__ == "__main__":
    # Пример из текста для p=2, r=3
    print("=== Пример: F_{2 ^ 3} ===")
    p = 2
    r = 3
    coeffs_example = [1, 0, 1]  # x ^ 2 + 1
    num = element_to_number(coeffs_example, p)
    print(f"Элемент: {coeffs_example} -> многочлен: ", end = "")
    print_element(coeffs_example)
    print(f"Номер (стандартная оцифровка): {num}")

    # Обратно
    reconstructed = number_to_element(num, p, r)
    print(f"Число {num} -> элемент: {reconstructed}")

    # Проверка всех элементов поля F_{3 ^ 2}
    print("\n=== Все элементы F_{3 ^ 2} (p = 3, r = 2) ===")
    p2 = 3
    r2 = 2
    print(f"Все числа от 0 до {p2 ** r2 - 1}:")
    for n in range(p2 ** r2):
        coeffs = number_to_element(n, p2, r2)
        print(f"{n:2} -> {coeffs} -> ", end = "")
        print_element(coeffs)