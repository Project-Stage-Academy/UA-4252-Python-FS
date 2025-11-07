import hashlib

from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle


class CommonRedisThrottle(BaseThrottle):
    """
    Redis-based throttle that limits requests by a combination of:
        - user IP address
        - email (if provided)

    RATE: allowed requests per duration
    DURATION: window in minutes
    """

    def _get_rate(self):
        return getattr(settings, "COMMON_REDIS_THROTTLE_RATE", 60)

    def _get_duration(self):
        return getattr(settings, "COMMON_REDIS_THROTTLE_DURATION", 60)

    def get_cache_key(self, request):
        ident = self.get_ident(request)
        email = request.data.get('email')
        email_hash = (
            hashlib.sha256((email or '').encode()).hexdigest() if email else 'no-email'
        )
        return f"throttle:{request.path}:{ident}:{email_hash}"

    def allow_request(self, request, view):
        key = self.get_cache_key(request)

        duration = self._get_duration()
        rate = self._get_rate()

        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=duration)
            return True
        if current >= rate:
            return False
        try:
            cache.incr(key)
        except Exception:
            current = cache.get(key) or 0
            cache.set(key, int(current) + 1, timeout=duration)
        return True
