from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'phone', SendNewPhonenumberVerifyViewSet)
schema_view = get_schema_view(
    openapi.Info(
        title="Flite API",
        default_version="v1",
        description="API for Flite",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="flite@cowrywise.com"),
    ),
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include([
        path('', include(router.urls)),  # Include URLs from your router
        path('', include('flite.core.urls')),  # Include URLs from your app
    ])),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(
        "api/playground/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

