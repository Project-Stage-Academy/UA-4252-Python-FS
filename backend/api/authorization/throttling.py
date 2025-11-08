from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle

RATE = getattr(settings, "COMMON_REDIS_THROTTLE_RATE", 6)
DURATION = getattr(settings, "COMMON_REDIS_THROTTLE_DURATION", 60)

EMAIL_RATE = getattr(settings, "EMAIL_THROTTLE_RATE", 6)
EMAIL_DURATION = getattr(settings, "EMAIL_THROTTLE_DURATION", 3600)

class CommonRedisThrottle(BaseThrottle):
    def get_cache_key(self, request):
        ident = self.get_ident(request)
        return f"throttle:{request.path}:{ident}"

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

class EmailThrottle(BaseThrottle):
    def get_cache_key(self, request, view):
        email = request.data.get("email")

        if not email:
            return None

        ident = email.strip().lower()
        
        return f"throttle:email:{request.path}:{ident}"

    def allow_request(self, request, view):
        key = self.get_cache_key(request, view)
        if key is None:
            return True 

        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=EMAIL_DURATION)
            return True
        if current >= EMAIL_RATE:
            return False
        try:
            cache.incr(key)
        except Exception:
            current = cache.get(key) or 0
            cache.set(key, int(current) + 1, timeout=EMAIL_DURATION)
        return True