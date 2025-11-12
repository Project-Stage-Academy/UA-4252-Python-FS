from django.urls import path

from .views import SavedItemViewSet

urlpatterns = [
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
