from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
from database import SessionLocal
from models import Notification

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

def send_notification(message):
    """Triggered when a background task completes."""
    logger.info(f"[SCHEDULER] Task complete: {message}")
    
    # Save to DB so frontend can fetch it
    db = SessionLocal()
    try:
        notif = Notification(message=message)
        db.add(notif)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[SCHEDULER] Failed to save notification: {e}")
    finally:
        db.close()

def schedule_task(message, delay=10):
    """Schedules a job to run after a specific delay."""
    run_time = time.time() + delay
    
    # Format run_date for APScheduler
    run_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_time))

    scheduler.add_job(
        send_notification,
        'date',
        run_date=run_date,
        args=[message]
    )
    logger.info(f"[SCHEDULER] Task scheduled in {delay}s: {message}")