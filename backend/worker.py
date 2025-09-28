from celery import Celery
import os

# Read broker from env
CELERY_BROKER_URL = os.getenv("CELERY_BROKER", "redis://redis:6379/0")
CELERY_BACKEND = os.getenv("CELERY_BACKEND", "rpc://")

celery = Celery(
    "cloud9_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND,
    include=["backend.tasks"],  # <- you can create tasks.py for async jobs
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery.task
def debug_task(msg):
    print(f"⚡ Celery debug task says: {msg}")
