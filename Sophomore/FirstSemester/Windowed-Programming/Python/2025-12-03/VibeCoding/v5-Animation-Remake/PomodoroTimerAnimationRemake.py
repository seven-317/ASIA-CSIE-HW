import tkinter as tk
import os

WORK_TIME = 25 * 60
SHORT_BREAK_TIME = 5 * 60
LONG_BREAK_TIME = 15 * 60


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄鐘")
        self.root.geometry("420x600")

        # 動畫狀態
        self.brightness_phase = 0  # 計時文字亮度循環
        self.current_bg = "#FFF5F0"  # 初始工作背景色
        self.target_bg = self.current_bg

        self.root.configure(bg=self.current_bg)

        # 計時狀態
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.session_cycle = 0
        self.is_running = False
        self.after_id = None

        self.load_tomato_image()
        self.build_ui()

    # ===============================
    #         番茄圖片載入邏輯
    # ===============================
    def load_tomato_image(self):
        if os.path.exists("tomato.png"):
            try:
                self.tomato_img_raw = tk.PhotoImage(file="tomato.png")
            except:
                self.tomato_img_raw = None
        else:
            self.tomato_img_raw = None

    # ===============================
    #         UI 建構
    # ===============================
    def build_ui(self):
        self.top_frame = tk.Frame(self.root, bg=self.current_bg)
        self.top_frame.pack(pady=25)

        if self.tomato_img_raw:
            self.tomato_label = tk.Label(self.top_frame, image=self.tomato_img_raw, bg=self.current_bg)
        else:
            self.tomato_label = tk.Label(self.top_frame, text="🍅", font=("Arial", 90), bg=self.current_bg)

        self.tomato_label.pack()

        self.mode_label = tk.Label(self.root, text=f"模式：{self.current_mode}",
                                   font=("Arial Rounded MT Bold", 20),
                                   bg=self.current_bg, fg="#C0392B")
        self.mode_label.pack(pady=(10, 5))

        self.timer_label = tk.Label(self.root,
                                    text=self.format_time(self.remaining_seconds),
                                    font=("Arial Rounded MT Bold", 48),
                                    fg="#8B0000", bg=self.current_bg)
        self.timer_label.pack(pady=10)

        self.count_label = tk.Label(self.root,
                                    text=f"已完成番茄數：{self.tomato_count}",
                                    font=("Arial Rounded MT Bold", 15),
                                    bg=self.current_bg, fg="#A93226")
        self.count_label.pack(pady=10)

        # 按鈕
        self.btn_frame = tk.Frame(self.root, bg=self.current_bg)
        self.btn_frame.pack(pady=30)

        self.start_btn = self.create_button("開始", self.start_timer)
        self.pause_btn = self.create_button("暫停", self.pause_timer)
        self.reset_btn = self.create_button("重置", self.reset_timer)

        self.start_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.reset_btn.grid(row=0, column=2, padx=10)

    # ===============================
    #      統一的按鈕樣式 + 動畫
    # ===============================
    def create_button(self, text, command):
        btn = tk.Button(
            self.btn_frame, text=text,
            width=10, height=2,
            font=("Arial Rounded MT Bold", 12),
            bg="#FF8D72", fg="white",
            bd=0, relief="ridge",
            activebackground="#FF7A5C",
            command=lambda: self.button_press_animation(btn, command)
        )
        return btn

    def button_press_animation(self, btn, command):
        btn.config(font=("Arial Rounded MT Bold", 11))
        self.root.after(120, lambda: btn.config(font=("Arial Rounded MT Bold", 12)))
        command()

    # ===============================
    #      計時文字柔和亮度動畫
    # ===============================
    def animate_timer_brightness(self):
        if not self.is_running:
            return

        # brightness_phase 0~100
        self.brightness_phase = (self.brightness_phase + 3) % 100
        brightness = 0.96 + 0.04 * (self.brightness_phase / 100)

        # 產生亮度效果（不跳動，不重排控件）
        r, g, b = 139, 0, 0
        nr = int(r * brightness)
        ng = int(g * brightness)
        nb = int(b * brightness)
        color = f"#{nr:02x}{ng:02x}{nb:02x}"

        self.timer_label.config(fg=color)
        self.root.after(60, self.animate_timer_brightness)

    # ===============================
    #     模式切換背景漸變動畫
    # ===============================
    def animate_background(self):
        if self.current_bg == self.target_bg:
            return

        def hex_to_rgb(h):
            return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

        c1 = hex_to_rgb(self.current_bg)
        c2 = hex_to_rgb(self.target_bg)

        new = tuple(int(c1[i] + (c2[i] - c1[i]) * 0.08) for i in range(3))

        self.current_bg = f"#{new[0]:02x}{new[1]:02x}{new[2]:02x}"

        self.root.configure(bg=self.current_bg)
        self.top_frame.configure(bg=self.current_bg)
        self.mode_label.configure(bg=self.current_bg)
        self.timer_label.configure(bg=self.current_bg)
        self.count_label.configure(bg=self.current_bg)
        self.btn_frame.configure(bg=self.current_bg)
        self.tomato_label.configure(bg=self.current_bg)

        self.root.after(40, self.animate_background)

    # ===============================
    #     番茄淡入效果
    # ===============================
    def tomato_fade_in(self, alpha=0):
        # alpha: 0~1
        if alpha > 1:
            return

        color = int(255 * alpha)
        hex_color = f"#{color:02x}{color:02x}{color:02x}"

        self.tomato_label.config(fg=hex_color)
        self.root.after(30, lambda: self.tomato_fade_in(alpha + 0.08))

    # ===============================
    #       格式化時間
    # ===============================
    def format_time(self, sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    # ===============================
    #       計時開始
    # ===============================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.animate_timer_brightness()
            self.tomato_fade_in()
            self.run_countdown()

    # ===============================
    #       計時暫停
    # ===============================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False

    # ===============================
    #       重置計時
    # ===============================
    def reset_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.is_running = False
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.session_cycle = 0

        self.target_bg = "#FFF5F0"
        self.animate_background()

        self.update_ui()

    # ===============================
    #       UI 更新
    # ===============================
    def update_ui(self):
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")

    # ===============================
    #       倒數邏輯
    # ===============================
    def run_countdown(self):
        if self.remaining_seconds > 0 and self.is_running:
            self.remaining_seconds -= 1
            self.update_ui()
            self.after_id = self.root.after(1000, self.run_countdown)
        else:
            if self.is_running:
                self.switch_mode()

    # ===============================
    #       模式切換
    # ===============================
    def switch_mode(self):
        if self.current_mode == "工作":
            self.tomato_count += 1
            self.session_cycle += 1

            if self.session_cycle == 4:
                self.current_mode = "長休息"
                self.remaining_seconds = LONG_BREAK_TIME
                self.target_bg = "#F0F5FF"
            else:
                self.current_mode = "短休息"
                self.remaining_seconds = SHORT_BREAK_TIME
                self.target_bg = "#F0FFF5"

        else:
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME
            self.target_bg = "#FFF5F0"

        self.animate_background()
        self.tomato_fade_in()
        self.update_ui()
        self.run_countdown()


# ===============================
#          主程式入口
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    PomodoroTimer(root)
    root.mainloop()
