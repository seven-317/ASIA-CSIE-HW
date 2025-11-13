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
    # 🔮 AI 預測主邏輯（含預測區間）
    # ==========================================================
    def forecast(self, df: pd.DataFrame, steps: int = 5, tf: str = "1m") -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=["yhat", "yhat_lower", "yhat_upper"])

        unit_name, val, pandas_freq = self._parse_tf(tf)
        print(f"[Predictor] Timeframe={tf} → unit={unit_name}, step={val}, pandas_freq={pandas_freq}")

        # ======================================================
        # ✅ Prophet 模型預測
        # ======================================================
        if self.use_prophet:
            try:
                hist = df[["Close"]].copy().reset_index()
                hist.columns = ["ds", "y"]
                hist = hist.tail(1000)

                # log 平滑
                hist["y"] = np.log(hist["y"].replace(0, np.nan)).fillna(method="ffill")

                is_short_tf = any(tf.endswith(x) for x in ["s", "m"])
                m = Prophet(
                    seasonality_mode="additive",
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=False,
                    changepoint_prior_scale=0.5,
                    n_changepoints=80,
                    interval_width=0.5
                )
                m.fit(hist)

                last_ts = df.index[-1]
                future_start = last_ts + pd.Timedelta(val, unit=unit_name)
                future = pd.date_range(start=future_start, periods=steps, freq=pandas_freq)
                future_df = pd.DataFrame({"ds": future})

                fcst = m.predict(future_df)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
                fcst[["yhat", "yhat_lower", "yhat_upper"]] = np.exp(fcst[["yhat", "yhat_lower", "yhat_upper"]])
                fcst = fcst.set_index("ds")

                # 智能波動範圍限制
                last_price = df["Close"].iloc[-1]
                vol = np.std(df["Close"].pct_change().dropna()) * 100
                clamp = max(0.05, min(0.25, vol / 5))

                fcst["yhat"] = np.clip(fcst["yhat"], last_price * (1 - clamp), last_price * (1 + clamp))
                fcst["yhat_lower"] = np.clip(fcst["yhat_lower"], last_price * (1 - clamp * 1.5), last_price * (1 + clamp))
                fcst["yhat_upper"] = np.clip(fcst["yhat_upper"], last_price * (1 - clamp), last_price * (1 + clamp * 1.5))

                return fcst[["yhat", "yhat_lower", "yhat_upper"]]
            except Exception as e:
                print(f"[Predictor] Prophet failed: {e}")

        # ======================================================
        # ⚙️ fallback：均線外推
        # ======================================================
        tail = df["Close"].tail(20)
        y = float(tail.mean()) if len(tail) else float(df["Close"].iloc[-1])
        last_ts = df.index[-1] if len(df) else datetime.now()
        idx = pd.date_range(start=last_ts + pd.Timedelta(val, unit=unit_name), periods=steps, freq=pandas_freq)
        return pd.DataFrame({
            "yhat": [y] * steps,
            "yhat_lower": [y * 0.98] * steps,
            "yhat_upper": [y * 1.02] * steps
        }, index=idx)
