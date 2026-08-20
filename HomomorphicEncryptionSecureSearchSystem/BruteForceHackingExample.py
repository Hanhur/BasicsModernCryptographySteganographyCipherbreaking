# Пример взлома методом грубой силы 
"""
Программа для расчета стойкости AES-256 к атаке перебором (brute force)
на основе производительности компьютера MacBook Pro 2015 (i7)
"""

import math
import time

def format_large_number(num, decimals = 2):
    """Форматирует огромные числа в читаемый вид с суффиксами"""
    if num == 0:
        return "0"
    
    # Суффиксы для тысяч, миллионов, миллиардов и т.д.
    suffixes = ['', 'тысяч', 'миллионов', 'миллиардов', 'триллионов', 
                'квадриллионов', 'квинтиллионов', 'секстиллионов', 
                'септиллионов', 'октиллионов', 'нониллионов', 'дециллионов']
    
    # Определяем порядок числа
    magnitude = int(math.floor(math.log10(abs(num)) / 3))
    
    if magnitude >= len(suffixes):
        # Если число слишком большое для суффиксов, возвращаем в экспоненциальной форме
        return f"{num:.2e}"
    
    # Округляем до 2 знаков после запятой
    scaled = num / (10 ** (magnitude * 3))
    return f"{scaled:.{decimals}f} {suffixes[magnitude]}"

def print_separator(char = '=', length = 80):
    """Печатает разделительную линию"""
    print(char * length)

def calculate_aes_bruteforce():
    """Основная функция расчета"""
    
    print_separator('=')
    print("🖥️  АНАЛИЗ СТОЙКОСТИ AES-256 К АТАКЕ ПЕРЕБОРОМ")
    print_separator('=')
    print()
    
    # ===== 1. ИСХОДНЫЕ ДАННЫЕ =====
    print("📊 ИСХОДНЫЕ ДАННЫЕ:")
    print_separator('-')
    
    # Производительность MacBook Pro 2015 (i7 4-core)
    performance_mb_per_sec = 1024  # Мбайт/с
    performance_bytes_per_sec = performance_mb_per_sec * 1024 * 1024  # байт/с
    performance_bytes_per_sec_exact = 2 ** 30  # 1 073 741 824 байт/с
    
    # Размер блока AES
    aes_block_size = 16  # байт (2^4)
    
    # Количество блоков в секунду
    blocks_per_second = performance_bytes_per_sec // aes_block_size
    blocks_per_second_exact = 2 ** 26  # 67 108 864 блоков/с
    
    # Количество секунд в году
    seconds_in_year = 60 * 60 * 24 * 365.25  # ≈ 31 557 600 секунд
    
    # Количество ключей для перебора (AES-256)
    total_keys = 2 ** 256
    average_keys_to_try = 2 ** 255  # В среднем нужно перебрать половину
    
    print(f"  💻 Процессор:          MacBook Pro 2015 (i7, 4 ядра)")
    print(f"  📀 Производительность: {performance_mb_per_sec:,} Мбайт/с")
    print(f"  📀 Производительность: {performance_bytes_per_sec:,} байт/с = 2 ^ 30 байт/с")
    print(f"  📦 Блок AES:           {aes_block_size} байт = 2 ^ 4 байт")
    print(f"  ⚡ Блоков в секунду:   {blocks_per_second:,} = 2 ^ 26 блоков/с")
    print(f"  ⏱️  Секунд в году:      {seconds_in_year:,.0f}")
    print(f"  🔑 Всего ключей:       2 ^ 256 = {total_keys:.2e}")
    print(f"  🎯 Среднее кол-во:     2 ^ 255 ключей")
    print()
    
    # ===== 2. РАСЧЕТ ДЛЯ ОДНОГО КОМПЬЮТЕРА =====
    print("🖥️  РАСЧЕТ ДЛЯ ОДНОГО КОМПЬЮТЕРА:")
    print_separator('-')
    
    # Ключей в год
    keys_per_year = blocks_per_second * seconds_in_year
    keys_per_year_exact = 2 ** 26 * seconds_in_year
    
    print(f"  📈 Ключей в год:       {format_large_number(keys_per_year)}")
    print(f"  📈 Точное значение:    {keys_per_year:,.0f}")
    print(f"  📈 Степень:            2 ^ 26 * {seconds_in_year:,.0f} ≈ 2 ^ 26 * 2 ^ 25 = 2 ^ 51")
    
    # Время перебора в годах
    years_for_bruteforce = average_keys_to_try / keys_per_year
    
    print(f"\n  ⏳ Время перебора (среднее):")
    print(f"     {format_large_number(years_for_bruteforce)} лет")
    print(f"     {years_for_bruteforce:.2e} лет (экспоненциальная форма)")
    
    # Разбиваем на группы (трлн трлн...)
    print(f"\n  📝 В альтернативном представлении:")
    # Переводим в триллионы (10^12)
    trillions = years_for_bruteforce / 10 ** 12
    if trillions > 10 ** 12:
        # Если число больше триллиона триллионов
        trillions_of_trillions = years_for_bruteforce / 10 ** 24
        print(f"     ~ {trillions_of_trillions:.2f} × 10 ^ 24 лет")
        print(f"     ~ {trillions_of_trillions:.2f} трлн трлн лет")
    
    print(f"\n  🌌 Сравнение:")
    universe_age = 15_000_000_000  # 15 млрд лет
    ratio = years_for_bruteforce / universe_age
    print(f"     Возраст Вселенной:  {universe_age:,} лет")
    print(f"     Время перебора:     в {ratio:.2e} раз больше возраста Вселенной")
    print()
    
    # ===== 3. РАСЧЕТ ДЛЯ ВСЕХ КОМПЬЮТЕРОВ ЗЕМЛИ =====
    print("🌍 РАСЧЕТ ДЛЯ ВСЕХ КОМПЬЮТЕРОВ ЗЕМЛИ:")
    print_separator('-')
    
    # Количество компьютеров на Земле (данные Wolfram Alpha)
    computers_on_earth = 2_000_000_000  # 2 млрд
    
    print(f"  💻 Компьютеров на Земле: {computers_on_earth:,} (2 млрд)")
    print(f"  🚀 Предположение:        Все компьютеры имеют мощность MacBook Pro i7")
    
    # Время для всех компьютеров
    years_all_computers = years_for_bruteforce / computers_on_earth
    
    print(f"\n  ⏳ Время перебора (все компьютеры):")
    print(f"     {format_large_number(years_all_computers)} лет")
    print(f"     {years_all_computers:.3e} лет (экспоненциальная форма)")
    
    # Полное число (в целочисленном виде, насколько это возможно)
    # Преобразуем в строку для красивого вывода
    if years_all_computers < 1e308:  # Проверяем, не выходит ли за пределы double
        full_number_str = f"{years_all_computers:.0f}"
        if len(full_number_str) <= 60:  # Показываем только если строка не слишком длинная
            print(f"\n  📝 Полное число:")
            # Разбиваем на группы по 3 цифры
            formatted = ''
            for i, digit in enumerate(reversed(full_number_str)):
                if i > 0 and i % 3 == 0:
                    formatted = ' ' + formatted
                formatted = digit + formatted
            print(f"     {formatted} лет")
    
    # ===== 4. ВЛИЯНИЕ КВАНТОВЫХ КОМПЬЮТЕРОВ =====
    print()
    print_separator('=')
    print("⚛️  КВАНТОВОЕ УСКОРЕНИЕ (АЛГОРИТМ ГРОВЕРА)")
    print_separator('=')
    print()
    
    print("  📐 Алгоритм Гровера дает квадратичное ускорение:")
    print(f"     √(2 ^ 256) = 2 ^ 128 операций (вместо 2 ^ 255)")
    print()
    
    # Квантовое время
    quantum_operations = 2 ** 128
    quantum_years = quantum_operations / keys_per_year
    
    print(f"  ⏳ Время на квантовом компьютере:")
    print(f"     {format_large_number(quantum_years)} лет")
    print(f"     {quantum_years:.2e} лет")
    
    ratio_quantum = quantum_years / universe_age
    print(f"     Это в {ratio_quantum:.2e} раз больше возраста Вселенной")
    print()
    
    print("  💡 Вывод: даже с алгоритмом Гровера AES-256 остается")
    print("     криптостойким (эффективная стойкость ~128 бит)")
    print()
    
    # ===== 5. ОЦЕНКА CSE =====
    print_separator('=')
    print("🔐 СИСТЕМА CSE (ГОМОМОРФНОЕ ШИФРОВАНИЕ)")
    print_separator('=')
    print()
    
    query_time = 0.35  # секунд
    queries_per_second = 1 / query_time
    
    print(f"  ⚡ Среднее время запроса: {query_time} секунд")
    print(f"  📊 Запросов в секунду:   {queries_per_second:.2f}")
    print(f"  📊 Запросов в год:       {queries_per_second * seconds_in_year:,.0f}")
    print()
    
    print("  ✅ Крипто-агильность (crypto-agility):")
    print("     - Ядро системы может быть заменено")
    print("     - Возможна замена на квантовый гомоморфный поиск")
    print("     - Независимость от используемых алгоритмов")
    print()
    
    # ===== 6. ИТОГОВОЕ РЕЗЮМЕ =====
    print_separator('=')
    print("📋 ИТОГОВОЕ РЕЗЮМЕ")
    print_separator('=')
    print()
    
    print("  🔑 AES-256:")
    print(f"     • Ключей:          2 ^ 256")
    print(f"     • Средний перебор: 2 ^ 255")
    print(f"     • 1 ПК:            {format_large_number(years_for_bruteforce)} лет")
    print(f"     • Все ПК Земли:    {format_large_number(years_all_computers)} лет")
    print(f"     • Квантовый ПК:    {format_large_number(quantum_years)} лет (Гровер)")
    print()
    
    print("  🛡️  CSE:")
    print(f"     • Время ответа:    {query_time} сек")
    print(f"     • Безопасность:    Гомоморфное шифрование + смена ядра")
    print(f"     • Гибкость:        Замена алгоритмов без изменения архитектуры")
    print()
    
    print_separator('=')
    print("✅ Расчет завершен!")
    print_separator('=')

def main():
    """Точка входа в программу"""
    try:
        calculate_aes_bruteforce()
    except OverflowError:
        print("⚠️  Число слишком велико для вычислений в стандартном Python")
        print("   Используйте экспоненциальную форму для больших чисел")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()