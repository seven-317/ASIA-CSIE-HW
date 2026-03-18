name = input()
price = float(input())
qty = int(input())
tax_rate = int(input())

sub_total = price * qty
tax = sub_total * tax_rate / 100
total = sub_total + tax

sub_total = round(sub_total, 1)
tax = round(tax, 1)
total = round(total, 1)

print(f'品名: {name} 小計: {sub_total} 稅額: {tax} 應付金額: {total}')
