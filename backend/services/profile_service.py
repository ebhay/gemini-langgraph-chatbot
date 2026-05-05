import logging
import json
from database import SessionLocal
from models import UserProfile

logger = logging.getLogger(__name__)


def get_user_profile(user_id: int) -> dict:
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return {}
        
        result = {
            "age": profile.age,
            "city": profile.city,
            "country": profile.country,
            "occupation": profile.occupation,
            "interests": profile.interests,
            "preferences": profile.preferences,
        }
        
        if profile.additional_data:
            try:
                additional = json.loads(profile.additional_data)
                result.update(additional)
            except:
                pass
        
        return {k: v for k, v in result.items() if v is not None}
    except Exception as e:
        logger.error(f"[PROFILE] Failed to fetch profile for user {user_id}: {e}")
        return {}
    finally:
        db.close()


def update_user_profile(user_id: int, key: str, value: str):
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
        
        standard_fields = ["age", "city", "country", "occupation", "interests", "preferences"]
        
        if key in standard_fields:
            if key == "age":
                try:
                    setattr(profile, key, int(value))
                except:
                    setattr(profile, key, None)
            else:
                setattr(profile, key, value)
        else:
            additional_data = {}
            if profile.additional_data:
                try:
                    additional_data = json.loads(profile.additional_data)
                except:
                    pass
            additional_data[key] = value
            profile.additional_data = json.dumps(additional_data)
        
        db.commit()
        logger.info(f"[PROFILE] Updated {key} for user {user_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"[PROFILE] Failed to update profile for user {user_id}: {e}")
    finally:
        db.close()


def create_user_profile(user_id: int) -> UserProfile:
    db = SessionLocal()
    try:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        logger.error(f"[PROFILE] Failed to create profile for user {user_id}: {e}")
        raise
    finally:
        db.close()
