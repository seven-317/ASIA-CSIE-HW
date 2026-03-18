n = int(input())
temps = list(map(float, input().split()))
T = float(input())

total = n
avg = round(sum(temps) / n, 1)
max_temp = max(temps)
min_temp = min(temps)

print(f"Total: {total}")
print(f"Avg: {avg}")
print(f"Max: {max_temp}")
print(f"Min: {min_temp}")

ranges = {
    "<18": 0,
    "18-24.999": 0,
    "25-29.999": 0,
    ">=30": 0
}

for t in temps:
    if t < 18:
        ranges["<18"] += 1
    elif 18 <= t < 25:
        ranges["18-24.999"] += 1
    elif 25 <= t < 30:
        ranges["25-29.999"] += 1
    else:
        ranges[">=30"] += 1

print("== Alerts ==")
print(ranges)

hot_list = [t for t in temps if t > T]
print("== Threshold ==")
print(f"Threshold: {T}")
print(f"HotCount: {len(hot_list)}")
print(f"HotList: {hot_list}")
