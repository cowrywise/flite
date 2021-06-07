from django.db import models

from django.conf import settings
from flite.core.models import BaseModel


class AllBanks(BaseModel):

    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=50)

    def __str__(self):
        return self.name

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

    def __str__(self):
        return "{}'s {} account".format(self.owner, self.bank)
