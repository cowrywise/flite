from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, P2PTransfer, Transaction


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


admin.site.register(Transaction)
admin.site.register(P2PTransfer)
