"""
Centralized OpenAI API key loading.
Single source of truth - used by app.py, ai_brain, config, and health check.
"""

import os
from pathlib import Path
# Resolve paths once at module load (file is in backend/)
_BACKEND = Path(__file__).resolve().parent
_ROOT = _BACKEND.parent


def get_openai_key() -> str:
    """
    Get OpenAI API key from env, .env files, or manual parse.
    Tries multiple locations and returns empty string if not found.
    """
    # 1. Already in os.environ (from run.py or dotenv)
    key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if key and key.startswith("sk-"):
        return key

    # 2. Load via dotenv from known paths
    try:
        from dotenv import load_dotenv
        for p in [_ROOT / ".env", _BACKEND / ".env"]:
            if p.exists():
                load_dotenv(p, override=True)
                key = (os.environ.get("OPENAI_API_KEY") or "").strip()
                if key and key.startswith("sk-"):
                    return key
    except ImportError:
        pass

    # 3. Manual parse - try all possible .env locations
    cwd = Path.cwd()
    candidates = [
        _ROOT / ".env",
        _BACKEND / ".env",
        cwd / ".env",
        cwd / "backend" / ".env",
        cwd.parent / ".env",
        cwd.parent / "backend" / ".env",
    ]
    seen = set()
    for p in candidates:
        if not p or not p.exists() or str(p) in seen:
            continue
        seen.add(str(p))
        try:
            with open(p, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    s = line.strip()
                    if "OPENAI_API_KEY" in s and "=" in s and not s.startswith("#"):
                        parts = s.split("=", 1)
                        if parts[0].strip() == "OPENAI_API_KEY":
                            k = parts[1].split("#")[0].strip().strip('"\'')
                            if k and k.startswith("sk-"):
                                os.environ["OPENAI_API_KEY"] = k  # cache for next call
                                return k
        except Exception:
            pass
    return ""
