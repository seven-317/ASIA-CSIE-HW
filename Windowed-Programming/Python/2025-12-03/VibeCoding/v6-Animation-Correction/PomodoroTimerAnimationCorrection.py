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

        # ===== 背景顏色狀態（會做漸變動畫） =====
        self.current_bg = "#FFF5F0"  # 工作模式背景
        self.target_bg = self.current_bg
        self.root.configure(bg=self.current_bg)

        # ===== 計時狀態 =====
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.tomato_count = 0
        self.session_cycle = 0
        self.is_running = False
        self.after_id = None

        # ===== 動畫狀態 =====
        self.brightness_phase = 0  # 計時文字亮度循環用
        self.highlight_running = False  # 番茄高亮動畫是否在跑

        self.load_tomato_image()
        self.build_ui()

    # ===============================
    #         番茄圖片載入
    # ===============================
    def load_tomato_image(self):
        self.tomato_img_raw = None
        if os.path.exists("tomato.png"):
            try:
                self.tomato_img_raw = tk.PhotoImage(file="tomato.png")
            except:
                self.tomato_img_raw = None

    # ===============================
    #            UI 建構
    # ===============================
    def build_ui(self):
        # 上方番茄區
        self.top_frame = tk.Frame(self.root, bg=self.current_bg)
        self.top_frame.pack(pady=25)

        if self.tomato_img_raw:
            self.tomato_label = tk.Label(self.top_frame, image=self.tomato_img_raw, bg=self.current_bg)
        else:
            # emoji 版番茄
            self.tomato_label = tk.Label(
                self.top_frame,
                text="🍅",
                font=("Arial", 90),
                bg=self.current_bg
            )
        self.tomato_label.pack()

        # 模式標籤
        self.mode_label = tk.Label(
            self.root,
            text=f"模式：{self.current_mode}",
            font=("Arial Rounded MT Bold", 20),
            bg=self.current_bg,
            fg="#C0392B"
        )
        self.mode_label.pack(pady=(10, 5))

        # 計時文字
        self.timer_label = tk.Label(
            self.root,
            text=self.format_time(self.remaining_seconds),
            font=("Arial Rounded MT Bold", 48),
            fg="#8B0000",
            bg=self.current_bg
        )
        self.timer_label.pack(pady=10)

        # 番茄累積數
        self.count_label = tk.Label(
            self.root,
            text=f"已完成番茄數：{self.tomato_count}",
            font=("Arial Rounded MT Bold", 15),
            bg=self.current_bg,
            fg="#A93226"
        )
        self.count_label.pack(pady=10)

        # 按鈕區
        self.btn_frame = tk.Frame(self.root, bg=self.current_bg)
        self.btn_frame.pack(pady=30)

        self.start_btn = self.create_button("開始", self.start_timer)
        self.pause_btn = self.create_button("暫停", self.pause_timer)
        self.reset_btn = self.create_button("重置", self.reset_timer)

        self.start_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.reset_btn.grid(row=0, column=2, padx=10)

    # ===============================
    #   統一按鈕樣式 + 按壓動畫
    # ===============================
    def create_button(self, text, command):
        btn = tk.Button(
            self.btn_frame,
            text=text,
            width=10,
            height=2,
            font=("Arial Rounded MT Bold", 12),
            bg="#FF8D72",
            fg="white",
            bd=0,
            relief="ridge",
            activebackground="#FF7A5C",
            command=lambda: self.button_press_animation(btn, command)
        )
        return btn

    def button_press_animation(self, btn, command):
        """按下時字體輕微縮小，製造按壓感"""
        btn.config(font=("Arial Rounded MT Bold", 11))
        self.root.after(120, lambda: btn.config(font=("Arial Rounded MT Bold", 12)))
        command()

    # ===============================
    #   計時文字柔和亮度動畫（不抖動）
    # ===============================
    def animate_timer_brightness(self):
        if not self.is_running:
            # 停止時還原顏色
            self.timer_label.config(fg="#8B0000")
            return

        self.brightness_phase = (self.brightness_phase + 3) % 100
        brightness = 0.96 + 0.04 * (self.brightness_phase / 100)

        r, g, b = 139, 0, 0
        nr = int(r * brightness)
        ng = int(g * brightness)
        nb = int(b * brightness)
        color = f"#{nr:02x}{ng:02x}{nb:02x}"

        self.timer_label.config(fg=color)
        self.root.after(60, self.animate_timer_brightness)

    # ===============================
    #   背景漸變動畫（模式切換用）
    # ===============================
    def animate_background(self):
        if self.current_bg == self.target_bg:
            return

        def hex_to_rgb(h):
            return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

        c1 = hex_to_rgb(self.current_bg)
        c2 = hex_to_rgb(self.target_bg)

        # 小步前進
        new = tuple(int(c1[i] + (c2[i] - c1[i]) * 0.12) for i in range(3))

        # 若已經很接近，就直接設為目標色，防止無限逼近
        if all(abs(new[i] - c2[i]) < 2 for i in range(3)):
            self.current_bg = self.target_bg
        else:
            self.current_bg = f"#{new[0]:02x}{new[1]:02x}{new[2]:02x}"

        # 套用到所有相關元件
        self.root.configure(bg=self.current_bg)
        self.top_frame.configure(bg=self.current_bg)
        self.mode_label.configure(bg=self.current_bg)
        self.timer_label.configure(bg=self.current_bg)
        self.count_label.configure(bg=self.current_bg)
        self.btn_frame.configure(bg=self.current_bg)
        self.tomato_label.configure(bg=self.current_bg)

        if self.current_bg != self.target_bg:
            self.root.after(40, self.animate_background)

    # ===============================
    #   番茄高亮動畫（不隱藏，只閃一下背景）
    # ===============================
    def highlight_tomato(self, step=0):
        """
        番茄周圍背景輕微高亮 → 再回到原本背景色
        不碰番茄的文字 / 圖片，只改背景顏色
        """
        if step == 0:
            self.highlight_running = True

        if not self.highlight_running:
            return

        # 高亮色（略亮的暖色）
        highlight_bg = "#FFE2D6"

        def hex_to_rgb(h):
            return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

        base_rgb = hex_to_rgb(self.current_bg)
        hl_rgb = hex_to_rgb(highlight_bg)

        # step: 0~10 → 去亮 / 10~20 → 回原色
        if step <= 10:
            t = step / 10.0
        else:
            t = (20 - step) / 10.0

        new = tuple(int(base_rgb[i] * (1 - t) + hl_rgb[i] * t) for i in range(3))
        temp_color = f"#{new[0]:02x}{new[1]:02x}{new[2]:02x}"

        self.top_frame.configure(bg=temp_color)
        self.tomato_label.configure(bg=temp_color)

        if step < 20:
            self.root.after(30, lambda: self.highlight_tomato(step + 1))
        else:
            # 結束時保證回到 current_bg
            self.top_frame.configure(bg=self.current_bg)
            self.tomato_label.configure(bg=self.current_bg)
            self.highlight_running = False

    # ===============================
    #         格式化時間
    # ===============================
    def format_time(self, sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    # ===============================
    #           開始計時
    # ===============================
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            # 重新啟動亮度動畫與番茄高亮
            self.animate_timer_brightness()
            self.highlight_tomato()
            self.run_countdown()

    # ===============================
    #           暫停計時
    # ===============================
    def pause_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.is_running = False
        # 不動番茄顯示，只停止計時與亮度動畫

    # ===============================
    #           重置計時
    # ===============================
    def reset_timer(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)

        # 狀態復原
        self.is_running = False
        self.current_mode = "工作"
        self.remaining_seconds = WORK_TIME
        self.session_cycle = 0

        # 背景恢復到工作顏色
        self.target_bg = "#FFF5F0"
        self.animate_background()

        # 文字與番茄保證正常顯示
        self.timer_label.config(fg="#8B0000")
        if self.tomato_img_raw:
            self.tomato_label.config(image=self.tomato_img_raw)
        else:
            self.tomato_label.config(text="🍅")

        # 高亮動畫關閉並恢復番茄背景
        self.highlight_running = False
        self.top_frame.configure(bg=self.current_bg)
        self.tomato_label.configure(bg=self.current_bg)

        # 更新文字內容
        self.update_ui()

    # ===============================
    #             UI 更新
    # ===============================
    def update_ui(self):
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
        self.mode_label.config(text=f"模式：{self.current_mode}")
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")

    # ===============================
    #             倒數邏輯
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
    #             模式切換
    # ===============================
    def switch_mode(self):
        if self.current_mode == "工作":
            self.tomato_count += 1
            self.session_cycle += 1

            if self.session_cycle == 4:
                self.current_mode = "長休息"
                self.remaining_seconds = LONG_BREAK_TIME
                self.target_bg = "#F0F5FF"  # 淡藍色
            else:
                self.current_mode = "短休息"
                self.remaining_seconds = SHORT_BREAK_TIME
                self.target_bg = "#F0FFF5"  # 淡綠色
        else:
            # 任何休息結束 → 回工作
            self.current_mode = "工作"
            self.remaining_seconds = WORK_TIME
            self.target_bg = "#FFF5F0"

        # 背景漸變 + 番茄高亮一下，表示新一輪開始
        self.animate_background()
        self.highlight_tomato()

        self.update_ui()
        self.run_countdown()


# ===============================
#           主程式入口
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    PomodoroTimer(root)
    root.mainloop()
