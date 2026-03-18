declare function describe(name: string, fn: () => void): void;
declare function beforeEach(fn: () => void): void;
declare function it(name: string, fn: () => void): void;
declare function expect(val: unknown): any;

// ── 型別定義 ──────────────────────────────────────────────────────

/** 矩陣座標 */
interface Coord {
  row: number;
  col: number;
}

/** 加密/解密結果物件 */
interface CipherResult {
  /** 輸出字串（加密後的密文 或 解密後含填充字元的明文） */
  output: string;
  /**
   * 移除填充字元（`*` 與 `_`）後的明文。
   * 僅在解密時有意義；加密時與 output 相同。
   */
  stripped: string;
  /** 分組後的字元對（供除錯用） */
  pairs: string[];
}

const CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*.,?_ ";
const MATRIX_SIZE = 7;

class Matrix49Cipher {
  /** 7×7 加密矩陣 */
  private readonly matrix: string[][];
  /** 字元 → 座標的快速查表 */
  private readonly posMap: Map<string, Coord>;
  /** 初始向量 (0~6) */
  private readonly iv: number;

  constructor(keyword: string, iv: number) {
    // 驗證 IV
    if (!Number.isInteger(iv) || iv < 0 || iv > 6) {
      throw new Error(`非法 IV "${iv}"：IV 必須為 0~6 的整數。`);
    }
    this.iv = iv;

    // 驗證 keyword 字元
    const kwUpper = keyword.toUpperCase();
    this.validateChars(kwUpper, "Keyword");

    // 生成矩陣
    this.matrix = this.buildMatrix(kwUpper);
    this.posMap = this.buildPosMap(this.matrix);
  }

  // ── 私有方法 ────────────────────────────────────────────────────

  private validateChars(text: string, label: string): void {
    for (const ch of text) {
      if (!CHARSET.includes(ch)) {
        throw new Error(
          `${label} 含有非法字元 "${ch}"：Matrix-49 僅接受 A-Z、0-9 及特殊符號。`
        );
      }
    }
  }

  private buildMatrix(kwUpper: string): string[][] {
    const seen = new Set<string>();
    const chars: string[] = [];

    // 先填 keyword（去重）
    for (const ch of kwUpper) {
      if (!seen.has(ch)) {
        seen.add(ch);
        chars.push(ch);
      }
    }
    // 再補齊字元集中未使用的字元
    for (const ch of CHARSET) {
      if (!seen.has(ch)) {
        seen.add(ch);
        chars.push(ch);
      }
    }

    // 切割成 7×7
    const mat: string[][] = [];
    for (let r = 0; r < MATRIX_SIZE; r++) {
      mat.push(chars.slice(r * MATRIX_SIZE, (r + 1) * MATRIX_SIZE));
    }
    return mat;
  }

  private buildPosMap(mat: string[][]): Map<string, Coord> {
    const map = new Map<string, Coord>();
    for (let r = 0; r < MATRIX_SIZE; r++) {
      for (let c = 0; c < MATRIX_SIZE; c++) {
        map.set(mat[r][c], { row: r, col: c });
      }
    }
    return map;
  }

  private mod(n: number): number {
    return ((n % MATRIX_SIZE) + MATRIX_SIZE) % MATRIX_SIZE;
  }

  private getCoord(ch: string): Coord {
    const coord = this.posMap.get(ch);
    if (coord === undefined) {
      throw new Error(`字元 "${ch}" 不在矩陣中，無法加解密。`);
    }
    return coord;
  }

  private padAndGroup(text: string): [string, string][] {
    const chars = text.split("");
    const padded: string[] = [];
    let fillerIndex = 0; // 0 → '*', 1 → '_', 輪替
    let i = 0;

    while (i < chars.length) {
      padded.push(chars[i]);

      if (i + 1 < chars.length) {
        if (chars[i] === chars[i + 1]) {
          // 同組相同字元：插入填充符號，不消耗下一個字元
          padded.push(fillerIndex % 2 === 0 ? "*" : "_");
          fillerIndex++;
          // 不推進 i+1，下一輪繼續處理 chars[i+1]
        } else {
          // 正常配對
          padded.push(chars[i + 1]);
          i++;
        }
      }
      i++;
    }

    // 奇數長度補 '_'
    if (padded.length % 2 !== 0) {
      padded.push("_");
    }

    // 切成字元對
    const pairs: [string, string][] = [];
    for (let j = 0; j < padded.length; j += 2) {
      pairs.push([padded[j], padded[j + 1]]);
    }
    return pairs;
  }

  private encryptPair(a: string, b: string, delta: number): [string, string] {
    const { row: r1, col: c1 } = this.getCoord(a);
    const { row: r2, col: c2 } = this.getCoord(b);

    let nr1: number, nc1: number, nr2: number, nc2: number;

    if (c1 === c2) {
      // 同行（Same Column）：列向下位移
      nr1 = this.mod(r1 + 1 + delta); nc1 = c1;
      nr2 = this.mod(r2 + 2 + delta); nc2 = c2;
    } else if (r1 === r2) {
      // 同列（Same Row）：欄向右位移
      nr1 = r1; nc1 = this.mod(c1 + 1 + delta);
      nr2 = r2; nc2 = this.mod(c2 + 2 + delta);
    } else {
      // 矩陣對角（Rectangle）：交換欄，列加 delta
      nr1 = this.mod(r1 + delta); nc1 = c2;
      nr2 = this.mod(r2 + delta); nc2 = c1;
    }

    return [this.matrix[nr1][nc1], this.matrix[nr2][nc2]];
  }

  private decryptPair(a: string, b: string, delta: number): [string, string] {
    const { row: r1, col: c1 } = this.getCoord(a);
    const { row: r2, col: c2 } = this.getCoord(b);

    let nr1: number, nc1: number, nr2: number, nc2: number;

    if (c1 === c2) {
      // 同行（Same Column）：列向上還原
      nr1 = this.mod(r1 - 1 - delta); nc1 = c1;
      nr2 = this.mod(r2 - 2 - delta); nc2 = c2;
    } else if (r1 === r2) {
      // 同列（Same Row）：欄向左還原
      nr1 = r1; nc1 = this.mod(c1 - 1 - delta);
      nr2 = r2; nc2 = this.mod(c2 - 2 - delta);
    } else {
      // 矩陣對角（Rectangle）：交換欄，列減 delta
      nr1 = this.mod(r1 - delta); nc1 = c2;
      nr2 = this.mod(r2 - delta); nc2 = c1;
    }

    return [this.matrix[nr1][nc1], this.matrix[nr2][nc2]];
  }

  public encrypt(plaintext: string): CipherResult {
    // 統一轉大寫（空格保留為空格）
    const upper = plaintext.toUpperCase();
    this.validateChars(upper, "明文");

    // 填充與分組
    const pairs = this.padAndGroup(upper);
    const cipherChars: string[] = [];

    for (let k = 0; k < pairs.length; k++) {
      // 動態位移量 delta = (IV + k) % 7
      const delta = (this.iv + k) % MATRIX_SIZE;
      const [ca, cb] = this.encryptPair(pairs[k][0], pairs[k][1], delta);
      cipherChars.push(ca, cb);
    }

    return {
      output: cipherChars.join(""),
      stripped: cipherChars.join(""), // 密文不需移除填充
      pairs: pairs.map(([a, b]) => a + b),
    };
  }

  public decrypt(ciphertext: string): CipherResult {
    if (ciphertext.length % 2 !== 0) {
      throw new Error("密文長度必須為偶數。");
    }
    this.validateChars(ciphertext, "密文");

    const pairs: [string, string][] = [];
    for (let j = 0; j < ciphertext.length; j += 2) {
      pairs.push([ciphertext[j], ciphertext[j + 1]]);
    }

    const plainChars: string[] = [];
    for (let k = 0; k < pairs.length; k++) {
      const delta = (this.iv + k) % MATRIX_SIZE;
      const [pa, pb] = this.decryptPair(pairs[k][0], pairs[k][1], delta);
      plainChars.push(pa, pb);
    }

    const output = plainChars.join("");
    return {
      output,
      // 移除加密時插入的填充字元 '*' 與 '_'（尾端補位的 '_' 也一併去除）
      stripped: output.replace(/[*_]/g, ""),
      pairs: pairs.map(([a, b]) => a + b),
    };
  }

  public printMatrix(): void {
    console.log("=== Matrix-49 (7×7) ===");
    this.matrix.forEach((row, i) => {
      console.log(`Row ${i}: [${row.map(c => c === " " ? "SPC" : c).join(", ")}]`);
    });
  }
}

// ── 測試 ─────────────────────────────────────────

describe("Matrix49Cipher", () => {
  const KEYWORD = "CRYPTO_2026!";
  const IV = 3;
  const PLAINTEXT = "Hello World 123";
  const EXPECTED_CIPHER = "EJYLB77V_P5E! 3C";

  let cipher: Matrix49Cipher;

  beforeEach(() => {
    cipher = new Matrix49Cipher(KEYWORD, IV);
  });

  it("應正確加密明文並符合預期密文", () => {
    const { output } = cipher.encrypt(PLAINTEXT);
    expect(output).toBe(EXPECTED_CIPHER);
  });

  it("解密後應還原為填充後的明文（含填充字元）", () => {
    const { output: encrypted } = cipher.encrypt(PLAINTEXT);
    const { output: decrypted, stripped } = cipher.decrypt(encrypted);
    expect(decrypted).toBe("HEL*LO WORLD 123");
    expect(stripped).toBe(PLAINTEXT.toUpperCase());
  });

  it("加解密應為互逆操作（round-trip）", () => {
    const { output: encrypted } = cipher.encrypt(PLAINTEXT);
    const { stripped } = cipher.decrypt(encrypted);
    expect(stripped).toBe(PLAINTEXT.toUpperCase());
  });

  it("非法 IV 應拋出 Error", () => {
    expect(() => new Matrix49Cipher(KEYWORD, 7)).toThrow("非法 IV");
    expect(() => new Matrix49Cipher(KEYWORD, -1)).toThrow("非法 IV");
  });

  it("明文含非法字元應拋出 Error", () => {
    expect(() => cipher.encrypt("HELLO~WORLD")).toThrow("非法字元");
  });
});
