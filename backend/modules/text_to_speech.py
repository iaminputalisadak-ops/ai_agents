"""
Text-to-Speech Module - Converts text to speech audio.
Uses pyttsx3 with adjustable speed, volume, and voice options.
"""

import tempfile
from typing import Optional

import pyttsx3


class TextToSpeech:
    """Handles text-to-speech conversion using pyttsx3."""

    def __init__(
        self,
        rate: int = 175,
        volume: float = 1.0,
        voice_index: Optional[int] = None,
    ):
        """
        Initialize TTS engine.

        Args:
            rate: Words per minute (default 175)
            volume: Volume 0.0 to 1.0
            voice_index: Index of voice to use (None = default)
        """
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            raise RuntimeError(
                f"TTS failed to initialize: {e}. "
                "On Windows, ensure SAPI voices are available."
            )
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", min(1.0, max(0.0, volume)))
        if voice_index is not None:
            try:
                voice_index = int(voice_index)
            except (ValueError, TypeError):
                voice_index = None
            if voice_index is not None:
                voices = self.engine.getProperty("voices")
                if 0 <= voice_index < len(voices):
                    self.engine.setProperty("voice", voices[voice_index].id)

    def set_rate(self, rate: int) -> None:
        """Set speech rate (words per minute)."""
        self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self.engine.setProperty("volume", min(1.0, max(0.0, volume)))

    def set_voice(self, voice_index: int) -> None:
        """Set voice by index (0=first, 1=second, etc.)."""
        voices = self.engine.getProperty("voices")
        if 0 <= voice_index < len(voices):
            self.engine.setProperty("voice", voices[voice_index].id)

    def get_available_voices(self) -> list[dict]:
        """Get list of available voices with id, name, and index."""
        voices = self.engine.getProperty("voices")
        return [
            {"id": v.id, "name": v.name, "index": i}
            for i, v in enumerate(voices)
        ]

    def text_to_audio_bytes(self, text: str) -> bytes:
        """
        Convert text to audio and return as WAV bytes.

        Args:
            text: Text to speak

        Returns:
            WAV audio bytes
        """
        if not text or not text.strip():
            return b""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()

            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            import os

            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def speak(self, text: str) -> None:
        """
        Speak text through system speakers (blocking).
        Used when running locally with microphone.

        Args:
            text: Text to speak
        """
        if text and text.strip():
            self.engine.say(text)
            self.engine.runAndWait()

    def stop(self) -> None:
        """Stop current speech output."""
        self.engine.stop()
