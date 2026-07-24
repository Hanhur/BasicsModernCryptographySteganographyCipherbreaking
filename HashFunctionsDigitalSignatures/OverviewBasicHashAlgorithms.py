# Обзор основных хеш-алгоритмов
import struct
import time
import binascii
import hashlib
import zlib
import sys

# ================================================
# РЕАЛИЗАЦИЯ SHA-256 С НУЛЯ (БЕЗ NUMPY)
# ================================================

class SHA256:
    """Реализация SHA-256 на чистом Python согласно FIPS 180-4"""
    
    # Инициальные хеш-значения (первые 32 бита дробных частей корней из простых чисел)
    _H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # Константы раундов (первые 32 бита дробных частей кубических корней простых чисел)
    _K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    @staticmethod
    def _right_rotate(x, n):
        """Циклический сдвиг вправо на n бит (32-битное слово)"""
        return (x >> n) | ((x << (32 - n)) & 0xffffffff)
    
    @staticmethod
    def _right_shift(x, n):
        """Логический сдвиг вправо на n бит"""
        return x >> n
    
    @classmethod
    def _ch(cls, x, y, z):
        """Функция выбора: если x = 1, то y, иначе z"""
        return (x & y) ^ (~x & z)
    
    @classmethod
    def _maj(cls, x, y, z):
        """Функция большинства: 1 если хотя бы 2 бита из 3 равны 1"""
        return (x & y) ^ (x & z) ^ (y & z)
    
    @classmethod
    def _sigma0(cls, x):
        """Σ0: ROTR^7 XOR ROTR^18 XOR SHR^3"""
        return cls._right_rotate(x, 7) ^ cls._right_rotate(x, 18) ^ cls._right_shift(x, 3)
    
    @classmethod
    def _sigma1(cls, x):
        """Σ1: ROTR^17 XOR ROTR^19 XOR SHR^10"""
        return cls._right_rotate(x, 17) ^ cls._right_rotate(x, 19) ^ cls._right_shift(x, 10)
    
    @classmethod
    def _big_sigma0(cls, x):
        """Σ0: ROTR^2 XOR ROTR^13 XOR ROTR^22"""
        return cls._right_rotate(x, 2) ^ cls._right_rotate(x, 13) ^ cls._right_rotate(x, 22)
    
    @classmethod
    def _big_sigma1(cls, x):
        """Σ1: ROTR^6 XOR ROTR^11 XOR ROTR^25"""
        return cls._right_rotate(x, 6) ^ cls._right_rotate(x, 11) ^ cls._right_rotate(x, 25)
    
    @classmethod
    def _pad_message(cls, message):
        """
        Дополнение сообщения согласно SHA-256:
        1. Добавить бит '1'
        2. Добавить нули до длины 448 mod 512
        3. Добавить 64-битную длину исходного сообщения
        """
        # Если message - строка, конвертируем в байты
        if isinstance(message, str):
            msg_bytes = message.encode('utf-8')
        else:
            msg_bytes = message
        
        original_length = len(msg_bytes) * 8  # длина в битах
        
        # Конвертируем в список байт
        data = list(msg_bytes)
        
        # Шаг 1: добавляем бит '1' (0x80 = 1000 0000)
        data.append(0x80)
        
        # Шаг 2: добавляем нули до 448 бит (56 байт) по модулю 512 бит (64 байта)
        while (len(data) * 8) % 512 != 448:
            data.append(0x00)
        
        # Шаг 3: добавляем 64-битную длину (Big-Endian)
        data.extend(struct.pack('>Q', original_length))
        
        return data
    
    @classmethod
    def hash(cls, message):
        """Вычисление хеша SHA-256"""
        # Дополняем сообщение
        padded = cls._pad_message(message)
        
        # Разбиваем на блоки по 512 бит (64 байта)
        blocks = [padded[i:i + 64] for i in range(0, len(padded), 64)]
        
        # Инициализируем рабочие переменные
        h = list(cls._H)
        
        for block in blocks:
            # Расширяем 16 слов (32 бита) до 64 слов
            w = [0] * 64
            for i in range(16):
                w[i] = struct.unpack('>I', bytes(block[i * 4:(i + 1) * 4]))[0]
            
            for i in range(16, 64):
                s0 = cls._sigma0(w[i - 15])
                s1 = cls._sigma1(w[i - 2])
                w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xffffffff
            
            # Инициализация рабочего состояния
            a, b, c, d = h[0], h[1], h[2], h[3]
            e, f, g, hh = h[4], h[5], h[6], h[7]
            
            # 64 раунда
            for i in range(64):
                Σ1 = cls._big_sigma1(e)
                ch = cls._ch(e, f, g)
                t1 = (hh + Σ1 + ch + cls._K[i] + w[i]) & 0xffffffff
                Σ0 = cls._big_sigma0(a)
                maj = cls._maj(a, b, c)
                t2 = (Σ0 + maj) & 0xffffffff
                
                hh = g
                g = f
                f = e
                e = (d + t1) & 0xffffffff
                d = c
                c = b
                b = a
                a = (t1 + t2) & 0xffffffff
            
            # Добавляем к начальному вектору
            h[0] = (h[0] + a) & 0xffffffff
            h[1] = (h[1] + b) & 0xffffffff
            h[2] = (h[2] + c) & 0xffffffff
            h[3] = (h[3] + d) & 0xffffffff
            h[4] = (h[4] + e) & 0xffffffff
            h[5] = (h[5] + f) & 0xffffffff
            h[6] = (h[6] + g) & 0xffffffff
            h[7] = (h[7] + hh) & 0xffffffff
        
        # Формируем финальный хеш (Big-Endian)
        return ''.join(f'{x:08x}' for x in h)


# ================================================
# ДЕМОНСТРАЦИЯ РАБОТЫ
# ================================================

def demo_hash_algorithms():
    """Демонстрация всех хеш-алгоритмов"""
    
    print("=" * 70)
    print("ОБЗОР ХЕШ-АЛГОРИТМОВ (РЕАЛИЗАЦИЯ НА PYTHON)")
    print("=" * 70)
    
    test_strings = [
        "Hello, World!",
        "Биткойн использует SHA-256",
        "MD5 был взломан в 2004 году"
    ]
    
    for text in test_strings:
        print(f"\n📝 Исходный текст: \"{text}\"")
        print("-" * 60)
        
        # 1. Наша реализация SHA-256
        start = time.perf_counter()
        sha256_our = SHA256.hash(text)
        time_our = (time.perf_counter() - start) * 1000
        
        # 2. Встроенный SHA-256 (для проверки)
        start = time.perf_counter()
        sha256_builtin = hashlib.sha256(text.encode('utf-8')).hexdigest()
        time_builtin = (time.perf_counter() - start) * 1000
        
        # 3. Встроенный MD5
        start = time.perf_counter()
        md5_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        time_md5 = (time.perf_counter() - start) * 1000
        
        # 4. CRC32
        start = time.perf_counter()
        crc32_val = zlib.crc32(text.encode('utf-8')) & 0xffffffff
        crc32_hex = f"{crc32_val:08x}"
        time_crc32 = (time.perf_counter() - start) * 1000
        
        print(f"  🔐 SHA-256 (наша реализация): {sha256_our}  ({time_our:.3f} мс)")
        print(f"  🔐 SHA-256 (встроенный):      {sha256_builtin}  ({time_builtin:.3f} мс)")
        print(f"  ✅ Совпадение: {sha256_our == sha256_builtin}")
        print(f"  📦 MD5:                       {md5_hash}  ({time_md5:.3f} мс)")
        print(f"  📊 CRC32:                     {crc32_hex}  ({time_crc32:.3f} мс)")


def demo_avalanche_effect():
    """Демонстрация лавинного эффекта (изменение 1 бита)"""
    
    print("\n" + "=" * 70)
    print("ЛАВИННЫЙ ЭФФЕКТ SHA-256 (изменение 1 бита)")
    print("=" * 70)
    
    text1 = "Hello, World!"
    text2 = "Hello, World?"  # Изменён последний символ
    
    print(f"\n📝 Текст 1: \"{text1}\"")
    hash1 = SHA256.hash(text1)
    print(f"   Хеш:     {hash1}")
    
    print(f"\n📝 Текст 2: \"{text2}\"")
    hash2 = SHA256.hash(text2)
    print(f"   Хеш:     {hash2}")
    
    # Подсчёт отличающихся бит
    diff_bits = 0
    for c1, c2 in zip(hash1, hash2):
        if c1 != c2:
            diff_bits += bin(int(c1, 16) ^ int(c2, 16)).count('1')
    
    print(f"\n💥 Отличается бит: {diff_bits} из 256 ({diff_bits / 256 * 100:.1f}%)")
    print("   (Идеальный лавинный эффект ~50%)")


def demo_ripemd160():
    """Демонстрация RIPEMD-160 (используется в Bitcoin)"""
    
    print("\n" + "=" * 70)
    print("RIPEMD-160 (используется в Bitcoin для адресов)")
    print("=" * 70)
    
    text = "Биткойн адрес"
    
    # Пробуем разные способы получить RIPEMD-160
    try:
        # Способ 1: hashlib.new (Python 3.11+)
        ripemd160 = hashlib.new('ripemd160', text.encode('utf-8')).hexdigest()
        print(f"\n📝 Текст: \"{text}\"")
        print(f"🔑 RIPEMD-160: {ripemd160}")
        print("   (Сокращает 256-битный ключ до 160 бит для адреса)")
    except ValueError:
        try:
            # Способ 2: через pycryptodome
            from Crypto.Hash import RIPEMD160
            ripemd160 = RIPEMD160.new(text.encode('utf-8')).hexdigest()
            print(f"\n📝 Текст: \"{text}\"")
            print(f"🔑 RIPEMD-160: {ripemd160}")
            print("   (Сокращает 256-битный ключ до 160 бит для адреса)")
        except ImportError:
            print("\n⚠️  RIPEMD-160 не доступен.")
            print("   Установите: pip install pycryptodome")
            print("   Или используйте Python 3.11+ с hashlib.new('ripemd160')")


def demo_collision_security():
    """Демонстрация устойчивости к коллизиям"""
    
    print("\n" + "=" * 70)
    print("УСТОЙЧИВОСТЬ К КОЛЛИЗИЯМ (теоретическая)")
    print("=" * 70)
    
    # Теоретические оценки из вашего текста
    data = {
        "MD5": {
            "выход": "128 бит",
            "атака дня рождения": "2^64 операций",
            "статус": "❌ СЛОМАН (практические коллизии с 2004)"
        },
        "SHA-1": {
            "выход": "160 бит", 
            "атака дня рождения": "2^80 операций",
            "статус": "❌ СЛОМАН (с 2017 практические коллизии)"
        },
        "SHA-256": {
            "выход": "256 бит",
            "атака дня рождения": "2^128 операций",
            "статус": "✅ БЕЗОПАСЕН (нет практических атак)"
        },
        "RIPEMD-160": {
            "выход": "160 бит",
            "атака дня рождения": "2^80 операций",
            "статус": "✅ БЕЗОПАСЕН (не взломан)"
        }
    }
    
    for algo, info in data.items():
        print(f"\n{algo}:")
        print(f"  • Длина: {info['выход']}")
        print(f"  • Сложность коллизии: {info['атака дня рождения']}")
        print(f"  • {info['статус']}")


def demo_bitcoin_mining_simulation():
    """Симуляция майнинга Bitcoin (упрощённо)"""
    
    print("\n" + "=" * 70)
    print("СИМУЛЯЦИЯ МАЙНИНГА BITCOIN (PoW)")
    print("=" * 70)
    
    # Упрощённая версия: ищем nonce, чтобы хеш начинался с 3 нулей (быстрее)
    block_data = "Блок #42: Транзакции майнера"
    target_zeros = 3  # Уменьшил с 4 до 3 для скорости
    target = "0" * target_zeros
    
    print(f"\n⛏️  Данные блока: \"{block_data}\"")
    print(f"🎯 Цель: хеш должен начинаться с {target_zeros} нулей ({target}...)")
    print("\nПоиск nonce... (нажмите Ctrl+C для прерывания)")
    print("-" * 60)
    
    start_time = time.perf_counter()
    nonce = 0
    found = False
    max_nonce = 200000  # Ограничим для безопасности
    
    try:
        while not found and nonce < max_nonce:
            test_data = f"{block_data}{nonce}"
            hash_result = SHA256.hash(test_data)
            
            if hash_result.startswith(target):
                found = True
                break
            
            nonce += 1
            
            # Показываем прогресс каждые 1000 попыток
            if nonce % 1000 == 0:
                print(f"  ⏳ Попытка {nonce}: {hash_result}")
                # Если слишком долго, уменьшаем цель
                if nonce > 10000 and not found:
                    print("  🔄 Упрощаем цель до 2 нулей...")
                    target = "00"
                    target_zeros = 2
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Поиск прерван пользователем")
        elapsed = time.perf_counter() - start_time
        print(f"   Попыток: {nonce}")
        print(f"   Время: {elapsed:.2f} секунд")
        return
    
    elapsed = time.perf_counter() - start_time
    
    if found:
        print(f"\n✅ Nonce найден: {nonce}")
        print(f"   Хеш блока: {hash_result}")
        print(f"   Время: {elapsed:.3f} секунд")
        print(f"   🎉 Майнер получает награду!")
    else:
        print(f"\n❌ Nonce не найден за {max_nonce} попыток")
        print(f"   (В реальном Bitcoin цель гораздо сложнее)")


def demo_quick_performance():
    """Быстрый тест производительности"""
    
    print("\n" + "=" * 70)
    print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 70)
    
    test_text = "Тестовое сообщение для проверки скорости" * 100
    
    # SHA-256 (наша реализация)
    start = time.perf_counter()
    for _ in range(10):
        SHA256.hash(test_text)
    our_time = (time.perf_counter() - start) * 1000
    
    # SHA-256 (встроенный)
    start = time.perf_counter()
    for _ in range(10):
        hashlib.sha256(test_text.encode('utf-8')).hexdigest()
    builtin_time = (time.perf_counter() - start) * 1000
    
    print(f"\n📊 10 хешей от {len(test_text)} байт:")
    print(f"  • Наша реализация SHA-256: {our_time:.2f} мс")
    print(f"  • Встроенный SHA-256:      {builtin_time:.2f} мс")
    print(f"  • Отношение: {our_time / builtin_time:.1f}x медленнее")


# ================================================
# ЗАПУСК ВСЕХ ДЕМОНСТРАЦИЙ
# ================================================

if __name__ == "__main__":
    try:
        demo_hash_algorithms()
        demo_avalanche_effect()
        demo_ripemd160()
        demo_collision_security()
        demo_bitcoin_mining_simulation()
        demo_quick_performance()
        
        print("\n" + "=" * 70)
        print("📚 ИТОГ:")
        print("  • SHA-256 — безопасен, используется в Bitcoin")
        print("  • MD5 — сломан (коллизии)")
        print("  • CRC32 — только для проверки целостности, не криптография")
        print("  • RIPEMD-160 — безопасен, применяется в адресах Bitcoin")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Программа остановлена пользователем")
        sys.exit(0)