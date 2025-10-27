from django.urls import path

from .views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "verify/<str:uid>/<str:token>/", VerifyEmailView.as_view(), name="verify-email"
    ),
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
