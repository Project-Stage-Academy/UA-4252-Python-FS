from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    TrackingViewSet,
    InvestorTrackingListView,
    SavedItemViewSet,
)

router = DefaultRouter()
router.register(r'tracking', TrackingViewSet, basename='tracking')

investor_patterns = [
    path(
        'investors/<uuid:investor_id>/tracking/',
        InvestorTrackingListView.as_view(),
        name='investor-tracking-list'
    ),
    path(
        "<uuid:investor_id>/saved/",
        SavedItemViewSet.as_view({"post": "create"}),
        name="saved-item-create",
    ),
    path(
        "<uuid:investor_id>/saved/<int:saved_item_id>/",
        SavedItemViewSet.as_view({"delete": "destroy"}),
        name="saved-item-delete",
    ),
]

urlpatterns = investor_patterns + router.urls
