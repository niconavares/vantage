import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vantage.settings')

app = Celery('vantage')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'scanner.tasks.*': {'queue': 'scan_queue'},
    'ai.tasks.*': {'queue': 'ai_queue'},
    'reports.tasks.*': {'queue': 'report_queue'},
}
