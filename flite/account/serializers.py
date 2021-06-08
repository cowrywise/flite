from rest_framework import serializers
from .models import AllBanks, Bank, Card, \
    CardTransfer, P2PTransfer, BankTransfer, Transaction
from flite.users.serializers import UserSerializer
from .utils import is_valid_uuid, get_valid_bank, get_valid_card


class AllBanksSerializer(serializers.ModelSerializer):

    class Meta:
        model = AllBanks
        fields = ('id', 'name', 'acronym', 'bank_code')


class BankSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Bank
        fields = ('owner', 'bank', 'account_name', 'account_number', 'account_type')


class CardSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Card
        fields = ('owner', 'authorization_code', 'ctype', 'cbrand',
                  'country_code', 'name', 'bank', 'number', 'is_active',)


class CardTransferSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CardTransfer
        fields = ('owner', 'reference', 'status', 'trans_type',
                  'amount', 'charge', 'card')
        read_only_fields = ('reference', 'status', 'charge')


class P2PTransferSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = P2PTransfer
        fields = ('owner', 'reference', 'status', 'trans_type',
                  'amount', 'charge', 'receipient')
        read_only_fields = ('reference', 'status', 'charge', 'trans_type')

class BankTransferSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.CharField(help_text="Enter Bank ID")

    def validate_bank(self, value):
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank

    class Meta:
        model = BankTransfer
        fields = ('bank', 'owner', 'reference', 'status', 'trans_type',
                  'amount', 'charge',)
        read_only_fields = ('reference', 'status', 'charge', 'trans_type')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('owner', 'reference', 'status', 'trans_type',
                  'amount', 'charge', 'description')
        read_only_fields = ('reference', 'status', 'charge', 'trans_type',
                            'description')


class DepositSerializer(serializers.Serializer):
    amount =  serializers.FloatField(min_value=100)
    card = serializers.CharField(help_text="Enter Card ID (Optional)", required=False)
    bank = serializers.CharField(help_text="Enter Bank ID (Optional)", required=False)

    class Meta:
        fields = ('amount', 'card', 'bank')
     
    def validate(self, data):
        card = data.get('card')
        bank = data.get('bank')
        if bank and card:
            raise serializers.ValidationError(
                "Oops!, We aren't sure about the transaction method you want to use. \
                please enter either a card or bank to credit account"
            )
        if bank is None and card is None:
            raise serializers.ValidationError(
                "Oops!, Transaction failed. \
                please enter either a card or bank to credit account"
            )
        return data

    def validate_bank(self, value):
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank

    def validate_card(self, value):
        owner = self.context.get('request').user
        card = get_valid_card(Card, owner, value)
        return card
