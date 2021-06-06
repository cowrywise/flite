from rest_framework import serializers
from flite.users.models import Balance, Transaction, BankTransfer, P2PTransfer


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = '__all__'


class P2PTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = P2PTransfer
        fields = '__all__'

   
class BankTransferSerializer(serializers.ModelSerializer):
    amount =  serializers.CharField(required=True)
    bank =  serializers.CharField(required=True)

    class Meta:
        model = BankTransfer
        fields = ('amount', 'bank',)

    
class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'
        
    
class WithdrawalSerializer(serializers.Serializer):
    amount =  serializers.CharField(required=True) 