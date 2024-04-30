from __future__ import absolute_import
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flite.config.local")
os.environ.setdefault('DJANGO_CONFIGURATION', 'Local')
import configurations
configurations.setup()

app = Celery('flite')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
