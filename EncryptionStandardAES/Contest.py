# 1. Конкурс 
"""
AES Competition Simulator
Программа, визуализирующая информацию о конкурсе AES (1997-2000)
на основе исторических данных.
"""

import time
import random
from typing import Dict, List, Tuple
from datetime import datetime


class AESCompetition:
    """Класс, представляющий конкурс AES и его участников"""
    
    def __init__(self):
        self.finalists = {
            "MARS": {
                "country": "США",
                "developers": "IBM (Coppersmith)",
                "year": 1999,
                "speed": 7.5,  # относительная скорость (чем выше, тем быстрее)
                "memory_ram": 512,
                "memory_rom": 4096,
                "features": ["Аппаратная оптимизация", "Сложная структура"],
                "security_rank": 4
            },
            "TWOFISH": {
                "country": "США",
                "developers": "Schneier et al.",
                "year": 1998,
                "speed": 8.2,
                "memory_ram": 384,
                "memory_rom": 2048,
                "features": ["Основан на BLOWFISH", "Быстрый на 32-бит"],
                "security_rank": 3
            },
            "RC6": {
                "country": "США",
                "developers": "RSA-lab (Rivest)",
                "year": 1998,
                "speed": 9.0,
                "memory_ram": 256,
                "memory_rom": 1024,
                "features": ["Простота реализации", "Высокая скорость"],
                "security_rank": 4
            },
            "RIJNDAEL": {
                "country": "Бельгия",
                "developers": "Daemen, Rijmen",
                "year": 1998,
                "speed": 8.5,
                "memory_ram": 256,
                "memory_rom": 2000,
                "features": ["SP-сеть", "Элегантная математика", "Победитель!"],
                "security_rank": 5,
                "winner": True
            },
            "SERPENT": {
                "country": "Великобритания/Израиль/Норвегия",
                "developers": "Anderson, Biham, Knudsen",
                "year": 1998,
                "speed": 6.0,
                "memory_ram": 768,
                "memory_rom": 4096,
                "features": ["Максимальная безопасность", "32 раунда"],
                "security_rank": 5
            }
        }
        
        self.des_info = {
            "year": 1974,
            "key_length": 56,
            "block_size": 64,
            "rounds": 16,
            "status": "Устарел, но выдержал 30+ лет криптоанализа"
        }
        
        self.aes_info = {
            "year": 2000,
            "key_lengths": [128, 192, 256],
            "block_size": 128,
            "rounds": {128: 10, 192: 12, 256: 14},
            "status": "Действующий стандарт",
            "total_candidates": 15,
            "countries": 12
        }
    
    def print_header(self, title: str, char: str = "=", width: int = 70):
        """Печать красиво оформленного заголовка"""
        print("\n" + char * width)
        print(f"{title.center(width)}")
        print(char * width + "\n")
    
    def show_history(self):
        """Отображение исторической справки"""
        self.print_header("ИСТОРИЯ КОНКУРСА AES", "=")
        
        print("📅 1974 год - Создан DES (56-битный ключ)")
        print("   → Слабые стороны: малая длина ключа, неудобство реализации\n")
        
        print("📅 1997 год - NIST объявляет конкурс на новый стандарт")
        print(f"   → Участников: {self.aes_info['total_candidates']} проектов из {self.aes_info['countries']} стран\n")
        
        print("📅 1998-1999 - Отбор финалистов (5 проектов):")
        for name, info in self.finalists.items():
            winner_mark = "🏆 " if info.get("winner") else "   "
            print(f"   {winner_mark}{name} ({info['country']}) - {info['developers']}")
        
        print("\n📅 2000 год - Победитель: RIJNDAEL (Бельгия)")
        print("   → Стандарт AES утвержден и действует до сих пор\n")
        
        print("💡 Ключевые требования NIST:")
        print("   • Открытость публикации")
        print("   • Симметричный блочный шифр (ключи 128/192/256 бит)")
        print("   • Аппаратная и программная реализация")
        print("   • Незапатентованность")
        print("   • Работа на смарт-картах (256 байт RAM, 2000 байт ROM)")
    
    def show_finalists_comparison(self):
        """Сравнительная таблица финалистов"""
        self.print_header("СРАВНЕНИЕ ФИНАЛИСТОВ", "-")
        
        print(f"{'Алгоритм':<12} {'Страна':<18} {'Скорость':<10} {'RAM (байт)':<12} {'Безопасность':<12}")
        print("-" * 70)
        
        for name, info in sorted(self.finalists.items(), key = lambda x: x[1]['speed'], reverse = True):
            winner_star = "★" if info.get("winner") else " "
            print(f"{name:<12} {info['country']:<18} " f"{info['speed']:<10.1f} {info['memory_ram']:<12} " f"{'⭐' * info['security_rank']:<12}")
        
        print("\n📊 Легенда:")
        print("   ★ - Победитель конкурса")
        print("   ⭐ - Относительная оценка безопасности (макс. 5)")
        print("   Скорость - относительная производительность (макс. 10)")
    
    def show_des_vs_aes(self):
        """Сравнение DES и AES"""
        self.print_header("DES vs AES: ЭВОЛЮЦИЯ СТАНДАРТОВ", "=")
        
        print(f"{'Параметр':<20} {'DES (1974)':<25} {'AES (2000)':<25}")
        print("-" * 70)
        
        print(f"{'Размер ключа':<20} {self.des_info['key_length']:>4} бит {'':<21} " f"{'128/192/256 бит':<25}")
        print(f"{'Размер блока':<20} {self.des_info['block_size']:>4} бит {'':<21} " f"{self.aes_info['block_size']:>4} бит")
        print(f"{'Раундов':<20} {self.des_info['rounds']:>4} {'':<21} " f"{'10/12/14 (зависит от ключа)':<25}")
        print(f"{'Структура':<20} {'Сеть Фейстеля':<25} {'SP-сеть':<25}")
        print(f"{'Статус':<20} {self.des_info['status']:<25} " f"{self.aes_info['status']:<25}")
        
        print("\n💡 Основная слабость DES:")
        print("   • 56-битный ключ → уязвим к полному перебору")
        print("   • Современные компьютеры взламывают DES за секунды\n")
        
        print("💪 Преимущества AES:")
        print("   • Математически обоснованная SP-сеть")
        print("   • Высокая скорость на всех платформах")
        print("   • Аппаратная поддержка (AES-NI в процессорах)")
        print("   • 25+ лет без практических атак")
    
    def visualize_speed(self):
        """Визуализация скорости шифрования в виде столбчатой диаграммы"""
        self.print_header("ВИЗУАЛИЗАЦИЯ СКОРОСТИ ШИФРОВАНИЯ", "-")
        
        max_speed = max(info['speed'] for info in self.finalists.values())
        
        print("Относительная скорость (чем шире столбец, тем быстрее):\n")
        
        sorted_algorithms = sorted(self.finalists.items(), key = lambda x: x[1]['speed'], reverse = True)
        
        for name, info in sorted_algorithms:
            bar_length = int((info['speed'] / max_speed) * 30)
            bar = "█" * bar_length
            winner = " 🏆" if info.get("winner") else ""
            print(f"{name:<12} {bar:.<32} {info['speed']:.1f}/10{winner}")
        
        print("\n📌 RIJNDAEL - идеальный баланс скорости и безопасности!")
    
    def simulate_encryption(self):
        """Симуляция процесса шифрования для демонстрации"""
        self.print_header("ДЕМОНСТРАЦИЯ ШИФРОВАНИЯ AES", "=")
        
        print("🔐 Симуляция процесса шифрования AES-128\n")
        
        # Генерируем случайные данные
        plaintext = "Привет, мир! Это тестовое сообщение для AES."
        key = "AES_KEY_2026_128"
        
        print(f"📝 Исходный текст: {plaintext}")
        print(f"🔑 Ключ: {key}\n")
        
        print("Шаги шифрования:")
        steps = [
            ("1. AddRoundKey", "Наложение ключа на блок данных (XOR)"),
            ("2. SubBytes", "Замена байтов через S-Box (таблица подстановки)"),
            ("3. ShiftRows", "Циклический сдвиг строк в матрице состояния"),
            ("4. MixColumns", "Перемешивание столбцов (умножение в поле Галуа)"),
            ("5. AddRoundKey", "Повторное наложение ключа")
        ]
        
        for i, (step_name, description) in enumerate(steps, 1):
            print(f"   {step_name}: {description}")
            time.sleep(0.3)  # Имитация процесса
        
        print("\n✅ Шифрование завершено!")
        print(f"📦 Зашифрованные данные: {hex(random.randint(0x1000, 0xFFFF))}...")
        print("\n💡 В реальном AES выполняется 10-14 таких раундов")
    
    def interactive_quiz(self):
        """Интерактивная викторина по тексту"""
        self.print_header("ВИКТОРИНА ПО ИСТОРИИ AES", "?")
        
        questions = [
            {
                "question": "Какова длина ключа DES?",
                "options": ["32 бит", "56 бит", "128 бит", "256 бит"],
                "answer": 1
            },
            {
                "question": "Какая страна создала победивший алгоритм RIJNDAEL?",
                "options": ["США", "Бельгия", "Великобритания", "Россия"],
                "answer": 1
            },
            {
                "question": "Сколько проектов участвовало в финальной стадии конкурса?",
                "options": ["5", "10", "15", "25"],
                "answer": 0
            },
            {
                "question": "Какое требование к памяти RAM было у NIST для смарт-карт?",
                "options": ["128 байт", "256 байт", "512 байт", "1024 байт"],
                "answer": 1
            },
            {
                "question": "Какой алгоритм занял 2-е место по безопасности (после Serpent)?",
                "options": ["MARS", "TWOFISH", "RIJNDAEL", "RC6"],
                "answer": 2
            }
        ]
        
        score = 0
        
        for i, q in enumerate(questions, 1):
            print(f"\nВопрос {i}: {q['question']}")
            for j, option in enumerate(q['options']):
                print(f"   {j + 1}. {option}")
            
            try:
                user_answer = int(input("Ваш ответ (номер): ")) - 1
                if user_answer == q['answer']:
                    print("✅ Правильно!")
                    score += 1
                else:
                    print(f"❌ Неправильно. Правильный ответ: {q['options'][q['answer']]}")
            except ValueError:
                print("❌ Пожалуйста, введите число")
            
            time.sleep(0.5)
        
        print(f"\n{'='*50}")
        print(f"🏆 Ваш результат: {score}/{len(questions)}")
        
        if score == len(questions):
            print("🎉 Отлично! Вы эксперт по истории AES!")
        elif score >= 3:
            print("👍 Хорошо! Вы хорошо знаете материал!")
        else:
            print("📚 Рекомендуем перечитать текст еще раз!")
    
    def run_menu(self):
        """Главное меню программы"""
        while True:
            self.print_header("🏛️ AES COMPETITION SIMULATOR", "=")
            print("Добро пожаловать в программу о конкурсе AES (1997-2000)!")
            print("\nВыберите раздел:")
            print("  1. 📜 История конкурса")
            print("  2. 📊 Сравнение финалистов")
            print("  3. ⚡ DES vs AES")
            print("  4. 📈 Визуализация скорости")
            print("  5. 🔐 Демонстрация шифрования")
            print("  6. ❓ Викторина")
            print("  7. 🚪 Выход")
            
            choice = input("\nВаш выбор (1-7): ").strip()
            
            if choice == "1":
                self.show_history()
            elif choice == "2":
                self.show_finalists_comparison()
            elif choice == "3":
                self.show_des_vs_aes()
            elif choice == "4":
                self.visualize_speed()
            elif choice == "5":
                self.simulate_encryption()
            elif choice == "6":
                self.interactive_quiz()
            elif choice == "7":
                print("\n👋 До свидания! Спасибо за использование программы!")
                break
            else:
                print("\n❌ Неверный выбор. Пожалуйста, выберите от 1 до 7.")
            
            input("\nНажмите Enter для продолжения...")


def main():
    """Главная функция"""
    app = AESCompetition()
    app.run_menu()


if __name__ == "__main__":
    main()