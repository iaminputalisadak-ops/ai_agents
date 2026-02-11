"""
Speech Recognition Module - Converts speech/audio to text.
Handles ambient noise adjustment and microphone input.
"""

import io
from typing import Optional

import speech_recognition as sr


class SpeechRecognizer:
    """Handles speech-to-text conversion using SpeechRecognition library."""

    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        """
        Initialize the speech recognizer.

        Args:
            energy_threshold: Minimum audio energy to consider as speech (ambient noise adjustment)
            pause_threshold: Seconds of silence to consider end of phrase
        """
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.dynamic_energy_threshold = True

    def adjust_for_ambient_noise(self, source: sr.AudioSource, duration: float = 1.0) -> None:
        """
        Adjust recognizer for ambient noise in the environment.

        Args:
            source: Audio source (microphone or file)
            duration: Seconds to listen for ambient noise
        """
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        except Exception as e:
            print(f"Ambient noise adjustment failed: {e}")

    def recognize_from_audio_file(self, audio_data: bytes, language: str = "en-US") -> str:
        """
        Convert audio file bytes to text.

        Args:
            audio_data: Raw audio bytes (WAV format preferred)
            language: Language code for recognition

        Returns:
            Transcribed text or empty string on failure
        """
        try:
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                # Adjust for ambient noise in short recordings
                self.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio, language=language)
            return text.strip() if text else ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}")
        except Exception as e:
            raise RuntimeError(f"Speech recognition failed: {e}")

    def recognize_from_file_path(self, file_path: str, language: str = "en-US") -> str:
        """
        Convert audio from file path to text.

        Args:
            file_path: Path to WAV audio file
            language: Language code

        Returns:
            Transcribed text
        """
        try:
            with sr.AudioFile(file_path) as source:
                self.adjust_for_ambient_noise(source)
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}")

    def listen_from_microphone(self, timeout: int = 5, phrase_time_limit: Optional[int] = 10) -> str:
        """
        Listen from system microphone and return transcribed text.
        Requires PyAudio. Use recognize_from_audio_file for web/API flow.

        Args:
            timeout: Max seconds to wait for speech to start
            phrase_time_limit: Max seconds for a single phrase

        Returns:
            Transcribed text
        """
        try:
            import pyaudio  # noqa: F401 - optional, only for microphone
        except ImportError:
            raise RuntimeError("PyAudio not installed. Use recognize_from_audio_file or: pip install pyaudio")
        try:
            with sr.Microphone() as source:
                self.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            return self.recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}")
