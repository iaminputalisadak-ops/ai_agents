"""
Task Executor Module - Executes voice commands.
Handles: YouTube, apps, web search, weather, news.
"""

import os
import webbrowser
from typing import Optional

import requests

from config import Config


class TaskExecutor:
    """Executes various tasks based on user intent."""

    def __init__(self):
        """Initialize task executor with API keys."""
        self.weather_api_key = Config.OPENWEATHERMAP_API_KEY
        self.news_api_key = Config.NEWS_API_KEY

    def play_youtube(self, query: str) -> str:
        """
        Open YouTube search in browser.

        Args:
            query: Search query (song/video name)

        Returns:
            Status message
        """
        if not query or not query.strip():
            return "What would you like me to play?"
        encoded = requests.utils.quote(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Opening YouTube to search for {query.strip()}"

    def open_application(self, app_name: str) -> str:
        """
        Open a desktop application.

        Args:
            app_name: Application name (chrome, notepad, etc.)

        Returns:
            Status message
        """
        apps = {
            "chrome": "chrome",
            "google chrome": "chrome",
            "notepad": "notepad",
            "calculator": "calc",
            "calc": "calc",
            "explorer": "explorer",
            "file explorer": "explorer",
            "cmd": "cmd",
            "command prompt": "cmd",
            "powershell": "powershell",
        }
        app_key = app_name.lower().strip()
        if app_key not in apps:
            return f"I don't know how to open {app_name}. Try Chrome, Notepad, or Calculator."

        try:
            os.system(f"start {apps[app_key]}")
            return f"Opening {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    def web_search(self, query: str) -> str:
        """
        Open web search in browser.

        Args:
            query: Search query

        Returns:
            Status message
        """
        if not query or not query.strip():
            return "What would you like to search for?"
        encoded = requests.utils.quote(query.strip())
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Searching the web for {query.strip()}"

    def get_weather(self, location: Optional[str] = None) -> str:
        """
        Get weather for a location.

        Args:
            location: City name or zip (None = use default)

        Returns:
            Weather description or error message
        """
        if not self.weather_api_key or not str(self.weather_api_key).strip():
            return "Weather is optional. To enable it, get a free key at openweathermap.org and add OPENWEATHERMAP_API_KEY to your .env file."

        loc = (location or "London").strip()
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": loc, "appid": self.weather_api_key, "units": "metric"}
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"In {loc}, it's {temp:.0f} degrees Celsius with {desc}."
        except requests.RequestException as e:
            return f"Could not fetch weather: {str(e)}"

    def get_news(self, topic: Optional[str] = None, count: int = 5) -> str:
        """
        Get latest news headlines.

        Args:
            topic: Optional topic filter
            count: Number of headlines

        Returns:
            News summary or error message
        """
        if not self.news_api_key or not str(self.news_api_key).strip():
            return "News is optional. To enable it, get a free key at newsapi.org and add NEWS_API_KEY to your .env file."

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {"apiKey": self.news_api_key, "pageSize": count, "country": "us"}
            if topic and topic.strip():
                params["q"] = topic.strip()
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()
            articles = data.get("articles", [])
            if not articles:
                return "No news headlines found."
            lines = []
            for i, a in enumerate(articles[:count], 1):
                title = a.get("title", "").strip()
                if title and title != "[Removed]":
                    lines.append(f"{i}. {title}")
            return "Here are the latest headlines:\n" + "\n".join(lines)
        except requests.RequestException as e:
            return f"Could not fetch news: {str(e)}"

    def execute_intent(self, intent: str, query: str) -> Optional[str]:
        """
        Execute task based on detected intent.

        Args:
            intent: play_music, open_app, search, weather, news
            query: User query/parameters

        Returns:
            Result message or None if intent unknown
        """
        intent = intent.lower()
        if "play" in intent or "music" in intent or "youtube" in intent:
            return self.play_youtube(query)
        if "open" in intent or "launch" in intent or "app" in intent:
            return self.open_application(query)
        if "search" in intent or "google" in intent:
            return self.web_search(query)
        if "weather" in intent:
            return self.get_weather(query)
        if "news" in intent:
            return self.get_news(query)
        return None
