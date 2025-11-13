from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import google.generativeai as genai


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)

    def is_ready(self) -> bool:
        return bool(self.api_key)

    def _attachment_from_path(self, path: str) -> Dict[str, Any]:
        mime = "image/png"
        if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"):
            mime = "image/jpeg"
        if path.lower().endswith(".webp"):
            mime = "image/webp"
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return {"inline_data": {"mime_type": mime, "data": data}}

    def chat(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
    ) -> str:
        if not self.is_ready():
            return "Error: GOOGLE_API_KEY not set."
        model = genai.GenerativeModel(model_id, system_instruction=system_instruction or "")
        # messages: [{"role":"user|model","parts":[...]}]
        res = model.generate_content(messages)
        return res.text or ""

    def generate_image(self, prompt: str, model_id: str = "gemini-flash-image") -> Optional[bytes]:
        if not self.is_ready():
            return None
        model = genai.GenerativeModel(model_id)
        res = model.generate_content(
            [prompt],
            request_options={"timeout": 120},
            generation_config={"response_mime_type": "image/png"},
        )
        # SDK returns an image part; support both bytes and base64 paths
        for part in res._result.candidates[0].content.parts:
            if getattr(part, "inline_data", None):
                return base64.b64decode(part.inline_data.data)
        return None

    def summarize_title(self, text: str, model_id: str = "gemini-1.5-flash") -> str:
        if not self.is_ready():
            return "New Chat"
        model = genai.GenerativeModel(model_id)
        prompt = f"Summarize this prompt into a short, 3-5 word title: {text}"
        res = model.generate_content([prompt])
        return (res.text or "New Chat").strip().strip('"')


