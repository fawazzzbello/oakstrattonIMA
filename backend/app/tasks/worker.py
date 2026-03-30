from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "oakstratton_ima",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.notifications",
        "app.tasks.metrics_sync",
        "app.tasks.payment_processing",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Sync social metrics every 6 hours
        "sync-social-metrics": {
            "task": "app.tasks.metrics_sync.sync_all_active_campaign_metrics",
            "schedule": 6 * 3600,
        },
        # Check overdue invoices daily at 9am UTC
        "check-overdue-invoices": {
            "task": "app.tasks.payment_processing.mark_overdue_invoices",
            "schedule": 86400,
        },
        # Send upcoming deliverable reminders daily
        "deliverable-reminders": {
            "task": "app.tasks.notifications.send_deliverable_reminders",
            "schedule": 86400,
        },
    },
)
