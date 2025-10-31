import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .emails import send_password_reset_email
from .serializers import (
    CheckEmailSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
    UserLoginSerializer,
)
from .throttling import CommonRedisThrottle

logger = logging.getLogger(__name__)

User = get_user_model()


class LoginView(APIView):
    """Authenticates user, generates refresh/access tokens.
    Throttle limited in throttling.py with throttle_classes, using Redis to count."""

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

        tokens = TokenObtainPairSerializer.get_token(user)

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
        except Exception as e:
            logger.exception("Failed to send verification email: %s", e)
            return Response(
                {"detail": "Failed to send email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    User registration endpoint supporting both startup and investor roles.
    POST /api/auth/register/

    Anti-enumeration Policy:
    - Returns HTTP 201 for all registration attempts (success or duplicate)
    - Prevents attackers from discovering registered emails
    - Duplicate emails are handled in serializer validation
    """

    def post(self, request):
        """
        Register a new user with role-specific profile.
        Returns:
            201: User created, verification email sent
            400: Validation errors
        """
        email = request.data.get("email")
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                # just return 201 without creating a new user
                return Response(
                    {"detail": "Verification email sent."},
                    status=status.HTTP_201_CREATED,
                )

        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        if settings.DEBUG:
            verification_link = f"http://localhost:8000/api/auth/verify/{uid}/{token}/"
        else:
            verification_link = f"{settings.FRONTEND_URL}/verify/{uid}/{token}/"

        try:
            send_mail(
                subject="Verify your email",
                message=f"Please, verify your email by clicking: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Email sending failed for user {user.email}: {e}")

        return Response(
            {"id": user.id, "email": user.email, "detail": "Verification email sent."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """
    Email verification endpoint.
    GET /api/auth/verify/<uid>/<token>/
    Activates user account after successful email verification.
    """

    def get(self, request, uid, token):
        """
        Verify user's email address.
        Returns:
            200: Email verified successfully
            400: Invalid or expired token
        """
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)

            if user.is_active:
                return Response(
                    {"detail": "Email already verified. You can log in."},
                    status=status.HTTP_200_OK,
                )

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()

                return Response(
                    {"detail": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetRequestView(APIView):
    """
    Endpoint to request a password reset.
    POST /api/auth/password-reset/
    Request body:
    {
        "email": "user@example.com"
    }
    Returns:
        200: Provided email has valid format (enumeration policy).
             If user with given email exists, sends an email with
             password reset link.
        400: Validation errors.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

            send_password_reset_email(user, reset_link)

        # always return success to avoid account enumeration
        return Response(
            {"detail": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Endpoint to confirm password reset and set a new password.
    POST /api/auth/password-reset/confirm/
    Request body:
    {
        "uid": "<encoded user id>",
        "token": "<reset token>",
        "new_password": "NewStrongP@ss1",
        "re_new_password": "NewStrongP@ss1"
    }
    Returns:
        200: Sets a new password for a user.
        400: Validation errors.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class CheckEmailView(APIView):
    """
    Safe backend endpoint that the frontend can call (debounced)
    to check whether an email is already registered.
    POST /api/auth/check-email/
    Request body:
    {
        "email": "someemail@gmail.com"
    }
    Response:
        'available': 'false' - User exists, 200
        'available': 'true' - No user with this email exists., 200
        400: Bad Request body
        429: Too Many Requests
    """

    throttle_classes = [CommonRedisThrottle]

    def post(self, request):
        serializer = CheckEmailSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            User.objects.get(email=email)
            return Response({'available': 'false'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'available': 'true'}, status=status.HTTP_200_OK)
