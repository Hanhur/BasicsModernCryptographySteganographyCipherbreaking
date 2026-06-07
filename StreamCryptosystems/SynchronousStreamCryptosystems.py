# 2. Синхронные поточные криптосистемы
class SynchronousStreamCipher:
    """
    Синхронная поточная криптосистема.
    Соответствует описанию:
    u0 = инициализация по ключу
    u_{i+1} = f(u_i, k)
    k_i = g(u_i, k)
    c_i = h(k_i, m_i)
    """

    def __init__(self, key: int):
        """
        key: секретный ключ (целое число)
        """
        self.key = key
        # u0 — начальное состояние, определяется только по ключу
        self._reset_state()

    def _reset_state(self):
        """Сброс состояния в u0 (зависит только от ключа)"""
        # Для простоты: u0 = key (но можно и сложнее)
        self.u = self.key

    def _f(self, u: int, k: int) -> int:
        """
        Функция перехода состояния f(u, k).
        Здесь: линейный конгруэнтный генератор.
        """
        # Параметры LCG (m = 2**64, a, c)
        a = 1103515245
        c = 12345
        m = 2 ** 64
        return (a * u + c + k) % m

    def _g(self, u: int, k: int) -> int:
        """
        Функция генерации поточного ключа g(u, k).
        Возвращает один байт (0..255) из текущего состояния.
        """
        # Берем младший байт состояния, перемешиваем с ключом
        return (u ^ k) & 0xFF

    def _h(self, ki: int, mi: int) -> int:
        """
        Функция шифрования h(ki, mi).
        mi, ki — целые числа (0..255 для байтов).
        """
        return ki ^ mi

    def _encrypt_bytes(self, data: bytes) -> bytes:
        """
        Шифрование/расшифрование последовательности байт.
        (В синхронных поточных шифрах шифрование и дешифрование
        идентичны из-за XOR)
        """
        result = bytearray()
        for byte in data:
            # Генерируем поточный ключ ki
            ki = self._g(self.u, self.key)
            # Шифруем байт
            cipher_byte = self._h(ki, byte)
            result.append(cipher_byte)
            # Переходим к следующему состоянию
            self.u = self._f(self.u, self.key)
        return bytes(result)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Шифрование текста"""
        self._reset_state()
        return self._encrypt_bytes(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Расшифрование текста (синхронный режим)"""
        self._reset_state()
        return self._encrypt_bytes(ciphertext)  # то же самое, что encrypt

    def decrypt_with_desync(self, ciphertext: bytes, insert_byte: int = None, remove_at: int = None) -> bytes:
        """
        Демонстрация десинхронизации:
        - insert_byte: вставить байт в указанной позиции
        - remove_at: удалить байт в указанной позиции

        Возвращает расшифрованный текст (скорее всего, мусор после точки десинхронизации)
        """
        self._reset_state()

        # Искажаем шифротекст (вставка или удаление)
        modified = list(ciphertext)
        if remove_at is not None and 0 <= remove_at < len(modified):
            modified.pop(remove_at)
            print(f"⚠️ Удалён байт на позиции {remove_at}")
        if insert_byte is not None:
            modified.insert(insert_byte["pos"], insert_byte["value"])
            print(f"⚠️ Вставлен байт {insert_byte['value']:02x} на позиции {insert_byte['pos']}")

        # Расшифровываем искажённый шифротекст
        decrypted = bytearray()
        for i, byte in enumerate(modified):
            ki = self._g(self.u, self.key)
            decrypted.append(self._h(ki, byte))
            self.u = self._f(self.u, self.key)

            # Проверяем возможное обнаружение десинхронизации:
            # (в реальных системах — по контрольной сумме или формату данных)
            if i < len(ciphertext) and (insert_byte is not None or remove_at is not None):
                if i >= (remove_at if remove_at is not None else insert_byte["pos"]):
                    print(f"  Позиция {i}: возможна десинхронизация (начиная с этого места данные некорректны)")
                    break  # для демонстрации показываем только первое место сбоя

        return bytes(decrypted)


# ========== ДЕМОНСТРАЦИЯ ==========
if __name__ == "__main__":
    print("=== СИНХРОННАЯ ПОТОЧНАЯ КРИПТОСИСТЕМА ===\n")

    # 1. Обычная работа
    key = 123456789
    cipher = SynchronousStreamCipher(key)

    plaintext = b"Hello, synchronous stream cipher!"
    print(f"Исходный текст: {plaintext}")

    ciphertext = cipher.encrypt(plaintext)
    print(f"Шифротекст (hex): {ciphertext.hex()}")

    decrypted = cipher.decrypt(ciphertext)
    print(f"Расшифровано:   {decrypted}\n")

    # 2. Искажение символа (ошибка не распространяется)
    print("--- Ошибка в одном символе (не влияет на остальные) ---")
    corrupted = bytearray(ciphertext)
    corrupted[5] ^= 0xFF  # инвертируем биты в одном байте
    cipher2 = SynchronousStreamCipher(key)
    decrypted_corrupted = cipher2.decrypt(bytes(corrupted))
    print(f"Расшифровано с ошибкой в байте 5: {decrypted_corrupted}")
    print("(Только один символ испорчен, остальные верны!)\n")

    # 3. Десинхронизация (вставка/удаление)
    print("--- ДЕСИНХРОНИЗАЦИЯ (активная атака) ---")
    cipher3 = SynchronousStreamCipher(key)

    # Удаление одного байта из шифротекста
    decrypted_desync = cipher3.decrypt_with_desync(ciphertext, remove_at = 10)
    print(f"Расшифровано после удаления байта: {decrypted_desync}\n")

    # Вставка байта
    cipher4 = SynchronousStreamCipher(key)
    decrypted_desync2 = cipher4.decrypt_with_desync(ciphertext, insert_byte = {"pos": 10, "value": 0xAA})
    print(f"Расшифровано после вставки байта: {decrypted_desync2}\n")

    print("=== Вывод: ===")
    print("✓ Нераспространение ошибки: искажение одного символа портит только один символ.")
    print("✓ Вставка/удаление немедленно нарушает синхронизацию -> дальнейшая расшифровка невозможна.")
    print("✓ Это позволяет обнаружить активные атаки (при наличии контрольных механизмов).")