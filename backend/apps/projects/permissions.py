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
            if obj.visibility == 'public':
                return True
            if obj.visibility == 'unlisted':
                return request.user.is_authenticated
            if obj.visibility == 'private':
                return (
                    request.user.is_authenticated and obj.startup.user == request.user
                )
            return False

        return obj.startup.user == request.user


class IsStartupOwner(permissions.BasePermission):
    """Permission to check if user is the owner of the startup"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user:
            return False

        if view.action == 'create':
            startup_pk = view.kwargs.get('startup_pk')
            if not startup_pk:
                return False

            try:
                startup = StartupProfile.objects.get(pk=startup_pk)
                return startup.user == request.user
            except StartupProfile.DoesNotExist:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        return obj.startup.user == request.user


class CanViewProject(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.visibility == 'public':
            return True
        if obj.visibility == 'private':
            return request.user.is_authenticated and obj.startup.user == request.user
        if obj.visibility == 'unlisted':
            return request.user.is_authenticated
        return False


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            can_view = CanViewProject()
            return can_view.has_object_permission(request, view, obj)
        return obj.startup.user == request.user
