from django.urls import path
from . import views

urlpatterns = [
    path('budget_categories/', views.budget_category_list, name='budget_category_list'),
    path('budget_categories/<int:pk>/', views.budget_category_detail, name='budget_category_detail'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
]