# backend/tasks.py
from backend.worker import celery

@celery.task
def sample_task(x, y):
    return x + y