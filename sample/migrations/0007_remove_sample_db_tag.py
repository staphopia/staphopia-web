# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-08 23:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0006_auto_20160602_1705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample',
            name='db_tag',
        ),
    ]