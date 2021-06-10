from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the object owners

        return obj == request.user


class IsOwnerOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to view or edit.
    """
    def has_object_permission(self, request, view, obj):
        print(obj)
        return obj == request.user
