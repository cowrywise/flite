from django.conf import settings
from django.db.models import base
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import (UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet, P2PTransferViewSet,
                          TransactionListViewSet, TransactionDetailsViewSet)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'signups', UserCreateViewSet, basename='signups')
router.register(r'phone', SendNewPhonenumberVerifyViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/<sender_account_id>/transfer/<recipient_account_id>/', P2PTransferViewSet.as_view(),
         name='p2p-transfer'),
    path('api/v1/accounts/<account_id>/transactions/', TransactionListViewSet.as_view(),
         name='transaction-list'),
    path('api/v1/account/<account_id>/transactions/<transaction_id>/',
         TransactionDetailsViewSet.as_view(), name='transaction-detail'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
