from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission: GET: allowed based on visibility"""

    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access this specific profiles"""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return obj.user == request.user
