from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User, UserProfile, Referral
from .factories import UserFactory, BalanceFactory, TransactionFactory, TransferFactory, FundFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.user_data = model_to_dict(UserFactory.build())

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=response.data.get('id'))
        eq_(user.username, self.user_data.get('username'))
        ok_(check_password(self.user_data.get('password'), user.password))

    def test_post_request_with_valid_data_succeeds_and_profile_is_created(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(UserProfile.objects.filter(user__username=self.user_data['username']).exists(),True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(self):
        
        referring_user = UserFactory()
        self.user_data.update({"referral_code": referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'], owner__username=referring_user.username).exists(), True)

    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(self):
        
        self.user_data.update({"referral_code":"FAKECODE"})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

        
class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        new_first_name = fake.first_name()
        payload = {'first_name': new_first_name}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.user.id)
        eq_(user.first_name, new_first_name)


class TestTransactions(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.balance = BalanceFactory()
        self.balance_data = model_to_dict(BalanceFactory.build())
        self.transfer = TransferFactory()
        self.transfer_data = model_to_dict(TransferFactory.build())
        self.fund = FundFactory()
        self.fund_data = model_to_dict(FundFactory.build())
        self.transaction = TransactionFactory()
        self.transaction_data = model_to_dict(TransactionFactory.build())
        self.fund_url = reverse('fund_account', kwargs={'user_id': self.user.id})
        self.transfer_url = reverse('transfer_funds', kwargs={'user_id': self.user.id})
        self.withdraw_url = reverse('withdraw_funds', kwargs={'user_id': self.user.id})
        self.balance_url = reverse('get_balance', kwargs={'user_id': self.user.id})
        self.single_transaction_url = reverse('view_account_transaction', kwargs={'balance_id': self.balance.id, 'transaction_id': self.transaction.id})
        self.transaction_url = reverse('all_accounts_transaction', kwargs={'balance_id': self.balance.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_user_can_make_a_deposit(self):
        response = self.client.post(self.fund_url, self.fund_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_withdrawal(self):
        response = self.client.post(self.withdraw_url, self.withdraw_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_p2p_transfer(self):
        response = self.client.post(self.transfer_url, self.transfer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_fetch_all_transactions(self):
        response = self.client.get(self.transaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        response = self.client.get(self.single_transaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

