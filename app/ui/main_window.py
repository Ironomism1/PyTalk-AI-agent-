from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout

from app.core.ai_client import GeminiClient
from app.core.state import AppState
from app.core.tts import TextToSpeech
from app.core.stt import SpeechToText
from app.ui.chat_sidebar import ChatSidebar
from app.ui.chat_view import ChatView
from app.ui.loading_screen import LoadingScreen
from app.ui.settings_modal import SettingsModal


class MainWindow(QMainWindow):
    def __init__(self, state: AppState, ai: GeminiClient, tts: TextToSpeech, stt: SpeechToText) -> None:
        super().__init__()
        self.setWindowTitle("PyTalk")
        self.resize(1200, 800)
        self.state = state
        self.ai = ai
        self.tts = tts
        self.stt = stt

        self.loading = LoadingScreen()
        self.setCentralWidget(self.loading)

        # Build main UI
        self._build_main()

    def _build_main(self) -> None:
        self.splitter = QSplitter()
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet("QSplitter::handle { background: rgba(6,182,212,0.2); }")

        self.sidebar = ChatSidebar(self.state, on_select=self._on_select_session)
        self.sidebar.setFixedWidth(260)
        self.chat = ChatView(self.state, self.ai, self.tts, self.stt)
        self.chat.set_sidebar_toggler(self._toggle_sidebar)
        self.chat.set_open_settings(self._open_settings)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.chat)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self._apply_sidebar_visibility()
        self._main_container = container

    def hide_loading_show_main(self) -> None:
        self.setCentralWidget(self._main_container)
        self.chat.refresh()

    def _on_select_session(self, session_id: str) -> None:
        self.chat.refresh()

    def _toggle_sidebar(self) -> None:
        self.state.settings.sidebar_visible = not self.state.settings.sidebar_visible
        self.state.save()
        self._apply_sidebar_visibility()

    def _apply_sidebar_visibility(self) -> None:
        if self.state.settings.sidebar_visible:
            self.sidebar.show()
            self.sidebar.setFixedWidth(260)
        else:
            self.sidebar.hide()
            self.sidebar.setFixedWidth(0)

    def _open_settings(self) -> None:
        dlg = SettingsModal(self.state, self)
        if dlg.exec():
            self.chat.refresh()


