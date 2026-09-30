# 🎙️ LiveKit Voice AI Assistant

A real-time **AI voice assistant** built with **Python, LiveKit Agents, Gradio, and LiveKit Inference**.

This project allows users to connect their microphone through a web interface and communicate with an AI voice agent in real time. The system receives spoken input, converts speech to text, processes the request with a Large Language Model, and converts the AI response back into speech.

The project combines a **LiveKit realtime voice agent** with a **Gradio-based web interface** that provides microphone controls, connection management, audio playback, and a live microphone waveform visualizer.

---

## ✨ Features

* 🎙️ Real-time voice conversation with an AI assistant
* 🔊 Speech-to-Text (STT)
* 🧠 Large Language Model (LLM) processing
* 🗣️ Text-to-Speech (TTS)
* 🌐 LiveKit realtime audio communication
* 🎛️ Microphone mute/unmute control
* 🔈 Enable/disable AI audio playback
* 📡 LiveKit room connection management
* 📊 Real-time microphone waveform visualizer
* 🔇 Audio noise cancellation / enhancement
* 👤 Custom user name
* 🚪 Custom room name or automatic room generation
* 🔐 LiveKit access-token generation
* 🧩 Automatic dispatch to the configured voice agent
* 🐛 Voice transcription and session debugging logs
* ⚠️ STT timeout and session error monitoring
* 🌙 Clean responsive web interface

---

# 🏗️ Architecture

The application follows this voice pipeline:

```text
┌─────────────────────┐
│     User Browser    │
│                     │
│  🎙️ Microphone      │
└──────────┬──────────┘
           │
           │ Audio
           ▼
┌─────────────────────┐
│      LiveKit        │
│   Realtime Room     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Speech-to-Text       │
│ AssemblyAI Universal │
│ 3.5 Pro              │
└──────────┬──────────┘
           │
           │ Transcript
           ▼
┌─────────────────────┐
│        LLM          │
│  Google Gemma 4     │
│      31B IT         │
└──────────┬──────────┘
           │
           │ Generated Text
           ▼
┌─────────────────────┐
│      TTS            │
│ Fish Audio S2.1 Pro │
└──────────┬──────────┘
           │
           │ Audio
           ▼
┌─────────────────────┐
│     LiveKit Room    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     User Browser    │
│   🔊 AI Voice       │
└─────────────────────┘
```

The core `AgentSession` orchestrates the STT, LLM, TTS, turn handling, VAD, and realtime room interaction. LiveKit documents `AgentSession` as the main orchestrator for voice AI pipelines.

---

# 🛠️ Technologies

| Technology            | Purpose                                        |
| --------------------- | ---------------------------------------------- |
| **Python 3.14+**      | Main programming language                      |
| **LiveKit Agents**    | Realtime voice-agent framework                 |
| **LiveKit API**       | Access tokens and room configuration           |
| **LiveKit Inference** | STT, LLM, and TTS model access                 |
| **Gradio**            | Web interface                                  |
| **JavaScript**        | Browser-side LiveKit client and audio controls |
| **AI Coustics**       | Audio enhancement / noise cancellation         |
| **uv**                | Python environment and dependency management   |
| **python-dotenv**     | Environment variable loading                   |

The project's `pyproject.toml` currently declares Python `>=3.14` along with Gradio, LiveKit Agents, LiveKit API, AI Coustics, and python-dotenv.

---

# 🎧 Voice AI Models

The current agent is configured with the following models.

### Speech-to-Text

```text
assemblyai/universal-3-5-pro
```

Language:

```text
en
```

The project also configures silence and VAD-related STT parameters.

### Language Model

```text
google/gemma-4-31b-it
```

### Text-to-Speech

```text
fishaudio/s2.1-pro
```

Voice:

```text
fa4c9eb3dccc4806b382b40d61c6b10a
```

### Voice Activity Detection

```text
silero
```

with an activation threshold of:

```text
0.3
```

### Audio Enhancement

The project uses the AI Coustics:

```text
QUAIL_VF_S
```

enhancement model for incoming audio.

LiveKit Inference currently supports using STT, LLM, and TTS models through its `inference` module, including the same Gemma and Fish Audio model families used by this project.

---

# 📋 Requirements

Before running the project, install:

### Required software

* Python **3.14 or newer**
* Git
* uv
* LiveKit CLI
* A LiveKit project/account
* A modern web browser with microphone support

The project specifies Python `3.14` in `.python-version`.

---

# 📥 Installation

## 1. Clone the repository

```powershell
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Enter the project directory:

```powershell
cd livekit-voiceagent
```

---

## 2. Install uv

Install uv from:

https://docs.astral.sh/uv/

Check that it is installed:

```powershell
uv --version
```

---

## 3. Create the project environment

Run:

```powershell
uv sync
```

This project is configured through `pyproject.toml`, so uv can create/manage the environment and install the listed dependencies.

---

# 🔑 Environment Variables

Create a file named:

```text
.env
```

in the project root.

The Gradio frontend expects these values:

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

The application reads these values from `.env` using `python-dotenv`.

### Example

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

> Never commit your real `.env` file, API keys, or API secrets to GitHub.

---

# ▶️ Running the Project

The project has two main parts:

```text
1. LiveKit Voice Agent
2. Gradio Web Interface
```

Run them in **two separate terminals**.

---

## Terminal 1 — Start the LiveKit Agent

The agent entry point is:

```text
agent.py
```

Using the current LiveKit CLI:

```powershell
lk agent dev agent.py
```

LiveKit's current CLI supports `lk agent dev [entrypoint]` for local agent development and automatic reload.

You can also start it in production-style local mode with:

```powershell
lk agent start agent.py
```

LiveKit documents `lk agent start` for running the agent locally in production mode.

---

## Terminal 2 — Start the Gradio Interface

Run:

```powershell
uv run app.py
```

The application launches on:

```text
http://127.0.0.1:7860
```

The source code explicitly configures Gradio to use host `127.0.0.1` and port `7860`.

Open the URL in your browser.

---

# 🚀 Quick Start

Once everything is installed:

### Terminal 1

```powershell
cd livekit-voiceagent
uv sync
uv run agent.py dev
```

### Terminal 2

```powershell
cd livekit-voiceagent
uv run app.py
```

Then open:

```text
http://127.0.0.1:7860
```

---

# 🎙️ How to Use

### Step 1 — Enter your name

The interface provides a **Your Name** field.

Example:

```text
Muhammad Shahzaib
```

If no name is supplied, the application uses:

```text
Guest
```

---

### Step 2 — Enter a room name

You can enter your own LiveKit room name.

Or leave the field empty.

When empty, the application automatically creates a unique room name such as:

```text
voice-room-a1b2c3d4
```

---

### Step 3 — Create the voice session

Click:

```text
Create Voice Session
```

The backend creates a LiveKit access token and configures the room to dispatch the agent named:

```text
my-agent
```

---

### Step 4 — Connect

After the session is created:

```text
Connect
```

The browser requests microphone permission and connects to the LiveKit room.

The frontend uses the LiveKit JavaScript client to create the realtime room connection.

---

### Step 5 — Enable microphone

The application publishes the browser microphone into the LiveKit room.

You should see:

```text
Microphone is live.
```

---

### Step 6 — Enable AI audio

Click:

```text
Enable Audio
```

The browser then enables playback of the AI assistant's audio response.

---

### Step 7 — Talk to the assistant

Speak normally into your microphone.

The voice pipeline processes:

```text
Your Speech
     ↓
Speech-to-Text
     ↓
Gemma 4 31B
     ↓
Text-to-Speech
     ↓
AI Voice Response
```

---

# 🎛️ Voice Controls

The web interface provides several controls.

### Connect

Connects the browser to the LiveKit room.

### Mute

Turns the local microphone on or off.

### Enable Audio

Enables browser playback for the AI's voice.

### Disconnect

Leaves the LiveKit room and stops the active voice session.

The corresponding controls are implemented directly in the Gradio/JavaScript interface.

---

# 📊 Microphone Visualizer

The application includes a browser-side microphone waveform visualizer.

It uses the Web Audio API to:

* Read microphone audio
* Analyze the waveform
* Draw the waveform on a canvas
* Calculate an approximate audio level
* Display microphone status

Example statuses include:

```text
Microphone connected • Speak now
```

and:

```text
Microphone active • Audio level 25%
```

---

# 🔊 AI Audio Playback

When the AI publishes an audio track, the browser subscribes to the remote track and attaches it to the page for playback.

The application monitors:

```text
TrackSubscribed
```

events and attaches remote audio tracks when available.

---

# 🧠 Agent Behavior

The voice assistant is configured with the following behavior:

* Helpful
* Concise
* Friendly
* Curious
* Informative
* Conversational
* Simple responses without complex formatting

The system instructions are defined in the `Assistant` class in `agent.py`.

---

# 🔄 Turn Handling

The project uses STT-based turn detection:

```python
turn_handling=TurnHandlingOptions(
    turn_detection="stt",
    endpointing={
        "min_delay": 0,
    },
)
```

This controls when the system considers the user's spoken turn complete.

---

# 🐛 Debugging and Logging

The agent contains several debugging event handlers.

## User transcription

The application logs:

```text
USER:
```

along with:

* Transcript
* Final/non-final state
* Detected language

---

## User state

The application logs user voice-state changes:

```text
USER STATE:
```

---

## STT timeout

The project listens for:

```text
user_transcription_timeout
```

and prints timeout information.

---

## Session errors

The application also listens for:

```text
error
```

events and prints session errors for debugging.

---

# 📁 Project Structure

```text
livekit-voiceagent/
│
├── README.md
├── agent.py
├── app.py
├── pyproject.toml
├── .python-version
│
└── src/
    └── livekit_voiceagent/
        └── __init__.py
```

### `agent.py`

Contains the main LiveKit voice agent.

Responsibilities include:

* Agent definition
* Speech-to-text configuration
* LLM configuration
* Text-to-speech configuration
* VAD
* Turn handling
* Audio enhancement
* Room/session management
* Debug logging
* Initial greeting

The agent registers under:

```text
my-agent
```

---

### `app.py`

Contains the Gradio web interface.

Responsibilities include:

* User input
* Room creation
* LiveKit access-token generation
* Browser-side LiveKit connection
* Microphone management
* Audio playback
* Microphone visualizer
* Connection status
* Mute/unmute
* Disconnect functionality

---

### `pyproject.toml`

Defines the project metadata, Python requirement, dependencies, and build system.

Current dependencies include:

```text
gradio>=6.29.0
livekit-agents>=1.8.3
livekit-api>=1.2.1
livekit-plugins-ai-coustics>=0.3.2
python-dotenv>=1.2.3
```

---

### `.python-version`

Contains:

```text
3.14
```

---

# 🔐 Security

Do not upload sensitive credentials to GitHub.

Your `.env` file should remain private:

```text
.env
```

It contains:

```text
LIVEKIT_URL
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
```

Never publish the API secret inside:

* Python source code
* README files
* Screenshots
* GitHub commits
* LinkedIn posts
* Public documentation

---

# ⚠️ Troubleshooting

## `LIVEKIT_URL is missing`

Make sure `.env` exists in the project root:

```text
livekit-voiceagent/
├── .env
├── agent.py
├── app.py
└── pyproject.toml
```

Check that:

```env
LIVEKIT_URL=...
```

is present.

The Gradio application explicitly checks for this variable.

---

## `LIVEKIT_API_KEY or LIVEKIT_API_SECRET is missing`

Make sure both variables are configured:

```env
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

The frontend uses these credentials to generate a LiveKit access token.

---

## Browser does not detect microphone

Make sure:

* Browser microphone permission is allowed
* A microphone is connected
* Another application is not exclusively using the microphone
* The browser is allowed to access microphone devices

When connecting, the application requests:

```javascript
navigator.mediaDevices.getUserMedia({
    audio: true
});
```

---

## AI voice is not playing

Click:

```text
Enable Audio
```

Modern browsers can restrict automatic audio playback until the user interacts with the page.

The application handles this through:

```javascript
room.startAudio()
```

---

## STT timeout

The application currently uses:

```text
transcription_timeout = 5.0 seconds
```

If speech is not being transcribed correctly, check:

* Microphone permissions
* Microphone input level
* Network connection
* LiveKit connection
* STT service availability
* STT timeout configuration

---

# 🧪 Testing Locally

For development, use:

```powershell
lk agent dev agent.py
```

LiveKit's current CLI provides development, console, start, and debugger commands for local testing.

You can also test the agent directly through LiveKit's local console mode:

```powershell
lk agent console agent.py
```

Console mode provides microphone/speaker interaction without connecting the agent to a LiveKit Cloud room, making it useful for local agent testing.

---

# 🌐 How the Web Interface Works

The frontend uses:

```text
Gradio
   ↓
Python backend
   ↓
LiveKit access token
   ↓
Browser JavaScript
   ↓
LiveKit JavaScript Client
   ↓
LiveKit Room
```

The LiveKit JavaScript SDK is loaded in the Gradio page from:

```text
https://cdn.jsdelivr.net/npm/livekit-client@2.22.3/dist/livekit-client.umd.min.js
```

---

# 📦 Dependencies

The project uses:

```text
Python >= 3.14
```

Main packages:

```text
gradio
livekit-agents
livekit-api
livekit-plugins-ai-coustics
python-dotenv
```

The exact minimum versions are defined in `pyproject.toml`.

---

# 💡 What I Learned From This Project

This project provided practical experience with:

* Real-time AI voice agents
* LiveKit Agents
* WebRTC-based realtime communication
* Speech-to-Text pipelines
* Large Language Models
* Text-to-Speech systems
* Voice Activity Detection
* Turn detection
* Audio enhancement
* Python async programming
* LiveKit API and access tokens
* Environment variables and secrets
* Browser microphone APIs
* JavaScript event handling
* Gradio web interfaces
* Realtime audio streaming
* Debugging voice AI pipelines
* Session and room management

---

# 🔮 Possible Future Improvements

Potential future enhancements include:

* Multi-language voice support
* Conversation transcript display
* Persistent conversation history
* Multiple AI personalities
* Model selection from the UI
* Voice selection
* Configurable STT/LLM/TTS models
* Image input support
* Tool/function calling
* Web search integration
* Authentication
* Database-backed conversations
* Deployment to LiveKit Cloud
* Mobile-friendly voice interface

---

# 📚 Useful Documentation

### LiveKit

https://docs.livekit.io/agents/

### LiveKit Agent Commands

https://docs.livekit.io/reference/developer-tools/livekit-cli/agent/

### LiveKit Inference

https://docs.livekit.io/agents/models/inference/

### Gradio

https://www.gradio.app/

### Python

https://www.python.org/

### uv

https://docs.astral.sh/uv/

---

👨‍💻 Author

Muhammad Shahzaib

IT / Computer Science Graduate
AI & Technology Enthusiast

GitHub




Project repository:

https://github.com/shahzaibx-ai/Livekit-voiceagent

LinkedIn


https://www.linkedin.com/in/muhammad-shahzaib-arshed/

Email

📧 mszaibi007@gmail.com

---

# ⭐ Project

This project demonstrates how **realtime communication, speech recognition, LLMs, text-to-speech, and browser-based audio interfaces** can be combined to build a complete AI voice assistant.

Built with:

```text
Python
+
LiveKit
+
Gradio
+
AI Models
```

---
