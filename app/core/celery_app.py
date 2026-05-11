from celery import Celery

celery = Celery(
    "dag_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery.conf.task_track_started = True
celery.conf.result_expires = 3600