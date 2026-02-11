"""
Configuration management for AI Voice Agent.
Loads environment variables and provides app settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root, then backend (override=True ensures .env wins over existing env)
_root = Path(__file__).resolve().parent.parent
for p in [_root / ".env", _root / "backend" / ".env", Path.cwd() / ".env"]:
    if p.exists():
        load_dotenv(p, override=True)


class Config:
    """Application configuration from environment variables."""

    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # OpenAI API (strip whitespace - .env can have trailing space)
    OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    # Speech settings
    DEFAULT_VOICE_SPEED = int(os.getenv("DEFAULT_VOICE_SPEED", "175"))
    DEFAULT_VOICE_VOLUME = float(os.getenv("DEFAULT_VOICE_VOLUME", "1.0"))

    # Conversation memory (number of exchanges to keep)
    CONVERSATION_MEMORY_LIMIT = int(os.getenv("CONVERSATION_MEMORY_LIMIT", "10"))

    # API Keys for external services (optional)
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required config and return list of missing keys."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing
