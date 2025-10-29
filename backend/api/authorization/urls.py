from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "auth/resend-verification/",
        views.ResendVerificationView.as_view(),
        name="resend-verification",
    ),
]
