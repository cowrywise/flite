from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import *
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

        eq_(Referral.objects.filter(
            referred__username=self.user_data['username'], owner__username=referring_user.username).exists(), True)

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

    def setUp(self):
        sender = User.objects.create(username=fake.user_name(), password=1234, email=fake.email(
        ), first_name=fake.first_name(), last_name=fake.last_name())
        # recipient = User.objects.create(username=fake.user_name(), password=1234, email=fake.email(
        # ), first_name=fake.first_name(), last_name=fake.last_name())
        recipient = User.objects.create(username='john22', password=1234,
                                        email='john@gmail.com', first_name='john', last_name='smith')

        testBank = AllBanks.objects.create(name='access bank', acronym='ABK', bank_code='901')
        sender_account = Bank.objects.create(
            account_name='sender account', account_number='123', account_type='savings', bank=testBank, owner=sender)
        recipient_account = Bank.objects.create(
            account_name='recipient account', account_number='123', account_type='savings', bank=testBank, owner=recipient)

        sender_balance = Balance.objects.get(owner=sender)
        recipient_balance = Balance.objects.get(owner=recipient)

        sender_transaction = Transaction.objects.create(
            owner=sender, amount=1000, status='success', new_balance=4000)

        # assign to class fields
        self.sender = sender
        self.recipient = recipient
        self.sender_balance = sender_balance
        self.recipient_balance = recipient_balance
        self.sender_account = sender_account
        self.recipient_account = recipient_account
        self.sender_transaction = sender_transaction
        self.test_bank = testBank
        self.payload = {'amount': 1000}
        self.withdrawalPayload = {'amount': 200}

        self.deposit_url = f"/api/v1/users/{sender.id}/deposits"
        self.withdrawal_url = f"/api/v1/users/{sender.id}/withdrawals"
        self.p2p_transfer_url = f"/api/v1/account/{sender.id}/transfers/{recipient.id}"
        self.all_transactions_url = f"/api/v1/account/{sender.id}/transactions"
        self.single_transaction_url = f"/api/v1/account/{sender.id}/transactions/{sender_transaction.id}"

    def test_user_can_make_a_deposit(self):
        self.client.force_authenticate(user=self.sender)
        initial_balance = self.sender_balance.book_balance
        res = self.client.post(self.deposit_url, self.payload)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_make_a_withdrawal(self):
        self.client.force_authenticate(user=self.sender)
        initial_balance = self.sender_balance.book_balance
        self.client.post(self.deposit_url, self.payload)
        res = self.client.post(self.withdrawal_url, self.withdrawalPayload)
        eq_(res.status_code, status.HTTP_200_OK)

    # def test_user_can_make_a_p2p_transfer(self):
    #     self.client.force_authenticate(user=self.sender)
    #     res = self.client.post(self.p2p_transfer_url, self.payload)
    #     eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_all_transactions(self):
        self.client.force_authenticate(user=self.sender)
        self.client.post(self.deposit_url, self.payload)
        res = self.client.get(self.all_transactions_url)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        self.client.force_authenticate(user=self.sender)
        res = self.client.get(self.single_transaction_url)
        eq_(res.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.sender.delete()
        self.recipient.delete()
        self.sender_transaction.delete()
        self.test_bank.delete()
