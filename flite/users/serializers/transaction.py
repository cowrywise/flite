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


class CreateDepositSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, required=True, decimal_places=2)

    class Meta:
        model = Transaction
        fields = ('amount', 'id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')
        read_only_fields = ('id', 'owner', 'reference', 'status', 'transaction_type', 'new_balance', 'created')

    def create(self, validated_data):
        amount = validated_data.get('amount')
        owner_id = self.context.get('user_id', None)
        if owner_id is None:
            raise serializers.ValidationError({"user_id": "user_id is required"})

        is_user_available, user = get_user(user_id=owner_id)
        if not is_user_available:
            raise serializers.ValidationError({"user_id": "User with this user_id does not exist"})
        balance, created = Balance.objects.get_or_create(
            owner=user,
            active=True
        )
        balance.credit(amount=amount)
        balance.save()
        transaction = Transaction.objects.create(
            owner=user,
            amount=amount,
            transaction_type=TransactionTypes.DEPOSIT.value,
            new_balance=balance.available_balance
        )
        return transaction
