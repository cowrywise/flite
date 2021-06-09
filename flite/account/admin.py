from django.contrib import admin
from .models import (AllBanks, Bank, Account, Transaction,
                     BankTransfer, P2PTransfer, Card, CardTransfer)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'bank']
    ordering = ['id']

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'number']
    ordering = ['id']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'book_balance', 'available_balance', 'active']
    ordering = ['-created']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'amount']
    ordering = ['-created']


@admin.register(P2PTransfer)
class P2PTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'amount', 'receipient']
    ordering = ['-created']

admin.site.register(AllBanks)
admin.site.register(BankTransfer)
admin.site.register(CardTransfer)

