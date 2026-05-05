from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
from database import SessionLocal
from models import Notification, User
from services.email_service import send_notification_email

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()


def send_notification(user_id: int, message: str):
    logger.info(f"[SCHEDULER] Task complete for user {user_id}: {message}")
    
    db = SessionLocal()
    try:
        notif = Notification(user_id=user_id, message=message, notification_type="reminder")
        db.add(notif)
        db.commit()
        
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            email_sent = send_notification_email(user.email, user.username, message)
            if email_sent:
                notif.is_emailed = True
                db.commit()
                logger.info(f"[SCHEDULER] Email sent to {user.email}")
    except Exception as e:
        db.rollback()
        logger.error(f"[SCHEDULER] Failed to save notification for user {user_id}: {e}")
    finally:
        db.close()


def schedule_task(user_id: int, message: str, delay: int = 10):
    run_time = time.time() + delay
    run_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_time))

    scheduler.add_job(
        send_notification,
        'date',
        run_date=run_date,
        args=[user_id, message]
    )
    logger.info(f"[SCHEDULER] Task scheduled in {delay}s for user {user_id}: {message}")