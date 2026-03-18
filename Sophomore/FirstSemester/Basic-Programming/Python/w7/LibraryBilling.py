from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import csv
from typing import List, Dict, Tuple

# ---- 規則常數 ----
CATEGORY_DAILY = {
    "參考書": 25,
    "熱門新書": 20,
    "普通藏書": 10,
    "期刊": 8,
    "其他": 12,
}
IDENTITY_FACTOR = {"student": 0.9, "staff": 1.0, "guest": 1.1}

OVERDUE_FEE = 30          # 逾期手續費（整筆）
ECO_BAG_DISCOUNT = 5      # 自備袋折抵（整筆，最低不低於 0）


@dataclass
class BorrowRecord:
    date: str
    title: str
    category: str
    days: int
    identity: str
    overdue: str  # 'Y' or 'N'
    eco_bag: str  # 'Y' or 'N'

    # 計算欄位（流程：小計 -> 乘身分 -> 扣環保）
    daily_fee: int = 0
    subtotal_before_factor: float = 0.0
    after_identity: float = 0.0
    final_amount: float = 0.0  # 單筆最終金額（不四捨五入，彙總才四捨五入）

    def compute(self):
        # 1) 日費
        self.daily_fee = CATEGORY_DAILY.get(self.category, CATEGORY_DAILY["其他"])
        # 2) 小計（未乘身分、未扣環保）
        self.subtotal_before_factor = self.daily_fee * self.days + (OVERDUE_FEE if self.overdue.upper() == "Y" else 0)
        # 3) 乘身分係數
        factor = IDENTITY_FACTOR.get(self.identity.lower(), 1.0)
        self.after_identity = self.subtotal_before_factor * factor
        # 4) 扣自備袋（最低 0）
        discount = ECO_BAG_DISCOUNT if self.eco_bag.upper() == "Y" else 0
        self.final_amount = max(self.after_identity - discount, 0.0)


def round_half_up(n: float) -> int:
    """四捨五入到整數（商業常用，.5 一律進位）"""
    return int(Decimal(n).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def read_input() -> List[BorrowRecord]:
    print("=== 圖書館借閱結帳與報表系統 ===")
    print("輸入格式：日期(YYYY-MM-DD), 書名, 類別, 借日數, 身分(student/staff/guest), 是否逾期(Y/N), 是否自備袋(Y/N)")
    print("例：2025-10-15, 資料結構, 普通藏書, 7, student, N, Y")
    print("連續輸入多筆；空白行或輸入 END 結束。")
    print("基本日費：參考書25、熱門新書20、普通藏書10、期刊8、其他12；逾期+30；自備袋-5；身份係數：student×0.9 / staff×1.0 / guest×1.1")
    records: List[BorrowRecord] = []
    while True:
        line = input("> ").strip()
        if not line or line.upper() == "END":
            break
        # 允許有中文逗號，先統一成英文逗號
        line = line.replace("，", ",")
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 7:
            print("✗ 欄位數需為 7，請再輸入一次。")
            continue
        date, title, category, days_str, identity, overdue, eco_bag = parts
        try:
            days = int(days_str)
            if days < 0:
                raise ValueError
        except ValueError:
            print("✗ 借日數需為非負整數。")
            continue
        rec = BorrowRecord(
            date=date,
            title=title,
            category=category,
            days=days,
            identity=identity,
            overdue=overdue.upper(),
            eco_bag=eco_bag.upper(),
        )
        rec.compute()
        records.append(rec)
        print(f"✓ 已加入：{title}（{category}，{days} 天） → 最終金額 {rec.final_amount:.2f}")
    return records


def write_borrowings_csv(records: List[BorrowRecord], path: str = "borrowings.csv"):
    headers = [
        "日期", "書名", "類別", "日費", "借日數", "是否逾期", "身分", "是否自備袋",
        "該筆小計(未乘身分/未扣環保)", "乘身分後", "最終金額"
    ]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in records:
            w.writerow([
                r.date, r.title, r.category, r.daily_fee, r.days, r.overdue,
                r.identity, r.eco_bag,
                f"{r.subtotal_before_factor:.2f}",
                f"{r.after_identity:.2f}",
                f"{r.final_amount:.2f}",
            ])


def aggregate(records: List[BorrowRecord]) -> Dict:
    total_entries = len(records)
    total_days = sum(r.days for r in records)
    sum_subtotals = sum(r.subtotal_before_factor for r in records)
    sum_after_identity = sum(r.after_identity for r in records)
    sum_final = sum(r.final_amount for r in records)
    payable = max(round_half_up(sum_final), 0)

    # 極值（同額取先出現）
    max_rec, min_rec = None, None
    for r in records:
        if (max_rec is None) or (r.final_amount > max_rec.final_amount):
            max_rec = r
        if (min_rec is None) or (r.final_amount < min_rec.final_amount):
            min_rec = r

    # 類別彙整
    by_cat: Dict[str, Tuple[int, float]] = {}
    for r in records:
        key = r.category if r.category in CATEGORY_DAILY else "其他"
        cnt, amt = by_cat.get(key, (0, 0.0))
        by_cat[key] = (cnt + 1, amt + r.final_amount)

    # 客製訊息
    messages = []
    any_student = any(r.identity.lower() == "student" for r in records)
    any_eco = any(r.eco_bag.upper() == "Y" for r in records)
    if any_student and total_days >= 14:
        messages.append("學習馬拉松！請留意眼健康～")
    if any_eco:
        messages.append("環保＋1，感謝支持綠色校園！")

    return {
        "total_entries": total_entries,
        "total_days": total_days,
        "sum_subtotals": sum_subtotals,
        "sum_after_identity": sum_after_identity,
        "sum_final": sum_final,
        "payable": payable,
        "max_rec": max_rec,
        "min_rec": min_rec,
        "by_cat": by_cat,
        "messages": messages,
    }


def write_report_txt(agg: Dict, path: str = "report.txt"):
    lines = []
    lines.append("=== 統計摘要 ===")
    lines.append(f"總筆數：{agg['total_entries']}")
    lines.append(f"總天數：{agg['total_days']}")
    lines.append(f"整單小計總和（未乘係數、未扣環保）：{agg['sum_subtotals']:.2f}")
    lines.append(f"身份係數後金額總和：{agg['sum_after_identity']:.2f}")
    lines.append(f"應付總金額（四捨五入、且 ≥ 0）：{agg['payable']}")
    lines.append("")

    lines.append("=== 單筆極值（以最終金額比較，同額取最先出現） ===")
    if agg["max_rec"]:
        r = agg["max_rec"]
        lines.append(f"最高單筆：{r.final_amount:.2f}（{r.date} / {r.title}）")
    if agg["min_rec"]:
        r = agg["min_rec"]
        lines.append(f"最低單筆：{r.final_amount:.2f}（{r.date} / {r.title}）")
    lines.append("")

    lines.append("=== 各類別彙整（總本數、總金額） ===")
    for cat, (cnt, amt) in agg["by_cat"].items():
        lines.append(f"{cat}：{cnt} 本，{amt:.2f} 元")
    lines.append("")

    lines.append("=== 客製化訊息 ===")
    if agg["messages"]:
        for m in agg["messages"]:
            lines.append(f"- {m}")
    else:
        lines.append("- （無）")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    records = read_input()
    if not records:
        print("沒有輸入任何資料，程式結束。")
        return
    write_borrowings_csv(records, "borrowings.csv")
    agg = aggregate(records)
    write_report_txt(agg, "report.txt")
    print("\n已輸出：borrowings.csv、report.txt")
    print(f"應付總金額（四捨五入）：{agg['payable']}")


if __name__ == "__main__":
    main()