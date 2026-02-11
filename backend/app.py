"""
AI Voice Agent - Main Flask Application
REST API with speech recognition, AI processing, and text-to-speech.
"""

import base64
import os
import re
import sys
import threading
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config
from modules.speech_recognition import SpeechRecognizer
from modules.ai_brain import AIBrain
from modules.text_to_speech import TextToSpeech
from modules.task_executor import TaskExecutor


def _read_key_from_disk() -> str:
    """Read OPENAI_API_KEY from .env files - bulletproof parsing."""
    from dotenv import load_dotenv
    base = Path(__file__).resolve().parent  # backend/
    root = base.parent  # voice-agent/
    for p in [root / ".env", base / ".env"]:
        if p.exists():
            try:
                load_dotenv(p, override=True)
                k = (os.environ.get("OPENAI_API_KEY") or "").strip()
                if k and k.startswith("sk-"):
                    return k
                # Fallback: parse manually
                with open(p, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        s = line.strip()
                        if s.startswith("OPENAI_API_KEY=") and not s.startswith("#"):
                            key = s.split("=", 1)[1].split("#")[0].strip().strip('"\'')
                            if key and key.startswith("sk-"):
                                return key
            except Exception:
                pass
    return ""


def _get_openai_key():
    """Get OpenAI key from Config, env, or .env file directly."""
    key = (Config.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY") or "").strip()
    if key and key.startswith("sk-"):
        return key
    # Fallback: read .env file directly (try multiple possible locations)
    _backend = Path(__file__).resolve().parent
    _root = _backend.parent
    candidates = [
        _root / ".env",
        _backend / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8-sig", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if "OPENAI_API_KEY" in line and "=" in line and not line.startswith("#"):
                            parts = line.split("=", 1)
                            if len(parts) == 2 and parts[0].strip() == "OPENAI_API_KEY":
                                key = parts[1].split("#")[0].strip().strip('"\'')
                                if key and key.startswith("sk-"):
                                    return key
            except Exception:
                pass
    return ""


# Initialize Flask app - use absolute path for static folder reliability
_frontend = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__, static_folder=str(_frontend), static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load and store API key - set once at startup, use everywhere
_OPENAI_KEY = _get_openai_key() or _read_key_from_disk() or (os.environ.get("OPENAI_API_KEY") or "").strip()
app.config["OPENAI_API_KEY"] = _OPENAI_KEY

# Initialize modules
_openai_key = _OPENAI_KEY
speech_recognizer = SpeechRecognizer(energy_threshold=300, pause_threshold=0.8)
ai_brain = AIBrain(api_key=_openai_key, memory_limit=Config.CONVERSATION_MEMORY_LIMIT)
task_executor = TaskExecutor()

# TTS engine per-thread to avoid pyttsx3 thread issues
_tts_lock = threading.Lock()


def get_tts(rate: int = 175, volume: float = 1.0, voice_index=None) -> TextToSpeech:
    """Get a TTS instance with given settings."""
    with _tts_lock:
        tts = TextToSpeech(rate=rate, volume=volume, voice_index=voice_index)
        return tts


# =============================================================================
# API ENDPOINTS
# =============================================================================


@app.route("/")
def serve_frontend():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files (CSS, JS)."""
    return send_from_directory(app.static_folder, path)


@app.route("/api/listen", methods=["POST"])
def api_listen():
    """
    Capture voice input from audio data.
    Expects: multipart/form-data with 'audio' file or JSON with base64 'audio' string.
    """
    try:
        audio_data = None

        if request.is_json:
            data = request.get_json()
            audio_b64 = data.get("audio")
            if audio_b64:
                audio_data = base64.b64decode(audio_b64)
        elif "audio" in request.files:
            file = request.files["audio"]
            audio_data = file.read()

        if not audio_data:
            return jsonify({"success": False, "error": "No audio data provided"}), 400

        text = speech_recognizer.recognize_from_audio_file(audio_data)
        return jsonify({"success": True, "text": text or ""})

    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/process", methods=["POST"])
def api_process():
    """
    Process text with AI brain.
    Expects: JSON { "text": "user message" }
    """
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        response = ai_brain.process(text, use_wikipedia=True)
        return jsonify({"success": True, "response": response})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/speak", methods=["POST"])
def api_speak():
    """
    Convert text to speech and return audio.
    Expects: JSON { "text": "...", "rate": 175, "volume": 1.0, "voice_index": null }
    """
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        rate = int(data.get("rate", Config.DEFAULT_VOICE_SPEED))
        volume = float(data.get("volume", Config.DEFAULT_VOICE_VOLUME))
        voice_index = data.get("voice_index")
        if voice_index is not None and voice_index != "":
            try:
                voice_index = int(voice_index)
            except (ValueError, TypeError):
                voice_index = None

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        tts = get_tts(rate=rate, volume=volume, voice_index=voice_index)
        audio_bytes = tts.text_to_audio_bytes(text)

        if not audio_bytes:
            return jsonify({"success": False, "error": "Failed to generate audio"}), 500

        # Return as base64 for frontend playback
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return jsonify({"success": True, "audio": audio_b64, "format": "wav"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Combined endpoint: process text with AI and optionally return TTS audio.
    Expects: JSON { "text": "...", "speak": true, "rate": 175, "volume": 1.0 }
    """
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()
        speak = data.get("speak", True)
        rate = int(data.get("rate", Config.DEFAULT_VOICE_SPEED))
        volume = float(data.get("volume", Config.DEFAULT_VOICE_VOLUME))
        voice_index = data.get("voice_index")
        if voice_index is not None and voice_index != "":
            try:
                voice_index = int(voice_index)
            except (ValueError, TypeError):
                voice_index = None

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        # Check for task intents first (play, open, search, weather, news)
        response = None
        text_lower = text.lower()
        if re.search(r"\bplay\b", text_lower):
            q = re.sub(r"^.*?\bplay\s+(?:a|the|some)?\s*", "", text, flags=re.I).strip()
            response = task_executor.play_youtube(q or text)
        elif re.search(r"\b(?:open|launch)\s+", text_lower):
            q = re.sub(r"^.*?\b(?:open|launch)\s+", "", text_lower).strip()
            response = task_executor.open_application(q or "notepad")
        elif re.search(r"\b(?:search|google)\b", text_lower):
            q = re.sub(r"^.*?\b(?:search\s+for|search|google)\s+", "", text_lower).strip()
            response = task_executor.web_search(q or text)
        elif "weather" in text_lower:
            q = re.sub(r"^.*?weather\s+(?:in\s+)?|^.*?what'?s?\s+the\s+weather\s*(?:in\s+)?", "", text_lower).strip()
            response = task_executor.get_weather(q or None)
        elif re.search(r"\b(?:news|headlines)\b", text_lower):
            q = re.sub(r"^.*?\b(?:news|headlines)\s+(?:about\s+)?", "", text_lower).strip()
            response = task_executor.get_news(q or None)

        # Fall back to AI if no task matched - always pass key from module-level _OPENAI_KEY
        if response is None:
            api_key = _OPENAI_KEY or app.config.get("OPENAI_API_KEY") or _read_key_from_disk()
            response = ai_brain.process(text, use_wikipedia=True, api_key_override=api_key)

        # Optionally generate TTS
        audio_b64 = None
        if speak and response:
            tts = get_tts(rate=rate, volume=volume, voice_index=voice_index)
            audio_bytes = tts.text_to_audio_bytes(response)
            if audio_bytes:
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify({
            "success": True,
            "response": response,
            "audio": audio_b64,
            "format": "wav" if audio_b64 else None,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/task", methods=["POST"])
def api_task():
    """
    Execute a task (play music, open app, search, weather, news).
    Expects: JSON { "intent": "play_music|open_app|search|weather|news", "query": "..." }
    """
    try:
        data = request.get_json() or {}
        intent = data.get("intent", "")
        query = data.get("query", "")
        result = task_executor.execute_intent(intent, query)
        if result is None:
            return jsonify({"success": False, "error": "Unknown intent"}), 400
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear conversation memory."""
    try:
        ai_brain.clear_memory()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/voices", methods=["GET"])
def api_voices():
    """Get available TTS voices."""
    try:
        tts = get_tts()
        voices = tts.get_available_voices()
        return jsonify({"success": True, "voices": voices})
    except RuntimeError as e:
        return jsonify({"success": False, "error": str(e), "voices": []}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check and config validation."""
    missing = Config.validate()
    key_loaded = bool(app.config.get("OPENAI_API_KEY") or _get_openai_key() or _read_key_from_disk())
    return jsonify({
        "status": "ok" if not missing and key_loaded else "warning",
        "missing_keys": missing,
        "api_key_configured": key_loaded,
    })


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    missing = Config.validate()
    if missing:
        print(f"Warning: Missing env vars: {', '.join(missing)}")
        print("Edit .env and add OPENAI_API_KEY for full functionality.")
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_ENV == "development")
