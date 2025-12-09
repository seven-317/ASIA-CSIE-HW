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
        self.root.configure(bg="#FFF5F0")

        # ==========================
        #       狀態變數
        # ==========================
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.session_cycle = 0
        self.is_running = False
        self.after_id = None

        # 動畫用變數
        self.fade_alpha = 0
        self.tomato_scale = 1.0
        self.jump_offset = 0

        # ==========================
        #       初始化 UI
        # ==========================
        self.load_tomato_image()
        self.build_ui()

        # 啟動淡入入場動畫
        self.fade_in_elements()

    # ==========================
    #       圖片讀取
    # ==========================
    def load_tomato_image(self):
        try:
            if os.path.exists("tomato.png"):
                self.tomato_img_raw = tk.PhotoImage(file="tomato.png")
            else:
                self.tomato_img_raw = None
        except:
            self.tomato_img_raw = None

    # ==========================
    #          UI 介面
    # ==========================
    def build_ui(self):
        # 上層番茄區
        self.top_frame = tk.Frame(self.root, bg="#FFF5F0")
        self.top_frame.pack(pady=25)

        if self.tomato_img_raw:
            self.tomato_img = self.tomato_img_raw
            self.tomato_label = tk.Label(self.top_frame, image=self.tomato_img, bg="#FFF5F0")
        else:
            self.tomato_label = tk.Label(self.top_frame, text="🍅",
                                         font=("Arial", 90), bg="#FFF5F0")

        self.tomato_label.pack()

        # 模式
        self.mode_label = tk.Label(self.root, text=f"模式：{self.current_mode}",
                                   font=("Arial Rounded MT Bold", 20),
                                   bg="#FFF5F0", fg="#C0392B")
        self.mode_label.pack(pady=(10, 5))

        # 倒數
        self.timer_label = tk.Label(self.root,
                                    text=self.format_time(self.remaining_seconds),
                                    font=("Arial Rounded MT Bold", 48),
                                    fg="#8B0000", bg="#FFF5F0")
        self.timer_label.pack(pady=10)

        # 番茄累積
        self.count_label = tk.Label(self.root,
                                    text=f"已完成番茄數：{self.tomato_count}",
                                    font=("Arial Rounded MT Bold", 15),
                                    bg="#FFF5F0", fg="#A93226")
        self.count_label.pack(pady=10)

        # 按鈕區
        self.btn_frame = tk.Frame(self.root, bg="#FFF5F0")
        self.btn_frame.pack(pady=30)

        self.start_btn = self.create_button("開始", self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.pause_btn = self.create_button("暫停", self.pause_timer)
        self.pause_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = self.create_button("重置", self.reset_timer)
        self.reset_btn.grid(row=0, column=2, padx=10)

    # ==========================
    #       按鈕建立 + 動畫
    # ==========================
    def create_button(self, text, command):
        return tk.Button(
            self.btn_frame, text=text, command=lambda: self.button_press_animation(text, command),
            width=10, height=2,
            font=("Arial Rounded MT Bold", 12),
            bg="#FF8D72", fg="white",
            bd=0, activebackground="#FF7A5C", relief="ridge"
        )

    def button_press_animation(self, text, command):
        """按鈕按壓動畫（簡單顏色變化）"""
        btn = None
        if text == "開始":
            btn = self.start_btn
        elif text == "暫停":
            btn = self.pause_btn
        else:
            btn = self.reset_btn

        btn.config(bg="#FF7A5C")
        self.root.after(120, lambda: btn.config(bg="#FF8D72"))
        command()

    # ==========================
    #       入場淡入動畫
    # ==========================
    def fade_in_elements(self):
        """UI 元素淡入動畫（不透明度逐步提升）"""
        if self.fade_alpha < 1:
            self.fade_alpha += 0.05
            alpha_hex = f"#{int(255 * self.fade_alpha):02x}"
            color = f"{alpha_hex}{alpha_hex}{alpha_hex}"

            try:
                self.tomato_label.config(fg=color)
                self.timer_label.config(fg="#8B0000")
            except:
                pass

            self.root.after(30, self.fade_in_elements)

    # ==========================
    #      番茄縮放動畫
    # ==========================
    def animate_tomato_bounce(self):
        """番茄在 start 時微縮放（彈一下）"""
        if not self.is_running:
            return

        self.tomato_scale = 1.0 + 0.03 * (1 if self.tomato_scale <= 1 else -1)
        scale = int(90 * self.tomato_scale)

        self.tomato_label.config(font=("Arial", scale))
        self.root.after(120, self.animate_tomato_bounce)

    # ==========================
    #     倒數文字跳動動畫
    # ==========================
    def animate_timer_text(self):
        """倒數文字微微跳動（提升注意力）"""
        if not self.is_running:
            return

        self.jump_offset = 1 if self.jump_offset == 0 else 0
        self.timer_label.pack_configure(pady=10 + self.jump_offset)

        self.root.after(300, self.animate_timer_text)

    # ==========================
    #    時間格式
    # ==========================
    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    # ==========================
    #      開始計時
    # ==========================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True

            # 啟動動畫
            self.animate_tomato_bounce()
            self.animate_timer_text()

            self.run_countdown()

    # ==========================
    #      暫停計時
    # ==========================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False

    # ==========================
    #      重置計時
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
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")

    # ==========================
    #      倒數邏輯
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
    #      模式切換
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
