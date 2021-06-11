from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet, P2PTransferView, TransactionViewSet, GetTransactionView
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'signup', UserCreateViewSet, basename='signup')
router.register(r'phone', SendNewPhonenumberVerifyViewSet),
router.register(r'accounts', TransactionViewSet, base_name='accounts')



urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/<sender_account_id>/transfer/<recipient_account_id>/', P2PTransferView.as_view(), name='p2p_transfer'),
    path('api/v1/account/<account_id>/transactions/<transaction_id>/', GetTransactionView.as_view(), name='account_transaction'),
    # /account/:account_id/transactions/:transaction_id

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

