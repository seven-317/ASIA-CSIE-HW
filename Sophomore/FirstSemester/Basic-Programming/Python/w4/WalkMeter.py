def main():
    moods = ["happy", "sad", "tired"]
    order = []
    table = {}

    print("請輸入健走日誌 (格式: YYYY-MM-DD,步數,心情)，輸入 END 結束:")

    while True:
        line = input().strip()
        if line == "" or line.upper() == "END":
            break

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            print("格式錯誤！正確：YYYY-MM-DD,步數,心情")
            continue

        date_raw, steps_str, mood = parts

        # 自動補零
        date_parts = date_raw.split("-")
        if len(date_parts) == 3 and all(p.isdigit() for p in date_parts):
            y, m, d = date_parts
            date = f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
        else:
            print("日期格式錯誤！請輸入 YYYY-MM-DD")
            continue

        if not steps_str.isdigit():
            print("步數必須為正整數")
            continue
        steps = int(steps_str)

        if mood not in moods:
            print("心情必須是 happy / sad / tired")
            continue

        if date not in table:
            table[date] = (steps, mood)
            order.append(date)
        else:
            old_steps, old_mood = table[date]
            if steps > old_steps:
                table[date] = (steps, mood)
                print(f"⚠ 已更新 {date}：步數 {old_steps} -> {steps}")
            else:
                print(f"ℹ 已忽略重複日期 {date}（已有更高或相同步數 {old_steps} ）")

    if not order:
        print("沒有資料")
        return

    records = [(d, table[d][0], table[d][1]) for d in order]

    total_days = len(records)
    total_steps = sum(r[1] for r in records)
    avg_steps = round(total_steps / total_days)

    max_record = records[0]
    min_record = records[0]
    for r in records[1:]:
        if r[1] > max_record[1]:
            max_record = r
        if r[1] < min_record[1]:
            min_record = r

    target_days = sum(1 for r in records if r[1] >= 8000)

    mood_stats = {}
    for m in moods:
        steps_list = [r[1] for r in records if r[2] == m]
        if steps_list:
            mood_stats[m] = (len(steps_list), round(sum(steps_list) / len(steps_list)))
        else:
            mood_stats[m] = (0, 0)

    print("\n===== 統計結果 =====")
    print(f"總天數: {total_days}")
    print(f"總步數: {total_steps}")
    print(f"平均步數: {avg_steps}")
    print(f"最高步數: {max_record[1]} (日期: {max_record[0]})")
    print(f"最低步數: {min_record[1]} (日期: {min_record[0]})")
    print(f"達標日數: {target_days}")

    print("\n心情統計:")
    for m, (days, avg) in mood_stats.items():
        print(f"{m}: {days} 天, 平均 {avg} 步")

if __name__ == "__main__":
    main()
