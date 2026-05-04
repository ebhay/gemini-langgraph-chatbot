import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from services.langgraph_service import app_graph
from database import SessionLocal
from models import Notification, UserProfile, Conversation
from sqlalchemy.orm import Session
from services.profile_service import get_user_profile, update_user_profile
from services.memory_service import get_all_sessions

router = APIRouter()

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default"

    @field_validator("user_input")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_input cannot be empty or whitespace")
        return v.strip()


@router.get("/notifications")
async def get_notifications():
    db = SessionLocal()
    try:
        notifs = db.query(Notification).filter(Notification.is_read == 0).all()
        return [{"id": n.id, "message": n.message, "created_at": n.created_at} for n in notifs]
    finally:
        db.close()

@router.post("/notifications/read/{notif_id}")
async def mark_notification_read(notif_id: int):
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.id == notif_id).first()
        if notif:
            notif.is_read = 1
            db.commit()
            return {"status": "success"}
        raise HTTPException(status_code=404, detail="Notification not found")
    finally:
        db.close()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = app_graph.invoke({
            "input": request.user_input,
            "session_id": request.session_id
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ROUTE] Graph invocation failed: {e}")
        return {"response": f"Error: {str(e)}"}

    output = result.get("output") if result else None
    if not output or not output.strip():
        logger.warning("[ROUTE] Graph returned empty output")
        return {"response": "I couldn't generate a response. Please try again."}

    return {"response": output}


# --- PROFILE ROUTES ---

@router.get("/profile")
async def get_profile():
    return get_user_profile()

class ProfileUpdate(BaseModel):
    key: str
    value: str

@router.post("/profile")
async def update_profile(update: ProfileUpdate):
    update_user_profile(update.key, update.value)
    return {"status": "success"}


# --- SESSION & HISTORY ROUTES ---

@router.get("/sessions")
async def get_sessions():
    return get_all_sessions()

@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    db = SessionLocal()
    try:
        convos = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.id.asc())
            .all()
        )
        history = []
        for c in convos:
            history.append({"role": "user", "text": c.user_input, "created_at": str(c.created_at)})
            history.append({"role": "bot", "text": c.bot_response, "created_at": str(c.created_at)})
        return history
    finally:
        db.close()

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    db = SessionLocal()
    try:
        db.query(Conversation).filter(Conversation.session_id == session_id).delete()
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()