from django.apps import AppConfig
from django.db.models.signals import post_save

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flite.core'

    def ready(self):
        from .models import Transaction
        from .tasks import check_budget_threshold_signal

        post_save.connect(check_budget_threshold_signal, sender=Transaction)