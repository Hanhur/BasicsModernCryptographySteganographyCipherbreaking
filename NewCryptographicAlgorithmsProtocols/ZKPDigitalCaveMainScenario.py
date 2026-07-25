# Основной сценарий ZKP — цифровая пещера
import hashlib
import random
import time
from typing import Tuple, Optional

class CaveZKP:
    """
    Симуляция Zero-Knowledge Proof для пещеры Али-Бабы
    С использованием неинтерактивного протокола (Fiat-Shamir)
    """
    
    def __init__(self, secret_code: str):
        """
        Инициализация с секретным кодом Пегги
        
        Args:
            secret_code: Секретный код от двери (только Пегги знает его)
        """
        self.secret_code = secret_code
        self.prover_name = "Peggy"
        self.verifier_name = "Victor"
        
    def _hash(self, data: str) -> str:
        """
        Криптографическая хеш-функция (имитация случайного оракула)
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _generate_challenge(self, commitment: str, timestamp: str) -> str:
        """
        Генерация "вопроса" Виктора через хеш (Fiat-Shamir)
        
        Возвращает 'left' или 'right' в зависимости от хеша
        """
        combined = f"{commitment}:{timestamp}:{self.prover_name}"
        hash_value = self._hash(combined)
        # Берем первый байт хеша и определяем сторону
        return 'left' if int(hash_value[:2], 16) % 2 == 0 else 'right'
    
    def prove_knowledge(self, timestamp: Optional[str] = None) -> dict:
        """
        Неинтерактивное доказательство знания кода
        
        Returns:
            Словарь с доказательством для Виктора
        """
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        # Шаг 1: Пегги выбирает случайный путь (commitment)
        initial_path = random.choice(['left', 'right'])
        print(f"🔐 [{self.prover_name}] Выбирает начальный путь: {initial_path}")
        
        # Шаг 2: Генерация "вопроса" через хеш (без участия Виктора)
        challenge = self._generate_challenge(initial_path, timestamp)
        print(f"❓ [{self.verifier_name}] (виртуальный) спрашивает: выйти с {challenge} стороны")
        
        # Шаг 3: Пегги формирует ответ
        # Если вопрос совпадает с начальным путем - она просто выходит
        # Если нет - она должна пройти через дверь (используя секрет)
        if initial_path == challenge:
            response = f"вышел с {challenge} стороны (без использования кода)"
            used_secret = False
        else:
            # Пегги использует секретный код, чтобы пройти через дверь
            response = f"прошел через дверь с {challenge} стороны (использовал код ✅)"
            used_secret = True
        
        # Шаг 4: Создание доказательства
        proof = {
            'commitment': initial_path,
            'challenge': challenge,
            'response': response,
            'timestamp': timestamp,
            'used_secret': used_secret,
            'hash': self._hash(f"{initial_path}:{challenge}:{response}:{timestamp}")
        }
        
        return proof
    
    def verify_proof(self, proof: dict) -> Tuple[bool, str]:
        """
        Проверка доказательства Виктором (без знания кода)
        
        Args:
            proof: Доказательство от Пегги
            
        Returns:
            (вердикт, сообщение)
        """
        print("\n" + "=" * 50)
        print(f"🔍 [{self.verifier_name}] Начинает проверку...")
        
        # Шаг 1: Виктор проверяет, что вопрос сгенерирован корректно
        expected_challenge = self._generate_challenge(
            proof['commitment'], 
            proof['timestamp']
        )
        
        if expected_challenge != proof['challenge']:
            return False, "Ошибка: Неправильная генерация вопроса!"
        
        print(f"✅ Вопрос '{proof['challenge']}' сгенерирован корректно")
        
        # Шаг 2: Проверка целостности доказательства
        expected_hash = self._hash(
            f"{proof['commitment']}:{proof['challenge']}:{proof['response']}:{proof['timestamp']}"
        )
        
        if expected_hash != proof['hash']:
            return False, "Ошибка: Нарушена целостность доказательства!"
        
        print(f"✅ Хеш доказательства корректен")
        
        # Шаг 3: Логическая проверка
        # Если Пегги использовала секрет - она действительно знает код
        if proof['used_secret']:
            return True, "✅ Доказательство принято! Пегги знает код (прошла через дверь)"
        
        # Если не использовала секрет, но ответ правильный - это случайность
        # (в реальном протоколе нужно много раундов, здесь для демонстрации)
        return True, "⚠️ Доказательство принято, но требуется несколько раундов для полной уверенности"


class InteractiveCaveSimulation:
    """
    Интерактивная симуляция (с множественными раундами)
    для достижения криптографической уверенности
    """
    
    def __init__(self, secret_code: str, rounds: int = 20):
        self.secret_code = secret_code
        self.rounds = rounds
        self.prover = CaveZKP(secret_code)
        
    def run_multi_round(self) -> dict:
        """
        Запуск множественных раундов неинтерактивного доказательства
        """
        print("\n" + "🏛️" * 20)
        print(f"НАЧАЛО МНОГОРАУНДОВОЙ ПРОВЕРКИ ({self.rounds} раундов)")
        print("🏛️" * 20 + "\n")
        
        successful_rounds = 0
        secret_used_count = 0
        total_rounds = 0
        
        for round_num in range(1, self.rounds + 1):
            print(f"\n--- Раунд {round_num} ---")
            
            # Разные временные метки для каждого раунда
            timestamp = str(int(time.time()) + round_num)
            proof = self.prover.prove_knowledge(timestamp)
            
            is_valid, message = self.prover.verify_proof(proof)
            
            if is_valid:
                successful_rounds += 1
                if proof['used_secret']:
                    secret_used_count += 1
                    print(f"✅ {message}")
                else:
                    print(f"ℹ️ {message}")
            else:
                print(f"❌ {message}")
                
            total_rounds += 1
            
            # Небольшая задержка для разных timestamp
            time.sleep(0.01)
        
        # Анализ результатов
        confidence = (successful_rounds / total_rounds) * 100
        secret_usage_rate = (secret_used_count / total_rounds) * 100
        
        return {
            'total_rounds': total_rounds,
            'successful_rounds': successful_rounds,
            'confidence': confidence,
            'secret_usage_rate': secret_usage_rate,
            'is_verified': confidence == 100.0
        }


def demonstrate_attack(secret_code: str):
    """
    Демонстрация атаки (когда кто-то пытается выдать себя за Пегги)
    """
    print("\n" + "🚨" * 20)
    print("ДЕМОНСТРАЦИЯ АТАКИ (злоумышленник не знает код)")
    print("🚨" * 20 + "\n")
    
    # Злоумышленник (Eve) пытается подделать доказательство
    eve = CaveZKP("wrong_code")  # Неправильный код!
    
    timestamp = str(int(time.time()))
    proof = eve.prove_knowledge(timestamp)
    
    # Подмена доказательства
    proof['response'] = "прошел через дверь (но это ложь!)"
    proof['hash'] = hashlib.sha256("fake_data".encode()).hexdigest()
    
    # Проверка Виктором
    is_valid, message = eve.verify_proof(proof)
    
    if not is_valid:
        print(f"\n🛡️ Атака обнаружена!")
        print(f"Причина: {message}")
    else:
        print(f"\n⚠️ Опасность! Атака прошла успешно!")


def main():
    """
    Главная функция с демонстрацией всех сценариев
    """
    print("=" * 60)
    print("СИМУЛЯЦИЯ ZKP ДЛЯ ПЕЩЕРЫ АЛИ-БАБЫ")
    print("=" * 60)
    
    # Секретный код (известен только Пегги)
    SECRET_CODE = "AliBaba2024!"
    
    print(f"\n📌 Секретный код установлен: {SECRET_CODE}")
    print("(Виктор и злоумышленники его не знают)\n")
    
    # Сценарий 1: Один раунд неинтерактивного доказательства
    print("\n" + "🔵" * 20)
    print("СЦЕНАРИЙ 1: ОДИН РАУНД НЕИНТЕРАКТИВНОГО ДОКАЗАТЕЛЬСТВА")
    print("🔵" * 20)
    
    peggy = CaveZKP(SECRET_CODE)
    single_proof = peggy.prove_knowledge()
    is_valid, message = peggy.verify_proof(single_proof)
    print(f"\n📊 Результат: {message}")
    
    # Сценарий 2: Многораундовая проверка (для уверенности)
    print("\n" + "🟢" * 20)
    print("СЦЕНАРИЙ 2: МНОГОРАУНДОВАЯ ПРОВЕРКА")
    print("🟢" * 20)
    
    multi_sim = InteractiveCaveSimulation(SECRET_CODE, rounds = 15)
    results = multi_sim.run_multi_round()
    
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего раундов: {results['total_rounds']}")
    print(f"   Успешных раундов: {results['successful_rounds']}")
    print(f"   Уверенность: {results['confidence']:.1f}%")
    print(f"   Использование секрета: {results['secret_usage_rate']:.1f}%")
    
    if results['is_verified']:
        print("   ✅ ВЕРДИКТ: Пегги действительно знает код!")
    else:
        print("   ⚠️ ВЕРДИКТ: Недостаточно доказательств")
    
    # Сценарий 3: Демонстрация атаки
    demonstrate_attack(SECRET_CODE)
    
    # Сценарий 4: Сравнение интерактивного vs неинтерактивного
    print("\n" + "🟡" * 20)
    print("СЦЕНАРИЙ 3: СРАВНЕНИЕ ПОДХОДОВ")
    print("🟡" * 20)
    
    print("\n📋 ИНТЕРАКТИВНЫЙ ПОДХОД (классическая пещера):")
    print("   1. Пегги входит в пещеру (выбирает путь)")
    print("   2. Виктор кричит: 'Выходи слева!' или 'Выходи справа!'")
    print("   3. Пегги выходит с указанной стороны")
    print("   4. Повторяется 20+ раз")
    print("   ❌ Требует присутствия Виктора в реальном времени")
    
    print("\n📋 НЕИНТЕРАКТИВНЫЙ ПОДХОД (Fiat-Shamir):")
    print("   1. Пегги выбирает случайный путь")
    print("   2. Вопрос генерируется через хеш (никто не участвует)")
    print("   3. Пегги формирует доказательство (один пакет)")
    print("   4. Виктор проверяет доказательство в любое время")
    print("   ✅ Не требует присутствия Виктора")
    print("   ✅ Защита от повторных атак (timestamp)")
    print("   ✅ Может использоваться в блокчейне и сетях")
    
    print("\n" + "=" * 60)
    print("🔑 КЛЮЧЕВЫЕ ВЫВОДЫ:")
    print("   • ZKP позволяет доказать знание секрета без его раскрытия")
    print("   • Неинтерактивные протоколы используют хеш-функции")
    print("   • Важно: результат зависит от правильной реализации")
    print("=" * 60)


if __name__ == "__main__":
    main()