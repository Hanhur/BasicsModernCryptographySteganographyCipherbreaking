# 3. Технология электронного платежа
import hashlib
import json
from typing import Dict, Optional

class DigitalSignature:
    """Эмуляция электронной подписи (упрощённо — хеш + условный приватный ключ)"""
    @staticmethod
    def sign(data: str, owner: str) -> str:
        # В реальной системе была бы асимметричная криптография
        return hashlib.sha256(f"{data}:{owner}_private_key".encode()).hexdigest()

    @staticmethod
    def verify(data: str, signature: str, owner: str) -> bool:
        expected = DigitalSignature.sign(data, owner)
        return signature == expected


class BankC:
    """Банк-эмитент C"""
    def __init__(self):
        self.accounts = {}          # Счета участников {участник: баланс}
        self.cards_db = {}          # База карт {номер: остаток}
        self.card_owner_map = {}    # В реальной системе может не знать владельца до первого использования

    def open_account(self, owner: str, initial_balance: float):
        self.accounts[owner] = initial_balance

    def issue_card(self, client: str, semi_card: Dict) -> Optional[Dict]:
        """
        Клиент А присылает полуфабрикат карточки с номером и своей подписью.
        Банк С стирает подпись клиента, ставит свою, списывает номинал со счёта А.
        """
        card_number = semi_card["number"]
        nominal = semi_card["nominal"]
        client_signature = semi_card["client_signature"]

        # Проверяем подпись клиента (эмуляция)
        client_data = f"{card_number}:{nominal}"
        if not DigitalSignature.verify(client_data, client_signature, client):
            print("❌ Ошибка: неверная подпись клиента")
            return None

        # Снимаем деньги со счёта клиента
        if self.accounts.get(client, 0) < nominal:
            print("❌ Недостаточно средств на счету клиента")
            return None

        self.accounts[client] -= nominal

        # Стираем подпись клиента (удаляем из карточки) и ставим подпись банка
        bank_signature = DigitalSignature.sign(f"{card_number}:{nominal}", "BankC")

        card = {
            "number": card_number,
            "nominal": nominal,
            "bank_signature": bank_signature
        }

        # Карта выпущена, но банк пока не знает её номер в БД (до первого использования)
        print(f"✅ Карта {card_number} номиналом {nominal} выпущена для {client}")
        return card

    def process_payment(self, card_data: Dict, amount: float, seller: str) -> bool:
        """
        Продавец В проверяет подлинность карточки через С и списывает средства.
        """
        card_number = card_data["number"]
        bank_signature = card_data["bank_signature"]

        # Проверяем подпись банка
        expected_data = f"{card_number}:{card_data['nominal']}"
        if not DigitalSignature.verify(expected_data, bank_signature, "BankC"):
            print("❌ Неверная подпись банка — карта поддельная")
            return False

        # Если карта не зарегистрирована в БД, заносим (первый платёж)
        if card_number not in self.cards_db:
            self.cards_db[card_number] = card_data["nominal"]
            print(f"🔍 Первое использование карты {card_number}, остаток = {self.cards_db[card_number]}")

        current_balance = self.cards_db.get(card_number, 0)
        if amount > current_balance:
            print(f"❌ Недостаточно средств на карте: запрошено {amount}, остаток {current_balance}")
            return False

        # Снимаем с карты, кладём продавцу
        self.cards_db[card_number] -= amount
        self.accounts[seller] = self.accounts.get(seller, 0) + amount

        print(f"💸 Платёж {amount} выполнен. Остаток на карте: {self.cards_db[card_number]}")
        return True

    def get_card_balance(self, card_number: str) -> float:
        return self.cards_db.get(card_number, 0.0)


class ClientA:
    def __init__(self, name: str, bank: BankC):
        self.name = name
        self.bank = bank
        self.card = None

    def request_card(self, nominal: float) -> bool:
        """Создаёт полуфабрикат карты и отправляет в банк"""
        card_number = f"card_{self.name}_{hash(self.name + str(nominal)) % 10000}"
        semi_card = {
            "number": card_number,
            "nominal": nominal,
            "client_signature": DigitalSignature.sign(f"{card_number}:{nominal}", self.name)
        }
        self.card = self.bank.issue_card(self.name, semi_card)
        return self.card is not None

    def pay(self, seller, amount: float) -> bool:
        if not self.card:
            print("У клиента нет карты")
            return False
        return self.bank.process_payment(self.card, amount, seller)


class SellerB:
    def __init__(self, name: str, bank: BankC):
        self.name = name
        self.bank = bank

    def accept_payment(self, client: ClientA, amount: float) -> bool:
        print(f"\n🛒 Продавец {self.name}: запрос платежа {amount} от {client.name}")
        success = client.pay(self.name, amount)
        if success:
            print(f"✅ Товар передан покупателю {client.name}")
        else:
            print("❌ Платёж отклонён, товар не отдан")
        return success

    def show_balance(self):
        print(f"💰 Баланс продавца {self.name}: {self.bank.accounts.get(self.name, 0)}")


# ===================== СИМУЛЯЦИЯ =====================
if __name__ == "__main__":
    # 1. Инициализация банка и участников
    bank = BankC()
    bank.open_account("Alice", 1000)   # Клиент А
    bank.open_account("Bob", 0)        # Продавец В (начальный баланс 0)

    alice = ClientA("Alice", bank)
    bob = SellerB("Bob", bank)

    # 2. Заказ электронной карточки
    print("=== ЭМИССИЯ КАРТЫ ===")
    if alice.request_card(500):
        print("Карта успешно получена клиентом")
    else:
        print("Ошибка эмиссии")

    print(f"Баланс Алисы в банке после эмиссии: {bank.accounts['Alice']}")  # 500

    # 3. Платёж в онлайн-режиме
    print("\n=== ПЛАТЁЖ ===")
    bob.accept_payment(alice, 120)   # Покупка на 120
    bob.accept_payment(alice, 200)   # Ещё на 200
    bob.accept_payment(alice, 200)   # Попытка сверх остатка (осталось 180)

    # 4. Проверка итогов
    print("\n=== ИТОГИ ===")
    bob.show_balance()  # 120 + 200 = 320
    print(f"Остаток на карте Алисы: {bank.get_card_balance(alice.card['number'])}")  # 500-320=180
    print(f"Баланс Алисы в банке (не тратится с карты): {bank.accounts['Alice']}")  # 500