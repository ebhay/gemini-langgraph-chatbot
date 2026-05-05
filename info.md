Product Requirement Document (PRD) - 2 Days
Title
Gemini + Langraph Powered Chatbot with FastAPI Backend
Objective
Each Intern will build and deliver a functional chatbot system in 48 hours. The chatbot must integrate Gemini (for AI responses) and Langraph (for orchestration). It should run on a FastAPI backend, with a simple UI (framework of choice). The chatbot should support memory, tools, and background tasks with notifications. You can use any ai coding tools you want.
Scope of Work
Core Deliverables
1. Backend (FastAPI)
○ /chat endpoint powered by Gemini + Langraph.
○ Implement short-term, episodic, and long-term memory.
○ Store user personal details and past conversations.
○ Response time: <15 seconds (p95).
2. Frontend (Interns decide framework)
○ Simple interface for chatting.
○ Display past conversations.
○ Allow users to view/edit stored personal details.
3. Tools Integration
○ Example tool: Find nearby hospitals (mock + real implementation) - Gmaps api or Openmaps
○ Expose tool endpoints usable by chatbot.
4. Background Tasks
○ Handle long-term requests via scheduled jobs.
○ Trigger mock email/notification when job completes.
5. Profiling & Performance Report
○ Collect latency, CPU, and DB timings.
○ Deliver short profiling report with optimizations.
6. Deployment
○ Host backend (Railway/Render/Cloud Run/etc.).
○ Host frontend (Vercel or equivalent).
Technical Guidelines
● Backend: FastAPI + Uvicorn.
● Integration: Langraph (mandatory), Gemini API.
● Memory: Decide on your own, and let us know why this is the best
● Scheduling: RQ, APScheduler, or Celery.
● Notifications: Mock mail (log to console) or real integration (SendGrid/Mailgun).
● Frontend: You can choose (React, Vue, Streamlit, etc.).
● Profiling: Middleware timings + simple report.
Acceptance Criteria
● Chat works with Gemini + Langraph.
● Response < 15s (p95).
● Memory persists across sessions.
● Tools executable via chat.
● Background tasks schedule and trigger notification.
● Profiling report submitted.
● System deployed and accessible.
Deliverables Checklist
● FastAPI server with endpoints.
● Langraph + Gemini integrated.
● Memory modules implemented.
● Tool endpoints (hospital search).
● Background task scheduling.
● Frontend connected to backend.
● Deployment instructions & live URL.
● Profiling report.
● README with setup guide.
Timeline
● Day 1: Backend core + chat integration + memory basics.
● Day 2: Tools, background tasks, notifications, profiling, deployment.
Notes for Interns
● You are free to choose the frontend framework and deployment platform.
● Focus on working prototypes, not polish.
● Document your choices in the README.
● Langraph must be used in the chat pipeline.