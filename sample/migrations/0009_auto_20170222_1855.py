# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-22 18:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sample', '0008_auto_20170220_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enametadata',
            name='sample',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sample.Sample'),
        ),
    ]