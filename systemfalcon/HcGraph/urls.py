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

from HcGraph import views
from HcGraph.views import index as index


urlpatterns = [
    url(r'index/$',index,name='index'),
    url(r'chart/big/ed=(\w+)$',views.Chart_Big,name='Chart_Big'),
    url(r'chart/ss/ed=(\w+)$',views.Chart_Big,name='Chart_Big'),
    url(r'chart/live/$',views.Chart_live,name='Chart_live'),
    url(r'chart/media/$',views.Chart_media,name='Chart_media'),
    url(r'chart/web/$',views.Chart_web,name='Chart_web'),
    url(r'chart/live_net/$',views.Chart_live_net,name='Chart_live_net'),
    url(r'chart/media_net/$',views.Chart_media_net,name='Chart_media_net'),
    url(r'chart/web_net/$',views.Chart_web_net,name='Chart_web_net'),

    url(r'chart/room/live/(.+)/$', views.Chart_room_live, name='Chart_room_live'),
    url(r'chart/room/media/(.+)/$', views.Chart_room_media, name='Chart_room_media'),
    url(r'chart/room/web/(.+)/$', views.Chart_room_web, name='Chart_room_web'),

    url(r'chart/room/live_ss/(.+)/$',views.Chart_room_live_ss,name='Chart_room_live_ss'),
    url(r'chart/room/media_ss/(.+)/$',views.Chart_room_media_ss,name='Chart_room_media_ss'),
    url(r'chart/room/web_ss/(.+)/$',views.Chart_room_web_ss,name='Chart_room_web_ss'),


    url(r'chart/network/$',views.Chart_net_index,name='Chart_net_index'),
    url(r'chart/service/$',views.Chart_ss_index,name='Chart_ss_index'),
    url(r'chart/room_networks/(.+)/$',views.Chart_room_index,name='Chart_room_index'),
    url(r'chart/room_services/(.+)/$',views.Chart_room_index_ss,name='Chart_room_index_ss'),

    #alarm info 
    url(r'chart/alarm_load/(.+)/$',views.Chart_Server_load,name='Chart_Server_load'),
    url(r'chart/alarm_cpu/(.+)/$',views.Chart_Server_cpu,name='Chart_Server_cpu'),
    url(r'chart/alarm_memory/(.+)/$',views.Chart_Server_mem,name='Chart_Server_mem'),
    url(r'chart/alarm_network/(.+)/$',views.Chart_Server_network,name='Chart_Server_network'),
    url(r'chart/alarm_network_error/(.+)/$',views.Chart_Server_network_error,name='Chart_Server_network_error'),
    url(r'chart/alarm_http/(.+)/$',views.Chart_Server_http,name='Chart_Server_http'),

]
