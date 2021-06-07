from rest_framework import serializers
from flite.banks.serializers import BankSerializer
from flite.dynamic_serializer import DynamicFieldsModelSerializer
from flite.transfers.models import BankTransfer


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
