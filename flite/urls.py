from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from flite.account.views import (AccountViewSet, BankTransferViewSet,
                                 BankViewSet, CardTransferViewSet, CardViewSet,
                                 P2PTransferViewSet)
from flite.config.swagger_api_docs import schema_view
from flite.users.views import SendNewPhonenumberVerifyViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'bank', BankViewSet, basename="bank")
router.register(r'card', CardViewSet, basename="card")
router.register(r'account', AccountViewSet, basename="account")
router.register(r'cardtransfer', CardTransferViewSet, basename="cardtransfer")
router.register(r'p2ptransfer', P2PTransferViewSet, basename="p2ptransfer")
router.register(r'banktransfer', BankTransferViewSet, basename="banktransfer")
router.register(r'phone', SendNewPhonenumberVerifyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),

    # Swagger docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(
        r'^$',
        RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
