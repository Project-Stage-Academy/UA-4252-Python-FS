from django.urls import path

from .views import health
from .views import LandingContentAPIView


general_patterns = [
    path("", health, name="health"),
]

content_patterns = [
    path("landing/", LandingContentAPIView.as_view(), name="landing-content"),
]