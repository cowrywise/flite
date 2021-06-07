from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import AccountTransactionDetailView, AccountTransactionListView, UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet, P2PAPIView
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'phone', SendNewPhonenumberVerifyViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/accounts/<str:account_id>/transactions/',
         AccountTransactionListView.as_view(), name='transaction-list'),
    path('api/v1/account/<str:account_id>/transactions/<str:transaction_id>/',
         AccountTransactionDetailView.as_view(), name='transaction-detail'),
    path('api/v1/account/<str:sender_account_id>/transfers/<str:recipient_account_id>/',
         P2PAPIView.as_view(), name='p2p-create'),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

