from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it or admins to read and write all objects.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # Check if the user is the owner of the object or if the object is a Template
            return obj.owner == request.user or isinstance(obj, Template) or request.user.is_staff
        # Write permissions are only allowed to the owner of the snippet or admin users.
        return obj.owner == request.user or request.user.is_staff
