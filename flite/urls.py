from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework_nested import routers
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet, AccountViewSet, TransactionViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'register', UserCreateViewSet, basename="register")
router.register(r'account', AccountViewSet)

transaction_router = routers.NestedDefaultRouter(router, r'account', lookup="account")
transaction_router.register(r'transactions', TransactionViewSet, basename='account-transactions')


urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls + transaction_router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

