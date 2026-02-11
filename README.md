# AI Voice Agent

An intelligent voice assistant similar to Alexa, built with Flask and a modern purple gradient UI. Supports speech-to-text, GPT-4 reasoning, Wikipedia search, text-to-speech, and task execution (YouTube, apps, weather, news).

---

## Features

- **Speech Recognition**: Web Speech API (browser) + SpeechRecognition backend for audio
- **AI Brain**: OpenAI GPT-4 with conversation memory and Wikipedia integration
- **Text-to-Speech**: pyttsx3 with adjustable speed, volume, and voice
- **Task Execution**: Play YouTube, open apps (Chrome, Notepad, etc.), web search, weather, news
- **Modern UI**: Purple gradient theme, animated voice visualizer, chat display, settings panel

---

## Project Structure

```
voice-agent/
├── backend/
│   ├── app.py           # Flask app & REST API
│   ├── config.py        # Environment config
│   ├── requirements.txt
│   └── modules/
│       ├── speech_recognition.py
│       ├── ai_brain.py
│       ├── text_to_speech.py
│       └── task_executor.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .env                 # Your secrets (create from .env.example)
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone / Navigate to Project

```bash
cd voice-agent
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**PyAudio is optional** – only needed for server-side microphone. The app uses Web Speech API in the browser by default. If you need PyAudio and it fails on Windows:

```bash
python -m pip install pipwin
python -m pipwin install pyaudio
```

### 4. Environment Variables

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` and set:

- `OPENAI_API_KEY` **(required)** – Get from [OpenAI](https://platform.openai.com/api-keys)
- `OPENWEATHERMAP_API_KEY` (optional) – For weather
- `NEWS_API_KEY` (optional) – For news

### 5. Run the Application

**Double-click** `run.bat` (Windows) or run:

```bash
python run.py
```

**Or from backend directory:**
```bash
cd backend
python app.py
```

Open **http://localhost:5000** in Chrome or Edge.

---

## API Endpoints

| Endpoint       | Method | Description                              |
|----------------|--------|------------------------------------------|
| `/api/listen`  | POST   | Speech-to-text (audio → text)           |
| `/api/process` | POST   | AI processing (text → response)          |
| `/api/speak`   | POST   | Text-to-speech (text → audio)           |
| `/api/chat`    | POST   | Combined: process + optional TTS         |
| `/api/task`    | POST   | Execute task (play, open, search, etc.) |
| `/api/clear`   | POST   | Clear conversation memory               |
| `/api/voices`  | GET    | List available TTS voices               |
| `/api/health`  | GET    | Health check                             |

---

## Usage

1. Open http://localhost:5000 in Chrome or Edge (for Web Speech API).
2. Click the microphone button or type in the text box.
3. Use commands like:
   - “Play despacito”
   - “Open Chrome”
   - “Search for Python tutorials”
   - “What’s the weather in London?”
   - “Read the news”
   - Or ask any question for GPT-4.

---

## Troubleshooting

- **Microphone not working**: Allow microphone in the browser and use HTTPS or localhost.
- **OpenAI errors**: Check `.env` and your API key.
- **TTS not playing**: Ensure pyttsx3 is installed; some systems need additional TTS engines.
- **PyAudio** is optional; the app works without it (uses browser speech).

---

## License

MIT
