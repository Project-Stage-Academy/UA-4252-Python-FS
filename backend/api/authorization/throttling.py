from rest_framework.throttling import BaseThrottle
from django.core.cache import cache

class CommonRedisThrottle(BaseThrottle):
    def get_cache_key(self, request):
        ident = self.get_ident(request)
        return f"throttle:{ident}"

    def allow_request(self, request, view):
        rate, duration = 50, 60 # For running tests change rate.
        key = self.get_cache_key(request)

        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=duration)
            return True
        if current >= rate:
            return False
        cache.incr(key)
        return True

