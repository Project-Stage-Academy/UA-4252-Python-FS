from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackingViewSet, InvestorTrackingListView


router = DefaultRouter()
router.register(r'tracking', TrackingViewSet, basename='tracking')

investor_patterns = [
    path(
        'investors/<uuid:investor_id>/tracking/',
        InvestorTrackingListView.as_view(),
        name='investor-tracking-list'
    ),
]

urlpatterns = investor_patterns + router.urls