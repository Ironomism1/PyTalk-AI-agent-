from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.state import AppState, ChatSession


class ChatSidebar(QWidget):
    def __init__(self, state: AppState, on_select: Callable[[str], None]) -> None:
        super().__init__()
        self.state = state
        self.on_select = on_select
        self.setObjectName("ChatSidebar")
        self.setStyleSheet("""
        #ChatSidebar {
          background-color: rgba(31, 41, 55, 0.5);
          border-right: 1px solid rgba(6,182,212,0.2);
        }
        QPushButton#newChat {
          background-color: #0891b2;
          color: white;
          padding: 10px;
          border-radius: 8px;
          margin: 8px;
        }
        QListWidget {
          border: none;
          color: #d1d5db;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.btn_new = QPushButton("＋ New Chat")
        self.btn_new.setObjectName("newChat")
        self.btn_new.clicked.connect(self.new_chat)
        layout.addWidget(self.btn_new)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemSelectionChanged.connect(self._on_selection_changed)
        self.list.itemDoubleClicked.connect(self._rename_selected)
        layout.addWidget(self.list, 1)

        self._context_menu()
        self.refresh()

    def _context_menu(self) -> None:
        self.list.setContextMenuPolicy(Qt.ActionsContextMenu)
        act_rename = QAction("Rename", self)
        act_rename.triggered.connect(self._rename_selected)
        act_delete = QAction("Delete", self)
        act_delete.triggered.connect(self._delete_selected)
        self.list.addAction(act_rename)
        self.list.addAction(act_delete)

    def refresh(self) -> None:
        self.list.clear()
        for s in self.state.sessions:
            item = QListWidgetItem(s.title)
            item.setData(Qt.UserRole, s.id)
            self.list.addItem(item)
            if s.id == self.state.active_session_id:
                item.setSelected(True)

    def new_chat(self) -> None:
        s = self.state.create_session("New Chat")
        self.refresh()
        self.on_select(s.id)

    def _on_selection_changed(self) -> None:
        items = self.list.selectedItems()
        if not items:
            return
        sid = items[0].data(Qt.UserRole)
        self.state.set_active_session(sid)
        self.on_select(sid)

    def _selected_session_id(self) -> Optional[str]:
        items = self.list.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.UserRole)

    def _rename_selected(self) -> None:
        sid = self._selected_session_id()
        if not sid:
            return
        current = self.state.get_session(sid)
        if not current:
            return
        text, ok = QInputDialog.getText(self, "Rename Chat", "Title:", text=current.title)
        if ok and text.strip():
            self.state.rename_session(sid, text.strip())
            self.refresh()

    def _delete_selected(self) -> None:
        sid = self._selected_session_id()
        if not sid:
            return
        self.state.delete_session(sid)
        self.refresh()
        if self.state.active_session_id:
            self.on_select(self.state.active_session_id)


