from flite.banks.serializers import BankSerializer
from flite.dynamic_serializer import DynamicFieldsModelSerializer
from flite.transfers.checks import TransferManager
from flite.transfers.models import BankTransfer, P2PTransfer, Transaction
from flite.transfers.wallets import UserWallet
from flite.users.serializers import UserSerializer
from rest_framework import serializers


class BankWithdrawalSerializer(DynamicFieldsModelSerializer):
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


class BankDepositSerializer(DynamicFieldsModelSerializer):
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


class P2PTransferSerializer(DynamicFieldsModelSerializer):
    recipient_details = UserSerializer(read_only=True, source="recipient")
    sender_details = UserSerializer(read_only=True, source="sender")


    class Meta:
        model = P2PTransfer
        fields = [
            "id",
            "owner",
            "reference",
            "status",
            "amount",
            "recipient_details",
            "sender_details",
            "new_balance",
            "created",
            "sender",
            "recipient",
        ]
        extra_kwargs = {"amount": {"required": True}}

    def validate_amount(self, value):
        user = self.context.get("request").user
        if UserWallet.has_enough_funds(user, value):
            return value
        raise serializers.ValidationError("Insufficient Funds")

    def validate(self, attrs):
        checks = TransferManager.run_checks(**attrs)
        if checks.get("success") is False:
            raise serializers.ValidationError(checks.get("message"))
        return attrs


class TransferSerializer(DynamicFieldsModelSerializer):
    owner_details = UserSerializer(read_only=True, source="owner")

    class Meta:
        model = Transaction
        fields = [
            "id",
            "owner",
            "owner_details",
            "reference",
            "status",
            "amount",
            "new_balance",
            "created",
        ]
