# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sccmec', '0003_auto_20151013_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='cassette',
            name='meca_length',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cassette',
            name='meca_start',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cassette',
            name='meca_stop',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='coverage',
            name='meca_maximum',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='coverage',
            name='meca_mean',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name='coverage',
            name='meca_median',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='coverage',
            name='meca_minimum',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='coverage',
            name='meca_total',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
    ]
