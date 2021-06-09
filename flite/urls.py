from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import (
    UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet, 
    UserTransactionViewSet, DepositWithdrawalViewSet,
    UserTransactionAllViewSet)
router = DefaultRouter()
router.register(r'users', UserCreateViewSet)
router.register(r'users', UserViewSet)
router.register(r'users', DepositWithdrawalViewSet, basename="deposits")
router.register(r'phone', SendNewPhonenumberVerifyViewSet)
router.register(r'account', UserTransactionAllViewSet, basename="account")


single_transactions = UserTransactionViewSet.as_view({
    'get': 'single_transactions'
})
p2p_transfer = UserTransactionViewSet.as_view({
    'post': 'p2p_transfer'
})

urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/account/<uuid:pk>/transactions/<uuid:transaction_id>/', single_transactions, name='single_transactions'),
    path('api/v1/account/<uuid:sender_account_id>/transfers/<uuid:receipient_id>/', p2p_transfer, name='p2p_transfer'),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

