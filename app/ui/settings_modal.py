from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.state import AppState, ModelInfo


class SettingsModal(QDialog):
    def __init__(self, state: AppState, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(560, 520)
        self.setStyleSheet("""
        QDialog {
          background-color: rgba(31,41,55,0.5);
          border: 1px solid rgba(6,182,212,0.3);
        }
        QLabel, QListWidget, QLineEdit, QTextEdit {
          color: #e5e7eb;
          font-family: 'Segoe UI', Roboto, Inter, sans-serif;
        }
        """)

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("color:#22d3ee; font-size:18px;")
        header.addWidget(title, 1)
        layout.addLayout(header)

        # System prompt
        layout.addWidget(QLabel("Custom System Prompt:"))
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("Define PyTalk's personality and role...")
        self.prompt.setPlainText(self.state.settings.system_instruction)
        self.prompt.setMinimumHeight(140)
        layout.addWidget(self.prompt)

        # Models
        layout.addWidget(QLabel("Manage Models:"))
        self.model_list = QListWidget()
        for m in self.state.settings.models:
            item = QListWidgetItem(f"{m.name}  ({m.model_id})")
            item.setData(Qt.UserRole, m.model_id)
            self.model_list.addItem(item)
        layout.addWidget(self.model_list, 1)

        btn_del = QPushButton("Delete Selected Model")
        btn_del.clicked.connect(self._delete_model)
        layout.addWidget(btn_del)

        layout.addWidget(QLabel("Add New Model:"))
        form = QFormLayout()
        self.model_name = QLineEdit()
        self.model_id = QLineEdit()
        form.addRow("Model Name", self.model_name)
        form.addRow("Model ID", self.model_id)
        layout.addLayout(form)
        btn_add = QPushButton("＋ Add Model")
        btn_add.clicked.connect(self._add_model)
        layout.addWidget(btn_add)

        buttons = QDialogButtonBox(QDialogButtonBox.Close | QDialogButtonBox.Save)
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _delete_model(self) -> None:
        items = self.model_list.selectedItems()
        if not items:
            return
        mid = items[0].data(Qt.UserRole)
        self.state.remove_model(mid)
        self._refresh_models()

    def _add_model(self) -> None:
        name = self.model_name.text().strip()
        mid = self.model_id.text().strip()
        if not mid:
            return
        self.state.add_model(name or mid, mid)
        self.model_name.clear()
        self.model_id.clear()
        self._refresh_models()

    def _refresh_models(self) -> None:
        self.model_list.clear()
        for m in self.state.settings.models:
            item = QListWidgetItem(f"{m.name}  ({m.model_id})")
            item.setData(Qt.UserRole, m.model_id)
            self.model_list.addItem(item)

    def _save_and_close(self) -> None:
        self.state.settings.system_instruction = self.prompt.toPlainText().strip()
        self.state.save()
        self.accept()


