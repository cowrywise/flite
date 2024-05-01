

from django.test import TestCase
from django.core import mail
from flite.users.models import User
from flite.core.models import BudgetCategory, Transaction
from flite.core.tasks import check_budget_threshold
from decimal import Decimal

class TestCheckBudgetThresholdTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = BudgetCategory.objects.create(name='Test Category', description='Test description', max_spend=100.00)

    def test_check_budget_threshold_below_threshold(self):
        # Create a transaction that does not exceed the budget threshold
        Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('40.00'), description='Test transaction')
        self.assertEqual(len(mail.outbox), 0)  # Assert no emails sent

    def test_check_budget_threshold_exceeds_threshold(self):
        # Create a transaction that exceeds the budget threshold
        Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('60.00'), description='Test transaction')
        transaction = Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('10.00'), description='Test transaction')
        check_budget_threshold(transaction.id)
        self.assertEqual(len(mail.outbox), 1)  # Assert one email sent
        self.assertEqual(mail.outbox[0].subject, 'Budget threshold warning')
        self.assertRegex(mail.outbox[0].body, r'Your spending for Test Category has reached 70.00')

    def test_check_budget_threshold_multiple_transactions(self):
        # Create multiple transactions that exceed the budget threshold
        Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('30.00'), description='Test transaction')
        Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('40.00'), description='Test transaction')
        transaction = Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('10.00'), description='Test transaction')
        check_budget_threshold(transaction.id)
        self.assertEqual(len(mail.outbox), 1)  # Assert one email sent (cumulative spending)
        self.assertEqual(mail.outbox[0].subject, 'Budget threshold warning')
        self.assertRegex(mail.outbox[0].body, r'Your spending for Test Category has reached 80.00')

    def test_check_budget_threshold_multiple_categories(self):
        # Create multiple budget categories and test emails for each
        category2 = BudgetCategory.objects.create(name='Test Category 2', description='Test description 2', max_spend=200.00)
        Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal('60.00'), description='Test transaction')
        transaction = Transaction.objects.create(owner=self.user, category=self.category, amount=Decimal)
