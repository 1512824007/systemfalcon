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
from django.conf.urls import url
from sysconf import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'room_band/$', views.room_band, name='room_band'),
    url(r'room_band/uploadFile/$', views.uploadFile, name='uploadFile'),
    url(r'room_band/updateband$', csrf_exempt(views.updateband), name='updateband'),

    url(r'user_manage/$', views.user_center, name='user_manage'),

    url(r'user_center/$', views.user_center, name='user_center'),
    url(r'user_show/$', views.user_show, name='user_show'),
    url(r'user_active/$', views.user_active, name='user_active'),
    url(r'user_import/$', views.user_import, name='user_import'),
    url(r'user_del/$', views.user_del, name='user_del'),

    url(r'group_add/$', views.group_add, name='group_add'),

    url(r'group_manage/$', views.group_manage, name='group_manage'),
    url(r'user_manage_op/$', views.user_manage_op, name='user_manage_op'),
    url(r'user_detail_op/$', views.user_detail_op, name='user_detail_op'),
    url(r'group_change/$', views.group_change, name='group_change'),
    url(r'group_save/$', views.group_save, name='group_save'),

    url(r'group_center/$', views.group_center, name='group_center'),
    url(r'groupManage/$', views.groupManage, name='groupManage'),
    url(r'group_manage_op/$', views.group_manage_op, name='group_manage_op'),
    url(r'group_change2/$', views.group_change2, name='group_change2'),
    url(r'group_save2/$', views.group_save2, name='group_save2'),
    url(r'group_del/$', views.group_del, name='group_del'),
    #url(r'group_c_name/$', csrf_exempt(views.group_c_name), name='group_c_name'),

    url(r'read_user_xml/$', views.read_user_xml, name='read_user_xml'),
    url(r'read_group_xml/$', views.read_group_xml, name='read_group_xml'),

    url(r'module_add/$', views.module_add, name='module_add'),
    url(r'module_del/$', views.module_del, name='module_del'),
    url(r'module_change/$', views.module_change, name='module_change'),

    url(r'log_list/$', views.log_list, name='log_list'),
    url(r'log_center/$', views.log_center, name='log_center'),

    url(r'classmod_man/$', views.classmod_man, name='classmod_man'),
    url(r'class_mod_del/$', views.class_mod_del, name='class_mod_del'),
    url(r'class_mod_change/$', views.class_mod_change, name='class_mod_change'),
    url(r'classmod_list/$', views.classmod_list, name='classmod_list'),
    url(r'ce_shi/$', views.ce_shi, name='ce_shi'),
]

