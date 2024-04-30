from django.test import TestCase
from core.models import BudgetCategory, Transaction

class TestBudgetCategoryModel(TestCase):
    def test_str_representation(self):
        category = BudgetCategory(name='Test Category', description='Test description', max_spend=100.00)
        self.assertEqual(str(category), 'Test Category')

class TestTransactionModel(TestCase):
    def test_str_representation(self):
        category = BudgetCategory(name='Test Category', description='Test description', max_spend=100.00)
        transaction = Transaction(owner=User.objects.create_user('testuser', 'test@example.com', 'password'), category=category, amount=50.00, description='Test transaction')
        self.assertEqual(str(transaction), 'Test Category - 50.00')
