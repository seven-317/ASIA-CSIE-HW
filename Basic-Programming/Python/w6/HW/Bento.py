import csv
import os

menu = {
    "雞腿飯": 95,
    "排骨飯": 90,
    "魚排飯": 100,
    "滷食飯": 85,
    "咖哩飯": 90,
}

discounts = {
    "student": 0.95,
    "staff": 1.0,
    "guest": 1.05
}

def input_order():
    orders = []
    while True:
        print("請輸入訂單資料：")
        date = input("日期 (YYYY-MM-DD): ")
        item = input("品項 (雞腿飯, 排骨飯, 魚排飯, 滷食飯, 咖哩飯): ")
        if item not in menu:
            print("品項錯誤，請重新選擇。")
            continue
        quantity = int(input("數量: "))
        add_size = input("是否加大(Y/N): ").upper() == "Y"
        is_self_bring = input("是否自備餐具(Y/N): ").upper() == "Y"
        identity = input("身份 (student/staff/guest): ").lower()

        price = menu[item]
        if add_size:
            price += 15
        if is_self_bring:
            price -= 5

        total_price = price * quantity
        discount = discounts.get(identity, 1)
        final_price = total_price * discount

        order = {
            "日期": date,
            "品項": item,
            "數量": quantity,
            "單價": price,
            "折扣後價格": final_price
        }
        orders.append(order)

        more = input("是否繼續輸入訂單 (Y/N): ").upper()
        if more != 'Y':
            break
    return orders

def save_orders_to_csv(orders):
    output_path = os.path.join(os.getcwd(), 'orders.csv')
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["日期", "品項", "數量", "單價", "折扣後價格"])
        writer.writeheader()
        for order in orders:
            writer.writerow(order)
    print(f"訂單明細已儲存到 {output_path}")

def save_report(orders):
    total_price = sum(order["折扣後價格"] for order in orders)
    total_items = len(orders)
    output_path = os.path.join(os.getcwd(), 'report.txt')
    with open(output_path, mode='w', encoding='utf-8') as file:
        file.write(f"總筆數: {total_items}\n")
        file.write(f"總金額: {total_price}\n")
        file.write(f"每筆訂單明細:\n")
        for order in orders:
            file.write(f"{order}\n")
    print(f"報告已儲存到 {output_path}")

def main():
    orders = input_order()
    save_orders_to_csv(orders)
    save_report(orders)
    print("訂單處理完畢，資料已儲存。")

if __name__ == "__main__":
    main()
