from rest_framework import serializers
from .models import AllBanks, Bank, Card, Account,\
    CardTransfer, P2PTransfer, BankTransfer, Transaction
from flite.users.serializers import UserSerializer
from .utils import is_valid_uuid, get_valid_bank, get_valid_card


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


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


class TransactionSerializer(DynamicFieldsModelSerializer):
    
    class Meta:
        model = Transaction
        fields = ('owner', 'reference', 'status', 'trans_type', 'category',
                  'amount', 'charge', 'description')
        read_only_fields = ('reference', 'status', 'charge', 'trans_type',
                            'description')


class WithdrawalSerializer(serializers.Serializer):
    amount =  serializers.FloatField(min_value=100)
    bank = serializers.CharField(help_text="Enter Bank ID (Optional)")

    class Meta:
        fields = ('amount', 'bank')
     
    def validate_bank(self, value):
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank




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
    

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class TransferSerializer(serializers.Serializer):
    amount =  serializers.FloatField(min_value=100)

    class Meta:
        fields = ('amount')
