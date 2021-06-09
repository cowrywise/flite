from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral, Transaction
from .factories import UserFactory, TransactionFactory, BalanceFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')
        self.url = reverse('user-list')
        self.user_data = model_to_dict(UserFactory.build())

    def test_get_request_returns_all_users(self):
        url = reverse('user-list')
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

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
        self.user_data.update({"referral_code":referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'],owner__username=referring_user.username).exists(),True)


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
    """ Test Transactions, Deposits and Withdrawals """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')
        self.transaction = TransactionFactory()
        self.balance = BalanceFactory()

    def test_user_can_make_a_deposit(self):
        url = reverse('deposits-users-deposits', kwargs={'pk': self.user.pk})
        payload = {'amount': 1000.00}
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_make_a_withdrawal(self):
        owner = self.balance.owner
        url = reverse('deposits-users-withdrawals', kwargs={'pk': owner.pk})
        payload = {'amount': 1000.00}
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_make_a_p2p_transfer(self):
        owner = self.balance.owner
        url = reverse('p2p_transfer', 
        kwargs={'sender_account_id': owner.pk, 'receipient_id': self.user.pk})
        payload = {'amount': 1000.00}
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_all_transactions(self):
        url = reverse('account-transactions', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')
        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        owner = self.transaction.owner
        url = reverse('single_transactions', 
        kwargs={'pk': owner.pk, 'transaction_id': self.transaction.id })
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')
        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction_returns_404(self):
        url = reverse('single_transactions',
        kwargs={'pk': self.user.pk, 'transaction_id': self.transaction.id })
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')
        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_404_NOT_FOUND)
