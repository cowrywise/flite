from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from faker import Faker
from ..models import Transaction, User,UserProfile,Referral
from .factories import UserFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('users-list')
        self.register_url = reverse('register-list')
        self.user_data = model_to_dict(UserFactory.build())

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.register_url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.register_url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=response.data.get('id'))
        eq_(user.username, self.user_data.get('username'))
        ok_(check_password(self.user_data.get('password'), user.password))

    def test_post_request_with_valid_data_succeeds_and_profile_is_created(self):
        response = self.client.post(self.register_url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(UserProfile.objects.filter(user__username=self.user_data['username']).exists(),True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(self):
        
        referring_user = UserFactory()
        self.user_data.update({"referral_code":referring_user.userprofile.referral_code})
        response = self.client.post(self.register_url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'],owner__username=referring_user.username).exists(),True)


    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(self):
        
        self.user_data.update({"referral_code":"FAKECODE"})
        response = self.client.post(self.register_url, self.user_data)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('users-detail', kwargs={'pk': self.user.pk})
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


class TestUserDepositTestCase(APITestCase):
    """
    Tests /users/:user_id/deposits operations.
    """

    def setUp(self):
        self.user = UserFactory.create()

        # authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_post_deposit_with_no_data_fails(self):
        deposit_url = reverse('users-deposits', kwargs={'pk': self.user.pk})
        response = self.client.post(deposit_url, {})
        eq_(response.json().get("message"), {'required': 'This field is required.', 'null': 'This field may not be null.', 'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'})

    def test_post_deposit_with_data_succeeds(self):
        deposit_url = reverse('users-deposits', kwargs={'pk': self.user.pk})
        former_balance = self.user.user_accounts.first().account_balance
        response = self.client.post(
            deposit_url, 
            {
                "account_number": self.user.user_accounts.first().account_number, 
                "amount": 8000
            }
        )
        eq_(response.status_code, 200)
        self.assertGreater(self.user.user_accounts.first().account_balance, former_balance)


class TestUserWithdrawalTestCase(APITestCase):
    """
    Tests /users/:user_id/withdrawals operations.
    """

    def setUp(self):
        self.user = UserFactory.create()
        # authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_post_withdrawal_with_no_data_fails(self):
        withdrawal_url = reverse('users-withdrawals', kwargs={'pk': self.user.pk})
        response = self.client.post(withdrawal_url, {})
        eq_(response.json().get('message'),  {'required': 'This field is required.', 'null': 'This field may not be null.', 'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'})

    def test_post_withdrawal_with_data_succeeds(self):
        withdrawal_url = reverse('users-withdrawals', kwargs={'pk': self.user.pk})
        # fund account before withdrawal, else test should fail
        account = self.user.user_accounts.first()
        account.account_balance = 10_000
        account.save()

        former_balance = account.account_balance
        response = self.client.post(
            withdrawal_url, 
            {
                "account_number": self.user.user_accounts.first().account_number, 
                "amount": 8000
            }
        )
        eq_(response.status_code, status.HTTP_200_OK)
        self.assertLess(self.user.user_accounts.first().account_balance, former_balance)


class TestTransfersTestCase(APITestCase):
    """
    Tests /account/:sender_account_id/transfers/:receiver_account_id transfer operations.
    """

    def setUp(self):
        self.first_user = UserFactory.create()
        self.second_user = UserFactory.create()

        # configure and credit first_user account balance
        self.first_user_account = self.first_user.user_accounts.first()
        self.first_user_account.account_name = self.first_user.get_full_name()
        self.first_user_account.account_balance = 10_000
        self.first_user_account.save()

        # configure second_user account
        self.second_user_account = self.second_user.user_accounts.first()
        self.second_user_account.account_name = self.second_user.get_full_name()
        self.second_user_account.save()

        # authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.first_user.auth_token}')

    def test_transfer_to_same_account_should_fail(self):
        url = reverse('account-transfers', kwargs={'pk': self.first_user_account.pk, 'recipient_account_pk': self.first_user_account.pk})
        response = self.client.post(url, {"amount": 8000})
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_transfer_to_different_account_should_succeed(self):
        first_user_former_balance = self.first_user_account.account_balance
        second_user_former_balance = self.second_user_account.account_balance
        amount = 8000

        url = reverse('account-transfers', kwargs={'pk': self.first_user_account.pk, 'recipient_account_pk': self.second_user_account.pk})
        response = self.client.post(url, {"amount": amount})
        eq_(response.status_code, status.HTTP_200_OK)
        
        # current balance should be lower than previous for first_user
        # current balance should be higher than previous for second_user
        self.first_user_account.refresh_from_db()
        self.second_user_account.refresh_from_db()
        self.assertLess(self.first_user_account.account_balance, first_user_former_balance)
        self.assertGreater(self.second_user_account.account_balance, second_user_former_balance)

    def test_transfer_to_different_account_with_amount_greater_than_balance_fails(self):
        # amount is greater than balance
        amount = 20_000
        self.assertGreater(amount, self.first_user_account.account_balance)

        url = reverse('account-transfers', kwargs={'pk': self.first_user_account.pk, 'recipient_account_pk': self.second_user_account.pk})
        response = self.client.post(url, {"amount": amount})
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTransactionsTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.second_user = UserFactory.create()

        # authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

        # endpoints implemented that trigers transaction generation per action
        self.deposits_url = reverse('users-deposits', kwargs={'pk': self.user.pk})
        self.withdrawals_url = reverse('users-withdrawals', kwargs={'pk': self.user.pk})
        self.transfers_url = reverse('account-transfers', kwargs={'pk': self.user.user_accounts.first().pk, 'recipient_account_pk': self.second_user.user_accounts.first().pk})

    def tearDown(self):
        User.objects.all().delete()
        Transaction.objects.all().delete()

    def test_user_make_a_deposit_can_generate_transaction(self):
        response = self.client.post(self.deposits_url, {"account_number": self.user.user_accounts.first().account_number, "amount": 5000})
        eq_(response.status_code, status.HTTP_200_OK)
        ok_(Transaction.objects.exists())
        transaction = Transaction.objects.get(owner=self.user.user_accounts.first())
        account = transaction.owner
        eq_(account.owner.username, self.user.username)

    def test_user_make_a_withdrawal_can_generate_transaction(self):
        response1 = self.client.post(self.deposits_url, {"account_number": self.user.user_accounts.first().account_number, "amount": 5000})
        eq_(response1.status_code, status.HTTP_200_OK)
        
        response2 = self.client.post(self.withdrawals_url, {"account_number": self.user.user_accounts.first().account_number, "amount": 5000})
        eq_(response2.status_code, status.HTTP_200_OK)
        
        ok_(Transaction.objects.exists())
        eq_(Transaction.objects.filter(owner=self.user.user_accounts.first()).count(), 2)

    def test_user_can_make_a_p2p_transfer_generates_transactions(self):
        account = self.user.user_accounts.first()
        account.account_balance = 10_000
        account.save()

        response = self.client.post(self.transfers_url, {"amount": 5000})
        eq_(response.status_code, status.HTTP_200_OK)

        ok_(Transaction.objects.exists())
        # transaction should be generated for two users
        eq_(Transaction.objects.count(), 2)
        eq_(Transaction.objects.filter(owner=self.user.user_accounts.first()).count(), 1)
        eq_(Transaction.objects.filter(owner=self.second_user.user_accounts.first()).count(), 1)

    def test_user_can_fetch_all_transactions(self):
        self.transactions_list_url = reverse('account-transactions-list', kwargs={'account_pk': self.user.user_accounts.first().pk})
        response = self.client.get(self.transactions_list_url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        # create transaction by depositing into account
        deposit_url = reverse('users-deposits', kwargs={'pk': self.user.pk})
        response1 = self.client.post(
            deposit_url, 
            {
                "account_number": self.user.user_accounts.first().account_number, 
                "amount": 8000
            }
        )
        eq_(response1.status_code, status.HTTP_200_OK)

        # check if transaction belongs to account
        user_transaction = Transaction.objects.get(owner=self.user.user_accounts.first())
        self.transaction_detail_url = reverse('account-transactions-detail', kwargs={'account_pk': self.user.user_accounts.first().pk, 'pk': user_transaction.pk})
        response2 = self.client.get(self.transaction_detail_url)
        eq_(response2.status_code, status.HTTP_200_OK)
