from django.contrib import admin
from .models import (AllBanks, Bank,
                     BankTransfer, P2PTransfer, Card)



@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'bank']
    ordering = ['id']


admin.site.register(AllBanks)
admin.site.register(BankTransfer)
admin.site.register(P2PTransfer)
admin.site.register(Card)

