from rest_framework import serializers
from .models import *
from . import utils
from django.db.models import F

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

class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = ('id', 'book_balance', 'available_balance')
        
class WithdrawalSerializer(serializers.Serializer):

    amount = serializers.FloatField()

    def validate_amount(self, amount):
        """
        Validates The Amount Entered By The User.
        """
        if amount <= 0.0:
            raise serializers.ValidationError("Invalid Amount")
        user = self.context["request"].user
        balance = Balance.objects.get(owner=user)
        if balance.available_balance < amount:
            raise serializers.ValidationError("Insufficient Balance")
        else:
            return amount

    def create(self, validated_data):
        """
        Removes Amount to User Balance and Saves User Transaction.
        """

        user = self.context["request"].user
        balance = Balance.objects.get(owner=user)
        balance.book_balance = F('book_balance') - validated_data.get("amount")
        balance.available_balance = F('available_balance') - validated_data.get("amount")
        balance.save()
        balance.refresh_from_db()
        transaction = Transaction(
            owner=user,
            status="success",
            amount=validated_data.get("amount"),
            new_balance=balance.book_balance
        )
        transaction.save()
        return balance

class DepositSerializer(serializers.Serializer):

    amount = serializers.FloatField()

    def validate_amount(self, amount):
        """
        Validates the Amount Entered By the User.
        """
        if amount <= 0.0:
            raise serializers.ValidationError("Invalid Amount")
        else:
            return amount

    def create(self, validated_data):
        """
        Adds Amount to User Balance and Saves User Transaction.
        """

        user = self.context["request"].user
        balance = Balance.objects.get(owner=user)
        balance.book_balance = F('book_balance') + validated_data.get("amount")
        balance.available_balance = F('available_balance') + validated_data.get("amount")
        balance.save()
        balance.refresh_from_db()
        transaction = Transaction(
            owner=user,
            status="success",
            amount=validated_data.get("amount"),
            new_balance=balance.book_balance
        )
        transaction.save()
        return balance

class TransferSerializer(serializers.Serializer):

    amount = serializers.FloatField()

    def validate_amount(self, amount):
        """
        Validates Transfer Amount.
        """
        if amount <= 0.0:
            raise serializers.ValidationError("Invalid Amount")
        sender = self.context["request"].user
        balance = Balance.objects.get(owner=sender)
        if balance.available_balance < amount:
            raise serializers.ValidationError("Insufficient Balance")
        else:
            return amount

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = "__all__"

class P2PTransferSerializer(serializers.ModelSerializer):

    sender = serializers.SerializerMethodField()
    receipient = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return obj.sender.get_full_name()
    
    def get_receipient(self, obj):
        return obj.receipient.get_full_name()

    class Meta:
        model = P2PTransfer
        fields = "__all__"
