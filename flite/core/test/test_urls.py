from django.test import SimpleTestCase
from django.urls import reverse, resolve
from flite.core import views

class TestUrls(SimpleTestCase):

    def test_budget_category_list_url(self):
        path = reverse('budget_category_list')
        self.assertEqual(resolve(path).func, views.budget_category_list)

    def test_budget_category_detail_url(self):
        path = reverse('budget_category_detail', kwargs={'pk': 1})
        self.assertEqual(resolve(path).func, views.budget_category_detail)

    def test_transaction_list_url(self):
        path = reverse('transaction_list')
        self.assertEqual(resolve(path).func, views.transaction_list)

    def test_transaction_detail_url(self):
        path = reverse('transaction_detail', kwargs={'pk': 1})
        self.assertEqual(resolve(path).func, views.transaction_detail)