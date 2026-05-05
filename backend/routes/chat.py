import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from auth import get_current_user, get_db
from models import User, Notification, Conversation
from services.langgraph_service import app_graph
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


class ProfileUpdate(BaseModel):
    key: str
    value: str


@router.post("/chat")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        result = app_graph.invoke({
            "input": request.user_input,
            "session_id": request.session_id,
            "user_id": current_user.id
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ROUTE] Graph invocation failed for user {current_user.id}: {e}")
        return {"response": f"Error: {str(e)}"}

    output = result.get("output") if result else None
    if not output or not output.strip():
        logger.warning(f"[ROUTE] Graph returned empty output for user {current_user.id}")
        return {"response": "I couldn't generate a response. Please try again."}

    return {"response": output}


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return get_user_profile(current_user.id)


@router.post("/profile")
async def update_profile(update: ProfileUpdate, current_user: User = Depends(get_current_user)):
    update_user_profile(current_user.id, update.key, update.value)
    return {"status": "success"}


@router.get("/sessions")
async def get_sessions(current_user: User = Depends(get_current_user)):
    return get_all_sessions(current_user.id)


@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convos = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id, Conversation.session_id == session_id)
        .order_by(Conversation.id.asc())
        .all()
    )
    history = []
    for c in convos:
        history.append({"role": "user", "text": c.user_input, "created_at": str(c.created_at)})
        history.append({"role": "bot", "text": c.bot_response, "created_at": str(c.created_at)})
    return history


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.session_id == session_id
        ).delete()
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()
    return [{"id": n.id, "message": n.message, "created_at": n.created_at, "type": n.notification_type} for n in notifs]


@router.post("/notifications/read/{notif_id}")
async def mark_notification_read(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Notification not found")


@router.delete("/notifications/{notif_id}")
async def delete_notification(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if notif:
        db.delete(notif)
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Notification not found")
