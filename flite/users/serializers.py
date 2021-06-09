from rest_framework import serializers
from .models import (User, NewUserPhoneVerification,
UserProfile,Referral, Transaction, P2PTransfer, Balance)
from . import utils
from rest_framework.response import Response
from rest_framework import status

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(required=False)


    def validate_referral_code(self, code):
        
        self.reffered_profile = UserProfile.objects.filter(referral_code=code.lower())
        is_valid_code = self.reffered_profile.exists()
        if not is_valid_code:
            raise serializers.ValidationError(
                "Referral code does not exist"
            )
        else:
            return code

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        referral_code = None
        if 'referral_code' in validated_data:
            referral_code = validated_data.pop('referral_code',None)
            
        user = User.objects.create_user(**validated_data)

        if referral_code:
            referral =Referral()
            referral.owner = self.reffered_profile.first().user
            referral.referred = user
            referral.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token','referral_code')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}



class SendNewPhonenumberSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number", None) 
        email = validated_data.get("email", None)

        obj, code = utils.send_mobile_signup_sms(phone_number, email)
        
        return {
            "verification_code":code,
            "id":obj.id
        }

    class Meta:
        model = NewUserPhoneVerification
        fields = ('id', 'phone_number', 'verification_code', 'email',)
        extra_kwargs = {'phone_number': {'write_only': True, 'required':True}, 'email': {'write_only': True}, }
        read_only_fields = ('id', 'verification_code')
        

class TransactionSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    class Meta:
        model = Transaction
        fields = ('id', 'reference', 'status', 'amount','new_balance', 'owner')
        read_only_fields = ('id', 'reference', )

class P2PTransferSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(required=True)
    receipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    class Meta:
        model = P2PTransfer
        fields = ('id', 'sender', 'receipient', 'amount')

    def create(self, validated_data):
        amount = validated_data.pop('amount')
        sender = validated_data.get('sender')
        receipient = validated_data.get('receipient')

        if Balance.objects.filter(owner=sender, active=True).exists():
            sender_balance = Balance.objects.filter(owner=sender).latest('available_balance')
            if sender_balance.available_balance < amount:
                raise serializers.ValidationError(
            "You cannot transfer more than you have in your wallet")
            reference = utils.generate_transaction_reference()
            # Sender
            sender_balance.available_balance = sender_balance.available_balance - amount
            sender_balance.save()
            data = {
                'sender': sender,
                'receipient': receipient,
                'owner':sender,
                'reference':reference,
                'amount': amount,
                'status': "DONE",
                'new_balance': sender_balance.available_balance
            }
            parent = P2PTransfer.objects.create(**data)
            # Update receipient Balance
            receipient_obj, _ = Balance.objects.get_or_create(owner=receipient)
            receipient_obj.available_balance = receipient_obj.available_balance + amount
            receipient_obj.save()
            # create a transaction history for both users
            # Receipient
            Transaction.objects.create(
                owner=receipient,
                reference=reference,
                amount= amount,
                status= "DONE",
                new_balance=receipient_obj.available_balance
            )
            return parent

        raise serializers.ValidationError(
            "Sender has no wallet to send from. Kindly setup a wallet for the sender")

class BalanceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Balance
        fields = ['id', 'owner', 'book_balance', 'available_balance']
        read_only_fields = ['id', ]

class DepositSerializer(BalanceSerializer):
    amount = serializers.FloatField(required=True, write_only=True)

    class Meta(BalanceSerializer.Meta):
        fields = BalanceSerializer.Meta.fields + ['amount']

    def create(self, validated_data):
        amount = validated_data.get('amount')
        owner = validated_data.get('owner')
        owner_bal, _ = Balance.objects.get_or_create(owner=owner)
        owner_bal.available_balance += amount
        reference = utils.generate_transaction_reference()
        Transaction.objects.create(
            owner=owner,
            reference=reference,
            amount= amount,
            status= "DONE",
            new_balance=owner_bal.available_balance
        )
        owner_bal.save()
        return owner_bal

class WithdrawSerializer(BalanceSerializer):
    amount = serializers.FloatField(required=True, write_only=True)

    class Meta(BalanceSerializer.Meta):
        fields = BalanceSerializer.Meta.fields + ['amount']

    def create(self, validated_data):
        amount = validated_data.get('amount')
        owner = validated_data.get('owner')
        if Balance.objects.filter(owner=owner, active=True).exists():
            owner_bal = Balance.objects.filter(
                owner=owner).latest('available_balance')
            if owner_bal.available_balance < amount:
                raise serializers.ValidationError(
            "You cannot send less than your available balance")

            owner_bal.available_balance -= amount
            reference = utils.generate_transaction_reference()
            Transaction.objects.create(
                owner=owner,
                reference=reference,
                amount= amount,
                status= "DONE",
                new_balance=owner_bal.available_balance
            )
            owner_bal.save()
            return owner_bal
        raise serializers.ValidationError(
            "This User has no wallet to withdraw from. Kindly setup a wallet")