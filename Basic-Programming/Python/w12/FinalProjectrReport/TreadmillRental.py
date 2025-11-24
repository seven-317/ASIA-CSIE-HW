import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, timedelta

CSV_FILE = "treadmill_rentals.csv"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

DORMS = ["感恩", "惜福", "築夢", "登峰學苑"]

MACHINE_LAYOUT = {
    1: ("感恩", 1),
    2: ("感恩", 2),
    3: ("惜福", 1),
    4: ("惜福", 2),
    5: ("築夢", 1),
    6: ("築夢", 2),
    7: ("登峰學苑", 1),
    8: ("登峰學苑", 2),
}


class RentalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("宿舍跑步機租借系統")
        self.root.state('zoomed')

        self.machine_labels = {}

        self.ensure_csv_exists()
        self.create_widgets()
        self.update_status()
        self.schedule_auto_refresh()

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

    def submit_rental(self):
        student_name = self.entry_name.get().strip()
        student_dorm = self.combo_dorm.get().strip()
        hours_text = self.entry_hours.get().strip()
        machine_id_text = self.combo_machine.get().strip()

        if not student_name:
            messagebox.showwarning("錯誤", "請輸入學生姓名")
            return

        if student_dorm not in DORMS:
            messagebox.showwarning("錯誤", "請選擇宿舍")
            return

        try:
            hours = int(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("錯誤", "租借時數請輸入大於 0 的整數")
            return

        if machine_id_text not in [str(i) for i in range(1, 9)]:
            messagebox.showwarning("錯誤", "請選擇正確的跑步機編號（1~8）")
            return

        machine_id = int(machine_id_text)

        now = datetime.now().replace(second=0, microsecond=0)
        start_time_str = now.strftime(DATETIME_FORMAT)
        end_time = now + timedelta(hours=hours)
        end_time_str = end_time.strftime(DATETIME_FORMAT)

        self.append_rental_to_csv(
            machine_id=machine_id,
            student_name=student_name,
            dormitory=student_dorm,
            hours=hours,
            start_time=start_time_str,
            end_time=end_time_str,
        )

        dorm_name, local_no = MACHINE_LAYOUT[machine_id]
        messagebox.showinfo(
            "成功",
            f"已成功租借：{dorm_name}棟 {local_no} 號跑步機（ID {machine_id}）給 {student_name}\n"
            f"開始時間：{start_time_str}\n"
            f"結束時間：{end_time_str}",
        )

        self.clear_form()
        self.update_status()

    def get_current_rental_for_machine(self, machine_id: int):
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

            if end > now:
                active_rentals.append((start, end, r))

        if not active_rentals:
            return None

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

    # ---------------- UI ----------------
    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)

        self.create_left_form(main_frame)
        self.create_right_status(main_frame)

    def create_left_form(self, parent):
        form_frame = tk.LabelFrame(parent, text="租借表單", padx=10, pady=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(form_frame, text="學生姓名：").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(form_frame, width=20)
        self.entry_name.grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(form_frame, text="學生宿舍：").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_dorm = ttk.Combobox(
            form_frame,
            values=DORMS,
            state="readonly",
            width=18,
        )
        self.combo_dorm.grid(row=1, column=1, sticky="w", pady=5)
        self.combo_dorm.set(DORMS[0])

        tk.Label(form_frame, text="租借時數（小時）：").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_hours = tk.Entry(form_frame, width=20)
        self.entry_hours.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(form_frame, text="選擇跑步機（ID）：").grid(row=3, column=0, sticky="w", pady=5)
        self.combo_machine = ttk.Combobox(
            form_frame,
            values=[str(i) for i in range(1, 9)],
            state="readonly",
            width=18,
        )
        self.combo_machine.grid(row=3, column=1, sticky="w", pady=5)
        self.combo_machine.set("1")

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        btn_submit = tk.Button(btn_frame, text="確認租借", command=self.submit_rental, width=12)
        btn_submit.grid(row=0, column=0, padx=5)

        btn_refresh = tk.Button(btn_frame, text="重新整理", command=self.update_status, width=12)
        btn_refresh.grid(row=0, column=1, padx=5)

        btn_clear = tk.Button(btn_frame, text="清空紀錄", command=self.clear_all_records, width=12)
        btn_clear.grid(row=0, column=2, padx=5)

    def create_right_status(self, parent):
        status_frame = tk.LabelFrame(parent, text="各宿舍跑步機使用狀態", padx=10, pady=10)
        status_frame.grid(row=0, column=1, sticky="nsew")

        for r in range(2):
            status_frame.rowconfigure(r, weight=1)
        for c in range(2):
            status_frame.columnconfigure(c, weight=1)

        self.dorm_frames = {}

        for idx, dorm in enumerate(DORMS):
            row = idx // 2
            col = idx % 2
            dorm_frame = tk.LabelFrame(status_frame, text=f"{dorm}棟", padx=5, pady=5)
            dorm_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            self.dorm_frames[dorm] = dorm_frame

        for machine_id in range(1, 9):
            dorm_name, local_no = MACHINE_LAYOUT[machine_id]
            dorm_frame = self.dorm_frames[dorm_name]

            machine_frame = tk.LabelFrame(
                dorm_frame,
                text=f"{local_no} 號跑步機（ID {machine_id}）",
                padx=5,
                pady=5,
            )
            machine_frame.pack(fill="x", pady=3)

            label = tk.Label(
                machine_frame,
                text="目前狀態：可租借",
                justify="left",
                anchor="w",
            )
            label.pack(fill="x", padx=3, pady=3)

            self.machine_labels[machine_id] = label

    # ---------------- UI Refresh ----------------
    def update_status(self):
        for machine_id, label in self.machine_labels.items():
            self.update_machine_status(machine_id, label)

    def update_machine_status(self, machine_id, label_widget):
        rental = self.get_current_rental_for_machine(machine_id)
        now = datetime.now()

        dorm_name, local_no = MACHINE_LAYOUT[machine_id]

        if rental is None:
            label_widget.config(
                text=f"機台位置：{dorm_name}棟 {local_no} 號\n目前狀態：可租借"
            )
            return

        try:
            end = datetime.strptime(rental["end_time"], DATETIME_FORMAT)
        except Exception:
            label_widget.config(text="資料錯誤，無法解析時間。")
            return

        if end <= now:
            label_widget.config(
                text=f"機台位置：{dorm_name}棟 {local_no} 號\n目前狀態：可租借"
            )
            return

        student_name = rental["student_name"]
        student_dorm = rental["dormitory"]
        hours = rental["hours"]
        start_time_str = rental["start_time"]
        end_time_str = rental["end_time"]

        remaining = end - now
        total_minutes = int(remaining.total_seconds() // 60)
        hours_left = total_minutes // 60
        minutes_left = total_minutes % 60

        info_text = (
            f"機台位置：{dorm_name}棟 {local_no} 號（ID {machine_id}）\n"
            f"目前狀態：使用中\n"
            f"學生姓名：{student_name}\n"
            f"學生宿舍：{student_dorm}\n"
            f"租借時數：{hours} 小時\n"
            f"開始時間：{start_time_str}\n"
            f"結束時間：{end_time_str}\n"
            f"剩餘時間：約 {hours_left} 小時 {minutes_left} 分鐘"
        )

        label_widget.config(text=info_text)

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_hours.delete(0, tk.END)
        self.combo_dorm.set(DORMS[0])
        self.combo_machine.set("1")

    def schedule_auto_refresh(self):
        self.update_status()
        # 每 60 秒自動更新一次倒數
        self.root.after(60000, self.schedule_auto_refresh)


if __name__ == "__main__":
    root = tk.Tk()
    app = RentalSystem(root)
    root.mainloop()
