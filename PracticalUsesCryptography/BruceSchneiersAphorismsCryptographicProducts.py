# 3. Афоризмы Брюса Шнайера о криптографической продукции
import re

class CryptoProductAnalyzer:
    """
    Инструмент для анализа криптографической продукции
    на основе афоризмов Брюса Шнайера.
    """

    def __init__(self, product_name, key_length_bits, uses_math = True, algorithm_secret = False, marketing_claims = None):
        self.product_name = product_name
        self.key_length = key_length_bits
        self.uses_math = uses_math
        self.algorithm_secret = algorithm_secret
        self.marketing_claims = marketing_claims if marketing_claims else []
        self.red_flags = []
        self.green_flags = []

    def analyze(self):
        """Запускает полный анализ продукта."""
        print(f"\n--- Анализ продукта: {self.product_name} ---")
        
        self._check_key_length()
        self._check_math_usage()
        self._check_algorithm_secrecy()
        self._check_marketing_buzzwords()
        self._make_verdict()

    def _check_key_length(self):
        """Проверка длины ключа (афоризм про 'ключи нелепой длины')."""
        if self.key_length >= 1_000_000:
            self.red_flags.append("Ключ длиной в миллион бит и более (абсурд, выдает некомпетентность).")
        elif self.key_length > 2048:
            self.red_flags.append("Ключ длиннее 2048 бит в симметричной системе не имеет смысла (полный перебор 256-бит уже запределен).")
        elif self.key_length < 128:
            self.red_flags.append(f"Ключ длиной {self.key_length} бит крайне ненадежен (рекомендуется минимум 128 бит).")
        else:
            self.green_flags.append(f"Длина ключа {self.key_length} бит выглядит разумной.")

    def _check_math_usage(self):
        """Проверка на 'антиматематическое кудахтанье'."""
        if not self.uses_math:
            self.red_flags.append(
                "Заявлено, что шифрование не использует математических алгоритмов. "
                "Это антиматематическое шарлатанство (восстановление данных невозможно? — заблуждение)."
            )
        else:
            self.green_flags.append("Продукт заявляет об использовании математических алгоритмов.")

    def _check_algorithm_secrecy(self):
        """Если разработчик скрывает алгоритм — это плохой признак."""
        if self.algorithm_secret:
            self.red_flags.append(
                "Разработчик скрывает используемые алгоритмы. "
                "По Шнайеру: если алгоритм секретен — продукт, скорее всего, недоброкачественный."
            )
        else:
            self.green_flags.append("Алгоритм открыт (принцип Керкгоффса — доверие к продукции выше).")

    def _check_marketing_buzzwords(self):
        """Поиск псевдонаучного 'кудахтанья' в маркетинговых заявлениях."""
        buzzwords = [
            "инкрементальный сдвиг", "уникальный алгоритм", "собственной разработки",
            "не имеет аналогов", "абсолютная защита", "100%", "невозможно взломать",
            "квантовый", "блокчейн", "искусственный интеллект"
        ]
        
        for claim in self.marketing_claims:
            claim_lower = claim.lower()
            for buzz in buzzwords:
                if buzz in claim_lower:
                    self.red_flags.append(
                        f"Обнаружено маркетинговое 'кудахтанье' в заявлении: "
                        f"«{claim}». Напоминает 'Ханаанский бальзам'."
                    )
                    break
            else:
                # Если шлак не найден, но заявление звучит как обещание всего и сразу
                if "все" in claim_lower or "любой" in claim_lower or "недуг" in claim_lower:
                    self.red_flags.append(f"Слишком общее обещание: «{claim}» — похоже на 'Ханаанский бальзам'.")

    def _make_verdict(self):
        """Выносит вердикт на основе собранных флагов."""
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ АНАЛИЗА:")
        print("=" * 60)
        
        if self.red_flags:
            print("🔴 ОБНАРУЖЕНЫ ПРИЗНАКИ НЕДОБРОКАЧЕСТВЕННОЙ ПРОДУКЦИИ:")
            for i, flag in enumerate(self.red_flags, 1):
                print(f"  {i}. {flag}")
            print("\n💊 ВЕРДИКТ: «ХАНААНСКИЙ БАЛЬЗАМ» — шарлатанство или грубая некомпетентность.")
        else:
            print("🟢 Серьезных нарушений не обнаружено.")
        
        if self.green_flags:
            print("\n🟢 ПОЛОЖИТЕЛЬНЫЕ МОМЕНТЫ:")
            for i, flag in enumerate(self.green_flags, 1):
                print(f"  {i}. {flag}")

        print("\n" + "=" * 60)
        print("Цитата Брюса Шнайера: «Плохая система защиты выглядит точно так же, как и хорошая.»")
        print("Будьте бдительны!")


# ======================================================================
# Примеры тестирования программы на основе текста
# ======================================================================

if __name__ == "__main__":
    # Пример 1: Продукт-шарлатан (как Encryptor 4.0 из текста)
    print("\n" + "=" * 60)
    print("ПРИМЕР 1: ТИПИЧНЫЙ «ХАНААНСКИЙ БАЛЬЗАМ»")
    print("=" * 60)
    
    bad_product = CryptoProductAnalyzer(
        product_name = "Encryptor 4.0",
        key_length_bits = 1_000_000,  # Миллион бит — абсурд!
        uses_math = False,            # Не использует математику — антинаучно
        algorithm_secret = True,      # Скрывают алгоритм
        marketing_claims = [
            "Использует уникальный алгоритм инкрементального сдвига базы собственной разработки.",
            "Так как длина ключа изменяется и механизм не использует математики, восстановление невозможно.",
            "Наша защита избавит вас от всех проблем с безопасностью!"
        ]
    )
    bad_product.analyze()

    # Пример 2: Некомпетентный энтузиаст (хочет как лучше, но не умеет)
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: НЕУМЕЛЫЙ ЭНТУЗИАСТ (ИСКРЕННЕ ВЕРИТ В ПРОДУКТ)")
    print("=" * 60)
    
    naive_product = CryptoProductAnalyzer(
        product_name = "SecureHome 1.0",
        key_length_bits = 512,        # Вроде норм, но для симметричных маловато
        uses_math = True,             # Математику использует
        algorithm_secret = False,     # Алгоритм открыт (хорошо)
        marketing_claims = [
            "Мы реализовали AES, но добавили свой запатентованный модуль для пущей надежности.",
            "Наш продукт защитит любой домашний компьютер."
        ]
    )
    naive_product.analyze()

    # Пример 3: Хороший продукт (гипотетический)
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: ДОБРОКАЧЕСТВЕННАЯ ПРОДУКЦИЯ")
    print("=" * 60)
    
    good_product = CryptoProductAnalyzer(
        product_name = "OpenCrypto Suite",
        key_length_bits = 256,         # Оптимальная длина
        uses_math = True,             # Использует математику
        algorithm_secret = False,     # Открытый алгоритм (AES, ChaCha20)
        marketing_claims = [
            "Использует стандартизированные алгоритмы с открытым кодом.",
            "Проходит независимый аудит безопасности."
        ]
    )
    good_product.analyze()