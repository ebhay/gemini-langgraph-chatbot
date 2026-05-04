from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()
scheduler.start()

def send_notification(message):
    print(f"[NOTIFICATION]: {message}")

def schedule_task(message, delay=10):
    run_time = time.time() + delay

    scheduler.add_job(
        send_notification,
        'date',
        run_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(run_time)),
        args=[message]
    )