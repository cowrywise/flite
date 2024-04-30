from configurations import Configuration
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import logging
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flite.core'

    def ready(self):
        from .models import Transaction
        from .tasks import check_budget_threshold

        @receiver(post_save, sender=Transaction)
        def run_check_budget_threshold(sender, instance, **kwargs):
            print("run_check_budget_threshold signal triggered") 
            logging.info("run_check_budget_threshold signal triggered")
            transaction.on_commit(lambda: check_budget_threshold.delay(instance.id))
            
