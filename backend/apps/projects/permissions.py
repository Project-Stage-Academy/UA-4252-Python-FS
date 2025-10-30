from rest_framework import permissions

from apps.startups.models import StartupProfile


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission: GET: allowed based on visibility"""

    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access this specific projects"""
        if request.method in permissions.SAFE_METHODS:
            if obj.visibility == 'public' and not obj.is_deleted:
                return True
            if not request.user.is_authenticated:
                return False
            if obj.startup.user == request.user:
                return True
            if obj.visibility == 'unlisted' and not obj.is_deleted:
                return True

            return False
        return obj.startup.user == request.user


class IsStartupOwner(permissions.BasePermission):
    """Permission to check if user is the owner of the startup"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        startup_pk = view.kwargs.get('startup_pk')
        if not startup_pk:
            return False

        try:
            startup = StartupProfile.objects.get(pk=startup_pk)
            return startup.user == request.user
        except StartupProfile.DoesNotExist:
            return False
