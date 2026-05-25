# 4. Тест Казисского и определение с его помощью длины ключа в шифре Виженера
"""
Тест Казиского для определения длины ключа в шифре Виженера
Реализация на основе индекса совпадений (Index of Coincidence)
"""

from collections import Counter
import math


class VigenereKeyLengthFinder:
    def __init__(self, alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """
        Инициализация анализатора
        
        Args:
            alphabet: строка с алфавитом (по умолчанию английский A-Z)
        """
        self.alphabet = alphabet.upper()
        self.n = len(alphabet)  # размер алфавита
        
        # Эталонные значения индекса совпадения
        self.IC_RANDOM = 1.0 / self.n  # ~0.038 для 26 букв
        self.IC_ENGLISH = 0.065  # для осмысленного английского текста
        
    def index_of_coincidence(self, text):
        """
        Вычисляет индекс совпадения для заданного текста
        
        Formula: IC = sum(f_i * (f_i - 1)) / (L * (L - 1))
        где f_i - частота i-й буквы, L - длина текста
        
        Args:
            text: строка с текстом (должна содержать только буквы алфавита)
            
        Returns:
            float: индекс совпадения
        """
        # Приводим к верхнему регистру и фильтруем только буквы алфавита
        filtered = [ch for ch in text.upper() if ch in self.alphabet]
        L = len(filtered)
        
        if L < 2:
            return 0.0
        
        # Подсчёт частот
        freq = Counter(filtered)
        
        # Вычисление суммы f_i * (f_i - 1)
        sum_fi_fi_minus_1 = sum(count * (count - 1) for count in freq.values())
        
        # Индекс совпадения
        ic = sum_fi_fi_minus_1 / (L * (L - 1))
        
        return ic
    
    def get_sequences_for_key_length(self, ciphertext, key_length):
        """
        Разбивает шифротекст на последовательности для предполагаемой длины ключа
        
        Например, при key_length=3:
        seq0: позиции 0, 3, 6, 9, ...
        seq1: позиции 1, 4, 7, 10, ...
        seq2: позиции 2, 5, 8, 11, ...
        
        Args:
            ciphertext: шифротекст
            key_length: предполагаемая длина ключа
            
        Returns:
            list: список строк-последовательностей
        """
        # Фильтруем только буквы алфавита
        filtered = [ch for ch in ciphertext.upper() if ch in self.alphabet]
        
        sequences = []
        for i in range(key_length):
            seq = ''.join(filtered[i::key_length])
            sequences.append(seq)
        
        return sequences
    
    def average_ic_for_key_length(self, ciphertext, key_length):
        """
        Вычисляет средний индекс совпадения для всех последовательностей
        при заданной предполагаемой длине ключа
        
        Args:
            ciphertext: шифротекст
            key_length: предполагаемая длина ключа
            
        Returns:
            float: средний IC
        """
        sequences = self.get_sequences_for_key_length(ciphertext, key_length)
        
        if not sequences:
            return 0.0
        
        ics = [self.index_of_coincidence(seq) for seq in sequences]
        avg_ic = sum(ics) / len(ics)
        
        return avg_ic
    
    def find_key_length(self, ciphertext, max_key_length = 20, threshold = None, verbose = True):
        """
        Определяет вероятную длину ключа методом Казиского
        
        Алгоритм:
        1. Для каждой предполагаемой длины ключа t от 1 до max_key_length
        2. Разбиваем шифротекст на t последовательностей
        3. Вычисляем средний IC для этих последовательностей
        4. Если средний IC близок к эталонному значению для языка (0.065),
           то t - вероятная длина ключа
        
        Args:
            ciphertext: шифротекст
            max_key_length: максимальная проверяемая длина ключа
            threshold: пороговое значение IC (если None, используется IC_ENGLISH)
            verbose: выводить ли подробности
            
        Returns:
            tuple: (найденная_длина_ключа, список_значений_IC_по_длинам)
        """
        if threshold is None:
            threshold = self.IC_ENGLISH
        
        results = []
        
        print("\n" + "=" * 60)
        print("ТЕСТ КАЗИСКОГО - Определение длины ключа")
        print("=" * 60)
        print(f"{'Длина ключа (t)':<15} {'Средний IC':<12} {'Оценка'}")
        print("-" * 60)
        
        for t in range(1, max_key_length + 1):
            avg_ic = self.average_ic_for_key_length(ciphertext, t)
            results.append((t, avg_ic))
            
            # Оценка
            if avg_ic > self.IC_RANDOM * 1.2:  # заметно выше случайного
                diff = abs(avg_ic - threshold)
                if diff < 0.01:
                    assessment = "✓ ОЧЕНЬ БЛИЗКО к эталону"
                elif avg_ic > threshold:
                    assessment = "↑ Выше эталона (возможно, длина ключа)"
                else:
                    assessment = "? Ниже эталона, но выше случайного"
            else:
                assessment = "✗ Близко к случайному"
            
            if verbose:
                print(f"{t:<15} {avg_ic:<12.4f} {assessment}")
        
        # Поиск кандидатов: где IC близок к эталону
        candidates = []
        for t, ic_val in results:
            # Критерий: IC находится в интервале [0.05, 0.08] для английского
            # или резко возрастает относительно предыдущих значений
            if ic_val > 0.05 and ic_val < 0.08:
                candidates.append((t, ic_val))
        
        # Также учитываем резкие скачки
        for i in range(1, len(results)):
            t_prev, ic_prev = results[i-1]
            t_curr, ic_curr = results[i]
            if ic_curr - ic_prev > 0.01 and ic_curr > 0.055:
                if (t_curr, ic_curr) not in candidates:
                    candidates.append((t_curr, ic_curr))
        
        # Сортируем кандидатов по близости к эталону
        candidates.sort(key = lambda x: abs(x[1] - self.IC_ENGLISH))
        
        print("-" * 60)
        print("\nВероятные длины ключа (от наиболее вероятной):")
        for i, (t, ic_val) in enumerate(candidates[:5]):
            print(f"  {i + 1}. t = {t:2d} (IC = {ic_val:.4f})")
        
        best_t = candidates[0][0] if candidates else 1
        
        return best_t, results
    
    def validate_with_known_text(self, plaintext, key):
        """
        Проверка метода на известном открытом тексте и ключе
        
        Args:
            plaintext: открытый текст
            key: ключ шифрования
            
        Returns:
            dict: результаты проверки
        """
        # Простое шифрование Виженера (для проверки)
        def vigenere_encrypt(text, key):
            text = text.upper()
            key = key.upper()
            result = []
            key_len = len(key)
            
            for i, ch in enumerate(text):
                if ch in self.alphabet:
                    p = self.alphabet.index(ch)
                    k = self.alphabet.index(key[i % key_len])
                    c = (p + k) % self.n
                    result.append(self.alphabet[c])
                else:
                    result.append(ch)
            return ''.join(result)
        
        ciphertext = vigenere_encrypt(plaintext, key)
        
        print(f"\n{'=' * 60}")
        print("ПРОВЕРКА НА ТЕСТОВОМ ПРИМЕРЕ")
        print(f"{'=' * 60}")
        print(f"Открытый текст (первые 100 символов): {plaintext[:100]}...")
        print(f"Длина открытого текста: {len(plaintext)}")
        print(f"Истинная длина ключа: {len(key)}")
        print(f"Ключ: {key}")
        print(f"\nIC открытого текста: {self.index_of_coincidence(plaintext):.4f}")
        print(f"IC шифротекста: {self.index_of_coincidence(ciphertext):.4f}")
        
        # Находим длину ключа
        found_length, _ = self.find_key_length(ciphertext, max_key_length = 30, verbose = False)
        
        print(f"\nРЕЗУЛЬТАТ: Найденная длина ключа = {found_length}")
        print(f"Истинная длина ключа = {len(key)}")
        
        if found_length == len(key):
            print("✓ УСПЕХ! Длина ключа определена верно.")
        elif found_length % len(key) == 0 and found_length > len(key):
            print(f"⚠ Найдена длина {found_length} (кратна истинной: {found_length} / {len(key)} = {found_length / len(key)})")
        else:
            print("✗ Не совпадает. Возможно, текст слишком короткий или неосмысленный.")
        
        return {
            'plaintext': plaintext[:100],
            'key': key,
            'true_key_length': len(key),
            'found_key_length': found_length,
            'ciphertext_ic': self.index_of_coincidence(ciphertext),
            'plaintext_ic': self.index_of_coincidence(plaintext)
        }


def demo_with_sample_text():
    """
    Демонстрация работы программы на примере
    """
    # Пример осмысленного текста на английском
    sample_text = """
        This is a sample English text that is supposed to be meaningful and long enough 
        to demonstrate the Kasiski test for Vigenere cipher key length determination. 
        The index of coincidence for meaningful English text is approximately 0.065, 
        while for random text it is about 0.038. When we encrypt this text with a 
        Vigenere cipher using a key of a certain length, we can then apply the Kasiski 
        test to recover the key length by looking at the average index of coincidence 
        for different assumed key lengths. When the assumed key length matches the 
        actual key length, the average index of coincidence should be close to 0.065.
    """
    
    # Удаляем лишние пробелы и знаки, оставляем только буквы
    import re
    clean_text = re.sub(r'[^A-Za-z]', '', sample_text).upper()
    
    # Ключ для шифрования
    key = "SECRET"
    
    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ТЕСТА КАЗИСКОГО ДЛЯ ОПРЕДЕЛЕНИЯ ДЛИНЫ КЛЮЧА")
    print("=" * 70)
    
    # Создаём анализатор
    analyzer = VigenereKeyLengthFinder()
    
    # Шифруем
    def simple_vigenere_encrypt(text, key, alphabet):
        n = len(alphabet)
        result = []
        key = key.upper()
        text_upper = text.upper()
        
        for i, ch in enumerate(text_upper):
            if ch in alphabet:
                p = alphabet.index(ch)
                k = alphabet.index(key[i % len(key)])
                c = (p + k) % n
                result.append(alphabet[c])
            else:
                result.append(ch)
        return ''.join(result)
    
    ciphertext = simple_vigenere_encrypt(clean_text, key, analyzer.alphabet)
    
    print(f"Длина открытого текста (только буквы): {len(clean_text)}")
    print(f"Используемый ключ: {key} (длина = {len(key)})")
    print(f"IC открытого текста: {analyzer.index_of_coincidence(clean_text):.4f}")
    print(f"IC шифротекста: {analyzer.index_of_coincidence(ciphertext):.4f}")
    
    # Находим длину ключа
    best_length, results = analyzer.find_key_length(ciphertext, max_key_length = 20)
    
    print("\n" + "=" * 70)
    print(f"ИТОГ: Наиболее вероятная длина ключа = {best_length}")
    print("=" * 70)
    
    # Анализ кратных длин
    print("\nПримечание: Часто тест находит длину, кратную истинной,")
    print("особенно если текст короткий. Рекомендуется проверять")
    print("делители найденной длины как возможные истинные ключи.")


def analyze_custom_ciphertext():
    """
    Анализ произвольного шифротекста, введённого пользователем
    """
    print("\n" + "=" * 60)
    print("АНАЛИЗ ШИФРОТЕКСТА ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    ciphertext = input("\nВведите шифротекст (только буквы A - Z): ").strip()
    
    if not ciphertext:
        print("Ошибка: пустой ввод!")
        return
    
    # Очищаем от небуквенных символов
    import re
    clean_cipher = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    
    if len(clean_cipher) < 50:
        print(f"\nПредупреждение: текст короткий ({len(clean_cipher)} символов).")
        print("Результаты могут быть неточными. Рекомендуется текст длиной > 100 символов.")
    
    max_len = min(len(clean_cipher) // 5, 30)  # не более 1/5 длины текста
    if max_len < 2:
        max_len = 5
    
    print(f"\nАнализ для длин ключа от 1 до {max_len}...")
    
    analyzer = VigenereKeyLengthFinder()
    best_length, _ = analyzer.find_key_length(clean_cipher, max_key_length = max_len)
    
    print("\n" + "=" * 60)
    print(f"РЕКОМЕНДАЦИЯ: Попробуйте длину ключа = {best_length}")
    print("Если это не сработает, проверьте также делители этого числа.")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    print(r"""
    ╔══════════════════════════════════════════════════════════════╗
    ║     ТЕСТ КАЗИСКОГО - Определение длины ключа Виженера        ║
    ║                   Index of Coincidence Method                ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Выберите режим работы:")
    print("  1 - Демонстрация на примере")
    print("  2 - Анализ собственного шифротекста")
    print("  3 - Проверка на случайном тексте (контрольный пример)")
    
    choice = input("\nВаш выбор (1/2/3): ").strip()
    
    if choice == '1':
        demo_with_sample_text()
    elif choice == '2':
        analyze_custom_ciphertext()
    elif choice == '3':
        # Контрольный пример со случайным текстом
        analyzer = VigenereKeyLengthFinder()
        random_text = "X" * 500  # "бессмысленный" текст из одной буквы
        print(f"\nIC для текста из повторяющейся буквы: {analyzer.index_of_coincidence(random_text):.4f}")
        print("(Должно быть близко к 1.0, так как все буквы одинаковы)")
    else:
        print("Неверный выбор. Запускаем демонстрацию по умолчанию.")
        demo_with_sample_text()