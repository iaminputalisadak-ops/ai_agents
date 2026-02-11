# API Keys Guide – What You Need

## Required (only 1)

| Key | Where to get | Needed for |
|-----|--------------|------------|
| **OPENAI_API_KEY** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | AI chat, answers, reasoning |

Add this to `.env` – the app won’t give AI replies without it.

---

## Optional (extra features)

| Key | Where to get | Needed for |
|-----|--------------|------------|
| **OPENWEATHERMAP_API_KEY** | [openweathermap.org/api](https://openweathermap.org/api) | "What's the weather in [city]?" |
| **NEWS_API_KEY** | [newsapi.org](https://newsapi.org) | "Read the news" |

These are optional. If you don’t add them, those features will show a short message instead of an error.

---

## Summary

You only need **OPENAI_API_KEY** for the main AI chat. Weather and news keys are optional.
