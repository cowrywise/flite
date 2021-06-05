from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(UserAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    pass