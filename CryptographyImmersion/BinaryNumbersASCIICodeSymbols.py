# Двоичные числа, код ASCII и условные обозначения
# Программа для работы с двоичными числами и кодом ASCII
# Без использования numpy

def decimal_to_binary(decimal_num):
    """
    Перевод числа из десятичной системы в двоичную
    с использованием деления с остатком
    """
    if decimal_num == 0:
        return "0"
    
    binary_digits = []
    num = decimal_num
    
    print(f"Деление числа {num} на 2 с остатком:")
    while num > 0:
        remainder = num % 2
        quotient = num // 2
        binary_digits.append(str(remainder))
        print(f"{num} ÷ 2 = {quotient}, остаток {remainder}")
        num = quotient
    
    # Читаем остатки снизу вверх
    binary_result = ''.join(reversed(binary_digits))
    print(f"\nРезультат: {decimal_num}₁₀ = {binary_result}₂")
    return binary_result


def binary_to_decimal(binary_str):
    """
    Перевод числа из двоичной системы в десятичную
    """
    decimal_num = 0
    power = len(binary_str) - 1
    
    for digit in binary_str:
        if digit == '1':
            decimal_num += 2 ** power
        power -= 1
    
    return decimal_num


def ascii_to_binary(char):
    """
    Перевод символа в двоичный ASCII-код (7 бит)
    """
    ascii_code = ord(char)
    binary = decimal_to_binary(ascii_code)
    # Дополняем до 7 бит
    binary_7bit = binary.zfill(7)
    return ascii_code, binary_7bit


def binary_to_ascii(binary_str):
    """
    Перевод двоичного ASCII-кода в символ
    """
    decimal = binary_to_decimal(binary_str)
    return chr(decimal)


def text_to_ascii_binary(text):
    """
    Перевод целого текста в ASCII-коды и двоичные представления
    """
    print(f"\n{'=' * 60}")
    print(f"Текст: '{text}'")
    print(f"{'=' * 60}")
    print(f"{'Символ':<8} {'ASCII (дес.)':<12} {'Двоичный код (7 бит)':<20} {'Шестнадцатеричный':<16}")
    print("-" * 60)
    
    result = []
    for char in text:
        ascii_code = ord(char)
        binary = decimal_to_binary(ascii_code).zfill(7)
        hex_code = hex(ascii_code)[2:].upper().zfill(2)
        print(f"{char:<8} {ascii_code:<12} {binary:<20} {hex_code:<16}")
        result.append({
            'char': char,
            'ascii': ascii_code,
            'binary': binary,
            'hex': hex_code
        })
    
    return result


def ascii_table():
    """
    Вывод таблицы ASCII для первых 32 управляющих символов и печатных символов
    """
    print("\n" + "=" * 80)
    print("ТАБЛИЦА ASCII (первые 32 символа)")
    print("=" * 80)
    print(f"{'Код':<6} {'Двоичный':<12} {'Символ':<10} {'Описание'}")
    print("-" * 80)
    
    # Управляющие символы (0-31)
    control_names = [
        'NUL', 'SOH', 'STX', 'ETX', 'EOT', 'ENQ', 'ACK', 'BEL',
        'BS', 'TAB', 'LF', 'VT', 'FF', 'CR', 'SO', 'SI',
        'DLE', 'DC1', 'DC2', 'DC3', 'DC4', 'NAK', 'SYN', 'ETB',
        'CAN', 'EM', 'SUB', 'ESC', 'FS', 'GS', 'RS', 'US'
    ]
    
    for i in range(32):
        binary = decimal_to_binary(i).zfill(7)
        # Непечатаемые символы
        print(f"{i:<6} {binary:<12} {' ':<10} {control_names[i]}")
    
    print("\n" + "=" * 80)
    print("ПЕЧАТНЫЕ СИМВОЛЫ ASCII (32 - 126)")
    print("=" * 80)
    
    # Печатные символы (32-126)
    for i in range(32, 127):
        binary = decimal_to_binary(i).zfill(7)
        char = chr(i)
        if i == 32:
            char_name = 'ПРОБЕЛ'
        elif i == 127:
            char_name = 'DEL'
        else:
            char_name = char
        
        # Вывод по 8 символов в строке
        if (i - 32) % 8 == 0:
            print()
        print(f"{i:<6} {binary:<12} {char_name:<10}", end = " | ")
    
    print("\n")


def compare_number_systems():
    """
    Сравнение разных систем счисления
    """
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ СИСТЕМ СЧИСЛЕНИЯ")
    print("=" * 60)
    print(f"{'Десятичная':<12} {'Двоичная':<12} {'Восьмеричная':<14} {'Шестнадцатеричная'}")
    print("-" * 60)
    
    for i in range(0, 33):
        binary = decimal_to_binary(i).zfill(7)
        octal = oct(i)[2:]
        hexa = hex(i)[2:].upper()
        print(f"{i:<12} {binary:<12} {octal:<14} {hexa:<16}")


def main():
    """
    Главная функция программы
    """
    print("=" * 70)
    print("ПРОГРАММА ДЛЯ РАБОТЫ С ДВОИЧНЫМИ ЧИСЛАМИ И ASCII")
    print("=" * 70)
    
    while True:
        print("\nВыберите действие:")
        print("1. Перевод десятичного числа в двоичное")
        print("2. Перевод двоичного числа в десятичное")
        print("3. Перевод символа в ASCII (двоичный код)")
        print("4. Перевод текста в ASCII (двоичные коды)")
        print("5. Показать таблицу ASCII")
        print("6. Сравнение систем счисления")
        print("7. Выход")
        
        choice = input("\nВаш выбор (1 - 7): ")
        
        if choice == '1':
            try:
                num = int(input("Введите десятичное число: "))
                if num < 0:
                    print("Пожалуйста, введите неотрицательное число.")
                    continue
                decimal_to_binary(num)
            except ValueError:
                print("Ошибка: введите целое число!")
        
        elif choice == '2':
            binary_str = input("Введите двоичное число (только 0 и 1): ")
            if all(c in '01' for c in binary_str):
                decimal = binary_to_decimal(binary_str)
                print(f"{binary_str}₂ = {decimal}₁₀")
            else:
                print("Ошибка: введите число, состоящее только из 0 и 1!")
        
        elif choice == '3':
            char = input("Введите один символ: ")
            if len(char) == 1:
                ascii_code, binary = ascii_to_binary(char)
                print(f"Символ '{char}':")
                print(f"  ASCII (десятичный): {ascii_code}")
                print(f"  ASCII (двоичный):   {binary}")
                print(f"  ASCII (шестнадцатеричный): {hex(ascii_code)[2:].upper()}")
            else:
                print("Ошибка: введите ровно один символ!")
        
        elif choice == '4':
            text = input("Введите текст: ")
            if text:
                text_to_ascii_binary(text)
            else:
                print("Ошибка: текст не может быть пустым!")
        
        elif choice == '5':
            ascii_table()
        
        elif choice == '6':
            compare_number_systems()
        
        elif choice == '7':
            print("До свидания!")
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()