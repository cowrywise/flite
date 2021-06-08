from django.conf import settings
from django.db import models

from flite.core.models import BaseModel
from django.utils import timezone


class AllBanks(BaseModel):

    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "All Banks"

    def __str__(self):
        return self.name


class Bank(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank = models.ForeignKey(AllBanks, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return "{}'s {} account".format(self.owner, self.bank)
