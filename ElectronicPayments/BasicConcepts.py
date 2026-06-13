# 1. Основные понятия
"""
Демонстрация криптографических принципов электронных платежей
на основе технологии DigiCash (D. Chaum)

Основные понятия из текста:
- Электронные деньги = информация о реальных средствах
- Купюра защищена слепой подписью банка
- Анонимность + защита от двойной траты
"""

import hashlib
import random
import json
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


class SimpleBlindSignature:
    """
    Упрощенная модель слепой подписи.
    
    В реальной криптографии используется RSA с ослепляющим множителем.
    Здесь мы имитируем принцип: банк подписывает скрытый номер.
    """
    
    def __init__(self, bank_secret_key: str = "BankSecret123"):
        self.bank_secret_key = bank_secret_key
    
    def blind(self, serial_number: str, blinding_factor: int) -> str:
        """Ослепление: покупатель скрывает серийный номер"""
        # В реальности: serial * (r^e) mod n
        blinded = hashlib.sha256(
            f"{serial_number}_{blinding_factor}".encode()
        ).hexdigest()
        return blinded
    
    def sign(self, blinded_data: str) -> str:
        """Банк подписывает ослепленные данные, не видя оригинал"""
        signature = hashlib.sha256(
            f"{blinded_data}_{self.bank_secret_key}".encode()
        ).hexdigest()
        return signature
    
    def unblind(self, signature: str, blinding_factor: int) -> str:
        """Снятие ослепления: покупатель получает подпись на оригинальный номер"""
        # В реальности: signature * (r^{-1}) mod n
        unblinded = hashlib.sha256(
            f"{signature}_{blinding_factor}".encode()
        ).hexdigest()
        return unblinded
    
    def verify(self, serial_number: str, unblinded_signature: str) -> bool:
        """Проверка подписи банка"""
        expected = hashlib.sha256(
            f"{serial_number}_{self.bank_secret_key}".encode()
        ).hexdigest()
        return unblinded_signature == expected


@dataclass
class ElectronicBill:
    """Электронная купюра (из текста: информация о реальных средствах)"""
    serial_number: str      # Уникальный идентификатор
    denomination: int       # Номинал
    bank_signature: str     # Подпись банка (защита от подделки)
    issued_at: str          # Время выпуска
    
    def to_string(self) -> str:
        """Для демонстрации"""
        return f"Купюра {self.serial_number} номиналом {self.denomination}"


class Bank:
    """Эмитент электронных денег (на основе DigiCash)"""
    
    def __init__(self, name: str):
        self.name = name
        self.blind_signer = SimpleBlindSignature(f"{name}_SecretKey")
        self.spent_bills_db: Dict[str, str] = {}  # База потраченных купюр
        self.issued_bills: List[ElectronicBill] = []
        
    def issue_blind_signature(self, blinded_data: str) -> str:
        """
        Банк подписывает ослепленную купюру.
        Не видит серийный номер -> анонимность покупателя
        """
        return self.blind_signer.sign(blinded_data)
    
    def verify_and_accept_bill(self, bill: ElectronicBill, spender_id: str) -> bool:
        """
        Проверка купюры при оплате/погашении
        
        Возвращает:
        - True: купюра валидна и не была потрачена
        - False: подделка или двойная трата
        """
        # 1. Проверка подписи банка (защита от подделки)
        if not self.blind_signer.verify(bill.serial_number, bill.bank_signature):
            print(f"  ОТКЛОНЕНО: Неверная подпись на купюре {bill.serial_number}")
            return False
        
        # 2. Проверка на двойное расходование
        if bill.serial_number in self.spent_bills_db:
            existing_spender = self.spent_bills_db[bill.serial_number]
            print(f"  ОТКЛОНЕНО: Двойная трата купюры {bill.serial_number}!")
            print(f"  Купюра уже была потрачена пользователем: {existing_spender}")
            return False
        
        # 3. Принимаем купюру
        self.spent_bills_db[bill.serial_number] = spender_id
        print(f"  ПРИНЯТО: Купюра {bill.serial_number} на {bill.denomination} руб.")
        return True
    
    def get_statistics(self):
        """Статистика работы банка"""
        print(f"\n--- Статистика банка {self.name} ---")
        print(f"Выпущено купюр: {len(self.issued_bills)}")
        print(f"Погашено купюр: {len(self.spent_bills_db)}")
        print(f"В обращении: {len(self.issued_bills) - len(self.spent_bills_db)}")


class Customer:
    """Пользователь электронных денег (покупатель)"""
    
    def __init__(self, name: str):
        self.name = name
        self.wallet: List[ElectronicBill] = []  # Кошелек с купюрами
        self.spending_history: List[ElectronicBill] = []
    
    def request_bill_from_bank(self, bank: Bank, denomination: int) -> Optional[ElectronicBill]:
        """
        Процесс получения электронной купюры:
        1. Покупатель генерирует серийный номер
        2. Ослепляет его (банк не видит)
        3. Банк подписывает ослепленный номер
        4. Покупатель снимает ослепление -> получает подписанную купюру
        """
        print(f"\n{self.name} запрашивает купюру номиналом {denomination}")
        
        # 1. Генерация уникального серийного номера
        serial = hashlib.sha256(
            f"{self.name}_{random.randint(1, 1000000)}_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # 2. Ослепление (покупатель скрывает номер от банка)
        blinding_factor = random.randint(1, 10000)
        blinded = bank.blind_signer.blind(serial, blinding_factor)
        
        # 3. Банк подписывает вслепую (не знает серийный номер!)
        blinded_signature = bank.issue_blind_signature(blinded)
        
        # 4. Снятие ослепления -> подписанный оригинал
        signature = bank.blind_signer.unblind(blinded_signature, blinding_factor)
        
        # 5. Проверка подписи
        if not bank.blind_signer.verify(serial, signature):
            print("  ОШИБКА: Подпись неверна!")
            return None
        
        # 6. Создание купюры
        bill = ElectronicBill(
            serial_number = serial,
            denomination = denomination,
            bank_signature = signature,
            issued_at = datetime.now().isoformat()
        )
        
        bank.issued_bills.append(bill)
        self.wallet.append(bill)
        print(f"  УСПЕШНО: {self.name} получил купюру {serial} на {denomination} руб.")
        return bill
    
    def pay(self, bank: Bank, amount: int, merchant_name: str) -> bool:
        """
        Оплата покупки.
        Моделирует передачу купюры продавцу и проверку в банке.
        """
        # Находим купюру подходящего номинала
        bill_to_use = None
        for bill in self.wallet:
            if bill.denomination == amount:
                bill_to_use = bill
                break
        
        if not bill_to_use:
            print(f"  {self.name}: нет купюры номиналом {amount}")
            return False
        
        print(f"\n{self.name} платит {amount} руб. в {merchant_name}")
        print(f"  Купюра: {bill_to_use.serial_number}")
        
        # Проверка банком (имитация процессинга платежа)
        if bank.verify_and_accept_bill(bill_to_use, self.name):
            self.wallet.remove(bill_to_use)
            self.spending_history.append(bill_to_use)
            print(f"  ПЛАТЕЖ УСПЕШЕН: {merchant_name} получил {amount} руб.")
            return True
        else:
            print(f"  ПЛАТЕЖ ОТКЛОНЕН: проблема с купюрой")
            return False
    
    def show_wallet(self):
        """Показать кошелек"""
        if not self.wallet:
            print(f"{self.name}: кошелек пуст")
            return
        print(f"\nКошелек {self.name}:")
        for bill in self.wallet:
            print(f"  - {bill.serial_number} : {bill.denomination} руб.")


class Merchant:
    """Продавец (торговая точка)"""
    
    def __init__(self, name: str):
        self.name = name
        self.received_bills: List[ElectronicBill] = []
        self.balance = 0
    
    def accept_payment(self, bill: ElectronicBill, bank: Bank, customer: Customer) -> bool:
        """
        Продавец принимает купюру и отправляет её в банк для проверки
        """
        print(f"  {self.name} проверяет купюру...")
        
        if bank.verify_and_accept_bill(bill, customer.name):
            self.received_bills.append(bill)
            self.balance += bill.denomination
            return True
        return False


def demonstrate_double_spending():
    """Демонстрация защиты от двойного расходования"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ ДВОЙНОГО РАСХОДОВАНИЯ")
    print("=" * 60)
    
    # Создаем новые независимые объекты для этой демонстрации
    bank = Bank("Центробанк")
    alice = Customer("Алиса")
    shop1 = Merchant("Магазин Электроника")
    shop2 = Merchant("Магазин Книги")
    
    # Алиса получает купюру
    bill = alice.request_bill_from_bank(bank, 100)
    
    if bill is None:
        print("Ошибка: не удалось создать купюру")
        return
    
    # Первая покупка (легальная)
    print("\n--- Первая трата купюры ---")
    # Сохраняем купюру в переменную до того, как Алиса ее потратит
    current_bill = alice.wallet[0]  # Теперь здесь точно есть купюра
    
    if shop1.accept_payment(current_bill, bank, alice):
        alice.wallet.remove(current_bill)
        print(f"  Первая трата успешно завершена")
    
    # Попытка потратить ТУ ЖЕ купюру снова
    print("\n--- Вторая трата ТОЙ ЖЕ купюры (двойное расходование!) ---")
    # Алиса пытается отправить ту же купюру во второй магазин
    # Для демонстрации: создаем копию купюры (как если бы Алиса сохранила ее копию)
    fake_bill_copy = ElectronicBill(
        serial_number = current_bill.serial_number,
        denomination = current_bill.denomination,
        bank_signature = current_bill.bank_signature,
        issued_at = current_bill.issued_at
    )
    
    print(f"Алиса пытается повторно использовать купюру {current_bill.serial_number}")
    shop2.accept_payment(fake_bill_copy, bank, alice)
    
    print("\nИТОГ: Вторая попытка траты была отклонена банком!")
    bank.get_statistics()


def demonstrate_anonymity():
    """Демонстрация анонимности: банк не знает, кто получил купюру"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ АНОНИМНОСТИ (СЛЕПАЯ ПОДПИСЬ)")
    print("=" * 60)
    
    bank = Bank("Анонимный Банк")
    alice = Customer("Алиса")
    bob = Customer("Боб")
    
    print("\nБанк подписывает купюры вслепую:")
    print("1. Алиса ослепляет свой серийный номер -> банк видит только хеш")
    print("2. Банк подписывает ослепленные данные")
    print("3. Алиса снимает ослепление -> получает подписанную купюру")
    print("4. Банк не может связать подпись с Алисой")
    
    alice.request_bill_from_bank(bank, 50)
    bob.request_bill_from_bank(bank, 100)
    
    print("\nБанк при погашении видит только серийные номера и подписи")
    print("НО не знает, кому они были выданы!")
    
    # Показываем, что банк не хранит связь между клиентом и серийным номером
    print("\nБаза данных банка содержит:")
    for bill in bank.issued_bills:
        print(f"  - Серийный номер: {bill.serial_number}")
    print("  (но банк не знает, что серийный номер 1 принадлежит Алисе, а номер 2 - Бобу)")


def demonstrate_forgery_protection():
    """Демонстрация защиты от подделки"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАЩИТЫ ОТ ПОДДЕЛКИ")
    print("=" * 60)
    
    bank = Bank("Безопасный Банк")
    alice = Customer("Алиса")
    mallory = Customer("Мэллори")  # Злоумышленник
    shop = Merchant("Магазин")
    
    # Легальная купюра
    real_bill = alice.request_bill_from_bank(bank, 50)
    
    # Попытка подделки: Мэллори создает купюру со случайным номером и фальшивой подписью
    print("\n--- Мэллори пытается подделать купюру ---")
    fake_serial = "FAKE_SERIAL_12345"
    fake_signature = "this_is_not_a_real_signature"
    
    fake_bill = ElectronicBill(
        serial_number = fake_serial,
        denomination = 1000,
        bank_signature = fake_signature,
        issued_at = datetime.now().isoformat()
    )
    
    print(f"Мэллори создал фальшивую купюру на 1000 руб. с серийным номером {fake_serial}")
    shop.accept_payment(fake_bill, bank, mallory)
    
    print("\nИТОГ: Фальшивая купюра была отклонена банком!")
    bank.get_statistics()


def main():
    """Главная демонстрация"""
    print("=" * 60)
    print("КРИПТОГРАФИЧЕСКАЯ ЗАЩИТА ЭЛЕКТРОННЫХ ПЛАТЕЖЕЙ")
    print("На основе технологии DigiCash (D. Chaum)")
    print("=" * 60)
    
    # Инициализация
    bank = Bank("MasterCard Bank")
    alice = Customer("Алиса")
    merchant = Merchant("Онлайн-магазин")
    
    print("\n--- ЭТАП 1: Выпуск электронной купюры ---")
    print("Информация о реальных деньгах превращается в защищенную купюру")
    alice.request_bill_from_bank(bank, 100)
    alice.request_bill_from_bank(bank, 50)
    
    alice.show_wallet()
    
    print("\n--- ЭТАП 2: Оплата покупки ---")
    alice.pay(bank, 100, "Онлайн-магазин")
    
    print("\n--- ЭТАП 3: Проверка банка ---")
    bank.get_statistics()
    
    # Демонстрация защиты от двойной траты
    demonstrate_double_spending()
    
    # Демонстрация анонимности
    demonstrate_anonymity()
    
    # Демонстрация защиты от подделки
    demonstrate_forgery_protection()
    
    print("\n" + "=" * 60)
    print("ВЫВОДЫ (из текста):")
    print("- Электронные деньги = информация, защищенная криптографией")
    print("- Слепая подпись обеспечивает анонимность покупателя")
    print("- База потраченных купюр защищает от двойного расходования")
    print("- Банк не может подделать купюру без секретного ключа")
    print("=" * 60)


if __name__ == "__main__":
    main()