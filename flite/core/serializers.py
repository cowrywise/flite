from rest_framework import serializers
from .models import BudgetCategory, Transaction

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'max_spend']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'description', 'owner', 'date']
        depth = 1