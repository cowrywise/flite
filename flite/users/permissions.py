from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsUserTransactionOnly(permissions.BasePermission):
    """
    Allows access only users that owns a particular transaction.
    """

    def has_object_permission(self, request, view, obj):
        """
        check object level permission
        Args:
            request:
            view:
            obj:

        Returns:

        """
        return obj.owner_id == request.user.id
