"""Celery application — scheduled AQI polling and alert dispatch."""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "cleanair",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.aqi_fetch", "app.workers.alert_dispatch"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        # Fetch AQI for all active user locations every 5 minutes
        "fetch-aqi-all-locations": {
            "task": "app.workers.aqi_fetch.fetch_all_active_locations",
            "schedule": settings.AQI_FETCH_INTERVAL_SECONDS,
        },
        # Check alert thresholds every 10 minutes
        "check-alert-thresholds": {
            "task": "app.workers.alert_dispatch.check_and_dispatch_alerts",
            "schedule": 600,
        },
        # Aggregate community stats daily at 1 AM IST
        "aggregate-community-stats": {
            "task": "app.workers.alert_dispatch.aggregate_community_stats",
            "schedule": crontab(hour=1, minute=0),
        },
    },
)

