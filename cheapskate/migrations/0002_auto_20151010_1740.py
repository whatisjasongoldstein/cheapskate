# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cheapskate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawal',
            name='checkno',
            field=models.IntegerField(null=True, verbose_name=b'Check No.', blank=True),
        ),
    ]
