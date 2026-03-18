from secrets import randbits, randbelow
from hashlib import sha256
from math import gcd
from textwrap import shorten

# ---------- Miller-Rabin 機率質數測試 ----------
def _try_composite(a, d, n, s):
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return False
    return True

def is_probable_prime(n, k=16):
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(k):
        a = randbelow(n - 3) + 2
        if _try_composite(a, d, n, s):
            return False
    return True

def gen_prime(bits=256):
    while True:
        n = (1 << (bits - 1)) | randbits(bits - 1) | 1
        if is_probable_prime(n):
            return n

def gen_safe_prime(bits=256):
    # 找 q 為質數、p = 2q + 1 也為質數
    while True:
        q = gen_prime(bits - 1)
        p = 2 * q + 1
        if is_probable_prime(p):
            return p, q

def find_generator(p, q):
    # 對 safe prime p=2q+1，挑 g 使得 g^2 != 1 且 g^q != 1 (mod p)
    for g in range(2, p - 1):
        if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
            return g
    raise RuntimeError("No generator found")

# ---------- 工具 ----------
def modinv(a, m):
    # Python 3.8+ 可直接用 pow(a, -1, m)
    if gcd(a, m) != 1:
        raise ValueError("No modular inverse")
    return pow(a, -1, m)

def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")

def int_to_bytes(n: int) -> bytes:
    L = (n.bit_length() + 7) // 8 or 1
    return n.to_bytes(L, "big")

# ---------- 金鑰 ----------
def elgamal_keygen(p: int, g: int):
    x = randbelow(p - 3) + 2            # 私鑰
    y = pow(g, x, p)                    # 公鑰 y = g^x mod p
    return x, y

# ---------- 加解密 ----------
def elgamal_encrypt(m: int, p: int, g: int, y: int):
    # 每次加密都抽新 k，並確保 gcd(k, p-1)=1（以利簽章場景計算 k^{-1}）
    while True:
        k = randbelow(p - 3) + 2
        if gcd(k, p - 1) == 1:
            break
    c1 = pow(g, k, p)
    c2 = (m * pow(y, k, p)) % p
    return (c1, c2), k

def elgamal_decrypt(cipher, p: int, x: int) -> int:
    c1, c2 = cipher
    s = pow(c1, x, p)
    s_inv = modinv(s, p)
    return (c2 * s_inv) % p

# ---------- 簽章/驗證（訊息先做 SHA-256 再 mod p-1） ----------
def elgamal_sign(message: bytes, p: int, g: int, x: int):
    H = int.from_bytes(sha256(message).digest(), "big") % (p - 1)
    while True:
        k = randbelow(p - 3) + 2
        if gcd(k, p - 1) == 1:
            break
    r = pow(g, k, p)
    s = (modinv(k, p - 1) * (H - x * r)) % (p - 1)
    return (r, s), H

def elgamal_verify(message: bytes, signature, p: int, g: int, y: int) -> bool:
    r, s = signature
    if not (1 < r < p):
        return False
    H = int.from_bytes(sha256(message).digest(), "big") % (p - 1)
    v1 = (pow(y, r, p) * pow(r, s, p)) % p
    v2 = pow(g, H, p)
    return v1 == v2

# ---------- Demo ----------
# 生成 ~256-bit safe prime（示範用；實務請用 >= 2048-bit）
p, q = gen_safe_prime(bits=256)
g = find_generator(p, q)

# 金鑰
x, y = elgamal_keygen(p, g)

# 明文（bytes 會轉為 < p 的整數）
plaintext = b"Hello ElGamal! \xf0\x9f\x94\x90"  # 含 emoji 🔐
m_int = bytes_to_int(plaintext)
assert m_int < p, "Plaintext too large; choose larger p or encode/chunk."

# 同一明文加密兩次（k 不同 -> 密文不同）
ct1, k1 = elgamal_encrypt(m_int, p, g, y)
ct2, k2 = elgamal_encrypt(m_int, p, g, y)

# 解密
pt1 = int_to_bytes(elgamal_decrypt(ct1, p, x))
pt2 = int_to_bytes(elgamal_decrypt(ct2, p, x))

# 簽章 + 驗證
sig, H = elgamal_sign(plaintext, p, g, x)
ok_true = elgamal_verify(plaintext, sig, p, g, y)
ok_false = elgamal_verify(b"Hello Elgamal? \xf0\x9f\x94\x90", sig, p, g, y)  # 範例失敗

# 輔助縮寫輸出
def short_int(i: int, width=90):
    return shorten(hex(i), width=width, placeholder="...")

# 輸出
print("=== ElGamal 金鑰參數（示範用 ~256-bit safe prime；實務請用 >= 2048-bit） ===")
print(f"p bits: {p.bit_length()}")
print(f"p (hex, short): {short_int(p)}")
print(f"g: {g}")
print(f"x (私鑰, short): {short_int(x)}")
print(f"y (公鑰 = g^x mod p, short): {short_int(y)}\n")

print("=== 明文 ===")
print(f"plaintext (bytes): {plaintext!r}")
print(f"plaintext as int (short): {short_int(m_int)}\n")

print("=== 同明文加密兩次（k 不同 -> 密文不同） ===")
print(f"k1 (short): {short_int(k1)}")
print(f"ciphertext1 c1 (short): {short_int(ct1[0])}")
print(f"ciphertext1 c2 (short): {short_int(ct1[1])}")
print("---")
print(f"k2 (short): {short_int(k2)}")
print(f"ciphertext2 c1 (short): {short_int(ct2[0])}")
print(f"ciphertext2 c2 (short): {short_int(ct2[1])}")
print("兩次密文是否不同？", ct1 != ct2, "\n")

print("=== 解密 ===")
print("decrypt(ct1) == plaintext ? ", pt1 == plaintext)
print("decrypt(ct2) == plaintext ? ", pt2 == plaintext)
print(f"pt1 (bytes): {pt1!r}")
print(f"pt2 (bytes): {pt2!r}\n")

print("=== 簽章與驗證（SHA-256） ===")
print(f"H = SHA-256(m) mod (p-1) (short): {short_int(H)}")
print(f"signature (r, s) short: r={short_int(sig[0])}, s={short_int(sig[1])}")
print("verify(plaintext, sig) ->", ok_true)
print("verify(tampered,  sig) ->", ok_false, "\n")