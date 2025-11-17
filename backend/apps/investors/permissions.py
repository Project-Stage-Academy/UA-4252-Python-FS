from rest_framework import permissions
from .models import InvestorProfile

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
        investor_id = view.kwargs.get('investor_id') or view.kwargs.get('id')
        return request.user.id == investor_id


class IsInvestor(permissions.BasePermission):
    message = "Only users with an investor profile can perform this action."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return InvestorProfile.objects.filter(user=request.user).exists()


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "You must be the owner of this object or an administrator."
    
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_staff or 
            obj.investor == request.user
        )
