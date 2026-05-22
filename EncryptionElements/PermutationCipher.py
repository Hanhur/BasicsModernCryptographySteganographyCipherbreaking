# 4. Шифр перестаковки
def apply_permutation(text_block, perm, mode = 'encrypt'):
    """
    Применяет перестановку к блоку текста.
    
    :param text_block: строка (блок) длины l
    :param perm: перестановка - список новых позиций (индексация с 1), например [2,1,4,3] для шифра из примера "abcd" -> "badc"
    :param mode: 'encrypt' или 'decrypt'
    :return: преобразованный блок
    """
    l = len(perm)
    if len(text_block) != l:
        raise ValueError(f"Длина блока {len(text_block)} не соответствует длине перестановки {l}")
    
    if mode == 'encrypt':
        # Шифрование: output[i] = input[perm[i]-1]
        # perm[i] - новая позиция для символа с позиции i? Нет, нужно определиться.
        # Будем считать perm = [3,1,4,2] означает: символ на позиции 1 идет в позицию 3, 
        # символ на позиции 2 -> в позицию 1, символ 3 -> в позицию 4, символ 4 -> в позицию 2.
        # Это старая_позиция -> новая_позиция.
        # Тогда зашифрованный блок: new[new_pos-1] = old[old_pos-1].
        # Удобнее задать perm как новое расположение старых символов: 
        # perm_as_new_order = [3,1,4,2] означает: на первое место шифроблока ставим символ 
        # из старой позиции 3, на второе - из старой позиции 1, на третье - из позиции 4, 
        # на четвертое - из позиции 2.
        # Пример из исходного текста: "abcd" -> "cadb" при perm=[3,1,4,2].
        # Будем использовать такую интерпретацию: perm задает порядок выборки символов из блока.
        # Это удобнее.
        new_block = ''.join(text_block[p - 1] for p in perm)
        return new_block
    else:  # decrypt
        # Расшифрование: нужно восстановить исходный порядок.
        # Если при шифровании мы брали символы в порядке perm, то при расшифровании
        # нужно поставить символы обратно: создаем обратную перестановку inv_perm,
        # где inv_perm[perm[i]-1] = i+1.
        inv_perm = [0] * l
        for i, p in enumerate(perm):
            inv_perm[p - 1] = i + 1
        new_block = ''.join(text_block[p - 1] for p in inv_perm)
        return new_block


def encrypt(plaintext, perm, block_len = None, pad_char = 'x'):
    """
    Шифрование текста блочной перестановкой.
    
    :param plaintext: исходный текст
    :param perm: перестановка (список) - порядок выборки символов из блока
    :param block_len: длина блока (если не указана, берется len(perm))
    :param pad_char: символ для дополнения последнего блока
    :return: зашифрованный текст
    """
    if block_len is None:
        block_len = len(perm)
    elif block_len != len(perm):
        raise ValueError("block_len должен совпадать с длиной перестановки")
    
    # Разбиваем на блоки
    blocks = [plaintext[i:i+block_len] for i in range(0, len(plaintext), block_len)]
    
    # Дополняем последний блок, если нужно
    if len(blocks[-1]) < block_len:
        blocks[-1] = blocks[-1].ljust(block_len, pad_char)
    
    # Шифруем каждый блок
    encrypted_blocks = [apply_permutation(block, perm, mode = 'encrypt') for block in blocks]
    
    return ''.join(encrypted_blocks)


def decrypt(ciphertext, perm, block_len = None, pad_char = 'x'):
    """
    Расшифрование текста блочной перестановкой.
    
    :param ciphertext: зашифрованный текст
    :param perm: перестановка (та же, что использовалась при шифровании)
    :param block_len: длина блока
    :param pad_char: символ дополнения (для удаления в конце)
    :return: расшифрованный текст (с возможным удалением pad_char в конце)
    """
    if block_len is None:
        block_len = len(perm)
    elif block_len != len(perm):
        raise ValueError("block_len должен совпадать с длиной перестановки")
    
    # Разбиваем на блоки
    blocks = [ciphertext[i:i + block_len] for i in range(0, len(ciphertext), block_len)]
    
    # Расшифровываем каждый блок
    decrypted_blocks = [apply_permutation(block, perm, mode = 'decrypt') for block in blocks]
    
    # Склеиваем
    result = ''.join(decrypted_blocks)
    
    # Удаляем символы дополнения (только если они были добавлены)
    # Простой способ: удалить все pad_char в конце (но если они были в тексте, это проблема)
    # В реальности нужно хранить длину исходного текста, но для примера:
    result = result.rstrip(pad_char)
    
    return result


# ============== Пример использования ==============
if __name__ == "__main__":
    # Перестановка из примера: "abcd" -> "cadb"
    # То есть берем символы в порядке: 3-й, 1-й, 4-й, 2-й
    permutation = [3, 1, 4, 2]
    
    plain = "hello world this is a secret message"
    print(f"Исходный текст: {plain}")
    
    encrypted = encrypt(plain, permutation)
    print(f"Зашифрованный: {encrypted}")
    
    decrypted = decrypt(encrypted, permutation)
    print(f"Расшифрованный: {decrypted}")
    
    # Проверка на русском тексте
    print("\n--- Русский текст ---")
    plain_ru = "привет мир это секретное сообщение"
    print(f"Исходный: {plain_ru}")
    
    encrypted_ru = encrypt(plain_ru, permutation, pad_char = '_')
    print(f"Зашифрованный: {encrypted_ru}")
    
    decrypted_ru = decrypt(encrypted_ru, permutation, pad_char = '_')
    print(f"Расшифрованный: {decrypted_ru}")
    
    # Демонстрация с другим блоком
    print("\n--- Пример abcd -> cadb ---")
    test = "abcd"
    perm_example = [3, 1, 4, 2]
    enc_test = encrypt(test, perm_example)
    print(f"'{test}' -> '{enc_test}' (ожидалось 'cadb')")
    
    # Пример с перестановкой (2,1,4,3) -> badc
    print("\n--- Пример (2,1,4,3) ---")
    perm2 = [2, 1, 4, 3]
    enc2 = encrypt("abcd", perm2)
    print(f"'abcd' -> '{enc2}' (ожидалось 'badc')")
    
    dec2 = decrypt(enc2, perm2)
    print(f"Расшифровка: '{dec2}'")