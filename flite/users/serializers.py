from rest_framework import serializers
from .models import User, UserProfile, Referral, Account, Transaction
from . import utils

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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class WithdrawalDepositSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=1000_000, decimal_places=2)

    def validated_amount(self, amount):
        if amount < 50:
            raise serializers.ValidationError(
                "Amount specified for deposit is less than the minimum required amount of #50"
            )
        return amount

    def validate_account_number(self, account_number):
        account_exists = Account.objects.filter(account_number=account_number).exists()
        if account_exists:
            return account_number
        else:
            raise serializers.ValidationError(
                "Account number '%s' specified for this user does not exist, please ensure you specify account that belongs to this user only" % account_number
            )


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=1000_000, decimal_places=2)

    def validate_amount(self, amount):
        if amount < 50:
            raise serializers.ValidationError(
                "Amount specified for transfer is less than the minimum required amount of #50"
            )
        return amount


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'