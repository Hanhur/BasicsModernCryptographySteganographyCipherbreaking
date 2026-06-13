# 2. Распределение ключей
# import hashlib
# import time
# import random
# from typing import Dict, Tuple

# # ---------- Имитация шифрования (небезопасно, но для демонстрации логики) ----------
# def simple_encrypt(key: str, plaintext: str) -> str:
#     """Имитация шифрования: XOR с хешем ключа"""
#     key_hash = hashlib.sha256(key.encode()).digest()
#     plain_bytes = plaintext.encode()
#     encrypted = bytes([plain_bytes[i] ^ key_hash[i % len(key_hash)] for i in range(len(plain_bytes))])
#     return encrypted.hex()

# def simple_decrypt(key: str, ciphertext_hex: str) -> str:
#     """Имитация расшифрования"""
#     key_hash = hashlib.sha256(key.encode()).digest()
#     cipher_bytes = bytes.fromhex(ciphertext_hex)
#     decrypted = bytes([cipher_bytes[i] ^ key_hash[i % len(key_hash)] for i in range(len(cipher_bytes))])
#     return decrypted.decode()

# # ---------- Пользователи и сервер ----------
# class User:
#     def __init__(self, name: str, master_key: str):
#         self.name = name
#         self.master_key = master_key      # Долгосрочный ключ с сервером K_AC
#         self.session_keys = {}             # Для хранения ключей с другими пользователями

# class Server:
#     def __init__(self):
#         self.users = {}   # имя -> мастер-ключ

#     def register_user(self, name: str, master_key: str):
#         self.users[name] = master_key

#     def generate_session_key(self) -> str:
#         """Генерация случайного сеансового ключа"""
#         return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:16]

#     def get_ticket_and_encrypted_session(self, client: str, target: str, nonce: str, lifetime: int) -> Tuple[str, str]:
#         """
#         Шаг (2): сервер C возвращает:
#           - E_K_AC(k, N, L, B)
#           - ticket = E_K_BC(k, A, L)
#         """
#         if client not in self.users or target not in self.users:
#             raise ValueError("Неизвестный пользователь")

#         k = self.generate_session_key()
#         L = lifetime
#         B = target

#         # Часть для клиента A
#         plain_for_A = f"{k},{nonce},{L},{B}"
#         encrypted_for_A = simple_encrypt(self.users[client], plain_for_A)

#         # Билет для B
#         plain_ticket = f"{k},{client},{L}"
#         ticket = simple_encrypt(self.users[target], plain_ticket)

#         return encrypted_for_A, ticket

# # ---------- Протокол ----------
# def kerberos_protocol():
#     print("=== ПРОТОКОЛ KERBEROS (симуляция) ===\n")

#     # 1. Инициализация
#     C = Server()
#     C.register_user("Alice", "MasterKey_Alice")
#     C.register_user("Bob",   "MasterKey_Bob")

#     Alice = User("Alice", "MasterKey_Alice")
#     Bob   = User("Bob",   "MasterKey_Bob")

#     # (1) A -> C: A, B, N
#     N = str(random.randint(1000, 9999))
#     print(f"(1) Alice -> Server: Я Alice, хочу говорить с Bob, nonce = {N}")

#     # (2) A <- C
#     encrypted_for_A, ticket = C.get_ticket_and_encrypted_session("Alice", "Bob", N, lifetime = 300)
#     print(f"(2) Server -> Alice: E_KA{{{encrypted_for_A[:20]}...}} и ticket (для Bob)")

#     # Алиса расшифровывает свой блок
#     decrypted = simple_decrypt(Alice.master_key, encrypted_for_A)
#     k, received_nonce, L, B = decrypted.split(',')
#     L = int(L)
#     if received_nonce != N:
#         print("Ошибка: nonce не совпадает!")
#         return
#     if B != "Bob":
#         print("Ошибка: неверный получатель в ответе сервера!")
#         return

#     print(f"  -> Alice расшифровала: ключ k = {k}, nonce = {received_nonce}, L = {L}, B = {B}")
#     Alice.session_keys["Bob"] = k

#     # (3) A -> B: ticket + authenticator
#     TA = int(time.time())
#     A_star = "ExtraKey_A"
#     authenticator_plain = f"Alice, {TA}, {A_star}"
#     authenticator = simple_encrypt(k, authenticator_plain)

#     print(f"(3) Alice -> Bob: ticket и authenticator (время = {TA})")

#     # Боб получает и расшифровывает
#     # Боб расшифровывает билет своим мастер-ключом
#     ticket_decrypted = simple_decrypt(Bob.master_key, ticket)
#     k_B, A_from_ticket, L_B = ticket_decrypted.split(',')
#     L_B = int(L_B)

#     if A_from_ticket != "Alice":
#         print("Ошибка: в билете неверный отправитель!")
#         return

#     Bob.session_keys["Alice"] = k_B  # Сохраняем ключ для Алисы

#     # Боб расшифровывает аутентификатор
#     auth_decrypted = simple_decrypt(k_B, authenticator)
#     A_auth, TA_auth, A_star_received = auth_decrypted.split(',')

#     TA_auth = int(TA_auth)
#     current_time = int(time.time())
#     if current_time - TA_auth > 60:   # Проверка времени жизни аутентификатора
#         print("Ошибка: аутентификатор устарел!")
#         return
#     if A_auth != "Alice":
#         print("Ошибка: отправитель не совпадает!")
#         return

#     print(f"  -> Боб проверил: ключ k = {k_B}, время = {TA_auth} OK, отправитель Alice")

#     # (4) A <- B: E_k(TA, B*)
#     B_star = "ExtraKey_B"
#     response_plain = f"{TA_auth}, {B_star}"
#     response = simple_encrypt(k_B, response_plain)

#     print(f"(4) Bob -> Alice: E_k({TA_auth}, {B_star})")

#     # Алиса расшифровывает ответ Боба
#     response_decrypted = simple_decrypt(k, response)
#     TA_response, B_star_rec = response_decrypted.split(',')
#     if int(TA_response) != TA:
#         print("Ошибка: несовпадение временной метки в ответе Боба!")
#         return

#     print(f"  -> Алиса проверила ответ: ТА = {TA_response} совпадает, B *= {B_star_rec}")

#     print("\n=== Протокол успешно завершён! ===")
#     print(f"Сеансовый ключ k = {k}")
#     print("Алиса и Боб могут безопасно общаться, используя этот ключ.")

# if __name__ == "__main__":
#     kerberos_protocol()

import hashlib
import time
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# ---------- AES шифрование ----------
def aes_encrypt(key: str, plaintext: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()  # 32 байта для AES-256
    cipher = AES.new(key_bytes, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return f"{iv}:{ct}"

def aes_decrypt(key: str, ciphertext: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()
    iv_b64, ct_b64 = ciphertext.split(':')
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv = iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

# ---------- Пользователи и сервер (те же, но с реальным шифрованием) ----------
class User:
    def __init__(self, name: str, master_key: str):
        self.name = name
        self.master_key = master_key
        self.session_keys = {}

class Server:
    def __init__(self):
        self.users = {}

    def register_user(self, name: str, master_key: str):
        self.users[name] = master_key

    def generate_session_key(self) -> str:
        return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:32]  # 32 байта

    def get_ticket_and_encrypted_session(self, client: str, target: str, nonce: str, lifetime: int):
        if client not in self.users or target not in self.users:
            raise ValueError("Неизвестный пользователь")
        k = self.generate_session_key()
        L = lifetime
        B = target

        plain_for_A = f"{k}, {nonce}, {L}, {B}"
        encrypted_for_A = aes_encrypt(self.users[client], plain_for_A)

        plain_ticket = f"{k},{client},{L}"
        ticket = aes_encrypt(self.users[target], plain_ticket)

        return encrypted_for_A, ticket

def kerberos_protocol_aes():
    print("=== ПРОТОКОЛ KERBEROS (AES) ===\n")
    C = Server()
    C.register_user("Alice", "MasterKey_Alice_LongEnough")
    C.register_user("Bob",   "MasterKey_Bob_LongEnough")

    Alice = User("Alice", "MasterKey_Alice_LongEnough")
    Bob   = User("Bob",   "MasterKey_Bob_LongEnough")

    N = str(random.randint(1000, 9999))
    print(f"(1) Alice -> Server: Alice, Bob, nonce = {N}")

    enc_for_A, ticket = C.get_ticket_and_encrypted_session("Alice", "Bob", N, lifetime = 300)
    print("(2) Server -> Alice: зашифрованный блок + ticket")

    decrypted = aes_decrypt(Alice.master_key, enc_for_A)
    k, rec_nonce, L, B = decrypted.split(',')
    if rec_nonce != N or B != "Bob":
        print("Ошибка проверки ответа сервера")
        return
    Alice.session_keys["Bob"] = k

    TA = int(time.time())
    A_star = "A_extra_key"
    authenticator = aes_encrypt(k, f"Alice, {TA}, {A_star}")
    print(f"(3) Alice -> Bob: ticket и authenticator (time = {TA})")

    # Bob side
    ticket_dec = aes_decrypt(Bob.master_key, ticket)
    k_B, A_ticket, L_B = ticket_dec.split(',')
    if A_ticket != "Alice":
        print("Ошибка: неверный отправитель в билете")
        return
    Bob.session_keys["Alice"] = k_B

    auth_dec = aes_decrypt(k_B, authenticator)
    A_auth, TA_auth, A_star_rec = auth_dec.split(',')
    TA_auth = int(TA_auth)
    if abs(int(time.time()) - TA_auth) > 60:
        print("Ошибка: аутентификатор устарел")
        return
    if A_auth != "Alice":
        print("Ошибка: отправитель не совпадает")
        return

    B_star = "B_extra_key"
    response = aes_encrypt(k_B, f"{TA_auth}, {B_star}")
    print(f"(4) Bob -> Alice: E_k({TA_auth}, {B_star})")

    resp_dec = aes_decrypt(k, response)
    TA_resp, B_star_rec = resp_dec.split(',')
    if int(TA_resp) != TA:
        print("Ошибка: несовпадение времени")
        return

    print("\n=== Успех! ===")
    print(f"Сеансовый ключ: {k}")

if __name__ == "__main__":
    kerberos_protocol_aes()