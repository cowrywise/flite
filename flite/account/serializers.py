from rest_framework import serializers
from .models import AllBanks, Bank, Card, \
    CardTransfer, P2PTransfer, BankTransfer
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

