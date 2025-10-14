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
        if serializer.is_valid():

            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])

            if user is not None:
                tokens = TokenObtainPairSerializer.get_token(user) # Possibility to add new field to the token.

                response = Response({
                     # "access": str(tokens.access_token),
                     # "refresh": str(tokens),
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
            else:
                return Response({'error':'Wrong email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error':'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        token = RefreshToken(refresh_token)
        if token:
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


