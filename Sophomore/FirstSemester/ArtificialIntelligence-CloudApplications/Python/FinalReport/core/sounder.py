import platform
import time

class Sounder:
    """跨平台提示音封裝"""
    def __init__(self):
        self.is_windows = (platform.system().lower() == "windows")
        if self.is_windows:
            try:
                import winsound
                self._winsound = __import__("winsound")
            except Exception:
                self.is_windows = False
        self._last_beep = 0.0
        self.cooldown_sec = 10.0

    def maybe_beep(self, condition: bool, freq=1000, dur_ms=200):
        now = time.time()
        if condition and (now - self._last_beep >= self.cooldown_sec):
            if self.is_windows:
                try:
                    self._winsound.Beep(freq, dur_ms)
                except Exception:
                    pass
            self._last_beep = now
