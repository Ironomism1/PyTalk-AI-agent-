import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.core.state import AppState
from app.core.ai_client import GeminiClient
from app.core.tts import TextToSpeech
from app.core.stt import SpeechToText


def ensure_app_dirs() -> Path:
    base_dir = Path.home() / ".pytalk"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def main() -> None:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication(sys.argv)
    app.setApplicationName("PyTalk")
    app.setOrganizationName("PyTalk")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    base_dir = ensure_app_dirs()
    state = AppState(storage_dir=base_dir)
    state.load()

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    ai = GeminiClient(api_key=api_key)
    tts = TextToSpeech()
    stt = SpeechToText()

    window = MainWindow(state=state, ai=ai, tts=tts, stt=stt)
    window.show()

    # Initial loading splash timing for aesthetics
    QTimer.singleShot(600, window.hide_loading_show_main)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


