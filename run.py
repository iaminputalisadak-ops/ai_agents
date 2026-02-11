#!/usr/bin/env python3
"""
Run the AI Voice Agent.
Execute from the voice-agent directory: python run.py
"""

import os
import sys
from pathlib import Path

# Load .env FIRST and force OPENAI_API_KEY into os.environ
_root = Path(__file__).resolve().parent
for env_path in [_root / ".env", _root / "backend" / ".env"]:
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        try:
            with open(env_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if s.startswith("OPENAI_API_KEY=") and not s.startswith("#"):
                        key = s.split("=", 1)[1].split("#")[0].strip().strip('"\'')
                        if key and key.startswith("sk-"):
                            os.environ["OPENAI_API_KEY"] = key
                            break
        except Exception:
            pass

# Add backend to path
backend_dir = _root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from app import app
from config import Config

if __name__ == "__main__":
    _key = (app.config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()
    if _key and _key.startswith("sk-"):
        print("API key loaded OK")
    else:
        print("WARNING: OPENAI_API_KEY not found - AI chat will not work")
        print("Check .env in voice-agent/ and voice-agent/backend/")

    missing = Config.validate()
    if missing:
        print(f"Warning: Missing env vars: {', '.join(missing)}")
    print("-" * 50)
    print("  AI Voice Agent - Starting server...")
    print("  Open: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("-" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
