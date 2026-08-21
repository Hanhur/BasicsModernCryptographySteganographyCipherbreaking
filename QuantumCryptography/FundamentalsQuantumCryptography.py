# Введение в Q-механику и Q-криптографию
import math
import random
import turtle

# ==========================================
# 1. СИМУЛЯЦИЯ ЭКСПЕРИМЕНТА С ДВУМЯ ЩЕЛЯМИ
# ==========================================

class DoubleSlitExperiment:
    """
    Симуляция знаменитого эксперимента Юнга.
    Моделирует поведение частиц (классических и квантовых)
    и эффект наблюдателя.
    """
    
    def __init__(self, num_particles = 500, screen_width = 800, screen_height = 600):
        self.num_particles = num_particles
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Параметры щелей (две вертикальные щели)
        self.slit_width = 20          # ширина каждой щели
        self.slit_height = 200        # высота щелей
        self.slit_gap = 80            # расстояние между центрами щелей
        self.slit_x = -150            # позиция экрана со щелями по X
        
        # Параметры экрана (где появляются полосы)
        self.screen_x = 200           # позиция финального экрана по X
        
        # Результаты попаданий
        self.hits = []                # список y-координат попаданий
        
        # Настройка turtle
        self.setup_turtle()
        
    def setup_turtle(self):
        """Инициализация графического окна"""
        self.window = turtle.Screen()
        self.window.title("Квантовый эксперимент с двумя щелями")
        self.window.bgcolor("black")
        self.window.setup(width = self.screen_width, height = self.screen_height)
        self.window.tracer(0)  # отключаем анимацию для скорости
        
        # Создаем черепашку для рисования
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.penup()
        self.pen.hideturtle()
        
        # Рисуем начальную сцену
        self.draw_scene()
        
    def draw_scene(self):
        """Рисует экран со щелями и финальный экран"""
        self.pen.color("white")  # "white" - стандартное имя
        self.pen.pensize(2)
        
        # Рисуем барьер со щелями
        self.pen.goto(self.slit_x, -self.screen_height // 2 + 50)
        self.pen.pendown()
        self.pen.goto(self.slit_x, self.screen_height // 2 - 50)
        self.pen.penup()
        
        # Рисуем верхнюю щель
        self.pen.goto(self.slit_x, self.slit_gap // 2 + self.slit_height // 2)
        self.pen.pendown()
        self.pen.goto(self.slit_x, self.slit_gap // 2 - self.slit_height // 2)
        self.pen.penup()
        
        # Рисуем нижнюю щель
        self.pen.goto(self.slit_x, -self.slit_gap // 2 + self.slit_height // 2)
        self.pen.pendown()
        self.pen.goto(self.slit_x, -self.slit_gap // 2 - self.slit_height // 2)
        self.pen.penup()
        
        # Рисуем финальный экран (справа)
        self.pen.goto(self.screen_x, -self.screen_height // 2 + 50)
        self.pen.pendown()
        self.pen.goto(self.screen_x, self.screen_height // 2 - 50)
        self.pen.penup()
        
        # Подписи
        self.pen.color("#888888")  # серый (HEX)
        self.pen.goto(self.slit_x - 80, self.screen_height // 2 - 30)
        self.pen.write("Барьер со щелями", align = "center", font = ("Arial", 10, "normal"))
        
        self.pen.goto(self.screen_x + 60, self.screen_height // 2 - 30)
        self.pen.write("Экран", align = "center", font = ("Arial", 10, "normal"))
        
        self.window.update()
        
    def shoot_particle_classical(self):
        """
        Классическая частица (пуля).
        Проходит строго через одну щель, летит прямо.
        """
        # Выбираем случайную щель (верхнюю или нижнюю)
        slit_center = random.choice([-self.slit_gap // 2, self.slit_gap // 2])
        
        # Небольшое случайное отклонение в пределах щели
        y_offset = random.uniform(-self.slit_height // 2, self.slit_height // 2)
        y = slit_center + y_offset
        
        # Частица летит прямо до экрана
        # На экране она попадает примерно на ту же высоту
        self.hits.append(y)
        
    def shoot_particle_quantum(self, with_observer = False):
        """
        Квантовая частица (фотон).
        - Без наблюдения: проявляет волновые свойства (интерференция).
        - С наблюдением: ведет себя как частица (2 полосы).
        """
        if with_observer:
            # Если мы наблюдаем (детекторы у щелей) - частица выбирает одну щель
            # Поведение как у классической частицы
            slit_center = random.choice([-self.slit_gap // 2, self.slit_gap // 2])
            y_offset = random.uniform(-self.slit_height // 2, self.slit_height // 2)
            y = slit_center + y_offset
            self.hits.append(y)
        else:
            # БЕЗ наблюдения: квантовая интерференция
            # Фотон проходит через ОБЕ щели одновременно (суперпозиция)
            
            # Параметры для интерференции
            d = self.slit_gap  # расстояние между щелями
            L = self.screen_x - self.slit_x  # расстояние до экрана
            wavelength = 30  # длина волны (подобрана для красивой картинки)
            
            # Пробуем сгенерировать точки с нужным распределением
            max_attempts = 1000
            for _ in range(max_attempts):
                # Случайная точка на экране
                y_test = random.uniform(-self.screen_height // 2 + 50, self.screen_height // 2 - 50)
                
                # Вычисляем интенсивность в этой точке (интерференционная формула)
                # I(y) = cos²(π * d * y / (λ * L))
                
                # Разность фаз
                delta_phi = 2 * math.pi * d * y_test / (wavelength * L)
                interference = math.cos(delta_phi / 2) ** 2
                
                # Дифракционная огибающая (от каждой щели) - делаем более плавной
                diffraction = math.exp(-(y_test ** 2) / (2 * (self.slit_height / 2) ** 2))
                
                # Итоговая вероятность
                probability = interference * diffraction * 1.5
                
                # Ограничиваем вероятность
                if probability > 1.0:
                    probability = 1.0
                
                # Метод принятия-отказа
                if random.random() < probability:
                    self.hits.append(y_test)
                    return
            
            # Если не удалось сгенерировать, добавляем случайную точку
            self.hits.append(random.uniform(-200, 200))
    
    def run_experiment(self, mode = "quantum", with_observer = False):
        """
        Запуск эксперимента.
        mode: "classical" или "quantum"
        with_observer: True/False (для квантового режима)
        """
        self.hits = []  # очищаем предыдущие результаты
        
        # Запускаем частицы
        for i in range(self.num_particles):
            if mode == "classical":
                self.shoot_particle_classical()
            else:  # quantum
                self.shoot_particle_quantum(with_observer)
            
            # Обновляем экран каждые 10 частиц
            if i % 10 == 0:
                self.draw_hits()
        
        # Финальный показ
        self.draw_hits()
        self.show_statistics(mode, with_observer)
        
    def draw_hits(self):
        """Отрисовывает попадания на экране"""
        # Используем #00FFFF (голубой) вместо "cyan"
        self.pen.color("#00FFFF")
        self.pen.pensize(3)
        
        # Ограничиваем количество отображаемых точек для скорости
        max_display = min(len(self.hits), 2000)
        step = max(1, len(self.hits) // max_display)
        
        # Рисуем точки на финальном экране
        for i in range(0, len(self.hits), step):
            y = self.hits[i]
            # Проверяем, что точка попадает в экран
            if -self.screen_height // 2 + 50 < y < self.screen_height // 2 - 50:
                # Рисуем точку на экране
                self.pen.goto(self.screen_x, y)
                self.pen.dot(3, "#00FFFF")
        
        self.window.update()
    
    def show_statistics(self, mode, with_observer):
        """Показывает статистику эксперимента"""
        self.pen.color("#FFFF00")  # желтый (HEX)
        self.pen.goto(0, -self.screen_height // 2 + 20)
        
        mode_name = "Классические частицы" if mode == "classical" else "Квантовые фотоны"
        observer_text = "С НАБЛЮДЕНИЕМ" if with_observer else "БЕЗ НАБЛЮДЕНИЯ"
        
        if mode == "quantum":
            status = f"{mode_name} | {observer_text} | Частиц: {len(self.hits)}"
        else:
            status = f"{mode_name} | Частиц: {len(self.hits)}"
        
        self.pen.clear()
        self.pen.write(status, align = "center", font = ("Arial", 12, "bold"))
        self.window.update()
    
    def clear_screen(self):
        """Очищает экран для нового эксперимента"""
        self.pen.clear()
        self.pen.penup()
        self.hits = []
        self.draw_scene()
        self.window.update()


# ==========================================
# 2. ИНТЕРАКТИВНАЯ ОБОЛОЧКА
# ==========================================

def print_menu():
    """Выводит меню в консоли"""
    print("\n" + "=" * 60)
    print(" КВАНТОВЫЙ ЭКСПЕРИМЕНТ С ДВУМЯ ЩЕЛЯМИ".center(60))
    print("=" * 60)
    print("\nВыберите режим:")
    print("  1. Классические частицы (пули) → 2 полосы")
    print("  2. Квантовые фотоны БЕЗ наблюдения → интерференция (много полос)")
    print("  3. Квантовые фотоны С наблюдением → 2 полосы (эффект наблюдателя)")
    print("  4. Сравнительный тест (все 3 режима подряд)")
    print("  0. Выход")
    print("\n" + "=" * 60)
    
def run_comparison():
    """Запускает все три режима последовательно"""
    experiment = DoubleSlitExperiment(num_particles = 300)
    
    print("\n▶ Режим 1: Классические частицы...")
    experiment.run_experiment(mode = "classical")
    input("\nНажмите Enter для следующего эксперимента...")
    experiment.clear_screen()
    
    print("\n▶ Режим 2: Квантовые фотоны БЕЗ наблюдения...")
    experiment.run_experiment(mode = "quantum", with_observer = False)
    input("\nНажмите Enter для следующего эксперимента...")
    experiment.clear_screen()
    
    print("\n▶ Режим 3: Квантовые фотоны С наблюдением...")
    experiment.run_experiment(mode = "quantum", with_observer = True)
    input("\nНажмите Enter для выхода...")
    
    experiment.window.bye()

def main():
    """Главная функция"""
    print_menu()
    
    choice = input("Ваш выбор: ")
    
    if choice == "0":
        print("До свидания!")
        return
    
    # Создаем эксперимент
    experiment = DoubleSlitExperiment(num_particles = 500)
    
    if choice == "1":
        print("\nЗапуск: Классические частицы...")
        experiment.run_experiment(mode = "classical")
        
    elif choice == "2":
        print("\nЗапуск: Квантовые фотоны БЕЗ наблюдения...")
        print("(Фотоны проходят через обе щели одновременно!)")
        experiment.run_experiment(mode = "quantum", with_observer = False)
        
    elif choice == "3":
        print("\nЗапуск: Квантовые фотоны С наблюдением...")
        print("(Детекторы у щелей разрушают волновую функцию)")
        experiment.run_experiment(mode = "quantum", with_observer = True)
        
    elif choice == "4":
        run_comparison()
        return
        
    else:
        print("Неверный выбор!")
        return
    
    # Оставляем окно открытым
    print("\nЭксперимент завершен. Закройте графическое окно для выхода.")
    experiment.window.mainloop()

if __name__ == "__main__":
    main()