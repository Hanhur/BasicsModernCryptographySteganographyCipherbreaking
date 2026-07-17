# Стегоанализ на основе сжатия данныхimport os
import random
import struct
import zlib
import lzma
import bz2
from pathlib import Path
from typing import List, Tuple, Optional
import argparse
import math
import os

class CompressionSteganalysis:
    """
    Стегоанализ на основе сжатия данных для BMP-изображений.
    Реализует метод, описанный в работе [55].
    """
    
    def __init__(self, compression_method = 'zlib', block_count = 4, threshold = 0.15):
        """
        Инициализация стегоанализатора.
        
        Args:
            compression_method: метод сжатия ('zlib', 'lzma', 'bz2')
            block_count: количество блоков для разбиения изображения
            threshold: порог для принятия решения (должен быть настроен экспериментально)
        """
        self.compression_method = compression_method
        self.block_count = block_count
        self.threshold = threshold
        self.compression_func = self._get_compression_func(compression_method)
        
    def _get_compression_func(self, method):
        """Возвращает функцию сжатия для выбранного метода."""
        if method == 'zlib':
            return lambda data: zlib.compress(data, level = 9)
        elif method == 'lzma':
            return lambda data: lzma.compress(data, format = lzma.FORMAT_ALONE)
        elif method == 'bz2':
            return lambda data: bz2.compress(data, compresslevel = 9)
        else:
            raise ValueError(f"Неподдерживаемый метод сжатия: {method}")
    
    def read_bmp(self, file_path: str) -> Tuple[bytes, int, int]:
        """
        Чтение BMP-файла.
        
        Returns:
            (данные_изображения, ширина, высота)
        """
        with open(file_path, 'rb') as f:
            # Читаем заголовок BMP
            header = f.read(54)  # Стандартный BMP заголовок
            
            # Проверяем, что это BMP
            if header[0:2] != b'BM':
                raise ValueError("Не BMP файл")
            
            # Получаем размеры изображения
            width = struct.unpack('<I', header[18:22])[0]
            height = struct.unpack('<I', header[22:26])[0]
            
            # Получаем смещение до данных пикселей
            pixel_offset = struct.unpack('<I', header[10:14])[0]
            
            # Читаем данные пикселей
            f.seek(pixel_offset)
            pixel_data = f.read()
            
            return pixel_data, width, height
    
    def get_lsb(self, byte: int) -> int:
        """Получает младший значащий бит байта."""
        return byte & 1
    
    def set_lsb(self, byte: int, bit: int) -> int:
        """Устанавливает младший значащий бит байта."""
        return (byte & 0xFE) | (bit & 1)
    
    def replace_lsb_with_random(self, data: bytes) -> bytes:
        """
        Заменяет LSB всех байтов на случайные биты.
        Соответствует преобразованию φ(U) из текста.
        """
        # Генерируем случайные биты для каждого байта
        random_bits = [random.randint(0, 1) for _ in range(len(data))]
        
        # Заменяем LSB
        result = bytearray(len(data))
        for i, byte in enumerate(data):
            result[i] = self.set_lsb(byte, random_bits[i])
        
        return bytes(result)
    
    def replace_lsb_with_message(self, data: bytes, message: bytes) -> bytes:
        """
        Встраивает сообщение в LSB байтов.
        Используется для создания заполненных контейнеров в экспериментах.
        """
        result = bytearray(data)
        msg_bits = self._bytes_to_bits(message)
        
        # Встраиваем биты сообщения в LSB
        bit_index = 0
        for i in range(len(result)):
            if bit_index < len(msg_bits):
                result[i] = self.set_lsb(result[i], msg_bits[bit_index])
                bit_index += 1
            else:
                # Если сообщение закончилось, заполняем случайными битами
                result[i] = self.set_lsb(result[i], random.randint(0, 1))
        
        return bytes(result)
    
    def _bytes_to_bits(self, data: bytes) -> List[int]:
        """Преобразует байты в биты."""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
    
    def compress_ratio(self, data: bytes) -> float:
        """
        Вычисляет коэффициент сжатия f(U) = |Ψ(U)| / |U|.
        """
        try:
            compressed = self.compression_func(data)
            return len(compressed) / len(data) if len(data) > 0 else 1.0
        except Exception as e:
            print(f"Ошибка сжатия: {e}")
            return 1.0
    
    def compute_delta(self, data: bytes) -> float:
        """
        Вычисляет δ(U) = |f(φ(U)) - f(U)|.
        """
        f_original = self.compress_ratio(data)
        
        # Применяем преобразование φ
        modified_data = self.replace_lsb_with_random(data)
        f_modified = self.compress_ratio(modified_data)
        
        return abs(f_modified - f_original)
    
    def analyze_image(self, image_path: str) -> Tuple[float, List[float], bool]:
        """
        Анализирует изображение на наличие скрытой информации.
        
        Returns:
            (среднее_δ, список_δ_по_блокам, есть_скрытые_данные)
        """
        # Читаем изображение
        pixel_data, width, height = self.read_bmp(image_path)
        
        # Разбиваем на блоки
        block_size = len(pixel_data) // self.block_count
        delta_values = []
        
        for i in range(self.block_count):
            start = i * block_size
            end = (i + 1) * block_size if i < self.block_count - 1 else len(pixel_data)
            block = pixel_data[start:end]
            
            if len(block) > 0:
                delta = self.compute_delta(block)
                delta_values.append(delta)
        
        # Вычисляем максимальное δ (как в оригинальном методе)
        max_delta = max(delta_values) if delta_values else 0
        
        # Принимаем решение на основе максимального δ
        has_hidden_data = max_delta < self.threshold
        
        return max_delta, delta_values, has_hidden_data
    
    def analyze_with_sliding_window(self, image_path: str, window_size: int = 1024) -> List[float]:
        """
        Анализирует изображение с использованием скользящего окна.
        Может быть более эффективным для обнаружения небольших вложений.
        """
        pixel_data, _, _ = self.read_bmp(image_path)
        delta_values = []
        
        for i in range(0, len(pixel_data) - window_size + 1, window_size // 2):
            window = pixel_data[i:i + window_size]
            delta = self.compute_delta(window)
            delta_values.append(delta)
        
        return delta_values
    
    def create_test_dataset(self, image_path: str, output_dir: str):
        """
        Создает тестовый набор данных для калибровки порога:
        - Исходное изображение (пустой контейнер)
        - Изображение со встроенным сообщением (заполненный контейнер)
        """
        os.makedirs(output_dir, exist_ok = True)
        
        # Читаем исходное изображение
        with open(image_path, 'rb') as f:
            original_data = f.read()
        
        # Сохраняем оригинал
        clean_path = os.path.join(output_dir, 'clean.bmp')
        with open(clean_path, 'wb') as f:
            f.write(original_data)
        
        # Создаем изображение со встроенным сообщением
        header_size = 54
        pixel_data = original_data[header_size:]
        
        # Генерируем случайное сообщение для встраивания
        message = os.urandom(len(pixel_data) // 8)  # Используем 12.5% емкости
        
        # Встраиваем сообщение
        modified_pixel_data = self.replace_lsb_with_message(pixel_data, message)
        
        # Собираем обратно BMP
        modified_data = original_data[:header_size] + modified_pixel_data
        
        filled_path = os.path.join(output_dir, 'filled.bmp')
        with open(filled_path, 'wb') as f:
            f.write(modified_data)
        
        print(f"Тестовые изображения созданы в {output_dir}")
        return clean_path, filled_path
    
    def calibrate_threshold(self, clean_images_dir: str, filled_images_dir: str) -> float:
        """
        Калибрует порог на основе известных чистых и заполненных изображений.
        """
        clean_deltas = []
        filled_deltas = []
        
        # Анализируем чистые изображения
        for img_file in Path(clean_images_dir).glob('*.bmp'):
            delta, _, _ = self.analyze_image(str(img_file))
            clean_deltas.append(delta)
        
        # Анализируем заполненные изображения
        for img_file in Path(filled_images_dir).glob('*.bmp'):
            delta, _, _ = self.analyze_image(str(img_file))
            filled_deltas.append(delta)
        
        if not clean_deltas or not filled_deltas:
            raise ValueError("Нет изображений для калибровки")
        
        # Вычисляем оптимальный порог (среднее между средними значениями)
        mean_clean = sum(clean_deltas) / len(clean_deltas)
        mean_filled = sum(filled_deltas) / len(filled_deltas)
        
        # Порог как среднее между средними
        threshold = (mean_clean + mean_filled) / 2
        
        print(f"Калибровка завершена:")
        print(f"  Среднее δ для чистых: {mean_clean:.4f}")
        print(f"  Среднее δ для заполненных: {mean_filled:.4f}")
        print(f"  Рекомендуемый порог: {threshold:.4f}")
        
        return threshold

def main():
    """Главная функция для командной строки."""
    parser = argparse.ArgumentParser(
        description = 'Стегоанализ BMP-изображений на основе сжатия'
    )
    parser.add_argument('image', help = 'Путь к BMP-изображению')
    parser.add_argument('--method', default = 'zlib',  choices = ['zlib', 'lzma', 'bz2'], help = 'Метод сжатия')
    parser.add_argument('--blocks', type = int, default = 4, help = 'Количество блоков для анализа')
    parser.add_argument('--threshold', type = float, default = 0.15, help = 'Порог для принятия решения')
    parser.add_argument('--calibrate', action = 'store_true', help = 'Калибровать порог (требуется папка с тестовыми изображениями)')
    parser.add_argument('--test-data', help = 'Создать тестовые данные в указанной папке')
    parser.add_argument('--window', type = int, default = 0, help = 'Размер окна для скользящего анализа (0 - отключен)')
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = CompressionSteganalysis(
        compression_method = args.method,
        block_count = args.blocks,
        threshold = args.threshold
    )
    
    if args.test_data:
        # Создаем тестовые данные
        clean_path, filled_path = analyzer.create_test_dataset(
            args.image, 
            args.test_data
        )
        return
    
    if args.calibrate:
        # Калибровка порога
        print("Калибровка порога...")
        print("Укажите папки с чистыми и заполненными изображениями:")
        clean_dir = input("Папка с чистыми изображениями: ").strip()
        filled_dir = input("Папка с заполненными изображениями: ").strip()
        threshold = analyzer.calibrate_threshold(clean_dir, filled_dir)
        analyzer.threshold = threshold
        return
    
    # Анализируем изображение
    print(f"Анализ изображения: {args.image}")
    print(f"Метод сжатия: {args.method}")
    print(f"Количество блоков: {args.blocks}")
    print(f"Порог: {args.threshold}")
    print("-" * 50)
    
    try:
        max_delta, delta_values, has_hidden = analyzer.analyze_image(args.image)
        
        print(f"Максимальное δ: {max_delta:.6f}")
        print(f"Все значения δ по блокам: {[f'{d:.6f}' for d in delta_values]}")
        avg_delta = sum(delta_values) / len(delta_values) if delta_values else 0
        print(f"Среднее δ: {avg_delta:.6f}")
        
        # Вычисляем стандартное отклонение
        if len(delta_values) > 1:
            variance = sum((d - avg_delta) ** 2 for d in delta_values) / len(delta_values)
            std_delta = math.sqrt(variance)
            print(f"Стандартное отклонение δ: {std_delta:.6f}")
        print("-" * 50)
        
        if has_hidden:
            print("⚠️  ОБНАРУЖЕНЫ скрытые данные!")
            print(f"   (δ = {max_delta:.6f} < порога {args.threshold})")
        else:
            print("✅ Скрытые данные НЕ обнаружены")
            print(f"   (δ = {max_delta:.6f} >= порога {args.threshold})")
        
        # Дополнительный анализ со скользящим окном
        if args.window > 0:
            print(f"\nДополнительный анализ со скользящим окном (размер: {args.window}):")
            sliding_deltas = analyzer.analyze_with_sliding_window(args.image, args.window)
            if sliding_deltas:
                min_delta = min(sliding_deltas)
                max_delta_sliding = max(sliding_deltas)
                avg_delta_sliding = sum(sliding_deltas) / len(sliding_deltas)
                print(f"  Минимальное δ: {min_delta:.6f}")
                print(f"  Максимальное δ: {max_delta_sliding:.6f}")
                print(f"  Среднее δ: {avg_delta_sliding:.6f}")
        
    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()