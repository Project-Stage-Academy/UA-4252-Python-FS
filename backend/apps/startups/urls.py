from rest_framework.routers import DefaultRouter
from .views import StartupPublicProfileViewSet

router = DefaultRouter()
router.register(r'startups', StartupPublicProfileViewSet, basename='startup')

urlpatterns = router.urls