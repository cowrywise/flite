from django.urls import path

from flite.users.views import deposit_account, withdraw_account,\
    transfer, UserList

urlpatterns = [
    path('users', UserList.as_view()),
    path('users/<str:user_id>', UserList.as_view()),
    path('users/<str:user_id>/deposits', deposit_account),
    path('users/<str:user_id>/withdrawals',  withdraw_account),
    path('account/<str:sender_account_id>/transfers/<str:recipient_account_id>',  transfer),
    ]
