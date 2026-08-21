# Происхождение Q-криптографии: квантовые деньги
import random
import string

# -------------------------------------------------------------------
# 1. БАЗОВЫЕ КВАНТОВЫЕ ОПЕРАЦИИ (без numpy)
# -------------------------------------------------------------------

class Polarization:
    """Класс-константа для направлений поляризации"""
    H = 'H'  # Горизонтальная (0°)
    V = 'V'  # Вертикальная (90°)
    D = 'D'  # Диагональная (45°)
    A = 'A'  # Анти-диагональная (135°)
    
    # Базисы измерения: {название: список допустимых состояний}
    BASES = {
        'rectilinear': [H, V],   # Прямолинейный базис (+, ×)
        'diagonal': [D, A]       # Диагональный базис (×)
    }
    
    # Соответствие битов для каждого базиса
    BIT_MAP = {
        H: 0, V: 1,
        D: 0, A: 1
    }

def random_photon():
    """Создает случайный фотон со случайной поляризацией"""
    return random.choice([Polarization.H, Polarization.V, Polarization.D, Polarization.A])

def get_basis(polarization):
    """Определяет базис для данной поляризации"""
    if polarization in [Polarization.H, Polarization.V]:
        return 'rectilinear'
    else:
        return 'diagonal'

def measure_photon(photon, filter_orientation):
    """
    Имитирует измерение фотона через фильтр.
    Возвращает: (прошел_ли_фотон, новая_поляризация)
    """
    # Определяем базис фильтра
    if filter_orientation in [Polarization.H, Polarization.V]:
        filter_basis = 'rectilinear'
    else:
        filter_basis = 'diagonal'
    
    photon_basis = get_basis(photon)
    
    # Если базисы совпадают - измерение детерминированное
    if photon_basis == filter_basis:
        # Фотон проходит только если его поляризация совпадает с фильтром
        if photon == filter_orientation:
            return (True, photon)  # Прошел без изменения
        else:
            return (False, None)   # Заблокирован
    else:
        # Базисы разные - квантовый случай (суперпозиция)
        # Фотон проходит с вероятностью 50% и меняет поляризацию
        if random.random() < 0.5:
            # Прошел, выбрал случайную поляризацию в базисе фильтра
            new_polarization = random.choice([filter_orientation, get_opposite_in_basis(filter_orientation)])
            return (True, new_polarization)
        else:
            return (False, None)

def get_opposite_in_basis(polarization):
    """Возвращает противоположную поляризацию в том же базисе"""
    if polarization == Polarization.H:
        return Polarization.V
    elif polarization == Polarization.V:
        return Polarization.H
    elif polarization == Polarization.D:
        return Polarization.A
    elif polarization == Polarization.A:
        return Polarization.D

# -------------------------------------------------------------------
# 2. КВАНТОВАЯ БАНКНОТА (по идее Визнера)
# -------------------------------------------------------------------

class QuantumBanknote:
    """Класс, представляющий квантовую банкноту с 20 фотонами"""
    
    def __init__(self, num_photons = 20):
        self.num_photons = num_photons
        self.serial_number = self._generate_serial()
        # Секретные данные банка: поляризация каждого фотона
        self.photons = [random_photon() for _ in range(num_photons)]
        # Сохраняем битовое представление для проверки
        self.bits = [Polarization.BIT_MAP[p] for p in self.photons]
        # Словарь для хранения результатов измерений (заполняется при проверке)
        self.measurement_results = None
    
    def _generate_serial(self):
        """Генерирует случайный серийный номер"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
    
    def get_photon(self, index):
        """Возвращает поляризацию фотона (знает только банк)"""
        if 0 <= index < self.num_photons:
            return self.photons[index]
        return None
    
    def get_bit(self, index):
        """Возвращает бит, соответствующий фотону"""
        return self.bits[index]
    
    def print_secret(self):
        """Показывает секретную информацию банкноты (для отладки)"""
        print(f"\n=== СЕКРЕТНАЯ ИНФОРМАЦИЯ БАНКНОТЫ ===")
        print(f"Серийный номер: {self.serial_number}")
        print(f"Поляризации:   {''.join(self.photons)}")
        print(f"Биты:          {''.join(map(str, self.bits))}")
        print("=" * 40)

# -------------------------------------------------------------------
# 3. ПРОЦЕСС ПОДДЕЛКИ (Ева)
# -------------------------------------------------------------------

class Eve:
    """Класс, моделирующий действия злоумышленницы Евы"""
    
    @staticmethod
    def copy_banknote(original_banknote):
        """
        Ева пытается скопировать банкноту, измеряя все фотоны
        случайными фильтрами.
        Возвращает: новую банкноту (подделку)
        """
        num = original_banknote.num_photons
        # Создаем поддельную банкноту с таким же серийным номером
        fake = QuantumBanknote(num)
        fake.serial_number = original_banknote.serial_number  # Копируем серийник
        
        print(f"\n👤 Ева пытается скопировать банкноту {original_banknote.serial_number}...")
        
        # Ева не знает поляризации, она измеряет случайными фильтрами
        for i in range(num):
            # Ева выбирает случайный фильтр
            eve_filter = random.choice([Polarization.H, Polarization.V, Polarization.D, Polarization.A])
            
            # Измеряет оригинальный фотон
            passed, new_polarization = measure_photon(original_banknote.photons[i], eve_filter)
            
            if passed and new_polarization is not None:
                # Ева записывает то, что увидела (искаженная информация!)
                fake.photons[i] = new_polarization
            else:
                # Фотон заблокирован - Ева не знает, что было, ставит случайное
                fake.photons[i] = random_photon()
            
            # Ева записывает бит, который она "увидела" (по своему базису)
            if passed and new_polarization is not None:
                fake.bits[i] = Polarization.BIT_MAP[new_polarization]
            else:
                fake.bits[i] = random.randint(0, 1)
        
        print(f"   Ева создала подделку (измерено {num} фотонов случайными фильтрами)")
        return fake

# -------------------------------------------------------------------
# 4. ПРОВЕРКА БАНКОМ
# -------------------------------------------------------------------

class Bank:
    """Класс, представляющий банк, который проверяет подлинность"""
    
    @staticmethod
    def verify(banknote, original_photons):
        """
        Проверяет банкноту, используя знание оригинальных поляризаций.
        Возвращает: (подлинна_ли, процент_ошибок)
        """
        print(f"\n🏦 Банк проверяет банкноту {banknote.serial_number}...")
        
        num = len(original_photons)
        correct = 0
        total = 0
        
        for i in range(num):
            original = original_photons[i]
            candidate = banknote.photons[i]
            
            # Банк знает правильный базис и поляризацию
            # Он измеряет фотон фильтром, соответствующим оригиналу
            passed, measured = measure_photon(candidate, original)
            
            # Если фотон прошел через правильный фильтр - это хороший знак
            # Но нужно проверить битовое значение
            if passed and measured is not None:
                # Сравниваем бит, который мы измерили, с ожидаемым
                measured_bit = Polarization.BIT_MAP[measured]
                expected_bit = Polarization.BIT_MAP[original]
                
                if measured_bit == expected_bit:
                    correct += 1
                total += 1
            else:
                # Фотон не прошел - явная ошибка
                total += 1
        
        error_rate = (total - correct) / total if total > 0 else 1.0
        is_authentic = error_rate < 0.15  # Допускаем 15% ошибок из-за квантовых флуктуаций
        
        print(f"   Результат: {correct}/{total} правильных битов")
        print(f"   Ошибок: {error_rate*100:.1f}%")
        print(f"   ВЕРДИКТ: {'✅ ПОДЛИННАЯ' if is_authentic else '❌ ФАЛЬШИВКА'}")
        
        return is_authentic, error_rate

# -------------------------------------------------------------------
# 5. ДЕМОНСТРАЦИЯ РАБОТЫ
# -------------------------------------------------------------------

def demo_quantum_money():
    """Полная демонстрация квантовых денег Визнера"""
    
    print("=" * 60)
    print("        💰 КВАНТОВЫЕ ДЕНЬГИ (Симуляция Визнера) 💰")
    print("=" * 60)
    
    # 1. Банк создает настоящую банкноту
    print("\n🔵 ШАГ 1: Банк эмитирует новую банкноту")
    real_banknote = QuantumBanknote(num_photons = 20)
    real_banknote.print_secret()
    
    # Сохраняем оригинальные фотоны для проверки
    original_photons = real_banknote.photons.copy()
    original_bits = real_banknote.bits.copy()
    
    # 2. Ева пытается подделать
    print("\n🔴 ШАГ 2: Попытка подделки")
    fake_banknote = Eve.copy_banknote(real_banknote)
    fake_banknote.print_secret()
    
    # 3. Банк проверяет подделку
    print("\n🔵 ШАГ 3: Проверка подделки банком")
    is_fake_authentic, fake_error = Bank.verify(fake_banknote, original_photons)
    
    # 4. Для сравнения - банк проверяет настоящую банкноту
    print("\n🔵 ШАГ 4: Контрольная проверка настоящей банкноты")
    is_real_authentic, real_error = Bank.verify(real_banknote, original_photons)
    
    # 5. Итоговый вывод
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Настоящая банкнота: {'✅ ПОДЛИННАЯ' if is_real_authentic else '❌ НЕ ПРОШЛА'}")
    print(f"   Подделка Евы:       {'✅ ПРОШЛА КАК НАСТОЯЩАЯ' if is_fake_authentic else '❌ РАСПОЗНАНА'}")
    print("=" * 60)
    
    # Объяснение принципа неопределенности
    print("\n🔬 ПРИНЦИП НЕОПРЕДЕЛЕННОСТИ В ДЕЙСТВИИ:")
    print("   Ева не знала правильные базисы, поэтому при измерении она")
    print("   меняла поляризацию фотонов. Банк это обнаружил по")
    print("   повышенному проценту ошибок при проверке.")
    print("   Без знания серийного номера (и связанных с ним базисов)")
    print("   подделать банкноту невозможно!")
    print("=" * 60)

# -------------------------------------------------------------------
# 6. ДОПОЛНИТЕЛЬНАЯ ФУНКЦИЯ: СТАТИСТИЧЕСКИЙ ЭКСПЕРИМЕНТ
# -------------------------------------------------------------------

def statistical_experiment(num_trials = 100):
    """
    Проводит множество экспериментов для демонстрации статистики
    """
    print("\n" + "=" * 60)
    print(f"📊 СТАТИСТИЧЕСКИЙ ЭКСПЕРИМЕНТ ({num_trials} попыток подделки)")
    print("=" * 60)
    
    success_count = 0
    errors = []
    
    for trial in range(num_trials):
        # Создаем банкноту
        real = QuantumBanknote(num_photons = 20)
        original = real.photons.copy()
        
        # Ева пытается подделать
        fake = Eve.copy_banknote(real)
        
        # Банк проверяет
        is_authentic, error = Bank.verify(fake, original)
        
        if is_authentic:
            success_count += 1
            errors.append(error)
    
    success_rate = success_count / num_trials * 100
    avg_error = sum(errors) / len(errors) if errors else 0
    
    print(f"\n📈 Результаты эксперимента:")
    print(f"   Успешных подделок (прошли проверку): {success_count} / {num_trials}")
    print(f"   Процент успеха: {success_rate:.1f}%")
    print(f"   Средняя ошибка у успешных подделок: {avg_error * 100:.1f}%")
    print("\n   💡 Вывод: Ева НЕ может систематически подделывать банкноты,")
    print("      так как ошибки возникают из-за квантовых измерений.")
    print("      Даже если одна подделка случайно прошла (в редких случаях),")
    print("      банк заметит это по статистике при массовой эмиссии.")
    print("=" * 60)

# -------------------------------------------------------------------
# 7. ЗАПУСК
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Запускаем основную демонстрацию
    demo_quantum_money()
    
    # Запускаем статистический эксперимент (можно закомментировать для скорости)
    print("\n")
    statistical_experiment(num_trials = 50)