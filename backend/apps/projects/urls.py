from django.urls import path, include
from rest_framework_nested import routers
from apps.startups.views import StartupPublicProfileViewSet
from .views import ProjectViewSet

router = routers.SimpleRouter()
router.register(r'startups', StartupPublicProfileViewSet, basename='startups')

projects_router = routers.NestedSimpleRouter(router, r'startups', lookup='startup')
projects_router.register(r'projects', ProjectViewSet, basename='startup-projects')

urlpatterns = [
    path('', include(projects_router.urls)),
    path('projects/<uuid:pk>/',
         ProjectViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy',
         }),
         name='project-detail'),
    path('', include(router.urls)),
]
