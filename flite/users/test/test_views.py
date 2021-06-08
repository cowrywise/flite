from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral, Balance, Transaction, P2PTransfer
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
    """
    Test Withdrawals, Deposits and Transactions
    """
    def setUp(self):
        sender = User.objects.create(username="cowry1", email="cowry1@test.com", password="123456")
        receipient = User.objects.create(username="cowry2", email="cowry2@test.com", password="123456")
        sender_balance = Balance.objects.get(owner=sender)
        receipient_balance = Balance.objects.get(owner=receipient)
        sender_balance.book_balance = 15000
        sender_balance.available_balance = 15000
        sender_balance.save()       
        self.test_transaction = Transaction.objects.create(owner=sender, amount=2000, status="success", new_balance=5000)
        self.test_p2p_transaction = P2PTransfer.objects.create(
            owner=sender, 
            amount=3000, 
            status="success", 
            new_balance=2000,
            sender=sender,
            receipient=receipient)
        self.sender = sender
        self.receipient = receipient
        self.sender_balance = sender_balance
        self.receipient_balance = receipient_balance
        self.payload = {"amount": 5000.00}
        self.deposit_url = f"/api/v1/users/{sender.id}/deposits"
        self.withdrawal_url = f"/api/v1/users/{sender.id}/withdrawals"
        self.transfer_url = f"/api/v1/account/{sender.id}/transfers/{receipient.id}"
        self.transaction_list_url = f"/api/v1/account/{sender.id}/transactions"
        self.transaction_detail_url = f"/api/v1/account/{sender.id}/transactions/{self.test_transaction.id}"
        self.transaction_detail_url_2 = f"/api/v1/account/{sender.id}/transactions/{self.test_p2p_transaction.id}"           

    def test_user_can_make_a_deposit(self):
        self.client.force_authenticate(user=self.sender)
        sender_initial_balance = self.sender_balance.book_balance
        res = self.client.post(self.deposit_url, self.payload)
        eq_(res.status_code, status.HTTP_201_CREATED)
        eq_(res.json().get("book_balance"), sender_initial_balance+self.payload["amount"])

    def test_user_can_make_a_withdrawal(self):
        self.client.force_authenticate(user=self.sender)
        initial_balance = self.sender_balance.book_balance
        res = self.client.post(self.withdrawal_url, self.payload)
        eq_(res.status_code, status.HTTP_201_CREATED)
        eq_(res.json().get("book_balance"), initial_balance-self.payload["amount"])

    def test_user_can_make_a_p2p_transfer(self):
        self.client.force_authenticate(user=self.sender)
        res = self.client.post(self.transfer_url, self.payload)
        eq_(res.status_code, status.HTTP_201_CREATED)
        

    def test_user_can_fetch_all_transactions(self):
        self.client.force_authenticate(user=self.sender)
        self.client.post(self.deposit_url, self.payload)        
        res = self.client.get(self.transaction_list_url)
        eq_(res.status_code, status.HTTP_200_OK)

    def test_user_can_fetch_a_single_transaction(self):
        self.client.force_authenticate(user=self.sender)
        res_1 = self.client.get(self.transaction_detail_url)
        res_2 = self.client.get(self.transaction_detail_url_2)
        eq_(res_1.status_code, status.HTTP_200_OK)
        eq_(res_2.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.sender.delete()
        self.receipient.delete()
        self.test_transaction.delete()
        self.test_p2p_transaction.delete()
    

