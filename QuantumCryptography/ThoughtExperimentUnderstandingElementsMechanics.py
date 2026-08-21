# Мысленный эксперимент для понимания элементов Q-механики
import random
import math
import time

class QuantumSimulation:
    """
    Симуляция мысленного эксперимента с двумя щелями
    на основе текста о квантовой механике
    """
    
    def __init__(self):
        self.screen_width = 80
        self.screen_height = 20
        self.slit_position = self.screen_height // 2
        self.photon_state = None  # 0 - левая щель, 1 - правая щель, None - суперпозиция
        
    def clear_screen(self):
        """Очистка консоли"""
        print("\033[2J\033[H", end = "")
    
    def draw_screen(self, hits, mode = "superposition"):
        """
        Отрисовка экрана с результатами попаданий
        hits: список координат попаданий на экран
        mode: "superposition", "collapsed", "classical"
        """
        # Создаем пустой экран
        screen = [[' ' for _ in range(self.screen_width)] for _ in range(self.screen_height)]
        
        # Рисуем стену со щелями
        for y in range(self.screen_height):
            if y == self.slit_position - 2 or y == self.slit_position + 2:
                screen[y][0] = '|'  # Стена
            elif y == self.slit_position - 1 or y == self.slit_position + 1:
                screen[y][0] = ' '  # Щель
            else:
                screen[y][0] = '█'  # Стена
        
        # Рисуем экран (правый край)
        for y in range(self.screen_height):
            screen[y][self.screen_width - 1] = '█'
        
        # Отображаем попадания
        for x, y in hits:
            if 1 <= x < self.screen_width - 1 and 0 <= y < self.screen_height:
                # Чем больше попаданий в точку, тем ярче символ
                if screen[y][x] == ' ':
                    screen[y][x] = '·'
                elif screen[y][x] == '·':
                    screen[y][x] = '*'
                elif screen[y][x] == '*':
                    screen[y][x] = '█'
        
        # Добавляем заголовок
        print("\n" + "="*self.screen_width)
        titles = {
            "superposition": "СУПЕРПОЗИЦИЯ: Две открытые щели (интерференция)",
            "collapsed": "КОЛЛАПС: Наблюдение за частицей (одна щель)",
            "classical": "КЛАССИЧЕСКИЙ МИР: Обычные шарики"
        }
        print(titles.get(mode, "КВАНТОВЫЙ ЭКСПЕРИМЕНТ"))
        print("=" * self.screen_width)
        
        # Выводим экран
        for row in screen:
            print(''.join(row))
        
        print("-"*self.screen_width)
        print(f"Всего попаданий: {len(hits)}")
        print("Нажмите Enter для продолжения...", end = "", flush = True)
    
    def slit_experiment(self, num_photons = 200, mode = "superposition", observe = False):
        """
        Основной эксперимент с двумя щелями
        
        num_photons: количество фотонов
        mode: "superposition" - обе щели открыты, 
              "collapsed" - наблюдение за щелями,
              "classical" - классические шарики
        observe: если True, детекторы фиксируют щель
        """
        hits = []
        photons_through_left = 0
        photons_through_right = 0
        
        for _ in range(num_photons):
            if mode == "classical":
                # Классический шарик проходит через одну щель
                slit = random.choice([0, 1])  # 0 - левая, 1 - правая
                if slit == 0:
                    photons_through_left += 1
                    # Попадание прямо за левой щелью (с небольшим разбросом)
                    x = self.screen_width // 4 + random.randint(-5, 5)
                    y = self.slit_position - 2 + random.randint(-3, 3)
                else:
                    photons_through_right += 1
                    x = self.screen_width // 4 * 3 + random.randint(-5, 5)
                    y = self.slit_position + 2 + random.randint(-3, 3)
                
                hits.append((min(max(x, 1), self.screen_width - 2), min(max(y, 0), self.screen_height - 1)))
                
            elif observe:
                # Наблюдение: детекторы заставляют выбрать одну щель
                # При измерении частица коллапсирует в одно состояние
                slit = random.choice([0, 1])
                if slit == 0:
                    photons_through_left += 1
                    # Интерференция разрушена - только левая щель
                    x = self.screen_width // 4 + random.randint(-10, 10)
                    y = self.slit_position - 2 + random.randint(-5, 5)
                else:
                    photons_through_right += 1
                    x = self.screen_width // 4 * 3 + random.randint(-10, 10)
                    y = self.slit_position + 2 + random.randint(-5, 5)
                
                hits.append((min(max(x, 1), self.screen_width - 2), min(max(y, 0), self.screen_height - 1)))
                
            else:
                # Суперпозиция: фотон проходит через ОБЕ щели одновременно
                # Квантовая интерференция создает полосатый узор
                
                # Амплитуда вероятности - волна от обеих щелей
                x = random.randint(1, self.screen_width - 2)
                
                # Расстояние от двух щелей до точки на экране
                dist_left = math.sqrt((x - self.screen_width // 4) ** 2 + (self.slit_position - 2) ** 2)
                dist_right = math.sqrt((x - self.screen_width // 4 * 3) ** 2 + (self.slit_position + 2) ** 2)
                
                # Разность хода волн
                path_diff = abs(dist_left - dist_right)
                
                # Условие интерференционного максимума: path_diff = n * lambda
                # Создаем полосы (чем меньше остаток, тем выше вероятность попадания)
                lambda_wave = 3.0  # Длина волны (в пикселях)
                phase = (path_diff % lambda_wave) / lambda_wave
                
                # Вероятность попадания в точку (интерференционная картина)
                probability = (math.cos(phase * 2 * math.pi) + 1) / 2
                
                # Добавляем небольшой шум для реалистичности
                probability = probability * random.uniform(0.8, 1.2)
                probability = min(max(probability, 0), 1)
                
                # Решаем, попадет ли фотон в эту точку
                if random.random() < probability:
                    # Определяем y-координату с интерференционным узором
                    # Полосы по вертикали тоже образуются из-за интерференции
                    y_offset = int((path_diff * 2) % self.screen_height)
                    y = (self.slit_position + y_offset) % self.screen_height
                    hits.append((x, y))
                else:
                    # Фотон не попал в эту точку, пробуем другую
                    # В реальности это моделирует распределение вероятностей
                    pass
        
        return hits, photons_through_left, photons_through_right
    
    def demonstrate_spin(self):
        """
        Демонстрация спина и запутанности
        """
        print("\n" + "=" * 80)
        print("ЭТАП 3: СПИН И ЗАПУТАННОСТЬ")
        print("=" * 80)
        
        # Создаем запутанную пару (синглетное состояние)
        print("\nСоздаем запутанную пару электронов...")
        time.sleep(1)
        
        # В запутанном состоянии спины противоположны
        # Но пока не измерили - оба в суперпозиции
        print("Состояние пары: |↑↓> + |↓↑> (суперпозиция)")
        time.sleep(1)
        
        print("\nИзмеряем спин первого электрона в Калифорнии...")
        time.sleep(1)
        
        # Случайный коллапс
        spin1 = random.choice(['↑', '↓'])
        spin2 = '↓' if spin1 == '↑' else '↑'
        
        print(f"\nРезультат измерения в Калифорнии: {spin1}")
        print(f"Мгновенно! Спин второго электрона в Нью-Джерси: {spin2}")
        
        print("\n" + "!" * 80)
        print("Это происходит быстрее скорости света (жуткое действие на расстоянии)!")
        print("Но информацию передать нельзя - результат случайный.")
        print("!" * 80)
        
        input("\nНажмите Enter для продолжения...")
    
    def run_experiment(self):
        """
        Запуск полного эксперимента
        """
        print("\033[2J\033[H")  # Очистка экрана
        print("=" * 80)
        print("КВАНТОВЫЙ МЫСЛЕННЫЙ ЭКСПЕРИМЕНТ С ДВУМЯ ЩЕЛЯМИ")
        print("=" * 80)
        print("\nЭтот эксперимент демонстрирует:")
        print("1. Суперпозицию - частица в двух состояниях одновременно")
        print("2. Коллапс волновой функции при наблюдении")
        print("3. Спин и квантовую запутанность")
        input("\nНажмите Enter для начала...")
        
        # ЭТАП 1: Суперпозиция (интерференция)
        print("\033[2J\033[H")
        print("ЭТАП 1: Суперпозиция")
        print("-" * 80)
        print("Запускаем фотоны через две открытые щели...")
        print("Фотоны находятся в состоянии суперпозиции |0> + |1>")
        print("Они проходят через ОБЕ щели одновременно!")
        time.sleep(2)
        
        hits, left, right = self.slit_experiment(200, mode = "superposition", observe = False)
        self.draw_screen(hits, mode = "superposition")
        input()
        
        # ЭТАП 2: Наблюдение (коллапс)
        print("\033[2J\033[H")
        print("ЭТАП 2: Принцип неопределенности")
        print("-" * 80)
        print("Ставим детекторы перед каждой щелью...")
        print("Теперь мы пытаемся узнать, через какую щель прошел фотон.")
        time.sleep(2)
        
        hits, left, right = self.slit_experiment(200, mode = "collapsed", observe = True)
        self.draw_screen(hits, mode = "collapsed")
        print(f"\nФотонов через левую щель: {left}")
        print(f"Фотонов через правую щель: {right}")
        print("\nПолосатый узор исчез! Наблюдение разрушило суперпозицию.")
        input()
        
        # ЭТАП 3: Классический мир
        print("\033[2J\033[H")
        print("Сравнение с классической физикой")
        print("-" * 80)
        print("Теперь представим, что это обычные шарики (не фотоны)...")
        time.sleep(2)
        
        hits, left, right = self.slit_experiment(200, mode = "classical", observe = False)
        self.draw_screen(hits, mode = "classical")
        print("\nШарики ведут себя предсказуемо - просто две линии.")
        print("Нет интерференции, нет суперпозиции.")
        input()
        
        # ЭТАП 4: Запутанность
        self.demonstrate_spin()
        
        # Финальный вывод
        print("\033[2J\033[H")
        print("=" * 80)
        print("ВЫВОДЫ ИЗ ЭКСПЕРИМЕНТА")
        print("=" * 80)
        print("""
        1. СУПЕРПОЗИЦИЯ: Квантовые частицы могут существовать 
           в нескольких состояниях одновременно (|0> + |1>).
           
        2. ИЗМЕРЕНИЕ: Наблюдение (взаимодействие с детектором) 
           заставляет частицу выбрать одно состояние - 
           это называется коллапсом волновой функции.
           
        3. ЗАПУТАННОСТЬ: Две частицы могут быть связаны так, 
           что измерение одной мгновенно определяет состояние другой,
           независимо от расстояния между ними.
           
        4. ПРИМЕНЕНИЕ: Эти свойства используются в квантовой 
           криптографии (QKD) для создания абсолютно защищенных 
           каналов связи.
        """)
        print("=" * 80)
        print("\nБог не играет в кости?")
        print("Квантовая механика говорит: 'Играет, и очень хорошо!'")
        print("\nСпасибо за внимание!")


# Запуск симуляции
if __name__ == "__main__":
    sim = QuantumSimulation()
    sim.run_experiment()