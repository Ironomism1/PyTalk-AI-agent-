<div align="center">

# PyTalk – Your own custom Ai Agent

Glow-infused AI assistant for coding & conversation.  
Chats, speaks, listens, and paints with Google Gemini — all inside a sleek PySide6 desktop app.

</div>

---

## ✨ Highlights

- **Immersive UI** – Dark neon aesthetic, animated splash screen, collapsible history sidebar.
- **Multi-session Memory** – Create, rename, delete, and resume chats. Everything persists locally.
- **Gemini Everywhere** – Pick built-in models or add your own IDs. One-click image generation included.
- **Voice In / Voice Out** – Dictate prompts with SpeechRecognition, hear replies via offline TTS (pyttsx3).
- **Markdown Pro** – Syntax-highlighted responses with copy-friendly code blocks and inline images.
- **Custom System Persona** – Craft PyTalk’s role & tone with a persisted system prompt.

---

## 🧰 Requirements

| Component | Details |
|-----------|---------|
| Python    | 3.10 – 3.12 (Conda 3.11 recommended) |
| API Key   | Google Generative AI (`YOUR_AI_API_KEY`) |
| Audio     | `PyAudio` (Windows) or `sounddevice` (macOS/Linux) |
| Extras    | Microphone for STT, speakers for TTS (optional) |

> ⚠️ On Windows, installing `PyAudio` may require Microsoft C++ Build Tools. Using `conda install -c conda-forge pyaudio` usually solves it.

---

## 🚀 Quick Start

### Option 1 – Conda (recommended on Windows)
```cmd
conda create -n pytalk python=3.11 -y
conda activate pytalk
conda install -c conda-forge pyaudio -y  # skip if mic not needed
pip install -r requirements.txt
set GOOGLE_API_KEY=YOUR_API_KEY
python -m app.main
```

### Option 2 – Virtualenv (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:API_KEY="YOUR_API_KEY"
python -m app.main
```

> Tip: add `setx Your_API_KEY "YOUR_API_KEY"` to persist the key across shell sessions (open a new shell afterwards).

---

## 🖥️ Using PyTalk

- **Sidebar** → All chats. Hover to rename/delete. `New Chat` starts a fresh session.
- **Header controls** → Toggle sidebar, pick model, mute/unmute TTS, open Settings.
- **Messages** → Assistant replies render markdown with code copy buttons and inline images.
- **Input bar** → Attach images, toggle mic, request image generation, or send messages.
- **Settings modal** → Update system prompt, manage models, tweak persona.
- **Persistence** → Stored at `~/.pytalk/pytalk.json` (Windows: `C:\Users\<you>\.pytalk\pytalk.json`). Delete it to reset.

---

## 🗂️ Persistence Schema

```jsonc
{
  "pytalk-sessions": [
    {
      "id": "...",
      "title": "My Chat",
      "model_id": "gemini-1.5-pro",
      "messages": [
        { "role": "user", "content": "Hello", "images": [], "created_at": "..." }
      ]
    }
  ],
  "pytalk-models": [{ "name": "Gemini 1.5 Pro", "model_id": "gemini-1.5-pro" }],
  "pytalk-current-model": "gemini-1.5-pro",
  "pytalk-system-instruction": "You are PyTalk...",
  "pytalk-sidebar-visible": true,
  "pytalk-muted": false,
  "pytalk-active-session": "session-id"
}
```

---

## 🧠 Architecture

- `app/main.py` – Application entry, wiring state + services into the main window.
- `app/core/state.py` – JSON-backed persistence, session/model/settings management.
- `app/core/ai_client.py` – Gemini wrapper for chat, image generation, and title summaries.
- `app/core/tts.py` & `app/core/stt.py` – Text-to-speech (pyttsx3) and speech-to-text (speech_recognition).
- `app/core/markdown_renderer.py` – Markdown → HTML with Pygments code highlighting & copy links.
- `app/ui/*` – PySide6 UI widgets: loading screen, sidebar, chat view, settings modal, main window.

---

## 🧪 Verification Checklist

- [ ] API key set in environment (`print(os.getenv("GOOGLE_API_KEY"))` to confirm)
- [ ] Microphone/voice features tested (optional)
- [ ] Image generation works with `gemini-flash-image`
- [ ] Sessions persist after restart (`~/.pytalk/pytalk.json` grows)
- [ ] TTS mute toggle updates instantly

---

## 📦 Deploy to GitHub

```bash
git init
git remote add origin https://github.com/<your-username>/PyTalk-AI-agent-.git
git add .
git commit -m "Initial PyTalk release"
git push -u origin main
```

Then add a summary screenshot and fill out the GitHub repository description with:
> Futuristic Gemini-powered desktop copilot · PySide6 UI · Markdown, voice, image generation, multi-session persistence

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: PySide6` | Ensure you’re inside `conda activate pytalk` (or your venv) **before** installing requirements. |
| `PyAudio` install fails | `conda install -c conda-forge portaudio pyaudio`, or remove voice features temporarily. |
| UI launches but Gemini errors | Verify `GOOGLE_API_KEY` is set and valid. |
| Old sessions cause crashes | Delete `~/.pytalk/pytalk.json` and relaunch. |

---

## ❤️ Credits

Crafted with PySide6, Pygments, SpeechRecognition, pyttsx3, Pillow,.  
Inspired by sci-fi interfaces and powered by the Gemini family.

Enjoy building with PyTalk! 🚀
