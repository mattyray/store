# Import Celery app so Django loads it and uses correct broker settings
from .celery import app as celery_app

__all__ = ('celery_app',)
