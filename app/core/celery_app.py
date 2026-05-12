import os
from celery import Celery
from app.tasks.step_tasks import process_step

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

celery.conf.broker_connection_retry_on_startup = True
celery.conf.broker_connection_retry = True
celery.conf.broker_connection_max_retries = None
celery.conf.redis_socket_keepalive = True

celery.conf.task_ignore_result = True
celery.conf.task_track_started = True
celery.conf.result_expires = 3600