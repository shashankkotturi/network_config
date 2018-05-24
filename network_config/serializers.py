from rest_framework import serializers
from .models import Tenant, Device, UserGroup  # , Profile
from django.contrib.auth.models import User

"""
Model Serializers have built in functionality that automatically relays information based on 
the request made by the user.
"""


class TenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant
        fields = ('id', 'name', 'is_active')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active', 'username')


"""
Attributes that have a foreign relation must be specified before the meta class is specified.
Foreign relations in serializers can be specified in many different ways.
Django Rest Documentation on Serializer Relations: http://www.django-rest-framework.org/api-guide/relations/

"""


class DeviceSerializer(serializers.ModelSerializer):
    tenant = serializers.SlugRelatedField(queryset=Tenant.objects.all(), slug_field='name')
    owner_group = serializers.SlugRelatedField(queryset=UserGroup.objects.all(), slug_field='name')
    modified_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    # access_groups = serializers.SlugRelatedField(many=True, queryset=UserGroup.objects.all(), slug_field='name')

    class Meta:
        model = Device
        fields = ('id', 'name', 'is_active', 'tenant', 'owner_group', 'note', 'last_modified', 'modified_by')  # , 'access_groups')


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ('first_name', 'last_name', 'email', 'is_active', 'username')
