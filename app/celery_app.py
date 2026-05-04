import os

from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

celery_app = Celery(
    "movie_booking",
    broker=CELERY_BROKER_URL,
    include=["app.payment_task"],
)

celery_app.conf.timezone = "Asia/Bangkok"
celery_app.conf.beat_schedule = {
    "scan-pending-payments-every-minute": {
        "task": "scan_pending_payments",
        "schedule": 60,
    },
}
