from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from flite.core.models import BaseModel
from django.utils import timezone
from .utils import randomStringDigits


User = settings.AUTH_USER_MODEL


class AllBanks(BaseModel):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Approved Banks"
        verbose_name = "Approved Bank"
        ordering = ["name"]
     


class Bank(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(AllBanks, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50)

    class Meta:
        ordering = ["account_name"]

    def __str__(self):
        return self.account_name
     


class Transaction(BaseModel):
    status_options = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
    ]
    type_options = [
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw'),

    ]
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",)
    reference = models.CharField(max_length=10, unique=True, default=randomStringDigits())
    status = models.CharField(max_length=9, choices=status_options, default='Pending')
    trans_type = models.CharField(max_length=8, choices=type_options, default='Incoming')
    amount = models.FloatField(default=0.0)
    charge = models.FloatField(default=0.0)

    def __str__(self):
        return f"Transaction {reference}"

    class Meta:
        ordering = ["-created"]


class CardTransfer(Transaction):
    card = models.ForeignKey("Card", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.trans_type = 'Incoming'
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Card Transfers"


class BankTransfer(Transaction):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Bank Transfers"


class P2PTransfer(Transaction):
    receipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")

    class Meta:
        verbose_name_plural = "P2P Transfers"


class Card(BaseModel):

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=200)
    ctype = models.CharField(max_length=200)
    cbin = models.CharField(max_length=200, null=True)
    cbrand = models.CharField(max_length=200, null=True)
    country_code = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=200)
    bank = models.CharField(max_length=200)
    expiry_month = models.CharField(max_length=2, help_text="MM")
    expiry_year = models.CharField(max_length=4, help_text="YYYY")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return self.number

    def delete(self):
        self.is_active = False
        self.is_deleted = True
        self.save()
