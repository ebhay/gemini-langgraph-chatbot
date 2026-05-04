import logging
from database import SessionLocal
from models import UserProfile

logger = logging.getLogger(__name__)

def get_user_profile() -> dict:
    """Fetch all user facts from the DB and return as a dict."""
    db = SessionLocal()
    try:
        profiles = db.query(UserProfile).all()
        return {p.key: p.value for p in profiles}
    except Exception as e:
        logger.error(f"[PROFILE] Failed to fetch profile: {e}")
        return {}
    finally:
        db.close()

def update_user_profile(key: str, value: str):
    """Update or create a user profile fact."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.key == key).first()
        if profile:
            profile.value = value
        else:
            profile = UserProfile(key=key, value=value)
            db.add(profile)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[PROFILE] Failed to update profile key {key}: {e}")
    finally:
        db.close()
