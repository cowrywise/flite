from django.contrib import admin
from .models import (AllBanks, Bank,
                     BankTransfer, P2PTransfer, Card)


admin.site.register(AllBanks)
admin.site.register(Bank)
admin.site.register(BankTransfer)
admin.site.register(P2PTransfer)
admin.site.register(Card)
