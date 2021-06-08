from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from flite.users.views import (
    UserViewSet,
    UserCreateAndListViewSet,
    SendNewPhoneNumberVerifyViewSet,
    DepositViewSet,
    WithdrawalViewSet,
    PeerToPeerTransferViewSet,
    FetchPaginatedTransactionsForUserViewSet,
    FetchSingleTransactionsForUserView,
    # FetchSingleTransactionsForUserViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateAndListViewSet)
router.register(r'phone', SendNewPhoneNumberVerifyViewSet)
router.register(r'users/(?P<user_id>[0-9A-Za-z\-]+)/deposits',
                DepositViewSet, basename='transaction-deposit')
router.register(r'users/(?P<user_id>[0-9A-Za-z\-]+)/withdrawals',
                WithdrawalViewSet, basename='transaction-withdrawal')
router.register(r'account/(?P<sender_account_id>[0-9A-Za-z\-]+)/transfers/(?P<recipient_account_id>[0-9A-Za-z\-]+)',  # noqa: E501
                PeerToPeerTransferViewSet,
                basename='peer_to_peer_transfer')
router.register(r'account/(?P<account_id>[0-9A-Za-z\-]+)/transactions',
                FetchPaginatedTransactionsForUserViewSet,
                basename='transaction')

urlpatterns = [
                  path('admin/', admin.site.urls),
                  #   path('jet_api/', include('jet_django.urls')),
                  path('api/v1/', include(router.urls)),
                  path('api/v1/account/<str:account_id>/transactions/<str:transaction_id>/',
                       FetchSingleTransactionsForUserView.as_view(), name='transaction-detail'),
                  path('api-token-auth/', views.obtain_auth_token),
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                  # the 'api-root' from django rest-frameworks default router
                  # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
                  re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
