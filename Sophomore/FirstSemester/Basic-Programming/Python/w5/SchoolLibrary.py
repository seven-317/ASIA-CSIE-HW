def discount(condition):
    if condition >= 90:
        return 0.9
    elif condition >= 80:
        return 0.85
    elif condition >= 60:
        return 0.8
    else:
        return 0.7

def main():
    print("=== 校園二手書交換平台 ===")
    print("輸入格式：日期, 書名, 類別, 定價, 成色(0~100), 數量, 身分(student/staff/guest)")
    print("範例：2025-09-26, Python基礎, CS, 450, 85, 2, student")
    print("輸入空白行或 END 結束\n")

    orders = []
    while True:
        line = input(">>> ").strip()
        if line == "" or line.upper() == "END":
            break
        try:
            date, name, category, price, cond, qty, identity = [x.strip() for x in line.split(",")]
            price = float(price)
            cond = float(cond)
            qty = int(qty)
            identity = identity.lower()
            if identity not in ["student", "staff", "guest"]:
                print("⚠️ 身分錯誤，請輸入 student/staff/guest")
                continue
            each = round(price * discount(cond))
            total = each * qty
            orders.append({
                "日期": date,
                "書名": name,
                "類別": category,
                "定價": price,
                "成色": cond,
                "數量": qty,
                "身份": identity,
                "每本成交價": each,
                "小計": total
            })
        except Exception as e:
            print("⚠️ 格式錯誤：", e)

    if not orders:
        print("無資料，程式結束。")
        return

    identity = orders[-1]["身份"]
    coef = {"student": 0.97, "staff": 1.00, "guest": 1.05}[identity]

    print("\n=== 逐筆明細 ===")
    for o in orders:
        print(f"{o['日期']} {o['書名']} 類別:{o['類別']} 定價:{o['定價']} 成色:{o['成色']} "
              f"數量:{o['數量']} 每本成交價:{o['每本成交價']} 小計:{o['小計']}")

    total_lines = len(orders)
    total_books = sum(o["數量"] for o in orders)
    subtotal = sum(o["小計"] for o in orders)
    grand_total = round(subtotal * coef)

    max_order = max(orders, key=lambda x: x["小計"])
    min_order = min(orders, key=lambda x: x["小計"])

    cat_stat = {}
    for o in orders:
        cat = o["類別"]
        if cat not in cat_stat:
            cat_stat[cat] = {"數量": 0, "金額": 0}
        cat_stat[cat]["數量"] += o["數量"]
        cat_stat[cat]["金額"] += o["小計"]

    print("\n=== 整體統計 ===")
    print(f"總筆數:{total_lines}  總本數:{total_books}")
    print(f"整單小計:{subtotal}")
    print(f"身分:{identity}  係數:{coef}")
    print(f"應付總金額:{grand_total}")

    print(f"\n最高單筆: {max_order['書名']} ({max_order['日期']}) 金額:{max_order['小計']}")
    print(f"最低單筆: {min_order['書名']} ({min_order['日期']}) 金額:{min_order['小計']}")

    print("\n=== 各類別統計 ===")
    for k, v in cat_stat.items():
        print(f"{k}: 本數={v['數量']} 金額={v['金額']}")

    print("\n=== 客製化訊息 ===")
    msg = {
        "student": "學生優惠已套用，祝你課業順利！📚",
        "staff": "感謝教職員支持校園循環書籍！🙌",
        "guest": "歡迎光臨，含手續費方案已套用。🙏"
    }[identity]
    print(msg)


if __name__ == "__main__":
    main()
