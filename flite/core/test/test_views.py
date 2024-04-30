from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory,force_authenticate
from rest_framework import status
from django.contrib.auth.models import User
from .views import budget_category_list, budget_category_detail, transaction_list, transaction_detail
from core.models import BudgetCategory,Transaction
class TestBudgetCategoryViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = BudgetCategory.objects.create(name='Test Category', description='Test description', max_spend=100.00)

    def test_budget_category_list_get(self):
        request = self.factory.get('/budget-categories/', format='json')
        force_authenticate(request, user=self.user)
        response = budget_category_list(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_budget_category_list_post(self):
        data = {'name': 'New Category', 'description': 'New description', 'max_spend': 200.00}
        request = self.factory.post('/budget-categories/', data, format='json')
        force_authenticate(request, user=self.user)
        response = budget_category_list(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BudgetCategory.objects.count(), 2)

    def test_budget_category_detail_get(self):
        request = self.factory.get('/budget-categories/{}/'.format(self.category.pk), format='json')
        force_authenticate(request, user=self.user)
        response = budget_category_detail(request, pk=self.category.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)

    def test_budget_category_detail_put(self):
        data = {'name': 'Updated Category', 'description': 'Updated description', 'max_spend': 150.00}
        request = self.factory.put('/budget-categories/{}/'.format(self.category.pk), data, format='json')
        force_authenticate(request, user=self.user)
        response = budget_category_detail(request, pk=self.category.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_budget_category_detail_delete(self):
        request = self.factory.delete('/budget-categories/{}/'.format(self.category.pk), format='json')
        force_authenticate(request, user=self.user)
        response = budget_category_detail(request, pk=self.category.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BudgetCategory.objects.count(), 0)

class TestTransactionViews(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = BudgetCategory.objects.create(name='Test Category', description='Test description', max_spend=100.00)
        self.transaction = Transaction.objects.create(owner=self.user, category=self.category, amount=50.00, description='Test transaction')

    def test_transaction_list_get(self):
        request = self.factory.get('/transactions/', format='json')
        force_authenticate(request, user=self.user)
        response = transaction_list(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_transaction_list_post(self):
        data = {'category': self.category.pk, 'amount': 20.00, 'description': 'New transaction'}
        request = self.factory.post('/transactions/', data, format='json')
        force_authenticate(request, user=self.user)
        response = transaction_list(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)

    def test_transaction_detail_get(self):
        request = self.factory.get('/transactions/{}/'.format(self.transaction.pk), format='json')
        force_authenticate(request, user=self.user)
        response = transaction_detail(request, pk=self.transaction.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], self.transaction.amount)

    def test_transaction_detail_put(self):
        data = {'category': self.category.pk, 'amount': 30.00, 'description': 'Updated transaction'}
        request = self.factory.put('/transactions/{}/'.format(self.transaction.pk), data, format='json')
        force_authenticate(request, user=self.user)
        response = transaction_detail(request, pk=self.transaction.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, 30.00)

    def test_transaction_detail_delete(self):
        request = self.factory.delete('/transactions/{}/'.format(self.transaction.pk), format='json')
        force_authenticate(request, user=self.user)
        response = transaction_detail(request, pk=self.transaction.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)
