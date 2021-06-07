from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from faker import Faker
from ..models import User, UserProfile, Referral
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


def deposit_detail_url(user_id):
    """
    Return deposit detail url
    """
    return reverse('transaction-deposit-list', args=[user_id])


def sample_user(username='username', email='user@example.com', password='password'):
    """
    create a sample user
    """
    return User.objects.create_user(username, email, password)


class TestTransactions(APITestCase):

    def setUp(self):
        self.user_one = sample_user(username='username_one', email='user_one@example.com', password='password')
        self.user_two = sample_user(username='username_two', email='user_two@example.com', password='password')
        self.client = APIClient()
        self.client.force_authenticate(self.user_one)
        self.client.force_authenticate(self.user_two)

    def test_user_can_make_a_deposit(self):
        payload = {'amount': 1000.00}
        url = deposit_detail_url(self.user_one.id)
        res = self.client.post(url, payload)
        eq_(res.status_code, status.HTTP_201_CREATED)

    def test_user_can_not_make_a_deposit_with_invalid_user_id(self):
        payload = {'amount': 1000.00}
        url = deposit_detail_url('a09d27e8-870d-4fa9-a999-70eeeeeeeee2')
        res = self.client.post(url, payload)
        eq_(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_user_can_make_a_withdrawal(self):
    #     assert False
    #
    # def test_user_can_make_a_p2p_transfer(self):
    #     assert False
    #
    # def test_user_can_fetch_all_transactions(self):
    #     assert False
    #
    # def test_user_can_fetch_a_single_transaction(self):
    #     assert False
