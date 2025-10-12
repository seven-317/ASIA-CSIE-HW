

import sys
import os
import hashlib
from typing import Tuple

try:
    from Crypto.Cipher import DES
    from Crypto.Random import get_random_bytes
except Exception as e:
    print("Missing dependency. Please install PyCryptodome first:\n  pip install pycryptodome")
    sys.exit(1)

BLOCK_SIZE = 8  # DES block size (bytes)

def derive_des_key(secret: str) -> bytes:
    """
    Derive a fixed 8-byte DES key from an arbitrary-length secret string using SHA-256.
    (Takes first 8 bytes of the SHA-256 digest.)
    """
    return hashlib.sha256(secret.encode("utf-8")).digest()[:8]

def pad_pkcs7(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len

def unpad_pkcs7(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded data length.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid PKCS#7 padding.")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid PKCS#7 padding bytes.")
    return data[:-pad_len]

def encrypt_file(key: bytes, in_path: str, out_path: str) -> Tuple[int, str]:
    """Encrypt file at in_path -> out_path (binary). Prepends IV (8 bytes) to output."""
    with open(in_path, "rb") as f:
        plaintext = f.read()
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = DES.new(key, DES.MODE_CBC, iv)
    ct = cipher.encrypt(pad_pkcs7(plaintext, BLOCK_SIZE))
    # Store as: IV || ciphertext
    with open(out_path, "wb") as f:
        f.write(iv + ct)
    return len(ct), out_path

def decrypt_file(key: bytes, in_path: str, out_path: str) -> Tuple[int, str]:
    """Decrypt file at in_path (expects leading IV) -> out_path (binary)."""
    with open(in_path, "rb") as f:
        blob = f.read()
    if len(blob) < BLOCK_SIZE:
        raise ValueError("Ciphertext file is too short (missing IV).")
    iv, ct = blob[:BLOCK_SIZE], blob[BLOCK_SIZE:]
    if len(ct) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext length is not a multiple of block size.")
    cipher = DES.new(key, DES.MODE_CBC, iv)
    pt_padded = cipher.decrypt(ct)
    pt = unpad_pkcs7(pt_padded, BLOCK_SIZE)
    with open(out_path, "wb") as f:
        f.write(pt)
    return len(pt), out_path

def main():
    print("=== DES 檔案加解密工具 (DES-CBC, PKCS#7) ===")
    print("提示：先安裝相依套件 → pip install pycryptodome\n")

    # (二) 首先輸入 Secret Key。
    secret = input("請輸入 Secret Key：").strip()
    key = derive_des_key(secret)
    print("已產生 8-byte DES 金鑰（由 Secret Key 派生）。")

    # (三) 輸入欲加密之文字檔、檔名，再輸入欲保存密文之檔名。
    in_plain = input("請輸入欲加密之文字檔路徑：").strip()
    if not os.path.isfile(in_plain):
        print("找不到明文檔：", in_plain)
        sys.exit(1)
    out_cipher = input("請輸入欲保存密文之檔名（例如 output.des）：").strip() or "output.des"

    # (四) 靜待加密過程。
    try:
        ct_len, ct_path = encrypt_file(key, in_plain, out_cipher)
        print(f"加密完成 → {ct_path}（密文長度 {ct_len} bytes，檔案開頭包含 8-byte IV）")
    except Exception as e:
        print("加密失敗：", e)
        sys.exit(1)

    # (五) 是否解密 “Y” 或 “N”。
    choice = input("是否進行解密？（Y/N）：").strip().upper()
    if choice != "Y":
        # (六) 輸入 “N” 則程式結束
        print("程式結束。")
        return

    # (六) 螢幕顯示輸入欲解密之檔名。
    in_cipher = input("請輸入欲解密之檔名（例如 output.des）：").strip() or out_cipher

    # (七) 輸入保存解密資料之檔名。
    out_plain = input("請輸入保存解密資料之檔名（例如 recovered.txt）：").strip() or "recovered.txt"

    # (八) 靜待解密過程。
    try:
        pt_len, pt_path = decrypt_file(key, in_cipher, out_plain)
        print(f"解密完成 → {pt_path}（明文長度 {pt_len} bytes）")
    except Exception as e:
        print("解密失敗：", e)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已中止。")
