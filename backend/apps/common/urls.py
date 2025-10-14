from django.urls import path
from . import views
from apps.startups.views import StartupPublicProfileViewSet

urlpatterns = [
    path('health/', views.GetHealth.as_view()),
    path('startups/<int:id>/', StartupPublicProfileViewSet.as_view({'get': 'retrieve'}), name='startupprofile-detail'),
]
