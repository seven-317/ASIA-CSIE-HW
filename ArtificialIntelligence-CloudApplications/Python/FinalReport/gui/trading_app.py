import threading
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import mplfinance as mpf
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core import DataFetcher, Predictor, rsi, macd, Sounder, tf_tier, REFRESH_BY_TIER, TIMEFRAME_CHOICES


class TradingApp:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("AI 智慧交易視覺系統")
        self.root.state("zoomed")
        ttk.Style("cyborg")

        # --- 模組初始化 ---
        self.fetcher = DataFetcher()
        self.predictor = Predictor()
        self.sounder = Sounder()

        # --- 狀態變數 ---
        self.symbol_var = tk.StringVar(value="AAPL")
        self.tf_var = tk.StringVar(value="1m")
        self.horizon_var = tk.StringVar(value="3")
        self.threshold_var = tk.DoubleVar(value=0.01)
        self.df = pd.DataFrame()
        self.pred_df = pd.DataFrame()
        self.update_job = None

        # --- GUI 組件 ---
        self._build_topbar()
        self._build_metrics_frame()
        self._build_chart()

    # ==========================================================
    # 🧱 GUI 組件
    # ==========================================================
    def _build_topbar(self):
        top = ttk.Frame(self.root)
        top.pack(side=TOP, fill=X, padx=10, pady=6)

        ttk.Label(top, text="代號").pack(side=LEFT)
        ttk.Entry(top, textvariable=self.symbol_var, width=20).pack(side=LEFT)

        ttk.Label(top, text="週期").pack(side=LEFT, padx=(10, 0))
        ttk.Combobox(top, textvariable=self.tf_var, values=TIMEFRAME_CHOICES,
                     width=6, state="readonly").pack(side=LEFT)

        ttk.Label(top, text="預測範圍").pack(side=LEFT, padx=(10, 0))
        self.ent_h = ttk.Entry(top, textvariable=self.horizon_var, width=6)
        self.ent_h.pack(side=LEFT)

        ttk.Label(top, text="閾值(%)").pack(side=LEFT, padx=(10, 0))
        ttk.Entry(top, textvariable=self.threshold_var, width=6).pack(side=LEFT)

        ttk.Button(top, text="查詢 / 開始", command=self.on_query).pack(side=LEFT, padx=10)
        self.lbl_src = ttk.Label(top, text="來源：-")
        self.lbl_src.pack(side=RIGHT)

    def _build_metrics_frame(self):
        lf = ttk.Labelframe(self.root, text="即時資訊", padding=8)
        lf.pack(side=TOP, fill=X, padx=10, pady=6)

        self.price_var = tk.StringVar(value="—")
        self.pred_var = tk.StringVar(value="—")
        self.vol_var = tk.StringVar(value="—")
        self.vola_var = tk.StringVar(value="—")
        self.pred_range_var = tk.StringVar(value="—")

        ttk.Label(lf, text="即時價格：").grid(row=0, column=0)
        ttk.Label(lf, textvariable=self.price_var, bootstyle=SUCCESS).grid(row=0, column=1)
        ttk.Label(lf, text="預測價格：").grid(row=0, column=2)
        ttk.Label(lf, textvariable=self.pred_var, bootstyle=PRIMARY).grid(row=0, column=3)
        ttk.Label(lf, text="成交量：").grid(row=0, column=4)
        ttk.Label(lf, textvariable=self.vol_var).grid(row=0, column=5)
        ttk.Label(lf, text="波動率：").grid(row=0, column=6)
        ttk.Label(lf, textvariable=self.vola_var).grid(row=0, column=7)
        ttk.Label(lf, text="預測範圍：").grid(row=0, column=8)
        ttk.Label(lf, textvariable=self.pred_range_var, bootstyle=INFO).grid(row=0, column=9)

    def _build_chart(self):
        frm = ttk.Frame(self.root)
        frm.pack(side=TOP, fill=BOTH, expand=YES, padx=10, pady=10)
        self.fig, self.ax_main = plt.subplots(2, 1, figsize=(12, 7), dpi=100, sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frm)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frm, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=TOP, fill=X)

    # ==========================================================
    # ⚙️ 主要流程
    # ==========================================================
    def on_query(self):
        sym = self.symbol_var.get().strip()
        tf = self.tf_var.get()
        if not sym:
            return
        threading.Thread(target=self._fetch_data, args=(sym, tf), daemon=True).start()

    def _fetch_data(self, symbol, tf):
        res = self.fetcher.fetch_initial(symbol, tf)
        self.df = res.df
        self.lbl_src.configure(text=f"來源：{res.source}")
        self.root.after(0, self._after_data_loaded)

    def _after_data_loaded(self):
        self._recompute_pred()
        self._draw_chart()
        self._schedule_update()

    def _recompute_pred(self):
        try:
            steps = int(self.horizon_var.get())
        except Exception:
            steps = 3
        tf = self.tf_var.get()
        self.pred_df = self.predictor.forecast(self.df, steps=steps, tf=tf)
        self._update_pred_range_label()

    def _schedule_update(self):
        tier = tf_tier(self.tf_var.get())
        interval = REFRESH_BY_TIER.get(tier, 10_000)
        self.update_job = self.root.after(interval, self._update_loop)

    def _update_loop(self):
        sym = self.symbol_var.get().strip()
        tf = self.tf_var.get()
        try:
            th = max(0.0, min(float(self.threshold_var.get()) / 100.0, 1.0))
        except ValueError:
            th = 0.01

        new_price = self.fetcher.fetch_ticker_price(sym)
        if new_price is None:
            new_price = float(self.df["Close"].iloc[-1]) + np.random.normal(0, 0.1)
        self.df.iloc[-1, self.df.columns.get_loc("Close")] = new_price

        self._recompute_pred()
        self._draw_chart()
        self._update_metrics()

        try:
            if len(self.pred_df) > 0:
                pred = float(self.pred_df["yhat"].iloc[-1])
                real = float(self.df["Close"].iloc[-1])
                th = float(self.threshold_var.get()) / 100.0
                if pred > real * (1 + th) or pred < real * (1 - th):
                    self.sounder.maybe_beep(True)
        except:
            pass

        self._schedule_update()

    # ==========================================================
    # 📈 圖表繪製與資料更新
    # ==========================================================
    def _update_metrics(self):
        if len(self.df) > 0:
            self.price_var.set(f"{self.df['Close'].iloc[-1]:.4f}")
        if len(self.pred_df) > 0:
            self.pred_var.set(f"{self.pred_df['yhat'].iloc[-1]:.4f}")

        if "Volume" in self.df.columns and len(self.df) > 1:
            self.vol_var.set(f"{int(self.df['Volume'].tail(10).mean()):,}")
        else:
            self.vol_var.set("—")

        if len(self.df) > 10:
            ret = self.df["Close"].pct_change().tail(30).std() * np.sqrt(30)
            self.vola_var.set(f"{ret*100:.2f}%")
        else:
            self.vola_var.set("—")

    def _draw_chart(self):
            """繪製預測線（上）與即時價格線（下）＋閾值提示線"""
            for ax in self.ax_main:
                ax.clear()

            df_to_plot = self.df.tail(300)
            close = df_to_plot["Close"]

            # 取最後即時價與閾值
            if len(self.df) > 0:
                real = float(self.df["Close"].iloc[-1])
            else:
                real = 0.0
            th = float(self.threshold_var.get()) / 100.0

            upper_line = real * (1 + th)
            lower_line = real * (1 - th)

            # --- 上方圖：預測線 + 閾值線 ---
            self.ax_main[0].set_title("AI 預測與閾值範圍", fontsize=11, pad=8)
            self.ax_main[0].set_ylabel("預測價格")
            self.ax_main[0].grid(True, linestyle="--", alpha=0.3)

            if len(self.pred_df) > 0:
                pred_concat = pd.concat([
                    pd.Series(np.nan, index=df_to_plot.index),
                    self.pred_df["yhat"]
                ])
                self.ax_main[0].plot(
                     pred_concat.index,
                     pred_concat.values,
                     color="orange",
                     linewidth=1.6,
                     label="AI 預測線"
                )

            # 閾值提示線（綠上紅下）
            self.ax_main[0].axhline(upper_line, color="lime", linestyle="--", linewidth=1, alpha=0.7, label=f"+{th*100:.1f}% 閾值線（多頭）")
            self.ax_main[0].axhline(lower_line, color="red", linestyle="--", linewidth=1, alpha=0.7, label=f"-{th*100:.1f}% 閾值線（空頭）")

            # --- 下方圖：即時價格 ---
            self.ax_main[1].set_ylabel("即時價格")
            self.ax_main[1].grid(True, linestyle="--", alpha=0.3)
            self.ax_main[1].plot(
                 close.index,
                 close.values,
                 color="deepskyblue",
                 linewidth=1.2,
                 label="即時價格線"
            )

            self.ax_main[0].legend(loc="upper left")
            self.ax_main[1].legend(loc="upper left")
            self.canvas.draw()


    def _update_pred_range_label(self):
        tf = self.tf_var.get()
        try:
            steps = int(self.horizon_var.get())
        except Exception:
            self.pred_range_var.set("—")
            return

        match = re.match(r"(\d+)([smhdw])", tf)
        if not match:
            self.pred_range_var.set("—")
            return

        num, unit = int(match.group(1)), match.group(2)
        total = num * steps
        unit_label = {
            "s": "秒",
            "m": "分鐘",
            "h": "小時",
            "d": "天",
            "w": "週"
        }.get(unit, "—")

        self.pred_range_var.set(f"{total} {unit_label}（基於 {tf}）")
