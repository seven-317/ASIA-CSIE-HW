TIMEFRAME_CHOICES = [
    "1s", "5s", "10s", "30s",
    "1m", "5m", "10m", "15m", "30m",
    "1h", "2h", "3h", "4h", "5h",
    "1d", "1w"
]

REFRESH_BY_TIER = {
    "sec": 1000,     # 1 秒刷新
    "min": 10_000,   # 10 秒刷新
    "hour": 60_000   # 60 秒刷新
}

def tf_tier(tf: str):
    """判斷 timeframe 所屬層級（秒 / 分 / 時）"""
    if tf.endswith("s"): return "sec"
    if tf.endswith("m"): return "min"
    return "hour"
