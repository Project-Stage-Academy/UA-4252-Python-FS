from rest_framework import permissions

class IsTrackingOwner(permissions.BasePermission):
    """
    A permission that checks whether the current user
    is the owner of the 'Tracking' object.
    """
    def has_object_permission(self, request, view, obj):
        return obj.investor == request.user

class IsInvestorSelf(permissions.BasePermission):
    """
    Allows access only if the `investor_id` in the URL
    matches the authenticated user's ID.
    """
    def has_permission(self, request, view):
        return request.user.id == view.kwargs.get('investor_id')