from rest_framework import serializers
from .models import BudgetCategory, Transaction

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'max_spend']
        read_only_fields = ['owner']

class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'description', 'date']
        read_only_fields = ['owner']