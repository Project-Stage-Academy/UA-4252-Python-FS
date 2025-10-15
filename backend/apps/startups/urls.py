from django.urls import path
from . import views
from apps.startups.views import StartupPublicProfileViewSet

urlpatterns = [
    path('<int:id>/', StartupPublicProfileViewSet.as_view({'get': 'retrieve'}), name='startupprofile-detail'),
]
