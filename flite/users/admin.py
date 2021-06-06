from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


admin.site.register(AllBanks)
admin.site.register(Bank)


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


@admin.register(P2PTransfer)
class P2PTransferAdmin(admin.ModelAdmin):
    list_display = (
        'sender',
        'receipient',  
        'amount',      
    )
    search_fields = ('sender', 'receipient')
    readonly_fields = ('amount', 'new_balance')
    list_filter = ('created', 'modified',)


@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = (       
        'owner',  
        'amount',  
        'bank',    
    )
    search_fields = ('sender', 'receipient')
    readonly_fields = ('amount', 'new_balance')
    list_filter = ('created', 'modified',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'status',  
        'amount', 
        'created',     
    )
   

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'active',       
    )
