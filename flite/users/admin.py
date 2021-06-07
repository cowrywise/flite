from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, UserProfile, Phonenumber, Balance,
                     NewUserPhoneVerification, Referral)


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
