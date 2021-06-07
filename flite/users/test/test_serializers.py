from uuid import uuid4
from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import eq_, ok_
from ..models import User
from .factories import UserFactory
from ..serializers import UserSerializer, CreateUserSerializer, AccountSerializer, WithdrawalDepositSerializer, TransferSerializer


class TestUserSerializer(TestCase):

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())
        self.user_data.pop('groups')
        self.user_data.pop('user_permissions')
        self.user = User.objects.create(**self.user_data)
    
    def test_serializer_with_empty_data(self):
        serializer = UserSerializer(data={})
        eq_(serializer.is_valid(), True)

    def test_serializer_with_valid_data(self):
        serializer = UserSerializer(instance=self.user)
        # should match same user
        eq_(serializer.data["id"], str(self.user.id))

        serializer = UserSerializer(data=serializer.data)
        ok_(serializer.is_valid())


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


class TestAccountSerializer(TestCase):
    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())
        self.user_data.pop('groups')
        self.user_data.pop('user_permissions')
        self.user = User.objects.create(**self.user_data)

    def test_serializer_with_empty_data(self):
        serializer = AccountSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        account = AccountSerializer(instance=self.user.user_accounts.first())
        serializer = AccountSerializer(data=account.data)
        ok_(serializer.is_valid())

class TestWithdrawalDepositSerializer(TestCase):
    
    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())
        self.user_data.pop('groups')
        self.user_data.pop('user_permissions')
        self.user = User.objects.create(**self.user_data)

    def test_serializer_with_empty_data(self):
        serializer = WithdrawalDepositSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = WithdrawalDepositSerializer(data={"account_number": self.user.user_accounts.first().account_number, "amount": 5000})
        ok_(serializer.is_valid())

    def test_serializer_with_invalid_data(self):
        serializer = WithdrawalDepositSerializer(data={"account_number": uuid4(), "amount": 5000})
        eq_(serializer.is_valid(), False)


class TestTransferSerializer(TestCase):
    
    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_invalid_data(self):
        # invalid data type
        serializer = TransferSerializer(data={"amount": "12"})
        eq_(serializer.is_valid(), False)
        # less than minimum amount
        serializer = TransferSerializer(data={"amount": 30})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        # greater than minimum amount required
        serializer = TransferSerializer(data={"amount": 100})
        ok_(serializer.is_valid())
