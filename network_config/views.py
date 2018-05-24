from network_config.models import *
from network_config.serializers import TenantSerializer, UserSerializer, DeviceSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from .permissions import IsDeviceOwnerGroupOrReadOnly, IsAdminOrReadOnly  # , IsDeviceOwnerGroup

from rest_framework.response import Response
from rest_framework import status

from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication


"""
NOTE: Permissions can be assigned for a view by importing custom permissions written in a separate
file and assigning these permissions as a list to permission_classes. However, since these permissions
are called when an object is created, a POST request does not work as expect with respect to the
assigned permissions. For specific permission(s) that need to work with a POST request, the create
function must be specifically defined when using a generics view and within the create function, user
must check for the required permissions. The TenantList class and the DeviceList class specify this functionality.
For further explanation: https://github.com/encode/django-rest-framework/issues/1103
"""


class TenantList(generics.ListCreateAPIView):
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def create(self, request, *args, **kwargs):
        """
        Verify that the POST has the request user as the admin
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        if request.user.is_staff:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        serializer.save()


class TenantDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def create(self, request, *args, **kwargs):
    #     """
    #     Verify that the POST has the request user as the admin
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #
    #     if request.user.is_staff:
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_create(serializer)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(status=status.HTTP_403_FORBIDDEN)
    #
    # def perform_create(self, serializer):
    #     # serializer.save(profile=self.request.user.profile)
    #
    #     # Below code is not working since tenant cannot be null.
    #     # But how can I create a user without tenant?
    #     if self.request.user.is_superuser:
    #         serializer.save(tenant=None)
    #     serializer.save()


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


"""
Note: get_queryset is another way to specify the queryset for the serializer to display.
In DeviceList, instead of allowing users access to all Devices, the get_queryset method
filters the list of devices that the user has access to based on the group(s) that the
user is a member of.
You can also use filter backends and create a custom filter in a separate file. This would
provide similar functionality to filtering using get_queryset.
"""


class DeviceList(generics.ListCreateAPIView):
    # queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = (IsDeviceOwnerGroupOrReadOnly, )
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        """
        This view should return a list of all the devices within the group that the user is in
        """
        usergroups = UserGroup.objects.filter(users=self.request.user)
        # __in is being used for filteration as usergroup can be a list of values
        return Device.objects.filter(owner_group__in=usergroups)

    """
    This create function is called for a every POST request. This function checks for two different
    types of permissions. The user must be of the same group as the owner group for which the user
    has posted the device. The user must also have the permission can_post_devices. If the user lacks
    either permission, the post request will be denied with a 403 Forbidden response thrown.
    """
    def create(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if UserGroup.objects.filter(users=request.user).filter(name=request.data.get("owner_group")).exists():

            if request.user.has_perm('network_config.can_post_devices'):
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        serializer.save()


"""
NOTE: Adding permissions to the permission classes directly to check for the owner group of the
user and the device causes unexpected problems. The IsDeviceOwnerGroup permission checks if the
user is part of a user group that the user intends to add the device into. But in a PUT statement, if
the owner_group needs to be changed, then the permission class needs to check the owner_group of
both the old object and the owner_group from the new request. This is currently not implemented.
This can be implemented by overwriting the def update function and checking for permissions. This is
similar to how the create functions were written but the internal permission checks and updating the
serializer can be different.
"""


class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )  # IsDeviceOwnerGroup
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

# class ProfileList(generics.ListAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
