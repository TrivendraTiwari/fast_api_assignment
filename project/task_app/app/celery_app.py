from celery import Celery
from task_app.app.services_config.config import *


celery = Celery(
    "worker",
    broker= REDIS_URL, 
    backend= REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Kolkata',    
    enable_utc=True,
)
celery.autodiscover_tasks(packages=["task_app.app.bg_tasks.email_tasks"])

