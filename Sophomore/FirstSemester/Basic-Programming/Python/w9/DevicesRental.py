# campus_rental_system.py
# 校園租借設備結帳與報表系統（含類別版）
# 標準函式庫即可執行：python3 campus_rental_system.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import csv
from typing import List, Dict, Tuple

# ---- 參數設定 ----
CATEGORY_RATE = {
    "視聽設備": 50,
    "資訊設備": 80,
    "體育器材": 40,
    "會議器材": 60,
    "其他": 30,
}

IDENTITY_FACTOR = {
    "student": Decimal("0.9"),
    "staff":   Decimal("1.0"),
    "guest":   Decimal("1.1"),
}

OVERTIME_FEE = Decimal("50")  # 逾時固定手續費
CSV_FILE = "rentals.csv"
REPORT_FILE = "report.txt"

def round_half_up(n: Decimal | float | int) -> int:
    """四捨五入到整數（ROUND_HALF_UP）。"""
    if not isinstance(n, Decimal):
        n = Decimal(str(n))
    return int(n.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

@dataclass
class RentalRecord:
    date: str                 # YYYY-MM-DD
    name: str                 # 設備名稱
    category: str             # 類別（需在 CATEGORY_RATE）
    hours: Decimal            # 租用時數
    identity: str             # student/staff/guest
    overtime: bool            # 是否逾時

    # 計算欄位（執行時計算）
    base_rate: Decimal = field(init=False)
    subtotal: Decimal = field(init=False)     # 含手續費，但未乘係數
    final_amount: int = field(init=False)     # 乘身分係數後、四捨五入（整數）

    def __post_init__(self):
        # 取得每小時單價
        self.base_rate = Decimal(str(CATEGORY_RATE[self.category]))

        # 基本租金
        base = self.base_rate * self.hours

        # 含手續費的小計
        self.subtotal = base + (OVERTIME_FEE if self.overtime else Decimal("0"))

        # 乘身分係數後四捨五入
        factor = IDENTITY_FACTOR[self.identity]
        self.final_amount = round_half_up(self.subtotal * factor)

def parse_input_line(line: str) -> RentalRecord:
    """
    解析一行輸入：
    日期(YYYY-MM-DD), 設備名稱, 類別, 租用時數, 身分(student/staff/guest), 是否逾時(Y/N)
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 6:
        raise ValueError("欄位數量應為 6。")

    date_str, name, category, hours_str, identity, overtime_str = parts

    # 驗證日期
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式錯誤，應為 YYYY-MM-DD。")

    # 類別驗證
    if category not in CATEGORY_RATE:
        raise ValueError(f"未知類別：「{category}」，允許：{', '.join(CATEGORY_RATE.keys())}")

    # 時數驗證
    try:
        hours = Decimal(hours_str)
        if hours <= 0:
            raise ValueError
    except Exception:
        raise ValueError("時數需為正數。")

    # 身分驗證
    identity = identity.lower()
    if identity not in IDENTITY_FACTOR:
        raise ValueError("身分需為 student/staff/guest。")

    # 逾時驗證
    overtime_str = overtime_str.upper()
    if overtime_str not in ("Y", "N"):
        raise ValueError("是否逾時需為 Y 或 N。")
    overtime = overtime_str == "Y"

    return RentalRecord(
        date=date_str, name=name, category=category,
        hours=hours, identity=identity, overtime=overtime
    )

def print_welcome():
    print("="*72)
    print("校園租借設備結帳與報表系統（含類別版）")
    print("- 可連續輸入多筆，輸入空白行或 END 結束")
    print("- 每筆 6 欄位以逗號分隔：")
    print("  日期(YYYY-MM-DD), 設備名稱, 類別, 租用時數, 身分(student/staff/guest), 是否逾時(Y/N)")
    print("  範例：2025-10-31, 投影機, 視聽設備, 5, student, N")
    print()
    print("類別與單價(每小時)：")
    for k, v in CATEGORY_RATE.items():
        print(f"  {k: <6} → {v}")
    print("="*72)

def collect_records() -> List[RentalRecord]:
    records: List[RentalRecord] = []
    while True:
        line = input("> 請輸入一筆資料（或按 Enter/輸入 END 結束）：").strip()
        if line == "" or line.upper() == "END":
            break
        try:
            rec = parse_input_line(line)
            records.append(rec)
        except Exception as e:
            print(f"  ❌ 輸入有誤：{e}")
    return records

def print_details(records: List[RentalRecord]):
    print("\n【明細表】（逐筆）")
    print("日期, 設備名稱, 類別, 時數, 逾時, 小計(含手續費/未乘係數), 應付金額(四捨五入)")
    for r in records:
        overtime_str = "Y" if r.overtime else "N"
        print(f"{r.date}, {r.name}, {r.category}, {r.hours}, {overtime_str}, "
              f"{r.subtotal}, {r.final_amount}")

def aggregate_by_category(records: List[RentalRecord]) -> Dict[str, Tuple[int, int]]:
    """
    回傳：{類別: (次數, 金額總和)}
    """
    agg: Dict[str, Tuple[int, int]] = {}
    for r in records:
        cnt, amt = agg.get(r.category, (0, 0))
        agg[r.category] = (cnt + 1, amt + r.final_amount)
    return agg

def print_statistics(records: List[RentalRecord]):
    print("\n【統計報表】")
    total_count = len(records)
    total_hours = sum((r.hours for r in records), Decimal("0"))
    total_amount = sum(r.final_amount for r in records)

    print(f"總筆數：{total_count}")
    print(f"總時數：{total_hours}")
    print(f"總金額：{total_amount}")

    if records:
        # 最高/最低金額
        highest = max(records, key=lambda r: r.final_amount)
        lowest = min(records, key=lambda r: r.final_amount)
        print(f"最高金額：{highest.final_amount}（{highest.date} / {highest.name}）")
        print(f"最低金額：{lowest.final_amount}（{lowest.date} / {lowest.name}）")

        # 類別彙整
        print("\n各類別彙整（次數 / 金額）")
        agg = aggregate_by_category(records)
        for cat in CATEGORY_RATE.keys():
            cnt, amt = agg.get(cat, (0, 0))
            print(f"  {cat: <6}：{cnt} 次 / {amt} 元")

        # 客製化訊息（至少 2 條）
        any_student = any(r.identity == "student" for r in records)
        any_overtime = any(r.overtime for r in records)
        if total_hours >= 20 and any_student:
            print("\n勤學好問！多使用公共設備很棒～")
        if any_overtime:
            print("提醒：請準時歸還設備以免罰金！")

def write_csv(records: List[RentalRecord], path: str = CSV_FILE):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "name", "category", "hours", "overtime",
                         "subtotal_including_fee", "final_amount"])
        for r in records:
            writer.writerow([
                r.date, r.name, r.category, str(r.hours),
                "Y" if r.overtime else "N",
                str(r.subtotal), r.final_amount
            ])

def write_report(records: List[RentalRecord], path: str = REPORT_FILE):
    total_count = len(records)
    total_hours = sum((r.hours for r in records), Decimal("0"))
    total_amount = sum(r.final_amount for r in records)

    lines = []
    lines.append("【統計摘要】")
    lines.append(f"總筆數：{total_count}")
    lines.append(f"總時數：{total_hours}")
    lines.append(f"總金額：{total_amount}")

    if records:
        highest = max(records, key=lambda r: r.final_amount)
        lowest = min(records, key=lambda r: r.final_amount)
        lines.append(f"最高金額：{highest.final_amount}（{highest.date} / {highest.name}）")
        lines.append(f"最低金額：{lowest.final_amount}（{lowest.date} / {lowest.name}）")

        lines.append("\n【各類別彙整】（次數 / 金額）")
        agg = aggregate_by_category(records)
        for cat in CATEGORY_RATE.keys():
            cnt, amt = agg.get(cat, (0, 0))
            lines.append(f"{cat}：{cnt} 次 / {amt} 元")

        any_student = any(r.identity == "student" for r in records)
        any_overtime = any(r.overtime for r in records)
        lines.append("\n【客製化訊息】")
        if total_hours >= 20 and any_student:
            lines.append("勤學好問！多使用公共設備很棒～")
        if any_overtime:
            lines.append("提醒：請準時歸還設備以免罰金！")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    print_welcome()
    records = collect_records()
    if not records:
        print("\n未輸入任何資料，程式結束。")
        return

    # 螢幕輸出
    print_details(records)
    print_statistics(records)

    # 檔案輸出
    write_csv(records, CSV_FILE)
    write_report(records, REPORT_FILE)
    print(f"\n已輸出：{CSV_FILE}、{REPORT_FILE}")

if __name__ == "__main__":
    main()
