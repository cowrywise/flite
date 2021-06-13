from rest_framework import serializers
from .models import (Balance, BankTransfer, Card, P2PTransfer, Transaction,
                     User, NewUserPhoneVerification, UserProfile, Referral)
from . import utils
from rest_framework.response import Response
from rest_framework.decorators import action

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
            referral=Referral()
            referral.owner = self.reffered_profile.first().user
            referral.referred = user
            referral.save()
        
        # create 0 balance for new user.
        data = {"owner": user, "book_balance":0.00, "available_balance":0.0}
        serializer = BalanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

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


class DepositWithdrawalSerializer(serializers.Serializer):
    # amount = serializers.DecimalField(max_digits=999999, decimal_places=2)
    amount = serializers.FloatField(max_value=999999999, min_value=1.00)
    reference = serializers.CharField(max_length=250)


class P2PTransferSerializer(serializers.Serializer):
    amount = serializers.FloatField(max_value=999999999, min_value=1.00)
    reference = serializers.CharField(max_length=250)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
