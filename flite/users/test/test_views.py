from django.contrib.auth.hashers import check_password
from django.forms.models import model_to_dict
from django.urls import reverse

from faker import Faker
from nose.tools import eq_, ok_
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Referral, User, UserProfile
from .factories import UserFactory, BankFactory, AllBankFactory
from flite.transfers.wallets import UserWallet

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse("user-list")
        self.user_data = model_to_dict(UserFactory.build())

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=response.data.get("id"))
        eq_(user.username, self.user_data.get("username"))
        ok_(check_password(self.user_data.get("password"), user.password))

    def test_post_request_with_valid_data_succeeds_and_profile_is_created(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(
            UserProfile.objects.filter(
                user__username=self.user_data["username"]
            ).exists(),
            True,
        )

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(
        self,
    ):

        referring_user = UserFactory()
        self.user_data.update(
            {"referral_code": referring_user.userprofile.referral_code}
        )
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(
            Referral.objects.filter(
                referred__username=self.user_data["username"],
                owner__username=referring_user.username,
            ).exists(),
            True,
        )

    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(
        self,
    ):

        self.user_data.update({"referral_code": "FAKECODE"})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.auth_token}")

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        new_first_name = fake.first_name()
        payload = {"first_name": new_first_name}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.user.id)
        eq_(user.first_name, new_first_name)


class TestTransactions(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.auth_token}")

    def dummy_bank(self):
        data = {
            "name": "Wema Bank",
            "acronym": "wema",
            "bank_code": "801",
        }
        return AllBankFactory(**data)

    def create_bank_account(self, **kwargs):
        return BankFactory(
            owner=self.user,
            bank=self.dummy_bank(),
            account_name="{} {}".format(self.user.first_name, self.user.last_name),
            account_number="0229867743",
            account_type="savings",
        )

    def fund_wallet(self, amount, bank):
        return UserWallet.receive_bank_deposit(self.user, amount, bank)

    def test_user_can_make_a_deposit(self):
        url = reverse("user-deposits", kwargs={"pk": self.user.pk})
        bank = self.create_bank_account()
        payload = {"bank": bank.pk, "amount": 1000}
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_withdrawal(self):
        url = reverse("user-withdrawals", kwargs={"pk": self.user.pk})
        bank = self.create_bank_account()
        self.fund_wallet(10_000, bank)
        payload = {"amount": 1500, "bank": bank.pk}
        response = self.client.post(url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_p2p_transfer(self):
        recipient = UserFactory()
        url = reverse(
            "account-transfers", kwargs={"pk": self.user.pk, "recipient": recipient.id}
        )
        bank = self.create_bank_account()
        self.fund_wallet(10_000, bank)
        response = self.client.post(url, {"amount": 1000}, format="json")
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_fetch_all_transactions(self):
        url = reverse("account-transactions", kwargs={"pk": self.user.pk})
        bank = self.create_bank_account()
        self.fund_wallet(10_000, bank)
        response = self.client.get(url)
        count = response.json()["count"]
        eq_(count, 1)

    def test_user_can_fetch_a_single_transaction(self):
        bank = self.create_bank_account()
        transaction = self.fund_wallet(10_000, bank)
        url = reverse(
            "account-single_transaction",
            kwargs={"pk": self.user.pk, "transaction_id": transaction.id},
        )
        response = self.client.get(url)
        json_res = response.json()
        amount = json_res["data"]["amount"]
        eq_(amount, transaction.amount)
