# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-23 20:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ena', '0009_auto_20170823_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='sralink',
            name='is_queried',
            field=models.BooleanField(default=False),
        ),
    ]