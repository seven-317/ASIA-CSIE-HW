from datetime import datetime
import pandas as pd
import numpy as np

# Prophet optional
_HAS_PROPHET = False
try:
    from prophet import Prophet
    _HAS_PROPHET = True
except Exception:
    _HAS_PROPHET = False


class Predictor:
    def __init__(self):
        self.use_prophet = _HAS_PROPHET

    # ==========================================================
    # 🧩 Timeframe 解析
    # ==========================================================
    def _parse_tf(self, tf: str) -> tuple[str, int, str]:
        unit_map = {
            "s": ("s", "s"),
            "m": ("min", "min"),
            "h": ("h", "h"),
            "d": ("d", "D"),
            "w": ("w", "W"),
        }
        for k, (unit_name, pd_code) in unit_map.items():
            if tf.endswith(k):
                try:
                    val = int(tf.replace(k, ""))
                except Exception:
                    val = 1
                return unit_name, val, f"{val}{pd_code}"
        return "min", 1, "1min"

    # ==========================================================
    # 🔮 預測主邏輯
    # ==========================================================
    def forecast(self, df: pd.DataFrame, steps: int = 5, tf: str = "1m") -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=["yhat"])

        # --- 時間解析 ---
        unit_name, val, pandas_freq = self._parse_tf(tf)
        print(f"[Predictor] Timeframe={tf} → unit={unit_name}, step={val}, pandas_freq={pandas_freq}")

        # ======================================================
        # ✅ Prophet 模型預測
        # ======================================================
        if self.use_prophet:
            try:
                # 準備 Prophet 格式資料
                hist = df[["Close"]].copy()
                hist = hist.reset_index()
                hist.columns = ["ds", "y"]  # Prophet 需要這兩個欄位
                hist = hist.tail(300)

                m = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=True,
                    changepoint_prior_scale=0.3
                )
                m.fit(hist)

                # 產生未來時間
                last_ts = df.index[-1]
                future_start = last_ts + pd.Timedelta(val, unit=unit_name)
                future = pd.date_range(start=future_start, periods=steps, freq=pandas_freq)
                future_df = pd.DataFrame({"ds": future})

                fcst = m.predict(future_df)[["ds", "yhat"]]
                fcst = fcst.set_index("ds")

                # 限制異常值範圍（避免 Prophet 預測爆炸）
                last_price = df["Close"].iloc[-1]
                fcst["yhat"] = np.clip(fcst["yhat"], last_price * 0.5, last_price * 1.5)
                return fcst[["yhat"]]
            except Exception as e:
                print(f"[Predictor] Prophet failed: {e}")

        # ======================================================
        # ⚙️ fallback：均線外推
        # ======================================================
        tail = df["Close"].tail(20)
        y = float(tail.mean()) if len(tail) else float(df["Close"].iloc[-1])
        last_ts = df.index[-1] if len(df) else datetime.now()
        idx = pd.date_range(start=last_ts + pd.Timedelta(val, unit=unit_name), periods=steps, freq=pandas_freq)
        return pd.DataFrame({"yhat": [y] * steps}, index=idx)
