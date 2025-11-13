import threading
import re
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import mplfinance as mpf
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ✅ 讓 Matplotlib 正常顯示中文與負號（Windows）
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

from core import (
    DataFetcher, Predictor, rsi, macd, Sounder,
    tf_tier, REFRESH_BY_TIER, TIMEFRAME_CHOICES
)


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
        self.symbol_var = tk.StringVar(value="BTC/USDT")
        self.tf_var = tk.StringVar(value="1m")
        self.horizon_var = tk.StringVar(value="3")      # 預測根數（使用者可輸入任意整數）
        self.threshold_var = tk.DoubleVar(value=1)      # 以「百分比」輸入；1 = 1%
        self.show_band_var = tk.BooleanVar(value=True)  # 顯示/隱藏預測區間
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

        # ✅ 顯示/隱藏預測區間的切換
        ttk.Checkbutton(
            top, text="顯示預測區間", variable=self.show_band_var,
            bootstyle=SUCCESS, command=self._draw_chart
        ).pack(side=LEFT, padx=(10, 0))

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

        ttk.Label(lf, text="即時價格：").grid(row=0, column=0, sticky=W, padx=(0, 4))
        ttk.Label(lf, textvariable=self.price_var, bootstyle=SUCCESS).grid(row=0, column=1, sticky=W, padx=(0, 16))

        ttk.Label(lf, text="預測價格：").grid(row=0, column=2, sticky=W, padx=(0, 4))
        ttk.Label(lf, textvariable=self.pred_var, bootstyle=PRIMARY).grid(row=0, column=3, sticky=W, padx=(0, 16))

        ttk.Label(lf, text="成交量：").grid(row=0, column=4, sticky=W, padx=(0, 4))
        ttk.Label(lf, textvariable=self.vol_var).grid(row=0, column=5, sticky=W, padx=(0, 16))

        ttk.Label(lf, text="波動率：").grid(row=0, column=6, sticky=W, padx=(0, 4))
        ttk.Label(lf, textvariable=self.vola_var).grid(row=0, column=7, sticky=W, padx=(0, 16))

        ttk.Label(lf, text="預測範圍：").grid(row=0, column=8, sticky=W, padx=(0, 4))
        ttk.Label(lf, textvariable=self.pred_range_var, bootstyle=INFO).grid(row=0, column=9, sticky=W)

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
        # 取消既有更新排程（避免多重循環）
        if self.update_job:
            try:
                self.root.after_cancel(self.update_job)
            except Exception:
                pass
            self.update_job = None
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

        # 閾值（百分比 → 小數）
        try:
            th = max(0.0, min(float(self.threshold_var.get()) / 100.0, 1.0))
        except ValueError:
            th = 0.01  # fallback 1%

        # 實時價格（ticker）或 fallback 隨機微變化
        new_price = self.fetcher.fetch_ticker_price(sym)
        if new_price is None:
            new_price = float(self.df["Close"].iloc[-1]) + np.random.normal(0, 0.1)

        # 更新最後一根 close（保持 timeframe 解耦的即時變化）
        if len(self.df) == 0:
            self.df = pd.DataFrame({"Close": [new_price]}, index=[pd.Timestamp.utcnow()])
        else:
            self.df.iloc[-1, self.df.columns.get_loc("Close")] = new_price

        # 重新預測與重畫
        self._recompute_pred()
        self._draw_chart()
        self._update_metrics()

        # 提示音（自動偵測多/空突破）
        try:
            if len(self.pred_df) > 0:
                pred = float(self.pred_df.iloc[-1]["yhat"])
                real = float(self.df["Close"].iloc[-1])
                if pred > real * (1 + th) or pred < real * (1 - th):
                    self.sounder.maybe_beep(True)
        except Exception:
            pass

        self._schedule_update()

    # ==========================================================
    # 📈 圖表繪製與資料更新
    # ==========================================================
    def _update_metrics(self):
        if len(self.df) > 0:
            self.price_var.set(f"{self.df['Close'].iloc[-1]:.4f}")
        if len(self.pred_df) > 0 and "yhat" in self.pred_df.columns:
            self.pred_var.set(f"{self.pred_df['yhat'].iloc[-1]:.4f}")
        else:
            self.pred_var.set("—")

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
        """繪製：上方 AI 預測（含區間帶 + 閾值線）、下方 即時價格線"""
        for ax in self.ax_main:
            ax.clear()

        df_to_plot = self.df.tail(300)
        close = df_to_plot["Close"] if "Close" in df_to_plot.columns else pd.Series(dtype=float)

        # 即時價與閾值
        real = float(self.df["Close"].iloc[-1]) if len(self.df) > 0 else 0.0
        th = float(self.threshold_var.get()) / 100.0
        upper_line = real * (1 + th)
        lower_line = real * (1 - th)

        # --- 上方圖：AI 預測 + 區間 + 閾值 ---
        self.ax_main[0].set_title("AI 預測與閾值範圍", fontsize=12, pad=8)
        self.ax_main[0].set_ylabel("預測價格")
        self.ax_main[0].grid(True, linestyle="--", alpha=0.3)

        if len(self.pred_df) > 0:
            # 把預測拼接到歷史尾端（前段用 NaN 補齊，以對齊 X 軸）
            base_index = df_to_plot.index
            yhat_full = pd.concat([pd.Series(np.nan, index=base_index), self.pred_df.get("yhat", pd.Series(dtype=float))])

            self.ax_main[0].plot(
                yhat_full.index, yhat_full.values,
                color="orange", linewidth=1.8, label="AI 預測線"
            )

            # ✅ 顯示預測區間（上/下界 + 灰色填滿）
            if self.show_band_var.get() and "yhat_upper" in self.pred_df.columns and "yhat_lower" in self.pred_df.columns:
                up_full = pd.concat([pd.Series(np.nan, index=base_index), self.pred_df["yhat_upper"]])
                low_full = pd.concat([pd.Series(np.nan, index=base_index), self.pred_df["yhat_lower"]])

                # 灰色虛線（上/下界）
                self.ax_main[0].plot(up_full.index, up_full.values, color="gray", linestyle="--", linewidth=1, alpha=0.9, label="預測上界")
                self.ax_main[0].plot(low_full.index, low_full.values, color="gray", linestyle="--", linewidth=1, alpha=0.9, label="預測下界")

                # 區間帶填色（半透明）
                self.ax_main[0].fill_between(
                    up_full.index, low_full.values, up_full.values,
                    color="gray", alpha=0.12, step=None
                )

        # 閾值提示線（綠上紅下）
        self.ax_main[0].axhline(upper_line, color="lime", linestyle="--", linewidth=1, alpha=0.75, label=f"+{th*100:.1f}% 閾值線（多頭）")
        self.ax_main[0].axhline(lower_line, color="red", linestyle="--", linewidth=1, alpha=0.75, label=f"-{th*100:.1f}% 閾值線（空頭）")

        # --- 下方圖：即時價格 ---
        self.ax_main[1].set_ylabel("即時價格")
        self.ax_main[1].grid(True, linestyle="--", alpha=0.3)
        if len(close) > 0:
            self.ax_main[1].plot(
                close.index, close.values,
                color="deepskyblue", linewidth=1.2, label="即時價格線"
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
        unit_label = {"s": "秒", "m": "分鐘", "h": "小時", "d": "天", "w": "週"}.get(unit, "—")
        self.pred_range_var.set(f"{total} {unit_label}（基於 {tf}）")
