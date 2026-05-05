import logging
from database import SessionLocal
from models import EpisodicMemory
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


def save_episodic_memory(user_id: int, session_id: str, event_summary: str, event_type: str = "conversation", importance_score: float = 0.5):
    """Save an episodic memory (specific event/conversation)"""
    db = SessionLocal()
    try:
        memory = EpisodicMemory(
            user_id=user_id,
            session_id=session_id,
            event_summary=event_summary,
            event_type=event_type,
            importance_score=importance_score
        )
        db.add(memory)
        db.commit()
        logger.info(f"[EPISODIC] Saved memory for user {user_id}: {event_summary[:50]}...")
    except Exception as e:
        db.rollback()
        logger.error(f"[EPISODIC] Failed to save memory: {e}")
    finally:
        db.close()


def get_episodic_memories(user_id: int, limit: int = 10, min_importance: float = 0.3):
    """Retrieve episodic memories for a user, ordered by importance and recency"""
    db = SessionLocal()
    try:
        memories = (
            db.query(EpisodicMemory)
            .filter(
                EpisodicMemory.user_id == user_id,
                EpisodicMemory.importance_score >= min_importance
            )
            .order_by(EpisodicMemory.importance_score.desc(), EpisodicMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "summary": m.event_summary,
                "type": m.event_type,
                "importance": m.importance_score,
                "date": m.created_at.strftime("%Y-%m-%d")
            }
            for m in memories
        ]
    except Exception as e:
        logger.error(f"[EPISODIC] Failed to retrieve memories: {e}")
        return []
    finally:
        db.close()


def get_recent_episodic_memories(user_id: int, days: int = 7, limit: int = 5):
    """Get recent episodic memories from the last N days"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        memories = (
            db.query(EpisodicMemory)
            .filter(
                EpisodicMemory.user_id == user_id,
                EpisodicMemory.created_at >= cutoff_date
            )
            .order_by(EpisodicMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "summary": m.event_summary,
                "type": m.event_type,
                "date": m.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for m in memories
        ]
    except Exception as e:
        logger.error(f"[EPISODIC] Failed to retrieve recent memories: {e}")
        return []
    finally:
        db.close()


def summarize_session_to_episodic(user_id: int, session_id: str):
    """
    Summarize a conversation session into an episodic memory.
    This should be called when a session ends or reaches a certain length.
    """
    from services.memory_service import get_history
    
    history = get_history(user_id, session_id=session_id, limit=20)
    
    if not history or len(history) < 50:
        return  # Not enough content to summarize
    
    # Extract key topics/events from the conversation
    # In a production system, you might use an LLM to generate this summary
    lines = history.split('\n')
    user_messages = [line for line in lines if line.startswith('User:')]
    
    if len(user_messages) > 0:
        # Simple summary: first and last user messages
        first_msg = user_messages[0].replace('User:', '').strip()
        last_msg = user_messages[-1].replace('User:', '').strip()
        
        summary = f"Conversation about: {first_msg[:100]}"
        if len(user_messages) > 1:
            summary += f" ... {last_msg[:100]}"
        
        # Calculate importance based on conversation length
        importance = min(0.9, 0.3 + (len(user_messages) * 0.05))
        
        save_episodic_memory(
            user_id=user_id,
            session_id=session_id,
            event_summary=summary,
            event_type="conversation",
            importance_score=importance
        )
        logger.info(f"[EPISODIC] Created session summary for user {user_id}, session {session_id}")
