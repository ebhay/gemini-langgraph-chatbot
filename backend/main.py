import logging
from fastapi import FastAPI
from routes.chat import router as chat_router
from database import engine, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(chat_router)


@app.get("/")
def home():
    return {"message": "Server running"}