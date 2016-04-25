# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sccmec', '0004_primers_proteins'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coverage',
            name='mean',
            field=models.DecimalField(max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='coverage',
            name='meca_mean',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='coverage',
            name='meca_total',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='coverage',
            name='total',
            field=models.DecimalField(max_digits=7, decimal_places=2),
        ),
    ]
