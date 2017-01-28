# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-22 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cheapskate', '0004_auto_20160306_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='do_not_project',
            field=models.BooleanField(default=False, help_text=b'This is a one time thing.', verbose_name=b"Don't Project"),
        ),
        migrations.AddField(
            model_name='deposit',
            name='do_not_project',
            field=models.BooleanField(default=False, help_text=b'This is a one time thing.', verbose_name=b"Don't Project"),
        ),
        migrations.AddField(
            model_name='withdrawal',
            name='do_not_project',
            field=models.BooleanField(default=False, help_text=b'This is a one time thing.', verbose_name=b"Don't Project"),
        ),
    ]
