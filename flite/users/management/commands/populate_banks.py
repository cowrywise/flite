from django.core.management.base import BaseCommand
from flite.users.models import AllBanks
from paystackapi.misc import Misc


class Command(BaseCommand):
    help = 'Populate model with all banks'

    def handle(self, *args, **kwargs):
        list_banks = []
        banks = Misc.list_banks()
        for bank in banks['data']:
            list_banks.append(bank)
        for i in list_banks:
            AllBanks.objects.bulk_create([AllBanks(name=i['name'], acronym=i['slug'], bank_code=i['code'])])