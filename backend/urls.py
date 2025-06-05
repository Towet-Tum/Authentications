from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AuthViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
]
