DRINK_PRICE = {
    "blacktea": {"s": 25, "m": 30, "l": 35},
    "greentea": {"s": 30, "m": 35, "l": 40},
    "milktea":  {"s": 40, "m": 45, "l": 50},
}

TOPPING_PRICE = {
    "boba": 10,
    "pudding": 15,
    "none": 0,
}

IDENTITY_DISCOUNT = {
    "student": 0.95,
    "teacher": 0.90,
    "guest": 1.00,
}

DRINK_NAME = {"blacktea": "BlackTea", "greentea": "GreenTea", "milktea": "MilkTea"}
SIZE_NAME  = {"s": "S", "m": "M", "l": "L"}

print("===校園飲料快點===\n")

print(" 價目表")
print("飲料")
sizes = ["s", "m", "l"]
header = f"{'品項':<10}" + "".join([f"{SIZE_NAME[s]:>5}" for s in sizes])
print(header)
for dkey in DRINK_PRICE:
    row = f"{DRINK_NAME[dkey]:<10}" + "".join([f"{DRINK_PRICE[dkey][s]:>5}" for s in sizes])
    print(row)

print("\n配料")
for tkey, price in TOPPING_PRICE.items():
    sign = "+" if price >= 0 else ""
    print(f"{tkey:<8} {sign}{price}")

print("\n折扣")
for ikey, rate in IDENTITY_DISCOUNT.items():
    print(f"{ikey}: {int(rate*100)}%")

name = input("\n請輸入您的姓名： ").strip()
identity = input("請輸入您的身份（student/teacher/guest）： ").strip().lower()
if identity not in IDENTITY_DISCOUNT:
    print("⚠ 未知身份，將以 guest 計算。")
    identity = "guest"

orders = []

for i in range(1, 4):
    print(f"\n請輸入您的第{i}項飲料選擇（直接按 ENTER 跳過此筆）：")
    drink = input("飲料（blacktea/greentea/milktea）：").strip().lower()
    if drink == "":
        print("（已跳過此筆）")
        continue

    if drink not in DRINK_PRICE:
        print(f"⚠ 無效飲料: {drink}，此筆作廢。")
        continue

    size = input("尺寸（s/m/l）：").strip().lower()
    if size not in DRINK_PRICE[drink]:
        print(f"⚠ 無效尺寸: {size}，此筆作廢。")
        continue

    topping = input("配料（boba/pudding/none）：").strip().lower()
    if topping not in TOPPING_PRICE:
        print(f"⚠ 無效配料: {topping}，此筆作廢。")
        continue

    qty_str = input("數量（請輸入整數）：").strip()
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
    except:
        print(f"⚠ 無效數量: {qty_str}，此筆作廢。")
        continue

    orders.append({"drink": drink, "size": size, "topping": topping, "qty": qty})

if not orders:
    print("\n⚠ 您未選擇任何飲料。歡迎下次再來！")
else:
    print("\n===訂單明細===")
    print(f"顧客姓名: {name}")
    print(f"身份: {identity}")

    line_header = f"{'品項':<10}{'尺寸':<6}{'配料':<10}{'數量':<6}{'單價':<10}{'小計':<8}"
    print(line_header)
    print("-" * len(line_header))

    subtotal = 0
    for od in orders:
        base = DRINK_PRICE[od["drink"]][od["size"]]
        top = TOPPING_PRICE[od["topping"]]
        unit = base + top
        line_total = unit * od["qty"]
        subtotal += line_total
        print(f"{DRINK_NAME[od['drink']]:<10}{SIZE_NAME[od['size']]:<6}{od['topping']:<10}"
              f"{od['qty']:<6}{unit:<10}{line_total:<8}")

    discount_rate = IDENTITY_DISCOUNT.get(identity, 1.00)
    final_amount = round(subtotal * discount_rate)

    print("-" * len(line_header))
    print(f"{'小計':<42}{subtotal:<8}")
    print(f"折扣: x {discount_rate:.2f}")
    print(f"{'應付金額':<42}{final_amount:<8}")

    if identity == "student":
        msg = "祝你課業順利！"
    elif identity == "teacher":
        msg = "辛苦了，工作順心！"
    else:
        msg = "祝您有個美好的一天！"

    print(f"\n謝謝 {name}，{msg}")