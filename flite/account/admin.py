from django.contrib import admin
from .models import (Balance, AllBanks, Bank,
                     BankTransfer, P2PTransfer, Card)


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'book_balance', 'available_balance', 'active']
    ordering = ['-created']


admin.site.register(AllBanks)
admin.site.register(Bank)
admin.site.register(BankTransfer)
admin.site.register(P2PTransfer)
admin.site.register(Card)
