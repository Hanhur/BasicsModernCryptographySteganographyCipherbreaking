# 1. Общие сведения
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Крипто-Анализатор продукта
Основан на тексте о проблемах выбора криптографических средств защиты.
Использует эвристики Брюса Шнайера и проверку на известные уязвимости.
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple

class CryptoProductAnalyzer:
    """
    Анализатор криптографических продуктов по критериям надёжности.
    """
    
    def __init__(self):
        # База известных уязвимостей (имитация реальных примеров из текста)
        self.vulnerability_db = {
            "pgp_old": {
                "product": "PGP (версии до 8.0)",
                "vulnerability": "Уязвимость в генерации случайных чисел на Windows",
                "year": 2002,
                "severity": "Высокая"
            },
            "debian_openssl": {
                "product": "OpenSSL (Debian)",
                "vulnerability": "Предсказуемые ключи из-за ошибки в энтропии",
                "year": 2008,
                "severity": "Критическая"
            },
            "heartbleed": {
                "product": "OpenSSL (Heartbleed)",
                "vulnerability": "Чтение памяти сервера через heartbeat",
                "year": 2014,
                "severity": "Критическая"
            },
            "dual_ec_drbg": {
                "product": "Dual_EC_DRBG (RSA)",
                "vulnerability": "Потенциальная закладка от АНБ",
                "year": 2013,
                "severity": "Высокая"
            }
        }
        
        # Критерии оценки по Шнайеру (афоризмы в виде правил)
        self.schneier_rules = {
            "security_through_obscurity": {
                "question": "Продукт держит алгоритм в секрете?",
                "weight": -10,
                "comment": "Шнайер: 'Секретность алгоритма — не защита, а слабость'"
            },
            "proprietary_crypto": {
                "question": "Использует ли продукт собственный 'уникальный' алгоритм?",
                "weight": -8,
                "comment": "Шнайер: 'Не изобретай свою криптографию'"
            },
            "no_independent_audit": {
                "question": "Был ли проведён независимый аудит кода?",
                "weight": -7,
                "comment": "Шнайер: 'Только то, что открыто, может быть проверено'"
            },
            "marketing_over_tech": {
                "question": "Реклама обещает 'абсолютную' или 'военную' защиту?",
                "weight": -6,
                "comment": "Шнайер: 'Если система обещает больше, чем может дать — это обман'"
            },
            "old_standard_used": {
                "question": "Использует ли продукт устаревшие стандарты (MD5, DES, RC4)?",
                "weight": -9,
                "comment": "Шнайер: 'Вчерашняя криптография не защитит от завтрашних атак'"
            },
            "open_source": {
                "question": "Исходный код открыт для публичного просмотра?",
                "weight": +8,
                "comment": "Шнайер: 'Открытость — единственный путь к доверию'"
            },
            "long_public_history": {
                "question": "Продукт используется более 5 лет без серьёзных взломов?",
                "weight": +5,
                "comment": "Шнайер: 'Время — лучший тест на прочность'"
            },
            "standard_approved": {
                "question": "Алгоритм утверждён открытым стандартом (AES, ChaCha20, ECDH)?",
                "weight": +6,
                "comment": "Шнайер: 'Стандарты — это коллективный разум'"
            }
        }
    
    def assess_product(self, product_data: Dict[str, any]) -> Dict[str, any]:
        """
        Основной метод оценки продукта.
        Принимает словарь с описанием продукта.
        Возвращает полный отчёт.
        """
        report = {
            "product_name": product_data.get("name", "Неизвестно"),
            "assessment_date": datetime.now().isoformat(),
            "score": 0,
            "max_score": 0,
            "red_flags": [],
            "green_flags": [],
            "known_vulnerabilities": [],
            "schneier_comments": [],
            "verdict": "",
            "recommendation": ""
        }
        
        # 1. Проверка по правилам Шнайера
        for rule_id, rule in self.schneier_rules.items():
            # Получаем ответ от пользователя или из данных
            answer = product_data.get(rule_id, None)
            if answer is None:
                continue  # пропускаем, если нет данных
                
            if isinstance(answer, bool):
                if answer and rule["weight"] < 0:
                    report["red_flags"].append(rule["question"])
                    report["schneier_comments"].append(rule["comment"])
                elif not answer and rule["weight"] > 0:
                    report["red_flags"].append(rule["question"])
                    report["schneier_comments"].append(rule["comment"])
                elif answer and rule["weight"] > 0:
                    report["green_flags"].append(rule["question"])
                
                report["score"] += rule["weight"] if answer else 0
                report["max_score"] += abs(rule["weight"])
        
        # 2. Проверка на известные уязвимости (по имени продукта)
        product_name_lower = product_data.get("name", "").lower()
        for vuln_id, vuln in self.vulnerability_db.items():
            if vuln["product"].lower() in product_name_lower or \
               product_name_lower in vuln["product"].lower():
                report["known_vulnerabilities"].append(vuln)
                report["red_flags"].append(f"Историческая уязвимость: {vuln['vulnerability']}")
                report["score"] -= 15  # штраф за наличие известной уязвимости
        
        # 3. Нормализация оценки (в процентах)
        if report["max_score"] > 0:
            normalized = (report["score"] / report["max_score"]) * 100
        else:
            normalized = 0
        
        # 4. Вердикт
        if normalized >= 70:
            report["verdict"] = "✅ Надёжный продукт"
            report["recommendation"] = "Рекомендуется к использованию при соблюдении всех обновлений."
        elif 40 <= normalized < 70:
            report["verdict"] = "⚠️ Требует осторожности"
            report["recommendation"] = "Использовать только для нечувствительных данных, провести независимый аудит."
        else:
            report["verdict"] = "❌ Ненадёжный/опасный продукт"
            report["recommendation"] = "Категорически не рекомендуется. Вероятны закладки или критические ошибки."
        
        report["score_percent"] = round(normalized, 2)
        
        return report

    def interactive_mode(self):
        """
        Интерактивный режим для опроса пользователя о продукте.
        """
        print("\n" + "=" * 60)
        print("🔐 КРИПТО-АНАЛИЗАТОР ПРОДУКТА (по мотивам текста)")
        print("=" * 60)
        print("\nОтвечайте 'да' (y) или 'нет' (n) на вопросы.")
        print("Это имитация применения афоризмов Брюса Шнайера.\n")
        
        product_name = input("Название продукта: ").strip()
        product_data = {"name": product_name}
        
        for rule_id, rule in self.schneier_rules.items():
            while True:
                answer = input(f"\n{rule['question']} (y/n): ").lower().strip()
                if answer in ('y', 'yes', 'да', '1', 'true'):
                    product_data[rule_id] = True
                    break
                elif answer in ('n', 'no', 'нет', '0', 'false'):
                    product_data[rule_id] = False
                    break
                else:
                    print("Ответьте 'y' или 'n'")
        
        # Запускаем анализ
        report = self.assess_product(product_data)
        self.print_report(report)
        
        return report

    def print_report(self, report: Dict[str, any]):
        """
        Красиво выводит отчёт.
        """
        print("\n" + "=" * 60)
        print(f"📋 ОТЧЁТ ПО ПРОДУКТУ: {report['product_name']}")
        print("=" * 60)
        
        print(f"\n📅 Дата оценки: {report['assessment_date']}")
        print(f"📊 Оценка: {report['score']} / {report['max_score']} баллов")
        print(f"📈 Нормализовано: {report['score_percent']}%")
        
        print(f"\n⚖️ Вердикт: {report['verdict']}")
        print(f"💡 Рекомендация: {report['recommendation']}")
        
        if report["green_flags"]:
            print("\n✅ Плюсы (зелёные флаги):")
            for flag in report["green_flags"]:
                print(f"  + {flag}")
        
        if report["red_flags"]:
            print("\n❌ Минусы (красные флаги):")
            for flag in report["red_flags"]:
                print(f"  - {flag}")
        
        if report["known_vulnerabilities"]:
            print("\n🛑 ИЗВЕСТНЫЕ УЯЗВИМОСТИ (из базы):")
            for vuln in report["known_vulnerabilities"]:
                print(f"  • {vuln['product']}: {vuln['vulnerability']} ({vuln['year']}) - {vuln['severity']}")
        
        if report["schneier_comments"]:
            print("\n📖 Цитаты Шнайера, применимые к этому продукту:")
            for comment in set(report["schneier_comments"]):
                print(f"  \"{comment}\"")
        
        print("\n" + "=" * 60)
        print("🔔 Помните: даже хороший продукт требует правильного использования!")
        print("=" * 60 + "\n")


# ============== Примеры использования ==============

def example_good_product():
    """Пример оценки хорошего продукта (гипотетического)."""
    print("\n" + "📌 ПРИМЕР: Оценка надёжного продукта (AES-256 с открытым кодом)")
    
    product = {
        "name": "ModernCryptoLib v3.0 (Open Source)",
        "security_through_obscurity": False,      # алгоритм открыт
        "proprietary_crypto": False,              # не изобретал своё
        "no_independent_audit": False,            # аудит был
        "marketing_over_tech": False,             # скромная реклама
        "old_standard_used": False,               # современные алгоритмы
        "open_source": True,                      # открытый код
        "long_public_history": True,              # используется 6 лет
        "standard_approved": True                 # AES утверждён
    }
    
    analyzer = CryptoProductAnalyzer()
    report = analyzer.assess_product(product)
    analyzer.print_report(report)


def example_bad_product():
    """Пример оценки плохого продукта."""
    print("\n" + "📌 ПРИМЕР: Оценка опасного продукта (закрытый код, свой алгоритм)")
    
    product = {
        "name": "SuperSecurePro (проприетарный)",
        "security_through_obscurity": True,
        "proprietary_crypto": True,
        "no_independent_audit": True,
        "marketing_over_tech": True,
        "old_standard_used": True,
        "open_source": False,
        "long_public_history": False,
        "standard_approved": False
    }
    
    analyzer = CryptoProductAnalyzer()
    report = analyzer.assess_product(product)
    analyzer.print_report(report)


def example_pgp_legacy():
    """Пример оценки старой версии PGP (как в тексте)."""
    print("\n" + "📌 ПРИМЕР: Оценка старой версии PGP (из упоминания в тексте)")
    
    product = {
        "name": "PGP 7.0 (legacy)",
        "security_through_obscurity": False,      # алгоритмы открыты
        "proprietary_crypto": False,              # использует стандарты
        "no_independent_audit": False,            # был аудит
        "marketing_over_tech": False,             # адекватная реклама
        "old_standard_used": True,                # использует старые версии
        "open_source": False,                     # был проприетарным
        "long_public_history": True,              # долго использовался
        "standard_approved": True                 # но стандарты старые
    }
    
    analyzer = CryptoProductAnalyzer()
    report = analyzer.assess_product(product)
    analyzer.print_report(report)


# ============== Запуск ==============

if __name__ == "__main__":
    print("\n🔐 КРИПТОГРАФИЧЕСКИЙ АНАЛИЗАТОР")
    print("Основан на тексте о проблемах выбора средств защиты.")
    print("Использует эвристики Брюса Шнайера и базу известных уязвимостей.\n")
    
    print("Выберите режим:")
    print("  1 — Интерактивный опрос (введите данные о продукте)")
    print("  2 — Пример хорошего продукта")
    print("  3 — Пример плохого продукта")
    print("  4 — Пример старой версии PGP")
    print("  5 — Запустить все примеры")
    
    choice = input("\nВаш выбор (1-5): ").strip()
    
    analyzer = CryptoProductAnalyzer()
    
    if choice == "1":
        analyzer.interactive_mode()
    elif choice == "2":
        example_good_product()
    elif choice == "3":
        example_bad_product()
    elif choice == "4":
        example_pgp_legacy()
    elif choice == "5":
        example_good_product()
        example_bad_product()
        example_pgp_legacy()
    else:
        print("Неверный выбор. Запускаем интерактивный режим.")
        analyzer.interactive_mode()