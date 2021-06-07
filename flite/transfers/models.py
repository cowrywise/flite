from django.db import models
from django.conf import settings
from flite.banks.models import Bank
from flite.core.models import BaseModel
from flite.constants import TRANSACTION_TYPE

# Create your models here.


class Transaction(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transaction"
    )
    reference = models.CharField(max_length=200)
    status = models.CharField(
        max_length=200, help_text="was this transaction successful, pending or failed"
    )
    amount = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)


class BankTransfer(Transaction):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=200, default=TRANSACTION_TYPE["CREDIT"]
    )

    class Meta:
        verbose_name_plural = "Bank Transfers"


class P2PTransfer(Transaction):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipient"
    )

    class Meta:
        verbose_name_plural = "P2P Transfers"
