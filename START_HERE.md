# How to Run the AI Voice Agent

## First-Time Setup

**Step 1: Create `.env` file in the ROOT folder**

The `.env` file must be in the main project folder (`voice-agent/`), **NOT** in the `backend/` folder.

```
voice-agent/           ← .env goes HERE
├── .env              ← CREATE THIS FILE HERE
├── backend/
│   ├── app.py
│   └── ...
└── frontend/
```

**Step 2: Add your OpenAI API key**

Create or edit `.env` with:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Replace `sk-your-actual-api-key-here` with your real API key from [platform.openai.com](https://platform.openai.com/api-keys).

> Tip: Copy `.env.example` to `.env` and replace the placeholder key.

---

## Quick Start

1. **Open a terminal** (PowerShell or Command Prompt).

2. **Go to the project folder:**
   ```
   cd "C:\Users\Ghost\Downloads\ai voiuce agent\voice-agent"
   ```

3. **Run the app** (must use Python 3.12):
   ```
   py -3.12 run.py
   ```

4. **Open your browser** and go to: **http://localhost:5000**

---

## If It Doesn't Run

### "py is not recognized"
- Install Python 3.12 from [python.org](https://www.python.org/downloads/)
- Or use the full path: `C:\Users\Ghost\AppData\Local\Programs\Python\Python312\python.exe run.py`

### "No module named 'flask'" or similar
- Install dependencies first:
  ```
  cd backend
  py -3.12 -m pip install -r requirements.txt
  cd ..
  py -3.12 run.py
  ```

### "ModuleNotFoundError: aifc" or "aifc" error
- You're using Python 3.14. **Must use Python 3.12:**
  ```
  py -3.12 run.py
  ```

### "Port 5000 already in use" / Health shows "missing_keys: OPENAI_API_KEY"
- **Stop any old server first:** press `Ctrl+C` in the terminal where it's running.
- Start fresh with `py -3.12 run.py` from the `voice-agent` folder.
- You should see "API key loaded OK" when it starts correctly.
- If port is still in use, change `port=5000` to `port=5001` in `run.py`.

### Double-clicking run.bat closes immediately
- Open a terminal in the folder, run `py -3.12 run.py` manually to see the error message.
