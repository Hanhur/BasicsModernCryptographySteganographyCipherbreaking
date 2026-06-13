# Задачи и упражнения
import random
import math
from itertools import product

# ---------- RSA helpers ----------
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def multiplicative_inverse(e, phi):
    # extended Euclidean algorithm
    d_old, d_new = 0, 1
    r_old, r_new = phi, e
    while r_new:
        q = r_old // r_new
        d_old, d_new = d_new, d_old - q * d_new
        r_old, r_new = r_new, r_old - q * r_new
    return d_old % phi

def is_prime(n, k = 5):
    # Miller-Rabin
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    # write n-1 = d * 2^s
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    # test k times
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1  # make odd and with highest bit 1
        if is_prime(p):
            return p

def generate_rsa_keys(prime_bits = 16):
    # small primes for demo (prime_bits ~ 16 => n ~ 32 bits)
    p = generate_prime(prime_bits)
    q = generate_prime(prime_bits)
    while q == p:
        q = generate_prime(prime_bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    # ensure gcd(e, phi) = 1
    while gcd(e, phi) != 1:
        e = random.randrange(3, phi, 2)
    d = multiplicative_inverse(e, phi)
    return (n, e), (n, d)

# ---------- MITM attack on RSA with small K ----------
def mitm_rsa_attack(c, e, n, L):
    """
    L = number of bits of the secret key K
    We assume K = A * B, where A, B < 2 ** (L // 2)
    Returns K if found, else None.
    """
    half_bits = L // 2
    max_val = 1 << half_bits   # 2**(L/2)
    
    # Step 1: compute A^e mod n for all A in [1, max_val-1]
    # Store in dictionary: value -> A
    table = {}
    print(f"[*] Building table with {max_val - 1} entries...")
    for A in range(1, max_val):
        val = pow(A, e, n)
        table[val] = A
    
    # Step 2: for each B in [1, max_val-1], compute need = c * inv(B^e) mod n
    # and check if need in table. If yes, then K = A*B.
    print(f"[*] Trying {max_val - 1} B values...")
    for B in range(1, max_val):
        # Compute B^e mod n
        B_e = pow(B, e, n)
        # Compute inverse of B^e modulo n
        try:
            inv_B_e = pow(B_e, -1, n)  # Python 3.8+ supports modular inverse with -1
        except ValueError:
            # B_e not invertible mod n (very unlikely if gcd(B_e, n)=1)
            continue
        need = (c * inv_B_e) % n
        if need in table:
            A = table[need]
            K_candidate = A * B
            # Verify it's correct
            if pow(K_candidate, e, n) == c:
                return K_candidate
    return None

# ---------- Main demo ----------
def main():
    # Parameters
    L = 16           # key length in bits (for DES it's 56, but here small for speed)
    prime_bits = 16  # RSA modulus bits ~32, enough for this demo
    
    print("=== RSA with small secret key (known length) ===")
    print(f"Secret key length: {L} bits")
    
    # Generate RSA keys
    print("\n[1] Generating RSA keys...")
    (n, e), (n, d) = generate_rsa_keys(prime_bits)
    print(f"n = {n} (bits: {n.bit_length()})")
    print(f"e = {e}")
    
    # Generate random secret key K of exactly L bits (max bit length L)
    K = random.randrange(1 << (L - 1), 1 << L)  # L bits, highest bit 1
    print(f"\n[2] Secret key K (to be recovered): {K} (binary: {bin(K)[2:]})")
    
    # Encrypt K with RSA
    c = pow(K, e, n)
    print(f"Encrypted c = pow(K, e, n) = {c}")
    
    # Attack
    print(f"\n[3] Attacking: find K knowing only c, e, n, L = {L}")
    recovered = mitm_rsa_attack(c, e, n, L)
    
    if recovered is not None:
        print(f"\n[✓] Attack successful! Recovered K = {recovered}")
        if recovered == K:
            print("[✓] Matches original secret key.")
        else:
            print("[✗] Mismatch! Something went wrong.")
    else:
        print("\n[✗] Attack failed: K not found. (Try different L or increase range?)")
        
    print("\nNote: Attack complexity ~ O(2 ^ (L / 2)) operations.")
    print(f"Here L/2 = {L // 2}, so ~ {1 << (L // 2)} operations.")

if __name__ == "__main__":
    main()