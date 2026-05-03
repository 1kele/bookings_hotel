from celery import Celery
from celery.schedules import crontab

from src.config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.BROKER_URL,
    include=[
        "src.tasks.tasks",
    ],
)

celery_instance.conf.beat_schedule = {
    "pofig_booking": {
        "task": "booking_today_checkin",
        "schedule": crontab(hour=11, minute=40),
    }
}
