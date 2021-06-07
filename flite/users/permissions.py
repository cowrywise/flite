from rest_framework import permissions
from .models import User

class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user
    
    """
    View level permission to enforce user only transacts on his account
    """
    def has_permission(self, request, view):
        user_id = view.kwargs['pk']

        try:
            user = User.objects.get(id=user_id)
        except:
            user = None

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if user:
                return user == request.user
            return False

class IsAccountOwner(permissions.BasePermission):
    """
    View level permission to allow only account owner make transactions
    """

    def has_permission(self, request, view):
        account_id = view.kwargs['account_id']
        try:
            user = User.objects.get(id=account_id)

            return user == request.user
        except:
            return False

class IsWalletOwner(permissions.BasePermission):
    """
    View level permission to allow only account owner make transactions
    used in the P2PAPIView
    """

    def has_permission(self, request, view):
        account_id = view.kwargs['sender_account_id']
        try:
            user = User.objects.get(id=account_id)

            return user == request.user
        except:
            return False