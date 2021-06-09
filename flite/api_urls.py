from django.urls import path

from flite.users.views import get_user_list, deposit_account, withdraw_account,\
    transfer

urlpatterns = [
    path('users/<str:user_id>/deposits',  deposit_account),
    path('users/<str:user_id>/withdrawals',  withdraw_account),
    path('account/<str:sender_account_id>/transfers/recipient_account_id',  transfer),
    ]