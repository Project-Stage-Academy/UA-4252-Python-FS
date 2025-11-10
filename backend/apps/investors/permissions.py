from rest_framework import permissions

class IsTrackingOwner(permissions.BasePermission):
    """
    Дозвіл, який перевіряє, чи є поточний користувач
    власником 'Tracking' об'єкта.
    """
    def has_object_permission(self, request, view, obj):
        return obj.investor == request.user