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

from openfalcon.views import index as index,TroubleGroup,event,echart,Map,TroubleList,TroubleBI,TroubleInfo,ServerRoom,UserRequest,MonitorManage,ServerRoom_Detail,falcon,falcon_detail,falcon_alarm_info,falcon_alarm_detail,Device_Detail,TroubleInfo_Add

from userperm import views as uviews

urlpatterns = [
    url(r'Dashboard/$',index,name='home' ),
    url(r'MonitorInfo/$',event,name='event' ),
    url(r'MonitorInfo/TroubleList/$',TroubleList,name='TroubleList' ),
    url(r'MonitorInfo/TroubleBI/$',TroubleBI,name='TroubleBI' ),

    url(r'MonitorInfo/TroubleInfo/$',TroubleInfo,name='TroubleInfo'),
    url(r'MonitorInfo/TroubleInfo_Add/$',TroubleInfo_Add,name='TroubleInfo_Add' ),

    url(r'MonitorInfo/TroubleInfo/$',TroubleInfo,name='TroubleInfo' ),
    url(r'MonitorInfo/TroubleInfo_Add/$',TroubleInfo_Add,name='TroubleInfo_Add' ),
    url(r'MonitorInfo/ServerRoom/$',ServerRoom,name='ServerRoom' ),

    url(r'MonitorInfo/UserRequest/$',UserRequest,name='UserRequest' ),
    url(r'MonitorManage/$',MonitorManage,name='MonitorManage' ),
    url(r'MonitorInfo/ServerRoom/Detail/(.+)/$',ServerRoom_Detail,name='ServerRoom_Detail' ),
    url(r'MonitorInfo/Device/(.+)/$', Device_Detail, name='Device_Detail'),

    url(r'MonitorInfo/Map/$',Map,name='Map' ),
    # url(r'/fautdetail/(.+)/$',event_room,name='event_room' ),
    url(r'falcon/$',falcon,name='falcon' ),
    url(r'MonitorInfo/TroubleHistory/$',falcon_alarm_info,name='TroubleHistory' ),
	url(r'MonitorInfo/TroubleGroup/$', TroubleGroup, name='TroubleGroup'),

    url(r'falcon_detail/(?P<id>\d+)/$',falcon_detail,name='falcon_detail' ),
    url(r'MonitorInfo/alarm_detail/(?P<pk>\d+)/$',falcon_alarm_detail,name='falcon_alarm_detail' ),

    url(r'echart/$',echart,name='echart'),

]
