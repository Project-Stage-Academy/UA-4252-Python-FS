from rest_framework_nested import routers

from apps.startups.views import StartupPublicProfileViewSet

from .views import ProjectViewSet

router = routers.SimpleRouter()
router.register(r"startups", StartupPublicProfileViewSet, basename="startups")

projects_router = routers.NestedSimpleRouter(router, r"startups", lookup="startup")
projects_router.register(r"projects", ProjectViewSet, basename="startup-projects")

urlpatterns = router.urls + projects_router.urls
