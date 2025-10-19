from rest_framework.routers import DefaultRouter
from .views import StartupPublicProfileViewSet
from django.urls import path, include
router = DefaultRouter()
router.register(r'startups', StartupPublicProfileViewSet, basename='startup')

urlpatterns = [
    path("", include(router.urls)),
]