RATES = {"car": 40, "moto": 20}

def main():
    n = int(input().strip())

    records = []
    car_cnt = 0
    moto_cnt = 0
    total_fee = 0

    for _ in range(n):
        parts = input().strip().split()
        if len(parts) != 2:
            continue

        kind = parts[0].lower()
        try:
            hours = max(0, int(parts[1]))
        except:
            hours = 0

        if kind in RATES:
            fee = RATES[kind] * hours
            if kind == "car":
                car_cnt += 1
            else:
                moto_cnt += 1
        else:
            fee = 0

        total_fee += fee
        records.append((kind, hours, fee))

    for r in records:
        print(f"Fee: {r[2]}")

    fees = [r[2] for r in records]
    max_fee = max(fees) if fees else 0
    min_fee = min(fees) if fees else 0

    print("== Summary ==")
    print(f"TotalCars: {car_cnt}")
    print(f"TotalMoto: {moto_cnt}")
    print(f"TotalFee: {total_fee}")
    print(f"MaxFee: {max_fee}")
    print(f"MinFee: {min_fee}")

if __name__ == "__main__":
    main()
