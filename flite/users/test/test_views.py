from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from faker import Faker
from ..models import User, UserProfile, Referral, Balance, Transaction
from .factories import UserFactory
from ..serializers import BaseTransactionSerializer

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


def deposit_url(user_id):
    """
    Return deposit url
    """
    return reverse('transaction-deposit-list', args=[user_id])


def withdrawal_url(user_id):
    """
    Return withdrawal url
    """
    return reverse('transaction-withdrawal-list', args=[user_id])


def transfer_url(sender_account_id, recipient_account_id):
    """
    Return transfer url
    """
    return reverse('peer_to_peer_transfer-list', args=[sender_account_id, recipient_account_id])


def transactions_url(account_id):
    """
    Return transaction list url
    """
    return reverse('transaction-list', args=[account_id])


def single_transaction_url(account_id, transaction_id):
    """
    Return a transaction detail url
    """
    return reverse('transaction-detail', args=[account_id, transaction_id])


def sample_user(username='username', email='user@example.com', password='password'):
    """
    create a sample user
    """
    return User.objects.create_user(username, email, password)


def sample_update_balance_for_user(user, amount):
    balance = Balance.objects.filter(owner=user).first()
    balance.available_balance = amount
    balance.book_balance = amount
    balance.save()
    return balance


class TestTransactions(APITestCase):

    def setUp(self):
        self.user_one = sample_user(username='username_one',
                                    email='user_one@example.com',
                                    password='password')
        self.user_two = sample_user(username='username_two',
                                    email='user_two@example.com',
                                    password='password')
        self.client_one = APIClient()
        self.client_two = APIClient()
        self.client_one.force_authenticate(self.user_one)
        self.client_two.force_authenticate(self.user_two)

    def tearDown(self):
        self.user_one.delete()
        self.user_two.delete()

    def test_user_can_make_a_deposit(self):
        payload = {'amount': 1000.00}
        url = deposit_url(self.user_one.id)
        res = self.client_one.post(url, payload)
        balance = Balance.objects.filter(owner=self.user_one.id).first()
        eq_(balance.available_balance, 1000.00)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_not_make_a_deposit_with_invalid_user_id(self):
        payload = {'amount': 1000.00}
        url = deposit_url('a09d27e8-870d-4fa9-a999-70eeeeeeeee2')
        res = self.client_one.post(url, payload)
        eq_(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_make_a_withdrawal(self):
        sample_update_balance_for_user(self.user_two, 1000.00)
        payload = {'amount': 500.00}
        url = withdrawal_url(self.user_two.id)
        res = self.client_two.post(url, payload)
        balance = Balance.objects.filter(owner=self.user_two).first()
        eq_(balance.available_balance, 500.00)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_not_make_a_withdrawal_with_zero_balance(self):
        payload = {'amount': 1000.00}
        balance = Balance.objects.filter(owner=self.user_two.id).first()
        url = withdrawal_url(self.user_two.id)
        res = self.client_two.post(url, payload)
        eq_(balance.available_balance, 0.00)
        eq_(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_not_make_a_withdrawal_with_account_that_is_not_yours(self):
        payload = {'amount': 1000.00}
        amount = 1000.00
        sample_balance_for_user_two = sample_update_balance_for_user(self.user_two, amount)
        url = withdrawal_url(self.user_two.id)
        res = self.client_one.post(url, payload)
        eq_(res.status_code, status.HTTP_403_FORBIDDEN)
        eq_(sample_balance_for_user_two.available_balance, amount)

    def test_user_can_make_a_p2p_transfer(self):
        sample_update_balance_for_user(self.user_one, 1000.00)
        sample_update_balance_for_user(self.user_two, 2000.00)

        payload_amount_to_transfer = {'amount': 500.00}
        url = transfer_url(self.user_one.id, self.user_two.id)
        res = self.client_one.post(url, payload_amount_to_transfer)  # transfer from self.user_one to self.user_2

        user_one_balance = Balance.objects.filter(owner=self.user_one.id).first()
        user_two_balance = Balance.objects.filter(owner=self.user_two.id).first()

        eq_(res.status_code, status.HTTP_200_OK)
        eq_(user_one_balance.available_balance, 500.00)
        eq_(user_two_balance.available_balance, 2500.00)

    def test_user_can_not_make_a_p2p_transfer_due_to_insufficient_funds(self):
        sample_one_user_balance_before_request = sample_update_balance_for_user(self.user_one, 1000.00)
        sample_two_user_balance_before_request = sample_update_balance_for_user(self.user_two, 2000.00)

        payload_amount_to_transfer = {'amount': 1100.00}  # amount to transfer is higher than user_one
        url = transfer_url(self.user_one.id, self.user_two.id)
        res = self.client_one.post(url, payload_amount_to_transfer)  # transfer from self.user_one to self.user_2

        user_one_balance = Balance.objects.filter(owner=self.user_one.id).first()
        user_two_balance = Balance.objects.filter(owner=self.user_two.id).first()

        eq_(res.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(user_one_balance.available_balance, sample_one_user_balance_before_request.available_balance)
        eq_(user_two_balance.available_balance, sample_two_user_balance_before_request.available_balance)

    def test_user_can_not_make_a_p2p_transfer_from_an_account_that_is_not_theirs(self):
        sample_one_user_balance_before_request = sample_update_balance_for_user(self.user_one, 1000.00)
        sample_two_user_balance_before_request = sample_update_balance_for_user(self.user_two, 2000.00)

        payload_amount_to_transfer = {'amount': 500.00}  # amount to transfer is higher than user_one
        url = transfer_url(self.user_two.id, self.user_one.id)  # sender_account_id is user_two instead of user_one
        res = self.client_one.post(url, payload_amount_to_transfer)  # transfer from self.user_one to self.user_2

        user_one_balance = Balance.objects.filter(owner=self.user_one.id).first()
        user_two_balance = Balance.objects.filter(owner=self.user_two.id).first()

        eq_(res.status_code, status.HTTP_403_FORBIDDEN)
        eq_(user_one_balance.available_balance, sample_one_user_balance_before_request.available_balance)
        eq_(user_two_balance.available_balance, sample_two_user_balance_before_request.available_balance)

    def test_user_can_fetch_all_transactions(self):
        self.perform_a_transaction(self.user_one.id)
        self.perform_a_transaction(self.user_one.id)
        self.perform_a_transaction(self.user_two.id)

        url = transactions_url(self.user_one.id)
        url_two = transactions_url(self.user_two.id)

        res = self.client_one.get(url)
        res_two = self.client_two.get(url_two)

        user_one_transactions = Transaction.objects.filter(owner__id=self.user_one.id)
        user_two_transactions = Transaction.objects.filter(owner__id=self.user_two.id)

        serializer = BaseTransactionSerializer(user_one_transactions, many=True)
        serializer_two = BaseTransactionSerializer(user_two_transactions, many=True)

        eq_(res.status_code, status.HTTP_200_OK)
        eq_(res_two.status_code, status.HTTP_200_OK)

        eq_(len(res.data.get('results')), 2)
        eq_(len(res_two.data.get('results')), 1)

        eq_(res.data.get('results'), serializer.data)
        eq_(res_two.data.get('results'), serializer_two.data)

    def perform_a_transaction(self, user_id):
        payload = {'amount': 1000.00}
        url = deposit_url(user_id)
        return self.client_one.post(url, payload)

    def test_user_can_not_fetch_all_transactions_that_does_not_belong_to_them(self):
        self.perform_a_transaction(self.user_one.id)
        self.perform_a_transaction(self.user_one.id)
        self.perform_a_transaction(self.user_two.id)

        url = transactions_url(self.user_one.id)
        res = self.client_two.get(url)

        eq_(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_fetch_a_single_transaction(self):
        _ = self.perform_a_transaction(self.user_one.id)
        user_one_second_transaction = self.perform_a_transaction(self.user_one.id)

        url = single_transaction_url(self.user_one.id, user_one_second_transaction.data.get('id'))
        res = self.client_one.get(url)

        user_one_transactions = Transaction.objects.filter(owner__id=self.user_one.id).first()
        serializer = BaseTransactionSerializer(user_one_transactions, many=False)

        eq_(res.status_code, status.HTTP_200_OK)
        eq_(res.data, serializer.data)

    def test_user_can_not_fetch_a_single_transaction_that_is_not_theirs(self):
        user_two_transaction = self.perform_a_transaction(self.user_two.id)

        url = single_transaction_url(self.user_two.id, user_two_transaction.data.get('id'))
        res = self.client_one.get(url)

        eq_(res.status_code, status.HTTP_403_FORBIDDEN)
