# 2. гост р 34.10-94.
import random
import hashlib
from typing import Tuple, Optional

class GOST341094:
    """
    Реализация ГОСТ Р 34.10-94 (российский стандарт электронной подписи)
    Основан на схеме Эль-Гамаля, похож на DSS
    """
    
    def __init__(self, p: Optional[int] = None, q: Optional[int] = None, f: Optional[int] = None):
        """
        Инициализация параметров стандарта
        
        Args:
            p: простое число, 2 ^ 509 < p < 2 ^ 512 или 2 ^ 1020 < p < 2 ^ 1024
            q: простое число, 2 ^ 254 < q < 2 ^ 256, q | (p - 1)
            f: порождающий элемент подгруппы порядка q
        """
        if p is None or q is None or f is None:
            # Генерируем параметры по умолчанию (маленькие для демонстрации)
            # В реальности должны использоваться простые числа указанных размеров
            self.p, self.q, self.f = self._generate_params()
        else:
            self.p = p
            self.q = q
            self.f = f
            
        # Открытые данные: (p, q, f, y) - y вычисляется при генерации ключа
        self.y = None
        # Секретный ключ: a
        self.a = None
        
    def _generate_params(self) -> Tuple[int, int, int]:
        """
        Генерирует параметры p, q, f для демонстрации
        В реальном использовании должны быть использованы простые числа
        размером 2 ^ 254 < q < 2 ^ 256 и 2 ^ 509 < p < 2 ^ 512
        """
        # Для демонстрации используем маленькие простые числа
        # В реальном коде здесь должна быть генерация больших простых чисел
        
        # Пример: p = 23, q = 11 (q | p-1, т.е. 11 | 22)
        p = 23
        q = 11
        
        # Находим порождающий элемент подгруппы порядка q
        # Для p=23, q=11, подгруппа порядка 11 имеет генератор 2
        f = 2
        
        print(f"Сгенерированы параметры (демонстрационные): p = {p}, q = {q}, f = {f}")
        print("ВНИМАНИЕ: Для реального использования нужны простые числа 2 ^ 254 < q < 2 ^ 256")
        return p, q, f
    
    def _find_generator(self) -> int:
        """
        Находит порождающий элемент подгруппы порядка q
        Соответствует алгоритму из стандарта
        """
        # Проверяем случайные элементы g, пока не найдем f порядка q
        while True:
            g = random.randint(2, self.p - 2)
            f = pow(g, (self.p - 1) // self.q, self.p)
            if f != 1:
                return f
    
    def generate_key_pair(self) -> Tuple[int, int]:
        """
        Генерирует пару ключей (секретный и открытый)
        
        Returns:
            (a, y): секретный ключ a и открытый ключ y
        """
        # Выбираем долгосрочный секретный ключ a
        # НЕДОСТАТОК СТАНДАРТА: допускает a = 0
        self.a = random.randint(0, self.q - 1)
        
        # Вычисляем открытый ключ y = f^a mod p mod q
        self.y = pow(self.f, self.a, self.p) % self.q
        
        print(f"Сгенерированы ключи: a = {self.a}, y = {self.y}")
        if self.a == 0:
            print("ПРЕДУПРЕЖДЕНИЕ: Секретный ключ a = 0 (слабость стандарта!)")
        
        return self.a, self.y
    
    def _hash_message(self, message: bytes) -> int:
        """
        Хэширует сообщение с использованием ГОСТ Р 34.11-94 (имитация)
        В реальности используется ГОСТ Р 34.11-94
        
        Args:
            message: сообщение в байтах
            
        Returns:
            хэш-значение в Z_q
        """
        # В реальности здесь должен быть ГОСТ Р 34.11-94
        # Используем SHA-256 для демонстрации
        hash_bytes = hashlib.sha256(message).digest()
        hash_int = int.from_bytes(hash_bytes, 'big') % self.q
        
        # НЕДОСТАТОК СТАНДАРТА: замена h(m) = 0 на 1
        if hash_int == 0:
            print("ВНИМАНИЕ: h(m) = 0 mod q, заменяем на 1 (слабость стандарта!)")
            return 1
        
        return hash_int
    
    def sign(self, message: bytes, k: Optional[int] = None) -> Tuple[int, int]:
        """
        Создает электронную подпись (r, s) для сообщения
        
        Args:
            message: сообщение для подписи
            k: сессионный ключ (если не указан, генерируется случайно)
            
        Returns:
            (r, s): электронная подпись
        """
        if self.a is None:
            raise ValueError("Сначала сгенерируйте ключи вызовом generate_key_pair()")
        
        h = self._hash_message(message)
        
        # Генерация сессионного ключа k
        if k is None:
            k = random.randint(0, self.q - 1)
        
        # НЕДОСТАТОК СТАНДАРТА: допускает k = 0
        if k == 0:
            print("ПРЕДУПРЕЖДЕНИЕ: Сессионный ключ k = 0 (слабость стандарта!)")
        
        # Вычисляем r = (f^k mod p) mod q
        r = pow(self.f, k, self.p) % self.q
        
        # Если r = 0, нужно выбрать новый k (по стандарту)
        if r == 0:
            print("r = 0, выбираем новый k")
            return self.sign(message, None)
        
        # Вычисляем s = (k*h + a*r) mod q
        s = (k * h + self.a * r) % self.q
        
        # Если s = 0, нужно выбрать новый k (по стандарту)
        if s == 0:
            print("s = 0, выбираем новый k")
            return self.sign(message, None)
        
        print(f"Подпись создана: r = {r}, s = {s}, h(m) = {h}, k = {k}")
        return r, s
    
    def verify(self, message: bytes, r: int, s: int) -> bool:
        """
        Проверяет правильность электронной подписи
        
        Args:
            message: сообщение
            r, s: подпись
            
        Returns:
            True, если подпись верна, иначе False
        """
        if self.y is None:
            raise ValueError("Сначала сгенерируйте ключи вызовом generate_key_pair()")
        
        # Проверка неравенств 0 < r < q и 0 < s < q
        if not (0 < r < self.q and 0 < s < self.q):
            print(f"Подпись неверна: r = {r}, s = {s} вне допустимого диапазона")
            return False
        
        h = self._hash_message(message)
        
        # Вычисляем w = h^(-1) mod q
        try:
            w = pow(h, -1, self.q)
        except ValueError:
            # h = 0 mod q, но мы уже заменили 0 на 1 в _hash_message
            # Это еще одно место, где проявляется слабость стандарта
            print("Ошибка: h(m) = 0 mod q (должно быть заменено на 1)")
            return False
        
        # Вычисляем v = (f^(w*s) * y^(-w*r) mod p) mod q
        # y = f^a mod p, поэтому y^(-w*r) = f^(-a*w*r)
        term1 = pow(self.f, (w * s) % self.q, self.p)
        term2 = pow(self.y, (-w * r) % self.q, self.p)
        v = (term1 * term2) % self.p % self.q
        
        print(f"Проверка: v = {v}, r = {r}")
        return v == r


def demonstrate_weaknesses():
    """
    Демонстрация слабостей ГОСТ Р 34.10-94
    """
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ СЛАБОСТЕЙ СТАНДАРТА ГОСТ Р 34.10-94")
    print("=" * 60)
    
    # Инициализация с параметрами (для демонстрации используем маленькие числа)
    gost = GOST341094()
    
    # 1. Генерация ключей с a = 0
    print("\n1. Слабость: секретный ключ a = 0")
    gost.generate_key_pair()
    print(f"Открытый ключ y = {gost.y}")
    if gost.a == 0:
        print("Ключ a = 0! Любой может подделать подпись.")
    
    # 2. Демонстрация корректной подписи
    print("\n2. Корректная подпись")
    message = b"Hello, World!"
    r, s = gost.sign(message)
    is_valid = gost.verify(message, r, s)
    print(f"Подпись верна: {is_valid}")
    
    # 3. Демонстрация замены h(m) = 0 на 1
    print("\n3. Слабость: замена h(m) = 0 на 1")
    # Создаем сообщение, которое хэшируется в 0 (для демонстрации имитируем)
    # В реальности найти такое сообщение сложно, но теоретически возможно
    print("Если h(m) = 0 mod q, стандарт заменяет его на 1")
    print("Это нарушает привязку подписи к документу!")
    
    # 4. Демонстрация проблемы с двумя документами
    print("\n4. Атака: два документа с одинаковым h(m) mod q")
    message1 = b"Document 1"
    message2 = b"Document 2"
    print(f"Подпись документа 1: {gost.sign(message1)[0]}, {gost.sign(message1)[1]}")
    print(f"Подпись документа 2: {gost.sign(message2)[0]}, {gost.sign(message2)[1]}")
    print("Если h(m1) = h(m2) mod q, подписи будут одинаковыми!")


def main():
    """
    Полная демонстрация работы стандарта
    """
    print("=" * 60)
    print("РЕАЛИЗАЦИЯ ГОСТ Р 34.10-94")
    print("=" * 60)
    
    # 1. Инициализация и генерация ключей
    print("\n1. Инициализация параметров")
    gost = GOST341094()
    
    print("\n2. Генерация ключей")
    private_key, public_key = gost.generate_key_pair()
    print(f"Секретный ключ a: {private_key}")
    print(f"Открытый ключ y: {public_key}")
    
    # 2. Подпись сообщения
    print("\n3. Подпись сообщения")
    message = b"Test message for GOST R 34.10-94"
    print(f"Сообщение: {message.decode('utf-8', errors = 'ignore')}")
    
    r, s = gost.sign(message)
    print(f"Подпись: r = {r}, s = {s}")
    
    # 3. Проверка подписи
    print("\n4. Проверка подписи")
    is_valid = gost.verify(message, r, s)
    print(f"Подпись верна: {is_valid}")
    
    # 4. Проверка с измененным сообщением
    print("\n5. Проверка с измененным сообщением")
    modified_message = b"Modified message for GOST R 34.10-94"
    is_valid = gost.verify(modified_message, r, s)
    print(f"Подпись для измененного сообщения верна: {is_valid}")
    
    # 5. Демонстрация слабостей
    demonstrate_weaknesses()


if __name__ == "__main__":
    main()