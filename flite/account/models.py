from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from flite.core.models import BaseModel
from django.utils import timezone
from .utils import randomStringDigits


User = settings.AUTH_USER_MODEL


def verify_number(value):
    if not value.isdigit():
        raise ValidationError('please enter a valid number')


class Account(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book_balance = models.FloatField(default=0.0)
    available_balance = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"



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

    type_options = [
        ('Savings', 'Savings'),
        ('Current', 'Current'),
        ('Corporate', 'Corporate'),
        ('Joint', 'Joint')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(AllBanks, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, validators=[verify_number],)
    account_type = models.CharField(max_length=50, choices=type_options, default='Savings')

    class Meta:
        ordering = ["account_name"]

    def __str__(self):
        return self.account_name
     


class Transaction(BaseModel):
    status_options = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected')
    ]
    type_options = [
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw'),
        ('Transfer', 'Transfer'),
    ]
    category_options = [
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    ]
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name='transaction')
    status = models.CharField(max_length=10, choices=status_options, default='Successful')
    trans_type = models.CharField(max_length=8, choices=type_options, default='Deposit')
    category = models.CharField(max_length=6, choices=category_options, default='Credit')
    amount = models.FloatField(default=0.0)
    charge = models.FloatField(default=0.0)
    description = models.TextField()
    reference = models.CharField(max_length=12)

    def __str__(self):
        return f"Transaction {self.reference}"

    class Meta:
        ordering = ["-created"]


class CardTransfer(Transaction):
    card = models.ForeignKey("Card", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.trans_type = 'Deposit'
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
    number = models.CharField(max_length=200, validators=[verify_number],)
    bank = models.CharField(max_length=200)
    expiry_month = models.CharField(max_length=2, validators=[verify_number], help_text="MM")
    expiry_year = models.CharField(max_length=4, validators=[verify_number], help_text="YYYY")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return self.number

    def delete(self):
        self.is_active = False
        self.is_deleted = True
        self.save()
