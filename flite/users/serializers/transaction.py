from django.contrib.auth import get_user_model
from rest_framework import serializers

from flite.users.models import Balance, Transaction, P2PTransfer
from flite.users.utils import TransactionTypes

User = get_user_model()


def get_user(user_id):
    is_available = False
    try:
        user = User.objects.get(id=user_id)
        is_available = True
        return is_available, user
    except User.DoesNotExist:
        return is_available, None


def validate_and_create_balance(owner_id):
    is_user_available, user = get_user(user_id=owner_id)
    if not is_user_available:
        raise serializers.ValidationError({f"{owner_id}": f"User with this {owner_id} does not exist"})
    balance, created = Balance.objects.get_or_create(
        owner=user,
        active=True
    )
    return balance, created, user


class BaseTransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, required=True, decimal_places=2)

    class Meta:
        model = Transaction
        fields = ('amount', 'id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')
        read_only_fields = ('id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')


class CreateDepositSerializer(BaseTransactionSerializer):

    def create(self, validated_data):
        owner_id = self.context.get('user_id', None)
        amount = validated_data.get('amount')
        if owner_id is None:
            raise serializers.ValidationError({"user_id": "user_id is required"})
        balance, created, user = validate_and_create_balance(owner_id)
        balance.credit(amount=amount)
        balance.save()
        transaction = Transaction.objects.create(
            owner=user,
            amount=amount,
            transaction_type=TransactionTypes.DEPOSIT.value,
            new_balance=balance.available_balance
        )
        return transaction


class CreateWithdrawalSerializer(BaseTransactionSerializer):

    def create(self, validated_data):
        owner_id = self.context.get('user_id', None)
        amount = validated_data.get('amount')

        if owner_id is None:
            raise serializers.ValidationError({"user_id": "user_id is required"})

        balance, created, user = validate_and_create_balance(owner_id)
        if created:
            raise serializers.ValidationError({"user_id": "User must first make a deposit"})

        if not balance.can_debit(amount):
            raise serializers.ValidationError({
                "amount": f"Insufficient funds, you can't withdraw more "
                          f"than your available "
                          f"balance which is {balance.available_balance}"
            })

        balance.debit(amount=amount)
        balance.save()
        transaction = Transaction.objects.create(
            owner=user,
            amount=amount,
            transaction_type=TransactionTypes.WITHDRAW.value,
            new_balance=balance.available_balance
        )
        return transaction


class PeerToPeerTransferSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, required=True, decimal_places=2)

    class Meta:
        model = P2PTransfer
        fields = (
            'amount', 'id', 'owner', 'sender',
            'recipient', 'reference', 'status', 'transaction_type',
            'new_balance', 'created'
        )
        read_only_fields = (
            'id', 'owner', 'sender', 'recipient',
            'reference', 'status', 'transaction_type', 'new_balance', 'created'
        )

    def create(self, validated_data):
        sender_account_id = self.context.get('sender_account_id', None)
        recipient_account_id = self.context.get('recipient_account_id', None)
        amount = validated_data.get('amount')

        self.validate_user_id(sender_account_id)
        self.validate_user_id(recipient_account_id)

        sender_balance, sender_balance_created, sender_user = validate_and_create_balance(sender_account_id)
        recipient_balance, recipient_balance_created, recipient_user = validate_and_create_balance(recipient_account_id)

        if sender_balance_created:
            raise serializers.ValidationError({"sender_account_id": "User must first make a deposit"})

        if not sender_balance.can_debit(amount):
            raise serializers.ValidationError({
                "amount": f"Insufficient funds, you can't withdraw more "
                          f"than your available "
                          f"balance which is {sender_balance.available_balance}"
            })

        self.debit_user(sender_balance, amount)
        self.credit_user(recipient_balance, amount)

        peer_to_peer_for_sender = P2PTransfer.objects.create(
            owner=sender_user,
            amount=amount,
            transaction_type=TransactionTypes.PEER_TO_PEER_DEBIT.value,
            new_balance=sender_balance.available_balance,
            sender=sender_user,
            recipient=recipient_user
        )

        P2PTransfer.objects.create(
            owner=recipient_user,
            amount=amount,
            reference=peer_to_peer_for_sender.reference,
            transaction_type=TransactionTypes.PEER_TO_PEER_CREDIT.value,
            new_balance=recipient_balance.available_balance,
            sender=sender_user,
            recipient=recipient_user
        )
        return peer_to_peer_for_sender

    @staticmethod
    def debit_user(balance, amount):
        balance.debit(amount)
        balance.save()

    @staticmethod
    def credit_user(balance, amount):
        balance.credit(amount)
        balance.save()

    @staticmethod
    def validate_user_id(user_id):
        if user_id is None:
            raise serializers.ValidationError({f"{user_id}": f"{user_id} is required"})
