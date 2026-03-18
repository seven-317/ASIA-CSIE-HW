# core/__init__.py
"""
core package
AI 智慧交易視覺系統的核心模組
包含資料抓取、預測、技術指標、音效提示與共用工具。
"""

# --- 模組導入 ---
from .data_fetcher import DataFetcher, FetchResult
from .predictor import Predictor
from .indicators import rsi, macd, ema
from .sounder import Sounder
from .utils import tf_tier, REFRESH_BY_TIER, TIMEFRAME_CHOICES

# --- 匯出介面 ---
__all__ = [
    "DataFetcher",
    "FetchResult",
    "Predictor",
    "rsi",
    "macd",
    "ema",
    "Sounder",
    "tf_tier",
    "REFRESH_BY_TIER",
    "TIMEFRAME_CHOICES"
]
