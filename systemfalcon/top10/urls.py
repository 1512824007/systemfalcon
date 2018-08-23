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

from top10 import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'index/$', views.index, name='index'),
    url(r'idc_top10/$', views.idc_top10, name='idc_top10'),

    url(r'ec/(.+)/$', views.ec, name='ec'),
    url(r'icmp_graph/(.+)/$', views.icmp_graph, name='icmp_graph'),
    url(r'icmp_detail/(.+)/$', views.icmp_detail, name='icmp_detail'),
    url(r'ss/(.+)/(.+)/(.+)/(.+)/$', views.ss_ss, name='ss_ss'),
    url(r'Device_graph/(.+)/(.+)/(.+)/$', views.Device_graph, name='Device_graph'),
    url(r'project_hostlist/(.+)$', views.project_hostlist, name='project_hostlist'),

    url(r'idc_network_graph/(.+)/$', views.idc_network_graph, name='idc_network_graph'),
    url(r'Bandwidth/$', views.Bandwidth, name='Bandwidth'),
    url(r'band/$', views.band, name='band'),
]

