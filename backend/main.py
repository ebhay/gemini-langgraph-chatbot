import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from database import engine, Base
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gemini LangGraph Chatbot API",
    description="AI Chatbot with persistent memory, tools, and background tasks",
    version="1.0.0"
)

perf_logger = logging.getLogger("perf")


@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    perf_logger.info(
        f"[PERF] {request.method} {request.url.path} → {response.status_code} | {duration:.3f}s"
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])


@app.get("/")
def home():
    return {
        "message": "Gemini LangGraph Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
