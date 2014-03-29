# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('bank', models.CharField(max_length=255)),
                ('kind', models.CharField(max_length=255, choices=[(b'checking', b'Checking'), (b'cc', b'Credit Card')])),
            ],
        ),
        migrations.CreateModel(
            name='CCBill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField()),
                ('date', models.DateField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('account', models.ForeignKey(to='cheapskate.Account')),
            ],
            options={
                'verbose_name': 'Credit Card Bill',
            },
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('amount', models.FloatField()),
                ('date', models.DateField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('paid', models.BooleanField(default=False)),
                ('lost', models.BooleanField(default=False)),
                ('account', models.ForeignKey(to='cheapskate.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('amount', models.FloatField()),
                ('date', models.DateField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('account', models.ForeignKey(to='cheapskate.Account')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name': 'Expense Category',
                'verbose_name_plural': 'Expense Categories',
            },
        ),
        migrations.CreateModel(
            name='IncomeCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('amount', models.FloatField()),
                ('date', models.DateField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('checkno', models.IntegerField(null=True, blank=True)),
                ('account', models.ForeignKey(to='cheapskate.Account')),
                ('category', models.ForeignKey(blank=True, to='cheapskate.ExpenseCategory', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='deposit',
            name='category',
            field=models.ForeignKey(blank=True, to='cheapskate.IncomeCategory', null=True),
        ),
        migrations.AddField(
            model_name='charge',
            name='category',
            field=models.ForeignKey(to='cheapskate.ExpenseCategory'),
        ),
        migrations.AddField(
            model_name='ccbill',
            name='charges',
            field=models.ManyToManyField(to='cheapskate.Charge', blank=True),
        ),
    ]
