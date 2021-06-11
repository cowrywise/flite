from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Balance, Transaction


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', ]


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['owner', 'available_balance', 'created', ]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['owner', 'reference', 'status', 'new_balance' ]
