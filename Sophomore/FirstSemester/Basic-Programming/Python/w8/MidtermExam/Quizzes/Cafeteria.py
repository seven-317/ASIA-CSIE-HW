def read_input():
    n = int(input().strip())
    items = []
    for _ in range(n):
        name, price, qty = input().strip().split()
        items.append({
            "name": name,
            "price": float(price),
            "qty": int(qty),
        })
    discount = int(input().strip())
    return items, discount

def compute(items, discount):
    factor = discount / 100.0
    for it in items:
        it["amount"] = it["price"] * it["qty"]
        it["after"] = it["amount"] * factor

    total_before = sum(it["amount"] for it in items)
    total_after  = sum(it["after"]  for it in items)
    avg_after    = round(total_after / len(items), 1)

    max_item = max(items, key=lambda x: x["after"])
    min_item = min(items, key=lambda x: x["after"])

    return total_before, total_after, avg_after, max_item, min_item

def print_summary(items, discount, total_before, total_after, avg_after, max_item, min_item):
    print("=== 結帳摘要 ===")
    print("購買清單：")
    for it in items:
        print(f"- {it['name']}: price={it['price']}, qty={it['qty']}, amount={it['amount']:.1f}, after={it['after']:.1f}")
    print()
    print(f"總金額（未打折）：{total_before:.1f}")
    print(f"折扣：{discount}%")
    print(f"折扣後總金額：{total_after:.1f}")
    print(f"平均（折扣後，四捨五入到1位）：{avg_after:.1f}")
    print(f"最貴：{max_item['name']} {max_item['after']:.1f}")
    print(f"最便宜：{min_item['name']} {min_item['after']:.1f}")

if __name__ == "__main__":
    items, discount = read_input()
    total_before, total_after, avg_after, max_item, min_item = compute(items, discount)
    print_summary(items, discount, total_before, total_after, avg_after, max_item, min_item)
