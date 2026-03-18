const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const MODULUS = 36;

class PPVS36Cipher {
  private charToVal(ch: string): number {
    const idx = ALPHABET.indexOf(ch.toUpperCase());
    if (idx === -1) {
      throw new Error(
        `非法字元 "${ch}"：PPVS-36 僅接受 A-Z 與 0-9 的字元。`
      );
    }
    return idx;
  }

  private valToChar(val: number): string {
    return ALPHABET[val];
  }

  private mod(n: number, m: number): number {
    return ((n % m) + m) % m;
  }

  private perturbation(i: number): number {
    return i * i + i;
  }

  private validate(text: string, label: string): void {
    if (text.length === 0) {
      throw new Error(`${label}不得為空字串。`);
    }
    for (const ch of text.toUpperCase()) {
      if (ALPHABET.indexOf(ch) === -1) {
        throw new Error(
          `${label}含有非法字元 "${ch}"：PPVS-36 僅接受 A-Z 與 0-9。`
        );
      }
    }
  }

  public encrypt(plaintext: string, key: string): string {
    this.validate(plaintext, "明文");
    this.validate(key, "金鑰");

    const P = plaintext.toUpperCase();
    const K = key.toUpperCase();
    const L = K.length;
    let ciphertext = "";

    for (let i = 0; i < P.length; i++) {
      const p_i = this.charToVal(P[i]);           // 明文數值
      const k_i = this.charToVal(K[i % L]);       // 金鑰數值（循環使用）
      const d_i = this.perturbation(i);            // 擾動項 D_i = i² + i
      const c_i = this.mod(p_i + k_i + d_i, MODULUS); // 加密公式
      ciphertext += this.valToChar(c_i);
    }

    return ciphertext;
  }

  public decrypt(ciphertext: string, key: string): string {
    this.validate(ciphertext, "密文");
    this.validate(key, "金鑰");

    const C = ciphertext.toUpperCase();
    const K = key.toUpperCase();
    const L = K.length;
    let plaintext = "";

    for (let i = 0; i < C.length; i++) {
      const c_i = this.charToVal(C[i]);           // 密文數值
      const k_i = this.charToVal(K[i % L]);       // 金鑰數值（循環使用）
      const d_i = this.perturbation(i);            // 擾動項 D_i = i² + i
      const p_i = this.mod(c_i - k_i - d_i, MODULUS); // 解密公式
      plaintext += this.valToChar(p_i);
    }

    return plaintext;
  }
}

// ── 測試 ──────────────────────────────────────────────────────
// Plaintext: "GALAXY2026"  Key: "NOVA"
// 預期密文:  "TQCMU6TKF2"

const cipher = new PPVS36Cipher();
const plaintext = "GALAXY2026";
const key = "NOVA";
const expected = "TQCMU6TKF2";

const encrypted = cipher.encrypt(plaintext, key);
const decrypted = cipher.decrypt(encrypted, key);

console.log("=== PPVS-36 測試 ===");
console.log(`明文:     ${plaintext}`);
console.log(`金鑰:     ${key}`);
console.log(`加密結果: ${encrypted}`);
console.log(`預期密文: ${expected}`);
console.log(`加密驗證: ${encrypted === expected ? "✅ PASS" : "❌ FAIL"}`);
console.log(`解密結果: ${decrypted}`);
console.log(`解密驗證: ${decrypted === plaintext ? "✅ PASS" : "❌ FAIL"}`);
