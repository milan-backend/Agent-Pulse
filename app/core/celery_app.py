import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "dag_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.broker_use_ssl = {
    "ssl_cert_reqs": "none"
}

celery.conf.redis_backend_use_ssl = {
    "ssl_cert_reqs" : "none"
}

celery.autodiscover_tasks(["app.tasks"])

celery.conf.task_track_started = True
celery.conf.result_expires = 3600