from flite.banks.models import Bank
from rest_framework import serializers


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank


class BankTransferSerializer(serializers.ModelSerializer):
    Bank = BankSerializer()
    owner_details = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "owner",
            "reference",
            "status",
            "amount",
            "new_balance",
            "bank",
            "created",
        ]

    def get_owner_details(self, obj):
        return {
            "username": obj.owner.username,
            "email": obj.owner.email,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
        }
