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
from openfalcon.views import index as index,event
from userperm import views as uviews

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('userauth.urls')),
    url(r'^monitor/', include('openfalcon.urls')),
    url(r'^monitor/hcgraph/', include('HcGraph.urls')),
    url(r'^monitor/top10/', include('top10.urls')),
    url(r'^monitor/sysconf/', include('sysconf.urls')),
    url(r'^monitor/', include('systemconfig.urls')),


]
from django.conf import settings
from django.views.static import serve
if settings.DEBUG is False:
    urlpatterns += (url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT,}),)
