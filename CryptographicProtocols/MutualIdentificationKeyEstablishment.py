# Взаимная идентификация с установлением ключа
"""
Протокол Нидхэма-Шрёдера для взаимной идентификации и установления ключа
Реализация на основе шифра Эль-Гамаля
Пример из книги: p = 107, g = 2
"""

import random
import math


class ElGamalCipher:
    """Реализация шифра Эль-Гамаля"""
    
    def __init__(self, p, g, private_key, public_key):
        """
        Инициализация криптосистемы
        
        Args:
            p: простое число (модуль)
            g: первообразный корень по модулю p
            private_key: секретный ключ (c)
            public_key: открытый ключ (d = g ^ c mod p)
        """
        self.p = p
        self.g = g
        self.private_key = private_key
        self.public_key = public_key
    
    def encrypt(self, message, recipient_public_key):
        """
        Шифрование сообщения для получателя
        
        Args:
            message: целое число для шифрования
            recipient_public_key: открытый ключ получателя
            
        Returns:
            tuple: (r, e) - шифротекст
        """
        # Выбираем случайное k (1 < k < p-1)
        k = random.randint(2, self.p - 2)
        
        # r = g^k mod p
        r = pow(self.g, k, self.p)
        
        # e = m * (d_recipient)^k mod p
        e = (message * pow(recipient_public_key, k, self.p)) % self.p
        
        return (r, e)
    
    def decrypt(self, ciphertext):
        """
        Расшифрование сообщения
        
        Args:
            ciphertext: кортеж (r, e)
            
        Returns:
            int: расшифрованное сообщение
        """
        r, e = ciphertext
        
        # m = e * r^(p-1-c) mod p, где c - секретный ключ
        r_inv = pow(r, self.p - 1 - self.private_key, self.p)
        message = (e * r_inv) % self.p
        
        return message
    
    @staticmethod
    def generate_keys(p, g):
        """
        Генерация пары ключей для пользователя
        
        Args:
            p: простое число
            g: первообразный корень
            
        Returns:
            tuple: (private_key, public_key)
        """
        # Секретный ключ c (1 < c < p-1)
        private_key = random.randint(2, p - 2)
        
        # Открытый ключ d = g^c mod p
        public_key = pow(g, private_key, p)
        
        return private_key, public_key


class User:
    """Класс, представляющий пользователя в сети"""
    
    def __init__(self, name, cipher, identifier):
        """
        Инициализация пользователя
        
        Args:
            name: имя пользователя (A или B)
            cipher: объект ElGamalCipher
            identifier: числовой идентификатор (A_hat или B_hat)
        """
        self.name = name
        self.cipher = cipher
        self.identifier = identifier
        self.public_key = cipher.public_key
        self.private_key = cipher.private_key
        
        # Для хранения сессионных ключей
        self.k1 = None
        self.k2 = None
        self.session_key = None
        
        # Для логирования
        self.log = []
    
    def log_message(self, direction, data):
        """Логирование сообщений"""
        self.log.append(f"{direction}: {data}")
    
    def get_public_key(self):
        """Возвращает открытый ключ пользователя"""
        return self.public_key
    
    def get_identifier(self):
        """Возвращает идентификатор пользователя"""
        return self.identifier


class Alice(User):
    """Класс Алисы - инициатор протокола"""
    
    def __init__(self, cipher, identifier = 1):
        super().__init__("A", cipher, identifier)
        self.participants = {}
    
    def register_participant(self, name, public_key, identifier):
        """Регистрация информации о других пользователях"""
        self.participants[name] = {
            'public_key': public_key,
            'identifier': identifier
        }
    
    def step1_send_to_bob(self, bob):
        """
        Шаг 1: Алиса генерирует k1 и отправляет Бобу
        """
        # Генерируем случайное k1
        self.k1 = random.randint(1, self.cipher.p - 2)
        print(f"\n[A] Генерирует k1 = {self.k1}")
        
        # Формируем сообщение: k1 || A_hat
        # В примере: k1=3, A_hat=1 => message = 31
        message = self.k1 * 10 + self.identifier
        print(f"[A] Сообщение: {self.k1} || {self.identifier} = {message}")
        
        # Шифруем на открытом ключе Боба
        ciphertext = self.cipher.encrypt(message, bob.public_key)
        print(f"[A] Отправляет Бобу: P_B({message}) = {ciphertext}")
        
        self.log_message("A -> B", f"PB({message}) = {ciphertext}")
        
        return ciphertext
    
    def step3_receive_and_verify(self, ciphertext, bob):
        """
        Шаг 3: Алиса расшифровывает ответ Боба и проверяет k1
        """
        print(f"\n[A] Получено от Боба: {ciphertext}")
        
        # Расшифровываем
        message = self.cipher.decrypt(ciphertext)
        print(f"[A] Расшифровано: {message}")
        
        # Извлекаем k1 и k2 из сообщения
        # В примере: message = 37 => k1=3, k2=7
        received_k1 = message // 10
        self.k2 = message % 10
        print(f"[A] Извлечено: k1 = {received_k1}, k2 = {self.k2}")
        
        # Проверяем k1
        if received_k1 == self.k1:
            print(f"[A] ✓ k1={self.k1} подтвержден! Боб идентифицирован.")
            
            # Отправляем k2 обратно Бобу
            message_k2 = self.k2
            ciphertext_k2 = self.cipher.encrypt(message_k2, bob.public_key)
            print(f"[A] Отправляет Бобу: P_B({message_k2}) = {ciphertext_k2}")
            
            self.log_message("A -> B", f"PB({message_k2}) = {ciphertext_k2}")
            
            # Формируем сессионный ключ
            self.session_key = self.k1 ^ self.k2
            print(f"[A] Сессионный ключ: {self.k1} XOR {self.k2} = {self.session_key}")
            
            return ciphertext_k2
        else:
            print(f"[A] ✗ ОШИБКА: k1 = {received_k1} не совпадает с {self.k1}!")
            return None


class Bob(User):
    """Класс Боба - ответчик"""
    
    def __init__(self, cipher, identifier = 2):
        super().__init__("B", cipher, identifier)
        self.participants = {}
    
    def register_participant(self, name, public_key, identifier):
        """Регистрация информации о других пользователях"""
        self.participants[name] = {
            'public_key': public_key,
            'identifier': identifier
        }
    
    def step2_receive_and_respond(self, ciphertext, alice):
        """
        Шаг 2: Боб расшифровывает сообщение Алисы и отвечает
        """
        print(f"\n[B] Получено от Алисы: {ciphertext}")
        
        # Расшифровываем
        message = self.cipher.decrypt(ciphertext)
        print(f"[B] Расшифровано: {message}")
        
        # Извлекаем k1 и идентификатор
        self.k1 = message // 10
        received_id = message % 10
        print(f"[B] Извлечено: k1={self.k1}, ID={received_id}")
        
        # Проверяем идентификатор Алисы
        if received_id == alice.identifier:
            print(f"[B] ✓ Идентификатор Алисы {alice.identifier} подтвержден!")
            
            # Генерируем k2
            self.k2 = random.randint(1, self.cipher.p - 2)
            print(f"[B] Генерирует k2 = {self.k2}")
            
            # Формируем сообщение: k1 || k2
            message_response = self.k1 * 10 + self.k2
            print(f"[B] Сообщение: {self.k1} || {self.k2} = {message_response}")
            
            # Шифруем на открытом ключе Алисы
            ciphertext_response = self.cipher.encrypt(message_response, alice.public_key)
            print(f"[B] Отправляет Алисе: P_A({message_response}) = {ciphertext_response}")
            
            self.log_message("B -> A", f"PA({message_response}) = {ciphertext_response}")
            
            return ciphertext_response
        else:
            print(f"[B] ✗ ОШИБКА: ID = {received_id} не совпадает с {alice.identifier}!")
            return None
    
    def step4_receive_and_verify(self, ciphertext):
        """
        Шаг 4: Боб получает подтверждение и проверяет k2
        """
        print(f"\n[B] Получено от Алисы: {ciphertext}")
        
        # Расшифровываем
        received_k2 = self.cipher.decrypt(ciphertext)
        print(f"[B] Расшифровано: {received_k2}")
        
        # Проверяем k2
        if received_k2 == self.k2:
            print(f"[B] ✓ k2 = {self.k2} подтвержден! Алиса идентифицирована.")
            
            # Формируем сессионный ключ
            self.session_key = self.k1 ^ self.k2
            print(f"[B] Сессионный ключ: {self.k1} XOR {self.k2} = {self.session_key}")
            
            return True
        else:
            print(f"[B] ✗ ОШИБКА: k2 = {received_k2} не совпадает с {self.k2}!")
            return False


class Eve:
    """Класс Евы - пассивный наблюдатель (перехватчик)"""
    
    def __init__(self):
        self.intercepted_messages = []
    
    def intercept(self, sender, receiver, ciphertext):
        """Перехват сообщения"""
        print(f"\n[Eve] Перехвачено сообщение от {sender} к {receiver}: {ciphertext}")
        self.intercepted_messages.append({
            'from': sender,
            'to': receiver,
            'ciphertext': ciphertext
        })
        return ciphertext
    
    def analyze(self):
        """Анализ перехваченных сообщений"""
        print("\n[Eve] Анализ перехваченных сообщений:")
        for i, msg in enumerate(self.intercepted_messages, 1):
            print(f"  {i}. От: {msg['from']} -> Кому: {msg['to']}")
            print(f"     Шифротекст: {msg['ciphertext']}")
            print(f"     (Расшифровать невозможно без секретных ключей)")


def print_separator():
    """Печать разделителя для наглядного вывода"""
    print("\n" + "=" * 60)


def main():
    """Основная функция - демонстрация работы протокола"""
    
    print("=" * 60)
    print("ПРОТОКОЛ НИДХЭМА-ШРЁДЕРА")
    print("Взаимная идентификация и установление ключа")
    print("На основе шифра Эль-Гамаля")
    print("=" * 60)
    
    # Параметры системы (из примера в книге)
    p = 107
    g = 2
    
    print(f"\nПараметры системы:")
    print(f"  p = {p} (простое число)")
    print(f"  g = {g} (первообразный корень)")
    
    # Генерируем ключи для пользователей (используем фиксированные из примера)
    print(f"\nГенерация ключей:")
    
    # Ключи из примера: cA=33, dA=58; cB=45, dB=28
    alice_private = 33
    alice_public = 58
    bob_private = 45
    bob_public = 28
    
    print(f"  Алиса: cA = {alice_private}, dA = {alice_public}")
    print(f"  Боб:   cB = {bob_private}, dB = {bob_public}")
    
    # Создаем объекты шифров
    alice_cipher = ElGamalCipher(p, g, alice_private, alice_public)
    bob_cipher = ElGamalCipher(p, g, bob_private, bob_public)
    
    # Создаем пользователей
    alice = Alice(alice_cipher, identifier = 1)
    bob = Bob(bob_cipher, identifier = 2)
    
    # Регистрируем информацию друг о друге
    alice.register_participant("B", bob.public_key, bob.identifier)
    bob.register_participant("A", alice.public_key, alice.identifier)
    
    # Создаем Еву (пассивный наблюдатель)
    eve = Eve()
    
    print_separator()
    print("НАЧАЛО ПРОТОКОЛА")
    print_separator()
    
    # Шаг 1: Алиса -> Боб
    msg1 = alice.step1_send_to_bob(bob)
    eve.intercept("A", "B", msg1)
    
    # Шаг 2: Боб -> Алиса (обработка и ответ)
    msg2 = bob.step2_receive_and_respond(msg1, alice)
    if msg2 is None:
        print("\n[!] Протокол прерван на шаге 2!")
        return
    eve.intercept("B", "A", msg2)
    
    # Шаг 3: Алиса -> Боб (проверка и подтверждение)
    msg3 = alice.step3_receive_and_verify(msg2, bob)
    if msg3 is None:
        print("\n[!] Протокол прерван на шаге 3!")
        return
    eve.intercept("A", "B", msg3)
    
    # Шаг 4: Боб -> проверка
    success = bob.step4_receive_and_verify(msg3)
    
    print_separator()
    print("РЕЗУЛЬТАТЫ")
    print_separator()
    
    if success:
        print("\n✓ ПРОТОКОЛ УСПЕШНО ЗАВЕРШЕН!")
        print(f"\nОбщий сессионный ключ:")
        print(f"  Алиса: {alice.session_key}")
        print(f"  Боб:   {bob.session_key}")
        print(f"  Совпадают: {alice.session_key == bob.session_key}")
        
        print(f"\nИтоговый ключ (k = k1 ⊕ k2):")
        print(f"  k1 = {alice.k1}, k2 = {alice.k2}")
        print(f"  k = {alice.k1} ⊕ {alice.k2} = {alice.session_key}")
        print(f"  В двоичной записи: {bin(alice.k1)} ⊕ {bin(alice.k2)} = {bin(alice.session_key)}")
        
        print(f"\nПроверка идентификации:")
        print(f"  Алиса идентифицировала Боба: ✓")
        print(f"  Боб идентифицировал Алису: ✓")
    else:
        print("\n✗ ПРОТОКОЛ НЕ УДАЛСЯ!")
    
    print_separator()
    print("ПЕРЕХВАТ ЕВЫ")
    print_separator()
    eve.analyze()
    
    print("\n" + "=" * 60)
    print("ЗАВЕРШЕНИЕ ПРОГРАММЫ")
    print("=" * 60)


if __name__ == "__main__":
    # Для воспроизводимости результатов используем фиксированный seed
    random.seed(42)
    main()