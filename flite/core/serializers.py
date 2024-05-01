# serializers.py
from rest_framework import serializers
from .models import BudgetCategory, Transaction

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'max_spend']

class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField()  # Ensure the amount field is serialized as a float

    class Meta:
        model = Transaction
        fields = ['id', 'owner', 'category', 'amount', 'description', 'date']