from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Transfer, Transaction, Withdraw


@receiver(post_save, sender=Transfer)
def get_transfers(sender, instance=None, created=False, **kwargs):
    if created:
        Transaction.objects.create(owner=instance.owner, amount=instance.amount, reference=instance.reference,
                                   status=instance.status)


@receiver(post_save, sender=Withdraw)
def get_withdrawals(sender, instance=None, created=False, **kwargs):
    if created:
        Transaction.objects.create(owner=instance.receiver, amount=instance.amount, reference=instance.reference,
                                   status=instance.status)