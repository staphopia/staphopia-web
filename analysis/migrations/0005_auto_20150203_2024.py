# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0004_auto_20150202_0346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fastqstats',
            name='coverage',
            field=models.DecimalField(max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='fastqstats',
            name='total_bp',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='fastqstats',
            name='total_reads',
            field=models.BigIntegerField(),
        ),
    ]
