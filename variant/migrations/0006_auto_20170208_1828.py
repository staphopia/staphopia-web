# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-08 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('variant', '0005_auto_20170208_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='toindeljson',
            name='count',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='tosnpjson',
            name='count',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
    ]