import tkinter as tk
import os

# ==========================
#      Pomodoro 常數設定
# ==========================
WORK_TIME = 25 * 60
SHORT_BREAK_TIME = 5 * 60
LONG_BREAK_TIME = 15 * 60


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄鐘工作計時器")
        self.root.geometry("420x520")
        self.root.configure(bg="#FFEBE6")  # 番茄主題淡紅背景

        # ==========================
        #       功能狀態變數
        # ==========================
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.is_running = False
        self.after_id = None
        self.session_cycle = 0

        # ==========================
        #       UI 初始化
        # ==========================
        self.load_tomato_image()
        self.build_ui()

    # ==========================
    #      嘗試載入番茄圖片
    # ==========================
    def load_tomato_image(self):
        try:
            if os.path.exists("tomato.png"):
                self.tomato_img = tk.PhotoImage(file="tomato.png")
            else:
                self.tomato_img = None
        except:
            self.tomato_img = None

    # ==========================
    #      建立 UI 介面
    # ==========================
    def build_ui(self):
        # 模式顯示
        self.mode_label = tk.Label(self.root, text=f"模式：{self.current_mode}",
                                   font=("Arial", 20), bg="#FFEBE6", fg="#B30000")
        self.mode_label.pack(pady=15)

        # 主體番茄 + 計時文字（覆蓋）
        self.canvas = tk.Canvas(self.root, width=260, height=260,
                                bg="#FFEBE6", highlightthickness=0)
        self.canvas.pack()

        if self.tomato_img:
            self.canvas.create_image(130, 130, image=self.tomato_img)
        else:
            # fallback: emoji 番茄
            self.canvas.create_text(130, 130, text="🍅", font=("Arial", 120))

        self.timer_text = self.canvas.create_text(
            130, 130,
            text=self.format_time(self.remaining_seconds),
            fill="#8B0000",  # 深紅色
            font=("Arial", 36, "bold")
        )

        # 累積番茄數
        self.count_label = tk.Label(self.root, text=f"已完成番茄數：{self.tomato_count}",
                                    font=("Arial", 14), bg="#FFEBE6", fg="#8B0000")
        self.count_label.pack(pady=10)

        # ==========================
        #       美觀按鈕區塊
        # ==========================
        btn_frame = tk.Frame(self.root, bg="#FFEBE6")
        btn_frame.pack(pady=20)

        btn_style = {
            "width": 10,
            "height": 2,
            "font": ("Arial", 12, "bold"),
            "bg": "#FF8C66",
            "fg": "white",
            "activebackground": "#FF704D",
            "bd": 0
        }

        self.start_btn = tk.Button(btn_frame, text="開始", command=self.start_timer, **btn_style)
        self.start_btn.grid(row=0, column=0, padx=8)

        self.pause_btn = tk.Button(btn_frame, text="暫停", command=self.pause_timer, **btn_style)
        self.pause_btn.grid(row=0, column=1, padx=8)

        self.reset_btn = tk.Button(btn_frame, text="重置", command=self.reset_timer, **btn_style)
        self.reset_btn.grid(row=0, column=2, padx=8)

    # ==========================
    #       時間格式化
    # ==========================
    def format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    # ==========================
    #        開始計時
    # ==========================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.run_countdown()

    # ==========================
    #        暫停計時
    # ==========================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False

    # ==========================
    #        重置計時
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
    #         更新 UI
    # ==========================
    def update_ui(self):
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")
        self.canvas.itemconfig(self.timer_text, text=self.format_time(self.remaining_seconds))

    # ==========================
    #         倒數核心
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
    #       自動切換模式
    # ==========================
    def switch_mode(self):
        if self.current_mode == "工作":
            self.tomato_count += 1
            self.session_cycle += 1

            if self.session_cycle == 4:
                self.current_mode = "長休息"
                self.remaining_seconds = LONG_BREAK_TIME
                self.session_cycle = 0
            else:
                self.current_mode = "短休息"
                self.remaining_seconds = SHORT_BREAK_TIME

        elif self.current_mode == "短休息":
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME

        elif self.current_mode == "長休息":
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME

        self.update_ui()
        self.run_countdown()


# ==========================
#           主程式
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
