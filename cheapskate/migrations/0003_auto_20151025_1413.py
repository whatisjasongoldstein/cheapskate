# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cheapskate', '0002_auto_20151010_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccbill',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='charge',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='withdrawal',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
