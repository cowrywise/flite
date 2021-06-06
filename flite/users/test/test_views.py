from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User, UserProfile, Referral, Transaction, P2PTransfer
from .factories import UserFactory

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

        eq_(UserProfile.objects.filter(user__username=self.user_data['username']).exists(), True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(self):
        referring_user = UserFactory()
        self.user_data.update({"referral_code": referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'],
                                    owner__username=referring_user.username).exists(), True)

    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(self):
        self.user_data.update({"referral_code": "FAKECODE"})
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
    """
    Tests /users/:user_id/deposits operations.
    Tests /users/:user_id/withdrawals operations.
    Tests /account/ operations
    """

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()

        self.transaction = Transaction.objects.create(
            owner=self.user, reference='deposit', amount=100, status='deposited'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_user_can_make_a_deposit(self):
        payload = {'amount': 10.50}
        url = reverse('transaction-deposits', kwargs={'user_id': self.user.pk})
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        transaction = Transaction.objects.latest()
        eq_(transaction.amount, payload['amount'])
        eq_(transaction.status, 'deposited')

    def test_user_can_make_a_withdrawal(self):
        payload = {'amount': 10.50}
        url = reverse('transaction-withdrawals', kwargs={'user_id': self.user.pk})
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        transaction = Transaction.objects.latest()
        eq_(transaction.amount, -payload['amount'])
        eq_(transaction.status, 'withdrawn')

    def test_user_with_empty_balance_can_make_a_withdrawal(self):
        payload = {'amount': 10.50}
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user2.auth_token}')

        url = reverse('transaction-withdrawals', kwargs={'user_id': self.user2.pk})
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_make_a_p2p_transfer(self):
        payload = {'amount': 10.50}
        url = reverse(
            'account-p2p-transfer',
            kwargs={
                'sender_account_id': self.user.pk,
                'recipient_account_id': self.user2.pk
            }
        )
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user_transaction = Transaction.objects.filter(owner=self.user).latest()
        user2_transaction = Transaction.objects.filter(owner=self.user2).latest()

        p2p_transfer = P2PTransfer.objects.latest()

        eq_(user_transaction.amount, -payload['amount'])
        eq_(user2_transaction.amount, payload['amount'])

        ok_(p2p_transfer.sender, self.user)
        ok_(p2p_transfer.recipient, self.user2)

    def test_user_can_fetch_all_transactions(self):
        url = reverse('transaction-fetch-all-transactions', kwargs={'account_id': self.user.pk})
        response = self.client.get(url)

        eq_(response.status_code, status.HTTP_200_OK)
        ok_(response.data['results'][0]['id'], self.transaction.id)

    def test_user_can_fetch_a_single_transaction(self):
        url = reverse(
            'transaction-fetch-a-single-transaction',
            kwargs={'account_id': self.user.pk, 'transaction_id': self.transaction.pk}
        )
        response = self.client.get(url)

        eq_(response.status_code, status.HTTP_200_OK)
        ok_(response.data['id'], self.transaction.id)
