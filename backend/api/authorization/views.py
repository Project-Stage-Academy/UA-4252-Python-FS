import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User

from .serializers import UserLoginSerializer
from .throttling import CommonRedisThrottle

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """Authenticates user, generates refresh/access tokens.
    Throttle limited in settings.py with throttle_scope."""

    throttle_classes = [CommonRedisThrottle]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"error": "Wrong email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = TokenObtainPairSerializer.get_token(
            user
        )  # Possibility to add new field to the token.

        response = Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                }
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(tokens.access_token),
            httponly=True,
            secure=False,  # While still in development, True when in prod.
            samesite="Strict",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(tokens),
            httponly=True,
            secure=False,  # While still in development, True when in prod.
            samesite="Strict",
        )

        return response


class LogoutView(APIView):
    """
    Gets token from cookies, blacklisting it, deleting token from cookies.
    """

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        try:
            token.blacklist()
            response = Response(status=status.HTTP_204_NO_CONTENT)

            response.delete_cookie("refresh_token")
            response.delete_cookie("access_token")

            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """
    Generates access token for link,
    sends mail with verification link.
    """

    throttle_classes = [CommonRedisThrottle]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"detail": "Necessary fields are missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"detail": "Account was already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist:
            return Response(status=status.HTTP_200_OK)  # 400 for test

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.id))

        verification_link = (
            f"{settings.FRONTEND_URL}/api/auth/verify-email/{uid}/{token}/"
        )

        try:
            send_mail(
                subject="Verify your email",
                message=f"Please, verify your email by clicking: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Failed to send verification email")

        return Response(status=status.HTTP_200_OK)
