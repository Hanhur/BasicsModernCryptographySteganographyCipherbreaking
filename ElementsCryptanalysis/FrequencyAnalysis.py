# 3. Частотный анализ
import re
from collections import Counter

# Эталонные частоты букв русского языка (в процентах)
# Источник: из вашего текста (буква 'ё' отдельно, но обычно сливают с 'е')
RUSSIAN_FREQ = {
    'а': 7.96, 'б': 1.67, 'в': 4.71, 'г': 1.87, 'д': 3.07, 'е': 8.90, 'ё': 0.11,
    'ж': 1.18, 'з': 1.74, 'и': 6.38, 'й': 0.98, 'к': 3.25, 'л': 4.64, 'м': 3.13,
    'н': 6.70, 'о': 11.26, 'п': 2.71, 'р': 3.90, 'с': 5.32, 'т': 6.31, 'у': 2.63,
    'ф': 0.18, 'х': 0.73, 'ц': 0.29, 'ч': 1.91, 'ш': 0.82, 'щ': 0.29, 'ъ': 0.03,
    'ы': 1.73, 'ь': 2.25, 'э': 0.36, 'ю': 0.60, 'я': 2.39
}

# Сортируем буквы по убыванию частоты
RUSSIAN_LETTERS_BY_FREQ = [letter for letter, _ in sorted(RUSSIAN_FREQ.items(), key = lambda x: x[1], reverse = True)]

def load_ciphertext(filename="ciphertext.txt"):
    """Загружает зашифрованный текст из файла."""
    with open(filename, 'r', encoding = 'utf-8') as f:
        return f.read()

def get_freq_analysis(text):
    """Подсчёт частот символов в тексте (только кириллица)."""
    # Оставляем только русские буквы (включая ё)
    letters_only = re.findall(r'[а-яё]', text.lower())
    total = len(letters_only)
    if total == 0:
        return {}
    freq = Counter(letters_only)
    # Преобразуем в проценты
    freq_percent = {ch: (count / total) * 100 for ch, count in freq.items()}
    return freq_percent, freq

def suggest_mapping(cipher_freq_percent):
    """
    Предлагает начальное отображение:
    самая частая буква шифротекста -> самая частая буква русского языка и т.д.
    """
    sorted_cipher_letters = sorted(cipher_freq_percent.items(), key = lambda x: x[1], reverse = True)
    mapping = {}
    for (cipher_char, _), plain_char in zip(sorted_cipher_letters, RUSSIAN_LETTERS_BY_FREQ):
        mapping[cipher_char] = plain_char
    return mapping

def decrypt_with_mapping(text, mapping):
    """Расшифровывает текст с использованием отображения."""
    result = []
    for ch in text.lower():
        if ch in mapping:
            result.append(mapping[ch])
        else:
            result.append(ch)  # пробелы, знаки препинания, иные символы оставляем как есть
    return ''.join(result)

def interactive_refine(mapping, ciphertext, plaintext_sample):
    """
    Интерактивное уточнение отображения.
    Пользователь видит текущий расшифрованный фрагмент и может ввести
    пары вида "к=о" или "б=е", чтобы исправить подстановку.
    """
    current_mapping = mapping.copy()
    current_decrypted = decrypt_with_mapping(ciphertext, current_mapping)
    
    print("\n" + "=" * 70)
    print("ТЕКУЩЕЕ РАСШИФРОВАННОЕ СООБЩЕНИЕ (фрагмент):")
    print("=" * 70)
    print(current_decrypted[:500] + "..." if len(current_decrypted) > 500 else current_decrypted)
    print("=" * 70)
    
    while True:
        print("\nКоманды:")
        print("  введите пару вида 'к=о' (шифробуква=расшифровка)")
        print("  'list' — показать текущие отображения")
        print("  'reset' — сбросить все отображения")
        print("  'save' — сохранить текущий расшифрованный текст в файл")
        print("  'exit' — завершить")
        cmd = input("> ").strip().lower()
        
        if cmd == 'exit':
            break
        elif cmd == 'list':
            print("\nТекущие отображения:")
            for c, p in sorted(current_mapping.items()):
                print(f"  {c} -> {p}")
        elif cmd == 'reset':
            current_mapping = suggest_mapping(get_freq_analysis(ciphertext)[0])
            print("Отображения сброшены к начальным частотным.")
        elif cmd == 'save':
            filename = input("Имя файла для сохранения: ").strip()
            with open(filename, 'w', encoding = 'utf-8') as f:
                f.write(current_decrypted)
            print(f"Сохранено в {filename}")
        else:
            # Обработка пар вида "к=о" или "к=о, щ=е"
            pairs = cmd.replace(' ', '').split(',')
            for pair in pairs:
                if '=' in pair and len(pair) == 3:
                    cipher_char, plain_char = pair[0], pair[2]
                    if cipher_char in current_mapping or plain_char in RUSSIAN_FREQ:
                        # Удаляем все отображения, которые ведут на ту же открытую букву (обратная замена)
                        to_remove = [k for k, v in current_mapping.items() if v == plain_char]
                        for k in to_remove:
                            del current_mapping[k]
                        current_mapping[cipher_char] = plain_char
                        print(f"Установлено: {cipher_char} -> {plain_char}")
                    else:
                        print(f"Ошибка: '{cipher_char}' не найдена в шифротексте или '{plain_char}' не русская буква")
                else:
                    print(f"Неверный формат: '{pair}'. Используйте 'а=б'")
        
        # Обновляем расшифровку
        current_decrypted = decrypt_with_mapping(ciphertext, current_mapping)
        print("\n" + "=" * 70)
        print("ОБНОВЛЁННЫЙ ТЕКСТ (фрагмент):")
        print("=" * 70)
        print(current_decrypted[:500] + "..." if len(current_decrypted) > 500 else current_decrypted)
        print("=" * 70)
    
    return current_mapping

def main():
    print("=== ЧАСТОТНЫЙ АНАЛИЗ ДЛЯ ВЗЛОМА ШИФРА ПРОСТОЙ ЗАМЕНЫ ===\n")
    
    # Загружаем шифротекст
    try:
        ciphertext = load_ciphertext()
    except FileNotFoundError:
        print("Файл 'ciphertext.txt' не найден.")
        print("Создайте его и поместите туда зашифрованный текст (как в примере лекции).")
        print("\nДля демонстрации использую встроенный короткий пример из вашего текста:")
        ciphertext = """яхшбюфылегчыгаяеюххубощмккгикфкнкяукььшбэяэщякэбгбябнкьфбнкьюбяэщукъяэивьгкифчркьщщоучачгкгмняяиючфчшбуииухгчшбуишуксщщоук агкгмжбюкфкшбгэхяхрюоубчщи мчс ьбщ мыффещмниракокмбгшбуинбьябэошбуиыьш u0щаиюфбвфщцфбьяышэышкмбгшэщмнбрьдщфыщъющэяфхрюиг"""
        print(f"\nИспользую текст длиной {len(ciphertext)} символов.")
    
    print(f"\nДлина текста: {len(ciphertext)} символов (включая пробелы и знаки).")
    
    # Частотный анализ
    freq_percent, freq_abs = get_freq_analysis(ciphertext)
    if not freq_percent:
        print("В тексте нет русских букв. Проверьте кодировку.")
        return
    
    print("\n=== ЧАСТОТЫ СИМВОЛОВ В ШИФРОТЕКСТЕ ===")
    sorted_freq = sorted(freq_percent.items(), key = lambda x: x[1], reverse = True)
    print("Буква (частота %):")
    for ch, percent in sorted_freq[:10]:
        print(f"  {ch}: {percent:.2f}% (абс: {freq_abs[ch]})")
    
    print("\n=== ЭТАЛОННЫЕ ЧАСТОТЫ РУССКОГО ЯЗЫКА (первые 10) ===")
    for ch in RUSSIAN_LETTERS_BY_FREQ[:10]:
        print(f"  {ch}: {RUSSIAN_FREQ[ch]:.2f}%")
    
    # Начальное предположение отображения
    initial_mapping = suggest_mapping(freq_percent)
    print("\n=== НАЧАЛЬНОЕ ПРЕДПОЛОЖЕНИЕ (самая частая -> самая частая) ===")
    for i, (cipher_char, plain_char) in enumerate(list(initial_mapping.items())[:10]):
        print(f"  {cipher_char} -> {plain_char}")
    
    # Интерактивное уточнение
    final_mapping = interactive_refine(initial_mapping, ciphertext, "")
    
    # Итоговая расшифровка
    final_decrypted = decrypt_with_mapping(ciphertext, final_mapping)
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ РАСШИФРОВКА:")
    print("=" * 70)
    print(final_decrypted)
    print("=" * 70)
    
    # Сохраняем результат
    with open("decrypted.txt", "w", encoding = "utf-8") as f:
        f.write(final_decrypted)
    print("\nРезультат сохранён в файл 'decrypted.txt'.")

if __name__ == "__main__":
    main()