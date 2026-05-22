# Задачи и упражнения
# Задача1. Пусть алфавит состоит из 26 букв английского
# языка. Шифрование осуществляется при помощи подстановки
# s= (р, h, u,q, l, J, е, r, т, g, у, х, v, s, n, i, Ь, o,j, с, w, t)(a, k, d}( z).
# Здесь подстановка определяется циклом, в котором буквы переходят в следующие по написанию, а последняя буква переходит в
# первую (цикл замыкается) . Буква z остается на месте.
# Пример: исходный текст - I ат fine = iaтfine (мы не учитываем пробелы и разницу между строчными и прописными буквами,
# а также знаки препинания) , шифрованный текст bkgebir.
# 1) Зашифровать текст:
# Sоте peo ple say а таn is таdе ottt of тud А poor тans таdе
# out of тusc le and Ыооd Muscle and Ьlood and skin and bone А тind
# thats weak and the back thats strong Sixteen tons.
# 2) Расшифровать текст:
# btkiarmpuтjqyurkwuwukтprmranpтrrpirdтtttr
# тrpurwukтprmrapukgrnajrnefjtk.qkтdbirsrmxek
# wrbgrrpgkтdnjetrkdrimngkтdnjetjrofkdrfjiaji.
def create_cipher_mapping():
    """
    Создает словари для шифрования и дешифрования на основе циклов из условия.
    Циклы: (p, h, u, q, l, j, e, r, t, m, g, y, x, v, s, n, i, b, o, c, w, t? - исправляем)
    
    В условии опечатка, по логике и примеру "i am fine" -> "bkgebir" восстанавливаем правильные циклы.
    Пример показывает: i->b, a->k, m->g, f->e, n->i, e->r
    """
    
    # Первый большой цикл (22 буквы) - восстановлен по логике и примеру
    cycle1 = ['p', 'h', 'u', 'q', 'l', 'j', 'e', 'r', 't', 'm', 'g', 'y', 'x', 'v', 's', 'n', 'i', 'b', 'o', 'c', 'w']
    # Замыкание: последняя буква переходит в первую
    # w -> p
    
    # Второй цикл (3 буквы)
    cycle2 = ['a', 'k', 'd']
    # a -> k, k -> d, d -> a
    
    # Буква z остается на месте
    # z -> z
    
    # Создаем отображение для шифрования
    encrypt_map = {}
    
    # Обрабатываем первый цикл
    for i in range(len(cycle1)):
        current = cycle1[i]
        next_char = cycle1[(i + 1) % len(cycle1)]
        encrypt_map[current] = next_char
    
    # Обрабатываем второй цикл
    for i in range(len(cycle2)):
        current = cycle2[i]
        next_char = cycle2[(i + 1) % len(cycle2)]
        encrypt_map[current] = next_char
    
    # Буква z остается на месте
    encrypt_map['z'] = 'z'
    
    # Буквы, не вошедшие в циклы (если такие есть), остаются на месте
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    for letter in all_letters:
        if letter not in encrypt_map:
            encrypt_map[letter] = letter
    
    # Создаем отображение для дешифрования (обратное)
    decrypt_map = {v: k for k, v in encrypt_map.items()}
    
    return encrypt_map, decrypt_map


def encrypt(text, encrypt_map):
    """
    Шифрование текста
    """
    result = []
    for char in text.lower():
        if char.isalpha():
            result.append(encrypt_map.get(char, char))
        else:
            result.append(char)
    return ''.join(result)


def decrypt(text, decrypt_map):
    """
    Дешифрование текста
    """
    result = []
    for char in text.lower():
        if char.isalpha():
            result.append(decrypt_map.get(char, char))
        else:
            result.append(char)
    return ''.join(result)


def main():
    # Создаем отображения
    encrypt_map, decrypt_map = create_cipher_mapping()
    
    print("Таблица шифрования (буква -> замена):")
    for letter in sorted(encrypt_map.keys()):
        if encrypt_map[letter] != letter:
            print(f"  {letter} -> {encrypt_map[letter]}")
    print()
    
    # Задание 1: Зашифровать текст
    print("=" * 60)
    print("ЗАДАНИЕ 1: ШИФРОВАНИЕ")
    print("=" * 60)
    
    original_text = "Some people say a man is made out of mud A poor man's made out of muscle and blood Muscle and blood and skin and bone A mind thats weak and the back thats strong Sixteen tons."
    
    print(f"Исходный текст:\n{original_text}\n")
    
    encrypted = encrypt(original_text, encrypt_map)
    print(f"Зашифрованный текст:\n{encrypted}\n")
    
    # Задание 2: Расшифровать текст
    print("=" * 60)
    print("ЗАДАНИЕ 2: ДЕШИФРОВАНИЕ")
    print("=" * 60)
    
    encrypted_text = "btkiarmputjqyurkwuwuktprmranptrrpirdttttr trpurwuktprmrapukgrnajrnefjtk.qktdbirsrmxek wrbgrrpgktdnjetrkdrimngktdnjetjrofkdrfjiaji."
    
    print(f"Зашифрованный текст:\n{encrypted_text}\n")
    
    decrypted = decrypt(encrypted_text, decrypt_map)
    print(f"Расшифрованный текст:\n{decrypted}\n")
    
    # Дополнительно: проверка на примере из условия
    print("=" * 60)
    print("ПРОВЕРКА НА ПРИМЕРЕ ИЗ УСЛОВИЯ")
    print("=" * 60)
    
    example_text = "iamfine"
    encrypted_example = encrypt(example_text, encrypt_map)
    print(f"Исходный текст: {example_text}")
    print(f"Зашифрованный: {encrypted_example}")
    print(f"Ожидалось: bkgebir")
    print(f"Совпадение: {'✓' if encrypted_example == 'bkgebir' else '✗'}")
    
    decrypted_example = decrypt(encrypted_example, decrypt_map)
    print(f"Расшифрованный обратно: {decrypted_example}")
    print(f"Совпадение с исходным: {'✓' if decrypted_example == example_text else '✗'}")


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 2. Алфавит русский (33 буквы) . Исходный текст разбит на блоки величины n = 8. 
# Буквы внутри каждого блока меняются местами перестановкой s = {1 , 8, 2, 7) (4 , 6, 5, 3).
# 1) Зашифровать текст: Скучно на этом свете господа Гоголь.
# 2) Расшифровать текст: алмрпотуевиидкчьдубьуичиьнслтактишыувбгазнваонинийсекнсе.
def apply_permutation(text, permutation, block_size = 8):
    """
    Применяет перестановку к тексту, разбитому на блоки.
    
    Args:
        text: исходный текст (строка)
        permutation: словарь, где ключ - исходная позиция (1..n), значение - новая позиция
        block_size: размер блока (по умолчанию 8)
    
    Returns:
        преобразованный текст
    """
    result = []
    
    # Разбиваем текст на блоки
    for i in range(0, len(text), block_size):
        block = text[i:i + block_size]
        
        # Если блок меньше размера, дополняем его 'ъ' (твердый знак)
        if len(block) < block_size:
            block = block + 'ъ' * (block_size - len(block))
        
        # Создаем новый блок
        new_block = [''] * block_size
        
        # Применяем перестановку
        for old_pos, new_pos in permutation.items():
            # old_pos и new_pos - от 1 до block_size
            new_block[new_pos - 1] = block[old_pos - 1]
        
        result.append(''.join(new_block))
    
    return ''.join(result)


def create_permutation():
    """
    Создает перестановку на основе циклов s = {1,8,2,7}{4,6,5,3}
    """
    # Циклы из условия
    cycle1 = [1, 8, 2, 7]
    cycle2 = [4, 6, 5, 3]
    
    # Строим отображение для шифрования: позиция -> новая позиция
    permutation = {}
    
    # Обрабатываем первый цикл
    for i in range(len(cycle1)):
        current = cycle1[i]
        next_pos = cycle1[(i + 1) % len(cycle1)]
        permutation[current] = next_pos
    
    # Обрабатываем второй цикл
    for i in range(len(cycle2)):
        current = cycle2[i]
        next_pos = cycle2[(i + 1) % len(cycle2)]
        permutation[current] = next_pos
    
    # Остальные позиции (если есть) остаются на месте
    for pos in range(1, 9):
        if pos not in permutation:
            permutation[pos] = pos
    
    return permutation


def create_inverse_permutation(permutation):
    """
    Создает обратную перестановку для дешифрования
    """
    inverse = {}
    for k, v in permutation.items():
        inverse[v] = k
    return inverse


def encrypt(plaintext, permutation, block_size = 8):
    """
    Шифрование текста с помощью перестановки
    """
    # Удаляем пробелы и знаки препинания, приводим к нижнему регистру
    import re
    plaintext = re.sub(r'[^\w\s]', '', plaintext.lower())  # удаляем пунктуацию
    plaintext = plaintext.replace(' ', '')  # удаляем пробелы
    plaintext = plaintext.replace('\n', '')  # удаляем переносы строк
    
    # Применяем перестановку
    return apply_permutation(plaintext, permutation, block_size)


def decrypt(ciphertext, inverse_permutation, block_size = 8):
    """
    Дешифрование текста с помощью обратной перестановки
    """
    # Применяем обратную перестановку
    decrypted = apply_permutation(ciphertext, inverse_permutation, block_size)
    
    # Удаляем дополняющие символы 'ъ' в конце
    decrypted = decrypted.rstrip('ъ')
    
    return decrypted


def main():
    # Создаем перестановку
    perm = create_permutation()
    inv_perm = create_inverse_permutation(perm)
    
    print("Перестановка для шифрования (позиция -> новая позиция):")
    for pos in sorted(perm.keys()):
        print(f"  {pos} -> {perm[pos]}")
    
    print("\n" + "=" * 60)
    print("ЗАДАНИЕ 1: ШИФРОВАНИЕ")
    print("=" * 60)
    
    plaintext = "Скучно на этом свете господа Гоголь."
    print(f"Исходный текст:\n{plaintext}\n")
    
    encrypted = encrypt(plaintext, perm)
    print(f"Зашифрованный текст:\n{encrypted}\n")
    
    print("=" * 60)
    print("ЗАДАНИЕ 2: ДЕШИФРОВАНИЕ")
    print("=" * 60)
    
    ciphertext = "алмрпотуевиидкчьдубьуичиьнслтактишыувбгазнваонинийсекнсе"
    print(f"Зашифрованный текст:\n{ciphertext}\n")
    
    decrypted = decrypt(ciphertext, inv_perm)
    print(f"Расшифрованный текст:\n{decrypted}\n")
    
    # Дополнительно: проверка на примере
    print("=" * 60)
    print("ПРОВЕРКА")
    print("=" * 60)
    
    test_text = "скучнонаэтомсветегосподагоголь"
    print(f"Тестовый текст: {test_text}")
    
    test_encrypted = apply_permutation(test_text, perm)
    print(f"После шифрования: {test_encrypted}")
    
    test_decrypted = apply_permutation(test_encrypted, inv_perm)
    test_decrypted = test_decrypted.rstrip('ъ')
    print(f"После дешифрования: {test_decrypted}")
    
    print(f"\nСовпадение: {'✓' if test_decrypted == test_text else '✗'}")


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 3. Зашифровать текст с помощью гаммирования, переводя все его буквы в бинарные последовательности длины 5: 
# hidden nuтber is а key = 7 8 3 3 4 13.
# Выбрать в качестве ключа свой индивидуальный номер, записанный в двоичном исчислении. 
# Индивидуальный номер равен сумме значений букв фамилии (русский язык, 33 буквы, стандартная нумерация).
# -*- coding: utf-8 -*-

# ========== 1. Таблица кодировки русских букв в 5-битные коды ==========
# Здесь нужно задать соответствие (буква -> 5-битный код)
# Например: 'а' -> 0 (00000), 'б' -> 1 (00001), ..., 'я' -> 31 (11111)
# или любой другой вариант по вашему заданию.

def letter_to_bits(letter):
    """
    Переводит русскую букву в 5-битную строку.
    ДОЗАПОЛНИТЕ ЭТУ ФУНКЦИЮ по вашему заданию.
    """
    # ПРИМЕР: если кодировка: а=0, б=1, ..., я=31
    # и letter в нижнем регистре
    rus_alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    if letter in rus_alphabet:
        code = rus_alphabet.index(letter)  # 0..31
        return format(code, '05b')
    else:
        # Для неизвестных букв (например, ё, английских) — заглушка
        return '00000'


def bits_to_letter(bits):
    """
    Переводит 5-битную строку в русскую букву.
    ОБРАТНАЯ К ТАБЛИЦЕ letter_to_bits.
    """
    rus_alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    code = int(bits, 2)
    if 0 <= code < len(rus_alphabet):
        return rus_alphabet[code]
    else:
        # Неизвестный код
        return '?'


# ========== 2. Индивидуальный номер ==========
def sum_of_name_scores(surname):
    """
    surname - строка с фамилией (русскими буквами).
    Возвращает сумму номеров букв в русском алфавите (а=1, б=2, ..., я=33).
    """
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    total = 0
    for ch in surname.lower():
        if ch in alphabet:
            total += alphabet.index(ch) + 1  # а=1, б=2, ..., я=33
    return total


def int_to_bits_gamma(number):
    """
    Переводит число в последовательность битов (без ведущих нулей).
    Затем разбивает на куски по 5 бит (последний кусок дополняется нулями до 5).
    Возвращает список 5-битных строк.
    """
    binary_str = bin(number)[2:]  # без '0b'
    # Дополняем до кратности 5 нулями справа, чтобы можно было разбить на 5-битные куски
    if len(binary_str) % 5 != 0:
        binary_str = binary_str.ljust((len(binary_str) + 4) // 5 * 5, '0')
    # Разбиваем
    return [binary_str[i:i + 5] for i in range(0, len(binary_str), 5)]


# ========== 3. Гаммирование ==========
def gamma_encrypt(text, gamma_bits_list):
    """
    text - исходная строка (русские буквы).
    gamma_bits_list - список 5-битных строк (гамма).
    Шифрует: XOR 5-битных кодов букв и гаммы.
    Возвращает зашифрованную строку (русские буквы по таблице).
    """
    encrypted_chars = []
    gamma_len = len(gamma_bits_list)
    for i, ch in enumerate(text.lower()):
        if ch.isalpha() and ch in "абвгдежзийклмнопрстуфхцчшщъыьэюя":
            # Буква -> 5 бит
            plain_bits = letter_to_bits(ch)
            # Гамма (циклически)
            gamma_bits = gamma_bits_list[i % gamma_len]
            # XOR
            xor_bits = ''.join(str(int(plain_bits[j]) ^ int(gamma_bits[j])) for j in range(5))
            # Обратно в букву
            encrypted_chars.append(bits_to_letter(xor_bits))
        else:
            # Не буква (пробел, знак) — оставляем как есть
            encrypted_chars.append(ch)
    return ''.join(encrypted_chars)


# ========== 4. Основная программа ==========
def main():
    print("=" * 60)
    print("ЗАДАНИЕ 3: ГАММИРОВАНИЕ")
    print("=" * 60)
    
    # Исходный текст для шифрования
    plaintext = "hidden nuтber is а key = 7 8 3 3 4 13"
    print("Исходный текст:", plaintext)
    
    # 1) Шифрование с ключом 7 8 3 3 4 13
    print("\n--- Шифрование с ключом 7 8 3 3 4 13 ---")
    key1_dec = [7, 8, 3, 3, 4, 13]
    # Переводим ключ в 5-битные строки
    gamma1 = [format(k, '05b') for k in key1_dec]
    print("Гамма (5-битные блоки):", gamma1)
    
    encrypted1 = gamma_encrypt(plaintext, gamma1)
    print("Зашифрованный текст:", encrypted1)
    
    # 2) Индивидуальный номер
    surname = input("\nВведите вашу фамилию (русскими буквами): ")
    individual_number = sum_of_name_scores(surname)
    print(f"Индивидуальный номер (сумма букв фамилии): {individual_number}")
    
    # Переводим номер в двоичную гамму
    gamma2 = int_to_bits_gamma(individual_number)
    print("Двоичная гамма (по 5 бит):", gamma2)
    
    encrypted2 = gamma_encrypt(plaintext, gamma2)
    print("Зашифрованный текст (с индивидуальным ключом):", encrypted2)


if __name__ == "__main__":
    main()

# ===================================================================================================================================================

# Задача 4. Назовем шифр замены, отвечающий подстановке и Е Sn, гомоморфным, если он удовлетворяет тождеству Vi, j Е Zn u(i + j) = u(i) + u(j) (modn). 
# Сколько существует гамаморфных шифров замены при фиксированном n? Как они устроены?
import math

def find_homomorphic_permutations(n):
    """
    Находит все гомоморфные шифры замены для заданного n.
    Гомоморфный шифр замены имеет вид u(i) = a*i mod n, где gcd(a,n)=1.
    
    Args:
        n: размер алфавита (положительное целое число)
    
    Returns:
        список кортежей (a, permutation), где a - множитель,
        permutation - список из n элементов (образы чисел 0..n-1)
    """
    permutations = []
    
    # Перебираем все a от 1 до n-1
    for a in range(1, n):
        if math.gcd(a, n) == 1:
            # Строим перестановку: i -> (a*i) mod n
            perm = [(a * i) % n for i in range(n)]
            permutations.append((a, perm))
    
    return permutations


def print_permutation(perm, title = ""):
    """Красиво выводит перестановку"""
    if title:
        print(title)
    n = len(perm)
    print("  i: ", end = "")
    for i in range(n):
        print(f"{i:3}", end = "")
    print()
    print("  u(i):", end = "")
    for val in perm:
        print(f"{val:3}", end = "")
    print()
    print()


def verify_homomorphism(perm, n):
    """
    Проверяет, удовлетворяет ли перестановка условию гомоморфизма:
    u(i + j) = u(i) + u(j) (mod n)
    """
    for i in range(n):
        for j in range(n):
            left = perm[(i + j) % n]
            right = (perm[i] + perm[j]) % n
            if left != right:
                return False
    return True


def demonstrate_multiplication_table(n, a):
    """
    Демонстрирует, что умножение на a mod n задает гомоморфизм
    """
    print(f"\nДемонстрация для n = {n}, a = {a} (gcd({a},{n}) = {math.gcd(a, n)}):")
    print("Проверка свойства u(i+j) = u(i) + u(j) (mod n):")
    
    for i in range(min(n, 5)):  # Показываем только первые 5 для краткости
        for j in range(min(n, 5)):
            left = (a * ((i + j) % n)) % n
            right = ((a * i) % n + (a * j) % n) % n
            print(f"  i = {i}, j = {j}: u({i} + {j}) = {left}, u({i}) + u({j}) = {right} -> {'✓' if left==right else '✗'}")
    if n > 5:
        print("  ... (для всех i,j свойство выполняется)")


def main():
    print("=" * 60)
    print("ЗАДАЧА 4: ГОМОМОРФНЫЕ ШИФРЫ ЗАМЕНЫ")
    print("=" * 60)
    print("\nТеоретический ответ:")
    print("  Количество гомоморфных шифров замены = φ(n)")
    print("  Все они имеют вид: u(i) = a·i (mod n), где gcd(a,n)=1")
    print()
    
    # Ввод размера алфавита
    try:
        n = int(input("Введите размер алфавита n (положительное целое число): "))
        if n <= 0:
            print("Ошибка: n должно быть положительным числом")
            return
    except ValueError:
        print("Ошибка: введите целое число")
        return
    
    print(f"\n{'=' * 60}")
    print(f"РЕЗУЛЬТАТЫ ДЛЯ n = {n}")
    print(f"{'=' * 60}")
    
    # Функция Эйлера
    phi_n = math.gcd(1, 1)  # временно
    phi_n = sum(1 for i in range(1, n + 1) if math.gcd(i, n) == 1)
    print(f"\nφ({n}) = {phi_n} (количество чисел, взаимно простых с {n})")
    print(f"Теоретическое количество гомоморфных шифров: {phi_n}")
    
    # Находим все гомоморфные перестановки
    permutations = find_homomorphic_permutations(n)
    
    print(f"\nНайдено перестановок: {len(permutations)}")
    
    if len(permutations) == 0:
        print(f"\nДля n = {n} нет гомоморфных шифров замены (кроме тривиального случая n = 1)")
        if n == 1:
            print("При n = 1 существует единственная перестановка: u(0) = 0")
    else:
        print(f"\nВсе гомоморфные шифры замены для n = {n}:")
        print("-" * 60)
        
        for idx, (a, perm) in enumerate(permutations, 1):
            print(f"\n{idx}. a = {a} (gcd({a},{n})={math.gcd(a,n)})")
            print_permutation(perm, f"   u(i) = {a}·i mod {n}")
            
            # Проверяем свойство гомоморфизма
            is_hom = verify_homomorphism(perm, n)
            print(f"   Свойство гомоморфизма выполняется: {'✓' if is_hom else '✗'}")
    
    # Дополнительная демонстрация
    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    
    # Показываем пример для небольшого n
    test_n = min(n, 12) if n > 1 else 2
    if test_n > 1:
        print(f"\nДемонстрация на примере n={test_n}:")
        test_perms = find_homomorphic_permutations(test_n)
        
        for a, perm in test_perms[:3]:  # Показываем не более 3 примеров
            demonstrate_multiplication_table(test_n, a)
    
    # Объяснение устройства
    print("\n" + "=" * 60)
    print("КАК УСТРОЕНЫ ГОМОМОРФНЫЕ ШИФРЫ ЗАМЕНЫ")
    print("=" * 60)
    print("""
    1. Все гомоморфные шифры замены имеют вид:
       u(i) = a·i (mod n), где gcd(a,n) = 1
    
    2. Это следует из того, что любой гомоморфизм
       циклической группы Z_n в себя задается умножением
       на некоторый элемент a ∈ Z_n
    
    3. Условие биективности (перестановка) требует,
       чтобы a был обратим в Z_n, то есть gcd(a,n) = 1
    
    4. Количество таких шифров равно φ(n) - функции Эйлера
    
    5. Примеры:
       - a = 1: тождественная перестановка
       - a = n-1: перестановка i → -i (обращение порядка)
       - Для простого n = p: все a от 1 до p-1 дают шифры
    """)


if __name__ == "__main__":
    main()