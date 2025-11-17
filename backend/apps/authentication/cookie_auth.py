import logging

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request):
        header = self.get_header(request)

        if header is not None:
            # try to get the token from the Authorization header first
            token = self.get_raw_token(header)
        else:
            # check for token in cookies
            token = request.COOKIES.get("access_token")

        if token is not None:
            try:
                validated_token = self.get_validated_token(token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, TokenError) as e:
                logger.error(f"Token validation error: {str(e)}")

        return None
