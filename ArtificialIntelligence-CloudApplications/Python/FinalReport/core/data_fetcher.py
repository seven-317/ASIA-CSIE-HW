import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass

# ---------------------------------------------
# Optional libraries
# ---------------------------------------------
_HAS_CCXT = False
_HAS_YF = False
try:
    import ccxt
    _HAS_CCXT = True
except Exception:
    pass
try:
    import yfinance as yf
    _HAS_YF = True
except Exception:
    pass


# ---------------------------------------------
# Data container
# ---------------------------------------------
@dataclass
class FetchResult:
    df: pd.DataFrame
    last_price: float
    source: str


# ---------------------------------------------
# Main Fetcher
# ---------------------------------------------
class DataFetcher:
    def __init__(self):
        self.exchange = None
        if _HAS_CCXT:
            try:
                self.exchange = ccxt.binance()
            except Exception:
                self.exchange = None

    def is_crypto(self, symbol: str) -> bool:
        """判斷是否為加密貨幣（含有 / 符號）"""
        return "/" in symbol

    # -----------------------------------------
    # Synthetic fallback data
    # -----------------------------------------
    def _synthetic_series(self, n=300, start=100.0) -> FetchResult:
        """無法抓取資料時產生假資料"""
        idx = pd.date_range(end=datetime.now(), periods=n, freq="min")
        base = start + 2 * np.sin(np.linspace(0, 8 * np.pi, n))
        noise = np.random.normal(0, 0.5, n)
        close = base + noise
        open_ = close + np.random.normal(0, 0.2, n)
        high = np.maximum(open_, close) + np.abs(np.random.normal(0, 0.4, n))
        low = np.minimum(open_, close) - np.abs(np.random.normal(0, 0.4, n))
        vol = np.random.randint(100, 1000, n)
        df = pd.DataFrame({
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": vol
        }, index=idx)
        return FetchResult(df, float(close[-1]), "synthetic")

    # -----------------------------------------
    # Initial OHLCV Fetch
    # -----------------------------------------
    def fetch_initial(self, symbol: str, tf: str, lookback: int | None = None) -> FetchResult:
        """
        初始抓取 OHLCV 資料：
        - Crypto → 使用 CCXT (Binance)
        - Stock → 使用 YFinance
        - 無資料 → 使用 synthetic 模擬波
        """

        # 自動決定抓取範圍（越大 Prophet 越穩定）
        if lookback is None:
            if tf.endswith("s") or tf.endswith("m"):
                lookback = 2000
            elif tf.endswith("h"):
                lookback = 1500
            else:  # 日或週
                lookback = 1000

        # -------------------------------------
        # 1️⃣ Crypto via CCXT
        # -------------------------------------
        if self.is_crypto(symbol) and self.exchange:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=tf, limit=lookback)
                df = pd.DataFrame(ohlcv, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
                df["ts"] = pd.to_datetime(df["ts"], unit="ms")
                df = df.set_index("ts").tz_localize(None)
                # 限制最多 3000 根，以免 Prophet 太慢
                df = df.tail(3000)
                return FetchResult(df, float(df["Close"].iloc[-1]), "ccxt")
            except Exception as e:
                print(f"[DataFetcher] CCXT error: {e}")

        # -------------------------------------
        # 2️⃣ Stocks via YFinance
        # -------------------------------------
        if _HAS_YF:
            try:
                # timeframe 對應 interval
                interval_map = {
                    "1s": "1m", "5s": "1m", "10s": "1m", "30s": "1m",
                    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                    "1h": "60m", "4h": "60m", "1d": "1d", "1w": "1wk"
                }
                yf_tf = interval_map.get(tf, "1h")
                period = "1y" if "h" in tf or "d" in tf else "7d"

                data = yf.Ticker(symbol).history(period=period, interval=yf_tf, prepost=True, actions=False)
                data = data.rename(columns=str.title)
                data = data[["Open", "High", "Low", "Close", "Volume"]].dropna()
                data = data.tail(3000)
                return FetchResult(data, float(data["Close"].iloc[-1]), "yfinance")
            except Exception as e:
                print(f"[DataFetcher] YFinance error: {e}")

        # -------------------------------------
        # 3️⃣ Fallback synthetic data
        # -------------------------------------
        return self._synthetic_series()

    # -----------------------------------------
    # Realtime Ticker Fetch
    # -----------------------------------------
    def fetch_ticker_price(self, symbol: str) -> float | None:
        """取得最新價格，用於即時更新"""
        # 加密貨幣
        if self.is_crypto(symbol) and self.exchange:
            try:
                return float(self.exchange.fetch_ticker(symbol)["last"])
            except Exception:
                return None

        # 股票
        if _HAS_YF:
            try:
                info = yf.Ticker(symbol).history(period="7d", interval="1m", prepost=True, actions=False)
                if len(info) > 0:
                    return float(info["Close"].iloc[-1])
            except Exception:
                return None

        return None
