import logging
import time
from fastapi import FastAPI, Request
from routes.chat import router as chat_router
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

app.include_router(chat_router)


@app.get("/")
def home():
    return {"message": "Server running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)