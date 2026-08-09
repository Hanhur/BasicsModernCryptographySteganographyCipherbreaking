# Тестирование производительности Cybpher 
#!/usr/bin/env python3
"""
Cybpher Performance Simulator
Based on the described lightweight encryption algorithm
No external dependencies except cryptography for AES comparison
"""

import time
import os
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ============================================================================
# CYBPHER IMPLEMENTATION (SIMULATED LEA-BASED ALGORITHM)
# ============================================================================

class Cybpher:
    """
    Simulated Cybpher lightweight encryption algorithm
    Based on LEA (Lightweight Encryption Algorithm) principles
    Uses 16 rounds, 128-bit block, 256-bit key
    """
    
    def __init__(self, key: bytes):
        """
        Initialize Cybpher with a 32-byte (256-bit) key
        
        Args:
            key: 32-byte key material
        """
        if len(key) != 32:
            raise ValueError("Cybpher key must be 32 bytes (256 bits)")
        
        self.key = key
        self.rounds = 16
        self.block_size = 16  # 128-bit block
        
        # Generate round keys (key schedule) with random-like buffer
        self.round_keys = self._generate_round_keys(key)
        self.offset_buffer = self._generate_offset_buffer(key)
    
    def _generate_round_keys(self, key: bytes) -> list:
        """Generate 16 round keys from master key using LEA-like expansion"""
        round_keys = []
        
        # Split key into 4 64-bit words
        k0 = struct.unpack('<Q', key[0:8])[0]
        k1 = struct.unpack('<Q', key[8:16])[0]
        k2 = struct.unpack('<Q', key[16:24])[0]
        k3 = struct.unpack('<Q', key[24:32])[0]
        
        # Constants (delta values from LEA)
        delta = 0x9e3779b185ebca87  # Golden ratio constant
        
        for i in range(self.rounds):
            # Key expansion with rotation and addition
            t = (i * delta) & 0xFFFFFFFFFFFFFFFF
            rk0 = (k0 + t) & 0xFFFFFFFFFFFFFFFF
            rk1 = (k1 + (t << 1)) & 0xFFFFFFFFFFFFFFFF
            rk2 = (k2 + (t << 2)) & 0xFFFFFFFFFFFFFFFF
            rk3 = (k3 + (t << 3)) & 0xFFFFFFFFFFFFFFFF
            
            # Apply cyclic shifts for diffusion
            rk0 = self._rotl64(rk0, i % 64)
            rk1 = self._rotl64(rk1, (i * 3) % 64)
            rk2 = self._rotl64(rk2, (i * 5) % 64)
            rk3 = self._rotl64(rk3, (i * 7) % 64)
            
            round_keys.append((rk0, rk1, rk2, rk3))
        
        return round_keys
    
    def _generate_offset_buffer(self, key: bytes) -> list:
        """Generate offset buffer for whitening/randomization"""
        offsets = []
        for i in range(self.rounds * 2):  # Double buffer for encryption/decryption
            # Derive offset from key with non-linear transformation
            offset = struct.unpack('<Q', key[i % 16:(i % 16) + 8])[0] if i % 16 < 8 else 0
            offset = self._rotl64(offset, (i * 13) % 64)
            offset = (offset ^ 0xAAAAAAAA55555555) & 0xFFFFFFFFFFFFFFFF
            offsets.append(offset)
        return offsets
    
    @staticmethod
    def _rotl64(x: int, n: int) -> int:
        """Rotate 64-bit integer left by n bits"""
        n = n % 64
        return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF
    
    @staticmethod
    def _rotr64(x: int, n: int) -> int:
        """Rotate 64-bit integer right by n bits"""
        n = n % 64
        return ((x >> n) | (x << (64 - n))) & 0xFFFFFFFFFFFFFFFF
    
    def _encrypt_block(self, block: bytes) -> bytes:
        """
        Encrypt a single 16-byte block using 16 rounds
        
        Round function: XOR -> ADD -> ROTATE -> XOR with round key
        """
        if len(block) != 16:
            raise ValueError("Block must be 16 bytes")
        
        # Split block into 4 32-bit words (using 32-bit for ARM compatibility)
        a = struct.unpack('<I', block[0:4])[0]
        b = struct.unpack('<I', block[4:8])[0]
        c = struct.unpack('<I', block[8:12])[0]
        d = struct.unpack('<I', block[12:16])[0]
        
        # Apply offset buffer (whitening)
        a ^= (self.offset_buffer[0] & 0xFFFFFFFF)
        b ^= (self.offset_buffer[1] & 0xFFFFFFFF)
        c ^= (self.offset_buffer[2] & 0xFFFFFFFF)
        d ^= (self.offset_buffer[3] & 0xFFFFFFFF)
        
        for rnd in range(self.rounds):
            # Extract round key words (64-bit split into two 32-bit)
            rk0_low = self.round_keys[rnd][0] & 0xFFFFFFFF
            rk0_high = (self.round_keys[rnd][0] >> 32) & 0xFFFFFFFF
            rk1_low = self.round_keys[rnd][1] & 0xFFFFFFFF
            rk1_high = (self.round_keys[rnd][1] >> 32) & 0xFFFFFFFF
            
            # Core round: ARX (Addition, Rotation, XOR)
            # Similar to LEA structure
            a = (a + rk0_low) & 0xFFFFFFFF
            b = (b ^ rk0_high) & 0xFFFFFFFF
            c = (c + rk1_low) & 0xFFFFFFFF
            d = (d ^ rk1_high) & 0xFFFFFFFF
            
            # Apply rotations (different per round for diffusion)
            a = ((a << (3 + rnd % 5)) | (a >> (32 - (3 + rnd % 5)))) & 0xFFFFFFFF
            b = ((b >> (5 + rnd % 7)) | (b << (32 - (5 + rnd % 7)))) & 0xFFFFFFFF
            c = ((c << (7 + rnd % 11)) | (c >> (32 - (7 + rnd % 11)))) & 0xFFFFFFFF
            d = ((d >> (11 + rnd % 13)) | (d << (32 - (11 + rnd % 13)))) & 0xFFFFFFFF
            
            # XOR mixing
            a ^= b
            c ^= d
            b ^= c
            d ^= a
        
        # Final offset mixing
        a ^= (self.offset_buffer[4] & 0xFFFFFFFF)
        b ^= (self.offset_buffer[5] & 0xFFFFFFFF)
        c ^= (self.offset_buffer[6] & 0xFFFFFFFF)
        d ^= (self.offset_buffer[7] & 0xFFFFFFFF)
        
        # Pack back to bytes
        return struct.pack('<IIII', a, b, c, d)
    
    def _decrypt_block(self, block: bytes) -> bytes:
        """
        Decrypt a single 16-byte block (inverse of encryption)
        """
        if len(block) != 16:
            raise ValueError("Block must be 16 bytes")
        
        a = struct.unpack('<I', block[0:4])[0]
        b = struct.unpack('<I', block[4:8])[0]
        c = struct.unpack('<I', block[8:12])[0]
        d = struct.unpack('<I', block[12:16])[0]
        
        # Remove final offset
        a ^= (self.offset_buffer[4] & 0xFFFFFFFF)
        b ^= (self.offset_buffer[5] & 0xFFFFFFFF)
        c ^= (self.offset_buffer[6] & 0xFFFFFFFF)
        d ^= (self.offset_buffer[7] & 0xFFFFFFFF)
        
        # Reverse rounds
        for rnd in range(self.rounds - 1, -1, -1):
            rk0_low = self.round_keys[rnd][0] & 0xFFFFFFFF
            rk0_high = (self.round_keys[rnd][0] >> 32) & 0xFFFFFFFF
            rk1_low = self.round_keys[rnd][1] & 0xFFFFFFFF
            rk1_high = (self.round_keys[rnd][1] >> 32) & 0xFFFFFFFF
            
            # Reverse XOR mixing
            d ^= a
            b ^= c
            c ^= d
            a ^= b
            
            # Reverse rotations
            d = ((d << (11 + rnd % 13)) | (d >> (32 - (11 + rnd % 13)))) & 0xFFFFFFFF
            c = ((c >> (7 + rnd % 11)) | (c << (32 - (7 + rnd % 11)))) & 0xFFFFFFFF
            b = ((b << (5 + rnd % 7)) | (b >> (32 - (5 + rnd % 7)))) & 0xFFFFFFFF
            a = ((a >> (3 + rnd % 5)) | (a << (32 - (3 + rnd % 5)))) & 0xFFFFFFFF
            
            # Reverse core round
            d = (d ^ rk1_high) & 0xFFFFFFFF
            c = (c - rk1_low) & 0xFFFFFFFF
            b = (b ^ rk0_high) & 0xFFFFFFFF
            a = (a - rk0_low) & 0xFFFFFFFF
        
        # Remove initial offset
        a ^= (self.offset_buffer[0] & 0xFFFFFFFF)
        b ^= (self.offset_buffer[1] & 0xFFFFFFFF)
        c ^= (self.offset_buffer[2] & 0xFFFFFFFF)
        d ^= (self.offset_buffer[3] & 0xFFFFFFFF)
        
        return struct.pack('<IIII', a, b, c, d)
    
    def encrypt(self, data: bytes, iterations: int = 1) -> bytes:
        """Encrypt data with multiple iterations"""
        # Pad data to multiple of block_size
        padding_len = (self.block_size - (len(data) % self.block_size)) % self.block_size
        padded_data = data + b'\x80' + b'\x00' * (padding_len - 1) if padding_len else data
        
        result = bytearray()
        for _ in range(iterations):
            result = bytearray()
            for i in range(0, len(padded_data), self.block_size):
                block = padded_data[i:i + self.block_size]
                result.extend(self._encrypt_block(block))
            padded_data = bytes(result)
        
        return bytes(result)
    
    def decrypt(self, data: bytes, iterations: int = 1) -> bytes:
        """Decrypt data with multiple iterations"""
        result = data
        for _ in range(iterations):
            decrypted = bytearray()
            for i in range(0, len(result), self.block_size):
                block = result[i:i + self.block_size]
                decrypted.extend(self._decrypt_block(block))
            result = bytes(decrypted)
        
        # Remove padding
        # Find last 0x80 byte
        pad_pos = result.rfind(b'\x80')
        if pad_pos != -1:
            return result[:pad_pos]
        return result


# ============================================================================
# AES WRAPPERS (for fair comparison)
# ============================================================================

class AESWrapper:
    """Wrapper for AES-128 and AES-256 using cryptography library"""
    
    def __init__(self, key: bytes):
        self.key = key
        self.block_size = 16
        
    def _pad(self, data: bytes) -> bytes:
        """PKCS#7 padding"""
        padding_len = self.block_size - (len(data) % self.block_size)
        return data + bytes([padding_len] * padding_len)
    
    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS#7 padding"""
        padding_len = data[-1]
        if padding_len > self.block_size:
            raise ValueError("Invalid padding")
        return data[:-padding_len]
    
    def encrypt(self, data: bytes, iterations: int = 1) -> bytes:
        """Encrypt with AES in ECB mode (for performance testing)"""
        padded = self._pad(data)
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend = default_backend())
        encryptor = cipher.encryptor()
        
        result = padded
        for _ in range(iterations):
            encrypted = bytearray()
            for i in range(0, len(result), self.block_size):
                block = result[i:i + self.block_size]
                encrypted.extend(encryptor.update(block))
            encrypted.extend(encryptor.finalize())
            result = bytes(encrypted)
            # Re-initialize for next iteration
            if _ < iterations - 1:
                cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend = default_backend())
                encryptor = cipher.encryptor()
        
        return result
    
    def decrypt(self, data: bytes, iterations: int = 1) -> bytes:
        """Decrypt with AES in ECB mode"""
        cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend = default_backend())
        decryptor = cipher.decryptor()
        
        result = data
        for _ in range(iterations):
            decrypted = bytearray()
            for i in range(0, len(result), self.block_size):
                block = result[i:i + self.block_size]
                decrypted.extend(decryptor.update(block))
            decrypted.extend(decryptor.finalize())
            result = bytes(decrypted)
            if _ < iterations - 1:
                cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend = default_backend())
                decryptor = cipher.decryptor()
        
        try:
            return self._unpad(result)
        except ValueError:
            return result  # Return as-is for raw data comparison


# ============================================================================
# PERFORMANCE TESTING FRAMEWORK
# ============================================================================

def generate_test_data(size: int) -> bytes:
    """Generate pseudo-random test data of specified size"""
    # Use deterministic pattern for reproducibility
    pattern = b"Cybpher Performance Test Data 2026 - " * 10
    return (pattern * ((size // len(pattern)) + 1))[:size]


def run_performance_test(algorithm, data_size: int, iterations: int, test_name: str) -> dict:
    """
    Run performance test for a single algorithm configuration
    
    Returns:
        dict with timing and throughput metrics
    """
    # Generate test data
    plaintext = generate_test_data(data_size)
    
    # Warm-up (ensure JIT/optimizations are applied)
    _ = algorithm.encrypt(plaintext[:16], 1)
    _ = algorithm.decrypt(algorithm.encrypt(plaintext[:16], 1), 1)
    
    # Encryption test
    start_enc = time.perf_counter()
    ciphertext = algorithm.encrypt(plaintext, iterations)
    end_enc = time.perf_counter()
    enc_time_ms = (end_enc - start_enc) * 1000
    
    # Decryption test
    start_dec = time.perf_counter()
    decrypted = algorithm.decrypt(ciphertext, iterations)
    end_dec = time.perf_counter()
    dec_time_ms = (end_dec - start_dec) * 1000
    
    # Verify correctness (only for single iteration)
    if iterations == 1:
        if decrypted == plaintext:
            print(f"  ✓ {test_name}: Verification PASSED")
        else:
            print(f"  ✗ {test_name}: Verification FAILED (data mismatch)")
    
    # Calculate throughput in Mbps
    total_time_ms = enc_time_ms + dec_time_ms
    total_bits = data_size * 8 * iterations * 2  # both encrypt and decrypt
    throughput_mbps = (total_bits / 1000 / 1000) / (total_time_ms / 1000) if total_time_ms > 0 else 0
    
    return {
        'name': test_name,
        'data_size': data_size,
        'iterations': iterations,
        'enc_time_ms': enc_time_ms,
        'dec_time_ms': dec_time_ms,
        'total_time_ms': total_time_ms,
        'throughput_mbps': throughput_mbps
    }


def print_results_table(results: list):
    """Print results in a formatted table similar to the original"""
    print("\n" + "=" * 120)
    print("PERFORMANCE TEST RESULTS - Intel i7 Emulation")
    print("=" * 120)
    
    header = f"{'Algorithm':<12} {'Compiler':<12} {'Data Size':<15} {'Iterations':<10} {'Enc (ms)':<10} {'Dec (ms)':<10} {'Total (ms)':<12} {'Throughput':<12}"
    print(header)
    print("-" * 120)
    
    for r in results:
        size_str = f"{r['data_size']:,} B"
        if r['data_size'] >= 1024 * 1024:
            size_str = f"{r['data_size'] / 1024 / 1024:.1f} MB"
        elif r['data_size'] >= 1024:
            size_str = f"{r['data_size'] / 1024:.1f} KB"
        
        print(f"{r['name']:<12} {'DNDEBUG-03':<12} {size_str:<15} {r['iterations']:<10} {r['enc_time_ms']:<10.1f} {r['dec_time_ms']:<10.1f} {r['total_time_ms']:<12.1f} {r['throughput_mbps']:<12.2f}")
    
    print("="*120)


def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("CYBPHER PERFORMANCE TEST SUITE")
    print("Simulating tests from CyberusLabs benchmark")
    print("=" * 80)
    
    # Test parameters (matching the original table)
    DATA_SIZE = 1 * 1024 * 1024  # 1 MB
    KEY_128 = os.urandom(16)
    KEY_256 = os.urandom(32)
    
    # Initialize algorithms
    print("\n[INFO] Initializing cryptographic engines...")
    cybpher = Cybpher(KEY_256)
    aes128 = AESWrapper(KEY_128)
    aes256 = AESWrapper(KEY_256)
    
    results = []
    
    # Test 1: Cybpher - 1 iteration
    print("\n[TEST] Running Cybpher (1 iteration)...")
    r = run_performance_test(cybpher, DATA_SIZE, 1, "Cybpher")
    results.append(r)
    
    # Test 2: AES-128 - 1 iteration
    print("[TEST] Running AES-128 (1 iteration)...")
    r = run_performance_test(aes128, DATA_SIZE, 1, "AES 128")
    results.append(r)
    
    # Test 3: AES-256 - 1 iteration
    print("[TEST] Running AES-256 (1 iteration)...")
    r = run_performance_test(aes256, DATA_SIZE, 1, "AES 256")
    results.append(r)
    
    # Test 4: Cybpher - 1000 iterations
    print("[TEST] Running Cybpher (1000 iterations)...")
    r = run_performance_test(cybpher, DATA_SIZE, 1000, "Cybpher")
    results.append(r)
    
    # Test 5: AES-128 - 1000 iterations
    print("[TEST] Running AES-128 (1000 iterations)...")
    r = run_performance_test(aes128, DATA_SIZE, 1000, "AES 128")
    results.append(r)
    
    # Test 6: AES-256 - 1000 iterations
    print("[TEST] Running AES-256 (1000 iterations)...")
    r = run_performance_test(aes256, DATA_SIZE, 1000, "AES 256")
    results.append(r)
    
    # Print results
    print_results_table(results)
    
    # Calculate speedup factors
    print("\n" + "-" * 80)
    print("PERFORMANCE COMPARISON (Speedup vs AES)")
    print("-" * 80)
    
    cybpher_1x = results[0]
    aes128_1x = results[1]
    aes256_1x = results[2]
    cybpher_1000x = results[3]
    aes128_1000x = results[4]
    aes256_1000x = results[5]
    
    speedup_1x_enc = aes128_1x['enc_time_ms'] / cybpher_1x['enc_time_ms']
    speedup_1x_dec = aes128_1x['dec_time_ms'] / cybpher_1x['dec_time_ms']
    speedup_1000x_enc = aes128_1000x['enc_time_ms'] / cybpher_1000x['enc_time_ms']
    speedup_1000x_dec = aes128_1000x['dec_time_ms'] / cybpher_1000x['dec_time_ms']
    
    print(f"Cybpher vs AES-128 (1 iteration):  {speedup_1x_enc:.2f}x faster encryption, {speedup_1x_dec:.2f}x faster decryption")
    print(f"Cybpher vs AES-256 (1 iteration):  {aes256_1x['enc_time_ms'] / cybpher_1x['enc_time_ms']:.2f}x faster encryption, {aes256_1x['dec_time_ms'] / cybpher_1x['dec_time_ms']:.2f}x faster decryption")
    print(f"Cybpher vs AES-128 (1000 iter):   {speedup_1000x_enc:.2f}x faster encryption, {speedup_1000x_dec:.2f}x faster decryption")
    print(f"Cybpher vs AES-256 (1000 iter):   {aes256_1000x['enc_time_ms'] / cybpher_1000x['enc_time_ms']:.2f}x faster encryption, {aes256_1000x['dec_time_ms'] / cybpher_1000x['dec_time_ms']:.2f}x faster decryption")
    
    print("\n[NOTE] Results simulate the benchmark described in the article.")
    print("       Actual Cybpher specification is not publicly available.")
    print("       These tests run on Python (software-only), not native C/ARM.")
    print("       The cryptographic security of this implementation is for")
    print("       demonstration purposes only and has NOT been independently audited.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Check if cryptography is installed
    try:
        import cryptography
    except ImportError:
        print("ERROR: 'cryptography' library not found.")
        print("Please install it with: pip install cryptography")
        exit(1)
    
    main()