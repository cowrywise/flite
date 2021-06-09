from django.urls import path

from flite.users.views import get_user_list

urlpatterns = [
    path('users/<str:user_id>',  get_user_list),
    ]