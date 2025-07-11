# Celeryアプリを自動的に起動
from .celery import app as celery_app

__all__ = ('celery_app',) 