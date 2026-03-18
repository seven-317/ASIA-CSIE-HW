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
        self.root.title("番茄鐘")
        self.root.geometry("420x600")
        self.root.configure(bg="#FFF5F0")  # 柔和暖色背景

        # ==========================
        #      邏輯狀態變數
        # ==========================
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.session_cycle = 0
        self.is_running = False
        self.after_id = None

        # ==========================
        #      UI 初始化
        # ==========================
        self.load_tomato_image()
        self.build_ui()

    # ==========================
    #  圖片載入（若失敗→使用 emoji）
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
    #      UI 建構
    # ==========================
    def build_ui(self):

        # 整體上方番茄圖示區
        top_frame = tk.Frame(self.root, bg="#FFF5F0")
        top_frame.pack(pady=20)

        if self.tomato_img:
            self.tomato_label = tk.Label(top_frame, image=self.tomato_img, bg="#FFF5F0")
        else:
            self.tomato_label = tk.Label(top_frame, text="🍅", font=("Arial", 90), bg="#FFF5F0")

        self.tomato_label.pack()

        # 模式
        self.mode_label = tk.Label(self.root, text=f"模式：{self.current_mode}",
                                   font=("Arial Rounded MT Bold", 20),
                                   bg="#FFF5F0", fg="#C0392B")
        self.mode_label.pack(pady=(10, 5))

        # 大倒數文字
        self.timer_label = tk.Label(self.root,
                                    text=self.format_time(self.remaining_seconds),
                                    font=("Arial Rounded MT Bold", 48),
                                    fg="#8B0000",
                                    bg="#FFF5F0")
        self.timer_label.pack(pady=10)

        # 已完成番茄數
        self.count_label = tk.Label(self.root, text=f"已完成番茄數：{self.tomato_count}",
                                    font=("Arial Rounded MT Bold", 15),
                                    bg="#FFF5F0", fg="#A93226")
        self.count_label.pack(pady=10)

        # ==========================
        #         按鈕區
        # ==========================
        btn_frame = tk.Frame(self.root, bg="#FFF5F0")
        btn_frame.pack(pady=30)

        btn_style = {
            "width": 10,
            "height": 2,
            "font": ("Arial Rounded MT Bold", 12),
            "bg": "#FF8D72",
            "fg": "white",
            "activebackground": "#FF7A5C",
            "bd": 0,
            "relief": "ridge"
        }

        self.start_btn = tk.Button(btn_frame, text="開始", command=self.start_timer, **btn_style)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.pause_btn = tk.Button(btn_frame, text="暫停", command=self.pause_timer, **btn_style)
        self.pause_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = tk.Button(btn_frame, text="重置", command=self.reset_timer, **btn_style)
        self.reset_btn.grid(row=0, column=2, padx=10)

    # ==========================
    #     秒數格式化
    # ==========================
    def format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    # ==========================
    #       計時開始
    # ==========================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.run_countdown()

    # ==========================
    #       計時暫停
    # ==========================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False

    # ==========================
    #       計時重置
    # ==========================
    def reset_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.session_cycle = 0
        self.is_running = False

        self.update_ui()

    # ==========================
    #       UI 更新
    # ==========================
    def update_ui(self):
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")
        self.timer_label.config(text=self.format_time(self.remaining_seconds))

    # ==========================
    #         倒數邏輯
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
#         主程式入口
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
