from django.contrib import admin
from .models import BudgetCategory,Transaction

admin.site.register(BudgetCategory)
admin.site.register(Transaction)
