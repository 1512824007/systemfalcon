from django.conf.urls import url, include

from . import views
from openfalcon.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),
    url(r'^accounts/register/$', views.register, name='register'),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$',views.active_user,name='active_user'),

    url(r'^accounts/register/captcha/$', views.captcha, name='captcha'),
    url(r'^forget/$', views.ForgetPwdView.as_view(), name="forget_pwd"),
    url(r'^modify_pwd/$', views.ModifyPwdView.as_view(), name="modify_pwd"),
]
