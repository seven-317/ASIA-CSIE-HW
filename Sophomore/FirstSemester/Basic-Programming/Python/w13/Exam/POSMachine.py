import csv

records = []

def calc_final(unit, qty, member):
    s = unit * qty
    return round(s * 0.95) if member == "Y" else round(s)

def show_record(i, r):
    print(f"#{i+1} {r['date']} {r['name']} {r['category']} {r['price']}x{r['qty']} 會員:{r['member']} 金額:{r['final']}")

def load_seed():
    try:
        with open("sales_seed.csv", encoding="utf-8") as f:
            for row in csv.reader(f):
                d = {
                    "date": row[0],
                    "name": row[1],
                    "category": row[2],
                    "price": float(row[3]),
                    "qty": int(row[4]),
                    "member": row[5].upper(),
                    "final": int(row[6])
                }
                records.append(d)
        print("載入完成。")
    except:
        print("無法載入 sales_seed.csv")

while True:
    func = input("請輸入功能：")
    if func == "0":
        print("Bye")
        break

    if func == "1":
        date = input("日期：")
        name = input("商品名稱：")
        category = input("類別：")
        unit = float(input("單價："))
        qty = int(input("數量："))
        member = input("是否會員(Y/N)：").strip().upper()
        final = calc_final(unit, qty, member)
        d = {
            "date": date,
            "name": name,
            "category": category,
            "price": unit,
            "qty": qty,
            "member": member,
            "final": final
        }
        records.append(d)
        print(f"新增成功！本筆金額：{final}")

    elif func == "2":
        if not records:
            print("無資料")
        else:
            for i, r in enumerate(records):
                show_record(i, r)
            print(f"TotalAmount: {sum(x['final'] for x in records)}")

    elif func == "3":
        s = input("請輸入要查的字：")
        match = [r for r in records if s in r["name"]]
        if not match:
            print("查無資料")
        else:
            for i, r in enumerate(match):
                show_record(i, r)

    elif func == "4":
        if not records:
            print("無資料")
        else:
            total = sum(x["final"] for x in records)
            print(f"Count: {len(records)} TotalAmount: {total} Avg: {round(total/len(records),1)}")
            mx = max(records, key=lambda x: x["final"])
            mn = min(records, key=lambda x: x["final"])
            print(f"Max: {mx['final']} ({mx['name']})  Min: {mn['final']} ({mn['name']})")
            cat = {}
            for r in records:
                cat.setdefault(r["category"], 0)
                cat[r["category"]] += r["final"]
            print("By Category:")
            for k,v in cat.items():
                print(f"{k}: {v}")

    elif func == "5":
        with open("sales.csv","w",newline="",encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["日期","商品名稱","類別","單價","數量","會員","金額"])
            for r in records:
                w.writerow([r["date"],r["name"],r["category"],r["price"],r["qty"],r["member"],r["final"]])

        total = sum(x["final"] for x in records)
        mx = max(records, key=lambda x: x["final"])
        mn = min(records, key=lambda x: x["final"])
        cat = {}
        for r in records:
            cat.setdefault(r["category"], 0)
            cat[r["category"]] += r["final"]

        with open("report.txt","w",encoding="utf-8") as f:
            f.write("--- Summary ---\n")
            f.write(f"Count: {len(records)}\n")
            f.write(f"TotalAmount: {total}\n")
            f.write(f"Avg: {round(total/len(records),1)}\n")
            f.write(f"Max: {mx['final']} ({mx['name']})\n")
            f.write(f"Min: {mn['final']} ({mn['name']})\n")
            f.write("By Category:\n")
            for k,v in cat.items():
                f.write(f"{k}: {v}\n")

        print("已輸出 sales.csv 與 report.txt")

    elif func == "6":
        load_seed()

    else:
        print("功能錯誤")
