"""Celery application configuration."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "chess_evaluation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,  # Prevent workers from hoarding tasks
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
)

