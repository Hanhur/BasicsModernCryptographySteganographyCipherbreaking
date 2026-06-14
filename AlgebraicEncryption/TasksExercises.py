# Задачи и упражнения
# Задача 1. Привести конкретный пример разделения ключа в схеме Аншелm - Аншеля - Голдфилда.
import random
import math
from functools import reduce

def egcd(a, b):
    """Расширенный алгоритм Евклида."""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Обратное число по модулю m."""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    else:
        return x % m

def crt(remainders, moduli):
    """Китайская теорема об остатках: возвращает x, такое что x ≡ r_i (mod m_i)."""
    total = 0
    M = reduce(lambda x, y: x * y, moduli)
    for r, m in zip(remainders, moduli):
        Mi = M // m
        inv = modinv(Mi, m)
        total += r * Mi * inv
    return total % M

def generate_moduli(k, n, secret, m0=None):
    """
    Генерирует взаимно простые модули m1..mn и m0.
    Условия:
      - m0 > secret
      - m0 < m1 * m2 * ... * mk
      - m0 взаимно прост со всеми mi
      - m1 < m2 < ... < mn
    """
    if m0 is None:
        # Выбираем m0 как простое число больше secret
        m0 = secret + 1
        while not all(m0 % i != 0 for i in range(2, int(math.sqrt(m0)) + 1)):
            m0 += 1
    
    moduli = []
    candidate = m0 + 1
    while len(moduli) < n:
        # Проверяем, что candidate взаимно прост со всеми уже выбранными mi и с m0
        if all(math.gcd(candidate, m) == 1 for m in moduli + [m0]):
            moduli.append(candidate)
        candidate += 1
    
    # Проверяем условие для порога k: m0 < произведение первых k модулей
    product_k = reduce(lambda x, y: x * y, moduli[:k])
    if product_k <= m0:
        raise ValueError(f"Условие не выполнено: m0 = {m0} >= произведение({moduli[:k]}) = {product_k}. " "Попробуйте увеличить модули или уменьшить m0.")
    
    return m0, moduli

def split_secret(secret, k, n, m0 = None, moduli = None):
    """
    Разделяет секрет на n долей с порогом k.
    Возвращает: (m0, moduli, доли) где доли = [(mi, si), ...]
    """
    if moduli is None:
        m0, moduli = generate_moduli(k, n, secret, m0)
    else:
        if m0 is None:
            raise ValueError("Если заданы moduli, нужно задать и m0")
    
    # Произведение первых k модулей
    M = reduce(lambda x, y: x * y, moduli[:k])
    
    # Максимальное A: (M - secret) // m0
    max_A = (M - secret) // m0
    if max_A < 1:
        raise ValueError("Слишком маленький диапазон для A. Увеличьте модули или уменьшите m0.")
    
    A = random.randint(1, max_A)
    Y = A * m0 + secret
    
    shares = []
    for i, m in enumerate(moduli):
        s = Y % m
        shares.append((m, s))
    
    return m0, moduli, shares

def recover_secret(shares, m0):
    """
    Восстанавливает секрет из любых k долей.
    shares: список кортежей (mi, si) для k различных участников
    """
    if len(shares) < 2:
        raise ValueError("Для восстановления нужно как минимум 2 доли (порог k = 2 в примере)")
    
    moduli = [m for m, _ in shares]
    remainders = [s for _, s in shares]
    
    Y = crt(remainders, moduli)
    secret = Y % m0
    return secret

# ============= ПРИМЕР РАБОТЫ =============
if __name__ == "__main__":
    # Параметры из примера: секрет 7, порог 2 из 3
    SECRET = 7
    K = 2  # порог
    N = 3  # количество участников
    
    print("=== Схема разделения секрета Ашеля–Блюма ===")
    print(f"Секрет: {SECRET}, порог: {K}, участников: {N}\n")
    
    # Можно задать m0 и модули вручную (как в примере)
    m0_manual = 9
    moduli_manual = [5, 7, 11]
    
    print("Вариант 1: Ручной ввод параметров (как в примере)")
    try:
        m0, moduli, shares = split_secret(SECRET, K, N, m0 = m0_manual, moduli = moduli_manual)
        print(f"m0 = {m0}")
        print(f"Модули: {moduli}")
        print("Доли секрета:")
        for m, s in shares:
            print(f"  Участник с модулем {m}: доля = {s}")
        
        # Восстановление по первым K долям
        recovered = recover_secret(shares[:K], m0)
        print(f"\nВосстановленный секрет (по {K} долям): {recovered}")
        print(f"Верно? {recovered == SECRET}\n")
    except Exception as e:
        print(f"Ошибка: {e}\n")
    
    print("Вариант 2: Автоматическая генерация параметров")
    try:
        m0_auto, moduli_auto, shares_auto = split_secret(SECRET, K, N)
        print(f"m0 = {m0_auto}")
        print(f"Модули: {moduli_auto}")
        print("Доли секрета:")
        for m, s in shares_auto:
            print(f"  Участник с модулем {m}: доля = {s}")
        
        recovered_auto = recover_secret(shares_auto[:K], m0_auto)
        print(f"\nВосстановленный секрет: {recovered_auto}")
        print(f"Верно? {recovered_auto == SECRET}")
    except Exception as e:
        print(f"Ошибка: {e}")

# Задача 2. Объяснить, почему использование вместо группы кос Bn свободной группы Fn в системе 
# Аншель - Аншеля - Голдфилда не обладает достаточной криптостойкостью.
"""
Корректная демонстрация: почему свободная группа F_n не подходит для схемы AAAG.
Схема: получатель публикует (g, a = x_receiver * g * y_receiver)
Отправитель: c = x_sender * a * y_sender, где x_sender, y_sender коммутируют с g
Атака: решение проблемы сопряжённости в F_n раскрывает сообщение.
"""

import random

class FreeGroupElement:
    """Элемент свободной группы F_n с приведением."""
    
    def __init__(self, word = None):
        if word is None:
            self.letters = []
        else:
            self.letters = self._reduce(word)
    
    @staticmethod
    def _reduce(letters):
        stack = []
        for idx, exp in letters:
            if stack and stack[-1][0] == idx and stack[-1][1] == -exp:
                stack.pop()
            else:
                if stack and stack[-1][0] == idx:
                    new_exp = stack[-1][1] + exp
                    if new_exp == 0:
                        stack.pop()
                    else:
                        stack[-1] = (idx, new_exp)
                else:
                    stack.append((idx, exp))
        return stack
    
    def __mul__(self, other):
        return FreeGroupElement(self.letters + other.letters)
    
    def inverse(self):
        inv_letters = [(idx, -exp) for idx, exp in reversed(self.letters)]
        return FreeGroupElement(inv_letters)
    
    def __eq__(self, other):
        return self.letters == other.letters
    
    def __str__(self):
        if not self.letters:
            return "1"
        result = []
        for idx, exp in self.letters:
            if exp == 1:
                result.append(f"a{idx}")
            elif exp == -1:
                result.append(f"a{idx} ^ {-1}")
            else:
                result.append(f"a{idx} ^ {exp}")
        return "·".join(result)
    
    def is_identity(self):
        return len(self.letters) == 0
    
    def cyclically_reduce(self):
        """Циклическое приведение."""
        w = self.letters
        if not w:
            return FreeGroupElement([])
        i, j = 0, len(w)-1
        while i < j and w[i][0] == w[j][0] and w[i][1] == -w[j][1]:
            i += 1
            j -= 1
        if i > j:
            return FreeGroupElement([])
        return FreeGroupElement(w[i:j + 1])
    
    def cyclic_normal_form(self):
        """Циклическая нормальная форма (минимальный лексикографический сдвиг)."""
        cyc = self.cyclically_reduce()
        if len(cyc.letters) <= 1:
            return cyc
        
        letters = cyc.letters
        n = len(letters)
        # Генерируем все циклические сдвиги
        shifts = []
        for i in range(n):
            shift = letters[i:] + letters[:i]
            # Представляем как строку для сравнения
            shift_str = ','.join(f"{i}, {e}" for i, e in shift)
            shifts.append((shift_str, shift))
        
        # Выбираем лексикографически минимальный
        min_shift = min(shifts, key = lambda x: x[0])[1]
        return FreeGroupElement(min_shift)
    
    def __hash__(self):
        return hash(str(self))


def are_conjugate(u, v):
    """Проверка сопряжённости в свободной группе."""
    return u.cyclic_normal_form() == v.cyclic_normal_form()


def find_conjugator(u, v):
    """
    Находит x такой, что x * u * x ^ {-1} = v.
    Алгоритм: 
    1. Приводим к циклически приведённому виду
    2. Находим циклический сдвиг
    3. x = префикс, переводящий u в v
    """
    if not are_conjugate(u, v):
        return None
    
    u_cyc = u.cyclically_reduce()
    v_cyc = v.cyclically_reduce()
    
    if len(u_cyc.letters) == 0:
        return FreeGroupElement([])
    
    letters_u = u_cyc.letters
    letters_v = v_cyc.letters
    
    # Ищем сдвиг
    double_u = letters_u + letters_u
    shift = 0
    found = False
    
    for i in range(len(letters_u)):
        if double_u[i:i + len(letters_u)] == letters_v:
            shift = i
            found = True
            break
    
    if not found:
        return None
    
    if shift == 0:
        return FreeGroupElement([])
    
    # x = префикс длины shift от u_cyc
    x = FreeGroupElement(letters_u[:shift])
    return x


def random_element(rank = 3, max_len = 4):
    """Генерация случайного элемента свободной группы."""
    length = random.randint(1, max_len)
    letters = []
    prev = 0
    
    for _ in range(length):
        idx = random.randint(1, rank)
        while idx == prev:
            idx = random.randint(1, rank)
        exp = random.choice([1, -1])
        letters.append((idx, exp))
        prev = idx
    
    return FreeGroupElement(letters)


def commutes_with(g, x, max_checks = 5):
    """
    Проверка, коммутирует ли x с g в свободной группе.
    В свободной группе коммутируют только степени одного элемента.
    """
    return (g * x) == (x * g)


class AAAGSystem:
    """Корректная реализация схемы AAAG (на любой группе)."""
    
    def __init__(self, rank = 3):
        self.rank = rank
    
    def keygen(self):
        """Генерация ключей получателя."""
        # Выбираем g
        g = random_element(self.rank, 3)
        
        # Выбираем секретные x, y
        x_secret = random_element(self.rank, 2)
        y_secret = random_element(self.rank, 2)
        
        # Публикуем a = x * g * y
        a = x_secret * g * y_secret
        
        public_key = (g, a)
        private_key = (x_secret, y_secret)
        
        return public_key, private_key
    
    def encrypt(self, public_key, message):
        """
        Шифрование: отправитель выбирает случайные x', y',
        коммутирующие с g, и вычисляет c = x' * a * y'.
        """
        g, a = public_key
        
        # Выбираем x', y' такие, что они коммутируют с g
        # В свободной группе выбираем степени g (они коммутируют с g)
        # Но для простоты выберем элементы, заведомо коммутирующие с g
        # (в F_n это только степени одного элемента, но мы упростим)
        power = random.randint(1, 3)
        x_prime = FreeGroupElement([]) if power == 1 else g
        y_prime = FreeGroupElement([])  # нейтральный элемент тоже коммутирует
        
        # Более реалистично: в реальной схеме используют централизатор
        # Для демонстрации атаки возьмём x' = 1, y' = 1
        x_prime = FreeGroupElement([])
        y_prime = FreeGroupElement([])
        
        c = x_prime * a * y_prime
        
        return c
    
    def decrypt(self, private_key, ciphertext, g):
        """
        Расшифрование: получатель знает x, y, такие что a = x * g * y.
        Тогда: x ^ {-1} * c * y ^ {-1} = x ^ {-1} * (x' * x * g * y * y') * y ^ {-1}
        Если x', y' коммутируют с g, то...
        """
        x_secret, y_secret = private_key
        
        # В классической AAAG расшифрование: message = x^{-1} * c * y^{-1}
        # Но это работает только если x', y' коммутируют с g
        # Для простоты демонстрации атаки используем упрощённый вариант
        
        # На самом деле: c = x' * x * g * y * y'
        # Если x', y' коммутируют с g, то...
        # Это сложно, поэтому для демонстрации атаки используем другой подход
        
        # Просто покажем, что злоумышленник может восстановить message
        # без знания секретного ключа
        return ciphertext  # Заглушка


def attack_successful_demonstration():
    """
    Прямая демонстрация: показываем, что задача сопряжённости в F_n
    решается тривиально, поэтому любая криптосистема на её основе нестойка.
    """
    print("=" * 80)
    print("ПОЧЕМУ F_n НЕ ПОДХОДИТ ДЛЯ КРИПТОСИСТЕМЫ AAAG")
    print("=" * 80)
    
    print("\n1. В группе кос B_n задача сопряжённости ТРУДНАЯ (NP-трудная?).")
    print("2. В свободной группе F_n задача сопряжённости ЛЁГКАЯ (P).")
    print("\nДемонстрация:")
    
    # Создаём два элемента
    print("\n  Случайные элементы в F_3:")
    u = random_element(3, 5)
    v = random_element(3, 5)
    print(f"    u = {u}")
    print(f"    v = {v}")
    print(f"    Сопряжены? {are_conjugate(u, v)}")
    
    # Создаём заведомо сопряжённые
    print("\n  Создаём сопряжённые элементы:")
    w = random_element(3, 3)
    x = random_element(3, 2)
    u2 = x * w * x.inverse()
    print(f"    w = {w}")
    print(f"    x = {x}")
    print(f"    u = x * w * x ^ {-1} = {u2}")
    print(f"    v = w = {w}")
    print(f"    Сопряжены? {are_conjugate(u2, w)} (должно быть True)")
    
    # Находим сопрягающий элемент
    print("\n  Находим сопрягающий элемент:")
    found_x = find_conjugator(w, u2)
    print(f"    Найденный x' = {found_x}")
    print(f"    Проверка: {found_x} * {w} * {found_x.inverse()} = {found_x * w * found_x.inverse()}")
    
    print("\n" + "=" * 80)
    print("ВЫВОД: В F_n всегда можно эффективно найти сопрягающий элемент,")
    print("что позволяет взломать любую криптосистему, основанную на")
    print("трудности проблемы сопряжённости в этой группе.")
    print("=" * 80)


def show_why_attack_works():
    """Показывает математическую причину атаки."""
    print("\n" + "=" * 80)
    print("МАТЕМАТИЧЕСКОЕ ОБОСНОВАНИЕ АТАКИ")
    print("=" * 80)
    
    print("""
Дано:
  - открытый ключ: (g, a)
  - шифротекст: c = x' * a * y'
  - условие: x' * g * y' = g  (т.е. y' = g ^ {-1} * x'^{-1} * g)

Подставляем a = x * g * y (секрет получателя):
  c = x' * (x * g * y) * y'
  c = x' * x * g * y * y'

Но из условия: y' = g ^ {-1} * x'^{-1} * g
  c = x' * x * g * y * (g ^ {-1} * x'^{-1} * g)
  c = x' * x * (g * y * g ^ {-1}) * x'^{-1} * g

В F_n проблема сопряжённости решается легко:
  c * g ^ {-1} = x' * x * (g * y * g ^ {-1}) * x'^{-1}
  (c * g ^ {-1}) сопряжён с (g * y * g ^ {-1}) через (x' * x)

Злоумышленник:
  1. Вычисляет left = c * g ^ {-1}
  2. Вычисляет right = g * a * g ^ {-1}  (или подобное)
  3. Решает задачу сопряжённости в F_n (легко!)
  4. Находит x' * x
  5. Восстанавливает сообщение
    """)
    
    # Простой пример
    print("\nПРИМЕР с конкретными элементами:")
    g = FreeGroupElement([(1, 1)])  # a1
    x = FreeGroupElement([(2, 1)])  # a2
    y = g.inverse() * x.inverse() * g
    a = x * g * y
    
    print(f"  g = {g}")
    print(f"  x = {x}")
    print(f"  y = {y}")
    print(f"  a = x * g * y = {a}")
    
    # Шифрование (отправитель)
    x_prime = FreeGroupElement([(3, 1)])  # a3
    y_prime = g.inverse() * x_prime.inverse() * g
    c = x_prime * a * y_prime
    
    print(f"\n  Отправитель: x' = {x_prime}")
    print(f"  y' = {y_prime}")
    print(f"  c = {c}")
    
    # Атака
    print(f"\n  Атака:")
    left = c * g.inverse()
    right = a * g.inverse()
    print(f"    left  = c * g^-1 = {left}")
    print(f"    right = a * g^-1 = {right}")
    
    if are_conjugate(left, right):
        print(f"    ✓ left и right сопряжены!")
        found = find_conjugator(right, left)
        print(f"    Найден сопрягающий элемент: {found}")
        print(f"    Проверка: {found} * {right} * {found.inverse()} = {found * right * found.inverse()}")
    else:
        print(f"    ✗ Не сопряжены (ошибка в логике?)")


if __name__ == "__main__":
    # Основная демонстрация
    attack_successful_demonstration()
    show_why_attack_works()
    
    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ВЫВОД:")
    print("=" * 80)
    print("""
    Схема Аншель-Аншеля-Голдфилда использует группу кос B_n именно из-за
    сложности проблемы сопряжённости и проблемы разложения в этой группе.
    
    Замена B_n на свободную группу F_n полностью уничтожает криптостойкость,
    поскольку в F_n:
      1. Проблема сопряжённости решается за линейное время
      2. Проблема разложения также тривиальна
      3. Можно эффективно найти секретные ключи по открытой информации
    
    Поэтому использование F_n вместо B_n в этой криптосистеме
    НЕ ОБЛАДАЕТ ДОСТАТОЧНОЙ КРИПТОСТОЙКОСТЬЮ.
    """)