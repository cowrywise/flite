from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral
from .factories import UserFactory
from django.contrib.auth import get_user_model
from flite.users.models import *
import secrets


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
        get_user_model().objects.create(
            username='testlearner1', email='test@admin.com', password='admin1234x')
        get_user_model().objects.create(
            username='testlearner2', email='test@admin.com', password='admin1234x')         
        AllBanks.objects.create(
        name='Guaranty Trust Bank',
        acronym='GTBank',
        bank_code='058'
        )   
        self.test_user_1 = get_user_model().objects.get(username='testlearner1')
        self.test_user_2 = get_user_model().objects.get(username='testlearner2')  
        self.sample_bank = AllBanks.objects.get(name='Guaranty Trust Bank')   
        Bank.objects.create(
        owner =  self.test_user_1,
        bank = self.sample_bank ,
        account_name='Believe Ohiozua',
        account_number='0119639776',
        account_type='savings'
        )     
        self.test_bank = Bank.objects.get(owner=self.test_user_1)
        self.ref_code = secrets.token_urlsafe(6)
        BankTransfer.objects.create(
            bank= self.test_bank,
            owner= self.test_user_1,
            reference= self.ref_code ,
            status= 'success',
            amount= 1000.00,
            new_balance= 2000.00,
            transaction_type= 'banktransfer',            
        )      
        self.test_transaction = Transaction.objects.get(reference=self.ref_code) 

    def test_user_can_make_a_deposit(self):
        self.client.force_authenticate(user=self.test_user_1)
        payload = {'amount': 1000.00, 'bank': self.sample_bank.name}
        res = self.client.post(f'/api/v1/users/{self.test_user_1.id}/deposits/', payload)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_make_a_withdrawal(self):
        self.client.force_authenticate(user=self.test_user_1)
        payload = {'amount': 500.00, 'bank': self.sample_bank.name}
        res = self.client.post(f'/api/v1/users/{self.test_user_1.id}/withdrawals/', payload)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_make_a_p2p_transfer(self):
        self.client.force_authenticate(user=self.test_user_1)
        payload = {'amount': 100.00}
        res = self.client.post(f'/api/v1/account/{self.test_user_1.id}/withdrawals/{self.test_user_2.id}/', payload)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_all_transactions(self):
        self.client.force_authenticate(user=self.test_user_1)
        payload = {'amount': 1000.00, 'bank': self.sample_bank.name}
        self.client.post(f'/api/v1/users/{self.test_user_1.id}/deposit/', payload)        
        res = self.client.get(f'/api/v1/account/{self.test_user_1.id}/transactions/')
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        self.client.force_authenticate(user=self.test_user_1)
        res = self.client.get(f'/api/v1/account/{self.test_user_1.id}/transactions/{self.test_transaction.id}/')
        eq_(res.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.test_user_1.delete()
        self.test_user_2.delete()
        self.sample_bank.delete()
        self.test_bank.delete()
        self.ref_code = None
        self.test_transaction.delete()
