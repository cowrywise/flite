from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import eq_, ok_
from .factories import UserFactory, FundFactory, WithdrawFactory, TransferFactory, TransactionFactory
from ..serializers import CreateUserSerializer, FundAccountSerializer, TransferSerializer, WithdrawFundsSerializer


class TestCreateUserSerializer(TestCase):

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

    def test_serializer_hashes_password(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

        user = serializer.save()
        ok_(check_password(self.user_data.get('password'), user.password))


class TestFundSerializer(TestCase):

    def setUp(self):
        self.fund_data = model_to_dict(FundFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = FundAccountSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = FundAccountSerializer(data=self.fund_data)
        ok_(serializer.is_valid())


class TestTransferSerializer(TestCase):

    def setUp(self):
        self.transfer_data = model_to_dict(TransferFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = TransferSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = TransferSerializer(data=self.transfer_data)
        ok_(serializer.is_valid())


class TestWithdrawSerializer(TestCase):

    def setUp(self):
        self.withdraw_data = model_to_dict(WithdrawFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = WithdrawFundsSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = WithdrawFundsSerializer(data=self.withdraw_data)
        ok_(serializer.is_valid())
