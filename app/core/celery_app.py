import os
from celery import Celery
from app.tasks.step_tasks import process_step
import ssl

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "dag_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.broker_use_ssl = {

    "ssl_cert_reqs": ssl.CERT_NONE
}

celery.conf.backend_use_ssl ={
    "ssl_cert_reqs": ssl.CERT_NONE
}



celery.conf.task_ignore_result = True
celery.conf.task_track_started = True
celery.conf.result_expires = 3600