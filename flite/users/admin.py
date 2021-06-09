from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,  Transaction, Balance, P2PTransfer


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


admin.site.register(Transaction)
admin.site.register(Balance)
admin.site.register(P2PTransfer)