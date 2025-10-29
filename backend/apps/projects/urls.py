from django.urls import path, include
from rest_framework_nested import routers

from apps.startups.views import StartupPublicProfileViewSet

from .views import ProjectViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"startups", StartupPublicProfileViewSet, basename="startups")
router.register(r"projects", ProjectViewSet, basename="startup-projects")

urlpatterns = [
    path('', include(projects_router.urls)),
    path('', include(router.urls)),
]
