from django.urls import path

from flite.users.views import get_user_list, deposit_account

urlpatterns = [
    path('users/<str:user_id>/deposits',  deposit_account),
    ]