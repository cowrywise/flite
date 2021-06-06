import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from flite.core.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from . import constants

@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username

class Referral(BaseModel):
    owner = models.OneToOneField('users.User',on_delete=models.CASCADE,related_name="owner")
    referred = models.OneToOneField('users.User',on_delete=models.CASCADE, related_name="referred")

    class Meta:
        verbose_name = "User referral"

class UserProfile(BaseModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    phone = PhoneNumberField(null=True)
    referral_code = models.CharField(max_length=120)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_new_referal_code()
        return super(UserProfile, self).save(*args, **kwargs)

    def generate_new_referal_code(self):
        """Returns a unique passcode"""
        def _passcode():
            return str(uuid.uuid4().hex)[0:8]
        passcode = _passcode()
        while UserProfile.objects.filter(referral_code=passcode).exists():
            passcode = _passcode()
        return passcode



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        profile = UserProfile.objects.create(user=instance)
        Account.objects.create(
            owner=instance,
            account_name=profile.user.get_full_name(),
            account_number=uuid.uuid4(),
            account_type=constants.SAVINGS
        )


class Account(BaseModel):
    owner = models.ForeignKey('users.User', related_name="user_accounts", on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50, choices=constants.ACCOUNT_TYPES)
    account_balance = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name= "Account"
        verbose_name_plural = "Accounts"


class Transaction(BaseModel):
    owner = models.ForeignKey('users.Account', on_delete=models.CASCADE, editable=False, related_name='transactions')
    transaction_type = models.CharField(max_length=50, editable=False, choices=constants.TRANSACTION_TYPES, null=True)
    transaction_status = models.CharField(max_length=50, editable=False, choices=constants.TRANSACTION_STATUS, default=constants.PENDING)
    transaction_action = models.CharField(max_length=50, editable=False, null=True, choices=constants.TRANSACTION_ACTIONS)
    transaction_journal = models.TextField(editable=False, null=True)
    reference = models.CharField(max_length=200, editable=False, null=True)

    def __str__(self):
        return self.reference
