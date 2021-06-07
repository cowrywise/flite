from django.contrib.auth import get_user_model
from rest_framework import serializers

from flite.users.models import Balance, Transaction
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


class BaseDepositWithdrawalSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, required=True, decimal_places=2)

    class Meta:
        model = Transaction
        fields = ('amount', 'id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')
        read_only_fields = ('id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')

    @staticmethod
    def validate_and_create_balance(validated_data, owner_id):
        amount = validated_data.get('amount')
        is_user_available, user = get_user(user_id=owner_id)
        if not is_user_available:
            raise serializers.ValidationError({"user_id": "User with this user_id does not exist"})
        balance, created = Balance.objects.get_or_create(
            owner=user,
            active=True
        )
        return amount, balance, created, user


class CreateDepositSerializer(BaseDepositWithdrawalSerializer):

    def create(self, validated_data):
        owner_id = self.context.get('user_id', None)
        if owner_id is None:
            raise serializers.ValidationError({"user_id": "user_id is required"})
        amount, balance, created, user = self.validate_and_create_balance(validated_data, owner_id)
        balance.credit(amount=amount)
        balance.save()
        transaction = Transaction.objects.create(
            owner=user,
            amount=amount,
            transaction_type=TransactionTypes.DEPOSIT.value,
            new_balance=balance.available_balance
        )
        return transaction


class CreateWithdrawalSerializer(BaseDepositWithdrawalSerializer):

    def create(self, validated_data):
        owner_id = self.context.get('user_id', None)
        if owner_id is None:
            raise serializers.ValidationError({"user_id": "user_id is required"})
        amount, balance, created, user = self.validate_and_create_balance(validated_data, owner_id)
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
