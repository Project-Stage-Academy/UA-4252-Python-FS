from django.urls import path

from .views import StartupsProjectsElasticSearchView

urlpatterns = [
    path(
        "",
        StartupsProjectsElasticSearchView.as_view({"get": "list"}),
        name="search",
    ),
]
