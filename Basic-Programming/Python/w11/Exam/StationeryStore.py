def calc_amount(pages, mode, size, duplex, student_type):
    if size == "A4":
        unit = 1 if mode == "bw" else 3
    else:
        unit = 2 if mode == "bw" else 6

    if duplex == "Y":
        unit *= 0.9

    if student_type == "s":
        unit *= 0.9
    elif student_type == "t":
        unit *= 1.1

    final = round(unit * pages)
    return unit, final


def print_all(tasks):
    if not tasks:
        print("尚無資料")
        return

    total = 0
    for t in tasks:
        print(f"{t['id']} ... 金額 {t['final']}")
        total += t["final"]

    print(f"這筆列印 TotalAmount: {total}")


def search_id(tasks, key):
    found = [t for t in tasks if key.lower() in t["id"].lower()]
    if found:
        f = found[0]
        print(f"找到1筆；第一筆：{f['id']} ... 金額 {f['final']}")
    else:
        print("查無資料")


def stats(tasks):
    if not tasks:
        print("無資料可統計")
        return

    count = len(tasks)
    total_pages = sum(t["pages"] for t in tasks)
    total_amount = sum(t["final"] for t in tasks)
    avg_amount = round(total_amount / count, 1)
    max_item = max(tasks, key=lambda x: x["final"])
    min_item = min(tasks, key=lambda x: x["final"])

    print(f"Count: {count}, TotalPages: {total_pages}, TotalAmount: {total_amount}, Avg: {avg_amount}")
    print(f"Max: {max_item['final']} ({max_item['id']}), Min: {min_item['final']} ({min_item['id']})")


def main():
    tasks = []

    while True:
        print("\n功能：")
        print("1. 新增影印任務")
        print("2. 列印所有影印（含金額）")
        print("3. 查詢（依客戶 ID）")
        print("4. 統計")
        print("5. 刪除最後一筆")
        print("0. 結束")

        choice = input("請輸入功能：")

        if choice == "1":
            cid = input("客戶 ID：")
            pages = int(input("頁數："))
            mode = input("色彩(color/bw)：").lower()
            size = input("紙張(A4/A3)：").upper()
            duplex = input("雙面(Y/N)：").upper()
            st = input("身分類型(s/p/t)：").lower()

            _, final = calc_amount(pages, mode, size, duplex, st)

            task = {
                "id": cid,
                "pages": pages,
                "mode": mode,
                "size": size,
                "duplex": duplex,
                "final": final
            }

            tasks.append(task)
            print(f"新增成功！本筆金額：{final}")

        elif choice == "2":
            print_all(tasks)

        elif choice == "3":
            key = input("輸入關鍵字：")
            search_id(tasks, key)

        elif choice == "4":
            stats(tasks)

        elif choice == "5":
            if tasks:
                removed = tasks.pop()
                print(f"已刪除：{removed['id']} 金額 {removed['final']}")
            else:
                print("無資料可刪除")

        elif choice == "0":
            print("Bye")
            break

        else:
            print("錯誤輸入")


main()
