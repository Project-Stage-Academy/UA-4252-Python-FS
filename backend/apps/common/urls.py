from django.urls import path

from .views import LandingContentAPIView, health

general_patterns = [
    path("", health, name="health"),
]

content_patterns = [
    path("landing/", LandingContentAPIView.as_view(), name="landing-content"),
]
