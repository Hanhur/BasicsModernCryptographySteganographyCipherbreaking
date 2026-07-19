# ROT13
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROT13 - программа для шифрования/дешифрования текста.
Основана на циклическом сдвиге букв английского алфавита на 13 позиций.
Цифры, знаки препинания и прочие символы остаются неизменными.
"""

import sys
import os

# Константы для английского алфавита (26 букв)
UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER = 'abcdefghijklmnopqrstuvwxyz'

# Сдвиг на 13 позиций (ROT13)
ROT13_UPPER = 'NOPQRSTUVWXYZABCDEFGHIJKLM'
ROT13_LOWER = 'nopqrstuvwxyzabcdefghijklm'


def rot13_char(char: str) -> str:
    """
    Преобразует один символ по правилам ROT13.
    Если символ не является буквой английского алфавита, возвращает его без изменений.
    """
    if 'A' <= char <= 'Z':
        # Находим индекс буквы в алфавите, прибавляем 13, берём остаток от деления на 26
        idx = ord(char) - ord('A')
        new_idx = (idx + 13) % 26
        return chr(ord('A') + new_idx)
    elif 'a' <= char <= 'z':
        idx = ord(char) - ord('a')
        new_idx = (idx + 13) % 26
        return chr(ord('a') + new_idx)
    else:
        return char


def rot13_string(text: str) -> str:
    """
    Применяет ROT13 ко всей строке.
    """
    return ''.join(rot13_char(c) for c in text)


def rot13_file(input_path: str, output_path: str = None) -> None:
    """
    Читает файл, применяет ROT13 и сохраняет результат.
    Если output_path не указан, добавляет суффикс .rot13 к исходному имени.
    """
    try:
        with open(input_path, 'r', encoding = 'utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_path}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)

    transformed = rot13_string(content)

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}.rot13{ext}"

    try:
        with open(output_path, 'w', encoding = 'utf-8') as f:
            f.write(transformed)
        print(f"Готово! Результат сохранён в: {output_path}")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")
        sys.exit(1)


def interactive_mode() -> None:
    """
    Интерактивный режим: пользователь вводит текст, программа выводит ROT13.
    Выход по команде 'exit' или Ctrl+C.
    """
    print("=" * 50)
    print("ROT13 - интерактивный режим")
    print("Введите текст для шифрования/дешифрования.")
    print("Для выхода введите 'exit' или нажмите Ctrl+C.")
    print("=" * 50)
    print("(Напоминание: ROT13 применяется дважды для возврата исходного текста)\n")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ('exit', 'quit', 'q'):
                print("До свидания!")
                break
            if not user_input:
                continue
            result = rot13_string(user_input)
            print(f"ROT13: {result}\n")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except EOFError:
            print("\nДо свидания!")
            break


def show_help() -> None:
    """Выводит справку по использованию программы."""
    print("""
ROT13 - программа для шифрования/дешифрования текста с помощью циклического сдвига на 13 позиций.

Использование:
    python rot13.py [режим] [аргументы]

Режимы:
    (без аргументов)          - Запуск в интерактивном режиме.
    -t "текст" или --text "текст" - Применить ROT13 к переданной строке.
    -f файл или --file файл   - Применить ROT13 к содержимому файла.
    -f файл -o файл           - Применить ROT13 к файлу и сохранить в указанный файл.
    -h или --help             - Показать эту справку.

Примеры:
    python rot13.py -t "HELLO World!"
    python rot13.py -f input.txt
    python rot13.py -f input.txt -o output.txt
    python rot13.py

Примечание: ROT13 является инволюцией (применение дважды возвращает исходный текст).
""")

def main() -> None:
    """Главная функция программы, обрабатывающая аргументы командной строки."""
    args = sys.argv[1:]

    if not args:
        interactive_mode()
        return

    # Обработка флагов
    if args[0] in ('-h', '--help'):
        show_help()
        return

    if args[0] in ('-t', '--text'):
        if len(args) < 2:
            print("Ошибка: после -t укажите текст в кавычках.")
            sys.exit(1)
        text = ' '.join(args[1:])  # Объединяем, если текст разбит на несколько аргументов
        # Если текст был в кавычках, он уже собран; если нет - объединяем с пробелами
        result = rot13_string(text)
        print(result)
        return

    if args[0] in ('-f', '--file'):
        if len(args) < 2:
            print("Ошибка: после -f укажите путь к файлу.")
            sys.exit(1)
        input_file = args[1]
        output_file = None

        # Проверяем, есть ли флаг -o для выходного файла
        if '-o' in args:
            o_index = args.index('-o')
            if o_index + 1 < len(args):
                output_file = args[o_index + 1]
            else:
                print("Ошибка: после -o укажите путь к выходному файлу.")
                sys.exit(1)

        rot13_file(input_file, output_file)
        return

    # Если аргументы не распознаны
    print(f"Неизвестный аргумент: {args[0]}")
    print("Используйте -h или --help для получения справки.")
    sys.exit(1)


if __name__ == "__main__":
    main()