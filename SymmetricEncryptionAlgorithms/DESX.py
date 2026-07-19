# DESX
"""
DESX на Python (упрощенная реализация на базе SDES)
C = K3 XOR E_K1 (K2 XOR M)
"""

# ---------- Таблицы для упрощенного DES (SDES) ----------
# Начальная перестановка IP
IP = [1, 5, 2, 0, 3, 7, 4, 6]
# Обратная перестановка IP^-1
IP_INV = [3, 0, 2, 4, 6, 1, 7, 5]
# Перестановка расширения E/P (для 4-битного входа -> 8 бит)
EP = [3, 0, 1, 2, 1, 2, 3, 0]
# Перестановка S-блоков (4 бита -> 4 бита)
S0 = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2]
]
S1 = [
    [0, 1, 2, 3],
    [2, 0, 1, 3],
    [3, 0, 1, 0],
    [2, 1, 0, 3]
]
# Перестановка P4 (после S-блоков)
P4 = [1, 3, 2, 0]
# Перестановка P8 (для сжатия ключа)
P8 = [5, 2, 6, 3, 7, 4, 9, 8]
# Перестановка P10 (для начального ключа)
P10 = [2, 4, 1, 6, 3, 9, 0, 8, 7, 5]

# ---------- Вспомогательные функции ----------
def permute(bits, table):
    """Применяет перестановку к списку бит"""
    return [bits[i] for i in table]

def left_shift(bits, n = 1):
    """Циклический сдвиг влево"""
    return bits[n:] + bits[:n]

def xor_bits(a, b):
    """XOR двух списков бит"""
    return [x ^ y for x, y in zip(a, b)]

def bits_to_int(bits):
    """Список бит -> целое число"""
    return int(''.join(str(b) for b in bits), 2)

def int_to_bits(val, length):
    """Целое число -> список бит фиксированной длины"""
    return [int(b) for b in format(val, f'0{length}b')]

def sbox_lookup(sbox, bits):
    """Преобразование 4-битного входа через S-блок (возвращает 2 бита)"""
    row = (bits[0] << 1) | bits[3]   # 1-й и 4-й бит -> строка
    col = (bits[1] << 1) | bits[2]   # 2-й и 3-й бит -> столбец
    return int_to_bits(sbox[row][col], 2)

# ---------- Функции SDES ----------
def generate_subkeys(main_key):
    """
    Генерирует два раундовых подключа K1, K2 из 10-битного ключа
    """
    # P10 перестановка
    key = permute(main_key, P10)
    # Разделяем на две половины
    left = key[:5]
    right = key[5:]
    
    # Раунд 1: сдвиг на 1
    left = left_shift(left, 1)
    right = left_shift(right, 1)
    k1 = permute(left + right, P8)
    
    # Раунд 2: сдвиг на 2
    left = left_shift(left, 2)
    right = left_shift(right, 2)
    k2 = permute(left + right, P8)
    
    return k1, k2

def f_function(bits, subkey):
    """
    Функция Фейстеля: расширение, XOR с ключом, S-блоки, P4
    bits - 4 бита, subkey - 8 бит
    """
    # Расширение 4 -> 8
    expanded = permute(bits, EP)
    # XOR с подключом
    xored = xor_bits(expanded, subkey)
    # Разделяем на левую и правую часть для S-блоков
    left = xored[:4]
    right = xored[4:]
    # Проход через S0 и S1
    s0_out = sbox_lookup(S0, left)
    s1_out = sbox_lookup(S1, right)
    # Объединяем и делаем P4
    combined = s0_out + s1_out
    return permute(combined, P4)

def sdes_encrypt_block(block, k1, k2):
    """
    Шифрование одного 8-битного блока SDES
    """
    # Начальная перестановка IP
    block = permute(block, IP)
    left = block[:4]
    right = block[4:]
    
    # Раунд 1
    new_left = right
    new_right = xor_bits(left, f_function(right, k1))
    
    # Раунд 2 (меняем местами половины)
    left = new_left
    right = new_right
    new_left = right
    new_right = xor_bits(left, f_function(right, k2))
    
    # Финальная перестановка IP^-1
    result = permute(new_left + new_right, IP_INV)
    return result

def sdes_decrypt_block(block, k1, k2):
    """
    Расшифрование одного 8-битного блока SDES (подключи в обратном порядке)
    """
    block = permute(block, IP)
    left = block[:4]
    right = block[4:]
    
    # Раунд 1 (с k2)
    new_left = right
    new_right = xor_bits(left, f_function(right, k2))
    
    # Раунд 2 (с k1)
    left = new_left
    right = new_right
    new_left = right
    new_right = xor_bits(left, f_function(right, k1))
    
    result = permute(new_left + new_right, IP_INV)
    return result

# ---------- DESX (обёртка) ----------
def desx_encrypt(plaintext_bits, k1_bits, k2_bits, k3_bits):
    """
    DESX шифрование: C = K3 XOR E_K1( K2 XOR M )
    Все входы - списки бит (plaintext - 8 бит, ключи - 10, 8, 8 бит соответственно)
    """
    # 1. XOR с K2
    xored = xor_bits(plaintext_bits, k2_bits)
    # 2. SDES шифрование с K1
    subkeys = generate_subkeys(k1_bits)
    encrypted = sdes_encrypt_block(xored, subkeys[0], subkeys[1])
    # 3. XOR с K3
    ciphertext = xor_bits(encrypted, k3_bits)
    return ciphertext

def desx_decrypt(ciphertext_bits, k1_bits, k2_bits, k3_bits):
    """
    DESX расшифрование: M = K2 XOR D_K1( K3 XOR C )
    """
    # 1. XOR с K3
    xored = xor_bits(ciphertext_bits, k3_bits)
    # 2. SDES расшифрование с K1
    subkeys = generate_subkeys(k1_bits)
    decrypted = sdes_decrypt_block(xored, subkeys[0], subkeys[1])
    # 3. XOR с K2
    plaintext = xor_bits(decrypted, k2_bits)
    return plaintext

# ---------- Тестирование ----------
if __name__ == "__main__":
    print("=== DESX (упрощенный) ===\n")
    
    # Исходные данные (все в битовых списках)
    # 8-битное сообщение
    M = int_to_bits(0b10110101, 8)   # 0xB5
    # Ключи: K1 - 10 бит, K2 и K3 - 8 бит
    K1 = int_to_bits(0b0111111101, 10)  # 10-битный мастер-ключ
    K2 = int_to_bits(0b11110000, 8)     # 8-битный ключ XOR перед шифром
    K3 = int_to_bits(0b10101010, 8)     # 8-битный ключ XOR после шифра
    
    print(f"Исходное сообщение M:       {''.join(map(str, M))}  (0x{bits_to_int(M):02X})")
    print(f"K1 (мастер-ключ DES):       {''.join(map(str, K1))}  (0x{bits_to_int(K1):03X})")
    print(f"K2 (внешний левый):         {''.join(map(str, K2))}  (0x{bits_to_int(K2):02X})")
    print(f"K3 (внешний правый):        {''.join(map(str, K3))}  (0x{bits_to_int(K3):02X})")
    
    # Шифрование
    C = desx_encrypt(M, K1, K2, K3)
    print(f"\nЗашифрованный текст C:      {''.join(map(str, C))}  (0x{bits_to_int(C):02X})")
    
    # Расшифрование
    M_dec = desx_decrypt(C, K1, K2, K3)
    print(f"Расшифрованный текст M':     {''.join(map(str, M_dec))}  (0x{bits_to_int(M_dec):02X})")
    
    # Проверка
    if M == M_dec:
        print("\n✅ Успех! M == M' (расшифрование корректно)")
    else:
        print("\n❌ Ошибка! M != M'")
    
    # Дополнительно: покажем, что без K2/K3 расшифровать нельзя
    print("\n--- Проверка атаки (неправильный K2) ---")
    K2_wrong = int_to_bits(0b00001111, 8)
    M_bad = desx_decrypt(C, K1, K2_wrong, K3)
    print(f"С неверным K2 получено:      {''.join(map(str, M_bad))}  (0x{bits_to_int(M_bad):02X})")
    print(f"Оригинал M:                  {''.join(map(str, M))}  (0x{bits_to_int(M):02X})")