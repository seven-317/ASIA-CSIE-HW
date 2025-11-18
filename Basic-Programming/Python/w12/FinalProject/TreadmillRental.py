import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, timedelta

CSV_FILE = "treadmill_rentals.csv"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class RentalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("宿舍跑步機租借系統")
        self.root.geometry("800x400")

        self.ensure_csv_exists()
        self.create_widgets()
        self.update_status()
        self.schedule_auto_refresh()

    # ---------------- CSV 相關 ----------------
    def ensure_csv_exists(self):
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["machine_id", "student_name", "dormitory", "hours", "start_time", "end_time"]
                )

    def append_rental_to_csv(self, machine_id, student_name, dormitory, hours, start_time, end_time):
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [machine_id, student_name, dormitory, str(hours), start_time, end_time]
            )

    def load_all_rentals(self):
        rentals = []
        if not os.path.exists(CSV_FILE):
            return rentals

        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rentals.append(row)
        return rentals

    # ---------------- 租借邏輯 ----------------
    def submit_rental(self):
        student_name = self.entry_name.get().strip()
        dormitory = self.combo_dorm.get().strip()
        hours_text = self.entry_hours.get().strip()
        machine_id = self.combo_machine.get().strip()

        if not student_name:
            messagebox.showwarning("錯誤", "請輸入學生姓名")
            return

        if dormitory not in ["感恩學苑", "惜福學苑", "築夢學苑", "登峰學苑"]:
            messagebox.showwarning("錯誤", "請選擇宿舍")
            return

        try:
            hours = int(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("錯誤", "租借時數請輸入大於 0 的整數")
            return

        if machine_id not in ["1", "2"]:
            messagebox.showwarning("錯誤", "請選擇跑步機 (1 或 2)")
            return

        now = datetime.now().replace(second=0, microsecond=0)
        start_time_str = now.strftime(DATETIME_FORMAT)
        end_time = now + timedelta(hours=hours)
        end_time_str = end_time.strftime(DATETIME_FORMAT)

        self.append_rental_to_csv(
            machine_id=machine_id,
            student_name=student_name,
            dormitory=dormitory,
            hours=hours,
            start_time=start_time_str,
            end_time=end_time_str,
        )

        messagebox.showinfo(
            "成功",
            f"{machine_id} 號跑步機已成功租借給 {student_name}\n"
            f"開始時間：{start_time_str}\n"
            f"結束時間：{end_time_str}",
        )

        self.clear_form()
        self.update_status()

    def get_current_rental_for_machine(self, machine_id):
        rentals = self.load_all_rentals()
        now = datetime.now()
        active_rentals = []

        for r in rentals:
            if r["machine_id"] != str(machine_id):
                continue

            try:
                start = datetime.strptime(r["start_time"], DATETIME_FORMAT)
                end = datetime.strptime(r["end_time"], DATETIME_FORMAT)
            except Exception:
                continue

            # 只找「尚未結束」的租借
            if end > now:
                active_rentals.append((start, end, r))

        if not active_rentals:
            return None

        # 取得開始時間最新、但尚未結束的那一筆
        active_rentals.sort(key=lambda x: x[0], reverse=True)
        return active_rentals[0][2]

    def clear_all_records(self):
        ans = messagebox.askyesno("確認", "確定要清空所有租借紀錄嗎？此動作無法復原。")
        if not ans:
            return

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["machine_id", "student_name", "dormitory", "hours", "start_time", "end_time"]
            )

        messagebox.showinfo("完成", "已清空所有紀錄。")
        self.update_status()

    # ---------------- UI 建立 ----------------
    def create_widgets(self):
        # 整體主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 左側：租借表單
        self.create_left_form(main_frame)

        # 右側：跑步機狀態
        self.create_right_status(main_frame)

    def create_left_form(self, parent):
        form_frame = tk.LabelFrame(parent, text="租借表單", padx=10, pady=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 學生姓名
        tk.Label(form_frame, text="學生姓名：").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(form_frame, width=20)
        self.entry_name.grid(row=0, column=1, sticky="w", pady=5)

        # 隸屬宿舍
        tk.Label(form_frame, text="隸屬宿舍：").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_dorm = ttk.Combobox(
            form_frame,
            values=["感恩學苑", "惜福學苑", "築夢學苑", "登峰學苑"],
            state="readonly",
            width=18,
        )
        self.combo_dorm.grid(row=1, column=1, sticky="w", pady=5)
        self.combo_dorm.set("感恩學苑")

        # 租借時數
        tk.Label(form_frame, text="租借時數（小時）：").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_hours = tk.Entry(form_frame, width=20)
        self.entry_hours.grid(row=2, column=1, sticky="w", pady=5)

        # 跑步機編號
        tk.Label(form_frame, text="選擇跑步機：").grid(row=3, column=0, sticky="w", pady=5)
        self.combo_machine = ttk.Combobox(
            form_frame,
            values=["1", "2"],
            state="readonly",
            width=18,
        )
        self.combo_machine.grid(row=3, column=1, sticky="w", pady=5)
        self.combo_machine.set("1")

        # 按鈕列
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        btn_submit = tk.Button(btn_frame, text="確認租借", command=self.submit_rental, width=12)
        btn_submit.grid(row=0, column=0, padx=5)

        btn_refresh = tk.Button(btn_frame, text="重新整理", command=self.update_status, width=12)
        btn_refresh.grid(row=0, column=1, padx=5)

        btn_clear = tk.Button(btn_frame, text="清空紀錄", command=self.clear_all_records, width=12)
        btn_clear.grid(row=0, column=2, padx=5)

    def create_right_status(self, parent):
        status_frame = tk.LabelFrame(parent, text="跑步機使用狀態", padx=10, pady=10)
        status_frame.grid(row=0, column=1, sticky="nsew")

        status_frame.columnconfigure(0, weight=1)

        # 1 號跑步機卡片
        self.machine1_frame = tk.LabelFrame(status_frame, text="1 號跑步機")
        self.machine1_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.label_machine1 = tk.Label(self.machine1_frame, text="載入中...", justify="left", anchor="w")
        self.label_machine1.pack(fill=tk.BOTH, padx=5, pady=5)

        # 2 號跑步機卡片
        self.machine2_frame = tk.LabelFrame(status_frame, text="2 號跑步機")
        self.machine2_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.label_machine2 = tk.Label(self.machine2_frame, text="載入中...", justify="left", anchor="w")
        self.label_machine2.pack(fill=tk.BOTH, padx=5, pady=5)

    # ---------------- UI 更新 ----------------
    def update_status(self):
        self.update_machine_status(1, self.label_machine1)
        self.update_machine_status(2, self.label_machine2)

    def update_machine_status(self, machine_id, label_widget):
        rental = self.get_current_rental_for_machine(machine_id)
        now = datetime.now()

        if rental is None:
            label_widget.config(text="目前狀態：可租借")
            return

        try:
            end = datetime.strptime(rental["end_time"], DATETIME_FORMAT)
        except Exception:
            label_widget.config(text="資料錯誤，無法解析時間。")
            return

        if end <= now:
            # 租借已到期
            label_widget.config(text="目前狀態：可租借")
            return

        student_name = rental["student_name"]
        dormitory = rental["dormitory"]
        hours = rental["hours"]
        start_time_str = rental["start_time"]
        end_time_str = rental["end_time"]

        remaining = end - now
        total_minutes = int(remaining.total_seconds() // 60)
        hours_left = total_minutes // 60
        minutes_left = total_minutes % 60

        info_text = (
            "目前狀態：使用中\n"
            f"學生：{student_name}\n"
            f"宿舍：{dormitory}\n"
            f"租借時數：{hours} 小時\n"
            f"開始時間：{start_time_str}\n"
            f"結束時間：{end_time_str}\n"
            f"剩餘時間：約 {hours_left} 小時 {minutes_left} 分鐘"
        )

        label_widget.config(text=info_text)

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_hours.delete(0, tk.END)
        self.combo_dorm.set("感恩學苑")
        self.combo_machine.set("1")

    def schedule_auto_refresh(self):
        # 每 60 秒自動重新整理一次狀態（倒數會更新）
        self.update_status()
        self.root.after(60000, self.schedule_auto_refresh)


if __name__ == "__main__":
    root = tk.Tk()
    app = RentalSystem(root)
    root.mainloop()

