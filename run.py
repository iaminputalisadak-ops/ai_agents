#!/usr/bin/env python3
"""
Run the AI Voice Agent.
Execute from the voice-agent directory: python run.py
"""

import os
import sys
from pathlib import Path

# Load .env FIRST, before any app imports (project root and backend)
_root = Path(__file__).resolve().parent
for env_path in [_root / ".env", _root / "backend" / ".env"]:
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)

# Add backend to path
backend_dir = _root / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from app import app
from config import Config

if __name__ == "__main__":
    missing = Config.validate()
    if missing:
        print(f"Warning: Missing env vars: {', '.join(missing)}")
        print("Edit .env and add OPENAI_API_KEY for full functionality.")
    print("-" * 50)
    print("  AI Voice Agent - Starting server...")
    print("  Open: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("-" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
