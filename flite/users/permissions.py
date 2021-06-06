from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsTransactionOwner(permissions.BasePermission):
    """
    if the arg (pk) provided can perform action at viewpoint.
    """

    def has_permission(self, request, view):
        arg = (view.kwargs.get('user_id') or view.kwargs.get('account_id') or view.kwargs.get('sender_account_id'))
        return arg == str(request.user.id)

