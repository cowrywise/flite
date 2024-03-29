from django.urls import path
from .views import (
    UserDetailView,
    UsersListView,
    UserDepositView,
    UserWithdrawalView,
    P2PTransferView,
    TransactionsListView,
    TransactionDetailView
)

urlpatterns = [
    path('users/', UsersListView.as_view(), name='users'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:user_id>/deposits/', UserDepositView.as_view(), name='user-deposits'),
    path('users/<uuid:user_id>/withdrawals/', UserWithdrawalView.as_view(), name='user-withrawals'),
    path('account/<uuid:sender_account_id>/transfers/<uuid:recipient_account_id>/', P2PTransferView.as_view(), name='p2p-transfer'),
    path('account/<uuid:account_id>/transactions/', TransactionsListView.as_view(), name='transactions-list'),
    path('account/<uuid:account_id>/transactions/<str:transaction_id>/', TransactionDetailView.as_view(), name='transactions-detail'),
]