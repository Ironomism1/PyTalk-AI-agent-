from __future__ import annotations

import threading
from typing import Callable, Optional

import speech_recognition as sr


class SpeechToText:
    def __init__(self) -> None:
        self._recognizer = sr.Recognizer()
        self._listening = False
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = False

    def is_listening(self) -> bool:
        return self._listening

    def listen(self, on_text: Callable[[str], None], phrase_time_limit: int = 8) -> None:
        if self._listening:
            return
        self._listening = True

        def run() -> None:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                try:
                    audio = self._recognizer.listen(source, phrase_time_limit=phrase_time_limit)
                except Exception:
                    self._listening = False
                    return
            try:
                if self._stop_flag:
                    self._listening = False
                    return
                text = self._recognizer.recognize_google(audio)
                on_text(text)
            except Exception:
                # ignore recognition errors
                pass
            finally:
                self._listening = False

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_flag = True
        self._listening = False


