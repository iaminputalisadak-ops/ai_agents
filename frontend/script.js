/**
 * AI Voice Agent - Frontend Application
 * Handles voice input (Web Speech API), chat UI, TTS playback, and settings.
 */

const API_BASE = '/api';

// State
const state = {
  isListening: false,
  isProcessing: false,
  isSpeaking: false,
  recognition: null,
  audioContext: null,
  settings: {
    voiceSpeed: 175,
    voiceVolume: 1,
    voiceIndex: null,
    continuousMode: true,
  },
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const voiceBtn = document.getElementById('voiceBtn');
const voiceVisualizer = document.getElementById('voiceVisualizer');
const voiceStatus = document.getElementById('voiceStatus');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettings = document.getElementById('closeSettings');
const voiceSpeed = document.getElementById('voiceSpeed');
const voiceVolume = document.getElementById('voiceVolume');
const voiceSelect = document.getElementById('voiceSelect');
const speedValue = document.getElementById('speedValue');
const volumeValue = document.getElementById('volumeValue');

// =============================================================================
// Web Speech API - Speech Recognition
// =============================================================================

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceStatus.textContent = 'Voice not supported in this browser';
    voiceBtn.disabled = true;
    return;
  }
  state.recognition = new SpeechRecognition();
  state.recognition.continuous = state.settings.continuousMode;
  state.recognition.interimResults = false;
  state.recognition.lang = 'en-US';

  state.recognition.onstart = () => {
    state.isListening = true;
    setState('listening');
    voiceStatus.textContent = 'Listening...';
  };

  state.recognition.onresult = (event) => {
    const last = event.results.length - 1;
    const text = event.results[last][0].transcript;
    if (text.trim()) {
      processUserInput(text.trim());
    }
  };

  state.recognition.onend = () => {
    state.isListening = false;
    if (!state.isProcessing && !state.isSpeaking) {
      setState('ready');
      voiceStatus.textContent = 'Click to speak';
    }
  };

  state.recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    state.isListening = false;
    setState('ready');
    voiceStatus.textContent = 'Click to speak';
  };
}

// =============================================================================
// Voice Button & Toggle
// =============================================================================

voiceBtn.addEventListener('click', () => {
  if (state.isProcessing || state.isSpeaking) return;
  if (state.isListening) {
    state.recognition?.stop();
  } else {
    state.recognition?.start();
  }
});

// =============================================================================
// Text Input & Send
// =============================================================================

function handleSend() {
  const text = textInput.value.trim();
  if (!text) return;
  textInput.value = '';
  processUserInput(text);
}

sendBtn.addEventListener('click', handleSend);
textInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleSend();
});

// =============================================================================
// API Calls
// =============================================================================

async function processUserInput(text) {
  addMessage('user', text);
  setState('processing');
  voiceStatus.textContent = 'Thinking...';

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        speak: true,
        rate: state.settings.voiceSpeed,
        volume: state.settings.voiceVolume,
        voice_index: state.settings.voiceIndex,
      }),
    });

    const data = await res.json();

    if (!data.success) {
      throw new Error(data.error || 'Request failed');
    }

    addMessage('ai', data.response);

    if (data.audio) {
      setState('speaking');
      voiceStatus.textContent = 'Speaking...';
      await playAudioBase64(data.audio);
    }

  } catch (err) {
    console.error(err);
    addMessage('ai', `Error: ${err.message}`);
  }

  setState('ready');
  voiceStatus.textContent = 'Click to speak';
}

async function playAudioBase64(base64Audio) {
  return new Promise((resolve, reject) => {
    const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
    const cleanup = () => { state.isSpeaking = false; };
    audio.onended = () => { cleanup(); resolve(); };
    audio.onerror = (e) => { cleanup(); reject(e); };
    state.isSpeaking = true;
    audio.play().then(resolve).catch((e) => { cleanup(); reject(e); });
  });
}

// =============================================================================
// Chat UI
// =============================================================================

function addMessage(role, content) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = content;
  const meta = document.createElement('div');
  meta.className = 'message-meta';
  meta.textContent = role === 'user' ? 'You' : 'AI Assistant';
  bubble.appendChild(meta);
  div.appendChild(bubble);
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// =============================================================================
// Clear History
// =============================================================================

clearBtn.addEventListener('click', async () => {
  try {
    await fetch(`${API_BASE}/clear`, { method: 'POST' });
    chatMessages.innerHTML = '';
  } catch (err) {
    console.error('Failed to clear:', err);
  }
});

// =============================================================================
// Visual State
// =============================================================================

function setState(s) {
  voiceVisualizer.classList.remove('listening', 'processing', 'speaking');
  voiceBtn.disabled = s === 'processing' || s === 'speaking';
  if (s === 'listening' || s === 'processing' || s === 'speaking') {
    voiceVisualizer.classList.add(s);
  }
}

// =============================================================================
// Settings Modal
// =============================================================================

settingsBtn.addEventListener('click', () => {
  settingsModal.classList.add('show');
  loadVoices();
});

closeSettings.addEventListener('click', () => {
  settingsModal.classList.remove('show');
});

settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) {
    settingsModal.classList.remove('show');
  }
});

// Voice speed
voiceSpeed.addEventListener('input', () => {
  state.settings.voiceSpeed = parseInt(voiceSpeed.value, 10);
  speedValue.textContent = state.settings.voiceSpeed;
});

// Voice volume
voiceVolume.addEventListener('input', () => {
  state.settings.voiceVolume = parseInt(voiceVolume.value, 10) / 100;
  volumeValue.textContent = Math.round(state.settings.voiceVolume * 100);
});

// Voice selection
voiceSelect.addEventListener('change', () => {
  const idx = voiceSelect.value;
  state.settings.voiceIndex = idx === '' ? null : parseInt(idx, 10);
});

document.getElementById('continuousMode').addEventListener('change', (e) => {
  state.settings.continuousMode = e.target.checked;
  if (state.recognition) {
    state.recognition.continuous = state.settings.continuousMode;
  }
});

async function loadVoices() {
  try {
    const res = await fetch(`${API_BASE}/voices`);
    const data = await res.json();
    if (!data.success) return;
    voiceSelect.innerHTML = '<option value="">Default</option>';
    data.voices.forEach((v) => {
      const opt = document.createElement('option');
      opt.value = v.index;
      opt.textContent = v.name || `Voice ${v.index}`;
      if (v.index === state.settings.voiceIndex) opt.selected = true;
      voiceSelect.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to load voices:', err);
  }
}

// =============================================================================
// Init
// =============================================================================

function init() {
  voiceSpeed.value = state.settings.voiceSpeed;
  voiceVolume.value = state.settings.voiceVolume * 100;
  speedValue.textContent = state.settings.voiceSpeed;
  volumeValue.textContent = state.settings.voiceVolume * 100;
  initSpeechRecognition();
}

init();
