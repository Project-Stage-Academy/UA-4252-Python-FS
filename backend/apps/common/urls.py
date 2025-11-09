from django.urls import path

from .views import health
from .views import LandingContentAPIView

urlpatterns = [
    path("", health, name="health"),
    path(
        "landing/",
        LandingContentAPIView.as_view(),
        name="landing-content",
    ),
]
