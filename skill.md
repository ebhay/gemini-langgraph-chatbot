# Skill: Building a Gemini + LangGraph Chatbot with Memory and Tools

## Overview
This skill documents the complete process of building a production-ready conversational AI chatbot with persistent memory, session management, tool integration, and background task scheduling. The system uses Google Gemini for AI responses, LangGraph for orchestration, FastAPI for the backend, and React for the frontend.

---

## Core Architecture Pattern

### System Design
```
Frontend (React/Next.js)
    │
    │  REST API (JSON)
    ▼
Backend (FastAPI)
    │
    ├── LangGraph (Stateful Routing)
    │       ├── chat_node     → Gemini LLM
    │       ├── tool_node     → External API integrations
    │       └── scheduler_node → Background task scheduler
    │
    ├── Memory Layer (Two-Tier)
    │       ├── Short-term  → Session-scoped conversation history
    │       └── Long-term   → User profile facts (key-value)
    │
    └── Database (SQLite/PostgreSQL)
            ├── conversations (session_id, user_input, bot_response, timestamp)
            ├── user_profile (key, value)
            └── notifications (message, is_read, timestamp)
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI + Uvicorn (async, fast, Pydantic validation)
- **LLM:** Google Gemini (gemini-1.5-flash or gemini-2.5-flash)
- **Orchestration:** LangGraph (stateful routing between nodes)
- **Database:** SQLite + SQLAlchemy (zero-config, production: PostgreSQL)
- **Scheduler:** APScheduler (background jobs without task queue)
- **API Integration:** OpenStreetMap Nominatim (hospital finder example)

### Frontend
- **Framework:** React 18+ or Next.js 14+
- **State Management:** React hooks (useState, useEffect) or Zustand
- **Styling:** Tailwind CSS or vanilla CSS
- **HTTP Client:** Axios or fetch API

### Dependencies (Python)
```txt
fastapi==0.136.1
uvicorn==0.46.0
google-generativeai==0.8.6
langgraph==1.1.10
SQLAlchemy==2.0.49
APScheduler==3.11.2
python-dotenv==1.2.2
requests==2.33.1
pydantic==2.13.3
```

---

## Implementation Guide

### Phase 1: Backend Core Setup

#### 1.1 Database Models
Create three core tables:

```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_input = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

#### 1.2 Database Connection
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

#### 1.3 Gemini Service with Retry Logic
```python
# services/gemini_service.py
import google.generativeai as genai
import time
import logging

MAX_RETRIES = 3
BACKOFF_BASE = 5  # seconds

def get_response(prompt: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            if response.candidates:
                return response.candidates[0].content.parts[0].text
            return "No response from model"
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                if attempt < MAX_RETRIES:
                    time.sleep(wait)
                    continue
                return "Rate limit exceeded. Please try again later."
            return f"Error: {str(e)}"
```

---

### Phase 2: Memory System Implementation

#### 2.1 Short-Term Memory (Conversation History)
```python
# services/memory_service.py
def save_conversation(user_input: str, bot_response: str, session_id: str = "default"):
    db = SessionLocal()
    try:
        convo = Conversation(
            user_input=user_input,
            bot_response=bot_response,
            session_id=session_id
        )
        db.add(convo)
        db.commit()
    finally:
        db.close()

def get_history(session_id: str = "default", limit: int = 5) -> str:
    db = SessionLocal()
    try:
        convos = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.id.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()
    
    history = ""
    for c in reversed(convos):
        history += f"User: {c.user_input}\nBot: {c.bot_response}\n"
    return history
```

**Design Decision:** Use last 5 exchanges to balance context quality vs. prompt size.

#### 2.2 Long-Term Memory (User Profile)
```python
# services/profile_service.py
def get_user_profile() -> dict:
    db = SessionLocal()
    try:
        profiles = db.query(UserProfile).all()
        return {p.key: p.value for p in profiles}
    finally:
        db.close()

def update_user_profile(key: str, value: str):
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.key == key).first()
        if profile:
            profile.value = value
        else:
            profile = UserProfile(key=key, value=value)
            db.add(profile)
        db.commit()
    finally:
        db.close()
```

**Fact Extraction Pattern:**
Instruct Gemini to append `[EXTRACT: {"key": "value"}]` when it learns new facts:
```python
# In chat_node
if "[EXTRACT:" in response:
    parts = response.split("[EXTRACT:")
    clean_response = parts[0].strip()
    fact_json = parts[1].split("]")[0].strip()
    fact_data = json.loads(fact_json)
    for k, v in fact_data.items():
        update_user_profile(k, str(v))
```

---

### Phase 3: LangGraph Orchestration

#### 3.1 Graph Structure
```python
# services/langgraph_service.py
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ChatState(TypedDict, total=False):
    input: str
    output: str
    session_id: str

# Define nodes
def chat_node(state: ChatState):
    # Fetch history + profile, build prompt, call Gemini
    # Extract facts, save conversation
    return {"output": response}

def tool_node(state: ChatState):
    # Execute tool (e.g., hospital finder)
    return {"output": result}

def scheduler_node(state: ChatState):
    # Schedule background task
    return {"output": confirmation}

# Router logic
def route_decision(state: ChatState) -> str:
    user_input = state.get("input", "").lower()
    if "hospital" in user_input: return "tool"
    if "remind me" in user_input: return "scheduler"
    return "chat"

# Build graph
graph = StateGraph(ChatState)
graph.add_node("router", lambda s: s)
graph.add_node("chat", chat_node)
graph.add_node("tool", tool_node)
graph.add_node("scheduler", scheduler_node)
graph.set_entry_point("router")
graph.add_conditional_edges("router", route_decision, 
    {"chat": "chat", "tool": "tool", "scheduler": "scheduler"})
graph.add_edge("chat", END)
graph.add_edge("tool", END)
graph.add_edge("scheduler", END)
app_graph = graph.compile()
```

---

### Phase 4: Tool Integration

#### 4.1 Hospital Finder (OpenStreetMap Nominatim)
```python
# services/tool_service.py
import requests

def find_hospitals(location: str) -> list[str]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"hospital in {location}",
            "format": "json",
            "limit": 5
        }
        headers = {"User-Agent": "chatbot/1.0"}
        res = requests.get(url, params=params, headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()
        
        if not data:
            return _fallback(location)
        
        return [place["display_name"] for place in data]
    except Exception as e:
        return _fallback(location)

def _fallback(location: str) -> list[str]:
    return [
        f"{location} General Hospital",
        f"{location} Medical Center",
        f"{location} City Hospital"
    ]
```

**Key Pattern:** Always provide fallback data for graceful degradation.

---

### Phase 5: Background Task Scheduling

#### 5.1 APScheduler Setup
```python
# services/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()
scheduler.start()

def send_notification(message: str):
    db = SessionLocal()
    try:
        notif = Notification(message=message)
        db.add(notif)
        db.commit()
    finally:
        db.close()

def schedule_task(message: str, delay: int = 10):
    run_time = time.time() + delay
    run_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_time))
    scheduler.add_job(send_notification, 'date', run_date=run_date, args=[message])
```

---

### Phase 6: FastAPI Routes

#### 6.1 Core Endpoints
```python
# routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default"

@router.post("/chat")
async def chat(request: ChatRequest):
    result = app_graph.invoke({
        "input": request.user_input,
        "session_id": request.session_id
    })
    return {"response": result.get("output")}

@router.get("/sessions")
async def get_sessions():
    # Return list of sessions with metadata
    pass

@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    # Return full conversation history
    pass

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    # Delete session and all messages
    pass

@router.get("/profile")
async def get_profile():
    return get_user_profile()

@router.post("/profile")
async def update_profile(update: dict):
    update_user_profile(update["key"], update["value"])
    return {"status": "success"}

@router.get("/notifications")
async def get_notifications():
    # Return unread notifications
    pass

@router.post("/notifications/read/{notif_id}")
async def mark_notification_read(notif_id: int):
    # Mark as read
    pass
```

#### 6.2 Performance Middleware
```python
# main.py
import time
from fastapi import Request

@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"[PERF] {request.method} {request.url.path} → {response.status_code} | {duration:.3f}s")
    return response
```

---

### Phase 7: Frontend Implementation

#### 7.1 Core State Management
```javascript
// App.js or main component
const [sessions, setSessions] = useState([]);
const [currentSessionId, setCurrentSessionId] = useState(null);
const [messages, setMessages] = useState([]);
const [profile, setProfile] = useState({});
const [notifications, setNotifications] = useState([]);

// Load sessions on mount
useEffect(() => {
    fetch(`${API_URL}/sessions`)
        .then(res => res.json())
        .then(data => {
            setSessions(data);
            if (data.length > 0) {
                setCurrentSessionId(data[0].id);
            }
        });
}, []);

// Load messages when session changes
useEffect(() => {
    if (currentSessionId) {
        fetch(`${API_URL}/sessions/${currentSessionId}`)
            .then(res => res.json())
            .then(setMessages);
    }
}, [currentSessionId]);

// Poll notifications every 10 seconds
useEffect(() => {
    const interval = setInterval(() => {
        fetch(`${API_URL}/notifications`)
            .then(res => res.json())
            .then(setNotifications);
    }, 10000);
    return () => clearInterval(interval);
}, []);
```

#### 7.2 Chat Interface
```javascript
const sendMessage = async (text) => {
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_input: text,
            session_id: currentSessionId
        })
    });
    const data = await response.json();
    
    // Append to messages
    setMessages(prev => [
        ...prev,
        { role: 'user', text },
        { role: 'bot', text: data.response }
    ]);
};
```

#### 7.3 Session Management
```javascript
const createNewSession = () => {
    const newId = `session_${Date.now()}`;
    setSessions(prev => [{ id: newId, last_active: new Date() }, ...prev]);
    setCurrentSessionId(newId);
    setMessages([]);
};

const deleteSession = async (sessionId) => {
    await fetch(`${API_URL}/sessions/${sessionId}`, { method: 'DELETE' });
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (sessionId === currentSessionId) {
        // Switch to another session or create new
        if (sessions.length > 1) {
            setCurrentSessionId(sessions[0].id);
        } else {
            createNewSession();
        }
    }
};
```

---

## Key Design Patterns

### 1. Two-Tier Memory Architecture
- **Short-term:** Last N exchanges (default: 5) injected into every prompt
- **Long-term:** Key-value facts extracted by LLM and stored permanently
- **Why:** Balances context quality vs. token usage; user-controllable via profile UI

### 2. LangGraph Routing
- **Pattern:** Single router node → conditional edges → specialized nodes → END
- **Why:** Cleaner than if/else chains; each node is isolated and testable

### 3. Gemini Fact Extraction
- **Pattern:** Instruct LLM to append `[EXTRACT: {"key": "value"}]` in responses
- **Why:** Offloads NER to LLM; no separate NLP pipeline needed

### 4. Graceful Degradation
- **Pattern:** Always provide fallback data for external API calls
- **Why:** System remains functional even when third-party services fail

### 5. Exponential Backoff for Rate Limits
- **Pattern:** Retry with delays: 5s → 10s → 20s
- **Why:** Respects API limits while maximizing success rate

---

## Performance Optimization

### Backend
1. **Database Indexing:** Index `session_id` and `key` columns
2. **Connection Pooling:** Use SQLAlchemy's `sessionmaker` properly
3. **Async Operations:** FastAPI's async endpoints for I/O-bound tasks
4. **Middleware Logging:** Track p95 latency for `/chat` endpoint

### Frontend
1. **Lazy Loading:** Load messages only when session is selected
2. **Debouncing:** Debounce input to reduce API calls
3. **Polling Optimization:** Use 10-second intervals for notifications
4. **State Management:** Use React.memo for message components

### Target Metrics
- **Response Time:** <15 seconds (p95) for `/chat` endpoint
- **Database Queries:** <100ms for history retrieval
- **Memory Usage:** <500MB for backend process

---

## Environment Configuration

### Backend (.env)
```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///./chat.db  # or postgresql://...
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
# or for production:
REACT_APP_API_URL=https://your-backend.com
```

---

## Deployment Checklist

### Backend (Railway / Render / Cloud Run)
- [ ] Set environment variables (GEMINI_API_KEY, GEMINI_MODEL)
- [ ] Configure start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
- [ ] Enable CORS for frontend domain
- [ ] Set up database (SQLite for dev, PostgreSQL for production)
- [ ] Configure health check endpoint (`GET /`)

### Frontend (Vercel / Netlify)
- [ ] Set REACT_APP_API_URL to deployed backend
- [ ] Configure build command: `npm run build`
- [ ] Set publish directory: `build/` or `dist/`
- [ ] Enable HTTPS
- [ ] Configure redirects for SPA routing

---

## Testing Strategy

### Unit Tests
```python
# test_memory_service.py
def test_save_and_retrieve_conversation():
    save_conversation("Hello", "Hi there", session_id="test")
    history = get_history(session_id="test", limit=1)
    assert "Hello" in history
    assert "Hi there" in history
```

### Integration Tests
```python
# test_langgraph.py
def test_hospital_routing():
    result = app_graph.invoke({
        "input": "Find hospitals in Delhi",
        "session_id": "test"
    })
    assert "hospital" in result["output"].lower()
```

### API Tests
```python
# test_routes.py
def test_chat_endpoint(client):
    response = client.post("/chat", json={
        "user_input": "Hello",
        "session_id": "test"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

---

## Common Pitfalls & Solutions

### 1. SQLite Thread Safety
**Problem:** `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`
**Solution:** Use `connect_args={"check_same_thread": False}` in engine creation

### 2. Gemini Rate Limits
**Problem:** 429 errors during high usage
**Solution:** Implement exponential backoff with 3 retries

### 3. Empty Gemini Responses
**Problem:** Model returns empty candidates
**Solution:** Check `response.candidates` and provide fallback message

### 4. Session State Loss
**Problem:** Sessions disappear on page reload
**Solution:** Persist sessions in database, load on mount

### 5. Notification Polling Overhead
**Problem:** Too many API calls
**Solution:** Use 10-second intervals; consider WebSockets for real-time needs

---

## Extension Ideas

### 1. Multi-User Support
- Add user authentication (JWT, OAuth)
- Scope sessions and profiles by user_id
- Implement user-specific rate limiting

### 2. Advanced Tools
- Web search integration (DuckDuckGo, Brave)
- Weather API
- Calendar integration
- File upload and analysis

### 3. Enhanced Memory
- Vector database for semantic search (Pinecone, Weaviate)
- Conversation summarization for long histories
- Automatic fact verification

### 4. Real-Time Features
- WebSocket support for instant responses
- Typing indicators
- Read receipts

### 5. Analytics
- Conversation analytics dashboard
- User engagement metrics
- Tool usage statistics

---

## Profiling Report Template

### Performance Metrics
```
Endpoint: POST /chat
- p50 latency: X.XXs
- p95 latency: X.XXs
- p99 latency: X.XXs

Database Operations:
- save_conversation: X.XXXs avg
- get_history: X.XXXs avg
- get_user_profile: X.XXXs avg

Gemini API:
- Average response time: X.XXs
- Rate limit hits: X per hour
- Retry success rate: XX%

Bottlenecks Identified:
1. [Description]
2. [Description]

Optimizations Applied:
1. [Description + impact]
2. [Description + impact]
```

---

## Documentation Template

### README Structure
1. **Overview:** What the project does
2. **Architecture:** System diagram + component descriptions
3. **Features:** Bullet list with explanations
4. **Tech Stack:** Table with technology + rationale
5. **Setup Guide:** Step-by-step with code blocks
6. **API Reference:** Endpoint table with examples
7. **Design Decisions:** Why specific choices were made
8. **Deployment:** Platform-specific instructions
9. **Known Limitations:** Honest assessment of constraints

---

## Success Criteria

### Functional Requirements
- [x] Chat works with Gemini + LangGraph
- [x] Response time <15s (p95)
- [x] Memory persists across sessions
- [x] Tools executable via chat
- [x] Background tasks schedule and trigger notifications
- [x] System deployed and accessible

### Code Quality
- [x] Modular service architecture
- [x] Proper error handling and logging
- [x] Environment variable configuration
- [x] Database migrations (if using Alembic)
- [x] Type hints and Pydantic models

### Documentation
- [x] Comprehensive README
- [x] API endpoint documentation
- [x] Setup instructions
- [x] Architecture diagrams
- [x] Profiling report

---

## Learning Outcomes

By completing this project, you will master:

1. **LLM Integration:** Working with Google Gemini API, prompt engineering, rate limit handling
2. **Graph-Based Orchestration:** LangGraph for stateful routing and node composition
3. **Memory Systems:** Two-tier architecture (short-term + long-term)
4. **FastAPI Development:** Async endpoints, middleware, Pydantic validation
5. **Database Design:** SQLAlchemy ORM, session management, indexing
6. **Background Tasks:** APScheduler for delayed job execution
7. **API Integration:** External APIs with fallback strategies
8. **Full-Stack Development:** React state management, API communication
9. **Deployment:** Cloud platform configuration, environment management
10. **Performance Optimization:** Profiling, bottleneck identification, optimization strategies

---

## Quick Start Template

Use this as a starting point for new projects:

```bash
# Backend structure
backend/
├── main.py                  # FastAPI app + middleware
├── database.py              # SQLAlchemy setup
├── models.py                # ORM models
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── routes/
│   └── chat.py              # API endpoints
└── services/
    ├── gemini_service.py    # LLM wrapper
    ├── langgraph_service.py # Graph definition
    ├── memory_service.py    # Conversation history
    ├── profile_service.py   # User facts
    ├── tool_service.py      # External tools
    └── scheduler_service.py # Background tasks

# Frontend structure
frontend/
├── src/
│   ├── App.js               # Main component
│   ├── components/
│   │   ├── Chat.js          # Message interface
│   │   └── Sidebar.js       # Sessions + notifications
│   └── styles.css           # Styling
├── package.json
└── .env
```

---

## Conclusion

This skill provides a complete blueprint for building production-ready conversational AI systems with:
- **Persistent memory** (short-term + long-term)
- **Tool integration** (external APIs)
- **Background tasks** (scheduled notifications)
- **Session management** (multi-conversation support)
- **Performance monitoring** (middleware logging)
- **Graceful error handling** (retries, fallbacks)

The architecture is modular, scalable, and follows industry best practices. Use this as a foundation for building chatbots, virtual assistants, or any LLM-powered application requiring stateful interactions and memory.

---

**Version:** 1.0  
**Last Updated:** 2026-05-05  
**Maintainer:** AI Development Team  
**License:** MIT
