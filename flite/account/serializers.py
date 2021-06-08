from rest_framework import serializers
from .models import AllBanks, Bank, Card, \
    CardTransfer, P2PTransfer, BankTransfer, Transaction
from flite.users.serializers import UserSerializer


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
        if not value.isdigit:
            raise serializers.ValidationError(
        '''Please enter a valid Bank ID(int).''')

        owner = self.context.get('request').user
        bank = Bank.objects.filter(owner=owner, id=value).first()
        if not bank:
            raise serializers.ValidationError(
        '''We care about the safety of your funds so we will only transfer to
        a verified bank you own. Please add a verified bank to proceed. .''')
        return bank



    class Meta:
        model = BankTransfer
        fields = ('bank', 'owner', 'reference', 'status', 'trans_type', 
        'amount', 'charge',)
        read_only_fields = ('reference', 'status', 'charge', 'trans_type') 