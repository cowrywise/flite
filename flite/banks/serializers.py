from flite.banks.models import Bank
from rest_framework import serializers


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            "id",
            "owner",
            "bank",
            "account_name",
            "account_number",
            "account_type",
        ]
