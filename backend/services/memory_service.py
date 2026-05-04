import logging
from database import SessionLocal
from models import Conversation

logger = logging.getLogger(__name__)


def save_conversation(user_input: str, bot_response: str) -> None:
    """Persist a user/bot exchange to the database."""
    db = SessionLocal()
    try:
        convo = Conversation(user_input=user_input, bot_response=bot_response)
        db.add(convo)
        db.commit()
        logger.info(
            f"[MEMORY] Saved conversation | input_len={len(user_input)} | response_len={len(bot_response)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[MEMORY] Failed to save conversation: {e}")
        raise
    finally:
        db.close()


def get_history(limit: int = 5) -> str:
    """Retrieve the last `limit` exchanges in chronological order."""
    db = SessionLocal()
    try:
        convos = (
            db.query(Conversation)
            .order_by(Conversation.id.desc())
            .limit(limit)
            .all()
        )
        logger.info(f"[MEMORY] Retrieved {len(convos)} history entries")
    except Exception as e:
        logger.error(f"[MEMORY] Failed to retrieve history: {e}")
        return ""
    finally:
        db.close()

    history = ""
    for c in reversed(convos):
        history += f"User: {c.user_input}\nBot: {c.bot_response}\n"

    return history