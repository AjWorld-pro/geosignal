import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geosignal.settings')

USE_CELERY = os.environ.get('USE_CELERY', 'False').lower() in ('true', '1', 'yes')

if USE_CELERY:
    from celery import Celery
    app = Celery('geosignal')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
