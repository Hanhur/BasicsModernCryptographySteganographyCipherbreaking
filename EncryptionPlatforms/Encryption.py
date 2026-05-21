# 3. Платформы шифрования
import random
from math import gcd

# ---------- Абстрактный класс для группы ----------
class Group:
    def multiply(self, a, b):
        raise NotImplementedError
    
    def inverse(self, a):
        raise NotImplementedError
    
    def identity(self):
        raise NotImplementedError
    
    def order(self):
        raise NotImplementedError  # для конечных групп

# ---------- 1. Конечная коммутативная группа: мультипликативная группа Z*_p ----------
class MultiplicativeGroupModP(Group):
    def __init__(self, p):
        # p должно быть простым
        self.p = p
    
    def multiply(self, a, b):
        return (a * b) % self.p
    
    def inverse(self, a):
        # расширенный алгоритм Евклида
        return pow(a, -1, self.p)
    
    def identity(self):
        return 1
    
    def order(self):
        return self.p - 1
    
    def random_element(self):
        elem = random.randint(2, self.p-1)
        return elem

# ---------- 2. Некоммутативная группа (пример: GL(2, Z_n) - обратимые матрицы 2x2 над кольцом вычетов) ----------
class GL2Zn(Group):
    def __init__(self, n):
        self.n = n
        # элементы — матрицы 2x2, где det обратим по модулю n
        self.cache = {}
    
    def det(self, mat):
        return (mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]) % self.n
    
    def is_invertible(self, mat):
        return gcd(self.det(mat), self.n) == 1
    
    def multiply(self, a, b):
        # a, b — кортежи 2x2
        return (
            ((a[0][0]*b[0][0] + a[0][1]*b[1][0]) % self.n,
             (a[0][0]*b[0][1] + a[0][1]*b[1][1]) % self.n),
            ((a[1][0]*b[0][0] + a[1][1]*b[1][0]) % self.n,
             (a[1][0]*b[0][1] + a[1][1]*b[1][1]) % self.n)
        )
    
    def inverse(self, mat):
        d = self.det(mat)
        inv_d = pow(d, -1, self.n)
        a, b, c, d_ = mat[0][0], mat[0][1], mat[1][0], mat[1][1]
        # обратная матрица: inv_d * [[d_, -b], [-c, a]]
        return (
            ( (inv_d * d_) % self.n, (-inv_d * b) % self.n ),
            ( (-inv_d * c) % self.n, (inv_d * a) % self.n )
        )
    
    def identity(self):
        return ((1, 0), (0, 1))
    
    def order(self):
        return None  # бесконечная или неизвестная (для малых n можно вычислить)
    
    def random_element(self):
        while True:
            mat = (
                (random.randint(0, self.n-1), random.randint(0, self.n-1)),
                (random.randint(0, self.n-1), random.randint(0, self.n-1))
            )
            if self.is_invertible(mat):
                return mat

# ---------- Шифрование на группе (алгебраическая криптография, групповой Эль-Гамаль) ----------
def elgamal_group_encrypt(group, message, public_key):
    """
    message — элемент группы
    public_key = (generator, pub) где pub = generator^secret
    Возвращает (c1, c2)
    """
    gen, pub = public_key
    # эфемерный ключ
    k = random.randint(2, group.order() - 1) if group.order() else random.randint(2, 100)
    # в бесконечной группе выбираем k случайно (здесь для демо маленькое)
    if group.order() is None:
        k = random.randint(2, 10)
        # для матриц нельзя просто возвести в степень так, но мы покажем только
        # на коммутативной группе для простоты. В GL2: генерируем k как элемент?
        # Но в нашем примере реализуем только для коммутативной группы.
        raise NotImplementedError("Степень для некоммутативной группы требует отдельной реализации")
    
    # Вычисляем g^k
    gk = group.multiply(gen, k)  # так как multiply не степень, а бинарная операция — нужно переделать.
    # Для корректности: нужна функция pow_element(group, elem, exponent)
    return "См. исправленную версию ниже"

# ---------- Корректная реализация с возведением в степень ----------
def group_pow(group, elem, exp):
    """быстрое возведение в степень через multiply"""
    result = group.identity()
    base = elem
    while exp > 0:
        if exp & 1:
            result = group.multiply(result, base)
        base = group.multiply(base, base)
        exp >>= 1
    return result

def elgamal_encrypt(group, message, generator, public_key):
    """
    public_key = generator^secret
    """
    secret_key = None  # закрытый ключ получателя (не передаётся сюда)
    # На самом деле public_key = generator^secret
    k = random.randint(2, group.order() - 1) if group.order() else random.randint(2, 20)
    
    c1 = group_pow(group, generator, k)
    shared_secret = group_pow(group, public_key, k)
    c2 = group.multiply(message, shared_secret)
    return (c1, c2)

def elgamal_decrypt(group, ciphertext, secret_key, generator):
    c1, c2 = ciphertext
    shared_secret = group_pow(group, c1, secret_key)
    shared_secret_inv = group.inverse(shared_secret)
    message = group.multiply(c2, shared_secret_inv)
    return message

# ---------- Демонстрация ----------
if __name__ == "__main__":
    print("=== Алгебраическая криптография: платформа — группа ===")
    
    # 1. Коммутативная платформа: Z*_23
    print("\n1. Конечная коммутативная группа: Z*_23")
    G1 = MultiplicativeGroupModP(23)
    gen1 = 5  # генератор
    secret1 = 6
    pub1 = group_pow(G1, gen1, secret1)
    
    message1 = 10  # исходное сообщение (элемент группы)
    
    c1, c2 = elgamal_encrypt(G1, message1, gen1, pub1)
    dec1 = elgamal_decrypt(G1, (c1, c2), secret1, gen1)
    
    print(f"Сообщение: {message1}")
    print(f"Зашифровано: ({c1}, {c2})")
    print(f"Расшифровано: {dec1}")
    
    # 2. Некоммутативная платформа: GL(2, Z_7) (маленький модуль для демонстрации)
    print("\n2. Некоммутативная группа: обратимые матрицы 2x2 над Z_7")
    G2 = GL2Zn(7)
    # В GL(2, Z_7) нельзя просто так взять степень элемента — это корректно,
    # но генератор выберем фиксированный обратимый элемент
    # Для Эль-Гамаля нужна циклическая подгруппа — здесь для примера возьмём конкретную матрицу
    gen2 = ((2, 0), (0, 1))  # det=2, обратим по модулю 7
    # Убедимся, что обратим
    if not G2.is_invertible(gen2):
        gen2 = ((1, 1), (0, 1))
    
    # Закрытый ключ (скаляр — степень)
    secret2 = 3
    pub2 = group_pow(G2, gen2, secret2)
    
    # Сообщение — матрица
    message2 = ((1, 2), (3, 4))
    
    c1_mat, c2_mat = elgamal_encrypt(G2, message2, gen2, pub2)
    dec2_mat = elgamal_decrypt(G2, (c1_mat, c2_mat), secret2, gen2)
    
    print("Сообщение (матрица):")
    for row in message2:
        print(row)
    print("Зашифровано (c1, c2):")
    print("c1 =", c1_mat)
    print("c2 =", c2_mat)
    print("Расшифровано:")
    for row in dec2_mat:
        print(row)
    
    print("\nВывод: программа демонстрирует алгебраическую криптографию, где платформа — группа.")