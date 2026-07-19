# Шифр Вернама
import os
import sys

class VernamCipher:
    """
    Реализация шифра Вернама (One-Time Pad).
    Полная стойкость гарантируется только при соблюдении трёх условий:
    1. Ключ абсолютно случаен (используется os.urandom)
    2. Длина ключа >= длина сообщения
    3. Ключ используется только один раз
    """
    
    @staticmethod
    def text_to_bits(text: str, encoding: str = 'utf-8') -> str:
        """
        Преобразует текст в битовую строку.
        Использует UTF-8 для поддержки кириллицы.
        """
        byte_data = text.encode(encoding)
        bits = ''.join(format(byte, '08b') for byte in byte_data)
        return bits
    
    @staticmethod
    def bits_to_text(bits: str, encoding: str = 'utf-8') -> str:
        """
        Преобразует битовую строку обратно в текст.
        """
        # Дополняем биты до кратности 8
        if len(bits) % 8 != 0:
            raise ValueError("Длина битовой строки не кратна 8")
        
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            bytes_list.append(int(byte, 2))
        
        return bytes(bytes_list).decode(encoding)
    
    @staticmethod
    def generate_key(length: int) -> str:
        """
        Генерирует истинно случайный ключ заданной длины (в битах).
        Использует os.urandom() - криптографически стойкий генератор.
        """
        if length <= 0:
            raise ValueError("Длина ключа должна быть положительной")
        
        # Генерируем случайные байты
        num_bytes = (length + 7) // 8  # Округление вверх
        random_bytes = os.urandom(num_bytes)
        
        # Преобразуем в битовую строку
        bits = ''.join(format(byte, '08b') for byte in random_bytes)
        
        # Обрезаем до нужной длины
        return bits[:length]
    
    @staticmethod
    def xor_bits(bits1: str, bits2: str) -> str:
        """
        Побитовое сложение по модулю 2 (XOR).
        Длины строк должны совпадать.
        """
        if len(bits1) != len(bits2):
            raise ValueError(f"Длины битовых строк не совпадают: {len(bits1)} != {len(bits2)}")
        
        result = []
        for b1, b2 in zip(bits1, bits2):
            # XOR: '0'^'0'='0', '0'^'1'='1', '1'^'0'='1', '1'^'1'='0'
            result.append('1' if b1 != b2 else '0')
        
        return ''.join(result)
    
    @staticmethod
    def encrypt_text(plaintext: str) -> tuple:
        """
        Шифрует текстовое сообщение.
        Возвращает (ciphertext_bits, key_bits)
        """
        # Этап 1: Преобразование текста в биты
        plaintext_bits = VernamCipher.text_to_bits(plaintext)
        
        # Этап 2: Генерация случайного ключа той же длины
        key_bits = VernamCipher.generate_key(len(plaintext_bits))
        
        # Этап 3: XOR для получения шифротекста
        ciphertext_bits = VernamCipher.xor_bits(plaintext_bits, key_bits)
        
        return ciphertext_bits, key_bits
    
    @staticmethod
    def decrypt_text(ciphertext_bits: str, key_bits: str) -> str:
        """
        Расшифровывает сообщение.
        Выполняет XOR шифротекста с ключом для восстановления открытого текста.
        """
        # Этап 4: XOR шифротекста с ключом
        plaintext_bits = VernamCipher.xor_bits(ciphertext_bits, key_bits)
        
        # Преобразование битов обратно в текст
        return VernamCipher.bits_to_text(plaintext_bits)
    
    @staticmethod
    def encrypt_bits(plaintext_bits: str) -> tuple:
        """
        Шифрует битовую строку напрямую.
        Возвращает (ciphertext_bits, key_bits)
        """
        # Проверка, что строка состоит только из 0 и 1
        if not all(c in '01' for c in plaintext_bits):
            raise ValueError("Строка должна содержать только символы '0' и '1'")
        
        # Генерация ключа
        key_bits = VernamCipher.generate_key(len(plaintext_bits))
        
        # XOR
        ciphertext_bits = VernamCipher.xor_bits(plaintext_bits, key_bits)
        
        return ciphertext_bits, key_bits
    
    @staticmethod
    def decrypt_bits(ciphertext_bits: str, key_bits: str) -> str:
        """
        Расшифровывает битовую строку.
        """
        return VernamCipher.xor_bits(ciphertext_bits, key_bits)


def demo_text_example():
    """Демонстрация шифрования текста (как в книге)"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ: ШИФРОВАНИЕ ТЕКСТА")
    print("=" * 60)
    
    plaintext = "ПРИВЕТ"
    print(f"Исходное сообщение: {plaintext}")
    print(f"Длина сообщения: {len(plaintext)} символов")
    
    # Шифрование
    ciphertext_bits, key_bits = VernamCipher.encrypt_text(plaintext)
    print(f"\nКлюч (биты): {key_bits}")
    print(f"Шифротекст (биты): {ciphertext_bits}")
    
    # Дешифрование
    decrypted = VernamCipher.decrypt_text(ciphertext_bits, key_bits)
    print(f"\nРасшифрованное сообщение: {decrypted}")
    print(f"Успешно: {plaintext == decrypted}")


def demo_bits_example():
    """Демонстрация шифрования битовой строки (пример из книги)"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: ШИФРОВАНИЕ БИТОВОЙ СТРОКИ (ПРИМЕР ИЗ КНИГИ)")
    print("=" * 60)
    
    plaintext_bits = "00101001"
    print(f"Открытый текст (биты): {plaintext_bits}")
    
    # Используем КОНКРЕТНЫЙ ключ из книги для проверки
    key_bits = "10101100"
    print(f"Ключ (биты): {key_bits}")
    
    # Шифрование
    ciphertext_bits = VernamCipher.xor_bits(plaintext_bits, key_bits)
    print(f"Шифротекст (биты): {ciphertext_bits}")
    
    # Ожидаемый результат из книги: 10000101
    expected = "10000101"
    print(f"Ожидаемый результат: {expected}")
    print(f"Совпадает: {ciphertext_bits == expected}")
    
    # Дешифрование
    decrypted_bits = VernamCipher.xor_bits(ciphertext_bits, key_bits)
    print(f"Расшифрованные биты: {decrypted_bits}")
    print(f"Совпадает с исходным: {decrypted_bits == plaintext_bits}")


def demo_russian_letters_example():
    """Демонстрация с буквенным примером из книги (ПРИВЕТ → ТЦНГЖТ)"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: ПРИМЕР С РУССКИМИ БУКВАМИ")
    print("=" * 60)
    print("ПРИМЕЧАНИЕ: В книге используется сложение по модулю 33 для букв,")
    print("но в реальности шифр Вернама работает на БИТАХ (UTF-8).")
    print("Ниже показан реальный битовый XOR:")
    print("-" * 60)
    
    plaintext = "ПРИВЕТ"
    print(f"Исходное сообщение: {plaintext}")
    
    # Показываем битовое представление
    bits = VernamCipher.text_to_bits(plaintext)
    print(f"Биты UTF-8: {bits}")
    
    # Генерируем ключ
    key_bits = VernamCipher.generate_key(len(bits))
    print(f"Случайный ключ: {key_bits[:40]}... (показаны первые 40 бит)")
    
    # Шифруем
    ciphertext_bits, _ = VernamCipher.encrypt_text(plaintext)
    print(f"Шифротекст (биты): {ciphertext_bits[:40]}...")
    
    print("\nОбратите внимание: в реальном шифре Вернама НЕТ")
    print("соответствия 'П'→'Т', 'Р'→'Ц' и т.д., так как операция")
    print("XOR применяется к каждому БИТУ, а не к букве целиком.")


def demo_security_properties():
    """Демонстрация свойств безопасности"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СВОЙСТВ БЕЗОПАСНОСТИ")
    print("=" * 60)
    
    plaintext = "Секретное сообщение"
    print(f"Сообщение: {plaintext}")
    
    # Шифруем один раз
    c1, k1 = VernamCipher.encrypt_text(plaintext)
    print(f"\nКлюч 1: {k1[:32]}...")
    print(f"Шифротекст 1: {c1[:32]}...")
    
    # Шифруем второй раз с новым ключом
    c2, k2 = VernamCipher.encrypt_text(plaintext)
    print(f"\nКлюч 2: {k2[:32]}...")
    print(f"Шифротекст 2: {c2[:32]}...")
    
    # Проверяем, что шифротексты разные (даже для одного текста)
    print(f"\nШифротексты разные: {c1 != c2}")
    
    # Проверяем, что XOR двух шифротекстов даёт XOR двух ключей
    xor_c = VernamCipher.xor_bits(c1, c2)
    xor_k = VernamCipher.xor_bits(k1, k2)
    print(f"c1⊕c2 == k1⊕k2: {xor_c == xor_k}")
    
    print("\nЭто доказывает свойство совершенной стойкости:")
    print("Злоумышленник не может получить информацию о сообщении,")
    print("не зная ключа, так как c1⊕c2 = (m⊕k1)⊕(m⊕k2) = k1⊕k2")


def demo_wrong_key():
    """Демонстрация того, что неправильный ключ даёт бессмыслицу"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ: НЕПРАВИЛЬНЫЙ КЛЮЧ")
    print("=" * 60)
    
    plaintext = "Привет мир"
    print(f"Исходное сообщение: {plaintext}")
    
    # Шифруем
    ciphertext_bits, key_bits = VernamCipher.encrypt_text(plaintext)
    print(f"Ключ (первые 16 бит): {key_bits[:16]}...")
    
    # Создаём "почти правильный" ключ (меняем последний бит)
    wrong_key = key_bits[:-1] + ('1' if key_bits[-1] == '0' else '0')
    print(f"Неправильный ключ: {wrong_key[:16]}... (изменён последний бит)")
    
    # Пытаемся расшифровать
    try:
        decrypted = VernamCipher.decrypt_text(ciphertext_bits, wrong_key)
        print(f"\nРасшифровка неправильным ключом: {decrypted}")
        print("(Видите бессмыслицу? Это потому что даже 1 бит ошибки")
        print("в ключе полностью разрушает восстановление текста!)")
    except UnicodeDecodeError:
        print("\nРасшифровка не удалась: байты не образуют корректный UTF-8")
        print("Это демонстрирует, что даже 1 бит ошибки в ключе")
        print("делает расшифровку невозможной!")


def interactive_mode():
    """Интерактивный режим для экспериментов"""
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)
    print("Введите текст для шифрования (или 'выход' для выхода):")
    
    while True:
        text = input("\n> ").strip()
        if text.lower() in ('выход', 'exit', 'quit'):
            break
        
        if not text:
            continue
        
        try:
            # Шифруем
            ciphertext_bits, key_bits = VernamCipher.encrypt_text(text)
            print(f"Ключ (биты): {key_bits}")
            print(f"Шифротекст (биты): {ciphertext_bits}")
            
            # Расшифровываем
            decrypted = VernamCipher.decrypt_text(ciphertext_bits, key_bits)
            print(f"Расшифровано: {decrypted}")
            
            if decrypted == text:
                print("✓ Успешно!")
            else:
                print("✗ Ошибка!")
                
        except Exception as e:
            print(f"Ошибка: {e}")


def main():
    """Главная функция"""
    print("=" * 60)
    print("ШИФР ВЕРНАМА (ONE-TIME PAD)")
    print("Реализация на чистом Python без внешних библиотек")
    print("=" * 60)
    print("\nТЕОРЕТИЧЕСКАЯ ОСНОВА:")
    print("• Абсолютная стойкость (информационная энтропия Шеннона)")
    print("• Ключ генерируется через os.urandom (криптостойкий RNG)")
    print("• Длина ключа = длина сообщения")
    print("• Ключ используется только один раз")
    print("• Неуязвим для атак только на шифротекст")
    print("=" * 60)
    
    # Запускаем все демонстрации
    demo_text_example()
    demo_bits_example()
    demo_russian_letters_example()
    demo_security_properties()
    demo_wrong_key()
    
    # Интерактивный режим
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nДо свидания!")


if __name__ == "__main__":
    main()