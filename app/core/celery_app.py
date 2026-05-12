import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "dag_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.task_track_started = True
celery.conf.result_expires = 3600