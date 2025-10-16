from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.contrib.auth import get_user_model
from django.conf import settings

from .serializers import RegistrationSerializer
from apps.startups.models import StartupProfile
from apps.investors.models import InvestorProfile

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

        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f'{settings.FRONTEND_URL}/verify/{uid}/{token}/'

        send_mail(
            subject='Verify your email',
            message=f'Please, verify your email by clicking: {verification_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

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
