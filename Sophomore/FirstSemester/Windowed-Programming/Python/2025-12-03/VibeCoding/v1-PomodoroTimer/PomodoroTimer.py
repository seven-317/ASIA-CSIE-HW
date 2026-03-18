import tkinter as tk

# ==========================
#      Pomodoro 常數設定
# ==========================
WORK_TIME = 25 * 60        # 25 分鐘
SHORT_BREAK_TIME = 5 * 60  # 5 分鐘
LONG_BREAK_TIME = 15 * 60  # 15 分鐘


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄鐘工作計時器")
        self.root.geometry("400x300")

        # ==========================
        #        狀態變數
        # ==========================
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.is_running = False
        self.after_id = None
        self.session_cycle = 0  # 記錄第幾次工作（1~4）

        # ==========================
        #        UI 元件建立
        # ==========================
        self.mode_label = tk.Label(self.root, text="模式：工作", font=("Arial", 18))
        self.mode_label.pack(pady=10)

        self.timer_label = tk.Label(self.root, text=self.format_time(self.remaining_seconds),
                                    font=("Arial", 40), fg="red")
        self.timer_label.pack(pady=10)

        self.count_label = tk.Label(self.root, text="已完成番茄數：0", font=("Arial", 14))
        self.count_label.pack(pady=5)

        # ==========================
        #        按鈕區塊
        # ==========================
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="開始", width=10, command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(btn_frame, text="暫停", width=10, command=self.pause_timer)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="重置", width=10, command=self.reset_timer)
        self.reset_btn.grid(row=0, column=2, padx=5)

    # ==========================
    #       轉換秒數格式
    # ==========================
    def format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    # ==========================
    #       計時器開始
    # ==========================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.run_countdown()

    # ==========================
    #       計時器暫停
    # ==========================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False

    # ==========================
    #       計時器重置
    # ==========================
    def reset_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.is_running = False
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.session_cycle = 0
        self.update_ui()
    
    # ==========================
    #       UI 更新
    # ==========================
    def update_ui(self):
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")

    # ==========================
    #       倒數邏輯
    # ==========================
    def run_countdown(self):
        if self.remaining_seconds > 0 and self.is_running:
            self.remaining_seconds -= 1
            self.update_ui()
            self.after_id = self.root.after(1000, self.run_countdown)
        else:
            if self.is_running:
                self.switch_mode()

    # ==========================
    #      自動切換模式
    # ==========================
    def switch_mode(self):
        # 工作模式結束 → 短休 or 長休
        if self.current_mode == "工作":
            self.tomato_count += 1
            self.session_cycle += 1

            if self.session_cycle == 4:
                self.current_mode = "長休息"
                self.remaining_seconds = LONG_BREAK_TIME
                self.session_cycle = 0  # 重置
            else:
                self.current_mode = "短休息"
                self.remaining_seconds = SHORT_BREAK_TIME

        # 短休息 → 工作
        elif self.current_mode == "短休息":
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME

        # 長休息 → 工作
        elif self.current_mode == "長休息":
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME

        self.update_ui()

        # 自動開始下一輪
        self.run_countdown()


# ==========================
#           主程式
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
