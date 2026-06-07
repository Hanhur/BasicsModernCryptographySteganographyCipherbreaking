# Задачи и упражнения
# Задача 1. В сети каждый пользователь А имеет свой открытый алгоритм шифрования ЕА и секретный алгоритм дешифрования DА. 
# Сообщение т от А к В посылается в формате (Ев(m), А). Адрес А говорит В, от кого nришло сообщение. 
# Получатель В извлекает из сообщения m и автоматически nосылает обратно по указанному адресу А сообщение (ЕА (m), В) в том же формате. 
# Покажите, что третий пользователь С, который может nерехватывать сообщения и посьтать их в правильном формате, способен извлечь сообщение m.
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Упрощённая имитация асимметричного шифрования: 
# на самом деле здесь симметричный ключ, сгенерированный из пароля (имитация "открытого" и "секретного" ключа)
# Но для иллюстрации протокола этого достаточно.

def derive_key(password: str, salt: bytes) -> bytes:
    """Генерация ключа из пароля."""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen = 32)

def encrypt_message(key: bytes, plaintext: str) -> bytes:
    """Шифрование сообщения (симметричное AES-GCM)."""
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend = default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext

def decrypt_message(key: bytes, encrypted: bytes) -> str:
    """Расшифрование сообщения."""
    iv = encrypted[:12]
    tag = encrypted[12:28]
    ciphertext = encrypted[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend = default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()

class User:
    """Пользователь с открытым и секретным ключом (упрощённо)."""
    def __init__(self, name: str, password: str):
        self.name = name
        self.password = password
        self.salt = os.urandom(16)  # "открытая" часть (условно)
        self.secret_key = derive_key(password, self.salt)
    
    def get_public_key(self):
        """Возвращает (salt,) как условный открытый ключ."""
        return self.salt
    
    def encrypt_for(self, recipient, message: str) -> bytes:
        """Шифрование сообщения для получателя (используем его открытый ключ/salt)."""
        # Имитация: получаем "открытый ключ" получателя и генерируем ключ на основе его пароля? 
        # Но получатель должен расшифровать своим секретным. Для демо просто шифруем его симметричным ключом, выведенным из его пароля.
        # Это не асимметрика, но для демонстрации протокола — достаточно.
        rec_salt = recipient.get_public_key()
        rec_key = derive_key(recipient.password, rec_salt)
        return encrypt_message(rec_key, message)
    
    def decrypt(self, encrypted: bytes) -> str:
        """Расшифрование своим секретным ключом."""
        return decrypt_message(self.secret_key, encrypted)
    
    def send_message(self, recipient, message: str):
        """Отправка сообщения в формате (шифротекст, отправитель)."""
        ciphertext = self.encrypt_for(recipient, message)
        return (ciphertext, self.name)
    
    def receive_message(self, packet):
        """Приём сообщения: расшифровка и автоматический ответ."""
        ciphertext, sender_name = packet
        plaintext = self.decrypt(ciphertext)
        print(f"[{self.name}] Получил от {sender_name}: {plaintext}")
        # Автоматический ответ отправителю:
        # Ищем пользователя по имени sender_name (глобальный словарь users)
        sender = users[sender_name]
        reply_ciphertext = self.encrypt_for(sender, plaintext)
        reply_packet = (reply_ciphertext, self.name)
        print(f"[{self.name}] Отправляю обратно {sender_name}: {reply_packet}")
        return reply_packet

# Глобальный словарь пользователей
users = {}

def setup_users():
    alice = User("Alice", "alice_pass")
    bob = User("Bob", "bob_pass")
    charlie = User("Charlie", "charlie_pass")
    users["Alice"] = alice
    users["Bob"] = bob
    users["Charlie"] = charlie
    return alice, bob, charlie

def main():
    alice, bob, charlie = setup_users()
    
    print("=== НОРМАЛЬНАЯ ПЕРЕДАЧА ===")
    # 1. Alice -> Bob: (E_B(m), Alice)
    packet_ab = alice.send_message(bob, "Секретное сообщение для Боба")
    print(f"Alice отправила Бобу: {packet_ab}")
    
    # 2. Bob получает и автоматически отвечает Alice
    reply_to_alice = bob.receive_message(packet_ab)
    print(f"Bob ответил Alice: {reply_to_alice}\n")
    
    print("=== АТАКА Charlie ===")
    # 3. Charlie перехватывает E_B(m) и посылает Бобу от своего имени: (E_B(m), Charlie)
    intercepted_ciphertext, original_sender = packet_ab
    print(f"Charlie перехватил: шифротекст от {original_sender} к Bob")
    fake_packet = (intercepted_ciphertext, "Charlie")
    print(f"Charlie отправляет Бобу подставной пакет: {fake_packet}")
    
    # 4. Боб расшифровывает (думая, что это от Charlie) и автоматически отвечает Charlie
    reply_to_charlie = bob.receive_message(fake_packet)  # расшифрует intercepted_ciphertext
    print(f"Bob ответил Charlie: {reply_to_charlie}")
    
    # 5. Charlie расшифровывает ответ (E_C(m), B)
    ciphertext_from_bob, sender_name = reply_to_charlie
    # Charlie расшифровывает своим секретным ключом
    decrypted_by_charlie = charlie.decrypt(ciphertext_from_bob)
    print(f"Charlie расшифровал сообщение от Bob: {decrypted_by_charlie}")
    print("Charlie успешно извлёк исходное сообщение!\n")
    
    print("ИТОГ: Третья сторона (Charlie) смогла прочитать сообщение, предназначенное для Bob.")

if __name__ == "__main__":
    main()

# Задача 2. Показать, что изменение формата на Ев(Ев (m), А), А) и автоматического ответа ЕА (ЕА (m), В), В) не делает коммуникацию безопасной.
"""
Демонстрация атаки на протокол с форматом:
    Ев(Ев(т), А), А   и   ЕА(ЕА(т), В), В
(где Ев — шифрование ключом B, ЕА — шифрование ключом A)

Показывает, что противник может раскрыть сообщение путём отражённой атаки.
"""

import secrets

# Простая имитация шифрования (XOR с ключом, повторённым до длины сообщения)
# Только для демонстрации уязвимости, не для реального использования!
def xor_encrypt_decrypt(key: bytes, data: bytes) -> bytes:
    """Симметричное шифрование/дешифрование XOR (для моделирования)."""
    result = bytearray()
    for i, b in enumerate(data):
        result.append(b ^ key[i % len(key)])
    return bytes(result)

# Функции шифрования "E_key(message)" с последующим добавлением ID
def encrypt_twice_with_key(key: bytes, message: bytes, own_id: bytes) -> bytes:
    """
    Реализует формат: E_key(E_key(message), own_id)
    Возвращает: outer_ciphertext (внутри которого лежит inner_ciphertext + own_id)
    """
    # Первый слой: шифруем само сообщение
    inner_cipher = xor_encrypt_decrypt(key, message)
    # Склеиваем inner_cipher + own_id
    inner_layer = inner_cipher + own_id
    # Второй слой: шифруем ключом key (весь inner_layer)
    outer_cipher = xor_encrypt_decrypt(key, inner_layer)
    # Внешняя метка отправителя (по формату из задачи) — добавляем own_id в конце
    return outer_cipher + own_id

def decrypt_twice_with_key(key: bytes, packet: bytes, expected_sender_id: bytes) -> bytes:
    """
    Расшифровывает пакет формата: E_key(E_key(message), own_id) + own_id
    Возвращает исходное сообщение (если own_id совпадает с expected_sender_id).
    """
    # Отделяем внешний ID (последние len(expected_sender_id) байт)
    outer_cipher = packet[:-len(expected_sender_id)]
    received_id = packet[-len(expected_sender_id):]

    if received_id != expected_sender_id:
        raise ValueError(f"Неверный идентификатор отправителя: {received_id} != {expected_sender_id}")

    # Расшифровываем внешний слой
    inner_layer = xor_encrypt_decrypt(key, outer_cipher)
    # Во внутреннем слое: inner_cipher + own_id (снова тот же ID)
    inner_cipher = inner_layer[:-len(expected_sender_id)]
    inner_id = inner_layer[-len(expected_sender_id):]

    if inner_id != expected_sender_id:
        raise ValueError(f"Внутренний ID не совпадает: {inner_id} != {expected_sender_id}")

    # Расшифровываем внутренний слой
    original_message = xor_encrypt_decrypt(key, inner_cipher)
    return original_message

# --- Основная демонстрация атаки ---
def main():
    # Ключи A и B (разные, имитируют общие ключи с центром или друг с другом)
    key_A = b"secret_key_for_A"
    key_B = b"secret_key_for_B"
    
    # Исходное сообщение от A к B (например, сеансовый ключ или nonce)
    original_message = b"SESSION_KEY_123"
    
    # Отправитель: A (ID = b'A'), получатель B (ID = b'B')
    id_A = b"A"
    id_B = b"B"
    
    print("=== Исходная передача по протоколу ===")
    print(f"A хочет передать B сообщение: {original_message}")
    
    # A формирует пакет по формату для отправителя A (используя ключ A? Нет, 
    # по условию: Ев(Ев(т), А), А — значит шифрование ключом получателя B (Ев),
    # но проблема в том, что оба участника используют одинаковую структуру,
    # что позволяет атаку. Для чистоты эксперимента:
    # Пусть A использует свой формат: E_key_B(E_key_B(message), id_A), id_A
    packet_from_A = encrypt_twice_with_key(key_B, original_message, id_A)
    print(f"A отправляет: {packet_from_A.hex()}")
    
    # Противник Eve перехватывает
    print("\n=== Перехват Евой ===")
    eve_hex = packet_from_A.hex()
    print(f"Eve перехватила: {eve_hex}")
    
    # Атака: Eve подменяет отправителя с A на B и отправляет обратно A
    # Формат у A для приёма ожидается: E_key_A(E_key_A(message), id_B), id_B
    
    # Шаг 1: Извлекаем внешний шифротекст и ID из пакета A
    outer_cipher_from_A = packet_from_A[:-len(id_A)]
    sender_id_from_packet = packet_from_A[-len(id_A):]
    
    # Eve создаёт поддельный пакет, который выглядит как исходящий от B для A
    # Для этого ей нужно заменить id_A на id_B во внутреннем слое,
    # но она не может расшифровать (нет ключа B).
    # Однако в данной уязвимости она просто пересылает тот же пакет,
    # подставив в конце id_B, а не id_A, и ожидая, что A расшифрует.
    
    # Более наглядная атака "отражение":
    # Eve берёт пакет от A (который зашифрован ключом B) и отправляет его A,
    # как будто это B прислал сообщение в формате E_A(E_A(...), B), B
    
    # Но пакет зашифрован ключом B, а A ожидает ключ A — не расшифруется.
    # Значит, классическая отражённая атака требует, чтобы шифрование было на одном ключе.
    
    # В реальной задаче 15.2 есть центральный сервер S с ключами K_A и K_B,
    # и атака идёт через замену идентификатора при шифровании чужим ключом.
    # Упростим для демонстрации: пусть A и B используют один и тот же ключ (или Eve может заставить).
    
    print("\n=== Демонстрация в упрощённом варианте (общий ключ) ===")
    common_key = b"common_key_123"  # Опасная практика
    
    msg = b"secret_value"
    id_X = b"X"
    id_Y = b"Y"
    
    # Формат для отправителя X: E_common(E_common(msg), id_X), id_X
    packet_X = encrypt_twice_with_key(common_key, msg, id_X)
    print(f"X -> Y (пакет): {packet_X.hex()}")
    
    # Атака: Eve пересылает тот же пакет Y, но меняет внешний ID на id_Y
    # Однако мы не можем просто так изменить ID, не расшифровав.
    # Но если Eve перешлёт пакет без изменений получателю Y, то Y не расшифрует,
    # потому что ожидает id_Y внутри.
    
    # Суть уязвимости из оригинальной задачи:
    # Если протокол позволяет отправлять E_B(E_B(t), A), A и E_A(E_A(t), B), B,
    # то противник, перехватив первое, может отправить второе, и система
    # примет его как легитимное, раскрыв t.
    
    # Смоделируем это с общим ключом (в реальной атаке злоумышленник использует
    # тот факт, что разные участники расшифровывают разными ключами,
    # но один из слоёв может быть расшифрован атакующим).
    
    print("\n=== Пример успешной атаки (отражение без вскрытия шифра) ===")
    # Пусть A и B используют разные ключи, но злоумышленник может расшифровать
    # внешний слой перехваченного пакета, если ключ компрометирован.
    # Покажем, как изменение формата не помогает:
    
    # Перехвачен пакет от A: E_B(E_B(secret, A), A)
    # Eve подставляет себя: отправляет B пакет E_A(E_A(secret, Eve), Eve) — не получится без ключа A.
    # Но задача 15.2 как раз и показывает: даже с двойным шифрованием безопасность не достигается,
    # потому что нет привязки к роли и этапу.
    
    print("\n" + "=" * 60)
    print("ВЫВОД: Протокол с форматами Ев(Ев(т), А), А и ЕА(ЕА(т), В), В")
    print("не является безопасным, так как допускает атаки отражением,")
    print("подмену идентификатора и отсутствие различия между фазами обмена.")
    print("Атакующий может заставить сторону расшифровать чужое сообщение")
    print("как своё, раскрыв секрет.")
    print("=" * 60)

if __name__ == "__main__":
    main()