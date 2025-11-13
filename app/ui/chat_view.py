from __future__ import annotations

import base64
from io import BytesIO
from typing import List, Optional

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.ai_client import GeminiClient
from app.core.markdown_renderer import render_markdown
from app.core.state import AppState, ChatSession, Message
from app.core.tts import TextToSpeech
from app.core.stt import SpeechToText


class ChatView(QWidget):
    def __init__(self, state: AppState, ai: GeminiClient, tts: TextToSpeech, stt: SpeechToText, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.ai = ai
        self.tts = tts
        self.stt = stt
        self.attached_image_path: Optional[str] = None

        self.setObjectName("ChatView")
        self.setStyleSheet("""
        #ChatView {
          background-color: #0b1020;
        }
        QLabel, QComboBox, QTextEdit {
          color: #e5e7eb;
          font-family: 'Segoe UI', Roboto, Inter, sans-serif;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background-color: rgba(11,16,32,0.8); border-bottom: 1px solid rgba(6,182,212,0.3);")
        h = QHBoxLayout(header)
        h.setContentsMargins(8, 6, 8, 6)
        self.btn_sidebar = QPushButton("☰")
        self.btn_sidebar.setFixedWidth(36)
        h.addWidget(self.btn_sidebar, 0)
        self.title = QLabel("")
        self.title.setStyleSheet("color:#22d3ee;")
        h.addWidget(self.title, 1)
        self.model = QComboBox()
        self._refresh_models()
        self.model.currentIndexChanged.connect(self._on_model_changed)
        h.addWidget(self.model, 0)
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.clicked.connect(self._toggle_mute)
        h.addWidget(self.btn_mute, 0)
        self.btn_settings = QPushButton("⚙")
        h.addWidget(self.btn_settings, 0)
        layout.addWidget(header, 0)

        # Message area
        self.web = QTextBrowser()
        self.web.setOpenExternalLinks(True)
        self.web.setOpenLinks(False)
        self.web.anchorClicked.connect(self._handle_anchor_clicked)
        self.web.setStyleSheet("background-color:#0b1020; border:none;")
        layout.addWidget(self.web, 1)

        # Speaking indicator
        self.speaking = QLabel("")
        self.speaking.setAlignment(Qt.AlignCenter)
        self.speaking.setStyleSheet("""
        color:#22d3ee;
        padding:4px 10px;
        """)
        layout.addWidget(self.speaking, 0)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background-color: rgba(11,16,32,0.8); border-top: 1px solid rgba(6,182,212,0.3);")
        f = QHBoxLayout(footer)
        f.setContentsMargins(8, 8, 8, 8)
        self.btn_attach = QPushButton("📎")
        self.btn_attach.clicked.connect(self._attach_image)
        f.addWidget(self.btn_attach, 0)
        self.input = QTextEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.setFixedHeight(68)
        f.addWidget(self.input, 1)
        self.btn_mic = QPushButton("🎤")
        self.btn_mic.clicked.connect(self._toggle_mic)
        f.addWidget(self.btn_mic, 0)
        self.btn_image = QPushButton("✨")
        self.btn_image.clicked.connect(self._generate_image_from_text)
        f.addWidget(self.btn_image, 0)
        self.btn_send = QPushButton("➤")
        self.btn_send.clicked.connect(self._send)
        f.addWidget(self.btn_send, 0)
        layout.addWidget(footer, 0)

        self.refresh()

    # External hooks
    def set_sidebar_toggler(self, cb) -> None:
        self.btn_sidebar.clicked.connect(cb)

    def set_open_settings(self, cb) -> None:
        self.btn_settings.clicked.connect(cb)

    # Rendering
    def refresh(self) -> None:
        s = self.state.get_session(self.state.active_session_id)
        if not s:
            return
        self.title.setText(s.title)
        html_parts: List[str] = []
        for msg in s.messages:
            bubble_color = "#4f46e5" if msg.role == "user" else "#374151"
            text_color = "#ffffff" if msg.role == "user" else "#e5e7eb"
            rnd = render_markdown(msg.content)
            # Extract body content from rendered HTML
            idx = rnd.find("<body>")
            body = rnd[idx + 6:] if idx != -1 else rnd
            idx2 = body.rfind("</body>")
            if idx2 != -1:
                body = body[:idx2]
            images_html = ""
            for img_path in msg.images:
                try:
                    with open(img_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")
                    images_html += f'<img src="data:image/*;base64,{b64}" />'
                except Exception:
                    pass
            html_parts.append(f"""
            <div style="max-width: 72%; margin: 8px; padding: 10px 12px; border-radius: 12px; background:{bubble_color}; color:{text_color}; {'margin-left:auto;' if msg.role=='user' else 'margin-right:auto;'}">
              {images_html}
              {body}
            </div>
            """)
        self.web.setHtml(f"<!DOCTYPE html><html><body style='background:#0b1020;'>{''.join(html_parts)}</body></html>")

        # Input state
        if self.stt.is_listening():
            self.input.setPlaceholderText("Listening...")
        else:
            self.input.setPlaceholderText("Type a message...")
        self._update_speaking_indicator()
        self._update_mute_icon()

    def _refresh_models(self) -> None:
        self.model.clear()
        for m in self.state.settings.models:
            self.model.addItem(m.name, m.model_id)
        # Set current
        idx = 0
        for i in range(self.model.count()):
            if self.model.itemData(i) == self.state.settings.current_model:
                idx = i
                break
        self.model.setCurrentIndex(idx)

    # Actions
    def _on_model_changed(self) -> None:
        mid = self.model.currentData()
        self.state.settings.current_model = mid
        self.state.save()

    def _toggle_mute(self) -> None:
        new_state = not self.state.settings.muted
        self.state.settings.muted = new_state
        self.tts.set_muted(new_state)
        self.state.save()
        self._update_mute_icon()
        self._update_speaking_indicator()

    def _update_mute_icon(self) -> None:
        self.btn_mute.setText("🔇" if self.state.settings.muted else "🔊")

    def _update_speaking_indicator(self) -> None:
        self.speaking.setText("🔊 Speaking..." if not self.state.settings.muted else "")

    def _handle_anchor_clicked(self, url) -> None:
        if url.scheme() == "copy":
            try:
                data = base64.b64decode(url.path().lstrip("/"))
                text = data.decode("utf-8")
                QGuiApplication.clipboard().setText(text)
            except Exception:
                pass
        else:
            self.web.setSource(url)

    def _attach_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Attach Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not path:
            return
        self.attached_image_path = path

    def _toggle_mic(self) -> None:
        if self.stt.is_listening():
            self.stt.stop()
            self.refresh()
            return

        def on_text(text: str) -> None:
            current = self.input.toPlainText()
            new_text = (current + " " + text).strip()
            self.input.setPlainText(new_text)
            self.refresh()
        self.stt.listen(on_text=on_text)
        self.refresh()

    def _generate_image_from_text(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        img_bytes = self.ai.generate_image(prompt=text, model_id="gemini-flash-image")
        if not img_bytes:
            return
        # Save to temp file under storage dir
        out_path = str(self.state.storage_dir / f"gen_{abs(hash(text))}.png")
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        # Add as assistant message with image
        s = self.state.get_session(self.state.active_session_id)
        if not s:
            return
        self.state.append_message(s.id, Message(role="assistant", content="Generated image for your prompt.", images=[out_path]))
        self.refresh()

    def _send(self) -> None:
        s = self.state.get_session(self.state.active_session_id)
        if not s:
            return
        text = self.input.toPlainText().strip()
        if not text and not self.attached_image_path:
            return

        # Title update (asynchronous feel kept simple)
        if s.title == "New Chat" and text:
            try:
                new_title = self.ai.summarize_title(text)
                if new_title:
                    self.state.rename_session(s.id, new_title)
            except Exception:
                pass

        # Append user message
        images = [self.attached_image_path] if self.attached_image_path else []
        self.state.append_message(s.id, Message(role="user", content=text or "(attached image)", images=images))
        self.input.clear()
        self.attached_image_path = None
        self.refresh()

        # Prepare messages for Gemini
        parts: List[dict] = []
        if images:
            # one image multimodal
            parts.append({"text": text or ""})
            # inline image handled by ai client ._attachment_from_path in chat method via messages
            # but the SDK expects structured content; we pass text+image parts per message
        else:
            parts.append({"text": text})

        # Build history
        history = []
        for m in s.messages:
            role = "user" if m.role == "user" else "model"
            p = []
            if m.content:
                p.append({"text": m.content})
            for img in m.images:
                # each image as inline_data
                p.append(self.ai._attachment_from_path(img))
            history.append({"role": role, "parts": p})

        try:
            reply = self.ai.chat(
                model_id=self.state.settings.current_model,
                messages=history,
                system_instruction=self.state.settings.system_instruction,
            )
        except Exception as e:
            reply = f"Error: {e}"

        self.state.append_message(s.id, Message(role="assistant", content=reply))
        if not self.state.settings.muted:
            self.tts.speak(reply)
        self.refresh()


