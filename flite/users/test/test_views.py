from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral
from .factories import UserFactory
from flite.users.models import Balance, Transaction, P2PTransfer
from unittest.mock import patch

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('users')
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
        self.url = reverse('user-detail', kwargs={'user_id': self.user.pk})
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

    @patch('flite.users.views.UserDepositView.generate_transaction_reference', return_value='TEST1234567890')
    def test_user_can_make_a_deposit(self, mock_generate_reference):
        # Create a user and balance for testing
        self.user = User.objects.create(username='testuser')
        self.balance = Balance.objects.get(owner=self.user)
        
        url = reverse('user-deposits', kwargs={'user_id': self.user.id})
        data = {'amount': 100.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.balance.refresh_from_db()  # Refresh the balance object from the database
        self.assertEqual(self.balance.available_balance, 100.0)  # Check if available_balance is updated
        self.assertEqual(self.balance.book_balance, 100.0)  # Check if book_balance is updated
        self.assertTrue(Transaction.objects.filter(owner=self.user, reference='TEST1234567890').exists())  # Check if transaction is created



    @patch('flite.users.views.UserWithdrawalView.generate_transaction_reference', return_value='TEST1234567890')
    def test_user_can_make_a_withdrawal(self, mock_generate_reference):
        self.user = User.objects.create(username='testuser')
        self.balance = Balance.objects.get(owner=self.user)
        
        url = reverse('user-withdrawals', kwargs={'user_id': self.user.id})
        data = {'amount': 50.0}  # Withdrawal amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.balance.refresh_from_db()  # Refresh the balance object from the database
        self.assertEqual(self.balance.available_balance, -50.0)  # Check if available_balance is updated
        self.assertEqual(self.balance.book_balance, -50.0)  # Check if book_balance is updated
        self.assertTrue(Transaction.objects.filter(owner=self.user, reference='TEST1234567890').exists())  # Check if transaction is created


    @patch('flite.users.views.P2PTransferView.generate_transaction_reference', return_value='TEST1234567890')
    def test_user_can_make_a_p2p_transfer(self, mock_generate_reference):
        self.sender = User.objects.create(username='sender')
        self.recipient = User.objects.create(username='recipient')
        self.recipient_balance = Balance.objects.get(owner__id=self.sender.id)

        url = reverse('p2p-transfer', kwargs={'sender_account_id': self.sender.id, 'recipient_account_id': self.recipient.id})
        data = {'amount': 50.0}  # Transfer amount
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipient_balance.refresh_from_db()  # Refresh the recipient balance object from the database
        self.assertTrue(P2PTransfer.objects.filter(reference='TEST1234567890').exists())  # Check if P2PTransfer object is created


    def test_user_can_fetch_all_transactions(self):
        self.user = User.objects.create(username='testuser')
        self.transactions = [
            Transaction.objects.create(owner=self.user, reference=f'TRANS-{i}', status='SUCCESS', amount=i*10, new_balance=i*100)
            for i in range(1, 11)
        ]

        url = reverse('transactions-list', kwargs={'account_id': self.user.id})
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['page'], '1')
        self.assertEqual(len(response.data['data']), 5)  # Check if 5 transactions are returned for the first page


    def test_user_can_fetch_a_single_transaction(self):
        self.user = User.objects.create(username='testuser')
        self.transaction = Transaction.objects.create(owner=self.user, reference='TEST123', status='SUCCESS', amount=100.0, new_balance=1000.0)

        url = reverse('transactions-detail', kwargs={'account_id': self.user.id, 'transaction_id': 'TEST123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['owner']), str(self.user.id))  # Check if the owner ID matches
        self.assertEqual(response.data['reference'], 'TEST123')




# from django.urls import reverse
# from rest_framework.test import APITestCase
# from rest_framework import status
# from flite.users.models import Balance, Transaction, P2PTransfer
# from flite.users.serializers import UserSerializer
# from unittest.mock import patch
# from uuid import uuid4


# class UserDepositViewTests(APITestCase):
#     def setUp(self):
#         # Create a user and balance for testing
#         self.user = User.objects.create(username='testuser')
#         self.balance = Balance.objects.get(owner=self.user)

#     @patch('flite.users.views.UserDepositView.generate_transaction_reference', return_value='TEST1234567890')
#     def test_deposit_update(self, mock_generate_reference):
#         url = reverse('user-deposits', kwargs={'user_id': self.user.id})
#         data = {'amount': 100.0}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.balance.refresh_from_db()  # Refresh the balance object from the database
#         self.assertEqual(self.balance.available_balance, 100.0)  # Check if available_balance is updated
#         self.assertEqual(self.balance.book_balance, 100.0)  # Check if book_balance is updated
#         self.assertTrue(Transaction.objects.filter(owner=self.user, reference='TEST1234567890').exists())  # Check if transaction is created

#     def test_invalid_deposit_update(self):
#         url = reverse('user-deposits', kwargs={'user_id': self.user.id})
#         data = {'amount': 'invalid_amount'}  # Invalid amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(Transaction.objects.filter(owner=self.user).exists())  # Ensure no transaction is created

#         data = {}  # Missing amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(Transaction.objects.filter(owner=self.user).exists())  # Ensure no transaction is created


# class UserWithdrawalViewTests(APITestCase):
#     def setUp(self):
#         # Create a user and balance for testing
#         self.user = User.objects.create(username='testuser')
#         self.balance = Balance.objects.get(owner=self.user)

#     @patch('flite.users.views.UserWithdrawalView.generate_transaction_reference', return_value='TEST1234567890')
#     def test_valid_withdrawal(self, mock_generate_reference):
#         url = reverse('user-withdrawals', kwargs={'user_id': self.user.id})
#         data = {'amount': 50.0}  # Withdrawal amount
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.balance.refresh_from_db()  # Refresh the balance object from the database
#         self.assertEqual(self.balance.available_balance, -50.0)  # Check if available_balance is updated
#         self.assertEqual(self.balance.book_balance, -50.0)  # Check if book_balance is updated
#         self.assertTrue(Transaction.objects.filter(owner=self.user, reference='TEST1234567890').exists())  # Check if transaction is created

#     def test_invalid_withdrawal(self):
#         url = reverse('user-withdrawals', kwargs={'user_id': self.user.id})
#         data = {'amount': 'invalid_amount'}  # Invalid amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(Transaction.objects.filter(owner=self.user).exists())  # Ensure no transaction is created

#         data = {}  # Missing amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(Transaction.objects.filter(owner=self.user).exists())  # Ensure no transaction is created



# class P2PTransferViewTests(APITestCase):
#     def setUp(self):
#         # Create users and balances for testing
#         self.sender = User.objects.create(username='sender')
#         self.recipient = User.objects.create(username='recipient')
#         self.recipient_balance = Balance.objects.get(owner__id=self.sender.id)


#     @patch('flite.users.views.P2PTransferView.generate_transaction_reference', return_value='TEST1234567890')
#     def test_valid_transfer(self, mock_generate_reference):
#         url = reverse('p2p-transfer', kwargs={'sender_account_id': self.sender.id, 'recipient_account_id': self.recipient.id})
#         data = {'amount': 50.0}  # Transfer amount
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.recipient_balance.refresh_from_db()  # Refresh the recipient balance object from the database
#         self.assertTrue(P2PTransfer.objects.filter(reference='TEST1234567890').exists())  # Check if P2PTransfer object is created

#     def test_invalid_transfer(self):
#         url = reverse('p2p-transfer', kwargs={'sender_account_id': self.sender.id, 'recipient_account_id': self.recipient.id})
#         data = {'amount': 'invalid_amount'}  # Invalid amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(P2PTransfer.objects.filter(reference='TEST1234567890').exists())  # Ensure no P2PTransfer object is created

#         data = {}  # Missing amount data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertFalse(P2PTransfer.objects.filter(reference='TEST1234567890').exists())  # Ensure no P2PTransfer object is created


# class TransactionsListViewTests(APITestCase):
#     def setUp(self):
#         # Create a user and some transactions for testing
#         self.user = User.objects.create(username='testuser')
#         self.transactions = [
#             Transaction.objects.create(owner=self.user, reference=f'TRANS-{i}', status='SUCCESS', amount=i*10, new_balance=i*100)
#             for i in range(1, 11)
#         ]

#     def test_get_transactions_list(self):
#         url = reverse('transactions-list', kwargs={'account_id': self.user.id})
#         response = self.client.get(url, {'page': 1})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['data']), 5)  # Check if the default number of transactions returned is 5

#     def test_get_paginated_transactions_list(self):
#         url = reverse('transactions-list', kwargs={'account_id': self.user.id})
#         response = self.client.get(url, {'page': 1})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['page'], '1')
#         self.assertEqual(len(response.data['data']), 5)  # Check if 5 transactions are returned for the first page



# class TransactionDetailViewTests(APITestCase):
#     def setUp(self):
#         # Create a user and a transaction for testing
#         self.user = User.objects.create(username='testuser')
#         self.transaction = Transaction.objects.create(owner=self.user, reference='TEST123', status='SUCCESS', amount=100.0, new_balance=1000.0)

#     def test_get_transaction_detail(self):
#         url = reverse('transactions-detail', kwargs={'account_id': self.user.id, 'transaction_id': 'TEST123'})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(str(response.data['owner']), str(self.user.id))  # Check if the owner ID matches
#         self.assertEqual(response.data['reference'], 'TEST123')  # Check if the transaction reference matches

#     def test_nonexistent_transaction(self):
#         url = reverse('transactions-detail', kwargs={'account_id': self.user.id, 'transaction_id': 'NONEXISTENT'})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Check if proper 404 response is returned

# # python manage.py test flite.users.test.test_views