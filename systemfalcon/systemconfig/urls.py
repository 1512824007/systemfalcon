"""systemfalcon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from systemconfig import views
from userperm import views as uviews

urlpatterns = [
    #config files manager
    url(r'MonitorManage/$',views.MonitorManage,name='MonitorManage' ),
    url(r'MonitorManage/ConfigManag/(.+)/$',views.ConfigManag,name='ConfigManag' ),
    url(r'MonitorManage/ConfigGitdiff/(.+)/$',views.ConfigGitdiff,name='ConfigGitdiff' ),
    url(r'MonitorManage/ConfigGitstatus/$',views.ConfigGitstatus,name='ConfigGitstatus' ),
    url(r'MonitorManage/ConfigPush/(.+)/(.+)/$',views.ConfigPush,name='ConfigPush' ),
    url(r'MonitorManage/ConfigToolPush/(.+)/(.+)/$',views.ConfigToolPush,name='ConfigPush' ),
    url(r'MonitorManage/ConfigCreat/$',views.ConfigCreat,name='ConfigCreat' ),
    url(r'MonitorManage/ConfigFileList/$',views.ConfigFileList,name='ConfigFileList' ),
    url(r'MonitorManage/ConfigFileUpload/$',views.ConfigFileUpload,name='ConfigFileUpload' ),
    url(r'MonitorManage/ConfigFileUploadInput/(.+)/$',views.ConfigFileUploadInput,name='ConfigFileUploadInput' ),

    #Config tools manager
    url(r'MonitorManage/ConfigHost/$',views.ConfigHost,name='ConfigHost'),
    url(r'MonitorManage/ConfigHostListStatus/$',views.ConfigHostListStatus,name='ConfigHostListStatus'),
    url(r'MonitorManage/ConfigHostGroup/$',views.ConfigHostGroup,name='ConfigHostGroup'),
    url(r'MonitorManage/ConfigHostGroup/(?P<pk>\d+)/update/$',views.ConfigHostGroupUpdate,name='ConfigHostGroupUpdate'),
    url(r'MonitorManage/ConfigHost/detail/(?P<pk>\d+)/$',views.ConfigHostDetail,name='ConfigHostDetail'),
    url(r'MonitorManage/ConfigHost/detail/ConfigHostDetailAddUpdateDelete/$', views.ConfigHostDetailAddUpdateDelete, name='ConfigHostDetailAddUpdateDelete'),
    url(r'MonitorManage/ConfigHost/hostdetail/(?P<pk>\d+)/$', views.ConfigHostInfoDetail, name='ConfigHostInfoDetail'),
    # url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostPack/$', views.ConfigHostPack, name='ConfigHostPack'),
    # url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostSls/$', views.ConfigHostSls, name='ConfigHostSls'),
    url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostPack/(\d+)/Update/$', views.ConfigHostPackUpdate, name='ConfigHostPack'),
    url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostSls/(\d+)/Update/$', views.ConfigHostSlsUpdate, name='ConfigHostSlsUpdate'),
    # url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostTool/$', views.ConfigHostTool, name='ConfigHostTool'),
    # url(r'MonitorManage/ConfigHost/(\d+)/ConfigHostTool/(.+)/Update/$', views.ConfigHostToolUpdate, name='ConfigHostTool'),
    url(r'MonitorManage/ConfigHostPackParameter/$', views.ConfigHostPackParameter, name='ConfigHostPackParameter'),
    url(r'MonitorManage/ConfigHostPackParameterGroup/$', views.ConfigHostPackParameterGroup, name='ConfigHostPackParameterGroup'),
    url(r'MonitorManage/ConfigHostPackParameterGroup/detail/(\d+)/$', views.ConfigHostPackParameterGroupDetail,name='ConfigHostPackParameterGroupDetail'),

    url(r'MonitorManage/ConfigHostPackParameter/detail/(\d+)/$', views.ConfigHostPackParameterDetail, name='ConfigHostPackParameterDetail'),
    url(r'MonitorManage/ConfigToolList/$', views.ConfigToolList, name='ConfigToolList'),

    url(r'MonitorManage/ConfigPluginFile/$', views.ConfigPluginFile, name='ConfigPluginFile'),
    url(r'MonitorManage/ConfigHttpFile/$', views.ConfigHttpFile, name='ConfigHttpFile'),
    url(r'MonitorManage/ConfigPluginFileDetail/(.+)/$', views.ConfigPluginFileDetail, name='ConfigPluginFileDetail'),
    url(r'MonitorManage/ConfigPublicFile/$', views.ConfigPublicFile, name='ConfigPublicFile'),
    url(r'MonitorManage/ConfigPublicFileDetail/(\d+)/$', views.ConfigPublicFileDetail, name='ConfigPublicFileDetail'),
    url(r'MonitorManage/ConfigPrivateFile/$', views.ConfigPrivateFile, name='ConfigPrivateFile'),
    url(r'MonitorManage/ConfigPrivateFileDetail/(\d+)/$', views.ConfigPrivateFileDetail,name='ConfigPrivateFileDetail'),
    url(r'MonitorManage/ConfigPrivateFileDetail_core/(\d+)/$', views.ConfigPrivateFileDetail_core,name='ConfigPrivateFileDetail_core'),

    #Salt manage
    url(r'MonitorManage/SaltManagement/$', views.SaltManagement, name='SaltManagement'),
    url(r'MonitorManage/SaltManagementManage/$', views.SaltManagementManage, name='SaltManagementManage'),
    url(r'MonitorManage/SaltManagementManage/detail/(.+)/$', views.SaltManagementManageDetail, name='SaltManagementManage'),
    url(r'MonitorManage/SaltMessage/$', views.SaltMessage, name='SaltMessage'),
    url(r'MonitorManage/one_click_sync_salt/$', views.one_click_sync_salt,name='one_click_sync_salt'),
    url(r'MonitorManage/SaltControlRsa/$', views.SaltControlRsa, name='SaltControlRsa'),

    url(r'MonitorManage/AddHostTogrp/$',views.AddHostTogrp,name='AddHostTogrp'),
]
