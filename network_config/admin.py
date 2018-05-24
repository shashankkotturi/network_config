from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
#
from .models import UserGroup


# # Define an inline admin descriptor for UserProfile model
# # which acts a bit like a singleton
# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'
#
#
# # Define a new User admin
# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline, )
#
#     list_display = ('user',)  # name', 'email', 'is_staff', 'get_location')
#     list_select_related = ('profile', )
#
#     def get_location(self, instance):
#         return instance.profile.location
#     get_location.short_description = 'location'
#
#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class UserGroupInline(admin.TabularInline):
    model = UserGroup.users.through
    can_delete = False
    verbose_name_plural = 'User Group'
    fk_name = 'usergroup'


# Define a new User admin
class UserGroupAdmin(admin.ModelAdmin):

    list_display = ('name', 'tenant', 'active', 'id')
    ordering = ('tenant', 'name')


# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(UserGroup, UserGroupAdmin)
