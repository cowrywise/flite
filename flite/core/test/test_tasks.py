from django.test import TestCase
from core.tasks import check_budget_threshold
from django.core import mail
from core.models import BudgetCategory, Transaction
from django.contrib.auth.models import User

class TestCheckBudgetThresholdTask(TestCase):
    def setUp(self):
        self.category = BudgetCategory.objects.create(name='Test Category', description='Test description', max_spend=100.00)
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')

    def test_check_budget_threshold(self):
        Transaction.objects.create(owner=self.user, category=self.category, amount=50.00, description='Test transaction')
        check_budget_threshold()
        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Budget threshold warning')
