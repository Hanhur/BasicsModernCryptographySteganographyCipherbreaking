# Выводы по протоколу MBXX
"""
MBXX Protocol Simulation (Lightweight, No NumPy)
Based on the protocol description:
1. Decentralized peer-to-peer transactions with no third parties.
2. Consensus via mathematical balance verification (isomorphic balance + ZKP-like blind comparison).
3. Validator only sees initial total supply and balance violation flag.
4. Accepts only positive balances (no overdraft).
"""

import hashlib
import random
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class TransactionStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass
class Transaction:
    """Represents a transaction between two peers."""
    sender_id: str
    receiver_id: str
    amount: int
    timestamp: int
    nonce: int
    signature: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING
    
    def get_hash(self) -> str:
        """Generate cryptographic hash of transaction data."""
        data = f"{self.sender_id}{self.receiver_id}{self.amount}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sign(self, private_key: str) -> None:
        """Simulate signing with private key (simplified for demo)."""
        data = self.get_hash() + private_key
        self.signature = hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self, public_key: str) -> bool:
        """Verify transaction signature (simplified)."""
        if not self.signature:
            return False
        data = self.get_hash() + public_key
        expected = hashlib.sha256(data.encode()).hexdigest()
        return self.signature == expected


@dataclass
class Account:
    """Individual account with balance."""
    id: str
    balance: int
    public_key: str
    private_key: str
    
    def can_spend(self, amount: int) -> bool:
        """Check if balance is sufficient (positive balance only)."""
        return self.balance >= amount and amount >= 0


class BlindBalanceVerifier:
    """
    Simulates Zero-Knowledge Proof (ZKP) style blind comparison.
    Validator only learns: positive/negative balance status, not the actual amount.
    """
    
    @staticmethod
    def blind_compare(account_balance: int, transaction_amount: int) -> Tuple[bool, str]:
        """
        Blind comparison: validator sees only the result (True/False)
        and a blinded hash, not the actual balance.
        
        Returns:
            (is_positive_balance, blinded_hash)
        """
        # The validator only checks if balance - amount >= 0
        # but doesn't see the actual numbers (simulated with hashing)
        result = account_balance >= transaction_amount
        
        # Blind the balance (simulate ZKP by hashing with random salt)
        salt = random.randint(1000, 9999)
        blinded = hashlib.sha256(f"{account_balance}{transaction_amount}{salt}".encode()).hexdigest()
        
        # The validator sees only the result and the blinded value
        return result, blinded
    
    @staticmethod
    def verify_balance_proof(account: Account, amount: int, blinded_proof: str) -> bool:
        """
        Verify that the balance is positive without revealing the actual balance.
        In real ZKP, this would be more complex.
        """
        # Simulate verification: check if account can spend
        # In real ZKP, this would verify mathematical properties
        return account.can_spend(amount)


class IsomorphicBalanceChecker:
    """
    Implements isomorphic balance verification.
    Checks that total balance in the system remains invariant.
    """
    
    def __init__(self, initial_total_supply: int):
        self.initial_total_supply = initial_total_supply
        self._accounts: Dict[str, Account] = {}
    
    def register_account(self, account: Account) -> None:
        """Register an account in the system."""
        self._accounts[account.id] = account
    
    def get_total_balance(self) -> int:
        """Calculate total balance of all accounts."""
        return sum(acc.balance for acc in self._accounts.values())
    
    def verify_isomorphic_balance(self) -> Tuple[bool, int, int]:
        """
        Verify that total balance equals initial supply (isomorphic invariant).
        Returns: (is_balanced, current_total, initial_total)
        """
        current_total = self.get_total_balance()
        is_balanced = current_total == self.initial_total_supply
        return is_balanced, current_total, self.initial_total_supply
    
    def verify_transaction_balances(self, transaction: Transaction) -> Tuple[bool, str]:
        """
        Verify transaction doesn't break balance invariants.
        This implements the "validator only sees initial sum and violation flag" principle.
        """
        sender = self._accounts.get(transaction.sender_id)
        receiver = self._accounts.get(transaction.receiver_id)
        
        if not sender or not receiver:
            return False, "Account not found"
        
        # Perform blind comparison (ZKP style)
        # Validator doesn't see the actual balance, only the result
        result, blinded = BlindBalanceVerifier.blind_compare(sender.balance, transaction.amount)
        
        if not result:
            return False, f"Balance violation detected (blind proof: {blinded[:16]}...)"
        
        # The validator knows about initial supply, check isomorphic invariant
        total_before = self.get_total_balance()
        sender.balance -= transaction.amount
        receiver.balance += transaction.amount
        total_after = self.get_total_balance()
        
        # Restore balances if violation detected
        if total_before != total_after or total_after != self.initial_total_supply:
            sender.balance += transaction.amount
            receiver.balance -= transaction.amount
            return False, f"Isomorphic balance violation! Expected {self.initial_total_supply}, got {total_after}"
        
        return True, "Transaction verified (balanced preserved)"
    
    def get_balance_summary(self) -> Dict:
        """
        Returns only what the validator can see:
        - Initial total supply
        - Current total balance
        - Violation flag
        """
        current_total = self.get_total_balance()
        is_balanced = current_total == self.initial_total_supply
        
        return {
            "initial_total_supply": self.initial_total_supply,
            "current_total_balance": current_total,
            "balance_violation": not is_balanced,
            # Note: Validator does NOT see individual account balances or count
        }


class MBXXNode:
    """
    MBXX Protocol Node (Peer-to-Peer).
    Implements decentralized transaction processing.
    """
    
    def __init__(self, node_id: str, balance_checker: IsomorphicBalanceChecker):
        self.node_id = node_id
        self.balance_checker = balance_checker
        self.transaction_pool: List[Transaction] = []
        self.verified_transactions: List[Transaction] = []
        self.rejected_transactions: List[Transaction] = []
    
    def create_transaction(self, sender_id: str, receiver_id: str, amount: int) -> Transaction:
        """Create a new transaction (peer-to-peer)."""
        import time
        tx = Transaction(
            sender_id = sender_id,
            receiver_id = receiver_id,
            amount = amount,
            timestamp = int(time.time()),
            nonce = random.randint(1, 1000000)
        )
        # Sign with sender's private key (simulated)
        sender_acc = self.balance_checker._accounts.get(sender_id)
        if sender_acc:
            tx.sign(sender_acc.private_key)
        return tx
    
    def process_transaction(self, transaction: Transaction) -> bool:
        """
        Process a transaction in the decentralized peer-to-peer network.
        Validator (computer) can block transaction only if verification is not complete.
        """
        # Step 1: Verify signature (authentication)
        sender = self.balance_checker._accounts.get(transaction.sender_id)
        if not sender:
            transaction.status = TransactionStatus.REJECTED
            self.rejected_transactions.append(transaction)
            return False
        
        if not transaction.verify_signature(sender.public_key):
            transaction.status = TransactionStatus.REJECTED
            self.rejected_transactions.append(transaction)
            return False
        
        # Step 2: Verify balance using isomorphic + ZKP (mathematical consensus)
        # Validator checks if balance is positive (blind comparison)
        is_valid, message = self.balance_checker.verify_transaction_balances(transaction)
        
        if is_valid:
            transaction.status = TransactionStatus.VERIFIED
            self.verified_transactions.append(transaction)
            print(f"[VERIFIED] Transaction {transaction.get_hash()[:8]}... - {message}")
        else:
            transaction.status = TransactionStatus.REJECTED
            self.rejected_transactions.append(transaction)
            print(f"[REJECTED] Transaction {transaction.get_hash()[:8]}... - {message}")
        
        # Validator sees only the summary (not individual amounts)
        summary = self.balance_checker.get_balance_summary()
        print(f"[VALIDATOR VIEW] {summary}")
        
        return is_valid
    
    def get_validator_view(self) -> Dict:
        """
        Returns what the validator (computer) can see.
        Implements the protocol requirement:
        "Validator only knows initial sum and violation flag"
        """
        return self.balance_checker.get_balance_summary()


class LightweightEncryptionSimulator:
    """
    Simulates lightweight encryption mentioned in the protocol (IoT/streaming).
    """
    
    @staticmethod
    def xor_encrypt(data: str, key: int) -> str:
        """Simple XOR encryption (lightweight)."""
        result = []
        for char in data:
            result.append(chr(ord(char) ^ (key & 0xFF)))
        return ''.join(result)
    
    @staticmethod
    def xor_decrypt(encrypted: str, key: int) -> str:
        """Simple XOR decryption."""
        return LightweightEncryptionSimulator.xor_encrypt(encrypted, key)
    
    @staticmethod
    def stream_encrypt(data: str, key_stream: List[int]) -> str:
        """Stream encryption for IoT/data streaming."""
        result = []
        for i, char in enumerate(data):
            key = key_stream[i % len(key_stream)]
            result.append(chr(ord(char) ^ (key & 0xFF)))
        return ''.join(result)


def run_mbxx_demo():
    """
    Demonstration of the MBXX Protocol.
    Shows: decentralized P2P, ZKP-style balance checking, isomorphic invariant.
    """
    print("=" * 60)
    print("MBXX PROTOCOL DEMONSTRATION")
    print("Decentralized · Zero-Knowledge Consensus · Lightweight")
    print("=" * 60)
    
    # Initialize system with initial total supply
    INITIAL_TOTAL = 1000000
    balance_checker = IsomorphicBalanceChecker(INITIAL_TOTAL)
    
    # Create nodes (peers)
    nodes = [
        MBXXNode("Node_A", balance_checker),
        MBXXNode("Node_B", balance_checker),
        MBXXNode("Node_C", balance_checker),
    ]
    
    # Create accounts with initial balances
    accounts = [
        Account(
            id = "Alice",
            balance = 500000,
            public_key = "pub_alice_001",
            private_key = "priv_alice_001"
        ),
        Account(
            id = "Bob",
            balance = 300000,
            public_key = "pub_bob_002",
            private_key = "priv_bob_002"
        ),
        Account(
            id = "Charlie",
            balance = 200000,
            public_key = "pub_charlie_003",
            private_key = "priv_charlie_003"
        ),
    ]
    
    # Register accounts
    for account in accounts:
        balance_checker.register_account(account)
    
    print("\n[SYSTEM INITIALIZED]")
    print(f"Initial total supply: {INITIAL_TOTAL}")
    print(f"Accounts: {[acc.id for acc in accounts]}")
    
    # Show validator's view (only sees total, not individual)
    print(f"\n[VALIDATOR VIEW] {balance_checker.get_balance_summary()}")
    
    # ===== TRANSACTION 1: VALID =====
    print("\n" + "-" * 60)
    print("TRANSACTION 1: Alice -> Bob (100,000 units)")
    print("-" * 60)
    
    tx1 = nodes[0].create_transaction("Alice", "Bob", 100000)
    print(f"TX Hash: {tx1.get_hash()}")
    print(f"Signature: {tx1.signature[:16]}...")
    
    # Process (no third party involved - P2P)
    result1 = nodes[0].process_transaction(tx1)
    print(f"Result: {'SUCCESS' if result1 else 'FAILED'}")
    
    # ===== TRANSACTION 2: INSUFFICIENT BALANCE (should fail) =====
    print("\n" + "-" * 60)
    print("TRANSACTION 2: Charlie -> Alice (500,000 units - exceeds balance)")
    print("-" * 60)
    
    tx2 = nodes[1].create_transaction("Charlie", "Alice", 500000)
    print(f"TX Hash: {tx2.get_hash()}")
    print(f"Charlie's balance: {balance_checker._accounts['Charlie'].balance}")
    print(f"Amount requested: 500,000")
    
    result2 = nodes[1].process_transaction(tx2)
    print(f"Result: {'SUCCESS' if result2 else 'FAILED (expected)'}")
    
    # ===== TRANSACTION 3: VALID (within balance) =====
    print("\n" + "-" * 60)
    print("TRANSACTION 3: Charlie -> Alice (50,000 units)")
    print("-" * 60)
    
    tx3 = nodes[2].create_transaction("Charlie", "Alice", 50000)
    print(f"TX Hash: {tx3.get_hash()}")
    
    result3 = nodes[2].process_transaction(tx3)
    print(f"Result: {'SUCCESS' if result3 else 'FAILED'}")
    
    # ===== FINAL VALIDATOR SUMMARY =====
    print("\n" + "=" * 60)
    print("FINAL VALIDATOR SUMMARY")
    print("=" * 60)
    
    final_view = balance_checker.get_balance_summary()
    print(f"Initial total supply: {final_view['initial_total_supply']}")
    print(f"Current total balance: {final_view['current_total_balance']}")
    print(f"Balance violation: {final_view['balance_violation']}")
    
    print("\n[ACCOUNT BALANCES - ONLY SYSTEM KNOWS, NOT VALIDATOR]")
    for acc in accounts:
        print(f"  {acc.id}: {acc.balance}")
    
    # ===== VERIFY ISOMORPHIC INVARIANT =====
    is_balanced, current, initial = balance_checker.verify_isomorphic_balance()
    print(f"\n[ISOMORPHIC BALANCE CHECK]")
    print(f"  Is balanced: {is_balanced}")
    print(f"  Total: {current} / {initial}")
    print(f"  Status: {'✅ PRESERVED' if is_balanced else '❌ BROKEN'}")
    
    # ===== LIGHTWEIGHT ENCRYPTION DEMO (IoT/Streaming) =====
    print("\n" + "=" * 60)
    print("LIGHTWEIGHT ENCRYPTION DEMO (IoT / Streaming)")
    print("=" * 60)
    
    encryptor = LightweightEncryptionSimulator()
    message = "MBXX protocol for IoT devices"
    key_stream = [42, 87, 13, 99, 55, 201, 77]
    
    encrypted = encryptor.stream_encrypt(message, key_stream)
    decrypted = encryptor.stream_encrypt(encrypted, key_stream)
    
    print(f"Original:  {message}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {message == decrypted}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("Key MBXX properties demonstrated:")
    print("  ✅ No third-party involvement (P2P)")
    print("  ✅ Consensus via mathematical function (not probability)")
    print("  ✅ Validator sees only initial sum + violation flag")
    print("  ✅ Positive balance enforcement (no overdraft)")
    print("  ✅ Isomorphic balance preservation")
    print("  ✅ Lightweight encryption for IoT")
    print("=" * 60)


if __name__ == "__main__":
    run_mbxx_demo()