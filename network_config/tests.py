# from django.test import TestCase
from .models import *
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group, Permission

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from .views import *


class TenantTests(APITestCase):

    def test_admin_create_tenant(self):
        """
        Ensure only admin can create an account
        :return:
        """
        url = 'http://127.0.0.1:8000/tenants/'
        user = User.objects.create_superuser(username='admin', password='password123', email='')
        data = {'name': 'Waterloo', 'is_active': 'True'}

        # Login and logout use user credentials and they can be substituted for token authentication
        # login = self.client.login(username='admin', password='password123')

        self.client.force_authenticate(user=user, token=user.auth_token)

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tenant.objects.count(), 1)
        self.assertEqual(Tenant.objects.get().name, 'Waterloo')
        # logout = self.client.logout()

        # Stop using present credentials
        self.client.force_authenticate()

    def test_user_create_tenant(self):
        """
        Ensure non admin user cannot create an account
        :return:
        """
        url = 'http://127.0.0.1:8000/tenants/'
        user = User.objects.create_user(username='user', password='password123')
        data = {'name': 'Waterloo', 'is_active': 'True'}

        # Login and logout use user credentials and they can be substituted for token authentication
        # login = self.client.login(username='admin', password='password123')

        self.client.force_authenticate(user=user, token=user.auth_token)

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Stop using present credentials
        self.client.force_authenticate()

        # logout = self.client.logout()


class POSTDeviceTests(APITestCase):
    """
    Note: User can still post device using a tenant that the user is not part of. This must be fixed.
    This code only implements permission checks to ensure user can only post devices to an owner_group
    that the user is part of.
    """
    def setUp(self):

        superuser = User.objects.create_superuser(username='admin', password='password123', email='')
        self.client.login(username='admin', password='password123')

        url = 'http://127.0.0.1:8000/tenants/'
        data = {'name': 'Waterloo', 'is_active': 'True'}
        self.client.post(url, data, format='multipart')

        tenant = Tenant.objects.get(name='Waterloo')

        user_can_post = User.objects.create_user(username='can_post', password='password123')
        user_cannot_post = User.objects.create_user(username='cannot_post', password='password123')
        can_post_usergroup = UserGroup.objects.create(name='CanPost', tenant=tenant, active='True')  # , users=user_can_post)

        post_permission = Permission.objects.get(codename='can_post_devices', )
        can_post_group = Group.objects.get(name='CanPost')
        can_post_group.permissions.add(post_permission)  # , users='can_post')

        cannot_post_usergroup = UserGroup.objects.create(name='CannotPost', tenant=tenant, active='True')  # , users.set(user_cannot_post))

        # The following two lines are not working as expected
        # can_post_group = Group.objects.get(name='CanPost')
        cannot_post_group = Group.objects.get(name='CannotPost')

        can_post_usergroup.users.add(user_can_post)
        cannot_post_usergroup.users.add(user_cannot_post)

        # can_post_usergroup.users.add(user_can_post)
        # cannot_post_usergroup.users.add(user_cannot_post)

        user_can_post.groups.add(can_post_group)
        user_cannot_post.groups.add(cannot_post_group)

        # self.can_post_group.user_set.add(self.user_can_post)
        # self.cannot_post_group.user_set.add(self.user_cannot_post)

        # self.user_can_post.groups.add(self.can_post_group)
        # self.user_cannot_post.groups.add(self.cannot_post_group)

        self.client.logout()

    def test_create_device(self):
        """
        Ensure user can only post devices to an owner_group that the user is part of.
        :return:
        """
        # This subtest ensures that a user with the post permission can post a device to a group
        # that the user is a member of.
        url = 'http://127.0.0.1:8000/devices/'
        data = {'name': 'Should Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CanPost',
                'modified_by': 'can_post'}
        login = self.client.login(username='can_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Device.objects.get().name, 'Should Post')
        logout = self.client.logout()

        #######################################################################################################

        # This subtest ensures that a user with the post permission cannot post a device to a group
        # that the user is not a member of.

        url = 'http://127.0.0.1:8000/devices/'
        data = {'name': 'Should Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CannotPost',
                'modified_by': 'can_post'}
        self.client.login(username='can_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #######################################################################################################

        # This subtest ensures that a user without the post permission cannot post a device to any group.

        data = {'name': 'Should Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CannotPost',
                'modified_by': 'can_post'}
        self.client.login(username='cannot_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {'name': 'Should Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CannotPost',
                'modified_by': 'cannot_post'}
        self.client.login(username='cannot_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        logout = self.client.logout()


# All PUTDeviceTests currently fail due to the incomplete implementation
class PUTDeviceTests(APITestCase):

    def setUp(self):

        superuser = User.objects.create_superuser(username='admin', password='password123', email='')
        self.client.login(username='admin', password='password123')

        url = 'http://127.0.0.1:8000/tenants/'
        data = {'name': 'Waterloo', 'is_active': 'True'}
        self.client.post(url, data, format='multipart')

        tenant = Tenant.objects.get(name='Waterloo')

        user_can_post = User.objects.create_user(username='can_post', password='password123')
        user_cannot_post = User.objects.create_user(username='cannot_post', password='password123')
        can_post_usergroup = UserGroup.objects.create(name='CanPost', tenant=tenant, active='True')  # , users=user_can_post)

        post_permission = Permission.objects.get(codename='can_post_devices', )
        can_post_group = Group.objects.get(name='CanPost')
        can_post_group.permissions.add(post_permission)  # , users='can_post')

        cannot_post_usergroup = UserGroup.objects.create(name='CannotPost', tenant=tenant, active='True')  # , users.set(user_cannot_post))

        # The following two lines are not working as expected
        # can_post_group = Group.objects.get(name='CanPost')
        cannot_post_group = Group.objects.get(name='CannotPost')

        can_post_usergroup.users.add(user_can_post)
        cannot_post_usergroup.users.add(user_cannot_post)

        # can_post_usergroup.users.add(user_can_post)
        # cannot_post_usergroup.users.add(user_cannot_post)

        user_can_post.groups.add(can_post_group)
        user_cannot_post.groups.add(cannot_post_group)

        # self.can_post_group.user_set.add(self.user_can_post)
        # self.cannot_post_group.user_set.add(self.user_cannot_post)

        # self.user_can_post.groups.add(self.can_post_group)
        # self.user_cannot_post.groups.add(self.cannot_post_group)

        self.client.logout()

        url = 'http://127.0.0.1:8000/devices/'
        data = {'name': 'Should Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CanPost',
                'modified_by': 'can_post'}
        login = self.client.login(username='can_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        logout = self.client.logout()

    # def test_put_device(self):
    #     """
    #     Ensure user can only put devices to an owner_group and tenant that the user is part of.
    #     Currently this test will fail as the tenant check is not being done.
    #     :return:
    #     """
    #     # This subtest ensures that a user with the post permission can post a device to a group
    #     # that the user is a member of.
    #     url = 'http://127.0.0.1:8000/devices/1/'
    #     data = {'name': 'Should not Post', 'is_active': 'False', 'tenant': 'Koodo', 'owner_group': 'CannotPost',
    #             'modified_by': 'can_post'}
    #     login = self.client.login(username='can_post', password='password123')
    #     response = self.client.put(url, data, format='multipart')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     logout = self.client.logout()

        ##########################################################################################################

        # This subtest ensures that a user cannot PUT a device to an owner_group that the user is not a member of

        url = 'http://127.0.0.1:8000/devices/1/'
        data = {'name': 'Should not Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CannotPost',
                'modified_by': 'can_post'}
        self.client.login(username='can_post', password='password123')
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ##########################################################################################################

        # This subtest ensures that a user cannot PUT a device whose original owner_group is group that the user
        # is not a member of

        url = 'http://127.0.0.1:8000/devices/1/'
        data = {'name': 'Should not Post', 'is_active': 'False', 'tenant': 'Waterloo', 'owner_group': 'CanPost',
                'modified_by': 'can_post'}
        self.client.login(username='cannot_post', password='password123')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class AuthTokenTests(APITestCase):
    def setUp(self):
        user_authtoken = User.objects.create_user(username='authtoken', password='password123', is_staff=True)

    def test_auth_token(self):
        # Using the standard RequestFactory API to create a form POST request
        factory = APIRequestFactory()
        user = User.objects.get(username='authtoken')
        view = TenantList.as_view()

        request = factory.post('127.0.0.1:8000/tenants/', {'name': 'Koodo', 'is_active': 'False'}, format='multipart')
        force_authenticate(request, user=user, token=user.auth_token)
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.content, b'{"id":1,"name":"Koodo","is_active":false}')
