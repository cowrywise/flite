from rest_framework import serializers
from .models import BudgetCategory, Transaction

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'max_spend']

class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # Use DecimalField instead of FloatField

    class Meta:
        model = Transaction
        fields = ['id', 'owner', 'category', 'amount', 'description', 'date']
