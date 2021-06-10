from django.urls import reverse
from faker import Faker
from nose.tools import eq_
from rest_framework import status
from rest_framework.test import APITestCase

from flite.account.models import Account, Transaction
from flite.users.test.factories import UserFactory


fake = Faker()


class TestTransferTestCase(APITestCase):
    """
    Tests /account/:sender_account_id/transfers/:recipient_account_id transfer operations.
    """
    def setUp(self):
        self.testuser1 = UserFactory()
        self.testuser2 = UserFactory()
        self.old_bal = 2000
        self.account1 = Account.objects.get(owner=self.testuser1)
        self.account2 = Account.objects.get(owner=self.testuser2)
        self.url = reverse('account-transfers',
                           kwargs={
                               'pk': self.account1.pk,
                               'receipient_account_id': self.account2.id
                           })
        self.url2 = reverse('account-transfers',
                            kwargs={
                                'pk': self.account2.pk,
                                'receipient_account_id': self.account1.id
                            })
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.testuser1.auth_token}')

    def test_user_can_p2ptransfer(self):
        amount = fake.random_int(min=100, max=1000)
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)

        response = self.client.post(self.url, {'amount': amount})
        eq_(response.status_code, status.HTTP_202_ACCEPTED)

        testuser1_new_bal = Account.objects.get(
            owner=self.testuser1).available_balance
        eq_(self.old_bal - testuser1_new_bal, float(amount))

        testuser2_new_bal = Account.objects.get(
            owner=self.testuser2).available_balance
        eq_(testuser2_new_bal, float(amount))

    def test_user_can_p2ptransfer_with_invalid_details(self):
        amount = fake.random_int(min=100, max=1000)
        fake_account_id = fake.uuid4()
        url = reverse('account-transfers',
                      kwargs={
                          'pk': self.account1.pk,
                          'receipient_account_id': fake_account_id
                      })
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)

        response = self.client.post(url, {'amount': amount})
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, self.old_bal)

    def test_user_can_p2ptransfer_with_owned_account_only(self):
        amount = fake.random_int(min=100, max=1000)
        Account.objects.filter(owner=self.testuser2).update(
            available_balance=self.old_bal)
        response = self.client.post(self.url2, {'amount': amount})
        eq_(response.status_code, 422)

        new_bal = Account.objects.get(owner=self.testuser2).available_balance
        eq_(new_bal, self.old_bal)

    def test_user_can_withdraw_only_available_amount(self):
        amount = fake.random_int(min=10000, max=100000)
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=self.old_bal)

        response = self.client.post(self.url, {'amount': amount})
        eq_(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        new_bal = Account.objects.get(owner=self.testuser1).available_balance
        eq_(new_bal, self.old_bal)

        testuser1_new_bal = Account.objects.get(
            owner=self.testuser1).available_balance
        eq_(testuser1_new_bal, self.old_bal)

        testuser2_new_bal = Account.objects.get(
            owner=self.testuser2).available_balance
        eq_(testuser2_new_bal, 0.0)


class TestTransactionsListTestCase(APITestCase):
    """
    Tests /account/:account_id/transactions transactions operations.
    """
    def setUp(self):
        self.testuser1 = UserFactory()
        self.testuser2 = UserFactory()
        self.account = Account.objects.get(owner=self.testuser1)
        self.account1 = Account.objects.get(owner=self.testuser2)
        self.url = reverse('account-transactions',
                           kwargs={
                               'pk': self.account.pk,
                           })
        self.url2 = reverse('account-transactions',
                            kwargs={
                                'pk': self.account1.pk,
                            })
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.testuser1.auth_token}')

    def test_user_can_get_transaction_list(self):
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=3000)

        self.client.post(
            reverse('account-transfers',
                    kwargs={
                        'pk': self.account.pk,
                        'receipient_account_id': self.account1
                    }), {'amount': 200})

        self.client.post(
            reverse('account-transfers',
                    kwargs={
                        'pk': self.account.pk,
                        'receipient_account_id': self.account1
                    }), {'amount': 200})

        self.client.post(
            reverse('account-transfers',
                    kwargs={
                        'pk': self.account.pk,
                        'receipient_account_id': self.account1
                    }), {'amount': 200})

        transaction_count = Transaction.objects.filter(
            owner=self.testuser1).count()

        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.json().get('count'), transaction_count)

    def test_user_can_get_owned_transaction_list_only(self):
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=3000)

        self.client.post(
            reverse('account-transfers',
                    kwargs={
                        'pk': self.account.pk,
                        'receipient_account_id': self.account1
                    }), {'amount': 200})

        transaction_count = Transaction.objects.filter(
            owner=self.testuser1).count()
        transaction_count2 = Transaction.objects.filter(
            owner=self.testuser2).count()

        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.json().get('count'), transaction_count)

        response1 = self.client.get(self.url2)
        eq_(response1.json().get('count'), transaction_count)
        eq_(transaction_count2, 0)


class TestTransactionDetailTestCase(APITestCase):
    """
    Tests /account/:account_id/transactions/transaction_id details operations.
    """
    def setUp(self):
        self.testuser1 = UserFactory()
        self.testuser2 = UserFactory()
        self.account = Account.objects.get(owner=self.testuser1)
        self.account1 = Account.objects.get(owner=self.testuser2)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.testuser1.auth_token}')

    def test_user_can_get_transaction(self):
        Account.objects.filter(owner=self.testuser1).update(
            available_balance=3000)

        self.client.post(
            reverse('account-transfers',
                    kwargs={
                        'pk': self.account.pk,
                        'receipient_account_id': self.account1
                    }), {'amount': 200})

        transaction = Transaction.objects.filter(owner=self.testuser1).first()

        url = reverse('account-transaction',
                      kwargs={
                          'pk': self.account.pk,
                          'transaction_id': transaction.id
                      })

        response = self.client.get(url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(response.json().get('amount'), transaction.amount)

    def test_user_can_get_transaction_with_invalid_details(self):
        transaction_id = fake.uuid4()
        url = reverse('account-transaction',
                      kwargs={
                          'pk': self.account1.pk,
                          'transaction_id': transaction_id
                      })

        response = self.client.get(url)
        eq_(response.status_code, 422)
