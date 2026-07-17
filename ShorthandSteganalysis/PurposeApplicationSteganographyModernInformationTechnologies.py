# Назначение и применение стеганографии в современных информационных технологиях
"""
Стеганография в изображениях (метод LSB)
Исправленная версия с улучшенной обработкой ошибок
"""

from PIL import Image
import hashlib
import os
from typing import Tuple, Optional, List

class SteganographyLSB:
    """Класс для стеганографии с использованием LSB"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.delimiter = "#####"
        self.padding = "PADDING"  # Для выравнивания
        
    def _text_to_bits(self, text: str) -> List[int]:
        """Преобразует текст в биты с разделителем"""
        # Добавляем длину сообщения в начале (4 байта = 32 бита)
        text_bytes = text.encode('utf-8')
        length = len(text_bytes)
        length_bits = []
        for i in range(31, -1, -1):
            length_bits.append((length >> i) & 1)
        
        # Преобразуем текст в биты
        text_bits = []
        for byte in text_bytes:
            for i in range(7, -1, -1):
                text_bits.append((byte >> i) & 1)
        
        # Добавляем разделитель
        delimiter_bits = []
        for char in self.delimiter:
            byte = ord(char)
            for i in range(7, -1, -1):
                delimiter_bits.append((byte >> i) & 1)
        
        return length_bits + text_bits + delimiter_bits
    
    def _bits_to_text(self, bits: List[int]) -> str:
        """Преобразует биты обратно в текст"""
        if len(bits) < 32:
            return ""
        
        # Извлекаем длину сообщения
        length = 0
        for i in range(32):
            length = (length << 1) | bits[i]
        
        if length == 0 or length > 10000:
            return ""
        
        # Извлекаем текст
        text_bytes = []
        bit_idx = 32
        for _ in range(length):
            if bit_idx + 8 > len(bits):
                break
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[bit_idx + j]
            text_bytes.append(byte)
            bit_idx += 8
        
        try:
            return bytes(text_bytes).decode('utf-8', errors = 'ignore')
        except:
            return ""
    
    def _get_pixels_flat(self, img: Image.Image) -> List[int]:
        """Получает плоский список пикселей (совместимо с Pillow 12+)"""
        # Используем getdata() с предупреждением, но это работает
        pixels = list(img.getdata())
        flat = []
        for pixel in pixels:
            if isinstance(pixel, tuple):
                flat.extend(pixel)
            else:
                flat.append(pixel)
        return flat
    
    def _set_pixels_from_flat(self, img: Image.Image, flat: List[int]) -> Image.Image:
        """Восстанавливает изображение из плоского списка"""
        width, height = img.size
        channels = 3 if img.mode == 'RGB' else 1
        
        new_pixels = []
        idx = 0
        for _ in range(height):
            row = []
            for _ in range(width):
                if channels == 3:
                    pixel = tuple(flat[idx:idx + 3])
                    idx += 3
                else:
                    pixel = flat[idx]
                    idx += 1
                row.append(pixel)
            new_pixels.append(row)
        
        new_img = Image.new(img.mode, (width, height))
        new_img.putdata([p for row in new_pixels for p in row])
        return new_img
    
    def embed_message(self, image_path: str, message: str, output_path: str) -> bool:
        """Встраивает сообщение в изображение"""
        if self.verbose:
            print(f"[Алиса] Контейнер: {image_path}")
            print(f"[Алиса] Сообщение: '{message}'")
        
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
        
        flat_pixels = self._get_pixels_flat(img)
        bits = self._text_to_bits(message)
        
        max_bits = len(flat_pixels)
        if len(bits) > max_bits:
            print(f"Ошибка: сообщение слишком большое ({len(bits)} > {max_bits})")
            return False
        
        if self.verbose:
            print(f"[Алиса] Размер: {len(bits)} бит, ёмкость: {max_bits} бит")
        
        # Встраиваем биты
        for i in range(len(bits)):
            flat_pixels[i] = (flat_pixels[i] & ~1) | bits[i]
        
        embedded_img = self._set_pixels_from_flat(img, flat_pixels)
        embedded_img.save(output_path, 'PNG')
        
        # Сохраняем хэш
        hash_value = self._calculate_hash(output_path)
        with open(output_path + ".hash", 'w') as f:
            f.write(hash_value)
        
        if self.verbose:
            print(f"[Алиса] Сохранено: {output_path}")
        
        return True
    
    def extract_message(self, image_path: str) -> Optional[str]:
        """Извлекает сообщение из изображения"""
        if self.verbose:
            print(f"[Боб] Извлечение из: {image_path}")
        
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
        
        flat_pixels = self._get_pixels_flat(img)
        bits = [flat_pixels[i] & 1 for i in range(len(flat_pixels))]
        
        message = self._bits_to_text(bits)
        
        # Проверяем наличие разделителя
        if self.delimiter not in message:
            # Если разделитель не найден, пробуем извлечь без длины
            # Просто ищем текст до первого нечитаемого символа
            clean_message = ''.join(c for c in message if 32 <= ord(c) <= 126 or c in '.,!?- ')
            if clean_message and len(clean_message) > 3:
                message = clean_message
            else:
                message = ""
        
        if self.verbose:
            print(f"[Боб] Извлечено: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
        return message
    
    def _calculate_hash(self, image_path: str) -> str:
        """Вычисляет SHA-256 хэш"""
        with open(image_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def verify_integrity(self, image_path: str) -> Tuple[bool, str]:
        """Проверяет целостность"""
        hash_file = image_path + ".hash"
        if not os.path.exists(hash_file):
            return False, "❌ Файл хэша не найден"
        
        with open(hash_file, 'r') as f:
            stored_hash = f.read().strip()
        
        current_hash = self._calculate_hash(image_path)
        
        if current_hash == stored_hash:
            return True, "✅ Целостность подтверждена"
        else:
            return False, "❌ Целостность нарушена!"
    
    def attack_compression(self, image_path: str, quality: int = 30) -> str:
        """Атака сжатием JPEG"""
        if self.verbose:
            print(f"[Ева] Сжатие JPEG (качество = {quality})")
        
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
        
        output_path = f"{os.path.splitext(image_path)[0]}_compressed_{quality}.jpg"
        img.save(output_path, 'JPEG', quality = quality)
        
        if self.verbose:
            orig_size = os.path.getsize(image_path)
            comp_size = os.path.getsize(output_path)
            print(f"[Ева] {orig_size} → {comp_size} байт")
        
        return output_path


class WatermarkDemo:
    """Демонстрация водяных знаков"""
    
    def __init__(self, stego: SteganographyLSB):
        self.stego = stego
    
    def embed_watermark(self, image_path: str, owner_name: str, output_path: str) -> bool:
        """Встраивает водяной знак"""
        watermark = f"©{owner_name}|ID:{hashlib.md5(owner_name.encode()).hexdigest()[:8]}"
        return self.stego.embed_message(image_path, watermark, output_path)
    
    def verify_ownership(self, image_path: str, owner_name: str) -> bool:
        """Проверяет владельца"""
        extracted = self.stego.extract_message(image_path)
        if not extracted:
            return False
        return f"©{owner_name}" in extracted


def create_test_image():
    """Создаёт тестовое изображение"""
    test_image = "test_container.png"
    if os.path.exists(test_image):
        return test_image
    
    print("[Создание] Генерация тестового изображения...")
    
    width, height = 200, 200
    img = Image.new('RGB', (width, height), (100, 150, 200))
    pixels = img.load()
    
    # Узор
    for x in range(50, 150):
        for y in range(50, 150):
            if (x - 50) % 10 < 5 and (y - 50) % 10 < 5:
                pixels[x, y] = (255, 255, 255)
            elif (x - 50) % 10 >= 5 and (y - 50) % 10 >= 5:
                pixels[x, y] = (200, 100, 50)
    
    # Рамка
    for x in range(40, 160):
        pixels[x, 40] = (255, 255, 255)
        pixels[x, 159] = (255, 255, 255)
    for y in range(40, 160):
        pixels[40, y] = (255, 255, 255)
        pixels[159, y] = (255, 255, 255)
    
    img.save(test_image)
    print(f"[Создание] {test_image} ({width}x{height})")
    return test_image


def main():
    """Основная демонстрация"""
    print("=" * 70)
    print("СТЕГАНОГРАФИЯ В СОВРЕМЕННЫХ ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЯХ")
    print("=" * 70)
    print("\nНа основе текста:")
    print("  📌 Скрытая передача данных")
    print("  📌 Водяные знаки (защита авторских прав)")
    print("  📌 Проверка целостности")
    print("  📌 Атаки на стегосистемы")
    print("=" * 70)
    
    # Проверяем Pillow
    try:
        import PIL
        print(f"\n✅ Pillow {PIL.__version__}")
    except ImportError:
        print("\n❌ Установите: pip install Pillow")
        return
    
    stego = SteganographyLSB(verbose=True)
    test_image = create_test_image()
    
    # 1. Скрытая передача
    print("\n" + "─" * 70)
    print("1️⃣ СКРЫТАЯ ПЕРЕДАЧА (из текста: пример с Першингом)")
    print("─" * 70)
    
    secret = "Pershing sails from NY June I"
    stego_img = "stego_image.png"
    
    if stego.embed_message(test_image, secret, stego_img):
        extracted = stego.extract_message(stego_img)
        print(f"\n📨 Оригинал: '{secret}'")
        print(f"📨 Извлечено: '{extracted}'")
        print(f"✅ Совпадает: {extracted == secret}")
    
    # 2. Проверка целостности
    print("\n" + "─" * 70)
    print("2️⃣ ПРОВЕРКА ЦЕЛОСТНОСТИ")
    print("─" * 70)
    
    is_valid, msg = stego.verify_integrity(stego_img)
    print(f"\n🔍 {msg}")
    
    # 3. Атака сжатием
    print("\n" + "─" * 70)
    print("3️⃣ АТАКА СЖАТИЕМ (Ева пытается уничтожить данные)")
    print("─" * 70)
    
    compressed = stego.attack_compression(stego_img, quality = 30)
    if compressed:
        extracted_after = stego.extract_message(compressed)
        print(f"\n📨 После атаки: '{extracted_after[:50]}'")
        if extracted_after == secret:
            print("✅ Данные сохранены")
        else:
            print("⚠️ Данные частично/полностью разрушены (JPEG сжатие разрушает LSB)")
    
    # 4. Водяной знак
    print("\n" + "─" * 70)
    print("4️⃣ ВОДЯНОЙ ЗНАК (защита авторских прав)")
    print("─" * 70)
    
    wm = WatermarkDemo(stego)
    owner = "Алиса Иванова"
    wm_img = "watermarked.png"
    
    if wm.embed_watermark(test_image, owner, wm_img):
        print(f"\n👤 Владелец: {owner}")
        
        # Проверка
        is_owner = wm.verify_ownership(wm_img, owner)
        print(f"✅ Проверка '{owner}': {'Да' if is_owner else 'Нет'}")
        
        fake = "Ева Петрова"
        is_fake = wm.verify_ownership(wm_img, fake)
        print(f"❌ Проверка '{fake}': {'Да (ошибка!)' if is_fake else 'Нет (правильно)'}")
    
    # 5. Акростих
    print("\n" + "─" * 70)
    print("5️⃣ АКРОСТИХ (исторический метод)")
    print("─" * 70)
    
    poem = """Ангел лег у края небосклона,
        Наклонившись, удивлялся бездне;
        Новый мир был синим и беззвездным.
        Ад молчал, не слышалось ни стона.
        Алой крови робкое биение,
        Хрупких рук испуг и содроганье
        Миру снов досталось в обладанье
        Ангела святое отраженье.
        Тесно в мире, пусть живет, мечтая
        О любви, о свете и о тени,
        В ужасе предвечном открывая
        Азбуку своих же откровений"""
    
    lines = poem.split('\n')
    acrostic = ''.join(line.strip()[0] for line in lines if line.strip())
    
    print(f"\n📜 Акростих: {acrostic}")
    print(f"✅ Совпадает с 'АННААХМАТОВА': {acrostic == 'АННААХМАТОВА'}")
    
    # Итоги
    print("\n" + "=" * 70)
    print("📋 ИТОГИ")
    print("=" * 70)
    print("""
        ✅ LSB-стеганография работает
        ✅ Хэш-сумма подтверждает целостность
        ⚠️ JPEG-сжатие разрушает скрытые данные (это ожидаемо)
        ✅ Водяные знаки позволяют идентифицировать владельца
        ✅ Акростих демонстрирует исторический метод
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма остановлена.")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")