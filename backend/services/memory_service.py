import logging
import time
from database import SessionLocal
from models import Conversation

logger = logging.getLogger(__name__)


def save_conversation(user_input: str, bot_response: str, session_id: str = "default") -> None:
    """Persist a user/bot exchange to the database with session context."""
    db = SessionLocal()
    try:
        convo = Conversation(
            user_input=user_input, 
            bot_response=bot_response,
            session_id=session_id
        )
        db.add(convo)
        start = time.time()
        db.commit()
        logger.info(
            f"[MEMORY] Saved convo | session={session_id} | input_len={len(user_input)} | db_time={time.time()-start:.3f}s"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[MEMORY] Failed to save conversation: {e}")
        raise
    finally:
        db.close()


def get_history(session_id: str = "default", limit: int = 5) -> str:
    """Retrieve the last `limit` exchanges for a specific session."""
    db = SessionLocal()
    try:
        start = time.time()
        convos = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.id.desc())
            .limit(limit)
            .all()
        )
        logger.info(f"[MEMORY] get_history | session={session_id} | rows={len(convos)} | db_time={time.time()-start:.3f}s")
    except Exception as e:
        logger.error(f"[MEMORY] Failed to retrieve history for {session_id}: {e}")
        return ""
    finally:
        db.close()

    history = ""
    for c in reversed(convos):
        history += f"User: {c.user_input}\nBot: {c.bot_response}\n"

    return history

def get_all_sessions():
    """Retrieve unique session IDs, their last message time, and first message for title."""
    db = SessionLocal()
    try:
        from sqlalchemy import func

        sessions = (
            db.query(
                Conversation.session_id,
                func.max(Conversation.created_at).label("last_active"),
                func.min(Conversation.id).label("first_id")
            )
            .group_by(Conversation.session_id)
            .order_by(func.max(Conversation.created_at).desc())
            .all()
        )

        result = []
        for s in sessions:
            # Fetch the first message text for use as the session title
            first_convo = db.query(Conversation).filter(Conversation.id == s.first_id).first()
            result.append({
                "id": s[0],
                "last_active": s[1],
                "first_message": first_convo.user_input if first_convo else None
            })
        return result
    finally:
        db.close()