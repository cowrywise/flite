from django.test.client import Client
from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral
from .factories import AllBanksFactory, BankFactory, UserFactory, P2PTransferFactory, BankTransferFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.user_data = model_to_dict(UserFactory.build(), 
                                       fields=['username', 'first_name', 'last_name', 'email', 'password']
                                      )

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
    Tests all transactions operations
    """

    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.bank = AllBanksFactory()
        self.user1_account = BankFactory(
                                owner=self.user1, 
                                bank=self.bank, 
                                account_name=self.user1.get_full_name
                            )

        user1_balance = self.user1.balance.first()
 
        user1_balance.available_balance = fake.pyfloat(min_value=300_000, max_value=599_999, right_digits=2)
        user1_balance.book_balance = fake.pyfloat(min_value=300_000, max_value=599_999, right_digits=2)
        user1_balance.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user1.auth_token}')
        

    def test_user_can_make_a_deposit(self):
        url = reverse('user-deposits', kwargs={'pk': self.user1.pk})

        deposit_data = model_to_dict(BankTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, deposit_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_make_a_withdrawal(self):
        url = reverse('user-withdrawals', kwargs={'pk': self.user1.pk})

        withdrawal_data = model_to_dict(BankTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, withdrawal_data)
        eq_(response.status_code, status.HTTP_201_CREATED)


    def test_user_can_make_a_p2p_transfer(self):
        url = reverse('account-transfers', kwargs={'sender_id': self.user1.pk, 'recipient_id': self.user2.pk})

        p2p_transfer_data = model_to_dict(P2PTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, p2p_transfer_data)
        eq_(response.status_code, status.HTTP_201_CREATED)


    def test_user_can_fetch_all_transactions(self):
        url = reverse('account-transactions-list', kwargs={'pk': self.user1.pk})


        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)
        

    def test_user_can_fetch_a_single_transaction(self):
        bank_transfer = BankTransferFactory(owner=self.user1, bank=self.user1_account)
        url = reverse('account-transactions-detail', kwargs={'pk': self.user1.pk, 'transaction_id': bank_transfer.pk})

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_make_a_p2p_transfer_to_themselves(self):
        url = reverse('account-transfers', kwargs={'sender_id': self.user1.pk, 'recipient_id': self.user1.pk})
        # user1 attempting to make a transfer to themselves 

        p2p_transfer_data = model_to_dict(P2PTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, p2p_transfer_data)
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_make_a_withdrawal(self):
        url = reverse('user-withdrawals', kwargs={'pk': self.user2.pk})
        # user1 attempting to make a withdrawal from user2's account

        withdrawal_data = model_to_dict(BankTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, withdrawal_data)
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthorized_user_cannot_make_a_p2p_transfer(self):
        url = reverse('account-transfers', kwargs={'sender_id': self.user2.pk, 'recipient_id': self.user1.pk})
        # user1 attempting to make a transfer to themselves from user2's account

        p2p_transfer_data = model_to_dict(P2PTransferFactory.build(), fields=['reference', 'amount'])

        response = self.client.post(url, p2p_transfer_data)
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_fetch_all_transactions(self):
        url = reverse('account-transactions-list', kwargs={'pk': self.user2.pk})
        # user1 attempting to view all of user2's transactions

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_fetch_a_single_transaction(self):
        bank_transfer = BankTransferFactory(owner=self.user1, bank=self.user1_account)
        url = reverse('account-transactions-detail', kwargs={'pk': self.user1.pk, 'transaction_id': bank_transfer.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user2.auth_token}')

        # user2 attempting to view user1's transaction detail
        response = self.client.get(url)

        eq_(response.status_code, status.HTTP_403_FORBIDDEN)



