# AI Voice Agent – Success Checklist

Use this checklist to verify your setup is complete and working.

---

## Setup

- [ ] **Python installed** — Use Python 3.12 (3.14 works but PyAudio is not supported)
- [ ] **Virtual environment created and activated**
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```
- [ ] **All dependencies installed (no errors)**
  ```powershell
  cd backend
  pip install -r requirements.txt
  ```
- [ ] **.env file created with OpenAI API key**
  ```powershell
  copy .env.example .env
  # Edit .env and add: OPENAI_API_KEY=sk-your-key
  ```
- [ ] **All Python files created in backend/**
  - `app.py`, `config.py`, `requirements.txt`
  - `modules/speech_recognition.py`, `ai_brain.py`, `text_to_speech.py`, `task_executor.py`
- [ ] **All frontend files created**
  - `frontend/index.html`, `style.css`, `script.js`

---

## Run & Test

- [ ] **Backend running on http://localhost:5000**
  ```powershell
  python run.py
  # or: py -3.12 run.py  (if using Python 3.12 for PyAudio)
  ```
- [ ] **Frontend opened in browser**
  - Go to http://localhost:5000
  - Use Chrome or Edge (for Web Speech API)
- [ ] **Microphone permissions granted**
  - Allow microphone access when the browser prompts
- [ ] **Test message sent and received**
  - Type a message and click Send, or click the mic and speak
  - AI response appears in chat and plays as voice

---

## Quick Start (All at once)

```powershell
cd "c:\Users\Ghost\Downloads\ai voiuce agent\voice-agent"
copy .env.example .env
# Add your OPENAI_API_KEY to .env
pip install -r backend\requirements.txt
python run.py
```

Then open **http://localhost:5000** in Chrome or Edge.
