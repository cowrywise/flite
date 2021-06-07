from rest_framework import serializers
from flite.banks.serializers import BankSerializer
from flite.dynamic_serializer import DynamicFieldsModelSerializer
from flite.transfers.models import BankTransfer
from flite.transfers.wallets import UserWallet
from rest_framework import serializers


class BankTransferSerializer(DynamicFieldsModelSerializer):
    banking_details = BankSerializer(read_only=True, source="bank")
    reference = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = BankTransfer
        fields = [
            "id",
            "owner",
            "reference",
            "status",
            "amount",
            "transaction_type",
            "bank",
            "new_balance",
            "banking_details",
            "created",
        ]
        extra_kwargs = {"amount": {"required": True}}

    def validate_amount(self, value):
        user = self.context.get("request").user
        if UserWallet.has_enough_funds(user, value):
            return value
        raise serializers.ValidationError("Insufficient Funds")
