import pandas as pd
import numpy as np

def ema(series: pd.Series, span: int):
    """指數移動平均"""
    return series.ewm(span=span, adjust=False).mean()

def rsi(close: pd.Series, period=14):
    """相對強弱指標 RSI"""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    return 100 - (100 / (1 + rs))

def macd(close, fast=12, slow=26, signal=9):
    """MACD 指標"""
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist
