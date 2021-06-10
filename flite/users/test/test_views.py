from django.contrib.auth.hashers import check_password
from django.forms.models import model_to_dict
from django.urls import reverse
from faker import Faker
from nose.tools import eq_, ok_
from rest_framework import status
from rest_framework.test import APITestCase

from flite.account.models import Account
from flite.account.test.factories import BankFactory, CardFactory

from ..models import Referral, User, UserProfile
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

    def test_post_request_with_valid_data_succeeds_and_profile_and_account_is_created(
            self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(
            UserProfile.objects.filter(
                user__username=self.user_data['username']).exists(), True)
        eq_(
            Account.objects.filter(
                owner__username=self.user_data['username']).exists(), True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(
            self):

        referring_user = UserFactory()
        self.user_data.update(
            {"referral_code": referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(
            Referral.objects.filter(
                referred__username=self.user_data['username'],
                owner__username=referring_user.username).exists(), True)

    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(
            self):

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
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

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


class TestDepositTestCase(APITestCase):
    """
    Tests /users/:user_id/deposits detail operations.
    """
    def setUp(self):
        self.testuser1 = UserFactory()
        self.testuser2 = UserFactory()
        self.bank = BankFactory(owner=self.testuser1)
        self.card = CardFactory(owner=self.testuser1)
        self.card1 = CardFactory(owner=self.testuser2)
        self.bank1 = BankFactory(owner=self.testuser2)
        self.url = reverse('user-deposit', kwargs={'pk': self.testuser1.pk})
        self.url2 = reverse('user-deposit', kwargs={'pk': self.testuser2.pk})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.testuser1.auth_token}')

    def test_user_can_deposit_with_bank(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {'amount': amount, 'bank': self.bank.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal - old_bal, amount)

    def test_user_can_deposit_with_card(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {'amount': amount, 'card': self.card.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal - old_bal, amount)

    def test_user_can_deposit_with_card_and_bank(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {
            'amount': amount,
            'card': self.card.id,
            'bank': self.bank.id
        }
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, old_bal)

    def test_user_can_deposit_with_invalid_details(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {'amount': amount}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, old_bal)

    def test_user_can_deposit_with_owned_card_only(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {'amount': amount, 'card': self.card1.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, old_bal)

    def test_user_can_deposit_with_owned_bank_only(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser1).available_balance
        payload = {'amount': amount, 'bank': self.bank1.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, old_bal)

    def test_user_can_deposit_with_owned_account(self):
        amount = fake.random_int(min=100, max=10000)

        old_bal = Account.objects.get(owner=self.testuser2).available_balance
        payload = {'amount': amount, 'bank': self.bank1.id}
        response = self.client.post(self.url2, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser2).available_balance
        eq_(new_bal, old_bal)


class TestWithdrawTestCase(APITestCase):
    """
    Tests /users/:user_id/withdrawals detail operations.
    """
    def setUp(self):
        self.testuser1 = UserFactory()
        self.testuser2 = UserFactory()
        self.bank = BankFactory(owner=self.testuser1)
        self.bank1 = BankFactory(owner=self.testuser2)
        self.old_bal = 2000
        self.url = reverse('user-withdrawal', kwargs={'pk': self.testuser1.pk})
        self.url2 = reverse('user-withdrawal',
                            kwargs={'pk': self.testuser2.pk})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.testuser1.auth_token}')

    def test_user_can_withdraw_with_bank(self):
        amount = fake.random_int(min=100, max=1000)
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)

        payload = {'amount': amount, 'bank': self.bank.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(self.old_bal - new_bal, amount)

    def test_user_can_withdraw_with_invalid_details(self):
        amount = fake.random_int(min=100, max=1000)
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)

        payload = {'amount': amount}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, self.old_bal)

    def test_user_can_withdraw_with_owned_bank_only(self):
        amount = fake.random_int(min=100, max=1000)

        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)
        payload = {'amount': amount, 'bank': self.bank1.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, self.old_bal)

    def test_user_can_withdraw_with_owned_account(self):
        amount = fake.random_int(min=100, max=1000)
        Account.objects.filter(owner=self.testuser2).update(
            available_balance=self.old_bal)
        payload = {'amount': amount, 'bank': self.bank1.id}
        response = self.client.post(self.url2, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser2).available_balance
        eq_(new_bal, self.old_bal)

    def test_user_can_withdraw_only_available_amount(self):
        amount = fake.random_int(min=10000, max=100000)
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)
        payload = {'amount': amount, 'bank': self.bank1.id}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, self.old_bal)
