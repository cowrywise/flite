from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral
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

    def setUp(self):
        self.sender = UserFactory()
        self.recipient = UserFactory()
        #self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.sender.auth_token}')

    def test_user_can_make_a_deposit(self):
        self.url = reverse('user-deposits', kwargs={'pk':self.sender.id})
        payload = {'amount':5000}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_withdrawal(self):
        #make a deposit first
        self.url = reverse('user-deposits', kwargs={'pk':self.sender.id})
        payload = {'amount':5000}
        response = self.client.post(self.url, payload)

        # make withdrawal
        self.url = reverse('user-withdrawals', kwargs={'pk':self.sender.id})
        payload = {'amount':1000}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_p2p_transfer(self):
        #make a deposit first
        self.url = reverse('user-deposits', kwargs={'pk':self.sender.id})
        payload = {'amount':20000}
        response = self.client.post(self.url, payload)

        #make a p2p transfer
        self.url = reverse('p2p-create', kwargs={'sender_account_id':self.sender.id, 'recipient_account_id':self.recipient.id})
        payload = {'amount':2000}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        eq_(data['amount'], payload['amount'])
        eq_(data['sender'], self.sender.id)
        eq_(data['receipient'], self.recipient.id)


    def test_user_can_fetch_all_transactions(self):
        self.url = reverse('transaction-list', kwargs={'account_id':self.sender.id})
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

        eq_(type(response.json()), list)

        eq_(len(response.json()), 0)

    def test_user_can_fetch_a_single_transaction(self):
        #make a deposit first
        self.url = reverse('user-deposits', kwargs={'pk':self.sender.id})
        payload = {'amount':20000}
        response = self.client.post(self.url, payload)
        transaction_id = response.json()['transaction_id']

        #fetch transaction
        self.url = reverse('transaction-detail', kwargs={'account_id':self.sender.id, 'transaction_id':transaction_id})
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(type(response.json()), dict)