# Расстояние единственности шифра с секретным ключом
import math
import random
from itertools import permutations
from collections import defaultdict

class CryptoSystem:
    """Криптосистема с шифром подстановки (без использования NumPy)"""
    
    def __init__(self, alphabet, source_probs = None, transition_matrix = None):
        """
        Инициализация криптосистемы
        
        Args:
            alphabet: список символов алфавита
            source_probs: вероятности символов (для источника без памяти)
            transition_matrix: матрица переходов (для марковского источника)
        """
        self.alphabet = alphabet
        self.r = len(alphabet)
        
        # Генерируем все возможные ключи (перестановки)
        self.keys = list(permutations(alphabet))
        self.num_keys = len(self.keys)
        self.key_entropy = math.log2(self.num_keys)
        
        # Параметры источника
        self.source_probs = source_probs
        self.transition_matrix = transition_matrix
        
        # Вычисляем энтропию источника
        if source_probs is not None:
            self.source_entropy = self._compute_entropy_discrete(source_probs)
        elif transition_matrix is not None:
            self.source_entropy = self._compute_markov_entropy()
        else:
            self.source_entropy = 0
        
        self.max_entropy = math.log2(self.r)
        self.redundancy = self.max_entropy - self.source_entropy if self.source_entropy > 0 else 0
        
    def _compute_entropy_discrete(self, probs):
        """Вычисление энтропии дискретного распределения"""
        entropy = 0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def _compute_markov_entropy(self):
        """Вычисление энтропии марковского источника (без NumPy)"""
        if self.transition_matrix is None:
            return 0
        
        # Находим стационарное распределение методом итераций
        P = self.transition_matrix
        n = len(P)
        
        # Начинаем с равномерного распределения
        stationary = [1.0 / n] * n
        
        # Итеративно находим стационарное распределение
        for _ in range(1000):
            new_stationary = [0] * n
            for i in range(n):
                for j in range(n):
                    new_stationary[j] += stationary[i] * P[i][j]
            
            # Проверяем сходимость
            diff = sum(abs(new_stationary[i] - stationary[i]) for i in range(n))
            stationary = new_stationary
            if diff < 1e-10:
                break
        
        # Вычисляем энтропию
        entropy = 0
        for i in range(n):
            for j in range(n):
                if P[i][j] > 0 and stationary[i] > 0:
                    entropy -= stationary[i] * P[i][j] * math.log2(P[i][j])
        
        return entropy
    
    def encrypt(self, message, key_index):
        """
        Шифрование сообщения
        
        Args:
            message: строка с открытым текстом
            key_index: индекс ключа (0..num_keys-1)
        
        Returns:
            зашифрованное сообщение
        """
        key = self.keys[key_index]
        mapping = {self.alphabet[i]: key[i] for i in range(self.r)}
        return ''.join(mapping.get(ch, ch) for ch in message)
    
    def decrypt(self, ciphertext, key_index):
        """Дешифрование сообщения"""
        key = self.keys[key_index]
        inverse_mapping = {key[i]: self.alphabet[i] for i in range(self.r)}
        return ''.join(inverse_mapping.get(ch, ch) for ch in ciphertext)
    
    def generate_message_without_memory(self, length):
        """Генерация сообщения от источника без памяти"""
        if self.source_probs is None:
            # Если вероятности не заданы, используем равномерное распределение
            return ''.join(random.choice(self.alphabet) for _ in range(length))
        
        # Генерируем с заданными вероятностями
        # Используем метод обратного преобразования
        result = []
        for _ in range(length):
            r = random.random()
            cum_prob = 0
            for i, prob in enumerate(self.source_probs):
                cum_prob += prob
                if r <= cum_prob:
                    result.append(self.alphabet[i])
                    break
        return ''.join(result)
    
    def generate_message_with_memory(self, length, start_char = None):
        """Генерация сообщения от марковского источника"""
        if self.transition_matrix is None:
            return self.generate_message_without_memory(length)
        
        if start_char is None:
            # Начинаем со случайного символа
            start_char = random.choice(self.alphabet)
        
        message = [start_char]
        current_idx = self.alphabet.index(start_char)
        
        for _ in range(length - 1):
            # Выбираем следующий символ согласно матрице переходов
            probs = self.transition_matrix[current_idx]
            
            # Метод обратного преобразования
            r = random.random()
            cum_prob = 0
            for i, prob in enumerate(probs):
                cum_prob += prob
                if r <= cum_prob:
                    message.append(self.alphabet[i])
                    current_idx = i
                    break
        
        return ''.join(message)
    
    def compute_posterior_probabilities(self, ciphertext, prior_probs = None):
        """
        Вычисление апостериорных вероятностей ключей по формуле Байеса
        
        Args:
            ciphertext: зашифрованное сообщение
            prior_probs: априорные вероятности ключей (по умолчанию равномерные)
        
        Returns:
            словарь {индекс_ключа: вероятность}
        """
        if prior_probs is None:
            prior_probs = [1.0 / self.num_keys] * self.num_keys
        
        # Вычисляем вероятности P(E|Ki)
        likelihoods = []
        for key_idx in range(self.num_keys):
            plaintext = self.decrypt(ciphertext, key_idx)
            
            if self.source_probs is not None:
                # Источник без памяти
                prob = 1.0
                for ch in plaintext:
                    idx = self.alphabet.index(ch)
                    prob *= self.source_probs[idx]
            elif self.transition_matrix is not None:
                # Марковский источник
                prob = 1.0
                # Находим стационарное распределение
                stationary = self._get_stationary_distribution()
                
                for i, ch in enumerate(plaintext):
                    idx = self.alphabet.index(ch)
                    if i == 0:
                        # Используем стационарное распределение
                        prob *= stationary[idx]
                    else:
                        prev_idx = self.alphabet.index(plaintext[i-1])
                        prob *= self.transition_matrix[prev_idx][idx]
            else:
                # Если нет информации об источнике, все сообщения равновероятны
                prob = 1.0 / (self.r ** len(ciphertext))
            
            likelihoods.append(prob)
        
        # Вычисляем нормировочную константу
        evidence = sum(prior_probs[i] * likelihoods[i] for i in range(self.num_keys))
        
        # Защита от деления на ноль
        if evidence == 0:
            # Если все вероятности равны нулю, возвращаем равномерное распределение
            return {i: 1.0 / self.num_keys for i in range(self.num_keys)}
        
        # Вычисляем апостериорные вероятности
        posterior = {}
        for i in range(self.num_keys):
            posterior[i] = (prior_probs[i] * likelihoods[i]) / evidence
        
        return posterior
    
    def _get_stationary_distribution(self):
        """Получение стационарного распределения марковской цепи"""
        if self.transition_matrix is None:
            return [1.0 / self.r] * self.r
        
        n = len(self.transition_matrix)
        stationary = [1.0 / n] * n
        
        # Итеративный метод
        for _ in range(1000):
            new_stationary = [0] * n
            for i in range(n):
                for j in range(n):
                    new_stationary[j] += stationary[i] * self.transition_matrix[i][j]
            
            diff = sum(abs(new_stationary[i] - stationary[i]) for i in range(n))
            stationary = new_stationary
            if diff < 1e-10:
                break
        
        return stationary
    
    def compute_uniqueness_distance(self):
        """Вычисление расстояния единственности по Шеннону"""
        if self.redundancy == 0:
            return float('inf')
        return self.key_entropy / self.redundancy
    
    def analyze_key_recovery(self, ciphertext, threshold = 0.9):
        """
        Анализ восстановления ключа
        
        Args:
            ciphertext: зашифрованное сообщение
            threshold: порог вероятности для определения ключа
        
        Returns:
            dict с результатами анализа
        """
        posterior = self.compute_posterior_probabilities(ciphertext)
        max_prob = max(posterior.values())
        most_likely_key = max(posterior, key = posterior.get)
        
        return {
            'posterior_probabilities': posterior,
            'most_likely_key': most_likely_key,
            'max_probability': max_prob,
            'is_key_determined': max_prob >= threshold,
            'key_entropy': self.key_entropy,
            'source_entropy': self.source_entropy,
            'redundancy': self.redundancy,
            'uniqueness_distance': self.compute_uniqueness_distance()
        }


def run_example_7_3():
    """Пример 7.3 из текста: источник без памяти"""
    print("=" * 60)
    print("ПРИМЕР 7.3: Источник без памяти")
    print("=" * 60)
    
    alphabet = ['a', 'b', 'c']
    probs = [0.8, 0.15, 0.05]
    
    # Создаем криптосистему
    crypto = CryptoSystem(alphabet, source_probs = probs)
    
    print(f"\nАлфавит: {alphabet}")
    print(f"Вероятности: {dict(zip(alphabet, probs))}")
    print(f"Энтропия источника: {crypto.source_entropy:.3f} бит")
    print(f"Избыточность: {crypto.redundancy:.3f} бит")
    print(f"Энтропия ключа: {crypto.key_entropy:.3f} бит")
    print(f"Расстояние единственности: {crypto.compute_uniqueness_distance():.2f} символов")
    
    # Перехваченное сообщение
    ciphertext = "cccbc"
    print(f"\nПерехваченное сообщение: '{ciphertext}'")
    
    # Вычисляем апостериорные вероятности
    print("\nВычисление апостериорных вероятностей ключей...")
    posterior = crypto.compute_posterior_probabilities(ciphertext)
    
    print("\nРезультаты:")
    for key_idx, prob in sorted(posterior.items(), key = lambda x: x[1], reverse = True):
        key = crypto.keys[key_idx]
        plaintext = crypto.decrypt(ciphertext, key_idx)
        print(f"  K{key_idx + 1} {key}: {prob:.6f} -> '{plaintext}'")
    
    # Анализ
    analysis = crypto.analyze_key_recovery(ciphertext, threshold = 0.7)
    print(f"\nНаиболее вероятный ключ: K{analysis['most_likely_key'] + 1}")
    print(f"Вероятность правильного ключа: {analysis['max_probability']:.3f}")
    print(f"Ключ определен: {analysis['is_key_determined']}")
    
    return crypto


def run_example_7_5():
    """Пример 7.5 из текста: марковский источник"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 7.5: Марковский источник (источник с памятью)")
    print("=" * 60)
    
    alphabet = ['a', 'b', 'c']
    
    # Матрица переходов из примера
    # Строки: текущий символ, столбцы: следующий символ
    transition_matrix = [
        [0.0, 0.9, 0.1],   # a -> a:0, b:0.9, c:0.1
        [0.0, 0.1, 0.9],   # b -> a:0, b:0.1, c:0.9
        [0.4, 0.3, 0.3]    # c -> a:0.4, b:0.3, c:0.3
    ]
    
    # Создаем криптосистему с марковским источником
    crypto = CryptoSystem(alphabet, transition_matrix = transition_matrix)
    
    print(f"\nАлфавит: {alphabet}")
    print("Матрица переходов:")
    print("     a    b    c")
    for i, row in enumerate(transition_matrix):
        print(f"{alphabet[i]}  {row[0]:.1f}  {row[1]:.1f}  {row[2]:.1f}")
    
    print(f"\nЭнтропия источника: {crypto.source_entropy:.3f} бит")
    print(f"Избыточность: {crypto.redundancy:.3f} бит")
    print(f"Энтропия ключа: {crypto.key_entropy:.3f} бит")
    print(f"Расстояние единственности: {crypto.compute_uniqueness_distance():.2f} символов")
    
    # Перехваченное сообщение
    ciphertext = "bbacbac"
    print(f"\nПерехваченное сообщение: '{ciphertext}'")
    
    # Вычисляем апостериорные вероятности
    print("\nВычисление апостериорных вероятностей ключей...")
    posterior = crypto.compute_posterior_probabilities(ciphertext)
    
    print("\nРезультаты:")
    for key_idx, prob in sorted(posterior.items(), key = lambda x: x[1], reverse = True):
        key = crypto.keys[key_idx]
        plaintext = crypto.decrypt(ciphertext, key_idx)
        if prob > 0.001:
            print(f"  K{key_idx + 1} {key}: {prob:.6f} -> '{plaintext}'")
        else:
            print(f"  K{key_idx + 1} {key}: {prob:.6f}")
    
    # Анализ
    analysis = crypto.analyze_key_recovery(ciphertext, threshold = 0.7)
    print(f"\nНаиболее вероятный ключ: K{analysis['most_likely_key'] + 1}")
    print(f"Вероятность правильного ключа: {analysis['max_probability']:.3f}")
    print(f"Ключ определен: {analysis['is_key_determined']}")
    
    return crypto


def analyze_entropy_and_redundancy():
    """Анализ влияния длины сообщения на неопределенность"""
    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВИСИМОСТИ ОТ ДЛИНЫ СООБЩЕНИЯ")
    print("=" * 60)
    
    alphabet = ['a', 'b', 'c']
    probs = [0.8, 0.15, 0.05]
    crypto = CryptoSystem(alphabet, source_probs = probs)
    
    print("\nДля каждого ключа генерируем сообщение и шифруем его")
    print("Затем пытаемся восстановить ключ по шифротексту\n")
    
    lengths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    results = []
    
    for length in lengths:
        # Генерируем случайное сообщение
        message = crypto.generate_message_without_memory(length)
        
        # Выбираем случайный ключ
        true_key = random.randint(0, crypto.num_keys - 1)
        ciphertext = crypto.encrypt(message, true_key)
        
        # Вычисляем апостериорные вероятности
        posterior = crypto.compute_posterior_probabilities(ciphertext)
        
        # Проверяем, определен ли ключ
        max_prob = max(posterior.values())
        key_determined = max_prob >= 0.9
        correct_key_prob = posterior[true_key]
        
        results.append({
            'length': length,
            'message': message,
            'true_key': true_key,
            'max_prob': max_prob,
            'correct_key_prob': correct_key_prob,
            'key_determined': key_determined
        })
        
        status = "✓" if key_determined else "✗"
        print(f"Длина {length:2d}: сообщение='{message}', "
              f"ключ K{true_key + 1}, "
              f"P(правильный) = {correct_key_prob:.3f}, "
              f"определен? {status}")
    
    # Находим минимальную длину для определения ключа
    determined_at = next((r['length'] for r in results if r['key_determined']), None)
    if determined_at:
        print(f"\nМинимальная длина для определения ключа: {determined_at} символов")
    print(f"Теоретическое расстояние единственности: {crypto.compute_uniqueness_distance():.2f} символов")
    
    return results


def simulate_markov_generation():
    """Демонстрация генерации сообщений от марковского источника"""
    print("\n" + "=" * 60)
    print("ГЕНЕРАЦИЯ СООБЩЕНИЙ ОТ МАРКОВСКОГО ИСТОЧНИКА")
    print("=" * 60)
    
    alphabet = ['a', 'b', 'c']
    transition_matrix = [
        [0.0, 0.9, 0.1],
        [0.0, 0.1, 0.9],
        [0.4, 0.3, 0.3]
    ]
    
    crypto = CryptoSystem(alphabet, transition_matrix = transition_matrix)
    
    print("\nМатрица переходов:")
    print("     a    b    c")
    for i, row in enumerate(transition_matrix):
        print(f"{alphabet[i]}  {row[0]:.1f}  {row[1]:.1f}  {row[2]:.1f}")
    
    print(f"\nЭнтропия источника: {crypto.source_entropy:.3f} бит")
    print(f"Максимальная энтропия: {crypto.max_entropy:.3f} бит")
    print(f"Избыточность: {crypto.redundancy:.3f} бит")
    print(f"Расстояние единственности: {crypto.compute_uniqueness_distance():.2f} символов")
    
    print("\nГенерация 10 сообщений от марковского источника (длина 20):")
    for i in range(10):
        message = crypto.generate_message_with_memory(20)
        print(f"{i + 1:2d}. {message}")
    
    # Проверяем, что сочетание 'aa' действительно невозможно
    print("\nПроверка: в сгенерированных сообщениях не должно быть 'aa'")
    for i in range(5):
        message = crypto.generate_message_with_memory(20)
        has_aa = 'aa' in message
        print(f"Сообщение: {message} -> {'aa' in message}")


def demonstrate_bayesian_update():
    """Демонстрация обновления вероятностей по Байесу с ростом длины"""
    print("\n" + "=" * 60)
    print("БАЙЕСОВСКОЕ ОБНОВЛЕНИЕ ВЕРОЯТНОСТЕЙ КЛЮЧЕЙ")
    print("=" * 60)
    
    alphabet = ['a', 'b', 'c']
    probs = [0.8, 0.15, 0.05]
    crypto = CryptoSystem(alphabet, source_probs = probs)
    
    # Генерируем длинное сообщение
    true_key = 5  # K6 (индекс 5)
    message = crypto.generate_message_without_memory(20)
    ciphertext = crypto.encrypt(message, true_key)
    
    print(f"\nИстинный ключ: K{true_key + 1}")
    print(f"Сообщение: {message}")
    print(f"Шифротекст: {ciphertext}")
    
    print("\nЭволюция апостериорных вероятностей с ростом длины:")
    print("-" * 70)
    print(f"{'Длина':>6} ", end = "")
    for i in range(6):
        print(f"  K{i + 1}    ", end = "")
    print()
    print("-" * 70)
    
    for length in [1, 2, 3, 4, 5, 6, 8, 10, 12, 15]:
        prefix = ciphertext[:length]
        posterior = crypto.compute_posterior_probabilities(prefix)
        
        print(f"{length:6d} ", end = "")
        for i in range(6):
            prob = posterior.get(i, 0)
            print(f"{prob:8.3f} ", end = "")
        print()


def main():
    """Основная функция, запускающая все примеры"""
    print("\n" + "=" * 60)
    print("МОДЕЛИРОВАНИЕ КРИПТОАНАЛИЗА ШИФРА ПОДСТАНОВКИ")
    print("=" * 60)
    
    # Для воспроизводимости результатов
    random.seed(42)
    
    # Запускаем все примеры
    crypto_example3 = run_example_7_3()
    crypto_example5 = run_example_7_5()
    
    # Дополнительные анализы
    analyze_entropy_and_redundancy()
    simulate_markov_generation()
    demonstrate_bayesian_update()
    
    print("\n" + "=" * 60)
    print("ВЫВОДЫ")
    print("=" * 60)
    print("""
    1. Расстояние единственности определяет минимальную длину 
       шифротекста для однозначного восстановления ключа.
    
    2. Избыточность языка (зависимость между символами) уменьшает
       расстояние единственности, облегчая криптоанализ.
    
    3. Сжатие данных перед шифрованием увеличивает расстояние
       единственности, повышая стойкость шифра.
    
    4. Байесовский подход позволяет количественно оценить 
       вероятность каждого ключа при данном шифротексте.
    """)
    
    return crypto_example3, crypto_example5


if __name__ == "__main__":
    main()