from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def iso_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str
    images: List[str] = field(default_factory=list)  # file paths
    created_at: str = field(default_factory=iso_now)


@dataclass
class ChatSession:
    id: str
    title: str
    model_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=iso_now)
    updated_at: str = field(default_factory=iso_now)


@dataclass
class ModelInfo:
    name: str
    model_id: str


@dataclass
class Settings:
    system_instruction: str = "You are PyTalk, a helpful AI coding assistant."
    sidebar_visible: bool = True
    muted: bool = False
    current_model: str = "gemini-1.5-flash"
    models: List[ModelInfo] = field(default_factory=lambda: [
        ModelInfo(name="Gemini 1.5 Flash", model_id="gemini-1.5-flash"),
        ModelInfo(name="Gemini 1.5 Pro", model_id="gemini-1.5-pro"),
        ModelInfo(name="Flash Image", model_id="gemini-flash-image"),
    ])


class AppState:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_path = storage_dir / "pytalk.json"
        self.sessions: List[ChatSession] = []
        self.settings: Settings = Settings()
        self.active_session_id: Optional[str] = None

    # Persistence schema compatible with the spec keys
    def to_payload(self) -> Dict[str, Any]:
        return {
            "pytalk-sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "model_id": s.model_id,
                    "messages": [asdict(m) for m in s.messages],
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                } for s in self.sessions
            ],
            "pytalk-models": [asdict(m) for m in self.settings.models],
            "pytalk-current-model": self.settings.current_model,
            "pytalk-system-instruction": self.settings.system_instruction,
            "pytalk-sidebar-visible": self.settings.sidebar_visible,
            "pytalk-muted": self.settings.muted,
            "pytalk-active-session": self.active_session_id,
        }

    def from_payload(self, data: Dict[str, Any]) -> None:
        try:
            sessions_raw = data.get("pytalk-sessions", [])
            self.sessions = []
            for s in sessions_raw:
                msgs = [Message(**m) for m in s.get("messages", [])]
                self.sessions.append(ChatSession(
                    id=s["id"],
                    title=s.get("title", "New Chat"),
                    model_id=s.get("model_id", self.settings.current_model),
                    messages=msgs,
                    created_at=s.get("created_at", iso_now()),
                    updated_at=s.get("updated_at", iso_now()),
                ))
            models_raw = data.get("pytalk-models", [])
            if models_raw:
                self.settings.models = [ModelInfo(**m) for m in models_raw]
            self.settings.current_model = data.get("pytalk-current-model", self.settings.current_model)
            self.settings.system_instruction = data.get("pytalk-system-instruction", self.settings.system_instruction)
            self.settings.sidebar_visible = bool(data.get("pytalk-sidebar-visible", self.settings.sidebar_visible))
            self.settings.muted = bool(data.get("pytalk-muted", self.settings.muted))
            self.active_session_id = data.get("pytalk-active-session", None)
        except Exception:
            # Reset on corruption
            self.sessions = []
            self.settings = Settings()
            self.active_session_id = None

    def load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.from_payload(data)
        if not self.sessions:
            s = self.create_session(title="New Chat")
            self.active_session_id = s.id
            self.save()

    def save(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(self.to_payload(), f, ensure_ascii=False, indent=2)

    # Sessions
    def create_session(self, title: str, model_id: Optional[str] = None) -> ChatSession:
        sid = str(uuid.uuid4())
        session = ChatSession(
            id=sid,
            title=title,
            model_id=model_id or self.settings.current_model,
            messages=[],
        )
        self.sessions.insert(0, session)
        self.active_session_id = sid
        self.save()
        return session

    def rename_session(self, session_id: str, new_title: str) -> None:
        s = self.get_session(session_id)
        if not s:
            return
        s.title = new_title.strip() or s.title
        s.updated_at = iso_now()
        self.save()

    def delete_session(self, session_id: str) -> None:
        self.sessions = [s for s in self.sessions if s.id != session_id]
        if not self.sessions:
            s = self.create_session("New Chat")
            self.active_session_id = s.id
        else:
            if self.active_session_id == session_id:
                self.active_session_id = self.sessions[0].id
        self.save()

    def set_active_session(self, session_id: str) -> None:
        if self.get_session(session_id):
            self.active_session_id = session_id
            self.save()

    def get_session(self, session_id: Optional[str]) -> Optional[ChatSession]:
        if not session_id:
            return None
        for s in self.sessions:
            if s.id == session_id:
                return s
        return None

    def append_message(self, session_id: str, message: Message) -> None:
        s = self.get_session(session_id)
        if not s:
            return
        s.messages.append(message)
        s.updated_at = iso_now()
        self.save()

    # Models
    def add_model(self, name: str, model_id: str) -> None:
        model_id = model_id.strip()
        if not model_id:
            return
        self.settings.models = [m for m in self.settings.models if m.model_id != model_id]
        self.settings.models.append(ModelInfo(name=name.strip() or model_id, model_id=model_id))
        self.save()

    def remove_model(self, model_id: str) -> None:
        self.settings.models = [m for m in self.settings.models if m.model_id != model_id]
        if self.settings.current_model == model_id and self.settings.models:
            self.settings.current_model = self.settings.models[0].model_id
        self.save()


