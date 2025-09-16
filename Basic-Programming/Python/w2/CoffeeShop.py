menu = {
    "Latte": {"小": 40, "中": 50, "大": 60},
    "Americano": {"小": 35, "中": 45, "大": 55},
    "Mocha": {"小": 50, "中": 60, "大": 70}
}

print("====== 咖啡店菜單 ======")
print(f"{'品項':<10}{'小杯':<6}{'中杯':<6}{'大杯':<6}")
print("-" * 36)
for drink, sizes in menu.items():
    print(f"{drink:<12}{sizes['小']:<8}{sizes['中']:<8}{sizes['大']:<8}")
print("=======================\n")

name = input("請輸入您的姓名： ")

print("請輸入訂單 (格式: 品項-大小-數量，多品項以空白分隔)")
print("例如: Latte-中-2 Americano-小-1 Mocha-大-3")
order_input = input("輸入訂單： ")

orders = order_input.split()
total = 0
print("\n====== 訂單明細 ======")

for item in orders:
    try:
        drink, size, qty = item.split("-")
        qty = int(qty)

        if drink in menu and size in menu[drink]:
            price = menu[drink][size]
            subtotal = price * qty
            total += subtotal
            print(f"{drink:<10}{size:<3} x{qty:<2}  單價:{price}元  小計:{subtotal}元")
        else:
            print(f"⚠ 無效品項或大小: {item}")
    except ValueError:
        print(f"⚠ 格式錯誤: {item}")

print("=======================")
print(f"顧客姓名: {name}")
print(f"總金額: {total} 元")
print(f"謝謝 {name} 的訂購！祝您有美好的一天！")
