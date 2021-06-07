import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save, pre_save
from rest_framework.authtoken.models import Token
from flite.core.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

from flite.users.utils import TransactionTypes, TransactionStatus, transaction_reference_generator

MINIMAL_BALANCE = 0


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)
        Balance.objects.create(owner=instance)


class Phonenumber(BaseModel):
    number = models.CharField(max_length=24)
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    owner_email = models.EmailField()

    class Meta:
        verbose_name = "Phone Number"


class UserProfile(BaseModel):
    referral_code = models.CharField(max_length=120)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_new_referral_code()
        return super(UserProfile, self).save(*args, **kwargs)

    @staticmethod
    def generate_new_referral_code():
        """
        Returns a unique passcode
        """

        def _passcode():
            return str(uuid.uuid4().hex)[0:8]

        passcode = _passcode()
        while UserProfile.objects.filter(referral_code=passcode).exists():
            passcode = _passcode()
        return passcode


class NewUserPhoneVerification(BaseModel):
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    verification_code = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    email = models.CharField(max_length=100)

    def __str__(self):
        return str(self.phone_number) + '-' + str(self.verification_code)

    class Meta:
        verbose_name_plural = "New User Verification Codes"


class Referral(BaseModel):
    owner = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name="owner")
    referred = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name="referred")

    class Meta:
        verbose_name = "User referral"


class Balance(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balances"

    def can_debit(self, amount):
        return self.available_balance > MINIMAL_BALANCE and self.available_balance >= amount

    def debit(self, amount):
        if self.can_debit(amount):
            self.available_balance -= amount
            self.book_balance -= amount

    def credit(self, amount):
        self.available_balance += amount
        self.book_balance += amount


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction')
    reference = models.CharField(max_length=200)
    status = models.CharField(max_length=200,
                              choices=TransactionStatus.choices(),
                              default=TransactionStatus.SUCCESSFUL.value,
                              help_text="status of transaction performed")
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=100,
                                        choices=TransactionTypes.choices(),
                                        null=True,
                                        blank=True,
                                        help_text="type of transaction performed")
    new_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Transaction for {self.owner.username} and transaction type of {self.transaction_type}"

    def get_customer_transaction_type_label(self):
        return TransactionTypes(self.transaction_type).name.title()

    def get_customer_transaction_status_label(self):
        return TransactionTypes(self.status).name.title()


@receiver(pre_save, sender=Transaction)
def create_reference_key(sender,
                         instance: Transaction,
                         **kwargs):
    """
    pre-save a reference in Transaction
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if not instance.reference:
        instance.reference = transaction_reference_generator(instance)


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
