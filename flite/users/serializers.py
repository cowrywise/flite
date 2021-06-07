from rest_framework import serializers
from .models import User, NewUserPhoneVerification,UserProfile,Referral, Balance, Transaction, P2PTransfer
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

class UserTransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        fields = ['amount']

    def validate(self, attrs):
        txn_type = self.context.get('transaction_type')
        if txn_type == 'withdrawals':
            user = self.context.get('request').user
            if not Balance.objects.filter(owner=user).exists():
                raise serializers.ValidationError(
                    {"error": "user has no valid balance"})
            # find most recent balance
            latest_balance = Balance.objects.filter(
                owner=user).order_by('-modified').first()
            # check that balance > amount
            if latest_balance.available_balance < attrs['amount']:
                raise serializers.ValidationError(
                    {"error": "insufficient funds"})
            return super().validate(attrs)
        return super().validate(attrs)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class P2PTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = P2PTransfer
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'sender',
                            'receipient', 'reference', 'status', 'new balance', 'new_balance']

    def validate(self, attrs):
        # get sender and recpient users validated
        sender_id = self.context.get('sender_id')
        recepient_id = self.context.get('recepient_id')
        # check that sender and recpient exists
        if not User.objects.filter(id=sender_id).exists():
            raise serializers.ValidationError(
                {'error': 'unable to verify sender account'})
        if not User.objects.filter(id=recepient_id).exists():
            raise serializers.ValidationError(
                {'error': 'unable to verify recepient account'})
        # check that sender has sufficient account balance
        sender = User.objects.get(id=sender_id)
        sender_balance = Balance.objects.filter(owner=sender).order_by(
            '-modified').first().available_balance
        if sender_balance < attrs['amount']:
            raise serializers.ValidationError({"error": "insufficient funds"})
        return super().validate(attrs)