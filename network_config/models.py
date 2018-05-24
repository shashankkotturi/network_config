from django.db import models
from django.contrib.auth.models import User, Group

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token


"""
Tenant model with attributes id, name and is_active
Database table name: TENANT
Available Permissions: Can Post Tenants, Can Edit Tenants
"""


class Tenant(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=50)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='IS_ACTIVE')  # Field name made lowercase.

    class Meta:
        db_table = 'TENANT'
        permissions = (
            ('can_post_tenants', 'Can POST Tenants'),
            ('can_edit_tenants', 'Can EDIT Tenants'),
        )

    def __str__(self):
        return self.name


"""
UserGroup model with attributes tenant, active, users.
UserGroup extends Group models built into django.contrib.auth.models.
UserGroup inherits attributes id and name.
Database Table name: USER_GROUP.
Arrange groups by name, tenant.
"""

"""
NOTE: Creating a separate UserGroup model that does not extend Group can
be a better approach. Extending group model as below causes issues with permissions
given to users. Detailed explanation given in admin.py
"""


class UserGroup(Group):
    # id = models.AutoField(db_column='ID', primary_key=True)
    # group = models.OneToOneField(Group, models.CASCADE, db_column='GROUP_ID')
    # name = models.CharField(db_column='NAME', max_length=50)
    tenant = models.ForeignKey('Tenant', models.CASCADE, db_column='TENANT_ID', default='')
    active = models.BooleanField(db_column='ACTIVE', default=True)
    users = models.ManyToManyField(User)  # , through='UgHasUser')

    class Meta:
        db_table = 'USER_GROUP'
        ordering = ['name', 'tenant']
        # proxy = True

    def __str__(self):
        return self.name


"""
Receiver method that creates a token for every user that is created.
"""


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


"""
Device model with attributes id, name, is_active, tenant, owner_group, note, last_modified, modified_by
Database table name: DEVICE
Available Permissions: Can Post Devices, Can Edit Devices
"""


class Device(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    name = models.CharField(db_column='NAME', default='DEVICEDEFAULT', max_length=50)
    is_active = models.BooleanField(db_column='ACTIVE', default=True)
    tenant = models.ForeignKey('Tenant', models.CASCADE, db_column='TENANT_ID')
    owner_group = models.ForeignKey('UserGroup', models.CASCADE, db_column='USER_GROUP_ID')
    note = models.TextField(db_column='NOTE', max_length=255, blank=True)
    # protocol...
    last_modified = models.DateTimeField(db_column='LAST_MODIFIED', auto_now=True)
    modified_by = models.ForeignKey(User, models.DO_NOTHING, db_column='MODIFIED_BY')
    # access_groups = models.ManyToManyField('UserGroup', related_name='access_groups')

    class Meta:
        db_table = 'DEVICE'
        permissions = (
            ('can_post_devices', 'Can POST Devices'),
            ('can_edit_devices', 'Can EDIT Devices'),
        )

        def __str__(self):
            return self.name

"""
Through model between User and UserGroup model can be specified if required. Else django will create a default through
model within the database. 
"""


# class UgHasUser(models.Model):
#     id = models.AutoField(db_column='ID', primary_key=True)
#     ug = models.ForeignKey(UserGroup, db_column='USER_GROUP_ID', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, db_column='USER_ID', on_delete=models.CASCADE)
#     is_admin = models.BooleanField(db_column='IS_ADMIN', default=False)
#
#     class Meta:
#         db_table = 'UG_has_USER'
#         # unique_together = (('ug', 'user'),)


"""
Profile model that extends User model using a one to one relationship
"""


# class Profile(models.Model):
#     id = models.AutoField(db_column='ID', primary_key=True)
#     user = models.OneToOneField(User, models.CASCADE, db_column='USER_ID')  # , default='')
#     # tenant = models.ForeignKey('Tenant', models.DO_NOTHING, db_column='TENANT_ID', related_name='Tenant_Profile', default=1)
#
#     class Meta:
#         db_table = 'PROFILE'
#         # unique_together = (('user', 'tenant'),)
#
#     def __str__(self):
#         return self.user.username
#
# # Profile is created/updated once User model is saved.
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create()
#     instance.profile.save()

