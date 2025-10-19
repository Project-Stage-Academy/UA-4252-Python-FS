from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import UserLoginSerializer



class LoginView(APIView):
    throttle_scope = "auth_login"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response({'error': 'Wrong email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = TokenObtainPairSerializer.get_token(user)
        resp = Response({"user": {"id": user.id, "email": user.email}}, status=status.HTTP_200_OK)
        resp.set_cookie("access_token", str(tokens.access_token), httponly=True, secure=False, samesite="Strict")
        resp.set_cookie("refresh_token", str(tokens), httponly=True, secure=False, samesite="Strict")
        return resp


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        resp = Response(status=status.HTTP_204_NO_CONTENT)
        resp.delete_cookie('refresh_token')
        resp.delete_cookie('access_token')
        return resp


