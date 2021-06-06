from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from flite.core.models import BaseModel
from django.utils import timezone
from .utils import randomStringDigits


User = settings.AUTH_USER_MODEL

class Balance(BaseModel):

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book_balance = models.FloatField(default=0.0)
    available_balance = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balances"


class AllBanks(BaseModel):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "All Banks"


class Bank(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(AllBanks, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50)


class Transaction(BaseModel):
    status_options = [
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('cancel', 'cancel'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="%(app_label)s_%(class)s_related",
                              related_query_name="%(app_label)s_%(class)ss",)
    reference = models.CharField(max_length=10, unique=True, default=randomStringDigits())
    status = models.CharField(max_length=9, choices=status_options, default='pending',)
    amount = models.FloatField(default=0.0)
    new_balance = models.FloatField(default=0.0)

    class Meta:
        abstract = True


class BankTransfer(Transaction):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Bank Transfers"


class P2PTransfer(Transaction):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")

    class Meta:
        verbose_name_plural = "P2P Transfers"


class Card(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=200)
    ctype = models.CharField(max_length=200)
    cbin = models.CharField(max_length=200, default=None)
    cbrand = models.CharField(max_length=200, default=None)
    country_code = models.CharField(max_length=200, default=None)
    first_name = models.CharField(max_length=200, default=None)
    last_name = models.CharField(max_length=200, default=None)
    number = models.CharField(max_length=200)
    bank = models.CharField(max_length=200)
    expiry_month = models.CharField(max_length=10)
    expiry_year = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.number

    def delete(self):
        self.is_active = False
        self.is_deleted = True
        self.save()
