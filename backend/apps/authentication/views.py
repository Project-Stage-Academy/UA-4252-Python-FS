from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .serializers import RegistrationSerializer
from .models import User


class RegisterView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        if User.objects.filter(email=email).exists():
            return Response({
                'detail': 'Verification email sent.'
            }, status=status.HTTP_200_OK)

        user = serializer.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_link = f'https://mail.google.com/api/auth/verify/{uid}/{token}/'
        send_mail(
            subject='Verify your email',
            message=f'Please, verify your email by clicking: {verification_link}'),
        from_email = 'noreply',
        recipient_list = [user.email],
        fail_silently = False,
        )

        return Response({
            'id': user.id,
            'email': user.email,
            'detail': 'Verification email sent.'
        },
            status=status.HTTP_201_CREATED
        )
