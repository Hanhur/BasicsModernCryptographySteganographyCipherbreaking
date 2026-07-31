# Возможные атаки на ZK13
"""
ZK13 Protocol Implementation with Attack Demonstrations
Author: Security Research Demo
Date: 2026-07-31

This implementation demonstrates:
1. Normal protocol flow (Alice -> Bob authentication)
2. Man-in-the-Middle attack (failed attempt)
3. Replay attack and its prevention
4. Protection mechanisms (nonce, timestamp, session IDs)
"""

import hashlib
import secrets
import time
from typing import Tuple, Optional, Set, Dict
from dataclasses import dataclass
from collections import defaultdict
import threading


# ============================================================================
# Core Cryptographic Functions
# ============================================================================

def H(data: bytes) -> bytes:
    """Cryptographic hash function (SHA-256)"""
    return hashlib.sha256(data).digest()


def H_hex(data: bytes) -> str:
    """Hash function returning hexadecimal string for readability"""
    return H(data).hex()


def generate_random_bytes(length: int = 32) -> bytes:
    """Cryptographically secure random number generator"""
    return secrets.token_bytes(length)


# ============================================================================
# Protocol Constants and Data Structures
# ============================================================================

@dataclass
class Session:
    """Represents a protocol session"""
    session_id: str
    r: bytes          # Random challenge from Alice
    P: bytes          # Public parameter
    timestamp: float  # When session was created
    used: bool = False  # Flag to prevent replay


class ZK13Server:
    """
    Bob's server implementation with anti-replay protection
    """
    
    def __init__(self, secret_s: bytes, cache_size: int = 1000, ttl_seconds: int = 60):
        """
        Args:
            secret_s: Bob's long-term secret (known only to Bob and Alice)
            cache_size: Maximum number of used 'r' values to store
            ttl_seconds: Time-to-live for stored 'r' values
        """
        self.secret_s = secret_s
        self.H_s = H(secret_s)  # Pre-computed hash of secret
        
        # Anti-replay protection: store used (r, timestamp) pairs
        self.used_r_cache: Dict[bytes, float] = {}
        self.cache_size = cache_size
        self.ttl_seconds = ttl_seconds
        
        # Active sessions tracking for interleaving attack prevention
        self.active_sessions: Dict[str, Session] = {}
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        print(f"[BOB] Initialized with H[s] = {H_hex(self.H_s)[:16]}...")
    
    def _cleanup_cache(self):
        """Remove expired entries from the cache"""
        current_time = time.time()
        expired = [r for r, ts in self.used_r_cache.items() if current_time - ts > self.ttl_seconds]
        for r in expired:
            del self.used_r_cache[r]
        
        # If cache still too large, remove oldest entries
        if len(self.used_r_cache) > self.cache_size:
            sorted_entries = sorted(self.used_r_cache.items(), key = lambda x: x[1])
            for r, _ in sorted_entries[:len(self.used_r_cache) - self.cache_size]:
                del self.used_r_cache[r]
    
    def _is_replay(self, r: bytes) -> bool:
        """Check if this 'r' has been used before (replay attack detection)"""
        with self.lock:
            self._cleanup_cache()
            if r in self.used_r_cache:
                return True
            return False
    
    def _store_r(self, r: bytes):
        """Store 'r' in the cache to prevent replay"""
        with self.lock:
            self._cleanup_cache()
            self.used_r_cache[r] = time.time()
    
    def _compute_verification(self, r: bytes, P: bytes, session_id: str) -> bytes:
        """
        Compute F = H(r || P || H[s] || session_id)
        Including session_id prevents interleaving attacks
        """
        data = r + P + self.H_s + session_id.encode('utf-8')
        return H(data)
    
    def verify_session(self, r: bytes, P: bytes, F: bytes, session_id: str) -> Tuple[bool, str]:
        """
        Verify Alice's authentication attempt
        
        Returns:
            (success, message)
        """
        # Check for replay attack
        if self._is_replay(r):
            return False, f"REPLAY DETECTED: 'r' already used in previous session"
        
        # Compute expected verification value
        expected_F = self._compute_verification(r, P, session_id)
        
        # Check if verification matches
        if F != expected_F:
            return False, f"Authentication failed: F mismatch"
        
        # If successful, store 'r' to prevent replay
        self._store_r(r)
        
        # Store session as active
        session = Session(
            session_id = session_id,
            r = r,
            P = P,
            timestamp = time.time(),
            used = True
        )
        self.active_sessions[session_id] = session
        
        return True, f"Authentication SUCCESS for session {session_id}"
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session information"""
        return self.active_sessions.get(session_id)
    
    def cleanup_sessions(self):
        """Remove old sessions"""
        current_time = time.time()
        expired = [sid for sid, sess in self.active_sessions.items() if current_time - sess.timestamp > self.ttl_seconds * 2]
        for sid in expired:
            del self.active_sessions[sid]


class ZK13Client:
    """
    Alice's client implementation
    """
    
    def __init__(self, username: str, secret_s: bytes):
        self.username = username
        self.secret_s = secret_s
        self.H_s = H(secret_s)
    
    def create_authentication_request(self, session_id: str) -> Tuple[bytes, bytes, bytes]:
        """
        Generate authentication request (r, P, F)
        
        Returns:
            (r, P, F) where:
            - r: random challenge (generated from random k)
            - P: public parameter (can be any value, but in real protocols relates to s)
            - F: verification value
        """
        # Generate random 'k' (this is the ephemeral secret)
        k = generate_random_bytes(32)
        
        # Generate 'r' from k (in real protocol, r = g^k mod p, but simplified here)
        # We use k as the basis for r to demonstrate the concept
        r = H(k + b"r_generation")  # Deterministic from k, but still random
        
        # Generate 'P' (public parameter)
        # In real protocols: P = g^s mod p, but we simplify
        P = H(self.secret_s + b"P_generation")
        
        # Compute verification F = H(r || P || H[s] || session_id)
        data = r + P + self.H_s + session_id.encode('utf-8')
        F = H(data)
        
        return r, P, F


class EveAttacker:
    """
    Eve (adversary) attempting various attacks
    """
    
    def __init__(self):
        self.captured_messages: list = []
        self.fabricated_r_values: list = []
    
    def mitm_attempt(self, r: bytes, P: bytes, session_id: str) -> Tuple[bytes, bytes, bytes]:
        """
        Man-in-the-Middle attack: replace r with r1
        This will fail because Eve doesn't know H[s]
        """
        # Generate fake k1
        k1 = generate_random_bytes(32)
        
        # Generate fake r1
        r1 = H(k1 + b"r_generation")
        
        # Eve doesn't know H[s], so she can't compute correct F
        # She tries to guess or use random F
        fake_F = generate_random_bytes(32)
        
        print(f"[EVE] MitM attempt: replaced r = {r.hex()[:16]}... with r1 = {r1.hex()[:16]}...")
        print(f"[EVE] Cannot compute correct F without H[s]! Will send random F.")
        
        return r1, P, fake_F
    
    def capture_message(self, r: bytes, P: bytes, F: bytes, session_id: str):
        """Eve captures legitimate messages"""
        self.captured_messages.append({
            'r': r,
            'P': P,
            'F': F,
            'session_id': session_id,
            'timestamp': time.time()
        })
        print(f"[EVE] Captured message: r = {r.hex()[:16]}..., session = {session_id}")
    
    def replay_attack(self, index: int = -1, use_timestamp: bool = False) -> Tuple[bytes, bytes, bytes, str]:
        """
        Eve replays a previously captured message
        
        Args:
            index: Which captured message to replay (-1 for latest)
            use_timestamp: If True, adds a timestamp to try to bypass protection
        
        Returns:
            (r, P, F, session_id)
        """
        if not self.captured_messages:
            raise ValueError("No captured messages to replay")
        
        msg = self.captured_messages[index]
        r, P, F = msg['r'], msg['P'], msg['F']
        
        # If we use timestamp, we modify the session_id (but F won't match)
        if use_timestamp:
            old_session_id = msg['session_id']
            new_session_id = f"{old_session_id}_replay_{int(time.time())}"
            print(f"[EVE] Replay with timestamp spoofing: {old_session_id} -> {new_session_id}")
            # F won't match because it includes session_id
            return r, P, F, new_session_id
        else:
            print(f"[EVE] Simple replay attack: sending same (r, P, F) from session {msg['session_id']}")
            return r, P, F, msg['session_id']
    
    def interleaving_attack(self, server: ZK13Server, session1_id: str, session2_id: str):
        """
        Interleaving attack: use responses from one session in another
        """
        print(f"[EVE] Attempting interleaving attack between sessions {session1_id} and {session2_id}")
        
        # Get session info for session1 (captured earlier)
        # This is a simplified demonstration
        session1 = server.get_session(session1_id)
        session2 = server.get_session(session2_id)
        
        if session1 and session2:
            # Try to use session1's r in session2
            r_stolen = session1.r
            print(f"[EVE] Stealing r={r_stolen.hex()[:16]}... from session {session1_id}")
            print(f"[EVE] Attempting to use in session {session2_id}")
            
            # This will fail because F is computed with session2_id
            # But if the server doesn't check session_id in F, it would work
            return r_stolen
        return None


# ============================================================================
# Main Program
# ============================================================================

def demonstrate_protocol():
    """Main demonstration function"""
    
    print("=" * 70)
    print("ZK13 PROTOCOL DEMONSTRATION")
    print("=" * 70)
    print()
    
    # ========================================================================
    # 1. Setup
    # ========================================================================
    print("1. SETUP PHASE")
    print("-" * 40)
    
    # Bob's secret (long-term)
    bob_secret = b"Bob's Super Secret Key - Keep Safe!"
    bob = ZK13Server(bob_secret)
    
    # Alice's secret (same as Bob's - shared secret)
    alice = ZK13Client("Alice", bob_secret)
    
    # Eve the attacker
    eve = EveAttacker()
    
    print(f"\n[SETUP] Bob's server ready with H[s] = {H_hex(bob.H_s)[:16]}...")
    print("[SETUP] Alice ready to authenticate")
    print("[SETUP] Eve is listening...\n")
    
    # ========================================================================
    # 2. Normal Authentication Flow
    # ========================================================================
    print("2. NORMAL AUTHENTICATION FLOW")
    print("-" * 40)
    
    session_id = f"SESSION_{int(time.time())}"
    print(f"[ALICE] Starting session: {session_id}")
    
    # Alice creates authentication request
    r, P, F = alice.create_authentication_request(session_id)
    print(f"[ALICE] Generated r = {r.hex()[:16]}...")
    print(f"[ALICE] Generated P = {P.hex()[:16]}...")
    print(f"[ALICE] Generated F = {F.hex()[:16]}...")
    
    # Eve captures the message
    eve.capture_message(r, P, F, session_id)
    
    # Bob verifies
    success, message = bob.verify_session(r, P, F, session_id)
    print(f"\n[BOB] Verification result: {message}")
    
    # ========================================================================
    # 3. Man-in-the-Middle Attack (FAILED)
    # ========================================================================
    print("\n3. MAN-IN-THE-MIDDLE ATTACK (FAILED)")
    print("-" * 40)
    
    # Eve tries to replace r with r1
    session_id_mitm = f"SESSION_MITM_{int(time.time())}"
    print(f"[ALICE] Starting new session: {session_id_mitm}")
    
    r_orig, P_orig, F_orig = alice.create_authentication_request(session_id_mitm)
    print(f"[ALICE] Original r = {r_orig.hex()[:16]}...")
    
    # Eve performs MitM
    r1, P1, F1 = eve.mitm_attempt(r_orig, P_orig, session_id_mitm)
    
    # Bob receives Eve's fake values
    print(f"\n[BOB] Receiving from Eve (supposedly Alice)...")
    success_mitm, message_mitm = bob.verify_session(r1, P1, F1, session_id_mitm)
    print(f"[BOB] Verification result: {message_mitm}")
    print("[RESULT] MitM attack FAILED - Eve couldn't forge F without H[s]\n")
    
    # ========================================================================
    # 4. Replay Attack and Prevention
    # ========================================================================
    print("4. REPLAY ATTACK AND PREVENTION")
    print("-" * 40)
    
    # First, let's try a simple replay (without protection)
    print("4a. Simple Replay Attack (should be blocked)")
    print("-" * 20)
    
    # Eve replays the first captured message
    r_replay, P_replay, F_replay, session_id_replay = eve.replay_attack(0)
    
    # Bob verifies the replayed message
    success_replay, message_replay = bob.verify_session(r_replay, P_replay, F_replay, session_id_replay)
    print(f"[BOB] Replay verification: {message_replay}")
    print("[RESULT] Replay attack BLOCKED - 'r' is in the cache\n")
    
    # Now let's show that the first message is still valid if reused immediately
    print("4b. Attempting same session replay (different session ID)")
    print("-" * 20)
    
    # Create a new session with the same credentials
    session_id_legit = f"SESSION_NEW_{int(time.time())}"
    r_new, P_new, F_new = alice.create_authentication_request(session_id_legit)
    
    # Capture this new legitimate message
    eve.capture_message(r_new, P_new, F_new, session_id_legit)
    
    # Bob verifies - this should work
    success_legit, message_legit = bob.verify_session(r_new, P_new, F_new, session_id_legit)
    print(f"[BOB] New legitimate session: {message_legit}")
    
    # Now Eve tries to replay this new message
    r_replay2, P_replay2, F_replay2, session_id_replay2 = eve.replay_attack(-1)
    success_replay2, message_replay2 = bob.verify_session(r_replay2, P_replay2, F_replay2, session_id_replay2)
    print(f"[BOB] Replay of latest message: {message_replay2}")
    print("[RESULT] Replay attack BLOCKED again\n")
    
    # ========================================================================
    # 5. Interleaving Attack (requires session tracking)
    # ========================================================================
    print("5. INTERLEAVING ATTACK")
    print("-" * 40)
    
    session_a = f"SESSION_A_{int(time.time())}"
    session_b = f"SESSION_B_{int(time.time())+1}"
    
    # Create two legitimate sessions
    r_a, P_a, F_a = alice.create_authentication_request(session_a)
    r_b, P_b, F_b = alice.create_authentication_request(session_b)
    
    # Both authenticate successfully
    bob.verify_session(r_a, P_a, F_a, session_a)
    bob.verify_session(r_b, P_b, F_b, session_b)
    
    # Eve tries interleaving: use r from session A in session B
    stolen_r = eve.interleaving_attack(bob, session_a, session_b)
    
    # Try to use stolen r in session B's verification
    # But F is tied to session B, so it won't match
    if stolen_r:
        # Recompute F with stolen r but session B's context
        # This would require Eve to know H[s] - she doesn't
        fake_F = generate_random_bytes(32)
        success_inter, message_inter = bob.verify_session(stolen_r, P_b, fake_F, session_b)
        print(f"[BOB] Interleaving attempt result: {message_inter}")
        print("[RESULT] Interleaving attack FAILED - F includes session_id\n")
    
    # ========================================================================
    # 6. Cache Management and DoS Prevention
    # ========================================================================
    print("6. CACHE MANAGEMENT AND DoS PREVENTION")
    print("-" * 40)
    
    print(f"[BOB] Cache size: {len(bob.used_r_cache)} stored 'r' values")
    print(f"[BOB] Max cache size: {bob.cache_size}")
    print(f"[BOB] TTL: {bob.ttl_seconds} seconds")
    
    # Simulate many authentication attempts
    print("\n[TEST] Simulating 5 authentication attempts...")
    for i in range(5):
        test_session = f"TEST_{i}_{int(time.time())}"
        test_r, test_P, test_F = alice.create_authentication_request(test_session)
        success, msg = bob.verify_session(test_r, test_P, test_F, test_session)
        print(f"  Attempt {i + 1}: {msg}")
    
    print(f"\n[BOB] Final cache size: {len(bob.used_r_cache)}")
    print("[RESULT] Cache effectively prevents replay and handles multiple requests\n")
    
    # ========================================================================
    # 7. Summary
    # ========================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
    ATTACK TYPES & RESULTS:
    1. Man-in-the-Middle (MitM):     ❌ FAILED  (requires H[s])
    2. Replay Attack:                ❌ FAILED  (cache prevents reuse)
    3. Interleaving Attack:          ❌ FAILED  (session_id in F)
    4. Denial of Service (DoS):      ⚠️  PARTIALLY MITIGATED (cache limits)
    
    PROTECTION MECHANISMS:
    ✓ H[s] is never transmitted (only Alice and Bob know it)
    ✓ Each 'r' is stored after use (replay detection)
    ✓ Session ID included in F (prevents interleaving)
    ✓ Cache with TTL and size limit (prevents DoS)
    ✓ Cryptographic random number generation
    
    SECURITY STRENGTH: Strong against active attacks
    """)


if __name__ == "__main__":
    demonstrate_protocol()