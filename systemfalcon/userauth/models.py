#coding:utf8
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(u'手机号', max_length=16, blank=True)
    realName = models.CharField(u'用户姓名', max_length=100, blank=True)
    is_director = models.BooleanField(u'是否主管',default="False")
    #company = models.CharField(u'公司', max_length=100, blank=True)
    #department = models.CharField(u'部门', max_length=100, blank=True)
    #position = models.CharField(u'职位', max_length=100, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(u'描述', max_length=250, blank=True)
    date = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Group)
def create_group_profile(sender, instance, created, **kwargs):
    if created:
        GroupProfile.objects.create(group=instance)

@receiver(post_save, sender=Group)
def save_group_profile(sender, instance, **kwargs):
    instance.groupprofile.save()
