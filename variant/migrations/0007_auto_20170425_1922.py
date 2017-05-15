# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-04-25 19:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0006_auto_20170208_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toindeljson',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='tosnpjson',
            name='sample',
        ),
        migrations.RemoveField(
            model_name='indel',
            name='members',
        ),
        migrations.RemoveField(
            model_name='snp',
            name='members',
        ),
        migrations.DeleteModel(
            name='ToIndelJSON',
        ),
        migrations.DeleteModel(
            name='ToSNPJSON',
        ),
    ]
