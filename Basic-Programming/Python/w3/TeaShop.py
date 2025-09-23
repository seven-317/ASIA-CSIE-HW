DRINK_PRICE={
    "blacktea": {"s": 25, "m": 30, "l": 35},
    "greentea": {"s": 30, "m": 35, "l": 40},
    "milktea": {"s": 40, "m": 45, "l": 50},
}

TOPPING_PRICE={
    "boba": 10,
    "pudding": 15,
    "none": 0,
}

IDENTITY_DISCOUNT={
    "student": 0.95,
    "teacher": 0.90,
    "guest": 1.00,
}

print('===校園飲料快點===\n')
print(""" 價目表
飲料
品項     S   M   L
BlackTea 25 30 35
GreenTea 30 35 40
MilkTea 40 45 50

配料
boba +10
pudding +15
none +0

折扣
student: 95%
teacher: 90%
guest: 100%
""")
name = input('請輸入您的姓名： ').strip()
identity = input('請輸入您的身份（student/teacher/guest）： ').strip().lower()

orders=[]

for i in range(1,4):
    print(f'請輸入您的第{i}項飲料選擇（ENTER 跳過此筆）：')
    drink = input("飲料（blacktea/greentea/milktea）：").strip().lower()
    topping = input("配料（boba/pudding/none）：").strip().lower()
    qty_str = input("數量（請輸入整數）：").strip()

    if not (drink or size or topping or qty_str):
        continue
    if drink not in DRINK_PRICE:
        print(f'⚠ 無效飲料: {drink}')
        continue
    if size not in DRINK_PRICE[drink]:
        print(f'⚠ 無效尺寸: {size}')
        continue
    if topping not in TOPPING_PRICE:
        print(f'⚠ 無效配料: {topping}')
        continue
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
    except:
        print(f'⚠ 無效數量: {qty_str}')
        continue
    orders.append({"drink":drink, "size":size, "topping":topping, "qty":qty})

    if not orders:
        print('⚠ 您未選擇任何飲料，請重新輸入。')
        continue

print("\n===訂單明細===")
print(f"顧客姓名: {name}")
print(f"身份: {identity}")

header = f"{'品項':<10}{'尺寸':<6}{'配料':<10}{'數量':<6}{'單價':<10}{'小計':<8}"
print(header)
print("-" * len(header))

subtotal = 0
for order in orders:
    base = BASE_PRICE[order["drink"]][order["size"]]
    top = TOPPING_PRICE[order["topping"]]
    unit = base + top
    line_total = uni * od["qty"]
    subtotal += line_total

    print(f"{order['drink']:<10}{order['size'].upper():<6}{order['topping']:<10}{order['qty']:<6}{unit:<10}{line_total:<8}")

discount_rate = IDENTITY_DISCOUNT.get(identity, 1.00)
final_amount = round(subtotal * discount_rate)

print("-" * len(header))
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
