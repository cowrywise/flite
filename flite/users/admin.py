from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Transaction, Balance, UserProfile


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'referral_code',
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'status',
        'amount',
        'transaction_type',
        'created',
    )


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'available_balance',
        'book_balance',
        'active',
    )
