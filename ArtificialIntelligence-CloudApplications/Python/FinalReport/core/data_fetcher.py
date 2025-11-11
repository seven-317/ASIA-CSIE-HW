import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass

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


@dataclass
class FetchResult:
    df: pd.DataFrame
    last_price: float
    source: str


class DataFetcher:
    def __init__(self):
        self.exchange = None
        if _HAS_CCXT:
            try:
                self.exchange = ccxt.binance()
            except Exception:
                self.exchange = None

    def is_crypto(self, symbol):
        return "/" in symbol

    def _synthetic_series(self, n=300, start=100.0) -> FetchResult:
        """無法抓取資料時產生假資料"""
        idx = pd.date_range(end=datetime.now(), periods=n, freq="min")
        base = start + 2*np.sin(np.linspace(0, 8*np.pi, n))
        noise = np.random.normal(0, 0.5, n)
        close = base + noise
        open_ = close + np.random.normal(0, 0.2, n)
        high = np.maximum(open_, close) + np.abs(np.random.normal(0, 0.4, n))
        low = np.minimum(open_, close) - np.abs(np.random.normal(0, 0.4, n))
        vol = np.random.randint(100, 1000, n)
        df = pd.DataFrame({
            "Open": open_, "High": high, "Low": low,
            "Close": close, "Volume": vol
        }, index=idx)
        return FetchResult(df, float(close[-1]), "synthetic")

    def fetch_initial(self, symbol, tf, lookback=500):
        """初始抓取 OHLCV"""
        if self.is_crypto(symbol) and self.exchange:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=tf, limit=min(lookback, 1000))
                df = pd.DataFrame(ohlcv, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
                df["ts"] = pd.to_datetime(df["ts"], unit="ms")
                df = df.set_index("ts").tz_localize(None)
                return FetchResult(df, float(df["Close"].iloc[-1]), "ccxt")
            except Exception:
                pass

        if _HAS_YF:
            try:
                data = yf.Ticker(symbol).history(period="7d", interval="1m")
                data = data.rename(columns=str.title)
                return FetchResult(data[["Open", "High", "Low", "Close", "Volume"]],
                                   float(data["Close"].iloc[-1]), "yfinance")
            except Exception:
                pass

        return self._synthetic_series()

    def fetch_ticker_price(self, symbol):
        """取得最新價格，用於即時更新"""
        if self.is_crypto(symbol) and self.exchange:
            try:
                return float(self.exchange.fetch_ticker(symbol)["last"])
            except Exception:
                return None
        if _HAS_YF:
            try:
                info = yf.Ticker(symbol).history(period="1d", interval="1m")
                if len(info) > 0:
                    return float(info["Close"].iloc[-1])
            except Exception:
                return None
        return None
