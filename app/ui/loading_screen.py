from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Ring(QWidget):
    def __init__(self, color: QColor, thickness: int, parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self._thickness = thickness
        self.setMinimumSize(80, 80)
        self.setMaximumSize(80, 80)

    def paintEvent(self, e) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)
        pen = QPen(self._color)
        pen.setWidth(self._thickness)
        painter.setPen(pen)
        painter.drawEllipse(rect)


class LoadingScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("LoadingScreen")
        self.setStyleSheet("""
        #LoadingScreen {
          background-color: #0b1020;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container.setFixedSize(140, 140)
        layout.addWidget(container)

        self.outer = Ring(QColor("#22d3ee"), 4, container)
        self.middle = Ring(QColor("#d946ef"), 4, container)
        self.inner = Ring(QColor("#22d3ee"), 4, container)
        self.outer.move(30, 0)
        self.middle.move(15, 30)
        self.inner.move(45, 60)

        ai = QLabel("AI")
        f = QFont()
        f.setPointSize(24)
        f.setBold(True)
        ai.setFont(f)
        ai.setStyleSheet("color: #e2e8f0;")
        ai.setAlignment(Qt.AlignCenter)
        layout.addWidget(ai)

        self.text = QLabel("INITIALIZING AGENT...")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet("color: #94a3b8; letter-spacing: 6px;")
        layout.addWidget(self.text)

        # Simple animations to evoke spin/ping/pulse
        self._build_animations()

    def _build_animations(self) -> None:
        self.anim_outer = QPropertyAnimation(self.outer, b"geometry", self)
        self.anim_outer.setDuration(1600)
        self.anim_outer.setLoopCount(-1)
        self.anim_outer.setStartValue(QRect(30, 0, 80, 80))
        self.anim_outer.setEndValue(QRect(30, 0, 80, 80))
        self.anim_outer.start()

        self.anim_middle = QPropertyAnimation(self.middle, b"geometry", self)
        self.anim_middle.setDuration(900)
        self.anim_middle.setLoopCount(-1)
        self.anim_middle.setStartValue(QRect(15, 30, 80, 80))
        self.anim_middle.setEndValue(QRect(15, 30, 80, 80))
        self.anim_middle.start()

        self.anim_inner = QPropertyAnimation(self.inner, b"geometry", self)
        self.anim_inner.setDuration(1200)
        self.anim_inner.setLoopCount(-1)
        self.anim_inner.setStartValue(QRect(45, 60, 80, 80))
        self.anim_inner.setEndValue(QRect(45, 60, 80, 80))
        self.anim_inner.start()


