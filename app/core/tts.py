from __future__ import annotations

import threading
from typing import Optional

import pyttsx3


class TextToSpeech:
    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", 185)
        self._engine.setProperty("volume", 1.0)
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = False
        self._muted = False

    def set_muted(self, muted: bool) -> None:
        self._muted = muted
        if muted:
            self.stop()

    def is_muted(self) -> bool:
        return self._muted

    def speak(self, text: str) -> None:
        if self._muted or not text.strip():
            return
        def run() -> None:
            with self._lock:
                if self._stop_flag:
                    return
                self._engine.say(text)
                self._engine.runAndWait()
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._stop_flag = True
            try:
                self._engine.stop()
            except Exception:
                pass
            self._stop_flag = False


