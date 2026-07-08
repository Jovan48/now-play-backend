from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        owner = None
        if hasattr(obj, 'artist') and getattr(obj, 'artist', None) is not None:
            owner = getattr(obj.artist, 'created_by', None)
        elif hasattr(obj, 'created_by'):
            owner = getattr(obj, 'created_by', None)

        return owner is not None and request.user.is_authenticated and owner == request.user
