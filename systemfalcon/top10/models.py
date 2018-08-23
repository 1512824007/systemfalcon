# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.


class end_va_cou(models.Model):
    endpoint = models.CharField(max_length=255)
    value = models.FloatField(max_length=50)
    counter = models.CharField(max_length=255)
    add_date = models.IntegerField()
    cpu_num = models.IntegerField()

    def __unicode__(self):
        return self.name


class cluster_nic(models.Model):
    endpoint = models.CharField(max_length=255)
    value = models.FloatField(max_length=50)
    speed = models.SlugField(max_length=20)
    counter = models.CharField(max_length=255)
    idc = models.CharField(blank=True, max_length=30)
    add_date = models.IntegerField()

    def __unicode__(self):
        return self.name


class date_graph(models.Model):
    endpoint = models.CharField(max_length=255)
    value = models.FloatField(max_length=50)
    counter = models.CharField(max_length=255)
    project = models.SlugField(max_length=20)
    cluster = models.SlugField(max_length=20)
    idc = models.CharField(blank=True, max_length=30)
    add_date = models.IntegerField()



