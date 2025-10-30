from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle

RATE = getattr(settings, "COMMON_REDIS_THROTTLE_RATE", 60)
DURATION = getattr(settings, "COMMON_REDIS_THROTTLE_DURATION", 60)


class CommonRedisThrottle(BaseThrottle):
    """
    Redis-based throttle that limits requests by a combination of:
        - user IP address
        - email (if provided)

    RATE: allowed requests per duration
    DURATION: window in minutes
    """

    def get_cache_key(self, request):
        ident = self.get_ident(request)
        email = request.data.get('email')
        return f"throttle:{request.path}:{ident}:{email or 'no-email'}"

    def allow_request(self, request, view):
        key = self.get_cache_key(request)

        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=DURATION)
            return True
        if current >= RATE:
            return False
        try:
            cache.incr(key)
        except Exception:
            current = cache.get(key) or 0
            cache.set(key, int(current) + 1, timeout=DURATION)
        return True
