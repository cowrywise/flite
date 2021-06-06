from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import (
    UserViewSet,
    UserCreateViewSet,
    SendNewPhonenumberVerifyViewSet)
from flite.core.views import (
    DepositsViewSet,
    WithdrawalsViewSet,
    P2PTransferViewSet,
    TransactionListViewSet,
    RetrieveTransactionViewSet)


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'phone', SendNewPhonenumberVerifyViewSet)
router.register(r'users/(?P<user_id>[0-9A-Za-z\-]+)/deposits',
    DepositsViewSet,
    basename='deposits')
router.register(r'users/(?P<user_id>[0-9A-Za-z\-]+)/withdrawals',
    WithdrawalsViewSet,
    basename='withdrawals')
router.register(r'account/(?P<sender_account_id>[0-9A-Za-z\-]+)/withdrawals/(?P<recipient_account_id>[0-9A-Za-z\-]+)',
    P2PTransferViewSet,
    basename='P2PTransfer')
router.register(r'account/(?P<account_id>[0-9A-Za-z\-]+)/transactions',
    TransactionListViewSet,
    basename='transaction')
router.register(r'account/(?P<account_id>[0-9A-Za-z\-]+)/transactions/(?P<transaction_id>[0-9A-Za-z\-]+)',
    RetrieveTransactionViewSet,
    basename='single-transactions')


urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
