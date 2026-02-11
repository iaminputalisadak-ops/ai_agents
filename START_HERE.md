# How to Run the AI Voice Agent

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

### "Port 5000 already in use"
- Another instance is running. Close it or use a different port.
- In `run.py`, change `port=5000` to `port=5001`.

### Double-clicking run.bat closes immediately
- Open a terminal in the folder, run `py -3.12 run.py` manually to see the error message.
