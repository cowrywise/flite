import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from flite.core.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)
        Account.objects.create(owner=instance)

class Phonenumber(BaseModel): 
    number = models.CharField(max_length=24)
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    owner_email = models.EmailField()

    class Meta:
        verbose_name = "Phone Number"


class UserProfile(BaseModel):
    referral_code = models.CharField(max_length=120)
    user = models.OneToOneField('users.User',on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_new_referal_code()
        return super(UserProfile, self).save(*args, **kwargs)


    def generate_new_referal_code(self):
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
        return str(self.phone_number)+'-'+ str(self.verification_code)

    class Meta:
        verbose_name_plural = "New User Verification Codes"



class Referral(BaseModel):
    owner = models.OneToOneField('users.User',on_delete=models.CASCADE,related_name="owner")
    referred = models.OneToOneField('users.User',on_delete=models.CASCADE, related_name="referred")

    class Meta:
        verbose_name = "User referral"



