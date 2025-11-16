from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrackingViewSet, 
    InvestorTrackingListView,
    InvestmentViewSet,
    InvestorInvestmentsListView
)


router = DefaultRouter()
router.register(r'tracking', TrackingViewSet, basename='tracking')
router.register(r'investments', InvestmentViewSet, basename='investment')

investor_patterns = [
    path(
        'investors/<uuid:investor_id>/tracking/',
        InvestorTrackingListView.as_view(),
        name='investor-tracking-list'
    ),
    path(
        'investors/<uuid:id>/investments/',
        InvestorInvestmentsListView.as_view(),
        name='investor-investments-list'
    ),
]

urlpatterns = investor_patterns + router.urls