from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.contrib.auth import get_user_model
from django.conf import settings
from .serializers import (
    RegistrationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .emails import send_password_reset_email

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


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
        email = request.data.get('email')
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                # just return 201 without creating a new user
                return Response({
                    'detail': 'Verification email sent.'
                }, status=status.HTTP_201_CREATED)

        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        if settings.DEBUG:
            verification_link = f'http://localhost:8000/api/auth/verify/{uid}/{token}/'
        else:
            verification_link = f'{settings.FRONTEND_URL}/verify/{uid}/{token}/'

        try:
            send_mail(
                subject='Verify your email',
                message=f'Please, verify your email by clicking: {verification_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'Email sending failed for user {user.email}: {e}')

        return Response({
            'id': user.id,
            'email': user.email,
            'detail': 'Verification email sent.'
        },
            status=status.HTTP_201_CREATED
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
                return Response({
                    'detail': 'Email already verified. You can log in.'
                }, status=status.HTTP_200_OK)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()

                return Response({
                    'detail': 'Email verified successfully.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': 'Invalid or expired token.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, ValueError, TypeError):
            return Response({
                'detail': 'Invalid verification link.'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Endpoint to request a password reset.
    POST /api/auth/password-reset/
    Request body:
    {
        "email": "user@example.com"
    }
    Sends an email with a link to reset the password if a user with
    the provided email exists.
    Always returns 200 with a generic message to prevent account enumeration.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(
                email=serializer.validated_data['email']
            )

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            reset_link = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'

            send_password_reset_email(user, reset_link)

        # always return success to avoid account enumeration
        return Response(
            {'detail': 'Password reset link sent.'},
            status=status.HTTP_200_OK
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
    Sets a new password for a user, if provided uid and token are valid
    and passwords are matching.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK
        )
