from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from flite.core.models import BaseModel

User = settings.AUTH_USER_MODEL


def verify_number(value: str) -> None:
    """ Validate if an input string is a digit(number).

    Args:
        value: The string of numbers to be verified.

    Exceptions:
        ValidationError: It raises validation error if
        the string is not a valid number
    """
    if not value.isdigit():
        raise ValidationError('please enter a valid number')


class Account(BaseModel):
    """ A model to represent user accounts

    It holds details of the user account and is created
    automatically during user registration

    Relationships:
        Foreignkey: owner(User)
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book_balance = models.FloatField(default=0.0)
    available_balance = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"{self.id}"


class AllBanks(BaseModel):
    """ A model to represent all approved banks

    This model instances are considered to be approved
    banks that flite(company) can successfully transact
    with.
    """

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
    """A model to represent user personal banks.

    Instances of this model are user banks linked to
    the flite wallet. Users can only deposit and withdraw
    from these banks.

    Relationships:
        Foreignkey: owner(User), bank(AllBanks)
    """

    type_options = [('Savings', 'Savings'), ('Current', 'Current'),
                    ('Corporate', 'Corporate'), ('Joint', 'Joint')]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(AllBanks, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(
        max_length=50,
        validators=[verify_number],
    )
    account_type = models.CharField(
        max_length=50,
        choices=type_options,
        default='Savings')

    class Meta:
        ordering = ["account_name"]

    def __str__(self):
        return self.account_name


class Transaction(BaseModel):
    """ A model to represent user transactions.

    This model is the base model for all transactions.
    It contains common fields and method to be shared
    by P2Ptransfer, BankTransfer and CardTransfer transactions

    Relationships:
        Foreignkey: owner(User)
    """

    status_options = [('Pending', 'Pending'), ('Successful', 'Successful'),
                      ('Cancelled', 'Cancelled'), ('Rejected', 'Rejected')]
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
        User,
        on_delete=models.CASCADE,
        related_name='transaction')
    status = models.CharField(
        max_length=10,
        choices=status_options,
        default='Successful')
    trans_type = models.CharField(
        max_length=8,
        choices=type_options,
        default='Deposit')
    category = models.CharField(
        max_length=6,
        choices=category_options,
        default='Credit')
    amount = models.FloatField(default=0.0)
    charge = models.FloatField(default=0.0)
    description = models.TextField()
    reference = models.CharField(max_length=12)

    def __str__(self):
        return f"Transaction {self.reference}"

    class Meta:
        ordering = ["-created"]


class CardTransfer(Transaction):
    """ A model to represent user card transactons.

    This model inherits from Transaction models.
    All cardtransactions will be instance of this model

    Relationships:
        Foreignkey: card(Card)
    """
    card = models.ForeignKey("Card", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.trans_type = 'Deposit'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Card Transfers"


class BankTransfer(Transaction):
    """ A model to represent bank transfer.

    This model inherits from Transaction models.
    All bank transactions will be instance of this model

    Relationships:
        Foreignkey: bank(card)
   """
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Bank Transfers"


class P2PTransfer(Transaction):
    """ A model to represent peer-to-peer transfer.

    This model inherits from Transaction models.
    All p2p transactions will be instance of this model

    Relationships:
        Foreignkey: receipient(account)
    """
    receipient = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="recipient")

    class Meta:
        verbose_name_plural = "P2P Transfers"


class Card(BaseModel):
    """ A model to represent user personal cards.

    Instances of this model are user cards linked to
    the flite wallet. Users can only deposit using this
    cards.

    Relationships:
        Foreignkey: owner(User)
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=200)
    ctype = models.CharField(max_length=200)
    cbin = models.CharField(max_length=200, null=True)
    cbrand = models.CharField(max_length=200, null=True)
    country_code = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(
        max_length=200,
        validators=[verify_number],
    )
    bank = models.CharField(max_length=200)
    expiry_month = models.CharField(
        max_length=2,
        validators=[verify_number],
        help_text="MM")
    expiry_year = models.CharField(
        max_length=4,
        validators=[verify_number],
        help_text="YYYY")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.number

    def delete(self):
        self.is_active = False
        self.is_deleted = True
        self.save()
