import tkinter as tk
import os
import math

WORK_TIME = 25 * 60
SHORT_BREAK_TIME = 5 * 60
LONG_BREAK_TIME = 15 * 60


class PomodoroTimerPage(tk.Frame):
    """
    通用番茄鐘頁面：可用於工作、讀書、運動等不同模式。
    使用 Canvas 顯示番茄與環形進度條，並有柔和呼吸動畫。
    """
    def __init__(self, parent, app, profile_key, title_text):
        super().__init__(parent, bg=app.current_bg)
        self.app = app
        self.profile_key = profile_key
        self.title_text = title_text

        # 從 App 的 profiles 讀取此頁面的預設時間設定
        profile = self.app.profiles[self.profile_key]
        self.work_duration = profile["durations"]["work"]
        self.short_break_duration = profile["durations"]["short"]
        self.long_break_duration = profile["durations"]["long"]

        # ===== 計時狀態 =====
        self.current_phase = "工作"  # 工作 / 短休息 / 長休息
        self.remaining_seconds = self.work_duration
        self.current_session_total = self.work_duration
        self.tomato_count = 0
        self.session_cycle = 0  # 第幾個工作階段（1~4）
        self.is_running = False
        self.after_id = None

        # ===== 動畫狀態（Canvas 番茄呼吸 + 環形進度）=====
        self.breath_phase = 0.0
        self.breath_running = False

        self.canvas_size = 260
        self.center = self.canvas_size // 2
        self.base_radius = 60  # 番茄半徑基準

        self.build_ui()

    # -------- UI 建構 --------
    def build_ui(self):
        # 頁面標題（例如：工作模式、讀書模式）
        title_label = tk.Label(
            self,
            text=self.title_text,
            font=("Arial Rounded MT Bold", 20),
            bg=self.app.current_bg,
            fg=self.app.colors["text_primary"],
        )
        title_label.pack(pady=(15, 5))

        # 階段顯示：工作 / 短休息 / 長休息
        self.phase_label = tk.Label(
            self,
            text=f"階段：{self.current_phase}",
            font=("Arial Rounded MT Bold", 14),
            bg=self.app.current_bg,
            fg=self.app.colors["text_secondary"],
        )
        self.phase_label.pack(pady=(0, 10))

        # Canvas：番茄 + 環形進度條
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.app.current_bg,
            highlightthickness=0,
        )
        self.canvas.pack(pady=10)

        # 環形底圈
        ring_r = 90
        self.ring_bg_id = self.canvas.create_oval(
            self.center - ring_r,
            self.center - ring_r,
            self.center + ring_r,
            self.center + ring_r,
            outline=self.app.colors["accent"],
            width=6,
        )

        # 環形進度條（從 0 開始，之後更新 extent）
        self.ring_fg_id = self.canvas.create_arc(
            self.center - ring_r,
            self.center - ring_r,
            self.center + ring_r,
            self.center + ring_r,
            start=90,  # 由上方開始
            extent=0,
            style=tk.ARC,
            outline=self.app.colors["primary"],
            width=8,
        )

        # 番茄（紅色圓）
        r = self.base_radius
        self.tomato_circle_id = self.canvas.create_oval(
            self.center - r,
            self.center - r,
            self.center + r,
            self.center + r,
            fill=self.app.colors["primary"],
            outline="",
        )

        # 番茄 emoji 疊在中間
        self.tomato_emoji_id = self.canvas.create_text(
            self.center,
            self.center,
            text="🍅",
            font=("Arial", 40),
        )

        # 計時文字
        self.timer_text_id = self.canvas.create_text(
            self.center,
            self.center + 80,
            text=self.format_time(self.remaining_seconds),
            font=("Arial Rounded MT Bold", 26),
            fill=self.app.colors["timer_text"],
        )

        # 完成番茄數
        self.count_label = tk.Label(
            self,
            text=f"已完成番茄數：{self.tomato_count}",
            font=("Arial Rounded MT Bold", 12),
            bg=self.app.current_bg,
            fg=self.app.colors["text_secondary"],
        )
        self.count_label.pack(pady=(10, 5))

        # 控制按鈕列
        btn_frame = tk.Frame(self, bg=self.app.current_bg)
        btn_frame.pack(pady=15)

        self.start_btn = self.create_button(btn_frame, "開始", self.start_timer)
        self.pause_btn = self.create_button(btn_frame, "暫停", self.pause_timer)
        self.reset_btn = self.create_button(btn_frame, "重置", self.reset_timer)

        self.start_btn.grid(row=0, column=0, padx=8)
        self.pause_btn.grid(row=0, column=1, padx=8)
        self.reset_btn.grid(row=0, column=2, padx=8)

    def create_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=lambda: self.button_press_animation(btn, command),
            width=8,
            height=2,
            font=("Arial Rounded MT Bold", 11),
            bg=self.app.colors["primary"],
            fg="white",
            activebackground=self.app.colors["primary_dark"],
            activeforeground="white",
            bd=0,
            relief="ridge",
            highlightthickness=0,
        )
        return btn

    def button_press_animation(self, btn, command):
        # Material Design 風格：按下微縮放 + 顏色加深
        btn.config(bg=self.app.colors["primary_dark"])
        btn.config(font=("Arial Rounded MT Bold", 10))
        self.after(
            120,
            lambda: btn.config(
                bg=self.app.colors["primary"],
                font=("Arial Rounded MT Bold", 11),
            ),
        )
        command()

    # -------- 計時邏輯 --------
    def format_time(self, sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.breath_running = True
            self.animate_breath()
            self.run_countdown()

    def pause_timer(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.is_running = False
        self.breath_running = False

    def reset_timer(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.is_running = False
        self.breath_running = False

        # 重置為一輪的開始狀態
        self.current_phase = "工作"
        self.session_cycle = 0
        self.tomato_count = 0

        # 重新抓設定，避免使用者在設定頁更新時間後此頁面沒同步
        self.sync_profile_from_app()

        self.remaining_seconds = self.work_duration
        self.current_session_total = self.work_duration

        self.update_all_ui(full_reset=True)

    def run_countdown(self):
        if self.remaining_seconds > 0 and self.is_running:
            self.remaining_seconds -= 1
            self.update_all_ui()
            self.after_id = self.after(1000, self.run_countdown)
        else:
            if self.is_running:
                self.switch_phase()

    def switch_phase(self):
        # 完成一個工作階段
        if self.current_phase == "工作":
            self.tomato_count += 1
            self.session_cycle += 1
            if self.session_cycle % 4 == 0:
                self.current_phase = "長休息"
                self.remaining_seconds = self.long_break_duration
                self.current_session_total = self.long_break_duration
            else:
                self.current_phase = "短休息"
                self.remaining_seconds = self.short_break_duration
                self.current_session_total = self.short_break_duration
        else:
            # 任何休息之後都回到工作階段
            self.current_phase = "工作"
            self.remaining_seconds = self.work_duration
            self.current_session_total = self.work_duration

        # 每個新階段開始時「重新啟動呼吸動畫」
        self.breath_running = True
        self.animate_breath()
        self.update_all_ui()
        self.run_countdown()

    def update_all_ui(self, full_reset=False):
        # 更新 Canvas 計時文字
        self.canvas.itemconfig(self.timer_text_id, text=self.format_time(self.remaining_seconds))
        # 階段文字
        self.phase_label.config(text=f"階段：{self.current_phase}")
        # 完成番茄數
        self.count_label.config(text=f"已完成番茄數：{self.tomato_count}")

        # 更新環形進度條
        if self.current_session_total > 0:
            progress = 1 - self.remaining_seconds / self.current_session_total
        else:
            progress = 0
        extent = progress * 360
        self.canvas.itemconfig(self.ring_fg_id, extent=extent)

        if full_reset:
            # 完整重置時，進度條回到 0，番茄恢復原始尺寸
            self.canvas.itemconfig(self.ring_fg_id, extent=0)
            self.breath_phase = 0.0
            self.reset_tomato_size()

    # -------- Canvas 動畫：番茄柔和呼吸 --------
    def animate_breath(self):
        if not self.breath_running:
            self.reset_tomato_size()
            return

        # 呼吸週期 ~ 2 秒：phase 0 → 2π
        self.breath_phase += 0.12
        scale = 1.0 + 0.05 * math.sin(self.breath_phase)  # 0.95 ~ 1.05
        r = int(self.base_radius * scale)

        self.canvas.coords(
            self.tomato_circle_id,
            self.center - r,
            self.center - r,
            self.center + r,
            self.center + r,
        )
        # Emoji 不動，保持在中間即可

        # 每 50ms 更新一次，平滑不晃眼
        self.after(50, self.animate_breath)

    def reset_tomato_size(self):
        r = self.base_radius
        self.canvas.coords(
            self.tomato_circle_id,
            self.center - r,
            self.center - r,
            self.center + r,
            self.center + r,
        )

    # -------- 設定同步 --------
    def sync_profile_from_app(self):
        """從 App 的 profiles 同步最新設定（例如使用者在設定頁修改時間）"""
        profile = self.app.profiles[self.profile_key]
        self.work_duration = profile["durations"]["work"]
        self.short_break_duration = profile["durations"]["short"]
        self.long_break_duration = profile["durations"]["long"]


class SettingsPage(tk.Frame):
    """
    設定頁：可以調整不同模式的倒數時間（以分鐘為單位）
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.current_bg)
        self.app = app

        title = tk.Label(
            self,
            text="設定",
            font=("Arial Rounded MT Bold", 20),
            bg=app.current_bg,
            fg=app.colors["text_primary"],
        )
        title.pack(pady=(15, 10))

        desc = tk.Label(
            self,
            text="調整各模式的番茄時間（分鐘）",
            font=("Arial", 11),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        )
        desc.pack(pady=(0, 15))

        # 模式選擇
        mode_frame = tk.Frame(self, bg=app.current_bg)
        mode_frame.pack(pady=5)

        tk.Label(
            mode_frame,
            text="選擇模式：",
            font=("Arial", 11),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        ).grid(row=0, column=0, padx=5)

        self.selected_profile = tk.StringVar(value="work")
        options = [("工作模式", "work"), ("讀書模式", "study"), ("運動 / 休息", "balance")]
        col = 1
        for text, key in options:
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                value=key,
                variable=self.selected_profile,
                font=("Arial", 10),
                bg=app.current_bg,
                fg=app.colors["text_secondary"],
                selectcolor=app.current_bg,
                activebackground=app.current_bg,
                command=self.load_profile_values,
            )
            rb.grid(row=0, column=col, padx=5)
            col += 1

        # 時間設定區
        form_frame = tk.Frame(self, bg=app.current_bg)
        form_frame.pack(pady=15)

        tk.Label(
            form_frame,
            text="工作時間（分鐘）：",
            font=("Arial", 11),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        ).grid(row=0, column=0, sticky="e", padx=5, pady=3)

        tk.Label(
            form_frame,
            text="短休息（分鐘）：",
            font=("Arial", 11),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        ).grid(row=1, column=0, sticky="e", padx=5, pady=3)

        tk.Label(
            form_frame,
            text="長休息（分鐘）：",
            font=("Arial", 11),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        ).grid(row=2, column=0, sticky="e", padx=5, pady=3)

        self.work_var = tk.IntVar(value=25)
        self.short_var = tk.IntVar(value=5)
        self.long_var = tk.IntVar(value=15)

        self.work_entry = tk.Spinbox(form_frame, from_=1, to=180, textvariable=self.work_var, width=5)
        self.short_entry = tk.Spinbox(form_frame, from_=1, to=60, textvariable=self.short_var, width=5)
        self.long_entry = tk.Spinbox(form_frame, from_=1, to=120, textvariable=self.long_var, width=5)

        self.work_entry.grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.short_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        self.long_entry.grid(row=2, column=1, padx=5, pady=3, sticky="w")

        # 套用按鈕
        apply_btn = tk.Button(
            self,
            text="套用設定",
            command=self.apply_settings,
            width=12,
            height=2,
            font=("Arial Rounded MT Bold", 11),
            bg=app.colors["primary"],
            fg="white",
            activebackground=app.colors["primary_dark"],
            bd=0,
            relief="ridge",
        )
        apply_btn.pack(pady=10)

        self.status_label = tk.Label(
            self,
            text="",
            font=("Arial", 10),
            bg=app.current_bg,
            fg=app.colors["text_secondary"],
        )
        self.status_label.pack(pady=5)

        # 初次載入預設值
        self.load_profile_values()

    def load_profile_values(self):
        key = self.selected_profile.get()
        profile = self.app.profiles[key]
        self.work_var.set(profile["durations"]["work"] // 60)
        self.short_var.set(profile["durations"]["short"] // 60)
        self.long_var.set(profile["durations"]["long"] // 60)

    def apply_settings(self):
        key = self.selected_profile.get()
        profile = self.app.profiles[key]

        profile["durations"]["work"] = self.work_var.get() * 60
        profile["durations"]["short"] = self.short_var.get() * 60
        profile["durations"]["long"] = self.long_var.get() * 60

        # 通知對應頁面同步（如果頁面存在）
        page = self.app.pages.get(key)
        if isinstance(page, PomodoroTimerPage):
            page.sync_profile_from_app()
            # 如果當前頁面沒有在跑，順便刷新畫面顯示新的起始時間
            if not page.is_running:
                page.remaining_seconds = page.work_duration
                page.current_session_total = page.work_duration
                page.update_all_ui(full_reset=True)

        self.status_label.config(text="設定已更新（新的時間於下一輪開始生效）")


class PomodoroApp(tk.Tk):
    """
    主程式：多頁式 Material Design 風格番茄鐘
    - 工作模式
    - 讀書模式
    - 運動 / 休息平衡
    - 設定頁
    """

    def __init__(self):
        super().__init__()
        self.title("多模式番茄鐘")
        self.geometry("440x680")
        self.resizable(False, False)

        # Material Design 風格配色
        self.colors = {
            "primary": "#FF7043",       # Deep orange 300
            "primary_dark": "#F4511E",  # Deep orange 600
            "background": "#FAFAFA",
            "surface": "#FFFFFF",
            "accent": "#FFE0B2",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "timer_text": "#D84315",
        }
        self.current_bg = self.colors["background"]

        # 各模式預設時間設定
        self.profiles = {
            "work": {
                "label": "工作模式",
                "durations": {
                    "work": 25 * 60,
                    "short": 5 * 60,
                    "long": 15 * 60,
                },
            },
            "study": {
                "label": "讀書模式",
                "durations": {
                    "work": 50 * 60,
                    "short": 10 * 60,
                    "long": 20 * 60,
                },
            },
            "balance": {
                "label": "運動 / 休息模式",
                "durations": {
                    "work": 30 * 60,
                    "short": 10 * 60,
                    "long": 30 * 60,
                },
            },
        }

        self.configure(bg=self.current_bg)

        # 頂部 App Bar
        self.build_app_bar()

        # 內容容器（放各頁面）
        self.container = tk.Frame(self, bg=self.current_bg)
        self.container.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        # 儲存各頁面實例
        self.pages = {}

        self.build_pages()
        self.current_page_key = None
        self.show_page("work", animate=False)

    def build_app_bar(self):
        app_bar = tk.Frame(self, bg=self.colors["surface"], height=56)
        app_bar.pack(fill="x")

        title = tk.Label(
            app_bar,
            text="番茄鐘 App",
            font=("Arial Rounded MT Bold", 16),
            bg=self.colors["surface"],
            fg=self.colors["text_primary"],
        )
        title.pack(side="left", padx=16)

        # 簡單的 navigation tabs
        nav_frame = tk.Frame(app_bar, bg=self.colors["surface"])
        nav_frame.pack(side="right", padx=8)

        self.nav_buttons = {}
        nav_items = [
            ("工作", "work"),
            ("讀書", "study"),
            ("運動 / 休息", "balance"),
            ("設定", "settings"),
        ]
        for text, key in nav_items:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=lambda k=key: self.show_page(k),
                font=("Arial", 10),
                bg=self.colors["surface"],
                fg=self.colors["text_secondary"],
                bd=0,
                highlightthickness=0,
                activebackground=self.colors["surface"],
                activeforeground=self.colors["primary"],
                padx=8,
                pady=4,
            )
            btn.pack(side="left", padx=2)
            self.nav_buttons[key] = btn

    def build_pages(self):
        # 使用 place 疊放，並透過動畫做切換效果
        work_page = PomodoroTimerPage(self.container, self, "work", "工作番茄鐘")
        study_page = PomodoroTimerPage(self.container, self, "study", "讀書模式番茄鐘")
        balance_page = PomodoroTimerPage(self.container, self, "balance", "運動 / 休息平衡番茄鐘")
        settings_page = SettingsPage(self.container, self)

        self.pages["work"] = work_page
        self.pages["study"] = study_page
        self.pages["balance"] = balance_page
        self.pages["settings"] = settings_page

        for page in self.pages.values():
            page.place(relx=1.0, rely=0.0, relwidth=1.0, relheight=1.0)

    def highlight_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(fg=self.colors["primary"])
            else:
                btn.config(fg=self.colors["text_secondary"])

    def show_page(self, key, animate=True):
        if self.current_page_key == key:
            return

        new_page = self.pages[key]
        old_page = self.pages.get(self.current_page_key) if self.current_page_key else None

        self.highlight_nav(key)

        if not animate or old_page is None:
            # 初次或不需要動畫時，直接顯示
            new_page.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            if old_page and old_page is not new_page:
                old_page.place_forget()
        else:
            # 簡單 slide 動畫：舊頁面往左，新頁面從右滑入
            width = self.container.winfo_width() or 400

            # 先把新頁面放在右邊
            new_page.place(x=width, y=0, relwidth=1.0, relheight=1.0)

            def animate_step(step=0, steps=12):
                t = step / steps
                x_new = int(width * (1 - t))
                x_old = int(-width * t)
                new_page.place(x=x_new, y=0)
                old_page.place(x=x_old, y=0)
                if step < steps:
                    self.after(16, animate_step, step + 1, steps)
                else:
                    new_page.place(x=0, y=0, relwidth=1.0, relheight=1.0)
                    old_page.place_forget()

            animate_step()

        self.current_page_key = key


if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()
