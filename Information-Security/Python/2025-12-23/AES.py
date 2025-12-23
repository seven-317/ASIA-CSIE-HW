from __future__ import annotations

import base64
import os
from typing import Final

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# ====== 參數設定（可視需求調整，但不建議隨意降低） ======
SALT_LEN: Final[int] = 16          # PBKDF2 的 Salt 長度（建議 16 bytes 以上）
NONCE_LEN: Final[int] = 12         # AESGCM 建議 Nonce(IV) 長度為 12 bytes
KEY_LEN: Final[int] = 32           # AES-256 => 32 bytes
PBKDF2_ITERATIONS: Final[int] = 200_000  # PBKDF2 迭代次數（越高越慢但更抗暴力破解）


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    使用 PBKDF2HMAC(SHA256) 將使用者密碼衍生為 AES-256 金鑰。
    - password: 使用者原始密碼
    - salt: 隨機鹽值（每次加密都要不同）
    """
    if not password:
        raise ValueError("密碼不可為空。")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt(plain_text: str, password: str) -> str:
    """
    將明文加密並回傳 Base64 字串。
    流程：
    1) 隨機生成 Salt 與 Nonce
    2) 使用 PBKDF2HMAC(SHA256) 由 password+salt 衍生 AES-256 金鑰
    3) 使用 AES-256-GCM 加密（含完整性驗證）
    4) 輸出格式：Salt + Nonce + Ciphertext（Ciphertext 內含 GCM tag）
    5) 最終以 Base64 編碼回傳（方便儲存/傳輸）
    """
    if plain_text is None:
        raise ValueError("明文不可為 None。")

    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)

    # AESGCM.encrypt 會回傳：ciphertext || tag（tag 會附在尾端）
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), associated_data=None)

    packed = salt + nonce + ciphertext
    return base64.b64encode(packed).decode("utf-8")


def decrypt(encrypted_data: str, password: str) -> str:
    """
    將 Base64 字串解密回明文。
    流程：
    1) Base64 解碼取回 bytes
    2) 解析 Salt, Nonce, Ciphertext
    3) 重新衍生金鑰並用 AES-256-GCM 解密
    4) 若密碼錯誤或資料被竄改，會觸發 InvalidTag（代表驗證失敗）
    """
    if not encrypted_data:
        return "錯誤：加密資料為空，無法解密。"

    try:
        raw = base64.b64decode(encrypted_data.encode("utf-8"), validate=True)
    except Exception:
        return "錯誤：輸入不是有效的 Base64 格式。"

    # 至少要放得下 salt + nonce（ciphertext 最少還會包含 tag，空字串也會有 tag）
    min_len = SALT_LEN + NONCE_LEN + 16  # GCM tag 通常 16 bytes
    if len(raw) < min_len:
        return "錯誤：加密資料長度不足或格式不正確。"

    salt = raw[:SALT_LEN]
    nonce = raw[SALT_LEN:SALT_LEN + NONCE_LEN]
    ciphertext = raw[SALT_LEN + NONCE_LEN:]

    try:
        key = _derive_key(password, salt)
        aesgcm = AESGCM(key)
        plain_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        return plain_bytes.decode("utf-8")
    except InvalidTag:
        # 代表：密碼不對，或資料被改過（完整性驗證失敗）
        return "錯誤：解密失敗。可能是密碼錯誤，或資料已遭竄改。"
    except ValueError as e:
        # 例如密碼為空等
        return f"錯誤：{e}"
    except Exception:
        return "錯誤：解密時發生未知例外。"


if __name__ == "__main__":
    # ====== 測試案例：加密 -> 解密 -> 驗證 ======
    message = "這是一段要被 AES-256-GCM 保護的文字 ✅"
    password = "MyStrongPassword_123!"

    print("原始明文：", message)

    encrypted = encrypt(message, password)
    print("\n加密結果(Base64)：")
    print(encrypted)

    decrypted = decrypt(encrypted, password)
    print("\n解密結果：", decrypted)

    # 驗證解密是否一致
    if decrypted == message:
        print("\n✅ 驗證成功：解密內容與原文一致")
    else:
        print("\n❌ 驗證失敗：解密內容與原文不一致")

    # 額外測試：錯誤密碼
    wrong = decrypt(encrypted, "WrongPassword!")
    print("\n使用錯誤密碼解密：\n",wrong)
