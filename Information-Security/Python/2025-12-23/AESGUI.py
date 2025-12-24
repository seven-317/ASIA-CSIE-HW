from __future__ import annotations

import base64
import os
import time
from typing import List

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

import matplotlib.pyplot as plt

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# ===================== AES 參數 =====================
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
PBKDF2_ITERATIONS = 200_000


# ===================== 加解密核心 =====================
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_once(plain_text: str, password: str) -> str:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)

    return base64.b64encode(salt + nonce + ciphertext).decode()


def decrypt_once(cipher_text: str, password: str) -> str:
    raw = base64.b64decode(cipher_text)
    salt = raw[:SALT_LEN]
    nonce = raw[SALT_LEN:SALT_LEN + NONCE_LEN]
    ciphertext = raw[SALT_LEN + NONCE_LEN:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
    except InvalidTag:
        raise ValueError("密碼錯誤或資料遭竄改")


# ===================== GUI =====================
class AESApp(ttk.Window):
    def __init__(self):
        super().__init__(title="AES-256-GCM 加解密效能測試", themename="darkly", size=(900, 600))

        self.encrypted_sample = ""

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="明文輸入").pack(anchor=W)
        self.plain_entry = ttk.Text(frame, height=3)
        self.plain_entry.pack(fill=X, pady=5)

        ttk.Label(frame, text="密碼").pack(anchor=W)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill=X, pady=5)

        ttk.Button(frame, text="執行加解密效能測試", bootstyle=SUCCESS, command=self.run_test).pack(pady=10)

        self.result_box = ttk.Text(frame, height=18)
        self.result_box.pack(fill=BOTH, expand=True)

    def run_test(self):
        plain = self.plain_entry.get("1.0", "end").strip()
        password = self.password_entry.get().strip()

        if not plain or not password:
            messagebox.showerror("錯誤", "請輸入明文與密碼")
            return

        encrypt_times: List[float] = []
        decrypt_times: List[float] = []

        self.result_box.delete("1.0", "end")

        # ===== 加密測試 =====
        for i in range(20):
            start = time.perf_counter()
            cipher = encrypt_once(plain, password)
            elapsed = (time.perf_counter() - start) * 1000
            encrypt_times.append(elapsed)
            self.encrypted_sample = cipher
            self.result_box.insert("end", f"加密第 {i+1:02d} 次：{elapsed:.3f} ms\n")

        self.result_box.insert("end", f"\n加密平均時間：{sum(encrypt_times)/20:.3f} ms\n\n")

        # ===== 解密測試 =====
        for i in range(20):
            start = time.perf_counter()
            decrypt_once(self.encrypted_sample, password)
            elapsed = (time.perf_counter() - start) * 1000
            decrypt_times.append(elapsed)
            self.result_box.insert("end", f"解密第 {i+1:02d} 次：{elapsed:.3f} ms\n")

        self.result_box.insert("end", f"\n解密平均時間：{sum(decrypt_times)/20:.3f} ms\n")

        self.draw_chart(encrypt_times, decrypt_times)

    def draw_chart(self, enc: List[float], dec: List[float]):
        plt.figure(figsize=(8, 4))
        plt.plot(enc, label="Encrypt Time (ms)", marker="o")
        plt.plot(dec, label="Decrypt Time (ms)", marker="s")
        plt.xlabel("Iteration")
        plt.ylabel("Time (ms)")
        plt.title("AES-256-GCM Encryption / Decryption Performance")
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    app = AESApp()
    app.mainloop()
