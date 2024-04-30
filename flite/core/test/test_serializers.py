from django.test import TestCase
from nose.tools import ok_, eq_
from .serializers import BudgetCategorySerializer, TransactionSerializer
from .models import BudgetCategory, Transaction
from django.contrib.auth.models import User

class TestBudgetCategorySerializer(TestCase):
    def setUp(self):
        self.category_data = {'name': 'Test Category', 'description': 'Test description', 'max_spend': 100.00}
        self.category = BudgetCategory.objects.create(**self.category_data)
        self.serializer = BudgetCategorySerializer(instance=self.category)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'name', 'description', 'max_spend'])

    def test_name_field_content(self):
        data = self.serializer.data
        eq_(data['name'], self.category_data['name'])

class TestTransactionSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = BudgetCategory.objects.create(name='Test Category', description='Test description', max_spend=100.00)
        self.transaction_data = {'category': self.category.id, 'amount': 50.00, 'description': 'Test transaction', 'owner': self.user.id}
        self.transaction = Transaction.objects.create(**self.transaction_data)
        self.serializer = TransactionSerializer(instance=self.transaction)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'category', 'amount', 'description', 'owner', 'date'])

    def test_amount_field_content(self):
        data = self.serializer.data
        eq_(data['amount'], str(self.transaction_data['amount']))