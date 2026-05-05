# Gemini LangGraph Chatbot

> A conversational AI assistant with persistent memory, session management, and real-time tools — built with Google Gemini, LangGraph, FastAPI, and React.

🌐 **Live Demo:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment instructions

📊 **Performance Report:** See [PROFILING_REPORT.md](PROFILING_REPORT.md) for detailed metrics

🐛 **Known Issues:** See [fix.md](fix.md) for bug fixes and improvements

---

## What This Is

A full-stack chatbot that actually remembers you. Not just within a conversation — across sessions. It learns facts about you (name, age, city, preferences) and uses them to personalize every response. It can look up real hospitals near a location, schedule reminders with live notifications, and let you manage everything through a clean sidebar UI.

---

## Architecture Overview

```
Frontend (React)
    │
    │  REST API (JSON)
    ▼
Backend (FastAPI)
    │
    ├── LangGraph (Stateful Routing)
    │       ├── chat_node     → Gemini 1.5 Flash
    │       ├── tool_node     → OpenStreetMap / Nominatim
    │       └── scheduler_node → APScheduler
    │
    ├── Memory Layer
    │       ├── Short-term  → SQLite (per-session conversation history)
    │       └── Long-term   → SQLite (user profile key-value facts)
    │
    └── Database (SQLite via SQLAlchemy)
            ├── conversations
            ├── user_profile
            └── notifications
```

---

## Features

### 🧠 Memory System
- **Short-term:** Last 5 exchanges per session injected into every prompt.
- **Long-term:** Facts extracted by Gemini from natural conversation (e.g., *"I'm 20"* → `age: 20`) and stored permanently in the `user_profile` table.
- **Profile UI:** View and inline-edit all stored facts via the My Profile panel.

### 💬 Multi-Session Chat
- Unlimited named sessions, each with isolated history.
- Session titles auto-generated from the first user message.
- Sessions persist across page reloads — loaded from the database on startup.

### 🏥 Hospital Finder Tool
- Triggered automatically when the user mentions "hospital".
- Fetches live data from **OpenStreetMap Nominatim API** (no API key needed).
- Falls back to static results gracefully on timeout or empty response.

### ⏰ Reminder / Scheduler
- Triggered by phrases like "remind me to…" or "remind me about…".
- Uses **APScheduler** (background thread) to fire after a 10-second delay.
- Notifications saved to DB and polled by the frontend every 10 seconds.
- Dismissible notification cards appear in the sidebar.

### 🗑️ Session Deletion
- Three-dot menu on each sidebar session → custom modal confirmation.
- Deletes from both UI state and backend SQLite in one action.
- Automatically falls back to a new empty session if all sessions are deleted.

### ⚡ Performance Monitoring
- Every HTTP request is timed via FastAPI middleware.
- Logs format: `[PERF] POST /chat → 200 | 1.243s`
- DB write time also logged per `save_conversation` call.

### 🔁 Gemini Rate-Limit Handling
- Automatic retry with **exponential backoff**: 5s → 10s → 20s (3 attempts).
- Non-rate-limit errors fail immediately without retry.

---

## Project Structure

```
chatbot-project/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, perf middleware
│   ├── database.py              # SQLAlchemy engine + session factory
│   ├── models.py                # ORM models: Conversation, UserProfile, Notification
│   ├── requirements.txt         # Python dependencies
│   ├── chat.db                  # SQLite database (auto-created)
│   ├── .env                     # GEMINI_API_KEY, GEMINI_MODEL
│   ├── routes/
│   │   └── chat.py              # All API endpoints
│   └── services/
│       ├── gemini_service.py    # Gemini API wrapper + retry logic
│       ├── langgraph_service.py # Graph definition + routing + nodes
│       ├── memory_service.py    # Short-term history + session queries
│       ├── profile_service.py   # Long-term user fact CRUD
│       ├── tool_service.py      # Hospital lookup via Nominatim
│       └── scheduler_service.py # APScheduler + notification persistence
│
└── frontend/
    ├── package.json
    ├── .env                     # REACT_APP_API_URL
    └── src/
        ├── App.js               # Root: state, sessions, profile logic
        ├── styles.css           # All styles (custom CSS)
        ├── index.js             # React entry point
        └── components/
            ├── Chat.js          # Message list + input box
            └── Sidebar.js       # Session list + notifications + modals
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message, get a response |
| `GET` | `/sessions` | List all sessions with metadata |
| `GET` | `/sessions/{id}` | Full message history for a session |
| `DELETE` | `/sessions/{id}` | Delete session and all its messages |
| `GET` | `/profile` | Get all stored user facts |
| `POST` | `/profile` | Update or add a user fact |
| `GET` | `/notifications` | Get unread notifications |
| `POST` | `/notifications/read/{id}` | Mark a notification as read |
| `GET` | `/` | Health check |

---

## Memory Design — Why This Approach?

This project uses a **three-tier memory architecture** stored in SQLite:

### Tier 1 — Short-term (Conversation History)
Stored in the `conversations` table, scoped by `session_id`. On every request, the last **5 exchanges** are fetched and injected into the Gemini prompt as context. Five turns was chosen deliberately — it's enough to maintain conversational flow without bloating the prompt or hitting token limits.

### Tier 2 — Long-term (User Profile Facts)
Stored in the `user_profile` table as key-value pairs. After every Gemini response, the model is instructed to append a machine-readable `[EXTRACT: {"key": "value"}]` block if it detected a new personal fact. The backend parses this block, strips it from the visible response, and upserts the fact into the database.

### Tier 3 — Episodic (Event Memories)
Stored in the `episodic_memories` table. Captures specific events and conversations with importance scores. These memories can be recalled later to provide context about past interactions, decisions, or significant moments.

**Why this is the best approach for this project:**

- **No vector DB needed.** Facts are atomic key-value pairs (name, age, city), not semantic documents. SQLite lookups are instant, zero-overhead, and require no extra infrastructure.
- **Fully persistent.** Unlike in-memory stores (Redis, Python dicts), everything survives server restarts.
- **User-controllable.** The Profile panel lets users view and correct any fact the bot extracted — important for trust.
- **Gemini does the extraction.** Offloading NER (named entity recognition) to the LLM itself means no separate NLP pipeline is needed. The prompt enforces a strict JSON format for reliable parsing.
- **Episodic recall.** Important conversations and events are summarized and stored with importance scores, allowing the bot to recall past interactions contextually.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Google Gemini 1.5 Flash | Fast, cheap, large context window |
| Orchestration | LangGraph | Clean stateful routing between tool/chat/scheduler flows |
| Backend | FastAPI + Uvicorn | Async, fast, Pydantic validation built-in |
| Database | SQLite + SQLAlchemy | Zero-config persistence, perfect for single-server deploys |
| Scheduler | APScheduler | Lightweight background jobs without a task queue |
| Hospital Data | OpenStreetMap Nominatim | Free, no API key, real data |
| Frontend | React 19 (CRA) | Component model fits the session/chat/profile split cleanly |
| Styling | Vanilla CSS | Full control, zero dependencies |

---

## Setup Guide

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

---

### 1. Clone the Repository

```bash
git clone https://github.com/Som0904/gemini-langgraph-chatbot.git
cd gemini-langgraph-chatbot
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Create the `.env` file:**

```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**Start the server:**

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
The SQLite database (`chat.db`) is created automatically on first run.

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

**Create the `.env` file:**

```bash
# frontend/.env
REACT_APP_API_URL=http://127.0.0.1:8000
```

> For production, replace this with your deployed backend URL.

**Start the dev server:**

```bash
npm start
```

The app will open at `http://localhost:3000`.

---

### 4. Verify Everything Works

1. Open `http://localhost:3000`
2. Type `"Hi, my name is Alex"` — the bot should greet you and extract your name.
3. Open **My Profile** in the sidebar — `name: Alex` should appear.
4. Type `"Find hospitals in Delhi"` — live results from Nominatim should appear.
5. Type `"Remind me to drink water"` — a notification should appear in the sidebar after ~10 seconds.

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | — | Your Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Model name to use |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REACT_APP_API_URL` | ✅ Yes | — | Backend base URL |

---

## Deployment

🌐 **Live URL:** `https://your-deployment-url.com` ← _replace this_

### Deploy Backend (e.g., Render / Railway)
- Set `GEMINI_API_KEY` and `GEMINI_MODEL` as environment variables in your platform dashboard.
- Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Deploy Frontend (e.g., Vercel / Netlify)
- Set `REACT_APP_API_URL` to your deployed backend URL.
- Build command: `npm run build`
- Publish directory: `build/`

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **LangGraph for routing** | Cleaner than if/else chains; each node is isolated and testable |
| **SQLite over PostgreSQL** | No infra overhead; `check_same_thread=False` handles FastAPI concurrency |
| **Gemini for fact extraction** | Avoids a separate NLP pipeline; prompt-based extraction is flexible and accurate |
| **5-turn short-term window** | Balances context quality vs. prompt size; configurable via `limit` param |
| **APScheduler over Celery** | No Redis/broker needed for simple in-process delayed jobs |
| **Nominatim over Google Maps** | Zero cost, no API key required, sufficient for this use case |
| **Custom CSS over Tailwind** | Simpler build setup; full control over specifics without purge/JIT concerns |
| **Polling over WebSockets** | Notifications only need ~10s latency; polling avoids WS connection complexity |

---

## Known Limitations

- SQLite is not suited for high-concurrency production traffic — migrate to PostgreSQL for scale.
- The Nominatim API has rate limits; heavy usage may require a self-hosted instance.
- The Gemini `[EXTRACT:]` parsing relies on the model following instructions — occasional misses are possible.
- No authentication — all users share the same profile store (single-user design).

---

<p align="center">Built with 🤖 Gemini · ⚡ LangGraph · 🐍 FastAPI · ⚛️ React</p>
