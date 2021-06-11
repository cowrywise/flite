from rest_framework import serializers
from django.conf import settings
from django.http import JsonResponse
from paystackapi.paystack import Paystack
from .models import User, NewUserPhoneVerification, UserProfile, Referral, Balance, Transfer, BankAccount, Withdraw, \
    Card, Transaction, Fund, AllBanks
from . import utils


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)
        read_only_fields = ('username',)


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
            referral_code = validated_data.pop('referral_code', None)

        user = User.objects.create_user(**validated_data)

        if referral_code:
            referral = Referral()
            referral.owner = self.reffered_profile.first().user
            referral.referred = user
            referral.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token', 'referral_code')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}


class SendNewPhonenumberSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number", None)
        email = validated_data.get("email", None)

        obj, code = utils.send_mobile_signup_sms(phone_number, email)

        return {
            "verification_code": code,
            "id": obj.id
        }

    class Meta:
        model = NewUserPhoneVerification
        fields = ('id', 'phone_number', 'verification_code', 'email',)
        extra_kwargs = {'phone_number': {'write_only': True, 'required': True}, 'email': {'write_only': True}, }
        read_only_fields = ('id', 'verification_code')


class BalanceSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner_name')

    class Meta:
        model = Balance
        fields = ('id', 'owner', 'available_balance', 'active')

    def get_owner_name(self, request):
        name = request.owner.username
        return name


class BanksSerializer(serializers.ModelSerializer):

    class Meta:
        model = AllBanks
        fields = ('acronym', 'name', 'bank_code', 'id')


class CreateBankAccountSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner_name')

    class Meta:
        model = BankAccount
        fields = ('account_name', 'account_number', 'owner', 'bank')

    def get_owner_name(self, request):
        owner = request.owner.username
        return owner

    def get_bank_name(self, request):
        owner = request.bank.name
        return owner

    def post(self, request, validated_data):
        account_name = validated_data['account_name']
        account_number = validated_data['account_number']
        bank = validated_data['bank']
        single_bank = AllBanks.objects.get(id=bank.id)
        paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
        response = paystack.verification.verify_account(account_number=account_number,
                                                        bank_code=single_bank.bank_code)
        if response['status']:
            bank = BankAccount.objects.create(account_name=account_name, account_number=account_number,
                                              owner=request.user.id, bank=single_bank.id)
            bank.save()
            return bank


class TransferSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField('get_receiver_name')
    sender = serializers.SerializerMethodField('get_sender_name')

    class Meta:
        model = Transfer
        fields = ('date_created', 'reference', 'transfer_type', 'amount', 'sender', 'receiver')

    def get_sender_name(self, request):
        name = request.sender.username
        return name

    def get_receiver_name(self, request):
        name = request.receiver.username
        return name


#class FundAccountSerializer(serializers.ModelSerializer):
#    receiver = serializers.SerializerMethodField('get_owner_name')
#
#    class Meta:
#        model = Fund
#        fields = ('date_created', 'reference', 'amount', 'receiver', 'status', )
#
#    def get_owner_name(self, request):
#        owner = request.receiver.username
#        return owner

#    def post(self, request, validated_data):
#        amount = validated_data['amount']
#        paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
#        receiver_acct = BankAccount.objects.get(owner=request.user)
#        response = paystack.charge.start_charge(email=receiver_acct.owner.email, amount=amount, bank={'code':
#                                                receiver_acct.bank.bank_code, 'account_number':
#                                                receiver_acct.account_number})
#        charge_response = paystack.charge.submit_pin(pin="0987", reference=response['data']['reference'], )
#        if response.status_code == 200:
#            fund_made = Fund.objects.create(receiver=request.user, amount=amount,
#                                            reference=charge_response['data']['reference'],
#                                            status=charge_response['data']['status'],
#                                            transfer_type='Card')
#            fund_made.save()
#            if fund_made == 'SUCCESS':
#                receiver_balance = Balance.objects.get(owner=request.user)
#                receiver_balance += fund_made.amount
#                receiver_balance.save()
#            owner = request.user
#            authorization_code = charge_response['data']['authorization']['authorization_code']
#            ctype = charge_response['data']['authorization']['card_type']
#            cbin = charge_response['data']['authorization']['bin']
#            cbrand = charge_response['data']['authorization']['brand']
#            country_code = charge_response['data']['authorization']['country_code']
#            number = charge_response['data']['number']
#            bank = charge_response['data']['authorization']['bank']
#            expiry_month = charge_response['data']['authorization']['expiry_month']
#            expiry_year = charge_response['data']['authorization']['expiry_year']
#            card_details = Card.objects.create(owner=owner, authorization_code=authorization_code, ctype=ctype,
#                                               cbin=cbin, cbrand=cbrand, country_code=country_code, number=number,
#                                               bank=bank, expiry_month=expiry_month, expiry_year=expiry_year, )
#            card_details.save()
#            return fund_made


class FundAccountSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField('get_owner_name')

    class Meta:
        model = Fund
        fields = ('date_created', 'reference', 'amount', 'receiver', )

    def get_owner_name(self, request):
        owner = request.receiver.username
        return owner


class WithdrawFundsSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField('get_owner_name')

    class Meta:
        model = Withdraw
        fields = ('date_created', 'reference', 'amount', 'receiver', 'status')

    def get_owner_name(self, request):
        owner = request.receiver.username
        return owner


class TransactionSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_sender_name')

    class Meta:
        model = Transaction
        fields = ('date_created', 'reference', 'amount', 'owner', 'status', 'balance')

    def get_owner(self, request):
        owner = request.owner.username
        return owner
