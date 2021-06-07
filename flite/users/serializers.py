from rest_framework import request, serializers
from .models import Transaction, User, NewUserPhoneVerification, UserProfile, Referral, BankTransfer, P2PTransfer
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
        
class BankTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankTransfer
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance')
        read_only_fields = ('owner', 'status', 'new_balance')

    def create(self, validated_data):
        owner = validated_data.get('owner')
        amount = validated_data.get('amount')
        user_balance = owner.balance.first()

        new_balance = round(user_balance.available_balance + amount, 2)
        # determine user's new balance

        user_balance.book_balance = new_balance
        # update user's book balance before tranfer completion

        validated_data['new_balance'] = new_balance
        validated_data['status'] = "SUCCESS"
        validated_data['bank'] = owner.accounts.first()
        validated_data['amount'] = abs(amount) # save amount as the absolute value of itself in the case of a withdrawal
        
        bank_transfer = BankTransfer.objects.create(**validated_data)
        # complete bank transfer 

        user_balance.available_balance = new_balance
        user_balance.save()
        # update and save user's available balance after transfer completion

        return bank_transfer

class P2PTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = P2PTransfer
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance', 'sender', 'recipient')
        read_only_fields = ('status', 'new_balance', 'sender', 'recipient', 'owner')

    def create(self, validated_data):
        sender = validated_data.get('sender')
        recipient = validated_data.get('recipient')
        amount = validated_data.get('amount')

        sender_balance = sender.balance.first()
        recipient_balance = recipient.balance.first()
        # fetch sender and recipient current balances

        new_sender_balance = round(sender_balance.available_balance - amount, 2)
        new_recipient_balance = round(recipient_balance.available_balance + amount, 2)
        # determine sender's and recipient's new balances

        sender_balance.book_balance = new_sender_balance
        recipient_balance.book_balance = new_recipient_balance
        # update sender's and recipient's new balances

        validated_data['new_balance'] = new_sender_balance
        validated_data['status'] = "SUCCESS"
        validated_data['owner']

        p2p_transfer = P2PTransfer.objects.create(**validated_data)
        # complete P2P transfer

        sender_balance.available_balance = new_sender_balance
        recipient_balance.available_balance = new_recipient_balance

        sender_balance.save()
        recipient_balance.save()
        # update and save sender's and recipient's available balances

        return p2p_transfer




class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ('id', 'owner', 'reference', 'status', 'amount', 'new_balance')
        read_only_fields = ('status', 'new_balance', 'owner')
        