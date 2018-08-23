#coding=utf-8
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# 为celery程序设置DJANGO_SETTINGS_MODULE环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'systemfalcon.settings')

app = Celery('systemfalcon')

# 从Django的设置文件中导入CELERY设置

app.config_from_object('django.conf:settings')
# 从所有已注册的app中加载任务模块
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.result_backend = 'redis://localhost:6379/0'