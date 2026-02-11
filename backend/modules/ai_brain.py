"""
AI Brain Module - GPT-4 powered intelligent responses.
Handles conversation context, reasoning, and Wikipedia search.
"""

import os
from collections import deque
from typing import Optional

import wikipedia

from config import Config

# Use centralized key loader (backend/ is in sys.path from app)
from api_key import get_openai_key


class AIBrain:
    """ChatGPT-like AI with conversation memory and Wikipedia integration."""

    SYSTEM_PROMPT = """You are a helpful, friendly AI voice assistant similar to Alexa.
You respond concisely since your answers will be spoken aloud.
Keep responses brief (2-4 sentences typically) unless the user asks for detail.
You have access to conversation history and can reference previous messages.
Be natural and conversational. If you don't know something, say so honestly."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        memory_limit: int = 10,
    ):
        """
        Initialize the AI brain.

        Args:
            api_key: OpenAI API key (uses Config if not provided)
            model: OpenAI model to use
            memory_limit: Number of message exchanges to keep in context
        """
        self.api_key = (
            (api_key or "").strip()
            or (Config.OPENAI_API_KEY or "").strip()
            or (os.environ.get("OPENAI_API_KEY") or "").strip()
            or get_openai_key()
        )
        self.model = model or Config.OPENAI_MODEL
        self.memory_limit = memory_limit or Config.CONVERSATION_MEMORY_LIMIT
        self.conversation_history: deque = deque(maxlen=memory_limit * 2)

    def _search_wikipedia(self, query: str, sentences: int = 3) -> Optional[str]:
        """
        Search Wikipedia for relevant information.

        Args:
            query: Search query
            sentences: Number of sentences to return

        Returns:
            Summary text or None
        """
        try:
            wikipedia.set_lang("en")
            result = wikipedia.summary(query, sentences=sentences, auto_suggest=True)
            return result
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
            return None
        except Exception:
            return None

    def _build_messages(self, user_input: str, use_wikipedia: bool = False) -> list[dict]:
        """Build the message list for the API call."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add Wikipedia context if relevant (questions about facts/definitions)
        if use_wikipedia and any(
            w in user_input.lower()
            for w in ["what is", "who is", "define", "explain", "tell me about"]
        ):
            wiki_result = self._search_wikipedia(user_input)
            if wiki_result:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Relevant Wikipedia information (use to enhance your response):\n{wiki_result}",
                    }
                )

        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_input})

        return messages

    def _call_openai(self, api_key: str, messages: list[dict]) -> str:
        """Call OpenAI API using openai>=1.0 client."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def process(
        self,
        user_input: str,
        use_wikipedia: bool = True,
        stream: bool = False,
        api_key_override: Optional[str] = None,
    ) -> str:
        """
        Process user input and return AI response.

        Args:
            user_input: User's message
            use_wikipedia: Whether to augment with Wikipedia search
            stream: Whether to stream response (not used in current implementation)
            api_key_override: Optional API key passed at request time

        Returns:
            AI response text
        """
        api_key = (
            (api_key_override or "").strip()
            or (self.api_key or "").strip()
            or (os.environ.get("OPENAI_API_KEY") or "").strip()
            or get_openai_key()
        )
        if not api_key or not api_key.startswith("sk-"):
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in .env"

        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you please repeat?"

        try:
            messages = self._build_messages(user_input.strip(), use_wikipedia=use_wikipedia)

            assistant_message = self._call_openai(api_key, messages)

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return assistant_message

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "Error: Invalid OpenAI API key. Please check your .env configuration."
            return f"I encountered an error: {error_msg[:100]}"

    def clear_memory(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
