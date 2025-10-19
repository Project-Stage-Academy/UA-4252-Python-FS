from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserLoginSerializer

class LoginView(APIView):
    """ Authenticates user, generates refresh/access tokens.
    Throttle limited in settings.py with throttle_scope. """
    throttle_scope = 'auth_login'

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])

        if user is None:
            return Response({'error': 'Wrong email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = TokenObtainPairSerializer.get_token(user) # Possibility to add new field to the token.

        response = Response({
             "user": {
                "id": user.id,
                "email": user.email,
                }
            }, status=status.HTTP_200_OK)

        response.set_cookie(key='access_token',
                            value=str(tokens.access_token),
                            httponly=True,
                            secure=False, # While still in development, True when in prod.
                            samesite='Strict')

        response.set_cookie(key='refresh_token',
                            value=str(tokens),
                            httponly=True,
                            secure=False, # While still in development, True when in prod.
                            samesite='Strict')

        return response

        
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        try:
            token.blacklist()
            response = Response(status=status.HTTP_204_NO_CONTENT)

            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')

            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


