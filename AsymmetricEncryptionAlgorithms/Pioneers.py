# Первопроходцы
"""
Протокол обмена ключами Диффи-Хеллмана
Чистый Python, без numpy
Симуляция процесса из статьи: два незнакомца в интернете создают общий секрет
"""

import random
import hashlib

class DiffieHellman:
    """
    Класс, реализующий протокол Диффи-Хеллмана
    """
    
    def __init__(self, p = None, g = None):
        """
        Инициализация с параметрами или генерация новых
        
        p - большое простое число (модуль) - это наша "общая желтая краска"
        g - первообразный корень по модулю p (основание)
        """
        if p is None or g is None:
            # Генерируем безопасные параметры для демонстрации
            # В реальной жизни используются числа длиной 2048+ бит
            self.p = 23  # Простое число (для примера)
            self.g = 5   # Первообразный корень по модулю 23
        else:
            self.p = p
            self.g = g
        
        # Секретный ключ (число) - это наша "красная" или "синяя" краска
        self.private_key = None
        
        # Публичный ключ (результат смешивания с общей краской)
        self.public_key = None
        
        # Общий секретный ключ (после обмена)
        self.shared_secret = None
    
    def generate_private_key(self):
        """
        Генерирует случайный секретный ключ (число от 2 до p-2)
        Это наш личный цвет краски, который мы никому не показываем
        """
        self.private_key = random.randint(2, self.p - 2)
        return self.private_key
    
    def compute_public_key(self):
        """
        Вычисляет публичный ключ по формуле: A = g^private_key mod p
        Это смесь нашей секретной краски с общей (желтой)
        """
        if self.private_key is None:
            raise ValueError("Сначала сгенерируйте секретный ключ!")
        
        # g^private_key mod p
        self.public_key = pow(self.g, self.private_key, self.p)
        return self.public_key
    
    def compute_shared_secret(self, other_public_key):
        """
        Вычисляет общий секрет: shared = other_public_key^private_key mod p
        Это финальное смешивание: 
        - мы берем чужую смешанную краску (other_public_key)
        - смешиваем с нашей секретной (private_key)
        - получаем общий цвет
        """
        if self.private_key is None:
            raise ValueError("Сначала сгенерируйте секретный ключ!")
        
        self.shared_secret = pow(other_public_key, self.private_key, self.p)
        return self.shared_secret
    
    def derive_key(self, shared_secret=None):
        """
        Преобразует числовой общий секрет в байтовый ключ для шифрования
        Используем SHA-256 для получения ключа фиксированной длины
        """
        if shared_secret is None:
            shared_secret = self.shared_secret
        
        if shared_secret is None:
            raise ValueError("Нет общего секрета!")
        
        # Преобразуем число в байты и хешируем
        secret_bytes = str(shared_secret).encode('utf-8')
        key = hashlib.sha256(secret_bytes).digest()
        return key
    
    def simulate_exchange(self, other_public_key):
        """
        Полный цикл: вычисляем общий секрет на основе публичного ключа собеседника
        """
        self.compute_shared_secret(other_public_key)
        return self.derive_key()


def demo_diffie_hellman():
    """
    Демонстрация работы протокола между двумя сторонами: Алиса и Боб
    """
    print("=" * 60)
    print("ПРОТОКОЛ ДИФФИ-ХЕЛЛМАНА")
    print("Симуляция обмена ключами между Алисой и Бобом")
    print("=" * 60)
    
    # 1. Общедоступные параметры (знают все, даже злоумышленник)
    p = 23  # простое число
    g = 5   # первообразный корень
    
    print(f"\n[ОБЩИЕ ПАРАМЕТРЫ]")
    print(f"Простое число (модуль) p = {p}")
    print(f"Основание g = {g}")
    print(f"(Это наша 'желтая краска' - ее знают все)")
    
    # 2. Создаем участников
    alice = DiffieHellman(p, g)
    bob = DiffieHellman(p, g)
    
    # 3. Каждый генерирует свой СЕКРЕТНЫЙ ключ (личная краска)
    alice_private = alice.generate_private_key()
    bob_private = bob.generate_private_key()
    
    print(f"\n[ШАГ 1: ГЕНЕРАЦИЯ СЕКРЕТНЫХ КЛЮЧЕЙ]")
    print(f"Алиса выбрала секретное число: {alice_private} (это ее 'красная краска')")
    print(f"Боб выбрал секретное число: {bob_private} (это его 'синяя краска')")
    print("(Эти числа НИКОГДА не передаются по сети!)")
    
    # 4. Каждый вычисляет свой ПУБЛИЧНЫЙ ключ
    alice_public = alice.compute_public_key()
    bob_public = bob.compute_public_key()
    
    print(f"\n[ШАГ 2: ВЫЧИСЛЕНИЕ ПУБЛИЧНЫХ КЛЮЧЕЙ]")
    print(f"Алиса отправляет Бобу: A = {g} ^ {alice_private} mod {p} = {alice_public}")
    print(f"Боб отправляет Алисе: B = {g} ^ {bob_private} mod {p} = {bob_public}")
    print("(Эти числа передаются по открытому каналу - их видит злоумышленник!)")
    
    # 5. Каждый вычисляет ОБЩИЙ СЕКРЕТ
    alice_shared = alice.compute_shared_secret(bob_public)
    bob_shared = bob.compute_shared_secret(alice_public)
    
    print(f"\n[ШАГ 3: ВЫЧИСЛЕНИЕ ОБЩЕГО СЕКРЕТА]")
    print(f"Алиса вычисляет: {bob_public} ^ {alice_private} mod {p} = {alice_shared}")
    print(f"Боб вычисляет: {alice_public} ^ {bob_private} mod {p} = {bob_shared}")
    
    # 6. Проверка
    print(f"\n[РЕЗУЛЬТАТ]")
    if alice_shared == bob_shared:
        print(f"✅ Общий секрет успешно согласован: {alice_shared}")
        print(f"(Это и есть наш общий 'цвет' - грязно-коричневый в метафоре)")
        
        # 7. Получаем ключ для шифрования
        alice_key = alice.derive_key()
        bob_key = bob.derive_key()
        
        print(f"\n[КЛЮЧ ШИФРОВАНИЯ]")
        print(f"Алиса получила ключ: {alice_key.hex()[:32]}...")
        print(f"Боб получил ключ: {bob_key.hex()[:32]}...")
        
        if alice_key == bob_key:
            print("✅ Ключи идентичны! Можно начинать шифрованное общение.")
        else:
            print("❌ Ошибка! Ключи не совпадают.")
    else:
        print("❌ Ошибка! Общие секреты не совпадают.")
    
    # 8. Демонстрация проблемы для злоумышленника
    print("\n" + "=" * 60)
    print("ПРИМЕЧАНИЕ ДЛЯ ЗЛОУМЫШЛЕННИКА (Евы):")
    print("=" * 60)
    print(f"Ева знает: p = {p}, g = {g}, A = {alice_public}, B = {bob_public}")
    print(f"Ей нужно найти a или b из уравнений:")
    print(f"  {alice_public} = {g} ^ a mod {p}")
    print(f"  {bob_public} = {g} ^ b mod {p}")
    print("Это задача дискретного логарифмирования - она вычислительно сложна!")
    print(f"Для p = {p} это легко, но для 2048-битных чисел - практически невозможно.")
    
    return alice_shared, bob_shared


def manual_interaction_example():
    """
    Пример, показывающий пошаговое взаимодействие пользователей
    """
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ (пошаговая симуляция)")
    print("=" * 60)
    
    # Пользователь 1 (вы)
    print("\n[ПОЛЬЗОВАТЕЛЬ 1]")
    p = 23
    g = 5
    dh1 = DiffieHellman(p, g)
    private1 = dh1.generate_private_key()
    public1 = dh1.compute_public_key()
    print(f"Ваш секретный ключ: {private1} (сохраните в тайне!)")
    print(f"Ваш публичный ключ: {public1} (отправьте собеседнику)")
    
    # Пользователь 2 (собеседник)
    print("\n[ПОЛЬЗОВАТЕЛЬ 2]")
    dh2 = DiffieHellman(p, g)
    private2 = dh2.generate_private_key()
    public2 = dh2.compute_public_key()
    print(f"Секретный ключ собеседника: {private2} (сохраните в тайне!)")
    print(f"Публичный ключ собеседника: {public2} (отправьте вам)")
    
    # Обмен
    print("\n[ОБМЕН ПУБЛИЧНЫМИ КЛЮЧАМИ]")
    print("Вы отправляете собеседнику:", public1)
    print("Собеседник отправляет вам:", public2)
    
    # Вычисление общего секрета
    shared1 = dh1.compute_shared_secret(public2)
    shared2 = dh2.compute_shared_secret(public1)
    
    print(f"\n[ОБЩИЙ СЕКРЕТ]")
    print(f"Вы вычислили: {shared1}")
    print(f"Собеседник вычислил: {shared2}")
    
    if shared1 == shared2:
        print(f"✅ Общий секрет: {shared1}")
        key1 = dh1.derive_key()
        key2 = dh2.derive_key()
        print(f"Ключ (SHA-256): {key1.hex()[:40]}...")
    else:
        print("❌ Ошибка!")


if __name__ == "__main__":
    # Запуск основной демонстрации
    demo_diffie_hellman()
    
    # Дополнительный интерактивный пример
    manual_interaction_example()
    
    print("\n" + "=" * 60)
    print("ВЫВОД:")
    print("=" * 60)
    print("""
    Протокол Диффи-Хеллмана решает проблему, описанную в статье:
    Два незнакомца в интернете могут создать общий секретный ключ,
    не имея предварительно обмененной секретной информации.
    
    Это достигается за счет математической задачи дискретного
    логарифмирования, которая:
    - Легка в прямом направлении (возведение в степень)
    - Трудна в обратном (нахождение показателя степени)
    
    Алгоритм стал фундаментом для:
    - SSL/TLS (безопасные сайты)
    - SSH (безопасный доступ к серверам)
    - VPN (защищенные сети)
    - И многих других протоколов
    """)