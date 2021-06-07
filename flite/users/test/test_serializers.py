from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import eq_, ok_
from .factories import UserFactory, BankTransferFactory, AllBanksFactory, BankFactory
from ..serializers import CreateUserSerializer, BankTransferSerializer
from faker import Faker

fake = Faker()


class TestCreateUserSerializer(TestCase):
    """
    Tests CreateUserSerializer
    """

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_user_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_user_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

    def test_user_serializer_hashes_password(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

        user = serializer.save()
        ok_(check_password(self.user_data.get('password'), user.password))

class TestBankTransferSerializer(TestCase):
    """
    Tests BankTransferSerializer
    """

    def setUp(self):
        self.bank_transfer_data = model_to_dict(BankTransferFactory.build())
        self.user = UserFactory()
        bank = AllBanksFactory()
        self.user_account = BankFactory(
                                owner=self.user, 
                                bank=bank, 
                                account_name=self.user.get_full_name
                            )
        self.user_balance = self.user.balance.first()
        self.user_balance.available_balance = fake.pyfloat(min_value=300_000, max_value=599_999, right_digits=2)
        self.user_balance.book_balance = fake.pyfloat(min_value=300_000, max_value=599_999, right_digits=2)
        self.user_balance.save()

    def init_bank_transfer(self):
        serializer = BankTransferSerializer(data=self.bank_transfer_data)
        ok_(serializer.is_valid())

        self.bank_transfer = serializer.save(owner=self.user)   

    def test_bank_transfer_serializer_with_empty_data(self):
        serializer = BankTransferSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_bank_transfer_serializer_with_valid_data(self):
        serializer = BankTransferSerializer(data=self.bank_transfer_data)
        ok_(serializer.is_valid())

    def test_bank_transfer_serializer_saves_owner(self):
        self.init_bank_transfer()
        eq_(self.bank_transfer.owner, self.user)

    def test_bank_transfer_serializer_saves_with_success_status(self):
        self.init_bank_transfer()
        eq_(self.bank_transfer.status, "SUCCESS")

    def test_bank_transfer_serializer_saves_bank(self):
        self.init_bank_transfer()
        eq_(self.bank_transfer.bank, self.user_account)

    def test_bank_transfer_serializer_calculates_new_balance(self):
        available = self.user_balance.available_balance
        amount = self.bank_transfer_data['amount']

        balance = round(available + amount, 2)

        self.init_bank_transfer()
        eq_(self.bank_transfer.new_balance, balance)


    
