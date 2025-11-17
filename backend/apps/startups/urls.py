from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from apps.projects.views import ProjectViewSet

from .views import StartupPublicProfileViewSet

router = DefaultRouter()
router.register('', StartupPublicProfileViewSet, basename='startup')

projects_router = routers.NestedDefaultRouter(router, r"", lookup="startup")
projects_router.register(r"projects", ProjectViewSet, basename="startup-projects")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
]
