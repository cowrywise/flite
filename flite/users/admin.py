from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Balance, Transfer, Transaction, Fund


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('owner', 'available_balance', 'active', )


class TransferAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'reference', 'amount', )


class FundAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'reference', 'amount', 'status',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'reference', 'amount', 'balance', 'status',)


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transfer, TransferAdmin)
admin.site.register(Fund, FundAdmin)
admin.site.register(Transaction, TransactionAdmin)
