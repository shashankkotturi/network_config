from rest_framework import permissions
from .models import *


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit a tenant
    """

    def has_permission(self, request, view):

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # Not including POST method which is restricted as written in views.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write(and other) permissions are only allowed to admins
        return request.user.is_staff


class IsDeviceOwnerGroupOrReadOnly(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are
     - owner may GET, PUT, POST, DELETE
     - nobody else can access except for GET
     """

    def has_object_permission(self, request, view, obj):

        if request.method == 'GET':
            return True
        return UserGroup.objects.filter(users=request.user).filter(pk=obj.owner_group.pk).exists()


class IsDeviceOwnerGroup(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('network_config.can_post_devices'):
            return UserGroup.objects.filter(users=request.user).filter(pk=obj.owner_group.pk).exists()

        return False


# class HasDevicePostPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if request.user.has_perm('network_config.can_post_devices'):
#             return True
#         return False
