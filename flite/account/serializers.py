from rest_framework import serializers

from .models import (Account, AllBanks, Bank, BankTransfer, Card, CardTransfer,
                     P2PTransfer, Transaction)
from .utils import get_valid_bank, get_valid_card


class AllBanksSerializer(serializers.ModelSerializer):
    """An AllBanks ModelSerializer controls which fields should be displayed."""

    class Meta:
        model = AllBanks
        fields = ('id', 'name', 'acronym', 'bank_code')


class BankSerializer(serializers.ModelSerializer):
    """A Bank ModelSerializer controls which fields should be displayed."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Bank
        fields = ('owner', 'bank', 'account_name', 'account_number',
                  'account_type')


class CardSerializer(serializers.ModelSerializer):
    """A Card ModelSerializer controls which fields should be displayed."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Card
        fields = (
            'owner',
            'authorization_code',
            'ctype',
            'cbrand',
            'country_code',
            'name',
            'bank',
            'number',
            'is_active',
        )


class CardTransferSerializer(serializers.ModelSerializer):
    """A CardTransfer ModelSerializer controls which fields should be displayed."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CardTransfer
        fields = ('owner', 'reference', 'status', 'trans_type', 'amount',
                  'charge', 'card')
        read_only_fields = ('reference', 'status', 'charge')


class P2PTransferSerializer(serializers.ModelSerializer):
    """A P2P Transfer ModelSerializer controls which fields should be displayed."""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = P2PTransfer
        fields = ('owner', 'reference', 'status', 'category', 'trans_type',
                  'amount', 'charge', 'receipient')
        read_only_fields = ('reference', 'status', 'charge', 'trans_type')


class BankTransferSerializer(serializers.ModelSerializer):
    """A BankTransfer ModelSerializer controls which fields should be displayed."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bank = serializers.CharField(help_text="Enter Bank ID")

    def validate_bank(self, value: str) -> Bank:
        """ Validate a bank ID and returns bank instance.

        Args:
            value: The id of the bank to be validated

        Returns:
            bank: Bank instance with 'value' ID
        """
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank

    class Meta:
        model = BankTransfer
        fields = (
            'bank',
            'owner',
            'reference',
            'status',
            'trans_type',
            'amount',
            'charge',
        )
        read_only_fields = ('reference', 'status', 'charge', 'trans_type')


class TransactionSerializer(serializers.ModelSerializer):
    """A Transaction ModelSerializer controls which fields should be displayed."""

    class Meta:
        model = Transaction
        fields = ('id', 'owner', 'reference', 'status', 'trans_type',
                  'category', 'amount', 'charge', 'description')
        read_only_fields = ('id', 'reference', 'status', 'charge',
                            'trans_type', 'description')


class WithdrawalSerializer(serializers.Serializer):
    """A Withdrawal Serializer controls which fields should be displayed."""

    amount = serializers.FloatField(min_value=100)
    bank = serializers.CharField(help_text="Enter Bank ID (Optional)")

    class Meta:
        fields = ('amount', 'bank')

    def validate_bank(self, value):
        """ Validate a bank ID and returns bank instance.

        Args:
            value: The id of the bank to be validated

        Returns:
            bank: Bank instance with 'value' ID
        """
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank


class DepositSerializer(serializers.Serializer):
    """A Deposit Serializer controls which fields should be displayed."""

    amount = serializers.FloatField(min_value=100)
    card = serializers.CharField(help_text="Enter Card ID (Optional)",
                                 required=False)
    bank = serializers.CharField(help_text="Enter Bank ID (Optional)",
                                 required=False)

    class Meta:
        fields = ('amount', 'card', 'bank')

    def validate(self, data):
        """ Validate and return user inputed deposit data.

        Args:
            data: A dictionary containing data to be validated

        Returns:
            data: Validated Data
        """
        card = data.get('card')
        bank = data.get('bank')
        if bank and card:
            raise serializers.ValidationError(
                "Oops!, We aren't sure about the transaction method you want to use. \
                please enter either a card or bank to credit account")
        if bank is None and card is None:
            raise serializers.ValidationError("Oops!, Transaction failed. \
                please enter either a card or bank to credit account")
        return data

    def validate_bank(self, value):
        """ Validate a bank ID and returns bank instance.

        Args:
            value: The id of the bank to be validated

        Returns:
            bank: Bank instance with 'value' ID
        """
        owner = self.context.get('request').user
        bank = get_valid_bank(Bank, owner, value)
        return bank

    def validate_card(self, value):
        """ Validate a card ID and returns card instance.

        Args:
            value: The id of the card to be validated

        Returns:
            card: Card instance with 'value' ID
        """
        owner = self.context.get('request').user
        card = get_valid_card(Card, owner, value)
        return card


class AccountSerializer(serializers.ModelSerializer):
    """A Account ModelSerializer controls which fields should be displayed."""

    class Meta:
        model = Account
        fields = '__all__'


class TransferSerializer(serializers.Serializer):
    """A Transfer Serializer controls which fields should be displayed."""

    amount = serializers.FloatField(min_value=100)

    class Meta:
        fields = ('amount')
