# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.

from top10.models import clusterss

class ssTestCase(TestCase):
    def setUp(self):
        clusterss.objects.create(endpoint='sr014.cm-zjtz-01.c4hcdn.cn', ssvalue=800, project='clms',\
                                 cluster='CM_ZJTZ_EDGE', add_date=1496647815)
        clusterss.objects.create(endpoint='sr007.cm-zjhz-04.c4hcdn.cn', ssvalue=900, project='clms',\
                                 cluster='CM_ZJTZ_EDGE', add_date=1496647815)
    def test_ss(self):
        z1 = clusterss.objects.get(endpoint='sr014.cm-zjtz-01.c4hcdn.cn')
        z2 = clusterss.objects.get(endpoint='sr007.cm-zjhz-04.c4hcdn.cn')
        self.assertEqual(z1.ssvalue, 800)
        self.assertEqual(z2.ssvalue, 900)

