# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 21:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0004_auto_20160420_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='length',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
