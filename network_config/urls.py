from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from network_config import views

from django.contrib import admin
from django.urls import path

# urlpatterns = [
#     url(r'^tenants/$', views.tenant_list),
#     url(r'^tenants/(?P<pk>[0-9]+)/$', views.tenant_detail),
# ]

"""
urlpatterns defines the extensions of the url through which each view can be accessed
"""

urlpatterns = [
    url(r'^tenants/$', views.TenantList.as_view()),
    url(r'^tenants/(?P<pk>[0-9]+)/$', views.TenantDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^devices/$', views.DeviceList.as_view()),
    url(r'^devices/(?P<pk>[0-9]+)/$', views.DeviceDetail.as_view()),
    # url(r'^profile/$', views.ProfileList.as_view()),
    path('admin/', admin.site.urls),
]

urlpatterns = format_suffix_patterns(urlpatterns)

"""
NOTE: This is separately added to urlpatterns since importing views from rest_framework.authtoken
interferes with how django accesses custom views built for this app (the third import statement:
from network_config import views)
"""

from rest_framework.authtoken import views

urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token)
]