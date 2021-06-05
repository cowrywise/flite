from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, UserProfile, Phonenumber,
                     NewUserPhoneVerification, Referral, Balance,
                     AllBanks, Bank, Transaction, BankTransfer,
                     P2PTransfer, Card)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'username', 'date_joined']
    ordering = ['-date_joined']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'referral_code', 'created', 'modified']
    ordering = ['-created']

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'book_balance', 'available_balance', 'active']
    ordering = ['-created']

admin.site.register(Phonenumber)
admin.site.register(NewUserPhoneVerification)
admin.site.register(Referral)
admin.site.register(AllBanks)
admin.site.register(Bank)
admin.site.register(Transaction)
admin.site.register(BankTransfer)
admin.site.register(P2PTransfer)
admin.site.register(Card)